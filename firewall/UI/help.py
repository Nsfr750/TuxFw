#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTextEdit,
                             QPushButton, QGroupBox, QLabel, QTabWidget,
                             QListWidget, QListWidgetItem, QSplitter)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from firewall.lang.translations import translations


class HelpWindow(QWidget):
    """Window for displaying help information"""

    def __init__(self, parent, current_language):
        super().__init__(parent)
        self.current_language = current_language

        self.setWindowTitle(translations[self.current_language]['help'] or 'Help')
        self.setMinimumSize(700, 500)
        self.setWindowFlags(Qt.WindowType.Window)

        self.init_ui()

    def init_ui(self):
        """Initialize the UI"""
        layout = QVBoxLayout(self)

        # Header
        header_label = QLabel(translations[self.current_language]['help_title'] or 'Firewall Manager Help')
        header_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        header_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(header_label)

        # Create tab widget for different help sections
        self.tab_widget = QTabWidget()

        # Getting Started tab
        self.create_getting_started_tab()

        # Rules Management tab
        self.create_rules_tab()

        # Configuration tab
        self.create_config_tab()

        # Troubleshooting tab
        self.create_troubleshooting_tab()

        # About tab
        self.create_about_tab()

        layout.addWidget(self.tab_widget)

        # Footer with close button
        footer_layout = QHBoxLayout()
        footer_layout.addStretch()

        self.close_button = QPushButton(translations[self.current_language]['close'] or 'Close')
        self.close_button.clicked.connect(self.close)
        footer_layout.addWidget(self.close_button)

        footer_layout.addStretch()
        layout.addLayout(footer_layout)

    def create_getting_started_tab(self):
        """Create the getting started tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        content = QTextEdit()
        content.setReadOnly(True)
        content.setHtml(self.get_getting_started_html())
        layout.addWidget(content)

        self.tab_widget.addTab(tab, translations[self.current_language]['getting_started'] or 'Getting Started')

    def create_rules_tab(self):
        """Create the rules management tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        content = QTextEdit()
        content.setReadOnly(True)
        content.setHtml(self.get_rules_html())
        layout.addWidget(content)

        self.tab_widget.addTab(tab, translations[self.current_language]['rules_help'] or 'Rules Management')

    def create_config_tab(self):
        """Create the configuration tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        content = QTextEdit()
        content.setReadOnly(True)
        content.setHtml(self.get_config_html())
        layout.addWidget(content)

        self.tab_widget.addTab(tab, translations[self.current_language]['config_help'] or 'Configuration')

    def create_troubleshooting_tab(self):
        """Create the troubleshooting tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        content = QTextEdit()
        content.setReadOnly(True)
        content.setHtml(self.get_troubleshooting_html())
        layout.addWidget(content)

        self.tab_widget.addTab(tab, translations[self.current_language]['troubleshooting'] or 'Troubleshooting')

    def create_about_tab(self):
        """Create the about tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        content = QTextEdit()
        content.setReadOnly(True)
        content.setHtml(self.get_about_html())
        layout.addWidget(content)

        self.tab_widget.addTab(tab, translations[self.current_language]['about'] or 'About')

    def get_getting_started_html(self):
        """Get getting started HTML content"""
        return """
        <h2>Getting Started</h2>
        <p><strong>Welcome to the Python Firewall Manager!</strong></p>

        <h3>Quick Start Guide:</h3>
        <ol>
            <li><strong>Enable Firewall:</strong> Go to the Status tab and click "Enable Firewall"</li>
            <li><strong>Add Rules:</strong> Switch to the Rules tab to add firewall rules</li>
            <li><strong>Monitor Logs:</strong> Check the Logs tab for firewall activity</li>
            <li><strong>Configure Settings:</strong> Use the Configuration tab to customize behavior</li>
        </ol>

        <h3>System Requirements:</h3>
        <ul>
            <li>Python 3.7 or higher</li>
            <li>PySide6 for GUI</li>
            <li>Administrative privileges (for firewall modifications)</li>
            <li>Windows, Linux, or macOS support</li>
        </ul>

        <p><em>Note: This application provides a graphical interface for managing firewall rules.
        Actual firewall implementation may vary by operating system.</em></p>
        """

    def get_rules_html(self):
        """Get rules management HTML content"""
        return """
        <h2>Firewall Rules Management</h2>

        <h3>Adding Rules:</h3>
        <ol>
            <li>Go to the Rules tab</li>
            <li>Click "Add Rule" button</li>
            <li>Fill in the rule details:
                <ul>
                    <li><strong>Name:</strong> Descriptive name for the rule</li>
                    <li><strong>Protocol:</strong> TCP, UDP, or ICMP</li>
                    <li><strong>Port:</strong> Port number or range</li>
                    <li><strong>Direction:</strong> IN (incoming) or OUT (outgoing)</li>
                    <li><strong>Action:</strong> ALLOW or BLOCK</li>
                    <li><strong>Description:</strong> Optional description</li>
                </ul>
            </li>
            <li>Click OK to save the rule</li>
        </ol>

        <h3>Editing Rules:</h3>
        <ol>
            <li>Select a rule from the table</li>
            <li>Click "Edit Rule" button</li>
            <li>Modify the desired fields</li>
            <li>Click OK to save changes</li>
        </ol>

        <h3>Deleting Rules:</h3>
        <ol>
            <li>Select a rule from the table</li>
            <li>Click "Delete Rule" button</li>
            <li>Confirm the deletion</li>
        </ol>

        <h3>Rule Types:</h3>
        <ul>
            <li><strong>ALLOW:</strong> Permits traffic matching the criteria</li>
            <li><strong>BLOCK:</strong> Blocks traffic matching the criteria</li>
            <li><strong>TCP/UDP:</strong> Protocol-specific rules</li>
            <li><strong>ICMP:</strong> Network diagnostic rules</li>
        </ul>
        """

    def get_config_html(self):
        """Get configuration HTML content"""
        return """
        <h2>Configuration Settings</h2>

        <h3>General Settings:</h3>
        <ul>
            <li><strong>Firewall Enabled:</strong> Master switch for firewall functionality</li>
            <li><strong>Default Policy:</strong> Default action (ALLOW/BLOCK) for unmatched traffic</li>
            <li><strong>Logging:</strong> Enable or disable activity logging</li>
            <li><strong>Language:</strong> Select interface language (English/Italian)</li>
        </ul>

        <h3>Profiles:</h3>
        <p>Firewall profiles allow you to quickly switch between different rule sets:</p>
        <ul>
            <li><strong>Default:</strong> Basic firewall rules</li>
            <li><strong>Work:</strong> Secure configuration for work environments</li>
            <li><strong>Home:</strong> Balanced configuration for home use</li>
            <li><strong>Public:</strong> Maximum security for public networks</li>
        </ul>

        <h3>Configuration Management:</h3>
        <ul>
            <li><strong>Save:</strong> Save current configuration to file</li>
            <li><strong>Load:</strong> Load configuration from file</li>
            <li><strong>Reset:</strong> Restore default configuration</li>
        </ul>

        <h3>Language Settings:</h3>
        <p>The application supports multiple languages. Changes take effect immediately and are saved automatically.</p>

        <h3>Log Configuration:</h3>
        <p>Logging settings control what information is recorded:
        <ul>
            <li>Rule activations and modifications</li>
            <li>Security events and blocked connections</li>
            <li>Configuration changes</li>
            <li>Application events and errors</li>
        </ul>
        </p>
        """

    def get_troubleshooting_html(self):
        """Get troubleshooting HTML content"""
        return """
        <h2>Troubleshooting</h2>

        <h3>Common Issues:</h3>

        <h4>Application won't start:</h4>
        <ul>
            <li>Check Python version (3.7+ required)</li>
            <li>Verify PySide6 installation: <code>pip install PySide6</code></li>
            <li>Check for missing dependencies</li>
            <li>Run as administrator if firewall modifications are needed</li>
        </ul>

        <h4>Firewall rules not working:</h4>
        <ul>
            <li>Verify administrative privileges</li>
            <li>Check if firewall service is running</li>
            <li>Review system firewall configuration</li>
            <li>Test with simple rules first</li>
        </ul>

        <h4>Configuration not saving:</h4>
        <ul>
            <li>Check file permissions in config directory</li>
            <li>Verify disk space availability</li>
            <li>Check for antivirus interference</li>
            <li>Try saving to a different location</li>
        </ul>

        <h4>Logs not appearing:</h4>
        <ul>
            <li>Check logs directory permissions</li>
            <li>Verify logging is enabled in settings</li>
            <li>Check available disk space</li>
            <li>Review log file permissions</li>
        </ul>

        <h3>Performance Issues:</h3>
        <ul>
            <li><strong>Slow startup:</strong> Check for large configuration files</li>
            <li><strong>High memory usage:</strong> Monitor log file sizes</li>
            <li><strong>UI unresponsive:</strong> Check system resources</li>
        </ul>

        <h3>Getting Help:</h3>
        <ul>
            <li>Check the project GitHub page</li>
            <li>Review the documentation</li>
            <li>Check log files for error messages</li>
            <li>Contact support if issues persist</li>
        </ul>

        <h3>Log File Locations:</h3>
        <ul>
            <li><strong>Application logs:</strong> logs/firewall_YYYY-MM-DD.log</li>
            <li><strong>Configuration:</strong> config/firewall_config.json</li>
            <li><strong>Cache:</strong> __pycache__/ directory</li>
        </ul>
        """

    def get_about_html(self):
        """Get about HTML content"""
        return """
        <h2>About Firewall Manager</h2>

        <p><strong>Python Firewall Manager</strong> is an open-source graphical interface for managing firewall rules and monitoring network security.</p>

        <h3>Features:</h3>
        <ul>
            <li>Graphical rule management interface</li>
            <li>Real-time firewall status monitoring</li>
            <li>Comprehensive logging system</li>
            <li>Multiple firewall profiles</li>
            <li>Multi-language support</li>
            <li>QR code generation utility</li>
            <li>Cross-platform compatibility</li>
        </ul>

        <h3>Technical Details:</h3>
        <ul>
            <li><strong>Framework:</strong> PySide6 (Qt for Python)</li>
            <li><strong>Language:</strong> Python 3.7+</li>
            <li><strong>License:</strong> GPLv3</li>
            <li><strong>Backend:</strong> Platform-specific firewall APIs</li>
        </ul>

        <h3>Version Information:</h3>
        <ul>
            <li><strong>Current Version:</strong> 0.0.1</li>
            <li><strong>Developer:</strong> Nsfr750</li>
            <li><strong>Organization:</strong> Tuxxle</li>
        </ul>

        <h3>Contributing:</h3>
        <p>This project is open source and welcomes contributions:
        <ul>
            <li>Report bugs and issues</li>
            <li>Suggest new features</li>
            <li>Submit code improvements</li>
            <li>Help with translations</li>
        </ul>
        </p>

        <p><em>© Copyright 2025 Nsfr750 - All rights reserved</em></p>
        """
