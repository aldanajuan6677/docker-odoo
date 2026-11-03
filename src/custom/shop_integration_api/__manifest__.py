{
    'name': 'Shop Integration API',
    'version': '17.0.1.0.0',
    'category': 'Website',
    'summary': 'Endpoints para integración de productos con tienda en línea',
    'depends': ['base', 'stock', 'sale'],
    'data': [
        'security/ir.model.access.csv',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}