# TuxFw Project Structure

```text
TuxFw/
├── firewall/
│   ├── script/                         # Main application scripts
│   │   ├── firewall_manager.py         # Core firewall logic, signals to UI
│   │   ├── logger.py                   # Logger implementation
│   │   ├── main.py                     # Application entry point
│   │   ├── network_monitor.py          # Real-time stats & connections, IDS
│   │   ├── network_zones.py            # Zones, VPNManager, OpenVPN/WireGuard
│   │   ├── security_utils.py           # Rate limiting, GeoIP, Reputation, Knocking
│   │   ├── win_firewall.py             # Windows Firewall enforcement (Kill/Split)
│   │   └── version.py                  # Version information
│   ├── UI/                             # User interface components
│   │   ├── about.py                    # About dialog
│   │   ├── gui.py                      # Main UI window
│   │   ├── help.py                     # Help window
│   │   ├── menu.py                     # Menu bar
│   │   ├── monitoring_tab.py           # Monitoring (charts, connections, VPN, Security)
│   │   ├── sponsor.py                  # Sponsor dialog
│   │   └── view_logs.py                # Log viewing
│   ├── assets/                         # Static assets
│   │   ├── icon.png                    # Application icon
│   │   ├── icon.ico                    # Application icon (Windows)
│   │   ├── logo.png                    # Application logo
│   │   └── version_info.txt            # Windows version resource for builds
│   └── lang/                           # Internationalization
│       ├── language_manager.py         # Language manager
│       └── translations.py             # Translations
├── config/                             # Configuration files
│   ├── firewall_config.json            # App settings & rules
│   ├── configuration.json              # (Optional) security/vpn app config
│   └── zones/                          # Zone/VPN definitions (one JSON per zone)
├── docs/                               # Documentation
│   ├── STRUCT.md                       # Project structure
│   ├── SECURITY.md                     # Security policy and features
│   ├── ROADMAP.md                      # Development roadmap
│   └── USER_GUIDE.md                   # User guide
├── setup/                              # Build scripts
│   └── comp.py                         # PyInstaller build helper
├── logs/                               # Application logs (runtime)
├── tests/                              # Test files
├── CHANGELOG.md                        # Version history
├── LICENSE                             # GPLv3 license
├── README.md                           # Project README
├── requirements.txt                    # Python dependencies
└── TO_DO.md                            # TODO list
```

## Key Components

### Core

- `script/firewall_manager.py`: Core firewall logic, integrates monitoring, security, VPN; emits UI signals
- `script/main.py`: Main application entry point

### User Interface

- `UI/gui.py`: Main window and tabs
- `UI/monitoring_tab.py`: Monitoring dashboard (charts), connections, VPN controls, Security management
- `UI/view_logs.py`: Log viewing functionality

### Configuration

- `config/firewall_config.json`: Stores firewall rules and app settings
- `config/zones/*.json`: Zone and VPN definitions (`is_vpn`, `vpn_config`, persisted split tunneling)
- `lang/translations.py`: Translation strings

### Documentation

- `docs/STRUCT.md`: Project structure
- `docs/SECURITY.md`: Security features and policy (v0.1.0)
- `docs/ROADMAP.md`: Planned features and phases
- `docs/USER_GUIDE.md`: Usage guide

## Development

### Dependencies

- Python 3.8+
- PySide6
- Other dependencies listed in `requirements.txt`

### Building

1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Run the application: `python script/main.py`

## License

This project is licensed under the GPLv3 License - see the [LICENSE](LICENSE) file for details.
