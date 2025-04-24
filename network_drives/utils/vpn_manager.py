import subprocess
import logging
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

class VPNManager:
    def connect(self, credential):
        try:
            cmd = [
                'netExtender',
                f'{credential.server}:{credential.port}',
                '-u', credential.username,
                '-p', credential.password,
                '-d', credential.domain
            ]
            subprocess.run(cmd, check=True)
            return True
        except Exception as e:
            _logger.error(f"VPN connection failed: {str(e)}")
            return False

    def disconnect(self):
        try:
            subprocess.run(['netExtender', '-stop'], check=True)
            return True
        except Exception as e:
            _logger.error(f"VPN disconnection failed: {str(e)}")
            return False