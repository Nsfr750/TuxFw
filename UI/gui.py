#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QTabWidget, QGroupBox, QFormLayout, QLabel, QPushButton, 
                             QLineEdit, QComboBox, QTextEdit, QTableWidget, QTableWidgetItem, 
                             QHeaderView, QMessageBox, QFileDialog, QSplitter, QCheckBox,
                             QSpinBox, QMenuBar, QMenu, QStatusBar, QProgressBar, QDialog,
                             QDialogButtonBox, QVBoxLayout as QVBox, QHBoxLayout as QHBox,
                             QApplication, QMessageBox)
from PySide6.QtCore import Qt, QTimer, QThread, Signal, QSize
from PySide6.QtGui import QPixmap, QIcon, QFont, QAction, QImage, QPixmap
from wand.image import Image as WandImage
from lang.translations import translations
from UI.about import AboutDialog
from UI.menu import MenuManager
from UI.view_logs import ViewLogsWindow
from UI.sponsor import SponsorDialog as SponsorWindow
from UI.help import HelpWindow
from logger import get_logger
import os
import json
import qrcode
import sys
import tempfile
from datetime import datetime
from typing import Optional, Dict, Any, List

# Import FirewallManager from the main module
from script.firewall_manager import FirewallManager

class WindowsFirewallManager(QMainWindow):
    """Main firewall management application using PySide6"""
    
    def __init__(self, firewall_manager: FirewallManager):
        """
        Initialize the WindowsFirewallManager
        
        Args:
            firewall_manager: An instance of FirewallManager for handling core functionality
        """
        super().__init__()
        self.firewall = firewall_manager
        self.current_language = self.firewall.current_language
        
        # Initialize logger
        self.logger = get_logger("firewall.gui")
        self.logger.log_firewall_event("GUI_INIT", "Firewall Manager UI initialized")
        
        # Initialize UI components
        self.init_ui()
        
    def load_config_dialog(self):
        """Show file dialog to load configuration"""
        try:
            # Get translations from the firewall manager
            translations = self.firewall.translations
            
            file_path, _ = QFileDialog.getOpenFileName(
                self,
                translations.get(self.current_language, {}).get('load_config', 'Load Configuration'),
                "",  # Start in current directory
                "JSON Files (*.json);;All Files (*)"
            )
            
            if file_path:
                # Load the configuration using FirewallManager
                if self.firewall.load_config(file_path):
                    self.update_ui()
                    self.statusBar().showMessage(
                        translations.get(self.current_language, {}).get(
                            'config_loaded', 
                            'Configuration loaded successfully'
                        )
                    )
        except Exception as e:
            self.logger.log_error(f"Error loading configuration: {str(e)}", "load_config_dialog")
            QMessageBox.critical(
                self,
                self.firewall.translations.get(self.current_language, {}).get('error', 'Error'),
                f"Failed to load configuration: {str(e)}"
            )
    
    def save_config_dialog(self):
        """Show file dialog to save configuration"""
        try:
            # Get translations from the firewall manager
            translations = self.firewall.translations
            
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                translations.get(self.current_language, {}).get('save_config', 'Save Configuration'),
                "",  # Start in current directory
                "JSON Files (*.json);;All Files (*)"
            )
            
            if file_path:
                # Ensure the file has the .json extension
                if not file_path.lower().endswith('.json'):
                    file_path += '.json'
                    
                # Save the configuration using FirewallConfig
                if self.firewall.config.save_config(file_path):
                    self.statusBar().showMessage(
                        translations.get(self.current_language, {}).get(
                            'config_saved',
                            'Configuration saved successfully'
                        )
                    )
        except Exception as e:
            self.logger.log_error(f"Error saving configuration: {str(e)}", "save_config_dialog")
            QMessageBox.critical(
                self,
                self.translations[self.current_language].get('error', 'Error'),
                f"Failed to save configuration: {str(e)}"
            )
    
    def update_ui(self):
        """Update the UI to reflect the current state"""
        # This method should update all UI elements based on the current state
        # For example, update toggle buttons, rule lists, status indicators, etc.
        try:
            # Get current settings
            settings = self.firewall.config.config.get('settings', {})
            
            # Update UI elements based on settings
            # Example:
            # self.toggle_firewall_button.setChecked(settings.get('enabled', False))
            # self.block_inbound_checkbox.setChecked(settings.get('block_inbound', True))
            # self.block_outbound_checkbox.setChecked(settings.get('block_outbound', False))
            
            # Update rules table
            # self.update_rules_table()
            
            # Update status bar
            status = "Enabled" if settings.get('enabled', False) else "Disabled"
            self.statusBar().showMessage(f"Firewall: {status}")
            
        except Exception as e:
            self.logger.log_error(f"Error updating UI: {str(e)}", "update_ui")
            
    def init_ui(self):
        """Initialize the main UI components"""
        # Initialize dialog references
        self.about_dialog: Optional[AboutDialog] = None
        self.menu_manager: Optional[MenuManager] = None
        self.view_logs_window: Optional[ViewLogsWindow] = None
        self.sponsor_window: Optional[SponsorWindow] = None
        self.help_window: Optional[HelpWindow] = None
        
        # Set window properties
        self.setWindowTitle(translations[self.current_language].get('app_title', 'Firewall Manager'))
        self.setMinimumSize(1000, 700)
        
        # Set window icon if available
        self.setup_window_icon()
        
        # Set up the main window
        self.setup_menu()
        self.setup_toolbar()
        self.setup_statusbar()
        self.setup_main_widget()
        
        # Load initial data
        self.load_initial_data()
        
    def setup_window_icon(self):
        """Set up the application window icon"""
        try:
            # Get the absolute path to the icon file
            script_dir = os.path.dirname(os.path.abspath(__file__))
            icon_path = os.path.abspath(os.path.join(script_dir, '..', 'assets', 'icon.png'))
            
            if os.path.exists(icon_path):
                # Set window icon
                self.setWindowIcon(QIcon(icon_path))
                
                # Also set the application icon (for taskbar/desktop)
                app_icon = QIcon(icon_path)
                QApplication.setWindowIcon(app_icon)
                
                self.logger.log_firewall_event("ICON_LOADED", f"Loaded application icon from {icon_path}")
            else:
                self.logger.log_warning(f"Icon file not found at {icon_path}")
        except Exception as e:
            error_msg = f"Error loading window icon: {str(e)}"
            self.logger.log_error(error_msg)
            print(error_msg)  # Also print to console in case logger is not initialized properly

        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Create menu bar
        self.menu_manager = MenuManager(self, self.current_language)
        self.menu_manager.create_menu_bar()
        
        # Create tab widget for different sections
        self.tab_widget = QTabWidget()
        main_layout.addWidget(self.tab_widget)
        
        # Create status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage(translations[self.current_language].get('ready_status', 'Ready'))
        
        # Initialize tabs
        self.create_status_tab()
        self.create_rules_tab()
        self.create_logs_tab()
        self.create_qr_tab()
        self.create_config_tab()
        
        # Connect signals
        self.setup_connections()
        
        # Apply initial settings
        self.apply_ui_settings()
        
        # Show window
        self.show()
        
    def load_initial_data(self):
        """Load initial data for the UI"""
        try:
            # Load firewall status
            self.update_status()
            
            # Load rules
            self.load_rules()
            
            # Load logs
            self.refresh_logs()
            
        except Exception as e:
            self.logger.log_error(f"Error loading initial data: {e}")
            QMessageBox.critical(
                self,
                translations[self.current_language].get('error', 'Error'),
                f"Failed to load initial data: {str(e)}"
            )
    
    def setup_connections(self):
        """Set up signal/slot connections"""
        # Connect menu actions
        self.menu_manager.action_about.triggered.connect(self.show_about)
        self.menu_manager.action_exit.triggered.connect(self.close)
        self.menu_manager.action_view_logs.triggered.connect(self.show_logs)
        self.menu_manager.action_sponsor.triggered.connect(self.show_sponsors)
        self.menu_manager.action_help.triggered.connect(self.show_help)
        
        # Connect language change signals
        for action in self.menu_manager.language_actions.actions():
            action.triggered.connect(lambda checked, lang=action.data(): self.change_language(lang))
    
    def apply_ui_settings(self):
        """Apply UI-specific settings"""
        # Apply theme if needed
        self.apply_theme()
        
        # Update UI text based on current language
        self.retranslate_ui()
    
    def apply_theme(self):
        """Apply the current theme to the UI"""
        # This can be expanded to support different themes
        self.setStyleSheet("""
            QMainWindow, QDialog {
                background-color: #f0f0f0;
            }
            QTabWidget::pane {
                border: 1px solid #c0c0c0;
                padding: 5px;
            }
            QTabBar::tab {
                background: #e0e0e0;
                padding: 8px 12px;
                margin: 2px;
                border: 1px solid #c0c0c0;
                border-bottom: none;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }
            QTabBar::tab:selected {
                background: #ffffff;
                border-bottom: 1px solid #ffffff;
            }
        """)
    
    def retranslate_ui(self):
        """Update all UI text based on current language"""
        self.setWindowTitle(translations[self.current_language]['app_title'])
        
        # Update tab names
        tab_names = ['status', 'rules', 'logs', 'qr', 'config']
        for i, tab_name in enumerate(tab_names):
            if i < self.tab_widget.count():
                self.tab_widget.setTabText(i, translations[self.current_language][f'tab_{tab_name}'])
        
        # Update status bar
        self.status_bar.showMessage(translations[self.current_language].get('ready_status', 'Ready'))
    
    def update_status(self):
        """Update the status tab with current firewall status"""
        try:
            status = self.firewall.get_status()
            
            if hasattr(self, 'status_label'):
                status_text = ""
                status_text += f"Status: {'Enabled' if status['enabled'] else 'Disabled'}\n"
                status_text += f"Inbound: {'Blocked' if status['block_inbound'] else 'Allowed'}\n"
                status_text += f"Outbound: {'Blocked' if status['block_outbound'] else 'Allowed'}\n"
                status_text += f"Profile: {status['current_profile']}\n"
                status_text += f"Rules: {status['rules_count']}"
                
                self.status_label.setText(status_text)
                
                # Update toggle button text
                if hasattr(self, 'toggle_button'):
                    self.toggle_button.setText(
                        translations[self.current_language]['disable_firewall'] if status['enabled'] 
                        else translations[self.current_language]['enable_firewall']
                    )
                    
        except Exception as e:
            self.logger.log_error(f"Error updating status: {e}")
    
    def toggle_firewall(self):
        """Toggle firewall on/off"""
        try:
            current_status = self.firewall.get_status()
            new_status = not current_status['enabled']
            
            if self.firewall.toggle_firewall(new_status):
                self.firewall.apply_rules()
                self.update_status()
                
                # Show status message
                status_text = 'enabled' if new_status else 'disabled'
                self.status_bar.showMessage(
                    f"Firewall {status_text} successfully", 3000
                )
                
        except Exception as e:
            self.logger.log_error(f"Error toggling firewall: {e}")
            QMessageBox.critical(
                self,
                translations[self.current_language].get('error', 'Error'),
                f"Failed to toggle firewall: {str(e)}"
            )
    
    def load_rules(self):
        """Load firewall rules into the rules table"""
        try:
            if not hasattr(self, 'rules_table'):
                return
                
            rules = self.firewall.config.get_rules()
            self.rules_table.setRowCount(len(rules))
            
            for row, rule in enumerate(rules):
                self.rules_table.setItem(row, 0, QTableWidgetItem(rule.get('name', '')))
                self.rules_table.setItem(row, 1, QTableWidgetItem(rule.get('protocol', '')))
                self.rules_table.setItem(row, 2, QTableWidgetItem(str(rule.get('port', ''))))
                self.rules_table.setItem(row, 3, QTableWidgetItem(rule.get('direction', '')))
                self.rules_table.setItem(row, 4, QTableWidgetItem(rule.get('action', '')))
                
                # Add enabled checkbox
                enabled_item = QTableWidgetItem()
                enabled_item.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
                enabled_item.setCheckState(Qt.Checked if rule.get('enabled', False) else Qt.Unchecked)
                self.rules_table.setItem(row, 5, enabled_item)
                
        except Exception as e:
            self.logger.log_error(f"Error loading rules: {e}")
    
    def refresh_logs(self):
        """Refresh the logs display"""
        try:
            if hasattr(self, 'logs_text'):
                # In a real application, you would load logs from a file or log handler
                self.logs_text.setPlainText("Logs will be displayed here...")
        except Exception as e:
            self.logger.log_error(f"Error refreshing logs: {e}")
    
    # Tab creation methods
    def create_status_tab(self):
        """Create the status tab"""
        status_tab = QWidget()
        layout = QVBoxLayout(status_tab)
        
        # Status group
        status_group = QGroupBox(translations[self.current_language].get('status', 'Status'))
        status_layout = QVBoxLayout()
        
        # Status label
        self.status_label = QLabel()
        self.status_label.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self.status_label.setStyleSheet("font-family: monospace;")
        
        # Toggle button
        self.toggle_button = QPushButton()
        self.toggle_button.clicked.connect(self.toggle_firewall)
        
        status_layout.addWidget(self.status_label)
        status_layout.addWidget(self.toggle_button)
        status_group.setLayout(status_layout)
        
        layout.addWidget(status_group)
        layout.addStretch()
        
        self.tab_widget.addTab(status_tab, translations[self.current_language].get('tab_status', 'Status'))
    
    def create_rules_tab(self):
        """Create the rules management tab"""
        rules_tab = QWidget()
        layout = QVBoxLayout(rules_tab)
        
        # Rules table
        self.rules_table = QTableWidget()
        self.rules_table.setColumnCount(6)
        self.rules_table.setHorizontalHeaderLabels([
            translations[self.current_language].get('name', 'Name'),
            translations[self.current_language].get('protocol', 'Protocol'),
            translations[self.current_language].get('port', 'Port'),
            translations[self.current_language].get('direction', 'Direction'),
            translations[self.current_language].get('action', 'Action'),
            translations[self.current_language].get('enabled', 'Enabled')
        ])
        self.rules_table.horizontalHeader().setStretchLastSection(True)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.add_rule_btn = QPushButton(translations[self.current_language].get('add_rule', 'Add Rule'))
        self.edit_rule_btn = QPushButton(translations[self.current_language].get('edit_rule', 'Edit Rule'))
        self.delete_rule_btn = QPushButton(translations[self.current_language].get('delete_rule', 'Delete Rule'))
        
        button_layout.addWidget(self.add_rule_btn)
        button_layout.addWidget(self.edit_rule_btn)
        button_layout.addWidget(self.delete_rule_btn)
        button_layout.addStretch()
        
        layout.addWidget(self.rules_table)
        layout.addLayout(button_layout)
        
        self.tab_widget.addTab(rules_tab, translations[self.current_language].get('tab_rules', 'Rules'))
    
    def create_logs_tab(self):
        """Create the logs tab"""
        logs_tab = QWidget()
        layout = QVBoxLayout(logs_tab)
        
        # Logs text area
        self.logs_text = QTextEdit()
        self.logs_text.setReadOnly(True)
        self.logs_text.setFont(QFont("Consolas", 9))
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.refresh_logs_btn = QPushButton(translations[self.current_language].get('refresh', 'Refresh'))
        self.clear_logs_btn = QPushButton(translations[self.current_language].get('clear_logs', 'Clear Logs'))
        self.save_logs_btn = QPushButton(translations[self.current_language].get('save_logs', 'Save Logs...'))
        
        self.refresh_logs_btn.clicked.connect(self.refresh_logs)
        self.clear_logs_btn.clicked.connect(self.clear_logs)
        self.save_logs_btn.clicked.connect(self.save_logs)
        
        button_layout.addWidget(self.refresh_logs_btn)
        button_layout.addWidget(self.clear_logs_btn)
        button_layout.addWidget(self.save_logs_btn)
        button_layout.addStretch()
        
        layout.addWidget(self.logs_text)
        layout.addLayout(button_layout)
        
        self.tab_widget.addTab(logs_tab, translations[self.current_language].get('tab_logs', 'Logs'))
    
    def create_qr_tab(self):
        """Create the QR code generation tab"""
        qr_tab = QWidget()
        layout = QVBoxLayout(qr_tab)
        
        # Input
        input_layout = QHBoxLayout()
        
        self.qr_input = QLineEdit()
        self.qr_input.setPlaceholderText(
            translations[self.current_language].get('qr_placeholder', 'Enter text to generate QR code')
        )
        
        self.generate_qr_btn = QPushButton(
            translations[self.current_language].get('generate_qr', 'Generate QR')
        )
        self.generate_qr_btn.clicked.connect(self.generate_qr_code)
        
        input_layout.addWidget(self.qr_input)
        input_layout.addWidget(self.generate_qr_btn)
        
        # QR code display
        self.qr_label = QLabel()
        self.qr_label.setAlignment(Qt.AlignCenter)
        self.qr_label.setMinimumSize(300, 300)
        self.qr_label.setStyleSheet("background-color: white; border: 1px solid #ccc;")
        
        layout.addLayout(input_layout)
        layout.addWidget(self.qr_label, 1, Qt.AlignCenter)
        
        self.tab_widget.addTab(qr_tab, translations[self.current_language].get('tab_qr', 'QR Code'))
    
    def create_config_tab(self):
        """Create the configuration tab"""
        config_tab = QWidget()
        layout = QVBoxLayout(config_tab)
        
        # Settings group
        settings_group = QGroupBox(translations[self.current_language].get('settings', 'Settings'))
        settings_layout = QFormLayout()
        
        # Language selection
        self.language_combo = QComboBox()
        self.language_combo.addItem("English", "en")
        self.language_combo.addItem("Italiano", "it")
        # Add more languages as needed
        
        # Set current language
        index = self.language_combo.findData(self.current_language)
        if index >= 0:
            self.language_combo.setCurrentIndex(index)
        
        self.language_combo.currentIndexChanged.connect(self.on_language_changed)
        
        settings_layout.addRow(
            translations[self.current_language].get('language', 'Language') + ":", 
            self.language_combo
        )
        
        # Add more settings as needed
        
        settings_group.setLayout(settings_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.save_config_btn = QPushButton(translations[self.current_language].get('save', 'Save'))
        self.reset_config_btn = QPushButton(translations[self.current_language].get('reset', 'Reset'))
        
        self.save_config_btn.clicked.connect(self.save_config)
        self.reset_config_btn.clicked.connect(self.reset_config)
        
        button_layout.addStretch()
        button_layout.addWidget(self.save_config_btn)
        button_layout.addWidget(self.reset_config_btn)
        
        layout.addWidget(settings_group)
        layout.addStretch()
        layout.addLayout(button_layout)
        
        self.tab_widget.addTab(config_tab, translations[self.current_language].get('tab_config', 'Configuration'))
    
    # Action handlers
    def on_language_changed(self, index):
        """Handle language change"""
        language = self.language_combo.currentData()
        if language != self.current_language:
            self.change_language(language)
    
    def change_language(self, language: str):
        """Change the application language"""
        try:
            if self.firewall.change_language(language):
                self.current_language = language
                self.retranslate_ui()
        except Exception as e:
            self.logger.log_error(f"Error changing language: {e}")
    
    def show_about(self):
        """Show the about dialog"""
        if self.about_dialog is None:
            self.about_dialog = AboutDialog(self, self.current_language)
        self.about_dialog.show()
        self.about_dialog.raise_()
    
    def show_logs(self):
        """Show the logs window"""
        if self.view_logs_window is None:
            self.view_logs_window = ViewLogsWindow(self, self.current_language)
        self.view_logs_window.show()
        self.view_logs_window.raise_()
    
    def show_sponsors(self):
        """Show the sponsors window"""
        if self.sponsor_window is None:
            self.sponsor_window = SponsorWindow(self, self.current_language)
        self.sponsor_window.show()
        self.sponsor_window.raise_()
    
    def show_help(self):
        """Show the help window"""
        if self.help_window is None:
            self.help_window = HelpWindow(self, self.current_language)
        self.help_window.show()
        self.help_window.raise_()
    
    def generate_qr_code(self):
        """Generate a QR code from the input text"""
        text = self.qr_input.text().strip()
        if not text:
            QMessageBox.warning(
                self,
                translations[self.current_language].get('warning', 'Warning'),
                translations[self.current_language].get('qr_empty_warning', 'Please enter some text first')
            )
            return
        
        try:
            # Generate QR code
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(text)
            qr.make(fit=True)
            
            # Create and save QR code image
            img = qr.make_image(fill_color="black", back_color="white")
            
            # Convert to QPixmap and display
            temp_file = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
            img.save(temp_file.name)
            
            pixmap = QPixmap(temp_file.name)
            self.qr_label.setPixmap(pixmap.scaled(
                300, 300, 
                Qt.KeepAspectRatio, 
                Qt.SmoothTransformation
            ))
            
            # Clean up
            temp_file.close()
            os.unlink(temp_file.name)
            
        except Exception as e:
            self.logger.log_error(f"Error generating QR code: {e}")
            QMessageBox.critical(
                self,
                translations[self.current_language].get('error', 'Error'),
                f"Failed to generate QR code: {str(e)}"
            )
    
    def save_config(self):
        """Save configuration"""
        try:
            # Save language setting
            language = self.language_combo.currentData()
            if language != self.current_language:
                self.change_language(language)
            
            # Add more settings to save as needed
            
            QMessageBox.information(
                self,
                translations[self.current_language].get('success', 'Success'),
                translations[self.current_language].get('config_saved', 'Configuration saved successfully')
            )
            
        except Exception as e:
            self.logger.log_error(f"Error saving configuration: {e}")
            QMessageBox.critical(
                self,
                translations[self.current_language].get('error', 'Error'),
                f"Failed to save configuration: {str(e)}"
            )
    
    def reset_config(self):
        """Reset configuration to defaults"""
        try:
            reply = QMessageBox.question(
                self,
                translations[self.current_language].get('confirm', 'Confirm'),
                translations[self.current_language].get('confirm_reset', 'Are you sure you want to reset all settings to default?'),
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                # Reset language to default
                self.language_combo.setCurrentIndex(0)
                
                # Add more resets as needed
                
                QMessageBox.information(
                    self,
                    translations[self.current_language].get('success', 'Success'),
                    translations[self.current_language].get('config_reset', 'Configuration has been reset to defaults')
                )
                
        except Exception as e:
            self.logger.log_error(f"Error resetting configuration: {e}")
            QMessageBox.critical(
                self,
                translations[self.current_language].get('error', 'Error'),
                f"Failed to reset configuration: {str(e)}"
            )
    
    def clear_logs(self):
        """Clear the logs display"""
        if hasattr(self, 'logs_text'):
            self.logs_text.clear()
    
    def save_logs(self):
        """Save logs to a file"""
        if not hasattr(self, 'logs_text') or not self.logs_text.toPlainText().strip():
            QMessageBox.warning(
                self,
                translations[self.current_language].get('warning', 'Warning'),
                translations[self.current_language].get('no_logs_to_save', 'No logs to save')
            )
            return
        
        try:
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                translations[self.current_language].get('save_logs', 'Save Logs'),
                "",
                "Text Files (*.txt);;All Files (*)"
            )
            
            if file_path:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(self.logs_text.toPlainText())
                
                QMessageBox.information(
                    self,
                    translations[self.current_language].get('success', 'Success'),
                    translations[self.current_language].get('logs_saved', 'Logs saved successfully')
                )
                
        except Exception as e:
            self.logger.log_error(f"Error saving logs: {e}")
            QMessageBox.critical(
                self,
                translations[self.current_language].get('error', 'Error'),
                f"Failed to save logs: {str(e)}"
            )
    
    def closeEvent(self, event):
        """Handle window close event"""
        # Clean up resources
        if hasattr(self, 'firewall'):
            self.firewall = None
        
        # Close all child windows
        for window in self.findChildren(QDialog):
            window.close()
        
        event.accept()
        pass
        
    def create_qr_tab(self):
        """Create the QR code generation tab"""
        pass
        
    def create_config_tab(self):
        """Create the configuration tab"""
        pass
        
    def update_ui(self):
        """Update all UI elements"""
        pass
        
    def load_settings(self):
        """Load settings from configuration"""
        pass
        
    # Add other methods as needed...

class RuleDialog(QDialog):
    """Dialog for adding/editing firewall rules"""
    
    def __init__(self, parent, translations, rule=None):
        super().__init__(parent)
        self.translations = translations
        self.rule = rule or {}
        self.setup_ui()
    
    # [Previous method implementations would go here...]
    # Copy over the setup_ui and get_rule methods from the original file
