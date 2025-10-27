#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os

# Add project root directory to Python path
project_root = os.path.dirname(os.path.dirname(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Add script directory to Python path
script_dir = os.path.dirname(__file__)
if script_dir not in sys.path:
    sys.path.insert(0, script_dir)

from PySide6.QtWidgets import QApplication
from firewall_manager import FirewallManager
from UI.gui import WindowsFirewallManager
from logger import get_logger

def main():
    """Main application entry point"""
    try:
        # Initialize logger
        logger = get_logger("firewall")
        logger.log_firewall_event("STARTUP", "TuxFw Application started")
        
        # Create application
        app = QApplication(sys.argv)
        
        # Set application style
        app.setStyle('Fusion')
        
        # Set application info
        app.setApplicationName("TuxFw")
        app.setApplicationVersion("0.0.1")
        app.setOrganizationName("Tuxxle")
        
        # Import translations
        from lang.translations import translations
        
        # Create firewall manager with translations
        firewall_manager = FirewallManager(translations=translations)
        
        # Create and show main window
        window = WindowsFirewallManager(firewall_manager)
        window.show()

        # Start event loop
        logger.log_firewall_event("SHUTDOWN", "TuxFw application closed normally")
        sys.exit(app.exec())
    except Exception as e:
        logger.log_error(f"Application crashed: {e}", context="main()")
        raise

if __name__ == "__main__":
    main()
