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

TuxFw is a user-friendly firewall management tool for Linux systems. This guide provides detailed instructions on how to install, configure, and use TuxFw to manage your system's firewall rules and monitor network activity.

## Installation

### System Requirements
- Linux-based operating system
- Python 3.8 or higher
- Root/sudo privileges
- nftables or iptables installed
- 100MB free disk space
- 512MB RAM minimum (1GB recommended)

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

The main window is divided into several sections:

1. **Toolbar**: Quick access to common actions
2. **Rules List**: Displays all configured firewall rules
3. **Status Bar**: Shows current firewall status and connection information
4. **Log Panel**: Displays system and firewall logs

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

## Frequently Asked Questions (FAQ)

### Q: How do I reset TuxFw to default settings?
A: Close the application and delete the configuration file located at `~/.config/tuxfw/settings.json`

### Q: Can I use TuxFw on a server without a GUI?
A: Yes, TuxFw can be used in command-line mode. Run `python -m firewall.cli` for the command-line interface.

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
A: Contributions are welcome! Please see our [Contributing Guidelines](docs/CONTRIBUTING.md) for more information.

---

*Documentation last updated: October 28, 2025*

© 2025 Nsfr750 - All rights reserved
