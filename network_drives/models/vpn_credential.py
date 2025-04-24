from odoo import models, fields

class VPNCredential(models.Model):
    _name = 'vpn.credential'
    _description = 'VPN Credentials'

    name = fields.Char(required=True)
    server = fields.Char(required=True)
    port = fields.Integer(default=4433)
    domain = fields.Char(required=True)
    username = fields.Char(required=True)
    password = fields.Char(required=True)