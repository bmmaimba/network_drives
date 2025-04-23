from odoo import models, fields, api
import datetime

class VPNConnection(models.Model):
    _name = 'vpn.connection'
    _description = 'VPN Connection'

    name = fields.Char(required=True)
    server = fields.Char(required=True)
    domain = fields.Char()
    username = fields.Char(required=True)
    password = fields.Char(required=True)
    vpn_type = fields.Selection([
        ('sonicwall', 'SonicWall NetExtender'),
        ('cisco', 'Cisco VPN')
    ], required=True)
    status = fields.Selection([
        ('connected', 'Connected'),
        ('disconnected', 'Disconnected')
    ], default='disconnected')
    last_check_time = fields.Datetime()
    auto_reconnect = fields.Boolean(default=True)

    def _monitor_vpn_connections(self):
        vpn_manager = self.env['utils.vpn_manager'].get_instance()
        for connection in self.search([]):
            status = vpn_manager.check_connection_status(connection)
            if status != connection.status:
                connection.status = status
                if status == 'disconnected' and connection.auto_reconnect:
                    connection.connect()
            connection.last_check_time = fields.Datetime.now()