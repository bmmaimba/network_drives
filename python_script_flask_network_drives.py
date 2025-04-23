import http.server
import socketserver
import os
# Path to the network share (can be UNC path if accessible, or mapped drive like Z:)
SHARE_PATH = r"Z:\\" # or r"\\jpcfile01.jhbproperty.co.za\Site Inpection Pictures"
PORT = 8000
os.chdir(SHARE_PATH)
Handler = http.server.SimpleHTTPRequestHandler
httpd = socketserver.TCPServer(("", PORT), Handler)
print(f"Serving '{SHARE_PATH}' at http://localhost:{PORT}")
httpd.serve_forever()