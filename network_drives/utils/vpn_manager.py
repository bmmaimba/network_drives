import subprocess
import os
import logging
import platform

_logger = logging.getLogger(__name__)

class VPNManager:
    def __init__(self):
        self.system = platform.system()
        self.vpn_paths = {
            'Windows': {
                'sonicwall': r"C:\Program Files\SonicWall\NetExtender\NECLI.exe",
                'cisco': r"C:\Program Files (x86)\Cisco\Cisco AnyConnect Secure Mobility Client\vpncli.exe"
            },
            'Linux': {
                'sonicwall': "/usr/sbin/netExtender",
                'cisco': "/opt/cisco/anyconnect/bin/vpn"
            }
        }

    def get_vpn_path(self, vpn_type):
        return self.vpn_paths.get(self.system, {}).get(vpn_type)

    def connect(self, vpn_type, server, port, domain, username, password):
        vpn_path = self.get_vpn_path(vpn_type)
        if not vpn_path:
            raise Exception(f"VPN client not found for {vpn_type} on {self.system}")

        if vpn_type == 'sonicwall':
            return self._connect_sonicwall(vpn_path, server, port, domain, username, password)
        elif vpn_type == 'cisco':
            return self._connect_cisco(vpn_path, server, username, password)
        else:
            raise Exception(f"Unsupported VPN type: {vpn_type}")

    def _connect_sonicwall(self, vpn_path, server, port, domain, username, password):
        server_address = f"{server}:{port}"
        command = [
            vpn_path,
            '-s', server_address,
            '-d', domain,
            '-u', username,
            '-p', password,
            '-U', '1'
        ]

        try:
            result = subprocess.run(command,
                                  check=True,
                                  capture_output=True,
                                  text=True)
            _logger.info("VPN Connected successfully")
            return True
        except subprocess.CalledProcessError as e:
            _logger.error(f"VPN Connection failed: {e.stderr}")
            return False

    def disconnect(self):
        if self.system == 'Windows':
            os.system("taskkill /IM NECLI.exe /F")
        else:
            os.system("pkill netExtender")
        return True