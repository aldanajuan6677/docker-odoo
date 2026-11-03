from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

class PaymentRequest(models.Model):
    _name = 'payment.request'
    _description = 'Solicitud de Pago a Proveedor'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date desc, id desc'

    name = fields.Char(
        string='Referencia', 
        required=True, 
        copy=False, 
        readonly=True, 
        default=lambda self: _('New')
    )
    partner_id = fields.Many2one(
        'res.partner', 
        string='Proveedor', 
        required=True, 
        tracking=True,
        domain=[('supplier_rank', '>', 0)]
    )
    user_id = fields.Many2one(
        'res.users', 
        string='Solicitante', 
        required=True, 
        default=lambda self: self.env.user, 
        tracking=True
    )
    amount = fields.Monetary(
        string='Monto', 
        required=True, 
        currency_field='currency_id', 
        tracking=True
    )
    currency_id = fields.Many2one(
        'res.currency', 
        string='Moneda', 
        required=True, 
        default=lambda self: self.env.company.currency_id, 
        tracking=True
    )
    date = fields.Date(
        string='Fecha', 
        required=True, 
        default=fields.Date.context_today, 
        tracking=True
    )
    concept = fields.Text(
        string='Concepto', 
        required=True, 
        tracking=True
    )
    state = fields.Selection([
        ('draft', 'Borrador'),
        ('submitted', 'Enviada'),
        ('approved', 'Aprobada'),
        ('paid', 'Pagada'),
        ('rejected', 'Rechazada')
    ], string='Estado', default='draft', tracking=True, required=True, index=True)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('payment.request') or _('New')
        return super().create(vals_list)

    @api.constrains('amount')
    def _check_amount(self):
        for record in self:
            if record.amount <= 0:
                raise ValidationError(_('El monto de la solicitud debe ser mayor a cero.'))

    def write(self, vals):
        # Restricción: Una solicitud enviada o en estados avanzados no se puede editar libremente por el solicitante
        for record in self:
            if record.state != 'draft' and not self.env.su:
                # Si intentan cambiar campos que no sean el estado (por ejemplo, proveedor, monto, etc.)
                restricted_fields = {'partner_id', 'amount', 'currency_id', 'date', 'concept'}
                if any(f in vals for f in restricted_fields):
                    raise ValidationError(_('Una solicitud que ya ha sido enviada no se puede modificar.'))
        return super().write(vals)

    # Métodos de cambio de estado
    def action_submit(self):
        for record in self:
            if record.state != 'draft':
                continue
            record.state = 'submitted'

    def action_approve(self):
        for record in self:
            if record.state != 'submitted':
                continue
            record.state = 'approved'

    def action_pay(self):
        for record in self:
            if record.state != 'approved':
                continue
            record.state = 'paid'

    def action_reject(self):
        for record in self:
            if record.state != 'submitted':
                continue
            record.state = 'rejected'

    def action_draft(self):
        for record in self:
            record.state = 'draft'