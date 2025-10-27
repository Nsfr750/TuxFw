#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
import logging

# Add script directory to path
script_dir = os.path.dirname(os.path.dirname(__file__))
if script_dir not in sys.path:
    sys.path.insert(0, script_dir)

try:
    # Test logger integration with main application
    from script.firewall_manager import FirewallConfig
    from script.logger import get_logger

    print("✓ Successfully imported main application components")

    # Test FirewallConfig
    config = FirewallConfig("script/firewall_config.json")
    print("✓ FirewallConfig initialized")

    # Test logger integration
    logger = get_logger("firewall_test")
    logger.log_firewall_event("APP_TEST", "Testing logger integration with main app")
    logger.log_config_change("TEST_RULE", "Testing rule logging")

    # Check if log files were created for the main app
    import glob
    log_files = glob.glob("logs/firewall_test_*.log")
    if log_files:
        print(f"✓ Main app log files created: {len(log_files)} file(s)")
        for log_file in log_files:
            print(f"  - {os.path.basename(log_file)}")
    else:
        print("✗ No main app log files created")

    print("\n✓ Main application logger integration test completed!")

except ImportError as e:
    print(f"✗ Import error: {e}")
except Exception as e:
    print(f"✗ Error during testing: {e}")
    import traceback
    traceback.print_exc()
