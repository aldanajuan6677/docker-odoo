import json
from odoo.tests import tagged
from odoo.tests.common import HttpCase


@tagged("post_install", "-at_install")
class TestShopApiIntegration(HttpCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # 1. Crear usuario de prueba y generar su API Key nativa
        cls.test_user = cls.env["res.users"].create({
            "name": "Usuario API Tienda",
            "login": "api_shop_user",
            "email": "api@shop.com",
        })
        # Generar clave de API usando el modelo nativo res.users.apikeys
        _, cls.api_key = cls.env["res.users.apikeys"]._generate(
            scope="rpc", name="API Test Key", password=cls.test_user.password
        )

        # 2. Crear cliente (partner) de prueba con su RIF (campo vat)
        cls.partner = cls.env["res.partner"].create({
            "name": "Cliente Comprador C.A.",
            "vat": "J-12345678-9",
        })

        # 3. Crear producto de prueba con código (default_code)
        cls.product = cls.env["product.product"].create({
            "name": "Laptop de Prueba",
            "default_code": "LAPTOP-01",
            "list_price": 500.0,
            "type": "consu",
        })

    def test_01_orders_unauthorized(self):
        """Verifica que llamadas sin token o con token inválido devuelvan HTTP 401[cite: 5]."""
        url = "/api/v1/orders"
        headers = {"Content-Type": "application/json"}
        
        # Petición sin cabecera Authorization
        response = self.url_open(url, data=json.dumps({}), headers=headers)
        self.assertEqual(response.status_code, 401)

        # Petición con token falso
        headers["Authorization"] = "Bearer invalid_token_12345"
        response = self.url_open(url, data=json.dumps({}), headers=headers)
        self.assertEqual(response.status_code, 401)

    def test_02_orders_validation_errors_422(self):
        """Verifica que RIF o productos inexistentes devuelvan HTTP 422 con formato estructurado[cite: 2, 5]."""
        url = "/api/v1/orders"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }

        # Caso A: RIF inexistente
        payload_bad_partner = {
            "partner_rif": "J-99999999-9",
            "external_ref": "EXT-001",
            "lines": [{"default_code": "LAPTOP-01", "quantity": 1}]
        }
        response = self.url_open(url, data=json.dumps(payload_bad_partner), headers=headers)
        self.assertEqual(response.status_code, 422)
        res_json = response.json()
        self.assertEqual(res_json["error"]["code"], "PARTNER_NOT_FOUND")

        # Caso B: Producto inexistente
        payload_bad_product = {
            "partner_rif": "J-12345678-9",
            "external_ref": "EXT-002",
            "lines": [{"default_code": "PRODUCTO-FALSO", "quantity": 1}]
        }
        response = self.url_open(url, data=json.dumps(payload_bad_product), headers=headers)
        self.assertEqual(response.status_code, 422)
        res_json = response.json()
        self.assertEqual(res_json["error"]["code"], "PRODUCT_NOT_FOUND")
        self.assertIn("lines[0].default_code", res_json["error"]["field"])

    def test_03_orders_success(self):
        """Verifica una creación exitosa de pedido y su respectivo registro en el log[cite: 5]."""
        url = "/api/v1/orders"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        payload = {
            "partner_rif": "J-12345678-9",
            "external_ref": "EXT-TEST-999",
            "lines": [
                {"default_code": "LAPTOP-01", "quantity": 2}
            ]
        }

        response = self.url_open(url, data=json.dumps(payload), headers=headers)
        self.assertEqual(response.status_code, 200)
        res_json = response.json()
        self.assertTrue(res_json.get("success"))
        
        # Validar que el pedido nació como borrador (cotización) según nuestro supuesto[cite: 5]
        order_id = res_json.get("order_id")
        order = self.env["sale.order"].browse(order_id)
        self.assertEqual(order.state, "draft")
        self.assertEqual(order.client_order_ref, "EXT-TEST-999")

        # Verificar que la llamada quedó registrada en el modelo de logs[cite: 5]
        log_record = self.env["shop.api.log"].search([("endpoint", "=", "/api/v1/orders")], limit=1)
        self.assertTrue(log_record)
        self.assertEqual(log_record.response_code, "200")
        self.assertEqual(log_record.user_id, self.test_user)