#!/usr/bin/env python3
# -*- coding: utf-8 -*-

try:
    from PySide6.QtWidgets import QApplication
    print("PySide6 imported successfully")
except ImportError as e:
    print(f"Import error: {e}")
except Exception as e:
    print(f"Other error: {e}")
