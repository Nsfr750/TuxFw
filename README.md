# TuxFw

A comprehensive Windows firewall management application built with Python, PySide6, Wand, and QRCode.

## Features

- **Bilingual Interface**: Complete support for English and Italian languages
- **Rule Management**: Add, edit, delete, and manage firewall rules
- **Dark Theme**: Modern dark theme for better visibility
- **Log Viewer**: Advanced log viewer with search and filtering
- **Export Capabilities**: Export logs in multiple formats (TXT, CSV, JSON)
- **Real-time Monitoring**: Monitor firewall status in real-time
- **User-friendly UI**: Intuitive interface built with PySide6
- **Cross-platform**: Works on Windows, macOS, and Linux

## Requirements

- Python 3.8+
- PySide6 (Qt6 bindings for Python)
- Wand (ImageMagick bindings)
- qrcode (QR code generation)
- python-iptables (Linux firewall support)
- wheel
- shiboken6
- psutil

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/Nsfr750/firewall-manager.git
   cd firewall-manager
   ```

2. Create and activate virtual environment:

   ```bash
   python -m venv venv
   # On Windows
   venv\Scripts\activate
   # On Linux/macOS
   source venv/bin/activate
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Install system dependencies:

   ```bash
   # Windows (ImageMagick)
   # Download and install ImageMagick from: https://imagemagick.org/

   # Linux (Ubuntu/Debian)
   sudo apt-get install libmagickwand-dev

   # Linux (Fedora)
   sudo dnf install ImageMagick-devel

   # Linux (Arch)
   sudo pacman -S imagemagick
   ```

## Usage

### Running the Application

```bash
# Main entry point
python main.py

# Or directly from script folder
python script/main.py
```

### Windows Firewall Integration

The application provides a graphical interface for managing Windows firewall rules:

1. **Status Tab**: Monitor firewall status and connection statistics
2. **Rules Tab**: Add, edit, and delete firewall rules
3. **Logs Tab**: View and manage firewall logs
4. **QR Code Tab**: Generate QR codes for rule sharing
5. **Configuration Tab**: Manage profiles and settings

### Configuration File

The application uses `script/firewall_config.json` to store:
- Firewall rules with detailed properties
- Application settings and preferences
- Profile configurations
- User preferences

## Language Support

The application supports both English and Italian languages with full localization of all UI elements and messages.

## Building

### PyInstaller (Recommended for Windows)

```bash
# One-file executable
python -m PyInstaller --onefile --name "FirewallManager" --icon "assets/icon.ico" --version-file "version_info.txt" script/main.py

# Directory distribution
python -m PyInstaller --onedir --name "FirewallManager" --icon "assets/icon.ico" --version-file "version_info.txt" script/main.py
```

## Features in Detail

### Firewall Rules Management
- Add custom rules with protocol, port, direction, and action
- Edit existing rules with validation
- Delete rules with confirmation
- Enable/disable rules individually
- Rule validation and conflict detection

### Profile System
- **Work Profile**: Secure settings for office environment
- **Home Profile**: Balanced settings for home use
- **Public Profile**: Maximum security for public networks
- Easy profile switching

### QR Code Integration
- Generate QR codes from firewall configurations
- Share rules securely via QR codes
- Import configurations from QR codes

### Logging and Monitoring
- Real-time connection monitoring
- Detailed activity logs
- Export logs to files
- Configurable log levels

## License

GPLv3 - See [LICENSE](LICENSE) file for details

## Author

Nsfr750 - [GitHub](https://github.com/Nsfr750)

## Support

For support, please open an issue on GitHub or contact via email.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
