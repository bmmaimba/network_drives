from odoo import models, fields, api
from odoo.exceptions import UserError
import os
import zipfile
import io
import logging
from odoo.http import request

_logger = logging.getLogger(__name__)

class NetworkDrive(models.Model):
    _name = 'network.drive'
    _description = 'Network Drive'

    name = fields.Char(string='Name', required=True)
    file_path = fields.Char(string='File Path', required=True)
    content_ids = fields.One2many('network.drive.content', 'drive_id', string='Contents')
    vpn_required = fields.Boolean(string='Requires VPN', default=True,
                                help='Check if this network drive requires VPN connection')
    vpn_credential_id = fields.Many2one('vpn.credential', string='VPN Credential',
                                      help='Select the VPN credential to use for this drive')

    # Access Rights Fields
    allowed_user_ids = fields.Many2many('res.users', string='Allowed Users',
                                      help='Users who can access this record.')
    allowed_group_ids = fields.Many2many('res.groups', string='Allowed Groups',
                                       help='Groups whose members can access this record.')
    is_networkdrive = fields.Boolean(string="Is Network Drives")
    driver_credential_id = fields.Many2one('driver.credential', string="Driver Credential")

    # VPN Status Fields
    vpn_status = fields.Selection([
        ('not_required', 'VPN Not Required'),
        ('disconnected', 'VPN Disconnected'),
        ('connected', 'VPN Connected'),
        ('error', 'VPN Error')
    ], compute='_compute_vpn_status', string='VPN Status')

    last_vpn_error = fields.Text(string='Last VPN Error', readonly=True)

    @api.depends('vpn_required', 'vpn_credential_id')
    def _compute_vpn_status(self):
        for record in self:
            if not record.vpn_required:
                record.vpn_status = 'not_required'
                continue

            vpn_connection = self.env['vpn.connection'].search(
                [('vpn_credential_id', '=', record.vpn_credential_id.id)],
                limit=1
            )
            if vpn_connection:
                record.vpn_status = vpn_connection.status
            else:
                record.vpn_status = 'disconnected'

    @api.model
    def create(self, vals):
        # Add administrator to allowed users and groups
        admin_group = self.env.ref('base.group_system')
        admin_user = self.env.ref('base.user_admin')

        if 'allowed_group_ids' not in vals or not vals.get('allowed_group_ids'):
            vals['allowed_group_ids'] = [(4, admin_group.id)]
        elif isinstance(vals['allowed_group_ids'], list):
            vals['allowed_group_ids'].append((4, admin_group.id))

        if 'allowed_user_ids' not in vals or not vals.get('allowed_user_ids'):
            vals['allowed_user_ids'] = [(4, admin_user.id)]
        elif isinstance(vals['allowed_user_ids'], list):
            vals['allowed_user_ids'].append((4, admin_user.id))

        return super(NetworkDrive, self).create(vals)

    def write(self, vals):
        # Prevent removal of Administrator group and admin user
        admin_group = self.env.ref('base.group_system')
        admin_user = self.env.ref('base.user_admin')

        if 'allowed_group_ids' in vals:
            for record in self:
                if admin_group.id not in [cmd[1] for cmd in vals.get('allowed_group_ids', []) if cmd[0] == 4] + [g.id for g in record.allowed_group_ids]:
                    vals['allowed_group_ids'].append((4, admin_group.id))

        if 'allowed_user_ids' in vals:
            for record in self:
                if admin_user.id not in [cmd[1] for cmd in vals.get('allowed_user_ids', []) if cmd[0] == 4] + [u.id for u in record.allowed_user_ids]:
                    vals['allowed_user_ids'].append((4, admin_user.id))

        return super(NetworkDrive, self).write(vals)

    def ensure_vpn_connection(self):
        """Ensure VPN connection is established if required"""
        self.ensure_one()

        if not self.vpn_required:
            return True

        if not self.vpn_credential_id:
            raise UserError('VPN credentials not configured for this network drive.')

        vpn_connection = self.env['vpn.connection'].search(
            [('vpn_credential_id', '=', self.vpn_credential_id.id)],
            limit=1
        )

        if not vpn_connection:
            vpn_connection = self.env['vpn.connection'].create({
                'vpn_credential_id': self.vpn_credential_id.id,
                'status': 'inactive'
            })

        if vpn_connection.status != 'active':
            try:
                success = vpn_connection.action_connect_vpn()
                if not success:
                    self.last_vpn_error = "Failed to establish VPN connection"
                    raise UserError('Failed to establish VPN connection. Please check VPN credentials and try again.')
            except Exception as e:
                self.last_vpn_error = str(e)
                raise UserError(f'VPN Connection Error: {str(e)}')

        return True

    def action_refresh_contents(self):
        """Refresh the contents of the network drive"""
        self.ensure_one()
        _logger.info(f"Refreshing contents for drive: {self.name}")

        try:
            # Ensure VPN connection if required
            self.ensure_vpn_connection()

            # Clear existing contents
            self.content_ids.unlink()

            if not self.file_path:
                return

            if self.is_networkdrive:
                self._handle_network_drive_connection()

            path = self.file_path.replace('file:///', '')
            if not os.path.exists(path):
                _logger.warning(f"Path does not exist: {path}")
                return

            contents = self._scan_directory(path)
            if contents:
                self.env['network.drive.content'].create(contents)

        except Exception as e:
            _logger.error(f"Error refreshing drive contents: {str(e)}")
            raise UserError(f"Failed to refresh drive contents: {str(e)}")

    def _handle_network_drive_connection(self):
        """Handle network drive connection using credentials"""
        if not self.driver_credential_id:
            raise UserError('Driver credentials not configured for this network drive.')

        driver_credential = self.driver_credential_id.sudo()
        drive_letter = driver_credential.drive_letter
        network_share = fr'{self.file_path}'
        username = driver_credential.user_name
        password = driver_credential.password

        try:
            # Map the network drive
            os.system(f'net use {drive_letter} "{network_share}" /user:{username} {password}')

            # Test the connection
            test_path = rf'{drive_letter}\\'
            if not os.path.exists(test_path):
                raise UserError(f"Failed to access mapped drive: {network_share}")

        except Exception as e:
            _logger.error(f"Network drive mapping failed: {str(e)}")
            raise UserError(f"Failed to map network drive: {str(e)}")

    def _scan_directory(self, path):
        """Scan directory and return contents"""
        contents = []
        try:
            for item in os.listdir(path):
                item_path = os.path.join(path, item)
                item_type = 'Folder' if os.path.isdir(item_path) else 'File'
                contents.append({
                    'name': item,
                    'path': item_path,
                    'item_type': item_type,
                    'drive_id': self.id,
                })
        except Exception as e:
            _logger.error(f"Error scanning directory {path}: {str(e)}")
            raise UserError(f"Failed to scan directory: {str(e)}")

        return contents

    def _search(self, args, offset=0, limit=None, order=None, count=False, access_rights_uid=None):
        """Override search to implement access rights"""
        user = self.env.user
        if not user.has_group('base.group_system'):
            args = [
                '|',
                ('allowed_user_ids', 'in', [user.id]),
                ('allowed_group_ids', 'in', user.groups_id.ids)
            ] + (args or [])
        return super(NetworkDrive, self)._search(
            args, offset=offset, limit=limit, order=order,
            count=count, access_rights_uid=access_rights_uid
        )

class NetworkDriveContent(models.Model):
    _name = 'network.drive.content'
    _description = 'Network Drive Content'
    _parent_store = True

    name = fields.Char(string='Name', required=True)
    path = fields.Char(string='Path', required=False)
    item_type = fields.Selection([
        ('File', 'File'),
        ('Folder', 'Folder')
    ], string='Type', required=False)
    drive_id = fields.Many2one('network.drive', string='Drive',
                              required=True, ondelete='cascade')
    parent_id = fields.Many2one('network.drive.content', string='Parent',
                               index=True, ondelete='cascade')
    child_ids = fields.One2many('network.drive.content', 'parent_id',
                               string='Children')
    parent_path = fields.Char(index=True)
    has_children = fields.Boolean(string='Has Children',
                                compute='_compute_has_children', store=True)
    display_type = fields.Selection([
        ('line_section', 'Section'),
        ('line_note', 'Note')
    ], default=False, readonly=True)

    @api.depends('child_ids')
    def _compute_has_children(self):
        for record in self:
            record.has_children = len(record.child_ids) > 0

    def action_expand_folder(self):
        """Expand a folder to show its contents"""
        self.ensure_one()

        # Ensure VPN connection if required
        self.drive_id.ensure_vpn_connection()

        if self.item_type != 'Folder' or not os.path.exists(self.path):
            return

        existing_paths = self.child_ids.mapped('path')
        contents = []

        # Add section header
        self.env['network.drive.content'].sudo().create({
            'name': 'Sub Folders: ' + self.name,
            'display_type': 'line_section',
            'drive_id': self.drive_id.id,
            'path': self.path + '/',
            'parent_id': self.id,
        })

        try:
            for item in os.listdir(self.path):
                item_path = os.path.join(self.path, item)
                if item_path not in existing_paths:
                    item_type = 'Folder' if os.path.isdir(item_path) else 'File'
                    contents.append({
                        'name': item,
                        'path': item_path,
                        'item_type': item_type,
                        'drive_id': self.drive_id.id,
                        'parent_id': self.id,
                    })
        except Exception as e:
            _logger.error(f"Error expanding folder {self.path}: {str(e)}")
            raise UserError(f"Failed to expand folder: {str(e)}")

        if contents:
            self.env['network.drive.content'].create(contents)

    def action_collapse_folder(self):
        """Collapse a folder by removing its children"""
        if self.item_type == 'Folder':
            self.child_ids.unlink()

    def action_download(self):
        """Download a file"""
        self.ensure_one()

        # Ensure VPN connection if required
        self.drive_id.ensure_vpn_connection()

        return {
            'type': 'ir.actions.act_url',
            'url': f'/file/download/{self.id}',
            'target': 'self',
        }

    def action_open_folder(self):
        """Open a folder"""
        self.ensure_one()

        # Ensure VPN connection if required
        self.drive_id.ensure_vpn_connection()

        if self.item_type == 'Folder' and os.path.exists(self.path):
            url = f"/folder/open/?path={self.path}"
            return {
                'type': 'ir.actions.act_url',
                'url': url,
                'target': 'new',
            }
        else:
            _logger.error(f"Path does not exist or is not a folder: {self.path}")
            return False