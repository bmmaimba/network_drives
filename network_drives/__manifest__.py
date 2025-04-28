{
    'name': 'Network Drives',
    'version': '16.0.1.0.0',
    'summary': 'Manage and open network drives',
    'description': 'A module to manage and open network drives with file paths.',
    'author': 'Your Name',
    'category': 'Tools',
    'depends': ['base'],
    'data': [
        'views/network_drive_views.xml',
        'views/drive_credential_views.xml',
        'security/ir.model.access.csv',
    ],
    "external_dependencies": {"python": [
        "pywin32",
    ]},
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}