from odoo import fields, models

class ShopApiLog(models.Model):
    _name = "shop.api.log"
    _description = "Log de llamadas a la API de la tienda"
    _order = "create_date desc"

    endpoint = fields.Char(string="Endpoint", required=True)
    user_id = fields.Many2one("res.users", string="Usuario", ondelete="set null", help="Usuario autenticado mediante API Key")
    response_code = fields.Char(string="Código de Respuesta", required=True)
    duration = fields.Float(string="Duración (s)", digits=(10, 4), help="Tiempo de ejecución de la petición en segundos")