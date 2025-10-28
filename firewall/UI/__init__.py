"""
User Interface Module

This package contains all the UI components for the TuxFw application,
including the main window, dialogs, and other GUI elements.
"""

from firewall.UI.gui import WindowsFirewallManager
from firewall.UI.about import AboutDialog
from firewall.UI.help import HelpWindow
from firewall.UI.menu import MenuManager
from firewall.UI.sponsor import SponsorDialog as SponsorWindow
from firewall.UI.view_logs import ViewLogsWindow

__all__ = [
    'WindowsFirewallManager',
    'AboutDialog',
    'HelpWindow',
    'MenuManager',
    'SponsorWindow',
    'ViewLogsWindow'
]
