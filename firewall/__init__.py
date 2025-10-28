"""
TuxFw - Firewall Manager

This is the main package for the TuxFw firewall management application.
It provides a user interface for managing nftables firewall rules.
"""

__version__ = "0.0.1"
__author__ = "Nsfr750"
__email__ = "nsfr750@yandex.com"
__license__ = "GPLv3"

# Import main components for easier access
from firewall.script.firewall_manager import FirewallManager
from firewall.script.logger import get_logger