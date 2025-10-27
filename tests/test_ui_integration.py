#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os

# Add script directory to path
script_dir = os.path.dirname(os.path.dirname(__file__))
if script_dir not in sys.path:
    sys.path.insert(0, script_dir)

try:
    # Test importing all UI components
    from UI.about import AboutDialog
    from UI.menu import MenuManager
    from UI.view_logs import ViewLogsWindow
    from UI.sponsor import SponsorWindow
    from UI.help import HelpWindow

    print("✓ Successfully imported all UI components")

    # Test that main application can create instances
    from script.firewall_manager import FirewallConfig
    config = FirewallConfig()
    print("✓ FirewallConfig works")

    # Test translations
    from lang.translations import translations
    print(f"✓ Available languages: {list(translations.keys())}")

    # Check for new translation keys
    required_keys = ['logs', 'sponsors', 'help', 'export', 'close']
    for key in required_keys:
        if key in translations['en']:
            print(f"✓ Translation key found: {key}")
        else:
            print(f"✗ Translation key missing: {key}")

    print("\n✓ All UI components integration test completed!")

except ImportError as e:
    print(f"✗ Import error: {e}")
except Exception as e:
    print(f"✗ Error during testing: {e}")
    import traceback
    traceback.print_exc()
