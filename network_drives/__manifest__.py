{
    'name': 'Network Drives',
    'version': '16.0.1.0.0',
    'summary': 'Manage and open network drives with VPN support',
    'description': '''
        A module to manage VPN connections and network drives with file paths.
        Features:
        - Network drive management
        - VPN connection support
        - File system browsing
        - Access control
    ''',
    'author': 'Your Name',
    'website': 'https://www.yourcompany.com',
    'category': 'Tools',
    'depends': [
        'base',
        'web',
    ],
    'data': [
        'security/network_drive_security.xml',
        'security/ir.model.access.csv',
        'data/network_drive_actions.xml',
        'data/vpn_actions.xml',
        'views/driver_credential_views.xml',
        'views/network_drive_views.xml',
        'views/vpn_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'network_drives/static/src/js/*.js',
            'network_drives/static/src/xml/*.xml',
        ],
    },
    'images': ['static/description/icon.png'],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}