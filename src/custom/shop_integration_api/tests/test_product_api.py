import odoo.tests
from odoo.tests.common import HttpCase

@odoo.tests.tagged('post_install', '-at_install')
class TestShopProductApi(HttpCase):

    def setUp(self):
        """
        Configuración inicial que se ejecuta antes de cada prueba.
        Creamos un producto de prueba activo, vendible y con datos limpios.
        """
        super(TestShopProductApi, self).setUp()
        
        # Creamos un producto de prueba en la base de datos de tests
        self.test_product = self.env['product.product'].create({
            'name': 'Producto Prueba API',
            'default_code': 'PROD-TEST-123',
            'list_price': 100.0,
            'active': True,
            'sale_ok': True,
        })

    def test_01_get_products_success(self):
        """Verifica que el endpoint responda un código 200 y devuelva el producto creado."""
        # Nos autenticamos como el usuario administrador por defecto en las pruebas
        self.authenticate('admin', 'admin')
        
        # Hacemos una petición GET a la ruta de nuestra API
        response = self.url_open('/api/v1/products')
        
        # Comprobamos que el servidor responde con éxito (HTTP 200)
        self.assertEqual(response.status_code, 200)
        
        # Comprobamos que la respuesta contenga nuestro producto
        data = response.json()
        self.assertIn('products', data)
        product_codes = [p['code'] for p in data['products']]
        self.assertIn('PROD-TEST-123', product_codes)

    def test_02_get_products_invalid_date_error_handling(self):
        """
        Verifica que si envían una fecha mal escrita, la API devuelva un error claro 
        (HTTP 400) y NO un error interno del servidor (HTTP 500).
        """
        self.authenticate('admin', 'admin')
        
        # Enviamos un parámetro de fecha deliberadamente inválido
        response = self.url_open('/api/v1/products?modified_since=esto-no-es-una-fecha')
        
        # Debe retornar código HTTP 400 (Bad Request) y no explotar con 500
        self.assertEqual(response.status_code, 400)
        
        # Verificamos que la estructura del error devuelva un JSON descriptivo
        error_data = response.json()
        self.assertIn('error', error_data)
        self.assertEqual(error_data['error']['code'], 'INVALID_DATE_FORMAT')