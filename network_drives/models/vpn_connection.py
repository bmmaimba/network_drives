from odoo import models, fields, api
from ..utils.vpn_manager import VPNManager
import logging

_logger = logging.getLogger(__name__)

class VPNConnection(models.Model):
    _name = 'vpn.connection'
    _description = 'VPN Connection Manager'

    vpn_credential_id = fields.Many2one('vpn.credential', string='VPN Credential', required=True)
    start_time = fields.Datetime(string='Connection Start Time')
    end_time = fields.Datetime(string='Connection End Time')
    status = fields.Selection([
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('failed', 'Failed')
    ], default='inactive')

    def action_connect_vpn(self):
        vpn_manager = VPNManager()
        credential = self.vpn_credential_id

        try:
            success = vpn_manager.connect(
                vpn_type=credential.vpn_type,
                server=credential.server,
                port=credential.port,
                domain=credential.domain,
                username=credential.username,
                password=credential.password_encrypted  # Use decrypted password in actual implementation
            )

            if success:
                self.write({
                    'status': 'active',
                    'start_time': fields.Datetime.now()
                })
                return True
            else:
                self.write({'status': 'failed'})
                return False

        except Exception as e:
            _logger.error(f"VPN Connection failed: {str(e)}")
            self.write({'status': 'failed'})
            return False

    def action_disconnect_vpn(self):
        vpn_manager = VPNManager()
        try:
            vpn_manager.disconnect()
            self.write({
                'status': 'inactive',
                'end_time': fields.Datetime.now()
            })
            return True
        except Exception as e:
            _logger.error(f"VPN Disconnection failed: {str(e)}")
            return False