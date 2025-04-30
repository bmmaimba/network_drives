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
        """Open the folders"""
        """in Windows"""
        # path = f'file:///{path.replace("\\", "/")}'
        # path = fr"{path}"

        if not path or not os.path.exists(path):
            return "<h3>Path not found</h3>"

        if os.path.isfile(path):
            return http.local_redirect(f"/folder/view/?path={path}")

        entries = []
        for entry in os.listdir(path):
            full_path = os.path.join(path, entry)
            entries.append({
                'name': entry,
                'path': full_path,
                'is_dir': os.path.isdir(full_path),
            })

        html = f"<h2>📁 Folder: {path}</h2><ul>"
        for entry in entries:
            if entry['is_dir']:
                html += f"<li>📁 <a href='/folder/open/?path={entry['path']}'>{entry['name']}</a></li>"
            else:
                html += f"<li>📄 <a href='/folder/view/?path={entry['path']}' target='_blank'>{entry['name']}</a></li>"
        html += "</ul>"

        return html

    @http.route('/network/open/', type='http', auth='user')
    def open_network_path(self, path=None, **kwargs):
        if not path:
            return "<h3>Path not specified</h3>"

        clean_path = path.replace('/', '\\')
        if not clean_path.startswith('\\\\'):
            clean_path = '\\\\' + clean_path.lstrip('\\')

        file_url = f"file:///{clean_path}"

        html = f"""
        <html>
        <head>
            <title>Opening Network Path</title>
            <script type="text/javascript">
                window.onload = function() {{
                    window.location.href = "{file_url}";
                    setTimeout(function() {{
                        window.close();
                    }}, 1000);
                }};
            </script>
        </head>
        <body>
            <h3>Opening network path: {clean_path}</h3>
            <p>If the path doesn't open automatically, <a href="{file_url}">click here</a>.</p>
        </body>
        </html>
        """
        return html

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
