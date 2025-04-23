from flask import Flask, send_from_directory, render_template_string, request
import os
from urllib.parse import quote

app = Flask(__name__)

# Set this to your mapped drive or UNC path
BASE_DIR = r"Z:\\"  # or use r"\\jpcfile01.jhbproperty.co.za\Site Inpection Pictures"

@app.route('/')
@app.route('/browse', defaults={'req_path': ''})
@app.route('/browse/<path:req_path>')
def browse(req_path):
    # Get the full absolute path
    abs_path = os.path.join(BASE_DIR, req_path)

    # Return 404 if path doesn't exist
    if not os.path.exists(abs_path):
        return f"<h1>404</h1><p>Path '{abs_path}' not found.</p>", 404

    # Check if path is a file and serve it
    if os.path.isfile(abs_path):
        dir_path = os.path.dirname(abs_path)
        filename = os.path.basename(abs_path)
        return send_from_directory(
            directory=dir_path,
            path=filename,
            as_attachment=True
        )

    # Show directory contents
    files = os.listdir(abs_path)
    files.sort()
    file_links = []

    for filename in files:
        full_path = os.path.join(req_path, filename)
        is_dir = os.path.isdir(os.path.join(BASE_DIR, full_path))
        slash = "/" if is_dir else ""
        link = f"/browse/{quote(full_path)}"
        file_links.append(f"<li><a href='{link}'>{filename}{slash}</a></li>")

    html = f"""
    <h1>Browsing: {req_path or "root"}</h1>
    <ul>
        {''.join(file_links)}
    </ul>
    """
    return render_template_string(html)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=16010, debug=True)