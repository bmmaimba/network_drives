# controllers/main.py
from odoo import http
from odoo.http import request
import os
import io
import zipfile
import urllib.parse
import mimetypes
from odoo.http import content_disposition


class FileDownloadController(http.Controller):

    @http.route('/folder/open/', type='http', auth='user')
    def open_folder(self, path=None, **kwargs):
        if path and os.path.exists(path):
            return request.redirect(f"file://{path}")
        return request.not_found()

    @http.route('/folder/view/', type='http', auth='user')

    def view_file(self, path=None, **kwargs):
        """Open files"""
        """in Windows"""
        # path = f'file:///{path.replace("\\", "/")}'
        # path = fr"{path}"
        if not path or not os.path.exists(path) or not os.path.isfile(path):
            return "<h3>File not found</h3>"

        file_name = os.path.basename(path)
        mime_type, _ = mimetypes.guess_type(path)
        mime_type = mime_type or 'application/octet-stream'

        with open(path, 'rb') as f:
            file_data = f.read()

        return request.make_response(
            file_data,
            headers=[
                ('Content-Type', mime_type),
                ('Content-Disposition', f'inline; filename="{file_name}"')
            ]
        )


    @http.route('/file/download/<int:record_id>', type='http', auth='user')
    def download_file(self, record_id):
        record = request.env['network.drive.content'].browse(record_id)
        if not record.exists():
            return request.not_found()
        if record.item_type == 'File':
            with open(record.path, 'rb') as f:
                file_data = f.read()
            filename = os.path.basename(record.path)
            return request.make_response(file_data, [
                ('Content-Type', 'application/octet-stream'),
                ('Content-Disposition', f'attachment; filename="{filename}"')
            ])

        elif record.item_type == 'Folder':
            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, 'w',
                                 zipfile.ZIP_DEFLATED) as zip_file:
                for root, _, files in os.walk(record.path):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, record.path)
                        zip_file.write(file_path, arcname)

            zip_buffer.seek(0)
            zip_data = zip_buffer.read()

            return request.make_response(zip_data, [
                ('Content-Type', 'application/zip'),
                ('Content-Disposition',
                 f'attachment; filename="{record.name}.zip"')
            ])

        return request.not_found()
