#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TuxFw - Firewall Manager

This is the main entry point for the TuxFw application.
It sets up the Python path and imports the application from the firewall.script package.
"""

import os
import sys

def main():
    """Run the TuxFw application."""
    try:
        # Get the project root directory (one level up from firewall/)
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        # Add project root to Python path if not already there
        if project_root not in sys.path:
            sys.path.insert(0, project_root)
            
        # Now import using the full package path
        from firewall.script.main import main as app_main
        return app_main()
        
    except ImportError as e:
        print(f"Error: Failed to import application: {e}")
        print(f"Current working directory: {os.getcwd()}")
        print(f"Python path: {sys.path}")
        return 1
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
