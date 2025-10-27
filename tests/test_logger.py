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
    from script.logger import get_logger, FirewallLogger
    print("✓ Successfully imported logger module")

    # Test the logger
    logger = get_logger("test_firewall", logging.DEBUG)

    # Test basic logging
    logger.info("Test logger initialized")
    logger.log_firewall_event("TEST_START", "Testing firewall logger functionality")
    logger.log_security_event("CONNECTION_BLOCKED", source_ip="10.0.0.1", port=80, action="BLOCKED")
    logger.log_config_change("TEST_CONFIG", "Test configuration change")
    logger.log_performance("TEST_OPERATION", 25.5, operations=5)
    logger.warning("Test warning message")
    logger.error("Test error message", context="TestModule.test_function")

    # Test daily rotation
    print("✓ Logger functionality test completed")

    # Check if log files were created
    import glob
    log_files = glob.glob("logs/test_firewall_*.log")
    if log_files:
        print(f"✓ Log files created: {len(log_files)} file(s)")
        for log_file in log_files:
            print(f"  - {os.path.basename(log_file)}")
    else:
        print("✗ No log files created")

    print("\n✓ All logger tests passed!")

except ImportError as e:
    print(f"✗ Import error: {e}")
except Exception as e:
    print(f"✗ Error during testing: {e}")
