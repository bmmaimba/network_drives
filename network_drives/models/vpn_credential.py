from odoo import models, fields, api
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)

class VPNCredential(models.Model):
    _name = 'vpn.credential'
    _description = 'VPN Credentials'

    name = fields.Char(string='Name', required=True)
    vpn_type = fields.Selection([
        ('sonicwall', 'SonicWall NetExtender'),
        ('cisco', 'Cisco AnyConnect'),
        # Add other VPN types as needed
    ], string='VPN Type', required=True)

    server = fields.Char(string='Server', required=True)
    port = fields.Integer(string='Port', default=4433)
    domain = fields.Char(string='Domain')
    username = fields.Char(string='Username', required=True)
    password = fields.Char(string='Password', required=True)

    # For security, store password encrypted
    password_encrypted = fields.Char(string='Encrypted Password', readonly=True)

    active = fields.Boolean(default=True)
    state = fields.Selection([
        ('disconnected', 'Disconnected'),
        ('connected', 'Connected'),
        ('error', 'Error')
    ], default='disconnected', string='Status')

    last_connection = fields.Datetime(string='Last Connection')
    last_error = fields.Text(string='Last Error')

    @api.model
    def create(self, vals):
        # Encrypt password before storing
        if vals.get('password'):
            vals['password_encrypted'] = self._encrypt_password(vals['password'])
            vals['password'] = '********'  # Don't store plain password
        return super(VPNCredential, self).create(vals)

    def _encrypt_password(self, password):
        # Implement proper encryption here
        return password  # Placeholder