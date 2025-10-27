#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
import glob
import logging

# Add script directory to path
script_dir = os.path.dirname(os.path.dirname(__file__))
if script_dir not in sys.path:
    sys.path.insert(0, script_dir)

try:
    from script.logger import get_logger
    print("✓ Successfully imported logger module")

    # Test logger integration
    logger = get_logger("test_integration", log_level=logging.DEBUG)

    # Test all the logging functions
    logger.info("Integration test started")
    logger.log_firewall_event("TEST_EVENT", "Testing firewall event logging")
    logger.log_security_event("CONNECTION_TEST", source_ip="192.168.1.100", port=80, action="ALLOWED")
    logger.log_config_change("TEST_CONFIG", "Testing config change logging")
    logger.log_performance("TEST_OP", 15.5, operations=3)
    logger.log_error("Test error message", context="IntegrationTest.test_function")
    logger.warning("Test warning message")
    logger.critical("Test critical message")

    # Check if log files were created
    log_files = glob.glob("logs/test_integration_*.log")
    if log_files:
        print(f"✓ Log files created: {len(log_files)} file(s)")
        for log_file in log_files:
            print(f"  - {os.path.basename(log_file)}")

        # Show sample content
        with open(log_files[0], 'r') as f:
            content = f.read()
            sample_text = "Sample log content (first 500 chars):"
            print(f"\n{sample_text}")
            print("-" * 50)
            print(content[:500] + "..." if len(content) > 500 else content)
            print("-" * 50)
    else:
        print("✗ No log files created")

    # Test logger convenience functions
    from script.logger import log_firewall_event, log_error, log_security_event

    log_firewall_event("CONVENIENCE_TEST", "Testing convenience function")
    log_security_event("SECURITY_TEST", source_ip="10.0.0.1", action="BLOCKED")
    log_error("Convenience error test", context="TestScript")

    print("\n✓ All logger integration tests completed successfully!")

except ImportError as e:
    print(f"✗ Import error: {e}")
except Exception as e:
    print(f"✗ Error during testing: {e}")
    import traceback
    traceback.print_exc()
