from odoo.tests import tagged
from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError, AccessError


@tagged("post_install", "-at_install")
class TestPaymentRequest(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Crear un socio proveedor de prueba
        cls.partner = cls.env["res.partner"].create({
            name: "Proveedor de Prueba C.A.",
            supplier_rank: 1,
        })

        # Grupos de usuarios
        cls.group_requester = cls.env.ref("payment_request.group_payment_requester")
        cls.group_approver = cls.env.ref("payment_request.group_payment_approver")

        # Usuario solicitante de prueba
        cls.user_requester = cls.env["res.users"].create({
            name: "Usuario Solicitante",
            login: "solicitante_test",
            email: "solicitante@test.com",
            groups_id: [(6, 0, [cls.group_requester.id])]
        })

    def test_01_create_payment_request_success(self):
        """Verifica la creación correcta de la solicitud y secuencia."""
        req = self.env["payment.request"].create({
            partner_id: self.partner.id,
            amount: 150.0,
            concept: "Compra de insumos de oficina",
        })
        self.assertTrue(req.name.startswith("SP/"))
        self.assertEqual(req.state, "draft")

    def test_02_amount_validation(self):
        """Verifica que no se permita montos cero o negativos[cite: 6]."""
        with self.assertRaises(ValidationError):
            self.env["payment.request"].create({
                partner_id: self.partner.id,
                amount: 0.0,
                concept: "Monto cero",
            })

        with self.assertRaises(ValidationError):
            self.env["payment.request"].create({
                partner_id: self.partner.id,
                amount: -50.0,
                concept: "Monto negativo",
            })

    def test_03_immutability_after_submit(self):
        """Verifica que una solicitud enviada no se pueda editar[cite: 6]."""
        req = self.env["payment.request"].create({
            partner_id: self.partner.id,
            amount: 300.0,
            concept: "Prueba inmutabilidad",
        })
        req.action_submit()
        self.assertEqual(req.state, "submitted")

        # Intentar modificar el monto tras ser enviada debe fallar
        with self.assertRaises(ValidationError):
            req.write({amount: 500.0})

    def test_04_requester_cannot_approve(self):
        """Verifica que un usuario solicitante no pueda aprobar solicitudes[cite: 6]."""
        req = self.env["payment.request"].with_user(self.user_requester).create({
            partner_id: self.partner.id,
            amount: 1000.0,
            concept: "Prueba permisos aprobación",
        })
        req.action_submit()

        # El solicitante intenta aprobar su propia solicitud
        with self.assertRaises(Exception):
            req.with_user(self.user_requester).action_approve()