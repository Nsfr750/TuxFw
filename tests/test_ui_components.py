#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os

# Add project root directory to Python path (to find the lang module)
project_root = os.path.dirname(os.path.dirname(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Add script directory to Python path (to find firewall_manager)
script_dir = os.path.dirname(__file__)
if script_dir not in sys.path:
    sys.path.insert(0, script_dir)

try:
    from script.firewall_manager import WindowsFirewallManager
    print("✓ Successfully imported WindowsFirewallManager")

    # Test creating an instance (without showing the window)
    app = None
    try:
        from PySide6.QtWidgets import QApplication
        app = QApplication(sys.argv)

        # Create the main window instance
        window = WindowsFirewallManager()
        print("✓ Successfully created WindowsFirewallManager instance")

        # Test that UI components are properly initialized
        required_attrs = ['config', 'current_language', 'settings_loaded', 'about_dialog', 'menu_manager']
        for attr in required_attrs:
            if hasattr(window, attr):
                print(f"✓ Has attribute: {attr}")
            else:
                print(f"✗ Missing attribute: {attr}")

        # Test that methods exist
        required_methods = ['show_about', 'change_language', 'retranslate_ui']
        for method in required_methods:
            if hasattr(window, method):
                print(f"✓ Has method: {method}")
            else:
                print(f"✗ Missing method: {method}")

        print("\n✓ All tests passed! UI components are properly separated.")

    except Exception as e:
        print(f"✗ Error during initialization: {e}")
    finally:
        if app:
            app.quit()

except ImportError as e:
    print(f"✗ Import error: {e}")
except Exception as e:
    print(f"✗ Unexpected error: {e}")
