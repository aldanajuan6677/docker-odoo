{
    'name': 'Solicitudes de Pago',
    'version': '17.0.1.0.0',
    'category': 'Accounting/Localisation',
    'summary': 'Gestión y control de solicitudes de pago a proveedores',
    'depends': ['base', 'mail', 'account'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'security/ir_rule.xml',
        'data/sequence_data.xml',
        'views/payment_request_views.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}