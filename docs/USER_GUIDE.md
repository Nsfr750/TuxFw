# TuxFw - User Guide

## Table of Contents
1. [Introduction](#introduction)
2. [Installation](#installation)
   - [System Requirements](#system-requirements)
   - [Installation Steps](#installation-steps)
   - [First Run](#first-run)
3. [User Interface Overview](#user-interface-overview)
   - [Main Window](#main-window)
   - [Menu Bar](#menu-bar)
   - [Status Bar](#status-bar)
4. [Managing Firewall Rules](#managing-firewall-rules)
   - [Viewing Rules](#viewing-rules)
   - [Adding Rules](#adding-rules)
   - [Editing Rules](#editing-rules)
   - [Deleting Rules](#deleting-rules)
   - [Import/Export Rules](#import-export-rules)
5. [Log Management](#log-management)
   - [Viewing Logs](#viewing-logs)
   - [Filtering Logs](#filtering-logs)
   - [Exporting Logs](#exporting-logs)
   - [Clearing Logs](#clearing-logs)
6. [Settings](#settings)
   - [General Settings](#general-settings)
   - [Appearance](#appearance)
   - [Language](#language)
7. [Troubleshooting](#troubleshooting)
   - [Common Issues](#common-issues)
   - [Viewing Error Logs](#viewing-error-logs)
   - [Getting Help](#getting-help)
8. [Frequently Asked Questions (FAQ)](#frequently-asked-questions-faq)

## Introduction

TuxFw is a user-friendly firewall management tool for Windows, Linux, and macOS. This guide explains how to install, configure, and use TuxFw to manage firewall rules, monitor network activity, and configure VPN and advanced security features.

## Installation

### System Requirements

- Windows/Linux/macOS
- Python 3.8 or higher
- Administrative privileges for firewall/VPN enforcement (Windows)
- nftables/iptables (Linux) if applying system rules
- Optional: OpenVPN, WireGuard (for VPN)
- Optional: GeoLite2-Country.mmdb (GeoIP)

### Installation Steps

1. **Clone the repository**:
   ```bash
   git clone https://github.com/Nsfr750/TuxFw.git
   cd TuxFw
   ```

2. **Install dependencies**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Run the application**:
   ```bash
   python -m firewall.main
   ```

### First Run

When you first launch TuxFw, you'll be presented with the main interface. The application will attempt to detect your current firewall configuration and display it in the rules list.

## User Interface Overview

### Main Window

Key tabs:

1. **Status**: Firewall status and quick metrics
2. **Rules**: Manage firewall rules
3. **Logs**: View and export logs
4. **QR Code**: Generate QR codes for sharing
5. **Configuration**: Settings and profiles
6. **Monitoring**: Real-time charts, connections, security alerts, VPN controls, and Security management

### Menu Bar

- **File**: Import/export rules, preferences, and exit
- **Edit**: Manage rules and settings
- **View**: Customize the interface
- **Tools**: Additional utilities
- **Help**: Documentation and about information

### Status Bar

Displays:
- Firewall status (enabled/disabled)
- Number of active rules
- Last update time
- System resource usage

## Managing Firewall Rules

### Viewing Rules

1. Open TuxFw
2. The main window displays all configured rules
3. Use the filter options to narrow down the list

### Adding Rules

1. Click the "Add Rule" button
2. Fill in the rule details:
   - Name
   - Protocol (TCP/UDP/ICMP)
   - Port/Port Range
   - Source/Destination IP
   - Action (Allow/Block/Reject)
3. Click "Save"

### Editing Rules

1. Select the rule from the list
2. Click "Edit"
3. Make your changes
4. Click "Save"

### Deleting Rules

1. Select the rule(s) you want to delete
2. Click "Delete"
3. Confirm the deletion

### Import/Export Rules

1. Go to **File > Import/Export**
2. Choose to import or export rules
3. Select the file location
4. Confirm the operation

## Log Management

### Viewing Logs

1. Click on the "Logs" tab
2. Use the filter options to find specific entries
3. Click on a log entry for more details

### Filtering Logs

1. Open the log viewer
2. Use the filter bar to:
   - Search by text
   - Filter by log level (Info, Warning, Error, etc.)
   - Set date range

### Exporting Logs

1. Open the log viewer
2. Apply any desired filters
3. Click "Export"
4. Choose the export format (TXT, CSV, JSON)
5. Select the save location
6. Click "Save"

### Clearing Logs

1. Open the log viewer
2. Click "Clear Logs"
3. Confirm the action

## Monitoring

### Dashboard

- Real-time bandwidth charts (Download/Upload) with interface selector
- Security alerts table from IDS/enhanced security events

### Connections

- Live list of network connections with protocol, endpoints, status, process and PID

### VPN

- Select VPN (from configured zones)
- Connect/Disconnect
- Enable **Kill Switch** (Windows Firewall) and configure **Split Tunneling**
  - Modes: include (only listed routes via VPN), exclude (listed routes excluded from VPN)
  - Routes persisted per VPN and applied on startup

Note: Windows Firewall rules require running as Administrator.

### Security

- Block/unblock IP addresses (temporary)
- Block/unblock countries (GeoIP)

## Settings

### General Settings

- **Start on system startup**: Enable/disable auto-start
- **Check for updates**: Configure update checking
- **Backup settings**: Configure automatic backups

### Appearance

- **Theme**: Choose between light and dark mode
- **Font size**: Adjust the interface text size
- **Language**: Change the application language

### Language

1. Go to **Settings > Language**
2. Select your preferred language
3. Restart the application to apply changes

## Troubleshooting

### Common Issues

#### Firewall Not Starting
- Verify you have root privileges
- Check if another firewall is running
- View error logs for specific issues

#### Rules Not Applying
- Ensure the firewall is enabled
- Check for conflicting rules
- Verify rule order (rules are processed top to bottom)

### Viewing Error Logs

1. Go to **Help > View Logs**
2. Filter for "Error" level messages
3. Note any error codes or messages

### Getting Help

- Check the [GitHub Issues](https://github.com/Nsfr750/TuxFw/issues) page
- Consult the [online documentation](https://github.com/Nsfr750/TuxFw/wiki)

#### VPN Not Connecting

- Ensure OpenVPN/WireGuard tools are installed and on PATH
- Verify .ovpn/.conf files and permissions
- On Windows, run as Administrator for WireGuard service control

#### GeoIP Disabled

- Download GeoLite2-Country.mmdb and configure the path

## Frequently Asked Questions (FAQ)

### Q: How do I reset TuxFw to default settings?
A: Close the application and delete the configuration file located at `~/.config/tuxfw/settings.json`

### Q: Can I use TuxFw on a server without a GUI?
A: Yes, CLI tools are available for selected features (e.g., security CLI). A full CLI is planned in the roadmap.

### Q: How do I update TuxFw?
A: 
```bash
cd /path/to/TuxFw
git pull
pip install -r requirements.txt --upgrade
```

### Q: Is TuxFw compatible with UFW?
A: TuxFw can import UFW rules but runs independently. It's recommended to disable UFW when using TuxFw.

### Q: How can I contribute to the project?
A: Contributions are welcome! Please see our [Contributing Guidelines](CONTRIBUTING.md) for more information.

---

*Documentation last updated: October 28, 2025*

© 2025 Nsfr750 - All rights reserved
