#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Version information for TuxFw Firewall.
"""

# Version as a tuple (major, minor, patch)
VERSION = (0, 1, 0)

# String version
__version__ = ".".join(map(str, VERSION))

# Detailed version information
__status__ = "stable"
__author__ = "Nsfr750"
__maintainer__ = "Nsfr750"
__organization__ = 'Tuxxle'
__copyright__ = '© 2025 Nsfr750 - All Rights Reserved'
__email__ = "nsfr750@yandex.com"
__license__ = "GPL-3.0"

# Build information
__build__ = ""
__date__ = "2025-10-28"

# Version description
__description__ = "A modern firewall for Linux/windows"

# Dependencies
__requires__ = [
    "PySide6>=6.6.0",
    "Wand>=0.6.11",
    "wheel>=0.42.0",
    "shiboken6>=6.6.0",
    "psutil>=5.9.7",
    "pyrewall>=0.12.0",
    "pip-nftables>=1.0.2.post1",
    "pytest>=8.3.4",
    "pyinstaller>=6.11.0",
    "qrcode>=8.2",
    "geoip2>=4.2.0",
    "requests>=2.25.1",
    "aiohttp>=3.8.0"
]

# Version as a tuple for comparison
version_info = tuple(map(int, __version__.split('.')))

# Changelog
__changelog__ = """
## [0.1.0] - 2025-10-28

### Added
- Monitoring tab with real-time bandwidth charts (QtCharts), connections table, and security alerts
- Enhanced Security: rate limiting, GeoIP blocking (GeoLite2), IP reputation feeds, port knocking
- VPN integration: OpenVPN (process backend with live stdout streaming) and WireGuard (Windows service/exec)
- Windows Firewall enforcement: Kill Switch and Split Tunneling (include/exclude), persisted per VPN
- Security tab for IP and Country blocking management
- Help content updated (EN/IT) for Monitoring, Security, VPN and advanced features

### Changed
- FirewallManager signals extended for VPN status/logs; UI Monitoring tab enriched
- Zone-based VPN configuration supports persistence of split tunneling

### Fixed
- Network monitor counters handling and UI wiring
- Various UI stability fixes during startup and monitoring

## [0.0.1] - 2025-10-28

### Added
- Initial project setup and structure
- Basic firewall management interface with PySide6
- Support for English and Italian languages
- Basic rule management (add, edit, delete)
- Log viewer with search and filtering capabilities
- Dark theme support for the UI
- Log export functionality (TXT, CSV, JSON)
- Basic error handling and logging

### Changed
- Improved UI/UX with better organization and feedback
- Enhanced log viewer with syntax highlighting
- Optimized file loading for large log files

### Fixed
- Fixed logger parameter passing in ViewLogsWindow
- Resolved indentation and syntax issues in view_logs.py
- Fixed exception handling in file loading operations

### Removed
- Unused imports and redundant code
- Deprecated functions and variables
"""

def get_version():
    """Return the current version as a string."""
    return __version__

def get_version_info():
    """Return the version as a tuple for comparison."""
    return VERSION

def get_version_history():
    """Return the version history."""
    return [
        {
            "version": "0.1.0",
            "date": "2025-10-28",
            "changes": [
                "Monitoring tab with real-time charts and alerts",
                "Enhanced Security (rate limiting, GeoIP, reputation, port knocking)",
                "VPN integration (OpenVPN/WireGuard) with kill switch and split tunneling",
                "Windows Firewall enforcement and persisted split tunneling"
            ]
        },
        {
            "version": "0.0.1",
            "date": "2025-10-28",
            "changes": [
                "Initial project setup and structure",
                "Basic firewall management interface with PySide6",
                "Support for English and Italian languages",
                "Basic rule management (add, edit, delete)",
                "Log viewer with search and filtering capabilities",
                "Dark theme support for the UI",
                "Log export functionality (TXT, CSV, JSON)",
                "Basic error handling and logging"
            ]
        },
    ]

def get_latest_changes():
    """Get the changes in the latest version."""
    if get_version_history():
        return get_version_history()[0]['changes']
    return []

def is_development():
    """Check if this is a development version."""
    return "dev" in __version__ or "a" in __version__ or "b" in __version__

def get_codename():
    """Get the codename for this version."""
    # Simple codename based on version number
    major, minor, patch = VERSION
    codenames = ["Alpha", "Bravo", "Charlie", "Delta", "Echo", "Foxtrot", "Golf", "Hotel"]
    return codenames[minor % len(codenames)]
