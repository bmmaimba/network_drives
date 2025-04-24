from odoo import models, fields, api
from odoo.exceptions import UserError

class VPNConnection(models.Model):
    _name = 'vpn.connection'
    _description = 'VPN Connection'

    name = fields.Char(required=True)
    credential_id = fields.Many2one('vpn.credential', required=True)
    status = fields.Selection([
        ('disconnected', 'Disconnected'),
        ('connected', 'Connected'),
        ('error', 'Error')
    ], default='disconnected')
    last_error = fields.Text()
    
    def connect(self):
        vpn_manager = self.env['utils.vpn_manager'].get_instance()
        return vpn_manager.connect(self.credential_id)
        
    def disconnect(self):
        vpn_manager = self.env['utils.vpn_manager'].get_instance()
        return vpn_manager.disconnect()