import socket
import subprocess

class VPNManager:
    def check_connection_status(self, connection):
        if connection.vpn_type == 'sonicwall':
            return self._check_sonicwall_status(connection)
        elif connection.vpn_type == 'cisco':
            return self._check_cisco_status(connection)
        return 'disconnected'

    def _check_sonicwall_status(self, connection):
        try:
            sock = socket.create_connection((connection.server.split(':')[0], 4433), timeout=5)
            sock.close()
            return 'connected'
        except:
            return 'disconnected'

    def _check_cisco_status(self, connection):
        try:
            result = subprocess.run(['vpn', 'status'], capture_output=True, text=True)
            return 'connected' if 'Connected' in result.stdout else 'disconnected'
        except:
            return 'disconnected'