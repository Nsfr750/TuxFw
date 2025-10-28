# TuxFw

A comprehensive cross-platform firewall management application with a modern UI.

## Features (v0.1.0)

- **Monitoring**: Real-time bandwidth charts (QtCharts), live connections, security alerts
- **Enhanced Security**: Rate limiting, GeoIP blocking (GeoLite2), IP reputation feeds, port knocking
- **VPN Integration**: OpenVPN (process backend, live log streaming) and WireGuard (Windows service/exec)
- **Kill Switch & Split Tunneling (Windows)**: Enforced via Windows Firewall, per-VPN persistence
- **Security Tab**: Manage blocked IPs and countries (GeoIP)
- **Rule Management**: Add, edit, delete, import, and export rules
- **Dark Theme** with Wand-based imaging; QR Code generation
- **Logs**: Advanced log viewer with search/filtering and multi-format export (TXT/CSV/JSON)
- **Bilingual UI**: English and Italian
- **Cross-platform**: Windows, macOS, Linux; mock firewall for development

## Requirements

- Python 3.8+
- PySide6 (Qt6 bindings for Python)
- Wand (ImageMagick bindings for image processing)
- qrcode
- psutil
- geoip2, requests, aiohttp (Enhanced Security)
- pip-nftables (Linux)
- wheel, shiboken6, pytest (build/test)

Tools (optional, for VPN):

- OpenVPN installed and on PATH (or provide full path in zone `vpn_config`)
- WireGuard (Windows) with `wireguard.exe` available for service control

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/Nsfr750/TuxFw.git
   cd TuxFw
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
python firewall/main.py

# Or directly from script folder
python firewall/script/main.py
```

### Monitoring & VPN

- Monitoring → Dashboard: view live bandwidth charts, interface selector, security alerts.
- Monitoring → VPN: select VPN, connect/disconnect, enable Kill Switch, configure Split Tunneling (include/exclude) and routes.

Note: Kill Switch and Split Tunneling enforcement require Administrator privileges on Windows.

### Configuration File

The application uses `config/firewall_config.json` to store:

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
python -m PyInstaller --onefile --name "TuxFw" --icon "firewall/assets/icon.ico" --version-file "firewall/assets/version_info.txt" firewall/main.py

# Directory distribution
python -m PyInstaller --onedir --name "TuxFw" --icon "firewall/assets/icon.ico" --version-file "firewall/assets/version_info.txt" firewall/main.py
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

- Real-time connections and bandwidth charts
- IDS alerts and Enhanced Security events
- OpenVPN stdout streamed to VPN log panel
- Export logs to files; configurable log levels

## License

GPLv3 - See [LICENSE](LICENSE) file for details

## Author

Nsfr750 - [GitHub](https://github.com/Nsfr750)

## Support

For support, please open an issue on GitHub or contact via email.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
