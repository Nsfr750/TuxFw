#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test script to verify PySide6 firewall application components
"""

import sys
import os

def test_imports():
    """Test that all required modules can be imported"""
    try:
        import PySide6
        print("✓ PySide6 imported successfully")
    except ImportError as e:
        print(f"✗ PySide6 import failed: {e}")
        return False

    try:
        from PySide6.QtWidgets import QApplication, QMainWindow
        print("✓ PySide6.QtWidgets imported successfully")
    except ImportError as e:
        print(f"✗ PySide6.QtWidgets import failed: {e}")
        return False

    try:
        import qrcode
        print("✓ qrcode imported successfully")
    except ImportError as e:
        print(f"✗ qrcode import failed: {e}")
        return False

    try:
        from wand.image import Image as WandImage
        print("✓ Wand imported successfully")
    except ImportError as e:
        print(f"✗ Wand import failed: {e}")
        return False

    return True

def test_config():
    """Test configuration file operations"""
    config_path = "script/firewall_config.json"
    if os.path.exists(config_path):
        print(f"✓ Configuration file exists: {config_path}")
        try:
            import json
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            print("✓ Configuration file is valid JSON")
            print(f"  - Rules: {len(config.get('firewall_rules', []))}")
            print(f"  - Profiles: {len(config.get('profiles', {}))}")
            return True
        except Exception as e:
            print(f"✗ Configuration file error: {e}")
            return False
    else:
        print(f"✗ Configuration file not found: {config_path}")
        return False

def test_translations():
    """Test translation system"""
    try:
        sys.path.append('lang')
        from translations import translations
        print("✓ Translation system imported successfully")
        print(f"  - Languages: {list(translations.keys())}")
        print(f"  - English strings: {len(translations['en'])}")
        print(f"  - Italian strings: {len(translations['it'])}")
        return True
    except ImportError as e:
        print(f"✗ Translation import failed: {e}")
        return False

def main():
    """Run all tests"""
    print("Testing Python Firewall Manager Components")
    print("=" * 50)

    tests = [
        ("Import Tests", test_imports),
        ("Configuration Tests", test_config),
        ("Translation Tests", test_translations)
    ]

    passed = 0
    total = len(tests)

    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        if test_func():
            passed += 1

    print("\n" + "=" * 50)
    print(f"Test Results: {passed}/{total} passed")

    if passed == total:
        print("✓ All tests passed! Application is ready to run.")
        print("\nTo start the application:")
        print("  python main.py")
        print("  python script/main.py")
    else:
        print("✗ Some tests failed. Please check the errors above.")
        return 1

    return 0

if __name__ == "__main__":
    sys.exit(main())
