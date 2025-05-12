{
    'name': 'Network Drives',
    'version': '16.0.1.0.0',
    'category': 'Tools',
    'summary': 'Access network drives directly from Odoo',
    'description': """
        Open network drives directly from Odoo interface.
        Features:
        - Store network drive paths
        - Open network drives in browser
        - Easy access to shared folders
    """,
    'author': 'Your Company',
    'website': 'https://github.com/bmmaimba/network_drives',
    'depends': ['base'],
    'data': [
        'security/ir.model.access.csv',
        'views/network_drive_views.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}