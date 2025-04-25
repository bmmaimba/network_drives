{
    'name': 'Network Drives',
    'version': '16.0.1.0.0',
    'summary': 'Manage and open network drives',
    'description': 'A module to manage and open network drives with file paths.',
    'author': 'Your Name',
    'category': 'Tools',
    'depends': ['base'],
    'data': [
        'security/ir.model.access.csv',
        'views/network_drive_views.xml',
        'views/driver_credential_views.xml',
        'views/vpn_configuration_views.xml',
        'data/network_drive_actions.xml',
    ],
    "external_dependencies": {"python": [
        "pywin32",
    ]},
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}