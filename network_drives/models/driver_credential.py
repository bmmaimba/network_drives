from odoo import models, fields


class NetworkDriveCredential(models.Model):
    _name = 'drive.credential'
    _description = 'Network Drive Credential'
    _rec_name = 'drive_letter'

    drive_letter = fields.Char(string="Drive Letter", required=True)
    network_share = fields.Char(string="Network Share", required=True)
    user_name = fields.Char(string="Username", required=True)
    password = fields.Char(string="Password", required=True)

