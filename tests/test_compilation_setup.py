#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
from pathlib import Path

def test_compilation_setup():
    """Test compilation setup and assets"""

    print("Testing compilation setup...")

    # Check assets directory
    assets_dir = Path("assets")
    if assets_dir.exists():
        print(f"Assets directory exists: {assets_dir}")
    else:
        print(f"Assets directory missing: {assets_dir}")
        return False

    # Check version info file
    version_file = assets_dir / "version_info.txt"
    if version_file.exists():
        print("version_info.txt exists")
    else:
        print("version_info.txt missing")
        return False

    # Check logo file
    logo_file = assets_dir / "logo.png"
    if logo_file.exists():
        print("logo.png exists")
    else:
        print("logo.png missing")

    # Check setup directory
    setup_dir = Path("setup")
    if setup_dir.exists():
        print(f"Setup directory exists: {setup_dir}")
    else:
        print(f"Setup directory missing: {setup_dir}")
        return False

    # Check compile script
    compile_script = setup_dir / "compile_app.py"
    if compile_script.exists():
        print("compile_app.py exists")
    else:
        print("compile_app.py missing")
        return False

    # Check if PyInstaller is available
    try:
        import PyInstaller
        print("PyInstaller is available")
    except ImportError:
        print("PyInstaller not installed")
        print("Install with: pip install pyinstaller")

    print("\nCompilation setup test completed!")
    return True

if __name__ == "__main__":
    test_compilation_setup()
