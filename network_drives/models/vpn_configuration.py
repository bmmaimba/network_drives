from odoo import models, fields, api

class VpnConfiguration(models.Model):
    _name = 'vpn.configuration'
    _description = 'VPN Configuration'

    name = fields.Char(required=True)
    server = fields.Char(required=True)
    port = fields.Integer(default=4433)
    domain = fields.Char()
    username = fields.Char(required=True)
    password = fields.Char(required=True)
    vpn_type = fields.Selection([
        ('sonicwall', 'SonicWall NetExtender')
    ], default='sonicwall', required=True)
