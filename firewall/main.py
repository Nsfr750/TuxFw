#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TuxFw - Firewall Manager

This is the main entry point for the TuxFw application.
It simply imports and runs the application from the script package.
"""

import os
import sys

def main():
    """Run the TuxFw application."""
    try:
        # Add the script directory to the path if needed
        script_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'script')
        if script_dir not in sys.path:
            sys.path.insert(0, script_dir)
        
        # Import and run the main application
        from script.main import main as app_main
        return app_main()
    except ImportError as e:
        print(f"Error: Failed to import application: {e}")
        print(f"Python path: {sys.path}")
        return 1
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
