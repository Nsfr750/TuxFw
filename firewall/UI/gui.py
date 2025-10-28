#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QTabWidget, QGroupBox, QFormLayout, QLabel, QPushButton, 
                             QLineEdit, QComboBox, QTextEdit, QTableWidget, QTableWidgetItem, 
                             QHeaderView, QMessageBox, QFileDialog, QSplitter, QCheckBox,
                             QSpinBox, QMenuBar, QMenu, QStatusBar, QProgressBar, QDialog,
                             QDialogButtonBox, QVBoxLayout as QVBox, QHBoxLayout as QHBox,
                             QApplication, QMessageBox, QSizePolicy, QScrollArea, QStyle)
                             
# Import monitoring tab
from firewall.UI.monitoring_tab import MonitoringTab
from PySide6.QtCore import Qt, QTimer, QThread, Signal, QSize
from PySide6.QtGui import QPixmap, QIcon, QFont, QAction, QImage, QPixmap
import wand.image
import wand.color
import io
from firewall.lang.translations import translations
from firewall.UI.about import AboutDialog
from firewall.UI.menu import MenuManager
from firewall.UI.view_logs import ViewLogsWindow
from firewall.UI.sponsor import SponsorDialog as SponsorWindow
from firewall.UI.help import HelpWindow
from firewall.script.logger import get_logger
import os
import json
import qrcode
import sys
import tempfile
from datetime import datetime
from typing import Optional, Dict, Any, List

# Import FirewallManager from the main module
from firewall.script.firewall_manager import FirewallManager

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
            
    def setup_dark_theme(self):
        """Set up a modern dark theme with improved contrast and visual hierarchy"""
        self.setStyleSheet("""
            /* Base Colors */
            QMainWindow, QDialog, QWidget, QMenu {
                background-color: #1e1e1e;
                color: #ffffff;
                font-family: 'Segoe UI', 'Arial', sans-serif;
                border: none;
            }
            
            /* Text and Input Fields */
            QTextEdit, QPlainTextEdit, QLineEdit, QComboBox, QSpinBox, 
            QDoubleSpinBox, QDateEdit, QTimeEdit, QDateTimeEdit, QTableWidget {
                background-color: #252526;
                color: #ffffff;
                border: 1px solid #3e3e42;
                border-radius: 3px;
                padding: 5px 8px;
                selection-background-color: #264f78;
                selection-color: #ffffff;
            }
            
            /* Buttons */
            QPushButton, QToolButton {
                background-color: #333333;
                color: #ffffff;
                border: 1px solid #3e3e42;
                border-radius: 3px;
                padding: 5px 12px;
                min-width: 80px;
            }
            
            QPushButton:hover, QToolButton:hover {
                background-color: #0d7d0d;
                border: 1px solid #505050; 
            }
            
            QPushButton:pressed, QToolButton:pressed {
                background-color: #095609;
            }
            
            QPushButton:disabled, QToolButton:disabled {
                color: #7f7f7f;
                background-color: #2d2d2d;
                border: 1px solid #3e3e42;
            }
            
            /* Tabs */
            QTabWidget::pane {
                border: 1px solid #3e3e42;
                background: #252526;
                margin: 0;
                padding: 0;
            }
            
            QTabBar::tab {
                background: #2d2d2d;
                color: #e0e0e0;
                padding: 8px 15px;
                border: 1px solid #3e3e42;
                border-bottom: none;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                margin-right: 2px;
            }
            
            QTabBar::tab:selected, QTabBar::tab:hover {
                background: #1e1e1e;
                border-bottom: 1px solid #1e1e1e;
                margin-bottom: -1px;
            }
            
            QTabBar::tab:!selected {
                margin-top: 2px;
            }
            
            /* Headers and Sections */
            QHeaderView::section, QTableCornerButton::section {
                background-color: #333333;
                color: #ffffff;
                padding: 6px;
                border: 1px solid #3e3e42;
                text-align: left;
            }
            
            /* Scroll Bars */
            QScrollBar:vertical, QScrollBar:horizontal {
                background: #252526;
                width: 12px;
                height: 12px;
            }
            
            QScrollBar::handle:vertical, QScrollBar::handle:horizontal {
                background: #424242;
                border-radius: 6px;
                min-height: 20px;
                min-width: 20px;
            }
            
            QScrollBar::handle:vertical:hover, QScrollBar::handle:horizontal:hover {
                background: #5a5a5a;
            }
            
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical,
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
                height: 0px;
                width: 0px;
            }
            
            /* Group Boxes */
            QGroupBox {
                border: 1px solid #3e3e42;
                border-radius: 4px;
                margin-top: 15px;
                padding-top: 15px;
            }
            
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
                background-color: transparent;
                color: #c5c5c5;
            }
            
            /* Menus */
            QMenuBar {
                background-color: #252526;
                color: #e0e0e0;
                border: none;
                padding: 2px;
            }
            
            QMenuBar::item:selected {
                background: #3a3a3a;
            }
            QMenu {
                background-color: #2b2b2b;
                color: #f0f0f0;
                border: 1px solid #4a4a4a;
            }
            QMenu::item:selected {
                background-color: #0078d7;
            }
            QStatusBar {
                background-color: #1e1e1e;
                color: #f0f0f0;
            }
            QToolBar {
                background-color: #2b2b2b;
                border: none;
                spacing: 2px;
            }
            QToolButton {
                background: transparent;
                border: 1px solid transparent;
                border-radius: 2px;
                padding: 2px;
            }
            QToolButton:hover {
                background: #3a3a3a;
                border: 1px solid #5a5a5a;
            }
            QToolButton:pressed {
                background: #1a1a1a;
            }
        """)

    def init_ui(self):
        """Initialize the main UI components"""
        # Set window properties first
        self.setWindowTitle(translations[self.current_language].get('app_title', 'Firewall Manager'))
        self.setMinimumSize(1000, 700)
        
        # Apply dark theme
        self.setup_dark_theme()
        
        # Initialize dialog references
        self.about_dialog = AboutDialog(self, self.current_language)
        self.view_logs_window = None
        self.sponsor_window = None
        self.help_window = None
        
        # Set window icon if available
        self.setup_window_icon()
        
        # Set up the main window
        self.setup_toolbar()
        
        # Create the main widget and UI elements first
        self.setup_main_widget()
        
        # Now set up the status bar after the main widget
        self.setup_statusbar()
        
        # Finally, connect all signals after UI is fully initialized
        self.setup_connections()
        
        # Load initial data
        self.load_initial_data()
        
        # Show the window
        self.show()
        
    def setup_main_widget(self):
        """Set up the main widget and its components"""
        # Create central widget and layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        
        # Create menu bar
        self.menu_manager = MenuManager(self, self.current_language)
        self.menu_bar = self.menuBar()
        self.menu_manager.create_menu_bar()
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        
        # Create tabs
        self.status_tab = self.create_status_tab()
        self.rules_tab = self.create_rules_tab()
        self.monitoring_tab = MonitoringTab(self, self.firewall)  # Add monitoring tab
        self.logs_tab = self.create_logs_tab()
        self.qr_tab = self.create_qr_tab()
        self.config_tab = self.create_config_tab()
        
        # Add tabs to the tab widget in a logical order
        self.tab_widget.addTab(self.status_tab, translations[self.current_language].get('tab_status', 'Status'))
        self.tab_widget.addTab(self.rules_tab, translations[self.current_language].get('tab_rules', 'Rules'))
        self.tab_widget.addTab(self.monitoring_tab, translations[self.current_language].get('tab_monitoring', 'Monitoring'))
        self.tab_widget.addTab(self.logs_tab, translations[self.current_language].get('tab_logs', 'Logs'))
        self.tab_widget.addTab(self.qr_tab, translations[self.current_language].get('tab_qr', 'QR Code'))
        self.tab_widget.addTab(self.config_tab, translations[self.current_language].get('tab_config', 'Configuration'))
        
        # Add tab widget to main layout
        self.main_layout.addWidget(self.tab_widget)
        
        # Apply any additional styling
        self.tab_widget.setStyleSheet("""
            QTabBar::tab {
                padding: 8px 16px;
                margin-right: 2px;
                background: #2d2d2d;
                color: #cccccc;
                border: 1px solid #3d3d3d;
                border-bottom: none;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }
            QTabBar::tab:selected {
                background: #3d3d3d;
                color: #ffffff;
            }
            QTabBar::tab:hover:!selected {
                background: #353535;
            }
        """)
    
    def setup_window_icon(self):
        """Set up the application window icon"""
        try:
            # Try to load the application icon if it exists
            icon_path = os.path.join(os.path.dirname(__file__), '..', 'assets', 'icon.ico')
            if os.path.exists(icon_path):
                self.setWindowIcon(QIcon(icon_path))
            else:
                # Fallback to system default icon
                self.setWindowIcon(self.style().standardIcon(QStyle.SP_ComputerIcon))
        except Exception as e:
            self.logger.error(f"Error setting window icon: {e}")
            # If anything goes wrong, just use the default icon
            self.setWindowIcon(self.style().standardIcon(QStyle.SP_ComputerIcon))

    def setup_toolbar(self):
        """Set up the main toolbar with common actions"""
        # Create toolbar
        self.toolbar = self.addToolBar('Main Toolbar')
        self.toolbar.setMovable(False)
        
        # Add a simple label to the toolbar
        self.status_label = QLabel(translations[self.current_language].get('status_ready', 'Ready'))
        self.toolbar.addWidget(self.status_label)
        
        # Add a stretch to push the status label to the right
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self.toolbar.addWidget(spacer)
        
        # Add a refresh button to the right
        refresh_action = QAction('⟳', self)  # Using a refresh symbol
        refresh_action.setStatusTip(translations[self.current_language].get('refresh', 'Refresh'))
        refresh_action.triggered.connect(self.update_ui)
        self.toolbar.addAction(refresh_action)
        
    def setup_statusbar(self):
        """Set up the status bar with status label and progress bar"""
        # Create status bar
        self.status_bar = self.statusBar()
        
        # Create status label
        self.status_label = QLabel(translations[self.current_language].get('status_ready', 'Ready'))
        self.status_bar.addPermanentWidget(self.status_label, 1)
        
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
    
    def add_rule_dialog(self):
        """Show dialog to add a new firewall rule"""
        try:
            # Create and show the rule dialog
            dialog = RuleDialog(self, self.firewall.translations.get(self.current_language, {}))
            if dialog.exec() == QDialog.DialogCode.Accepted:
                # Get the rule data from the dialog
                rule = dialog.get_rule()
                if rule:
                    # Add the rule using the firewall manager
                    if self.firewall.add_rule(rule):
                        # Refresh the rules table
                        self.load_rules()
                        self.logger.log_firewall_event("RULE_ADDED", f"Added rule: {rule.get('name', 'Unnamed')}")
                    else:
                        QMessageBox.warning(
                            self,
                            translations[self.current_language].get('error', 'Error'),
                            translations[self.current_language].get('add_rule_failed', 'Failed to add rule')
                        )
        except Exception as e:
            self.logger.log_error(f"Error in add_rule_dialog: {e}")
            QMessageBox.critical(
                self,
                translations[self.current_language].get('error', 'Error'),
                f"Error adding rule: {str(e)}"
            )

    def delete_rule(self):
        """Delete the selected firewall rule"""
        try:
            # Get the selected row
            selected_rows = self.rules_table.selectionModel().selectedRows()
            if not selected_rows:
                QMessageBox.warning(
                    self,
                    translations[self.current_language].get('warning', 'Warning'),
                    translations[self.current_language].get('select_rule_to_delete', 'Please select a rule to delete')
                )
                return

            row = selected_rows[0].row()
            
            # Get the rule data
            rule = {
                'name': self.rules_table.item(row, 0).text(),
                'protocol': self.rules_table.item(row, 1).text(),
                'port': self.rules_table.item(row, 2).text(),
                'direction': self.rules_table.item(row, 3).text(),
                'action': self.rules_table.item(row, 4).text(),
                'enabled': self.rules_table.item(row, 5).checkState() == Qt.Checked
            }
            
            # Confirm deletion
            confirm = QMessageBox.question(
                self,
                translations[self.current_language].get('confirm_delete', 'Confirm Delete'),
                translations[self.current_language].get('confirm_delete_rule', 'Are you sure you want to delete this rule?'),
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if confirm == QMessageBox.StandardButton.Yes:
                if self.firewall.delete_rule(rule):
                    # Refresh the rules table
                    self.load_rules()
                    self.logger.log_firewall_event("RULE_DELETED", f"Deleted rule: {rule.get('name', 'Unnamed')}")
                else:
                    QMessageBox.warning(
                        self,
                        translations[self.current_language].get('error', 'Error'),
                        translations[self.current_language].get('delete_rule_failed', 'Failed to delete rule')
                    )
        except Exception as e:
            self.logger.log_error(f"Error in delete_rule: {e}")
            QMessageBox.critical(
                self,
                translations[self.current_language].get('error', 'Error'),
                f"Error deleting rule: {str(e)}"
            )

    def edit_rule(self):
        """Edit the selected firewall rule"""
        try:
            # Get the selected row
            selected_rows = self.rules_table.selectionModel().selectedRows()
            if not selected_rows:
                QMessageBox.warning(
                    self,
                    translations[self.current_language].get('warning', 'Warning'),
                    translations[self.current_language].get('select_rule_to_edit', 'Please select a rule to edit')
                )
                return

            row = selected_rows[0].row()
            
            # Get the current rule data
            rule = {
                'name': self.rules_table.item(row, 0).text(),
                'protocol': self.rules_table.item(row, 1).text(),
                'port': self.rules_table.item(row, 2).text(),
                'direction': self.rules_table.item(row, 3).text(),
                'action': self.rules_table.item(row, 4).text(),
                'enabled': self.rules_table.item(row, 5).checkState() == Qt.Checked
            }
            
            # Open the edit dialog with the current rule data
            dialog = RuleDialog(self, translations[self.current_language], rule)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                # Get the updated rule data
                updated_rule = dialog.get_rule()
                if updated_rule:
                    # Update the rule using the firewall manager
                    if self.firewall.delete_rule(rule) and self.firewall.add_rule(updated_rule):
                        # Refresh the rules table
                        self.load_rules()
                        self.logger.log_firewall_event("RULE_UPDATED", f"Updated rule: {updated_rule.get('name', 'Unnamed')}")
                    else:
                        QMessageBox.warning(
                            self,
                            translations[self.current_language].get('error', 'Error'),
                            translations[self.current_language].get('update_rule_failed', 'Failed to update rule')
                        )
        except Exception as e:
            self.logger.log_error(f"Error in edit_rule: {e}")
            QMessageBox.critical(
                self,
                translations[self.current_language].get('error', 'Error'),
                f"Error editing rule: {str(e)}"
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
            
        # Connect rule management buttons
        if hasattr(self, 'add_rule_btn'):
            self.add_rule_btn.clicked.connect(self.add_rule_dialog)
            self.edit_rule_btn.clicked.connect(self.edit_rule)
            self.delete_rule_btn.clicked.connect(self.delete_rule)
            
            # Disable buttons that aren't implemented yet
            self.load_config_btn.setEnabled(False)
            self.save_config_btn.setEnabled(False)
    
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
                background-color: #1e1e1e;
            }
            QTabWidget::pane {
                border: 1px solid #c0c0c0;
                padding: 5px;
            }
            QTabBar::tab {
                background: #525252
                padding: 8px 12px;
                margin: 2px;
                border: 1px solid #c0c0c0;
                border-bottom: none;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }
            QTabBar::tab:selected {
                background: #7d7d7d
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
            
            # Refresh the rules table in case of error
            try:
                rules = self.firewall.get_rules()
                if hasattr(self, 'rules_table'):
                    self.rules_table.setRowCount(len(rules))
                    
                    for row, rule in enumerate(rules):
                        if not isinstance(rule, dict):
                            continue
                            
                        self.rules_table.setItem(row, 0, QTableWidgetItem(rule.get('name', '')))
                        self.rules_table.setItem(row, 1, QTableWidgetItem(rule.get('protocol', '')))
                        self.rules_table.setItem(row, 2, QTableWidgetItem(str(rule.get('port', ''))))
                        self.rules_table.setItem(row, 3, QTableWidgetItem(rule.get('direction', '')))
                        self.rules_table.setItem(row, 4, QTableWidgetItem(rule.get('action', '')))
            except Exception as refresh_error:
                self.logger.log_error(f"Error refreshing rules table: {refresh_error}")
                
        except Exception as e:
            self.logger.log_error(f"Error in toggle_firewall: {e}")
            QMessageBox.critical(
                self,
                translations[self.current_language].get('error', 'Error'),
                f"An error occurred: {str(e)}"
            )
    
    def refresh_logs(self):
        """Refresh the logs display"""
        try:
            if hasattr(self, 'logs_text'):
                # In a real application, you would load logs from a file or log handler
                self.logs_text.setPlainText("Logs will be displayed here...")
        except Exception as e:
            self.logger.log_error(f"Error refreshing logs: {e}")
    
    def load_rules(self):
        """Load firewall rules into the rules table"""
        try:
            if not hasattr(self, 'rules_table'):
                return
                
            self.rules_table.setRowCount(0)
            rules = self.firewall.get_rules()
            
            for row, rule in enumerate(rules):
                if not isinstance(rule, dict):
                    continue
                    
                self.rules_table.insertRow(row)
                
                # Add rule properties to the table
                self.rules_table.setItem(row, 0, QTableWidgetItem(rule.get('name', '')))
                self.rules_table.setItem(row, 1, QTableWidgetItem(rule.get('protocol', '')))
                self.rules_table.setItem(row, 2, QTableWidgetItem(str(rule.get('port', ''))))
                self.rules_table.setItem(row, 3, QTableWidgetItem(rule.get('direction', '')))
                self.rules_table.setItem(row, 4, QTableWidgetItem(rule.get('action', '')))
                
                # Add enabled checkbox
                enabled_item = QTableWidgetItem()
                enabled_item.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
                enabled_item.setCheckState(Qt.Checked if rule.get('enabled', True) else Qt.Unchecked)
                self.rules_table.setItem(row, 5, enabled_item)
                
            # Resize columns to fit content
            self.rules_table.resizeColumnsToContents()
                
        except Exception as e:
            self.logger.log_error(f"Error loading rules: {e}")
            QMessageBox.critical(
                self,
                translations[self.current_language].get('error', 'Error'),
                translations[self.current_language].get('load_rules_failed', 'Failed to load rules') + f": {str(e)}"
            )
    
    # Tab creation methods
    def create_rules_tab(self):
        """Create the rules management tab"""
        rules_tab = QWidget()
        layout = QVBoxLayout(rules_tab)
        
        # Create rules table
        self.rules_table = QTableWidget()
        self.rules_table.setColumnCount(6)
        self.rules_table.setHorizontalHeaderLabels([
            translations[self.current_language].get('name', 'Name'),
            translations[self.current_language].get('direction', 'Direction'),
            translations[self.current_language].get('action', 'Action'),
            translations[self.current_language].get('protocol', 'Protocol'),
            translations[self.current_language].get('port', 'Port'),
            translations[self.current_language].get('enabled', 'Enabled')
        ])
        self.rules_table.horizontalHeader().setStretchLastSection(True)
        self.rules_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.rules_table.setSelectionMode(QTableWidget.SingleSelection)
        
        # Create buttons
        button_layout = QHBoxLayout()
        
        self.add_rule_btn = QPushButton(translations[self.current_language].get('add_rule', 'Add Rule'))
        self.edit_rule_btn = QPushButton(translations[self.current_language].get('edit_rule', 'Edit Rule'))
        self.delete_rule_btn = QPushButton(translations[self.current_language].get('delete_rule', 'Delete Rule'))
        
        # Config management buttons
        self.import_rules_btn = QPushButton(translations[self.current_language].get('import_rules', 'Import Rules'))
        self.export_rules_btn = QPushButton(translations[self.current_language].get('export_rules', 'Export Rules'))
        
        # Add buttons to layout
        button_layout.addWidget(self.add_rule_btn)
        button_layout.addWidget(self.edit_rule_btn)
        button_layout.addWidget(self.delete_rule_btn)
        button_layout.addStretch()
        button_layout.addWidget(self.import_rules_btn)
        button_layout.addWidget(self.export_rules_btn)
        
        # Connect buttons
        self.add_rule_btn.clicked.connect(self.add_rule_dialog)
        self.edit_rule_btn.clicked.connect(self.edit_rule)
        self.delete_rule_btn.clicked.connect(self.delete_rule)
        self.import_rules_btn.clicked.connect(self.import_rules)
        self.export_rules_btn.clicked.connect(self.export_rules)
        
        # Add widgets to layout
        layout.addWidget(self.rules_table)
        layout.addLayout(button_layout)
        
        # Initial load of rules
        self.load_rules()
        
        return rules_tab
        
    def create_status_tab(self):
        """Create the status tab"""
        status_tab = QWidget()
        layout = QVBoxLayout(status_tab)
        
        # Create button layout
        button_layout = QHBoxLayout()
        
        # Status group
        status_group = QGroupBox(translations[self.current_language].get('status', 'Status'))
        status_layout = QVBoxLayout()
        
        # Status label
        self.status_label = QLabel()
        self.status_label.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self.status_label.setStyleSheet("font-family: monospace;")
        
        # Toggle button with green background and white text
        self.toggle_button = QPushButton()
        self.toggle_button.setStyleSheet("""
            QPushButton {
                background-color: #2e7d32;
                color: white;
                font-weight: bold;
                padding: 8px 16px;
                border: 1px solid #1b5e20;
                border-radius: 4px;
                min-width: 120px;
            }
            QPushButton:hover {
                background-color: #1b5e20;
            }
            QPushButton:pressed {
                background-color: #0d3e10;
            }
        """)
        self.toggle_button.clicked.connect(self.toggle_firewall)
        
        status_layout.addWidget(self.status_label)
        status_layout.addWidget(self.toggle_button)
        status_group.setLayout(status_layout)
        
        self.add_rule_btn = QPushButton(translations[self.current_language].get('add_rule', 'Add Rule'))
        self.edit_rule_btn = QPushButton(translations[self.current_language].get('edit_rule', 'Edit Rule'))
        self.delete_rule_btn = QPushButton(translations[self.current_language].get('delete_rule', 'Delete Rule'))
        
        # Config management buttons
        self.load_config_btn = QPushButton(translations[self.current_language].get('load_config', 'Load Config'))
        self.save_config_btn = QPushButton(translations[self.current_language].get('save_config', 'Save Config'))
        
        # Add status information
        status_group = QGroupBox(translations[self.current_language].get('firewall_status', 'Firewall Status'))
        status_layout = QVBoxLayout()
        
        self.status_label = QLabel(translations[self.current_language].get('status_off', 'Status: Off'))
        self.toggle_button = QPushButton(translations[self.current_language].get('enable_firewall', 'Enable Firewall'))
        self.toggle_button.setStyleSheet("""
            QPushButton {
                background-color: #1e88e5;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1976d2;
            }
            QPushButton:pressed {
                background-color: #1565c0;
            }
        """)
        
        status_layout.addWidget(self.status_label)
        status_layout.addWidget(self.toggle_button)
        status_group.setLayout(status_layout)
        
        # Add status group to main layout
        layout.addWidget(status_group)
        
        # Add stretch to push content to the top
        layout.addStretch()
        
        return status_tab
        
        layout.addWidget(self.rules_table)
        layout.addLayout(button_layout)
        
        return rules_tab
    
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
        
        return logs_tab
    
    def create_qr_tab(self):
        """Create the QR code generation tab"""
        qr_tab = QWidget()
        layout = QVBoxLayout(qr_tab)
        
        # Add generate button and connect it
        self.generate_btn = QPushButton(translations[self.current_language].get('generate_qr', 'Generate QR Code'))
        def on_generate_clicked():
            self.logger.info("Generate button clicked - connection working")
            self.generate_qr_code()
        self.generate_btn.clicked.connect(on_generate_clicked)
        layout.addWidget(self.generate_btn)
    
        # Add a label to indicate what this tab is for
        info_label = QLabel(translations[self.current_language].get('qr_tab_info', 'Generate QR codes for sharing firewall rules'))
        info_label.setWordWrap(True)
        layout.addWidget(info_label)
        
        # Add input field for text to encode in QR code
        self.qr_input = QTextEdit()
        self.qr_input.setPlaceholderText(translations[self.current_language].get('qr_input_placeholder', 'Enter text to generate QR code...'))
        layout.addWidget(QLabel(translations[self.current_language].get('input_text', 'Input Text:')))
        layout.addWidget(self.qr_input)
        
        # Add generate button
        generate_btn = QPushButton(translations[self.current_language].get('generate_qr', 'Generate QR Code'))
        generate_btn.clicked.connect(self.generate_qr_code)
        layout.addWidget(generate_btn)
        
        # Add label to display the QR code
        self.qr_label = QLabel()
        self.qr_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.qr_label)
        
        # Add stretch to push content to the top
        layout.addStretch()
        
        # Apply dark theme styling
        qr_tab.setStyleSheet("""
            QWidget {
                background-color: #2d2d2d;
                color: #f0f0f0;
            }
            QTextEdit {
                background-color: #3d3d3d;
                color: #f0f0f0;
                border: 1px solid #4d4d4d;
                border-radius: 4px;
                padding: 5px;
            }
            QPushButton {
                background-color: #1e88e5;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1976d2;
            }
            QPushButton:pressed {
                background-color: #1565c0;
            }
            QLabel {
                color: #f0f0f0;
            }
        """)
        
        return qr_tab

# ... (rest of the code remains the same)
    
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
        
        return config_tab
    
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
            self.view_logs_window = ViewLogsWindow(self, self.current_language, self.logger)
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
        # Generate a QR code from the input text using pure Python and Qt
        try:
            self.logger.info("Generate QR Code button clicked")
            
            # Get text from input
            text = self.qr_input.toPlainText().strip()
            self.logger.info(f"Input text: {text[:50]}{'...' if len(text) > 50 else ''}")
            
            if not text:
                self.logger.warning("No text entered for QR code generation")
                QMessageBox.warning(
                    self,
                    translations[self.current_language].get('warning', 'Warning'),
                    translations[self.current_language].get('qr_empty_warning', 'Please enter some text first')
                )
                return

            self.logger.info("Generating QR code data...")
            from firewall.UI.qr_generator import generate_qr_code_data, qr_to_qimage
            qr_data = generate_qr_code_data(text)
            self.logger.info(f"QR data generated, size: {len(qr_data)}x{len(qr_data[0]) if qr_data else 0}")
            
            self.logger.info("Converting QR data to QImage...")
            qimage = qr_to_qimage(qr_data, scale=10, border=4)
            self.logger.info(f"QImage created, size: {qimage.width()}x{qimage.height()}")
            
            self.logger.info("Converting to QPixmap...")
            pixmap = QPixmap.fromImage(qimage)
            if pixmap.isNull():
                raise ValueError("Failed to create QPixmap from QImage")
            self.logger.info("QPixmap created successfully")
            
            # Calculate target size with some margin
            target_width = max(100, self.qr_label.width() - 10)
            target_height = max(100, self.qr_label.height() - 10)
            self.logger.info(f"Scaling to: {target_width}x{target_height}")
            
            # Scale the pixmap
            scaled_pixmap = pixmap.scaled(
                target_width,
                target_height,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            
            self.logger.info("Updating QR code display...")
            self.qr_label.setPixmap(scaled_pixmap)
            self.qr_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.logger.info("QR code displayed successfully")
            
        except Exception as e:
            error_msg = f"Error generating QR code: {str(e)}"
            self.logger.error(error_msg, exc_info=True)
            QMessageBox.critical(
                self,
                translations[self.current_language].get('error', 'Error'),
                error_msg
            )
    
    def import_rules(self):
        """Import firewall rules from a JSON file"""
        try:
            # Show file dialog to select import file
            file_path, _ = QFileDialog.getOpenFileName(
                self,
                translations[self.current_language].get('import_rules', 'Import Rules'),
                "",  # Start in current directory
                "JSON Files (*.json);;All Files (*)"
            )
            
            if file_path:
                # Read the file
                with open(file_path, 'r') as f:
                    rules = json.load(f)
                
                # Validate rules format
                if not isinstance(rules, list):
                    raise ValueError("Invalid rules format: expected a list of rules")
                
                # Add each rule
                success_count = 0
                for rule in rules:
                    if self.firewall.add_rule(rule):
                        success_count += 1
                
                # Refresh the rules table
                self.load_rules()
                
                # Show result
                QMessageBox.information(
                    self,
                    translations[self.current_language].get('success', 'Success'),
                    translations[self.current_language].get('rules_imported', 'Rules imported successfully')
                )
                
        except Exception as e:
            self.logger.log_error(f"Error importing rules: {e}")
            QMessageBox.critical(
                self,
                translations[self.current_language].get('error', 'Error'),
                f"Failed to import rules: {str(e)}"
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
        
    # Removed duplicate create_qr_tab method
    def create_config_tab(self):
        """Create the configuration tab with application settings"""
        config_tab = QWidget()
        layout = QVBoxLayout(config_tab)
        
        # Create a scroll area to handle many settings
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        
        # Language settings
        lang_group = QGroupBox(translations[self.current_language].get('settings_language', 'Language Settings'))
        lang_layout = QFormLayout()
        
        self.language_combo = QComboBox()
        self.language_combo.addItem("English", "en")
        self.language_combo.addItem("Italiano", "it")
        # Add more languages as needed
        
        # Set current language
        current_index = self.language_combo.findData(self.current_language)
        if current_index >= 0:
            self.language_combo.setCurrentIndex(current_index)
            
        self.language_combo.currentIndexChanged.connect(self.on_language_changed)
        
        lang_layout.addRow(translations[self.current_language].get('settings_language', 'Language:'), 
                          self.language_combo)
        lang_group.setLayout(lang_layout)
        
        # Theme settings
        theme_group = QGroupBox(translations[self.current_language].get('settings_theme', 'Appearance'))
        theme_layout = QVBoxLayout()
        
        self.theme_combo = QComboBox()
        self.theme_combo.addItem(translations[self.current_language].get('theme_dark', 'Dark'), 'dark')
        self.theme_combo.addItem(translations[self.current_language].get('theme_light', 'Light'), 'light')
        self.theme_combo.addItem(translations[self.current_language].get('theme_system', 'System'), 'system')
        
        # Load saved theme preference
        current_theme = self.firewall.config.config.get('settings', {}).get('theme', 'dark')
        theme_index = self.theme_combo.findData(current_theme)
        if theme_index >= 0:
            self.theme_combo.setCurrentIndex(theme_index)
            
        self.theme_combo.currentIndexChanged.connect(self.on_theme_changed)
        
        theme_layout.addWidget(QLabel(translations[self.current_language].get('settings_theme', 'Theme:')))
        theme_layout.addWidget(self.theme_combo)
        
        # Add theme preview or additional appearance settings here
        
        theme_group.setLayout(theme_layout)
        
        # Firewall behavior settings
        fw_group = QGroupBox(translations[self.current_language].get('settings_firewall', 'Firewall Behavior'))
        fw_layout = QFormLayout()
        
        # Auto-start with system
        self.auto_start_cb = QCheckBox(translations[self.current_language].get('settings_autostart', 'Start with system'))
        self.auto_start_cb.setChecked(self.firewall.config.config.get('settings', {}).get('auto_start', False))
        self.auto_start_cb.stateChanged.connect(self.on_auto_start_changed)
        
        # Show notifications
        self.show_notifications_cb = QCheckBox(translations[self.current_language].get('settings_notifications', 'Show notifications'))
        self.show_notifications_cb.setChecked(self.firewall.config.config.get('settings', {}).get('show_notifications', True))
        self.show_notifications_cb.stateChanged.connect(self.on_notifications_changed)
        
        # Block all incoming connections by default
        self.block_incoming_cb = QCheckBox(translations[self.current_language].get('settings_block_incoming', 'Block all incoming connections by default'))
        self.block_incoming_cb.setChecked(self.firewall.config.config.get('settings', {}).get('block_incoming', True))
        self.block_incoming_cb.stateChanged.connect(self.on_block_incoming_changed)
        
        fw_layout.addRow(self.auto_start_cb)
        fw_layout.addRow(self.show_notifications_cb)
        fw_layout.addRow(self.block_incoming_cb)
        
        # Add more firewall settings as needed
        
        fw_group.setLayout(fw_layout)
        
        # Add all groups to the scroll layout
        scroll_layout.addWidget(lang_group)
        scroll_layout.addWidget(theme_group)
        scroll_layout.addWidget(fw_group)
        
        # Add stretch to push content to the top
        scroll_layout.addStretch()
        
        # Set the scroll content
        scroll.setWidget(scroll_content)
        
        # Add scroll to main layout
        layout.addWidget(scroll)
        
        # Add save and reset buttons
        button_layout = QHBoxLayout()
        
        save_btn = QPushButton(translations[self.current_language].get('save', 'Save'))
        save_btn.clicked.connect(self.save_settings)
        
        reset_btn = QPushButton(translations[self.current_language].get('reset', 'Reset to Defaults'))
        reset_btn.clicked.connect(self.reset_settings)
        
        button_layout.addStretch()
        button_layout.addWidget(reset_btn)
        button_layout.addWidget(save_btn)
        
        layout.addLayout(button_layout)
        
        return config_tab
        
    def update_ui(self):
        """Update all UI elements"""
        pass
        
    def on_language_changed(self, index):
        """Handle language change from the settings tab"""
        try:
            new_lang = self.language_combo.currentData()
            if new_lang and new_lang != self.current_language:
                # Update the language using the firewall manager
                if not self.firewall.change_language(new_lang):
                    self.logger.log_error(f"Failed to change language to {new_lang}")
                    return
                    
                # Update the UI
                self.current_language = new_lang
                self.retranslate_ui()
                
                # No need to update settings again as change_language already does this
                
                # Show a message that the app needs to restart for changes to take effect
                QMessageBox.information(
                    self,
                    translations[self.current_language].get('restart_required', 'Restart Required'),
                    translations[self.current_language].get('restart_message', 'Please restart the application for language changes to take full effect.')
                )
        except Exception as e:
            self.logger.log_error(f"Error changing language: {e}")
            QMessageBox.critical(
                self,
                translations[self.current_language].get('error', 'Error'),
                f"Failed to change language: {str(e)}"
            )
    
    def on_theme_changed(self, index):
        """Handle theme change from the settings tab"""
        try:
            theme = self.theme_combo.currentData()
            if theme:
                # Update the theme in settings
                settings = self.firewall.config.config.get('settings', {})
                settings['theme'] = theme
                self.firewall.config.update_settings(settings)
                
                # Apply the theme
                if theme == 'dark':
                    self.setup_dark_theme()
                elif theme == 'light':
                    self.setup_light_theme()
                else:  # system
                    # You can implement system theme detection here
                    self.setup_dark_theme()  # Default to dark for now
        except Exception as e:
            self.logger.log_error(f"Error changing theme: {e}")
    
    def on_auto_start_changed(self, state):
        """Handle auto-start setting change"""
        try:
            auto_start = state == Qt.Checked
            settings = self.firewall.config.config.get('settings', {})
            settings['auto_start'] = auto_start
            self.firewall.config.update_settings(settings)
            
            # Here you would typically update the system auto-start setting
            # This is platform-specific code that would need to be implemented
            self.update_auto_start(auto_start)
        except Exception as e:
            self.logger.log_error(f"Error updating auto-start setting: {e}")
    
    def on_notifications_changed(self, state):
        """Handle notifications setting change"""
        try:
            show_notifications = state == Qt.Checked
            settings = self.firewall.config.config.get('settings', {})
            settings['show_notifications'] = show_notifications
            self.firewall.config.update_settings(settings)
        except Exception as e:
            self.logger.log_error(f"Error updating notifications setting: {e}")
    
    def on_block_incoming_changed(self, state):
        """Handle block incoming connections setting change"""
        try:
            block_incoming = state == Qt.Checked
            settings = self.firewall.config.config.get('settings', {})
            settings['block_incoming'] = block_incoming
            self.firewall.config.update_settings(settings)
            
            # Apply the firewall rule change
            self.firewall.update_settings({'block_incoming': block_incoming})
        except Exception as e:
            self.logger.log_error(f"Error updating block incoming setting: {e}")
    
    def save_settings(self):
        """Save all settings from the settings tab"""
        try:
            # Most settings are saved automatically when changed
            # This method can be used for settings that need to be saved together
            QMessageBox.information(
                self,
                translations[self.current_language].get('settings_saved', 'Settings Saved'),
                translations[self.current_language].get('settings_saved_msg', 'All settings have been saved.')
            )
        except Exception as e:
            self.logger.log_error(f"Error saving settings: {e}")
            QMessageBox.critical(
                self,
                translations[self.current_language].get('error', 'Error'),
                f"Failed to save settings: {str(e)}"
            )
    
    def reset_settings(self):
        """Reset all settings to default values"""
        try:
            reply = QMessageBox.question(
                self,
                translations[self.current_language].get('confirm_reset', 'Confirm Reset'),
                translations[self.current_language].get('confirm_reset_msg', 'Are you sure you want to reset all settings to default values?'),
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                # Reset to default values
                default_settings = {
                    'language': 'en',
                    'theme': 'dark',
                    'auto_start': False,
                    'show_notifications': True,
                    'block_incoming': True
                }
                
                # Update settings using the proper method
                if not self.firewall.config.update_settings(default_settings):
                    self.logger.log_error("Failed to reset settings to defaults")
                    QMessageBox.critical(
                        self,
                        translations[self.current_language].get('error', 'Error'),
                        translations[self.current_language].get('reset_failed', 'Failed to reset settings to default values.')
                    )
                    return
                
                # Update UI to reflect default settings
                self.current_language = 'en'
                self.retranslate_ui()
                self.setup_dark_theme()
                
                # Reset UI controls
                lang_index = self.language_combo.findData('en')
                if lang_index >= 0:
                    self.language_combo.setCurrentIndex(lang_index)
                    
                theme_index = self.theme_combo.findData('dark')
                if theme_index >= 0:
                    self.theme_combo.setCurrentIndex(theme_index)
                    
                self.auto_start_cb.setChecked(False)
                self.show_notifications_cb.setChecked(True)
                self.block_incoming_cb.setChecked(True)
                
                QMessageBox.information(
                    self,
                    translations[self.current_language].get('settings_reset', 'Settings Reset'),
                    translations[self.current_language].get('settings_reset_msg', 'All settings have been reset to default values.')
                )
        except Exception as e:
            self.logger.log_error(f"Error resetting settings: {e}")
            QMessageBox.critical(
                self,
                translations[self.current_language].get('error', 'Error'),
                f"Failed to reset settings: {str(e)}"
            )
    
    def update_auto_start(self, enable):
        """Update system auto-start setting (platform-specific)"""
        # This is a placeholder for platform-specific auto-start implementation
        # You would need to implement this based on the target OS
        if sys.platform == 'win32':
            # Windows implementation
            import winreg as reg
            try:
                key = reg.HKEY_CURRENT_USER
                key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
                with reg.OpenKey(key, key_path, 0, reg.KEY_ALL_ACCESS) as registry_key:
                    if enable:
                        reg.SetValueEx(registry_key, "TuxFw", 0, reg.REG_SZ, sys.executable)
                    else:
                        try:
                            reg.DeleteValue(registry_key, "TuxFw")
                        except WindowsError:
                            pass  # Key doesn't exist, which is fine
            except Exception as e:
                self.logger.log_error(f"Error updating Windows auto-start: {e}")
        elif sys.platform == 'darwin':
            # macOS implementation
            pass  # Implement macOS auto-start
        else:
            # Linux implementation
            pass  # Implement Linux auto-start

    def setup_light_theme(self):
        """Set up a light theme for the application"""
        self.setStyleSheet("""
            QMainWindow, QDialog, QWidget {
                background-color: #f0f0f0;
                color: #333333;
            }
            QTabWidget::pane {
                border: 1px solid #c0c0c0;
                background: #ffffff;
                margin: 0px;
                padding: 5px;
            }
            QTabBar::tab {
                background: #e0e0e0;
                border: 1px solid #c0c0c0;
                padding: 8px 12px;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background: #ffffff;
                border-bottom-color: #ffffff;
            }
            QGroupBox {
                border: 1px solid #c0c0c0;
                border-radius: 4px;
                margin-top: 10px;
                padding-top: 15px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
            QPushButton {
                background-color: #e0e0e0;
                border: 1px solid #c0c0c0;
                padding: 5px 15px;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #d0d0d0;
            }
            QPushButton:pressed {
                background-color: #c0c0c0;
            }
            QLineEdit, QComboBox, QTextEdit, QSpinBox, QDoubleSpinBox {
                border: 1px solid #c0c0c0;
                padding: 5px;
                border-radius: 3px;
                background: #ffffff;
                color: #000000;
            }
            QTableWidget {
                gridline-color: #e0e0e0;
                background: #ffffff;
                color: #000000;
            }
            QHeaderView::section {
                background-color: #e0e0e0;
                padding: 5px;
                border: 1px solid #c0c0c0;
            }
            QStatusBar {
                background: #e0e0e0;
                color: #333333;
            }
        """)
        
    def load_settings(self):
        """Load settings from configuration"""
        try:
            # This method is called during initialization to load saved settings
            settings = self.firewall.config.config.get('settings', {})
            
            # Apply theme
            theme = settings.get('theme', 'dark')
            if theme == 'light':
                self.setup_light_theme()
            elif theme == 'system':
                # Implement system theme detection if needed
                self.setup_dark_theme()
            else:
                self.setup_dark_theme()
                
            # Other settings can be loaded here if needed
            
        except Exception as e:
            self.logger.log_error(f"Error loading settings: {e}")
            # Fall back to default theme if there's an error
            self.setup_dark_theme()

    def import_rules(self):
        """Import rules from a JSON file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            self.translations[self.current_language].get('import_rules', 'Import Rules'),
            "",
            "JSON Files (*.json);;All Files (*)"
        )
        
        if file_path:
            try:
                # Ask if user wants to merge or replace existing rules
                reply = QMessageBox.question(
                    self,
                    self.translations[self.current_language].get('import_options', 'Import Options'),
                    self.translations[self.current_language].get('import_prompt', 'Merge with existing rules?\nClick No to replace all rules.'),
                    QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel
                )
                
                if reply == QMessageBox.Cancel:
                    return
                    
                merge = (reply == QMessageBox.Yes)
                
                # Call the firewall manager to handle the import
                if self.firewall.import_rules(file_path, merge=merge):
                    self.load_rules()
                    QMessageBox.information(
                        self,
                        self.translations[self.current_language].get('success', 'Success'),
                        self.translations[self.current_language].get('import_success', 'Rules imported successfully')
                    )
                else:
                    raise Exception("Failed to import rules")
                    
            except Exception as e:
                QMessageBox.critical(
                    self,
                    self.translations[self.current_language].get('error', 'Error'),
                    self.translations[self.current_language].get('import_error', 'Failed to import rules: ') + str(e)
                )
    
    def export_rules(self):
        """Export rules to a JSON file"""
        if not self.firewall.get_rules():
            QMessageBox.warning(
                self,
                self.translations[self.current_language].get('no_rules', 'No Rules'),
                self.translations[self.current_language].get('no_rules_to_export', 'No rules to export')
            )
            return
            
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            self.translations[self.current_language].get('export_rules', 'Export Rules'),
            f"firewall_rules_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            "JSON Files (*.json);;All Files (*)"
        )
        
        if file_path:
            try:
                if not file_path.lower().endswith('.json'):
                    file_path += '.json'
                    
                if self.firewall.export_rules(file_path):
                    QMessageBox.information(
                        self,
                        self.translations[self.current_language].get('success', 'Success'),
                        self.translations[self.current_language].get('export_success', f'Rules exported to {file_path}')
                    )
                else:
                    raise Exception("Failed to export rules")
                    
            except Exception as e:
                QMessageBox.critical(
                    self,
                    self.translations[self.current_language].get('error', 'Error'),
                    self.translations[self.current_language].get('export_error', 'Failed to export rules: ') + str(e)
                )
    
    def on_rule_selection_changed(self):
        """Handle rule selection change in the table"""
        selected = len(self.rules_table.selectedItems()) > 0
        self.edit_btn.setEnabled(selected)
        self.delete_btn.setEnabled(selected)

class RuleDialog(QDialog):
    """Dialog for adding/editing firewall rules with advanced options"""
    
    def __init__(self, parent, translations, rule=None):
        super().__init__(parent)
        self.translations = translations
        self.rule = rule or {}
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the rule dialog UI"""
        self.setWindowTitle(
            self.translations.get('edit_rule', 'Edit Rule') if self.rule.get('id') 
            else self.translations.get('add_rule', 'Add Rule')
        )
        self.setMinimumWidth(600)
        
        layout = QVBoxLayout(self)
        
        # Create form layout for rule properties
        form_layout = QFormLayout()
        
        # Rule name
        self.name_edit = QLineEdit(self.rule.get('name', ''))
        form_layout.addRow(self.translations.get('rule_name', 'Name:'), self.name_edit)
        
        # Action (Allow/Block/Reject)
        self.action_combo = QComboBox()
        self.action_combo.addItem(self.translations.get('allow', 'Allow'), 'allow')
        self.action_combo.addItem(self.translations.get('block', 'Block'), 'block')
        self.action_combo.addItem(self.translations.get('reject', 'Reject'), 'reject')
        
        # Set current action if editing
        if 'action' in self.rule:
            index = self.action_combo.findData(self.rule['action'])
            if index >= 0:
                self.action_combo.setCurrentIndex(index)
        form_layout.addRow(self.translations.get('action', 'Action:'), self.action_combo)
        
        # Direction (In/Out/Both)
        self.direction_combo = QComboBox()
        self.direction_combo.addItem(self.translations.get('inbound', 'Inbound'), 'in')
        self.direction_combo.addItem(self.translations.get('outbound', 'Outbound'), 'out')
        self.direction_combo.addItem(self.translations.get('both', 'Both'), 'both')
        
        if 'direction' in self.rule:
            index = self.direction_combo.findData(self.rule['direction'])
            if index >= 0:
                self.direction_combo.setCurrentIndex(index)
        form_layout.addRow(self.translations.get('direction', 'Direction:'), self.direction_combo)
        
        # Protocol
        self.protocol_combo = QComboBox()
        self.protocol_combo.addItem('TCP', 'tcp')
        self.protocol_combo.addItem('UDP', 'udp')
        self.protocol_combo.addItem('ICMP', 'icmp')
        self.protocol_combo.addItem('ICMPv6', 'icmpv6')
        self.protocol_combo.addItem('All', 'all')
        
        if 'protocol' in self.rule:
            index = self.protocol_combo.findData(self.rule['protocol'])
            if index >= 0:
                self.protocol_combo.setCurrentIndex(index)
        form_layout.addRow(self.translations.get('protocol', 'Protocol:'), self.protocol_combo)
        
        # Ports
        self.port_edit = QLineEdit(self.rule.get('port', ''))
        self.port_edit.setPlaceholderText('80, 443, 1000-2000')
        form_layout.addRow(self.translations.get('port', 'Port(s):'), self.port_edit)
        
        # Source IP
        self.source_ip_edit = QLineEdit(self.rule.get('source_ip', ''))
        self.source_ip_edit.setPlaceholderText('192.168.1.0/24 or any')
        form_layout.addRow(self.translations.get('source_ip', 'Source IP:'), self.source_ip_edit)
        
        # Source Port
        self.source_port_edit = QLineEdit(self.rule.get('source_port', ''))
        self.source_port_edit.setPlaceholderText('1024-65535')
        form_layout.addRow(self.translations.get('source_port', 'Source Port:'), self.source_port_edit)
        
        # IP Version
        self.ip_version_combo = QComboBox()
        self.ip_version_combo.addItem('IPv4', 'ip')
        self.ip_version_combo.addItem('IPv6', 'ip6')
        self.ip_version_combo.addItem(self.translations.get('any', 'Any'), 'any')
        
        if 'ip_version' in self.rule:
            index = self.ip_version_combo.findData(self.rule['ip_version'])
            if index >= 0:
                self.ip_version_combo.setCurrentIndex(index)
        form_layout.addRow(self.translations.get('ip_version', 'IP Version:'), self.ip_version_combo)
        
        # Connection State
        self.state_combo = QComboBox()
        self.state_combo.addItem(self.translations.get('any_state', 'Any State'), '')
        self.state_combo.addItem('NEW', 'new')
        self.state_combo.addItem('ESTABLISHED', 'established')
        self.state_combo.addItem('RELATED', 'related')
        self.state_combo.addItem('INVALID', 'invalid')
        
        if 'state' in self.rule:
            index = self.state_combo.findData(self.rule['state'])
            if index >= 0:
                self.state_combo.setCurrentIndex(index)
        form_layout.addRow(self.translations.get('connection_state', 'Connection State:'), self.state_combo)
        
        # Logging options
        self.logging_group = QGroupBox(self.translations.get('logging', 'Logging'))
        logging_layout = QVBoxLayout()
        
        self.enable_logging = QCheckBox(self.translations.get('enable_logging', 'Enable logging for this rule'))
        self.enable_logging.setChecked(self.rule.get('logging', False))
        logging_layout.addWidget(self.enable_logging)
        
        log_options_layout = QHBoxLayout()
        
        # Log Level
        self.log_level_combo = QComboBox()
        self.log_level_combo.addItem('Info', 'info')
        self.log_level_combo.addItem('Warning', 'warning')
        self.log_level_combo.addItem('Error', 'error')
        
        if 'log_level' in self.rule:
            index = self.log_level_combo.findData(self.rule['log_level'])
            if index >= 0:
                self.log_level_combo.setCurrentIndex(index)
        
        log_options_layout.addWidget(QLabel(self.translations.get('log_level', 'Log Level:')))
        log_options_layout.addWidget(self.log_level_combo)
        
        # Log Prefix
        self.log_prefix_edit = QLineEdit(self.rule.get('log_prefix', 'RULE'))
        log_options_layout.addWidget(QLabel(self.translations.get('log_prefix', 'Prefix:')), 1)
        log_options_layout.addWidget(self.log_prefix_edit, 2)
        
        logging_layout.addLayout(log_options_layout)
        self.logging_group.setLayout(logging_layout)
        
        # Description
        self.desc_edit = QTextEdit(self.rule.get('description', ''))
        self.desc_edit.setMaximumHeight(80)
        form_layout.addRow(self.translations.get('description', 'Description:'), self.desc_edit)
        
        # Add form layout to main layout
        layout.addLayout(form_layout)
        
        # Add logging group
        layout.addWidget(self.logging_group)
        
        # Add button box
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
    
    def get_rule(self):
        """Get the rule data from the dialog"""
        # Create a new rule or update the existing one
        rule = self.rule.copy() if self.rule else {}
        
        # Update rule with form values
        rule.update({
            'name': self.name_edit.text().strip(),
            'action': self.action_combo.currentData(),
            'direction': self.direction_combo.currentData(),
            'protocol': self.protocol_combo.currentData(),
            'port': self.port_edit.text().strip(),
            'source_ip': self.source_ip_edit.text().strip(),
            'source_port': self.source_port_edit.text().strip(),
            'ip_version': self.ip_version_combo.currentData(),
            'state': self.state_combo.currentData(),
            'logging': self.enable_logging.isChecked(),
            'log_level': self.log_level_combo.currentData(),
            'log_prefix': self.log_prefix_edit.text().strip(),
            'description': self.desc_edit.toPlainText().strip()
        })
        
        return rule
