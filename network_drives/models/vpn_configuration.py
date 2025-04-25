from odoo import models, fields

class VPNConfiguration(models.Model):
    _name = 'vpn.configuration'
    _description = 'VPN Configuration'

    name = fields.Char(required=True)
    server = fields.Char(required=True)
    domain = fields.Char(required=True)
    username = fields.Char(required=True)
    password = fields.Char(required=True)
