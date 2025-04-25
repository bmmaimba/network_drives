from odoo import models, fields, api
import subprocess

class VPNConfiguration(models.Model):
    _name = 'vpn.configuration'
    _description = 'VPN Configuration'

    name = fields.Char(required=True)
    server = fields.Char(required=True)
    domain = fields.Char(required=True)
    username = fields.Char(required=True)
    password = fields.Char(required=True)
    status = fields.Selection([
        ('disconnected', 'Disconnected'),
        ('connected', 'Connected')
    ], default='disconnected')

    def connect(self):
        if self.status == 'connected':
            return
        try:
            subprocess.run([
                'netExtender',
                self.server,
                '-d', self.domain,
                '-u', self.username,
                '-p', self.password
            ])
            self.status = 'connected'
        except Exception as e:
            raise UserError(f"VPN Connection failed: {str(e)}")
