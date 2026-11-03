from odoo.tests import tagged
from odoo.tests.common import TransactionCase, new_test_user


@tagged("post_install", "-at_install")
class TestSaleCommission(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Creación de usuario con perfil estrictamente de Vendedor (sin privilegios de gerente)
        cls.salesman = new_test_user(
            cls.env, login="commission_salesman", groups="sales_team.group_sale_salesman",
            name="Vendedor de prueba",
        )
        cls.salesman.commission_percent = 5.0
        cls.env.user.commission_percent = 5.0
        
        # Usuario vendedor secundario para pruebas de aislamiento de reportes
        cls.other_salesman = new_test_user(
            cls.env, login="commission_other_salesman", groups="sales_team.group_sale_salesman",
            name="Otro vendedor",
        )
        cls.other_salesman.commission_percent = 3.0
        
        # Datos base de prueba (cliente, categoría y producto)
        cls.partner = cls.env["res.partner"].create({"name": "Cliente de prueba"})
        cls.category = cls.env["product.category"].create({"name": "Repuestos"})
        cls.product = cls.env["product.product"].create({
            "name": "Producto de prueba",
            "categ_id": cls.category.id,
            "list_price": 100.0,
            "taxes_id": [(5, 0, 0)],
        })

    def _create_order(self, user, qty=2):
        """Método auxiliar para simular la creación de un pedido de venta asociado a un vendedor."""
        return self.env["sale.order"].create({
            "partner_id": self.partner.id,
            "user_id": user.id,
            "order_line": [(0, 0, {"product_id": self.product.id, "product_uom_qty": qty})],
        })

    def test_commission_on_confirm(self):
        """Valida que la comisión se calcule e inmovilice correctamente al confirmar el pedido."""
        order = self._create_order(self.salesman)
        self.assertEqual(order.order_line.commission_amount, 0.0)
        order.action_confirm()
        self.assertEqual(order.order_line.commission_percent, 5.0)
        self.assertAlmostEqual(order.order_line.commission_amount, 10.0)

    def test_salesman_report_only_own(self):
        """Valida que un vendedor solo visualice sus propias comisiones en el reporte mensual."""
        self._create_order(self.salesman).action_confirm()
        self._create_order(self.other_salesman).action_confirm()
        self.env.flush_all()
        lines = self.env["sale.commission.report"].with_user(self.salesman).search([])
        self.assertTrue(lines)
        self.assertEqual(lines.mapped("user_id"), self.salesman)

    def test_commission_by_category(self):
        """Valida el cálculo de comisiones basado en las reglas específicas configuradas por categoría."""
        self.category.commission_percent = 8.0
        order = self._create_order(self.salesman)
        order.action_confirm()
        self.assertEqual(order.order_line.commission_percent, 8.0)
        self.assertAlmostEqual(order.order_line.commission_amount, 16.0)

    def test_subcategory_uses_most_specific_rule(self):
        """Valida que el sistema aplique la regla de comisión más específica en subcategorías."""
        self.category.commission_percent = 8.0
        child = self.env["product.category"].create({"name": "Frenos", "parent_id": self.category.id})
        child.commission_percent = 10.0
        self.product.categ_id = child
        order = self._create_order(self.salesman)
        order.action_confirm()
        self.assertEqual(order.order_line.commission_percent, 10.0)

    def test_salesman_can_confirm_order_with_rules(self):
        """
        [TICKET T-200] Prueba de regresión y validación de seguridad de permisos.
        
        Funcionalidad evaluada:
        Garantiza que un usuario con rol exclusivo de vendedor (`salesman`) pueda confirmar 
        pedidos de venta que involucren consultas al modelo de reglas de comisión por categoría 
        (`sale.commission.rule`) sin disparar errores de acceso (AccessError).
        
        Comportamiento esperado:
        - Sin la corrección en 'ir.model.access.csv', este test falla con un error de permisos en el ORM.
        - Con la corrección de lectura aplicada, la orden pasa exitosamente a estado de venta y 
          aplica la regla de categoría correspondiente evaluada por el vendedor.
        """
        # Configurar una regla de comisión por categoría para forzar la consulta al modelo protegido
        self.category.commission_percent = 8.0
        
        # Crear la orden de venta
        order = self._create_order(self.salesman)
        
        # Ejecutar la confirmación de la orden forzando explícitamente el contexto del usuario vendedor
        order.with_user(self.salesman).action_confirm()
        
        # Verificaciones finales de éxito
        self.assertEqual(order.state, "sale")
        self.assertEqual(order.order_line.commission_percent, 8.0)