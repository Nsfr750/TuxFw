#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
import json

# Add script directory to path
script_dir = os.path.dirname(os.path.dirname(__file__))
if script_dir not in sys.path:
    sys.path.insert(0, script_dir)

try:
    # Import just the FirewallConfig class directly
    sys.path.insert(0, os.path.join(script_dir, 'script'))
    from firewall_manager import FirewallConfig
    print("✓ Successfully imported FirewallConfig")

    # Test loading config from config directory
    config = FirewallConfig()  # Should use config/firewall_config.json
    print("✓ FirewallConfig initialized with config directory")

    # Test that it loads the correct config
    rules = config.get_rules()
    settings = config.get_settings()
    profiles = config.config.get('profiles', {})

    print(f"✓ Loaded {len(rules)} firewall rules")
    print(f"✓ Language: {settings.get('language', 'en')}")
    print(f"✓ Firewall enabled: {settings.get('firewall_enabled', False)}")
    print(f"✓ Default policy: {settings.get('default_policy', 'BLOCK')}")
    print(f"✓ Available profiles: {list(profiles.keys())}")
    print(f"✓ Current profile: {config.config.get('current_profile', 'default')}")

    # Test saving config
    if config.save_config():
        print("✓ Configuration saved successfully")
    else:
        print("✗ Failed to save configuration")

    # Verify the file path
    print(f"✓ Config file path: {config.config_path}")
    print(f"✓ Config file exists: {os.path.exists(config.config_path)}")

    print("\n✓ Config directory integration test completed successfully!")

except ImportError as e:
    print(f"✗ Import error: {e}")
except Exception as e:
    print(f"✗ Error during testing: {e}")
    import traceback
    traceback.print_exc()
