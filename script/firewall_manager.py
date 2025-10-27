#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json
import sys
import uuid
from PySide6.QtWidgets import (
    QDialog, QFormLayout, QWidget, QLineEdit, 
    QComboBox, QCheckBox, QDialogButtonBox, QFileDialog
)
from PySide6.QtCore import Qt
from logger import get_logger

class FirewallConfig:
    """
    Handle firewall configuration JSON file operations
    
    This class manages the loading, saving, and validation of firewall
    configuration from/to JSON files.
    """

    def __init__(self, config_path=None, translations=None):
        """
        Initialize the FirewallConfig
        
        Args:
            config_path (str, optional): Path to the configuration file.
                Defaults to "config/firewall_config.json".
            translations (dict, optional): Dictionary of translations for the UI.
        """
        if config_path is None:
            # Default to config directory
            self.config_path = os.path.join("config", "firewall_config.json")
        else:
            self.config_path = config_path
            
        # Store translations and set default language
        self.translations = translations or {}
        self.current_language = 'en'  # Default language
        
        # Initialize logger
        self.logger = get_logger("firewall.config")
        
        # Load configuration
        self.config = self.load_config()
        
        # Update current_language from config if available
        if 'language' in self.config.get('settings', {}):
            self.current_language = self.config['settings']['language']

    def load_config(self, file_path=None):
        """
        Load configuration from JSON file
        
        Args:
            file_path (str, optional): Path to the configuration file.
                If None, uses the default config path.
                
        Returns:
            dict: The loaded configuration
        """
        try:
            path = file_path or self.config_path
            if os.path.exists(path):
                with open(path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                return self.get_default_config()
        except Exception as e:
            error_msg = f"Error loading config from {path}: {str(e)}"
            if hasattr(self, 'logger'):
                self.logger.log_error(error_msg, "FirewallConfig.load_config")
            else:
                print(error_msg)  # Fallback if logger not available
            return self.get_default_config()

    def save_config(self, file_path=None):
        """
        Save configuration to JSON file
        
        Args:
            file_path (str, optional): Path to save the configuration.
                If None, uses the default config path.
                
        Returns:
            bool: True if save was successful, False otherwise
        """
        try:
            path = file_path or self.config_path
            os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=4)
            return True
        except Exception as e:
            error_msg = f"Error saving config to {path}: {str(e)}"
            if hasattr(self, 'logger'):
                self.logger.log_error(error_msg, "FirewallConfig.save_config")
            else:
                print(error_msg)  # Fallback if logger not available
            return False

    def get_default_config(self):
        """Get default configuration"""
        return {
            "settings": {
                "enabled": True,
                "block_inbound": True,
                "block_outbound": False,
                "default_action": "block",
                "log_level": "info"
            },
            "profiles": {
                "default": {
                    "enabled": True,
                    "rules": []
                }
            },
            "current_profile": "default"
        }

    def get_rules(self):
        """Get current firewall rules"""
        try:
            # Ensure config has the right structure
            if not hasattr(self, 'config') or not isinstance(self.config, dict):
                self.config = self.get_default_config()
                return []
            
            # Handle old config format where rules are directly under firewall_rules
            if "firewall_rules" in self.config and isinstance(self.config["firewall_rules"], list):
                # Migrate old format to new format
                self.config["profiles"] = {
                    "default": {
                        "rules": self.config["firewall_rules"]
                    }
                }
                self.config["current_profile"] = "default"
                # Remove the old key to avoid confusion
                del self.config["firewall_rules"]
                self.save_config()
                
            # Ensure profiles exists and is a dictionary
            if "profiles" not in self.config or not isinstance(self.config["profiles"], dict):
                self.config["profiles"] = {"default": {"rules": []}}
                self.save_config()
                return []
            
            # Get current profile, default to 'default' if not set
            current_profile = self.config.get("current_profile", "default")
            
            # Ensure the current profile exists and has a rules list
            if not isinstance(self.config["profiles"].get(current_profile), dict):
                self.config["profiles"][current_profile] = {"rules": []}
                self.save_config()
                return []
                
            # Ensure rules exists and is a list
            if "rules" not in self.config["profiles"][current_profile] or not isinstance(self.config["profiles"][current_profile]["rules"], list):
                self.config["profiles"][current_profile]["rules"] = []
                self.save_config()
            
            # Ensure each rule has all required fields
            rules = self.config["profiles"][current_profile]["rules"]
            for rule in rules:
                if not isinstance(rule, dict):
                    rules.remove(rule)
                    continue
                # Ensure required fields exist
                rule.setdefault('id', str(uuid.uuid4()))
                rule.setdefault('name', 'Unnamed Rule')
                rule.setdefault('protocol', 'TCP')
                rule.setdefault('port', '')
                rule.setdefault('direction', 'IN')
                rule.setdefault('action', 'ALLOW')
                rule.setdefault('enabled', True)
                
            return rules
        except Exception as e:
            self.logger.log_error(f"Error getting rules: {str(e)}")
            return []

    def add_rule(self, rule):
        """Add a new firewall rule"""
        if "id" not in rule:
            rule["id"] = str(uuid.uuid4())
        current_profile = self.config["current_profile"]
        self.config["profiles"][current_profile].setdefault("rules", []).append(rule)
        return self.save_config()

    def update_rule(self, rule_id, updated_rule):
        """Update an existing firewall rule"""
        current_profile = self.config["current_profile"]
        rules = self.get_rules()
        for i, rule in enumerate(rules):
            if rule["id"] == rule_id:
                updated_rule["id"] = rule_id  # Ensure ID remains the same
                self.config["profiles"][current_profile]["rules"][i] = updated_rule
                return self.save_config()
        return False

    def delete_rule(self, rule_id):
        """Delete a firewall rule"""
        current_profile = self.config["current_profile"]
        rules = self.get_rules()
        self.config["profiles"][current_profile]["rules"] = [r for r in rules if r["id"] != rule_id]
        return self.save_config()

    def get_settings(self):
        """Get firewall settings"""
        return self.config.get("settings", {})

    def update_settings(self, settings):
        """Update firewall settings
        
        Args:
            settings (dict): Dictionary of settings to update
            
        Returns:
            bool: True if settings were updated successfully, False otherwise
        """
        try:
            if not isinstance(settings, dict):
                self.logger.log_error(f"Invalid settings format: {settings}")
                return False
                
            # Ensure settings dictionary exists in config
            if 'settings' not in self.config or not isinstance(self.config['settings'], dict):
                self.config['settings'] = {}
            
            # Store the current settings for rollback in case of error
            old_settings = self.config['settings'].copy()
            
            try:
                # Update the settings
                self.config['settings'].update(settings)
                
                # Save the updated configuration
                if not self.save_config():
                    raise Exception("Failed to save configuration")
                    
                return True
                
            except Exception as e:
                # Rollback to old settings if there was an error
                self.config['settings'] = old_settings
                raise
            
        except Exception as e:
            self.logger.log_error(f"Error updating settings: {e}")
            return False

    def update_ui(self):
        """Update UI elements (stub for backward compatibility)"""
        pass

    def change_language(self, language):
        """Change the application language"""
        self.current_language = language
        self.config.update_settings({"language": language})
        self.logger.log_firewall_event("LANGUAGE_CHANGED", f"Changed language to {language}")
        return True
        self.tab_widget.setTabText(0, translations[self.current_language]['tab_status'])
        self.tab_widget.setTabText(1, translations[self.current_language]['tab_rules'])
        self.tab_widget.setTabText(2, translations[self.current_language]['tab_logs'])
        self.tab_widget.setTabText(3, translations[self.current_language]['tab_qr'])
        self.tab_widget.setTabText(4, translations[self.current_language]['tab_config'])

        # Update table headers
        headers = [
            translations[self.current_language]['rule_name'],
            translations[self.current_language]['protocol'],
            translations[self.current_language]['port'],
            translations[self.current_language]['direction'],
            translations[self.current_language]['action'],
            translations[self.current_language]['description'],
            translations[self.current_language]['enabled']
        ]
        self.rules_table.setHorizontalHeaderLabels(headers)

        # Update buttons and other controls
        self.update_ui_texts()

    def update_ui_texts(self):
        """Update UI text elements"""
        # Status tab
        if hasattr(self, 'toggle_button') and self.toggle_button is not None:
            self.toggle_button.setText(translations[self.current_language]['enable_firewall'] if not self.config.get_settings().get('firewall_enabled') else translations[self.current_language]['disable_firewall'])

        # Rules tab
        if hasattr(self, 'add_rule_button') and self.add_rule_button is not None:
            self.add_rule_button.setText(translations[self.current_language]['add_rule'])
        if hasattr(self, 'edit_rule_button') and self.edit_rule_button is not None:
            self.edit_rule_button.setText(translations[self.current_language]['edit_rule'])
        if hasattr(self, 'delete_rule_button') and self.delete_rule_button is not None:
            self.delete_rule_button.setText(translations[self.current_language]['delete_rule'])

        # Logs tab
        if hasattr(self, 'refresh_logs_button') and self.refresh_logs_button is not None:
            self.refresh_logs_button.setText(translations[self.current_language]['refresh'])
        if hasattr(self, 'clear_logs_button') and self.clear_logs_button is not None:
            self.clear_logs_button.setText(translations[self.current_language]['clear_logs'])
        if hasattr(self, 'save_logs_button') and self.save_logs_button is not None:
            self.save_logs_button.setText(translations[self.current_language]['save_logs'])

        # QR tab
        if hasattr(self, 'generate_qr_button') and self.generate_qr_button is not None:
            self.generate_qr_button.setText(translations[self.current_language]['generate_qr'])

        # Config tab
        if hasattr(self, 'save_config_button') and self.save_config_button is not None:
            self.save_config_button.setText(translations[self.current_language]['save_config'])
        if hasattr(self, 'load_config_button') and self.load_config_button is not None:
            self.load_config_button.setText(translations[self.current_language]['load_config'])
        if hasattr(self, 'reset_config_button') and self.reset_config_button is not None:
            self.reset_config_button.setText(translations[self.current_language]['reset_config'])

    def toggle_firewall(self):
        """Toggle firewall on/off"""
        settings = self.config.get_settings()
        new_status = not settings.get('firewall_enabled', False)

        if self.config.update_settings({'firewall_enabled': new_status}):
            self.update_ui_texts()
            self.statusBar().showMessage(
                translations[self.current_language]['firewall_enabled'] if new_status
                else translations[self.current_language]['firewall_disabled']
            )

            # Log the firewall status change
            event_type = "FIREWALL_ENABLED" if new_status else "FIREWALL_DISABLED"
            self.logger.log_firewall_event(event_type, f"Firewall {'enabled' if new_status else 'disabled'} by user")

            self.log_message(f"Firewall {'enabled' if new_status else 'disabled'}", "FIREWALL_TOGGLE")

    def add_rule_dialog(self):
        """Show add rule dialog"""
        dialog = RuleDialog(self, translations[self.current_language])
        if dialog.exec():
            rule = dialog.get_rule()
            if self.config.add_rule(rule):
                self.load_rules()
                # Log the rule addition
                self.logger.log_config_change("RULE_ADDED", f"Added rule '{rule['name']}' ({rule['protocol']}:{rule['port']})")
                self.log_message(f"Rule '{rule['name']}' added", "RULE_ADDED")
                QMessageBox.information(self, translations[self.current_language]['success'],
                                      translations[self.current_language]['rule_added'] or 'Rule added successfully')

    def edit_rule_dialog(self):
        """Show edit rule dialog"""
        current_row = self.rules_table.currentRow()
        if current_row == -1:
            QMessageBox.warning(self, translations[self.current_language]['warning'],
                              translations[self.current_language]['no_rule_selected'] or 'No rule selected')
            return

        rule_id = self.rules_table.item(current_row, 0).data(Qt.ItemDataRole.UserRole)
        rules = self.config.get_rules()
        rule = next((r for r in rules if r['id'] == rule_id), None)

        if rule:
            dialog = RuleDialog(self, translations[self.current_language], rule)
            if dialog.exec():
                updated_rule = dialog.get_rule()
                if self.config.update_rule(rule_id, updated_rule):
                    self.load_rules()
                    # Log the rule update
                    self.logger.log_config_change("RULE_UPDATED", f"Updated rule '{updated_rule['name']}' ({updated_rule['protocol']}:{updated_rule['port']})")
                    self.log_message(f"Rule '{updated_rule['name']}' updated", "RULE_UPDATED")

    def delete_rule(self):
        """Delete selected rule"""
        current_row = self.rules_table.currentRow()
        if current_row == -1:
            QMessageBox.warning(self, translations[self.current_language]['warning'],
                              translations[self.current_language]['no_rule_selected'] or 'No rule selected')
            return

        rule_id = self.rules_table.item(current_row, 0).data(Qt.ItemDataRole.UserRole)
        rules = self.config.get_rules()
        rule = next((r for r in rules if r['id'] == rule_id), None)

        if rule:
            reply = QMessageBox.question(self, translations[self.current_language]['confirm'],
                                       f"Delete rule '{rule['name']}'?",
                                       QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

            if reply == QMessageBox.StandardButton.Yes:
                if self.config.delete_rule(rule_id):
                    self.load_rules()
                    # Log the rule deletion
                    self.logger.log_config_change("RULE_DELETED", f"Deleted rule '{rule['name']}' ({rule['protocol']}:{rule['port']})")
                    self.log_message(f"Rule '{rule['name']}' deleted", "RULE_DELETED")

    def refresh_logs(self):
        """Refresh logs"""
        self.logger.log_firewall_event("LOGS_REFRESHED", "User refreshed logs manually")
        self.log_message(translations[self.current_language]['logs_refreshed'] or 'Logs refreshed')

    def clear_logs(self):
        """Clear logs"""
        self.logs_text.clear()
        self.logger.log_firewall_event("LOGS_CLEARED", "User cleared logs manually")
        self.log_message(translations[self.current_language]['logs_cleared'] or 'Logs cleared')

    def save_logs(self):
        """Save logs to file"""
        file_path, _ = QFileDialog.getSaveFileName(self, translations[self.current_language]['save_logs'],
                                                 "", "Text Files (*.txt);;All Files (*)")

        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(self.logs_text.toPlainText())
                self.statusBar().showMessage(translations[self.current_language]['logs_saved'])
                # Log the logs save
                self.logger.log_firewall_event("LOGS_SAVED", f"Logs saved to {file_path}")
            except Exception as e:
                self.logger.log_error(f"Failed to save logs to {file_path}: {e}", context="LogsTab.save_logs")
                QMessageBox.critical(self, translations[self.current_language]['error'],
                                   f"{translations[self.current_language]['save_error']}: {str(e)}")

    def generate_qr_code(self):
        """Generate QR code"""
        text = self.qr_input.text().strip()
        if not text:
            QMessageBox.warning(self, translations[self.current_language]['warning'],
                              translations[self.current_language]['qr_empty'])
            return

        try:
            # Generate QR code
            qr = qrcode.QRCode(version=1, box_size=10, border=5)
            qr.add_data(text)
            qr.make(fit=True)

            # Create image
            qr_img = qr.make_image(fill_color="black", back_color="white")

            # Save to temporary file and load
            temp_path = "temp_qr.png"
            qr_img.save(temp_path)

            # Display in label
            pixmap = QPixmap(temp_path)
            self.qr_label.setPixmap(pixmap.scaled(300, 300, Qt.AspectRatioMode.KeepAspectRatio))

            # Clean up
            if os.path.exists(temp_path):
                os.remove(temp_path)

            self.statusBar().showMessage(translations[self.current_language]['qr_generated'])
            # Log the QR code generation
            self.logger.log_firewall_event("QR_GENERATED", f"QR code generated for text: {text[:50]}{'...' if len(text) > 50 else ''}")

        except Exception as e:
            self.logger.log_error(f"Failed to generate QR code: {e}", context="QRTab.generate_qr_code")
            QMessageBox.critical(self, translations[self.current_language]['error'],
                               f"{translations[self.current_language]['qr_error']}: {str(e)}")

    def save_config(self):
        """Save configuration"""
        if self.config.save_config():
            self.statusBar().showMessage(translations[self.current_language]['config_saved'])
            # Log the configuration save
            self.logger.log_config_change("CONFIG_SAVED", "Configuration saved successfully")
        else:
            self.logger.log_error("Failed to save configuration", context="ConfigTab.save_config")
            QMessageBox.critical(self, translations[self.current_language]['error'],
                               "Failed to save configuration")


    def reset_config(self):
        """Reset configuration to defaults"""
        reply = QMessageBox.question(
            self, 
            self.translations[self.current_language]['confirm'],
            self.translations[self.current_language].get('confirm_reset', 'Reset all settings to defaults?'),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.config = FirewallConfig(translations=self.translations)
            self.load_settings()
            self.load_rules()
            self.update_ui()
            self.statusBar().showMessage(
                self.translations[self.current_language]['config_reset']
            )
            # Log the configuration reset
            self.logger.log_config_change(
                "CONFIG_RESET", 
                self.translations[self.current_language].get(
                    'config_reset_log', 
                    'Configuration reset to defaults'
                )
            )

    def change_profile(self, profile_name):
        """Change current profile"""
        # Implementation for profile switching
        self.statusBar().showMessage(f"Profile changed to: {profile_name}")
        # Log the profile change
        self.logger.log_config_change("PROFILE_CHANGED", f"Switched to profile: {profile_name}")

    def update_status(self):
        """Update status information"""
        # Only update if elements exist
        if hasattr(self, 'status_label') and self.status_label is not None:
            settings = self.config.get_settings()
            self.status_label.setText(
                translations[self.current_language]['status_active'] if settings.get('firewall_enabled')
                else translations[self.current_language]['status_inactive']
            )

        if hasattr(self, 'blocked_label') and self.blocked_label is not None:
            self.blocked_label.setText(str(len([r for r in self.config.get_rules() if r.get('action') == 'BLOCK'])))

        if hasattr(self, 'allowed_label') and self.allowed_label is not None:
            self.allowed_label.setText(str(len([r for r in self.config.get_rules() if r.get('action') == 'ALLOW'])))

        if hasattr(self, 'rules_label') and self.rules_label is not None:
            self.rules_label.setText(str(len(self.config.get_rules())))

    def load_settings(self):
        """Load settings from configuration"""
        # Only load settings once
        if self.settings_loaded:
            return

        settings = self.config.get_settings()
        self.current_language = settings.get('language', 'en')

        # Load UI element settings only if elements exist
        if hasattr(self, 'firewall_enabled_cb') and self.firewall_enabled_cb is not None:
            self.firewall_enabled_cb.setChecked(settings.get('firewall_enabled', False))

        if hasattr(self, 'logging_enabled_cb') and self.logging_enabled_cb is not None:
            self.logging_enabled_cb.setChecked(settings.get('logging_enabled', True))

        if hasattr(self, 'default_policy_combo') and self.default_policy_combo is not None:
            self.default_policy_combo.setCurrentText(settings.get('default_policy', 'BLOCK'))

        # Load profiles
        if hasattr(self, 'profile_combo') and self.profile_combo is not None:
            profiles = self.config.config.get('profiles', {})
            self.profile_combo.clear()
            for profile_name, profile_data in profiles.items():
                self.profile_combo.addItem(profile_data['name'], profile_name)

            current_profile = self.config.config.get('current_profile', 'default')
            index = self.profile_combo.findData(current_profile)
            if index != -1:
                self.profile_combo.setCurrentIndex(index)

        self.settings_loaded = True

    def load_rules(self):
        """Load rules into the table"""
        # Only load rules if the table exists
        if hasattr(self, 'rules_table') and self.rules_table is not None:
            rules = self.config.get_rules()
            self.rules_table.setRowCount(len(rules))

            for row, rule in enumerate(rules):
                self.rules_table.setItem(row, 0, QTableWidgetItem(rule.get('name', '')))
                self.rules_table.item(row, 0).setData(Qt.ItemDataRole.UserRole, rule['id'])

                self.rules_table.setItem(row, 1, QTableWidgetItem(rule.get('protocol', '')))
                self.rules_table.setItem(row, 2, QTableWidgetItem(rule.get('port', '')))
                self.rules_table.setItem(row, 3, QTableWidgetItem(rule.get('direction', '')))
                self.rules_table.setItem(row, 4, QTableWidgetItem(rule.get('action', '')))
                self.rules_table.setItem(row, 5, QTableWidgetItem(rule.get('description', '')))

                # Enabled checkbox
                enabled_item = QTableWidgetItem()
                enabled_item.setCheckState(Qt.CheckState.Checked if rule.get('enabled', True) else Qt.CheckState.Unchecked)
                self.rules_table.setItem(row, 6, enabled_item)

    def log_message(self, message, event_type="UI_EVENT"):
        """Add message to logs and log to file"""
        # Log to file using the logger
        self.logger.log_firewall_event(event_type, message)

        # Also update the UI text area if it exists
        if hasattr(self, 'logs_text') and self.logs_text is not None:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.logs_text.append(f"[{timestamp}] {message}")

    def show_logs(self):
        """Show logs window"""
        if self.view_logs_window is None:
            self.view_logs_window = ViewLogsWindow(self, self.current_language, self.logger)
        self.view_logs_window.show()
        self.view_logs_window.raise_()
        self.view_logs_window.activateWindow()
        self.logger.log_firewall_event("LOGS_VIEWED", "User opened logs viewer")

    def show_sponsors(self):
        """Show sponsors window"""
        if self.sponsor_window is None:
            self.sponsor_window = SponsorWindow(self, self.current_language)
        self.sponsor_window.show()
        self.sponsor_window.raise_()
        self.sponsor_window.activateWindow()
        self.logger.log_firewall_event("SPONSORS_VIEWED", "User opened sponsors window")

    def show_help(self):
        """Show help window"""
        if self.help_window is None:
            self.help_window = HelpWindow(self, self.current_language)


class RuleDialog(QDialog):
    """Dialog for adding/editing firewall rules"""

    def __init__(self, parent, translations, rule=None):
        super().__init__(parent)
        self.translations = translations
        self.rule = rule or {}
        self.setup_ui()

    def setup_ui(self):
        """Setup the rule dialog UI"""
        self.setWindowTitle(self.translations['add_rule'] if not self.rule else self.translations['edit_rule'])

        # Create form widget
        form_widget = QWidget()
        layout = QFormLayout(form_widget)

        # Rule name
        self.name_input = QLineEdit()
        self.name_input.setText(self.rule.get('name', ''))
        layout.addRow(self.translations['rule_name'] + ":", self.name_input)

        # Description
        self.description_input = QLineEdit()
        self.description_input.setText(self.rule.get('description', ''))
        layout.addRow(self.translations['description'] + ":", self.description_input)

        # Protocol
        self.protocol_combo = QComboBox()
        self.protocol_combo.addItems(['TCP', 'UDP', 'ICMP'])
        self.protocol_combo.setCurrentText(self.rule.get('protocol', 'TCP'))
        layout.addRow(self.translations['protocol'] + ":", self.protocol_combo)

        # Port
        self.port_input = QLineEdit()
        self.port_input.setText(self.rule.get('port', ''))
        layout.addRow(self.translations['port'] + ":", self.port_input)

        # Direction
        self.direction_combo = QComboBox()
        self.direction_combo.addItems(['IN', 'OUT'])
        self.direction_combo.setCurrentText(self.rule.get('direction', 'IN'))
        layout.addRow(self.translations['direction'] + ":", self.direction_combo)

        # Action
        self.action_combo = QComboBox()
        self.action_combo.addItems(['ALLOW', 'BLOCK'])
        self.action_combo.setCurrentText(self.rule.get('action', 'ALLOW'))
        layout.addRow(self.translations['action'] + ":", self.action_combo)

        # Enabled
        self.enabled_cb = QCheckBox(self.translations['enabled'])
        self.enabled_cb.setChecked(self.rule.get('enabled', True))
        layout.addRow("", self.enabled_cb)

        # Set the form as the dialog's widget
        self.layout().addWidget(form_widget, 0, 0, 1, self.layout().columnCount())

        # Add buttons
        self.addButton(self.translations['ok'], QMessageBox.ButtonRole.AcceptRole)
        self.addButton(self.translations['cancel'], QMessageBox.ButtonRole.RejectRole)

        self.setDefaultButton(self.button(QMessageBox.ButtonRole.AcceptRole))

    def get_rule(self):
        """Get the rule data from the dialog"""
        return {
            'name': self.name_input.text().strip(),
            'description': self.description_input.text().strip(),
            'protocol': self.protocol_combo.currentText(),
            'port': self.port_input.text().strip(),
            'direction': self.direction_combo.currentText(),
            'action': self.action_combo.currentText(),
            'enabled': self.enabled_cb.isChecked()
        }

class FirewallManager:
    """
    Main firewall management class that handles the core functionality
    of the firewall application.
    """
    
    def __init__(self, config_path=None, translations=None):
        """
        Initialize the FirewallManager
        
        Args:
            config_path (str, optional): Path to the configuration file. 
                Defaults to None, which uses the default path.
            translations (dict, optional): Dictionary of translations for the UI.
                If not provided, it will be loaded when needed.
        """
        self.logger = get_logger("firewall")
        
        # If translations are not provided, import them now
        if translations is None:
            from lang.translations import translations as default_translations
            self.translations = default_translations
        else:
            self.translations = translations
            
        # Initialize config with translations
        self.config = FirewallConfig(config_path, self.translations)
        
        # Set current language from config or default to 'en'
        self.current_language = self.config.current_language
        
        self.logger.log_firewall_event("MANAGER_INIT", "Firewall manager initialized")
    
    def get_status(self):
        """
        Get the current status of the firewall
        
        Returns:
            dict: Dictionary containing firewall status information
        """
        settings = self.config.get_settings()
        return {
            'enabled': settings.get('enabled', False),
            'block_inbound': settings.get('block_inbound', True),
            'block_outbound': settings.get('block_outbound', False),
            'default_action': settings.get('default_action', 'block'),
            'current_profile': self.config.config.get('current_profile', 'default'),
            'rules_count': len(self.config.get_rules())
        }
    
    def toggle_firewall(self, enabled):
        """
        Toggle the firewall on or off
        
        Args:
            enabled (bool): Whether to enable or disable the firewall
            
        Returns:
            bool: True if the operation was successful, False otherwise
        """
        try:
            self.config.update_settings({'enabled': enabled})
            self.logger.log_firewall_event(
                "FIREWALL_TOGGLE", 
                f"Firewall {'enabled' if enabled else 'disabled'}"
            )
            return True
        except Exception as e:
            self.logger.log_error(f"Error toggling firewall: {e}")
            return False
    
    def apply_rules(self):
        """
        Apply the current firewall rules to the system
        
        Returns:
            bool: True if the operation was successful, False otherwise
        """
        try:
            # In a real implementation, this would apply the rules to the system firewall
            rules = self.config.get_rules()
            self.logger.log_firewall_event(
                "RULES_APPLIED", 
                f"Applied {len(rules)} firewall rules"
            )
            return True
        except Exception as e:
            self.logger.log_error(f"Error applying rules: {e}")
            return False
    
    def change_language(self, language):
        """
        Change the application language
        
        Args:
            language (str): Language code (e.g., 'en', 'it')
            
        Returns:
            bool: True if the language was changed successfully, False otherwise
        """
        try:
            if not language or not isinstance(language, str):
                self.logger.log_error(f"Invalid language code: {language}")
                return False
                
            # Update the current language
            self.current_language = language
            
            # Update the language in the config
            success = self.config.update_settings({'language': language})
            if not success:
                self.logger.log_error(f"Failed to update language setting: {language}")
                return False
                
            # Log the language change
            self.logger.log_firewall_event(
                "LANGUAGE_CHANGED", 
                f"Changed language to {language}"
            )
            return True
        except Exception as e:
            self.logger.log_error(f"Error changing language: {e}")
            return False
    
    def get_rules(self):
        """
        Get the current firewall rules
        
        Returns:
            list: List of firewall rules
        """
        return self.config.get_rules()
    
    def add_rule(self, rule):
        """
        Add a new firewall rule
        
        Args:
            rule (dict): The rule to add
            
        Returns:
            bool: True if the rule was added successfully, False otherwise
        """
        try:
            result = self.config.add_rule(rule)
            if result:
                self.logger.log_firewall_event(
                    "RULE_ADDED", 
                    f"Added rule: {rule.get('name', 'Unnamed rule')}"
                )
            return result
        except Exception as e:
            self.logger.log_error(f"Error adding rule: {e}")
            return False
    
    def update_rule(self, rule_id, updated_rule):
        """
        Update an existing firewall rule
        
        Args:
            rule_id (str): The ID of the rule to update
            updated_rule (dict): The updated rule data
            
        Returns:
            bool: True if the rule was updated successfully, False otherwise
        """
        try:
            result = self.config.update_rule(rule_id, updated_rule)
            if result:
                self.logger.log_firewall_event(
                    "RULE_UPDATED", 
                    f"Updated rule: {updated_rule.get('name', 'Unnamed rule')}"
                )
            return result
        except Exception as e:
            self.logger.log_error(f"Error updating rule: {e}")
            return False
    
    def delete_rule(self, rule_id):
        """
        Delete a firewall rule
        
        Args:
            rule_id (str): The ID of the rule to delete
            
        Returns:
            bool: True if the rule was deleted successfully, False otherwise
        """
        try:
            result = self.config.delete_rule(rule_id)
            if result:
                self.logger.log_firewall_event("RULE_DELETED", f"Deleted rule ID: {rule_id}")
            return result
        except Exception as e:
            self.logger.log_error(f"Error deleting rule: {e}")
            return False
    
    def get_settings(self):
        """
        Get the current firewall settings
        
        Returns:
            dict: Dictionary containing the current settings
        """
        return self.config.get_settings()
    
    def update_settings(self, settings):
        """
        Update firewall settings
        
        Args:
            settings (dict): Dictionary of settings to update
            
        Returns:
            bool: True if the settings were updated successfully, False otherwise
        """
        try:
            # Update the settings in the config
            if not self.config.config.get('settings'):
                self.config.config['settings'] = {}
            self.config.config['settings'].update(settings)
            
            # Save the updated configuration
            if self.config.save_config():
                self.logger.log_firewall_event(
                    "SETTINGS_UPDATED", 
                    f"Updated settings: {', '.join(settings.keys())}"
                )
                return True
            return False
        except Exception as e:
            self.logger.log_error(f"Error updating settings: {e}")
            return False


if __name__ == "__main__":
    # This file is not meant to be run directly
    # Use script/main.py instead
    print("This is a module and should not be run directly. Use script/main.py instead.")
    sys.exit(1)
