# TuxFw Project Structure

```text
TuxFw/
├── script/                   # Main application scripts
│   ├── firewall_manager.py   # Core firewall management logic
│   ├── logger.py             # Logger implementation
│   ├── main.py               # Application entry point
│   └── version.py            # Version information
│
├── UI/                       # User interface components
│   ├── about.py              # About dialog implementation
│   ├── gui.py                # Main GUI implementation
│   ├── help.py               # Help dialog implementation
│   ├── menu.py               # Menu implementation
│   ├── sponsor.py            # Sponsor dialog implementation
│   └── view_logs.py          # Log viewing functionality
│
├── assets/                   # Static assets
│   ├── icon.png              # Application icon
│   ├── icon.ico              # Application icon
│   └── logo.png              # Application logo
│
├── config/                   # Configuration files
│   └── firewall_config.json  # Firewall rules and settings
│
├── docs/                     # Documentation
│   ├── STRUCT.md             # Project structure documentation
│   └── SECURITY.md           # Security policy and guidelines
│
├── lang/                     # Internationalization
│   ├── language_manager.py   # Language manager implementation
│   └── translations.py       # Translation strings
│
├── logs/                     # Application logs
│
├── tests/                    # Test files
│
├── .gitignore                # Git ignore file
├── CHANGELOG.md              # Version history
├── LICENSE                   # License information (GPLv3)
├── README.md                 # Project README
├── requirements.txt          # Python dependencies
└── TO_DO.md                  # TODO list

```

## Key Components

### Core

- `script/firewall_manager.py`: Implements the core firewall functionality
- `script/main.py`: Main application entry point

### User Interface

- `UI/gui.py`: Main window and UI components
- `UI/view_logs.py`: Log viewing functionality

### Configuration

- `config/firewall_config.json`: Stores firewall rules and settings
- `lang/translations.py`: Contains translation strings for internationalization

### Documentation

- `docs/STRUCT.md`: Project structure documentation
- `docs/SECURITY.md`: Security policy and guidelines

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
