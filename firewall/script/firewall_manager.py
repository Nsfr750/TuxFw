#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json
import sys
import uuid
import platform
import threading
from datetime import datetime
from typing import Dict, List, Optional, Any, Union, Tuple, Callable
from PySide6.QtWidgets import (
    QDialog, QFormLayout, QWidget, QLineEdit, QTextEdit,
    QComboBox, QCheckBox, QDialogButtonBox, QFileDialog, QMessageBox,
    QVBoxLayout, QLabel, QSpinBox, QGroupBox, QHBoxLayout
)
from PySide6.QtCore import Qt, QCoreApplication, QSize, QObject, Signal
from firewall.script.logger import get_logger

# Import nftables manager
from firewall.script.nftables_manager import NFTablesManager
from firewall.script.network_monitor import NetworkMonitor, IntrusionDetectionSystem
from firewall.script.network_zones import ZoneManager, VPNManager, NetworkZone
from firewall.script.win_firewall import WindowsFirewallController
from .security_utils import (
    EnhancedSecurity,
    SecurityAction,
    RateLimitConfig,
    RateLimiter,
    IPReputationChecker,
    GeoIPBlocker,
    PortKnocking,
)

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
            # Debug: Log the type of self and available attributes
            self.logger.log_debug(f"get_rules called. Type of self: {type(self)}")
            self.logger.log_debug(f"Available attributes: {dir(self)}")
            
            # Ensure config has the right structure
            if not hasattr(self, 'config') or not isinstance(self.config, dict):
                self.logger.log_debug("Config not found or not a dict, getting default config")
                self.config = self.get_default_config()
                return []
            
            # Make a copy of the config to avoid modifying it directly
            config = self.config.copy()
            needs_save = False
            
            # Handle old config format where rules are directly under firewall_rules
            if "firewall_rules" in config and isinstance(config["firewall_rules"], list):
                self.logger.log_debug("Found old format config, migrating to new format")
                # Migrate old format to new format
                config["profiles"] = {
                    "default": {
                        "rules": config["firewall_rules"]
                    }
                }
                config["current_profile"] = "default"
                # Remove the old key to avoid confusion
                del config["firewall_rules"]
                needs_save = True
                
            # Ensure profiles exists and is a dictionary
            if "profiles" not in config or not isinstance(config["profiles"], dict):
                self.logger.log_debug("Profiles not found or not a dict, initializing")
                config["profiles"] = {"default": {"rules": []}}
                needs_save = True
                
            # Get current profile, default to 'default' if not set
            current_profile = config.get("current_profile", "default")
            self.logger.log_debug(f"Current profile: {current_profile}")
            
            # Ensure the current profile exists and has a rules list
            if not isinstance(config["profiles"].get(current_profile), dict):
                self.logger.log_debug(f"Profile {current_profile} not found or not a dict, initializing")
                config["profiles"][current_profile] = {"rules": []}
                needs_save = True
                
            # Ensure rules exists and is a list
            if "rules" not in config["profiles"][current_profile] or not isinstance(config["profiles"][current_profile]["rules"], list):
                self.logger.log_debug("Rules not found or not a list, initializing")
                config["profiles"][current_profile]["rules"] = []
                needs_save = True
            
            # Ensure each rule has all required fields
            rules = config["profiles"][current_profile]["rules"]
            self.logger.log_debug(f"Found {len(rules)} rules in profile {current_profile}")
            
            for rule in rules:
                if not isinstance(rule, dict):
                    self.logger.log_debug("Found non-dict rule, removing")
                    rules.remove(rule)
                    needs_save = True
                    continue
                    
                # Check if any required fields are missing
                required_fields = {
                    'id': str(uuid.uuid4()),
                    'name': 'Unnamed Rule',
                    'protocol': 'TCP',
                    'port': '',
                    'direction': 'IN',
                    'action': 'ALLOW',
                    'enabled': True
                }
                
                # Set any missing fields to their default values
                for field, default_value in required_fields.items():
                    if field not in rule:
                        self.logger.log_debug(f"Adding missing field '{field}' to rule")
                        rule[field] = default_value
                        needs_save = True
            
            # Save the updated config if any changes were made
            if needs_save:
                self.logger.log_debug("Saving updated config")
                self.config = config
                try:
                    # Save the config to file
                    with open(self.config_path, 'w', encoding='utf-8') as f:
                        json.dump(self.config, f, indent=4, ensure_ascii=False)
                    self.logger.log_debug("Config saved successfully")
                except Exception as e:
                    self.logger.log_error(f"Failed to save config: {str(e)}")
                    return False
                
            self.logger.log_debug(f"Returning {len(rules)} rules")
            return rules
            
        except Exception as e:
            self.logger.log_error(f"Error in get_rules: {type(e).__name__}: {str(e)}", exc_info=True)
            import traceback
            self.logger.log_error(f"Traceback: {traceback.format_exc()}")
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
        """
        Update firewall settings
        
        Args:
            settings (dict): Dictionary of settings to update
            
        Returns:
            bool: True if settings were updated successfully, False otherwise
        """
        try:
            # Update the settings in the config
            if 'settings' not in self.config:
                self.config['settings'] = {}
                
            # Update the settings
            self.config['settings'].update(settings)
            
            # Save the configuration
            if not self.save_config():
                raise Exception("Failed to save configuration")
                
            # Update current_language if it was changed
            if 'language' in settings:
                self.current_language = settings['language']
                
            return True
            
        except Exception as e:
            self.logger.log_error(f"Error updating settings: {e}")
            return False

            return False

    def update_ui(self):
        """Update UI elements (stub for backward compatibility)"""
        pass

    def change_language(self, language):
        """Change the application language"""
        try:
            # Update the language in settings
            settings = self.config.get_settings()
            settings['language'] = language
            if not self.config.update_settings(settings):
                raise Exception("Failed to update language setting")
                
            # Update current language
            self.current_language = language
            self.logger.log_firewall_event("LANGUAGE_CHANGED", f"Changed language to {language}")
            
            # Update UI elements if they exist
            if hasattr(self, 'tab_widget') and self.tab_widget is not None:
                self.tab_widget.setTabText(0, translations[self.current_language].get('tab_status', 'Status'))
                self.tab_widget.setTabText(1, translations[self.current_language].get('tab_rules', 'Rules'))
                self.tab_widget.setTabText(2, translations[self.current_language].get('tab_logs', 'Logs'))
                self.tab_widget.setTabText(3, translations[self.current_language].get('tab_qr', 'QR'))
                self.tab_widget.setTabText(4, translations[self.current_language].get('tab_config', 'Config'))

                # Update table headers if table exists
                if hasattr(self, 'rules_table') and self.rules_table is not None:
                    headers = [
                        translations[self.current_language].get('rule_name', 'Rule Name'),
                        translations[self.current_language].get('protocol', 'Protocol'),
                        translations[self.current_language].get('port', 'Port'),
                        translations[self.current_language].get('direction', 'Direction'),
                        translations[self.current_language].get('action', 'Action'),
                        translations[self.current_language].get('description', 'Description'),
                        translations[self.current_language].get('enabled', 'Enabled')
                    ]
                    self.rules_table.setHorizontalHeaderLabels(headers)

                # Update other UI elements
                if hasattr(self, 'update_ui_texts'):
                    self.update_ui_texts()
                    
            return True
            
        except Exception as e:
            self.logger.log_error(f"Failed to change language to {language}: {str(e)}")
            return False

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
    """Dialog for adding/editing firewall rules with advanced options"""
    
    def __init__(self, parent, translations, rule=None):
        super().__init__(parent)
        self.translations = translations
        self.rule = rule or {}
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the rule dialog UI with advanced options"""
        self.setWindowTitle(self.translations.get('add_rule', 'Add Firewall Rule'))
        layout = QVBoxLayout(self)
        
        # Create tab widget for different sections
        tabs = QTabWidget()
        
        # Basic tab
        basic_tab = QWidget()
        basic_layout = QFormLayout(basic_tab)
        
        # Rule name
        self.name_edit = QLineEdit(self.rule.get('name', ''))
        basic_layout.addRow(self.translations.get('name', 'Name:'), self.name_edit)
        
        # Enabled checkbox
        self.enabled_check = QCheckBox(self.translations.get('enabled', 'Enabled'))
        self.enabled_check.setChecked(self.rule.get('enabled', True))
        basic_layout.addRow('', self.enabled_check)
        
        # Action
        self.action_combo = QComboBox()
        self.action_combo.addItems(['accept', 'drop', 'reject', 'log'])
        if 'action' in self.rule:
            index = self.action_combo.findText(self.rule['action'])
            if index >= 0:
                self.action_combo.setCurrentIndex(index)
        basic_layout.addRow(self.translations.get('action', 'Action:'), self.action_combo)
        
        # Direction
        self.direction_combo = QComboBox()
        self.direction_combo.addItems(['in', 'out', 'both'])
        if 'direction' in self.rule:
            index = self.direction_combo.findText(self.rule['direction'])
            if index >= 0:
                self.direction_combo.setCurrentIndex(index)
        basic_layout.addRow(self.translations.get('direction', 'Direction:'), self.direction_combo)
        
        # Protocol tab
        protocol_tab = QWidget()
        protocol_layout = QFormLayout(protocol_tab)
        
        # Protocol selection
        self.protocol_combo = QComboBox()
        self.protocol_combo.addItems(['tcp', 'udp', 'icmp', 'icmpv6', 'any'])
        if 'protocol' in self.rule:
            index = self.protocol_combo.findText(self.rule['protocol'])
            if index >= 0:
                self.protocol_combo.setCurrentIndex(index)
        protocol_layout.addRow(self.translations.get('protocol', 'Protocol:'), self.protocol_combo)
        
        # Source address
        self.source_ip = QLineEdit(self.rule.get('source_ip', ''))
        protocol_layout.addRow(self.translations.get('source_ip', 'Source IP:'), self.source_ip)
        
        # Source port
        self.source_port = QLineEdit(str(self.rule.get('source_port', '')))
        protocol_layout.addRow(self.translations.get('source_port', 'Source Port:'), self.source_port)
        
        # Destination address
        self.dest_ip = QLineEdit(self.rule.get('dest_ip', ''))
        protocol_layout.addRow(self.translations.get('dest_ip', 'Destination IP:'), self.dest_ip)
        
        # Destination port
        self.dest_port = QLineEdit(str(self.rule.get('dest_port', '')))
        protocol_layout.addRow(self.translations.get('dest_port', 'Destination Port:'), self.dest_port)
        
        # Interface tab
        interface_tab = QWidget()
        interface_layout = QFormLayout(interface_tab)
        
        # Incoming interface
        self.in_interface = QLineEdit(self.rule.get('in_interface', ''))
        interface_layout.addRow(self.translations.get('in_interface', 'Incoming Interface:'), self.in_interface)
        
        # Outgoing interface
        self.out_interface = QLineEdit(self.rule.get('out_interface', ''))
        interface_layout.addRow(self.translations.get('out_interface', 'Outgoing Interface:'), self.out_interface)
        
        # Advanced tab
        advanced_tab = QWidget()
        advanced_layout = QFormLayout(advanced_tab)
        
        # Logging
        self.log_check = QCheckBox(self.translations.get('log', 'Log this rule'))
        self.log_check.setChecked(self.rule.get('log', False))
        advanced_layout.addRow('', self.log_check)
        
        # Log prefix
        self.log_prefix = QLineEdit(self.rule.get('log_prefix', 'FIREWALL'))
        advanced_layout.addRow(self.translations.get('log_prefix', 'Log Prefix:'), self.log_prefix)
        
        # Time constraints
        self.time_start = QLineEdit(self.rule.get('time_start', ''))
        advanced_layout.addRow(self.translations.get('time_start', 'Active from (HH:MM):'), self.time_start)
        
        self.time_end = QLineEdit(self.rule.get('time_end', ''))
        advanced_layout.addRow(self.translations.get('time_end', 'Active until (HH:MM):'), self.time_end)
        
        # Days of week
        self.days_of_week = QLineEdit(self.rule.get('days_of_week', 'Mon,Tue,Wed,Thu,Fri,Sat,Sun'))
        advanced_layout.addRow(self.translations.get('days_of_week', 'Active on days:'), self.days_of_week)
        
        # Description
        self.desc_edit = QTextEdit(self.rule.get('description', ''))
        self.desc_edit.setMaximumHeight(100)
        advanced_layout.addRow(self.translations.get('description', 'Description:'), self.desc_edit)
        
        # Add tabs to the tab widget
        tabs.addTab(basic_tab, self.translations.get('basic', 'Basic'))
        tabs.addTab(protocol_tab, self.translations.get('protocol', 'Protocol'))
        tabs.addTab(interface_tab, self.translations.get('interface', 'Interface'))
        tabs.addTab(advanced_tab, self.translations.get('advanced', 'Advanced'))
        
        layout.addWidget(tabs)
        
        # Buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel,
            Qt.Orientation.Horizontal, self
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
    
    def get_rule(self):
        """Get the rule data from the dialog"""
        return {
            'id': self.rule.get('id', str(uuid.uuid4())),
            'name': self.name_edit.text(),
            'enabled': self.enabled_check.isChecked(),
            'action': self.action_combo.currentText(),
            'direction': self.direction_combo.currentText(),
            'protocol': self.protocol_combo.currentText(),
            'source_ip': self.source_ip.text(),
            'source_port': self.source_port.text(),
            'dest_ip': self.dest_ip.text(),
            'dest_port': self.dest_port.text(),
            'in_interface': self.in_interface.text(),
            'out_interface': self.out_interface.text(),
            'log': self.log_check.isChecked(),
            'log_prefix': self.log_prefix.text(),
            'time_start': self.time_start.text(),
            'time_end': self.time_end.text(),
            'days_of_week': self.days_of_week.text(),
            'description': self.desc_edit.toPlainText(),
            'created_at': self.rule.get('created_at', datetime.now().isoformat()),
            'updated_at': datetime.now().isoformat()
        }


class FirewallSignals(QObject):
    """Signals for the FirewallManager to communicate with the UI"""
    network_stats_updated = Signal(dict)  # Network statistics
    connection_detected = Signal(dict)    # New connection detected
    intrusion_detected = Signal(dict)     # Potential intrusion detected
    vpn_status_changed = Signal(dict)     # VPN connection status changed
    vpn_log_line = Signal(str)            # VPN log line appended
    

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
        self._config = FirewallConfig(config_path, self.translations)
        
        # Set current language from config or default to 'en'
        self.current_language = self._config.current_language
        
        # Initialize rules cache and load rules
        self._rules = []
        self._load_rules()
        
        # Initialize nftables manager
        self.nft = None
        self._init_nftables()
        
        # Initialize network monitoring
        self.network_monitor = NetworkMonitor(update_interval=2.0)
        self.ids = IntrusionDetectionSystem()
        
        # Initialize zone and VPN management
        self.zone_manager = ZoneManager()
        self.vpn_manager = VPNManager(self.zone_manager)
        
        # Initialize enhanced security
        self.security = EnhancedSecurity()
        
        # Windows Firewall controller for kill switch / split tunneling
        try:
            self.winfw = WindowsFirewallController()
        except Exception:
            self.winfw = None
        
        # Setup signals for UI updates
        self.signals = FirewallSignals()
        
        # Start network monitoring
        self._setup_network_monitoring()
        # Apply any saved split tunneling policies
        try:
            self._apply_saved_split_tunneling()
        except Exception as e:
            self.logger.error(f"Failed to apply saved split tunneling: {e}")
        
        self.logger.log_firewall_event("MANAGER_INIT", "Firewall manager initialized")

    def _setup_network_monitoring(self):
        """Start network monitoring and wire callbacks to Qt signals and IDS."""
        try:
            self._last_stats = {}

            def _on_update(stats_dict, connections_list):
                # Prepare stats payload
                try:
                    payload = {"interfaces": {}}
                    for iface, st in stats_dict.items():
                        payload["interfaces"][iface] = {
                            "bytes_sent": getattr(st, "bytes_sent", 0),
                            "bytes_recv": getattr(st, "bytes_recv", 0),
                            "packets_sent": getattr(st, "packets_sent", 0),
                            "packets_recv": getattr(st, "packets_recv", 0),
                            "errors_in": getattr(st, "errors_in", 0),
                            "errors_out": getattr(st, "errors_out", 0),
                            "drop_in": getattr(st, "drop_in", 0),
                            "drop_out": getattr(st, "drop_out", 0),
                            "connections": 0,
                        }

                    # Emit updated stats
                    if hasattr(self, 'signals'):
                        self.signals.network_stats_updated.emit(payload)

                    # Process connections: emit to UI and run IDS checks
                    for conn in connections_list:
                        conn_dict = {
                            "protocol": getattr(conn, "protocol", ""),
                            "local_addr": getattr(conn, "local_addr", ""),
                            "remote_addr": getattr(conn, "remote_addr", ""),
                            "status": getattr(conn, "status", ""),
                            "process_name": getattr(conn, "process_name", ""),
                            "pid": getattr(conn, "pid", 0),
                        }
                        if hasattr(self, 'signals'):
                            self.signals.connection_detected.emit(conn_dict)

                        # IDS analysis
                        try:
                            threats = self.ids.analyze_connection(conn)
                            for t in threats:
                                alert = {
                                    "timestamp": datetime.now().isoformat(),
                                    "severity": t.get("severity", "info"),
                                    "description": t.get("description", ""),
                                    "connection": {
                                        "remote_addr": getattr(conn, "remote_addr", ""),
                                        "local_addr": getattr(conn, "local_addr", ""),
                                    },
                                }
                                if hasattr(self, 'signals'):
                                    self.signals.intrusion_detected.emit(alert)
                        except Exception as ids_err:
                            self.logger.error(f"IDS analysis error: {ids_err}")

                except Exception as cb_err:
                    self.logger.error(f"Network monitor callback error: {cb_err}")

            self.network_monitor.register_callback(_on_update)
            self.network_monitor.start()
            self.logger.info("Network monitoring initialized")

            # Hook VPN status back into UI
            try:
                if hasattr(self.vpn_manager, 'register_status_callback'):
                    self.vpn_manager.register_status_callback(self._on_vpn_status_update)
                if hasattr(self.vpn_manager, 'register_log_callback'):
                    self.vpn_manager.register_log_callback(self._on_vpn_log)
            except Exception as e:
                self.logger.error(f"Failed to register VPN status callback: {e}")
        except Exception as e:
            self.logger.error(f"Failed to set up network monitoring: {e}")

    # ----- Public helpers used by MonitoringTab -----
    def get_network_connections(self) -> List[Dict[str, Any]]:
        """Return current network connections as list of dicts for the UI."""
        try:
            conns = []
            for c in self.network_monitor.get_current_connections():
                conns.append({
                    "protocol": getattr(c, "protocol", ""),
                    "local_addr": getattr(c, "local_addr", ""),
                    "remote_addr": getattr(c, "remote_addr", ""),
                    "status": getattr(c, "status", ""),
                    "process_name": getattr(c, "process_name", ""),
                    "pid": getattr(c, "pid", 0),
                })
            return conns
        except Exception as e:
            self.logger.error(f"Error fetching network connections: {e}")
            return []

    # ----- VPN control helpers -----
    def _on_vpn_status_update(self, status: dict):
        try:
            if hasattr(self, 'signals'):
                self.signals.vpn_status_changed.emit(status)
        except Exception as e:
            self.logger.error(f"Error emitting VPN status: {e}")

    def _on_vpn_log(self, payload: dict):
        # payload: {"name": <vpn_name>, "line": <text>}
        try:
            line = payload.get("line") if isinstance(payload, dict) else str(payload)
            if line is None:
                return
            if hasattr(self, 'signals'):
                self.signals.vpn_log_line.emit(line.rstrip())
        except Exception as e:
            self.logger.error(f"Error emitting VPN log: {e}")

    def connect_vpn(self, name: str) -> bool:
        try:
            return self.vpn_manager.connect_vpn(name)
        except Exception as e:
            self.logger.error(f"Connect VPN failed for {name}: {e}")
            return False

    def disconnect_vpn(self, name: str) -> bool:
        try:
            return self.vpn_manager.disconnect_vpn(name)
        except Exception as e:
            self.logger.error(f"Disconnect VPN failed for {name}: {e}")
            return False

    def set_kill_switch(self, name: str, enabled: bool) -> bool:
        try:
            if enabled:
                ok = self.vpn_manager.enable_kill_switch(name)
                if ok and self.winfw:
                    self.winfw.enable_kill_switch()
                return ok
            else:
                ok = self.vpn_manager.disable_kill_switch(name)
                if ok and self.winfw:
                    self.winfw.disable_kill_switch()
                return ok
        except Exception as e:
            self.logger.error(f"Set kill switch failed for {name}: {e}")
            return False

    def set_split_tunneling(self, name: str, mode: str, routes: list[str]) -> bool:
        try:
            ok = self.vpn_manager.set_split_tunneling(name, mode, routes)
            if ok and self.winfw:
                # Apply Windows firewall rules
                if routes:
                    if mode.lower() == 'exclude':
                        self.winfw.apply_split_tunneling_exclude(routes)
                    else:
                        self.winfw.apply_split_tunneling_include(routes)
                else:
                    self.winfw.clear_split_tunneling()
            return ok
        except Exception as e:
            self.logger.error(f"Set split tunneling failed for {name}: {e}")
            return False

    def get_split_tunneling(self, name: str) -> dict:
        try:
            return self.vpn_manager.get_split_tunneling(name)
        except Exception:
            return {"mode": "exclude", "routes": []}

    def get_vpn_list(self) -> List[str]:
        try:
            return list(self.vpn_manager.vpn_clients.keys())
        except Exception:
            return []

    def get_vpn_status(self, name: str | None = None) -> dict:
        try:
            return self.vpn_manager.get_vpn_status(name) if hasattr(self.vpn_manager, 'get_vpn_status') else {}
        except Exception:
            return {}

    def _apply_saved_split_tunneling(self):
        # Iterate all VPNs and apply split tunneling state (Windows FW rules and routes)
        try:
            names = self.get_vpn_list()
            for name in names:
                cfg = self.get_split_tunneling(name)
                mode = (cfg.get('mode') or 'exclude').lower()
                routes = cfg.get('routes') or []
                if routes:
                    self.set_split_tunneling(name, mode, routes)
        except Exception as e:
            self.logger.error(f"Error in applying saved split tunneling: {e}")
    
    def _load_rules(self):
        """Load rules from the configuration"""
        try:
            rules = self._config.get_rules() if hasattr(self._config, 'get_rules') else []
            if isinstance(rules, list):
                self._rules = rules
                self.logger.info(f"Loaded {len(self._rules)} rules from configuration")
        except Exception as e:
            self.logger.error(f"Error loading rules: {str(e)}")
    
    def _init_nftables(self):
        """Initialize the nftables manager."""
        try:
            self.nft = NFTablesManager()
            self.logger.info("NFTables manager initialized")
        except Exception as e:
            self.logger.log_error(f"Unexpected error initializing nftables: {e}")
            return False

    def block_ip(self, ip: str, duration: int = 3600) -> bool:
        try:
            self.security.block_ip(ip, duration)
            return True
        except Exception:
            return False

    def unblock_ip(self, ip: str) -> bool:
        try:
            self.security.unblock_ip(ip)
            return True
        except Exception:
            return False

    def block_country(self, country_code: str) -> bool:
        try:
            self.security.geo_blocker.block_country(country_code.upper())
            return True
        except Exception:
            return False

    def unblock_country(self, country_code: str) -> bool:
        try:
            self.security.geo_blocker.unblock_country(country_code.upper())
            return True
        except Exception:
            return False

    def get_blocked_countries(self) -> List[str]:
        try:
            return sorted(list(self.security.geo_blocker.blocked_countries))
        except Exception:
            return []

    def get_blocked_ips(self) -> Dict[str, float]:
        try:
            return dict(self.security.blocked_ips)
        except Exception:
            return {}
            
    def export_rules(self, file_path: str) -> bool:
        """
        Export the current firewall rules to a JSON file.
        
        Args:
            file_path: Path to save the exported rules
            
        Returns:
            bool: True if export was successful, False otherwise
        """
        try:
            rules = self.get_rules()
            with open(file_path, 'w') as f:
                json.dump({
                    'version': '1.0',
                    'export_date': datetime.now().isoformat(),
                    'rules': rules
                }, f, indent=2, ensure_ascii=False)
            self.logger.info(f"Exported {len(rules)} rules to {file_path}")
            return True
        except Exception as e:
            self.logger.error(f"Error exporting rules: {str(e)}")
            return False
    
    def import_rules(self, file_path: str, merge: bool = False) -> bool:
        """
        Import firewall rules from a JSON file.
        
        Args:
            file_path: Path to the file containing rules to import
            merge: If True, merge with existing rules. If False, replace all rules.
            
        Returns:
            bool: True if import was successful, False otherwise
        """
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
                
            if not isinstance(data, dict) or 'rules' not in data:
                self.logger.error("Invalid rules file format")
                return False
                
            rules = data['rules']
            if not isinstance(rules, list):
                self.logger.error("Rules data is not a list")
                return False
                
            if not merge:
                # Clear existing rules
                self._rules = []
                
            # Add new rules
            success_count = 0
            for rule in rules:
                if 'id' not in rule:
                    rule['id'] = str(uuid.uuid4())
                    
                # Add timestamps
                now = datetime.now().isoformat()
                rule['created_at'] = rule.get('created_at', now)
                rule['updated_at'] = now
                
                # Set default values for new fields if not present
                rule.setdefault('enabled', True)
                rule.setdefault('source_port', '')
                rule.setdefault('ip_version', 'any')
                rule.setdefault('state', '')
                rule.setdefault('logging', False)
                rule.setdefault('log_level', 'info')
                rule.setdefault('log_prefix', '')
                
                # Add to the rules list
                self._rules.append(rule)
                
                # Save to config if not skipping
                if not merge:
                    self._save_rules()
                
                # Apply the rule to the firewall if enabled
                if self.nft and rule.get('enabled', True):
                    nft_rule = self._convert_rule_to_nftables(rule)
                    if nft_rule:  # Only add if conversion was successful
                        self.nft.add_rule(nft_rule)
                
                self.logger.info(f"Added rule: {rule.get('name', 'Unnamed')} (ID: {rule['id']})")
                success_count += 1
                
            # Save all rules
            if merge:
                self._save_rules()
            
            self.logger.info(f"Imported {success_count}/{len(rules)} rules from {file_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error importing rules: {str(e)}")
            return False
    
    def _show_error(self, title: str, message: str):
        """Show an error message dialog."""
        try:
            # Try to use Qt to show the error if we're in a GUI context
            app = QCoreApplication.instance()
            if app is not None:
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Critical)
                msg.setWindowTitle(title)
                msg.setText(message)
                msg.exec()
            else:
                # Fallback to console output
                print(f"ERROR: {title}\n{message}")
        except Exception as e:
            self.logger.log_error(f"Error showing error dialog: {e}")
            print(f"ERROR: {title}\n{message}")
    
    @property
    def config(self):
        """Get the FirewallConfig instance"""
        return self._config
    
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
    
    def _convert_rule_to_nftables(self, rule: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Convert an internal rule format to nftables format.
        
        Args:
            rule: The rule to convert
            
        Returns:
            dict: The rule in nftables format, or None if conversion fails
        """
        try:
            action = rule.get('action')
            if action == 'allow':
                nft_action = 'accept'
            elif action == 'block':
                nft_action = 'drop'
            elif action == 'reject':
                nft_action = 'reject with icmp type host-prohibited'
            else:
                self.logger.warning(f"Unknown action: {action}")
                return None
                
            # Determine IP version
            ip_version = rule.get('ip_version', 'any')
            if ip_version == 'ip6':
                family = 'ip6'
            elif ip_version == 'ip':
                family = 'ip'
            else:  # 'any' or unspecified
                family = 'ip'  # Default to IPv4 for now
                
            # Determine chain based on direction
            direction = rule.get('direction', 'in')
            if direction == 'in':
                chain = 'INPUT'
                iface_key = 'iifname'
            elif direction == 'out':
                chain = 'OUTPUT'
                iface_key = 'oifname'
            else:  # 'both'
                # For 'both', we'll create two separate rules
                rule1 = rule.copy()
                rule1['direction'] = 'in'
                rule2 = rule.copy()
                rule2['direction'] = 'out'
                
                # Return a list of both rules
                return [
                    self._convert_rule_to_nftables(rule1),
                    self._convert_rule_to_nftables(rule2)
                ]
            
            nft_rule = {
                'action': nft_action,
                'family': family,
                'table': 'filter',
                'chain': chain,
            }
            
            # Add protocol match
            protocol = rule.get('protocol')
            if protocol and protocol != 'all':
                nft_rule['meta'] = {'l4proto': protocol}
            
            # Add port match (destination port)
            port = str(rule.get('port', '')).strip()
            if port:
                if '-' in port:
                    # Port range
                    start_port, end_port = port.split('-', 1)
                    nft_rule['dport'] = {'>=': int(start_port), '<=': int(end_port)}
                elif ',' in port:
                    # Multiple ports
                    nft_rule['dport'] = [int(p.strip()) for p in port.split(',') if p.strip().isdigit()]
                elif port.isdigit():
                    # Single port
                    nft_rule['dport'] = int(port)
            
            # Add source port match
            source_port = str(rule.get('source_port', '')).strip()
            if source_port:
                if '-' in source_port:
                    # Port range
                    start_port, end_port = source_port.split('-', 1)
                    nft_rule['sport'] = {'>=': int(start_port), '<=': int(end_port)}
                elif ',' in source_port:
                    # Multiple ports
                    nft_rule['sport'] = [int(p.strip()) for p in source_port.split(',') if p.strip().isdigit()]
                elif source_port.isdigit():
                    # Single port
                    nft_rule['sport'] = int(source_port)
            
            # Add source IP match
            source_ip = rule.get('source_ip', '').strip()
            if source_ip and source_ip.lower() not in ('', 'any'):
                nft_rule['saddr'] = source_ip
                
            # Add destination IP match
            dest_ip = rule.get('destination_ip', '').strip()
            if dest_ip and dest_ip.lower() not in ('', 'any'):
                nft_rule['daddr'] = dest_ip
                
            # Add interface match
            interface = rule.get('interface', '').strip()
            if interface:
                nft_rule[iface_key] = interface
            
            # Add connection state match
            state = rule.get('state', '').strip()
            if state:
                nft_rule['ct'] = {'state': state}
            
            # Add logging if enabled
            if rule.get('logging'):
                log_prefix = rule.get('log_prefix', 'RULE')
                nft_rule['log'] = {
                    'prefix': f"{log_prefix} {rule.get('name', 'Unnamed')}",
                    'level': rule.get('log_level', 'info')
                }
            
            return nft_rule
            
        except Exception as e:
            self.logger.error(f"Error converting rule to nftables format: {str(e)}")
            return None
    
    def _create_default_nftables_config(self) -> Dict:
        """Create a default nftables configuration."""
        return {
            'nftables': [
                # Flush existing rules
                {'flush': {'ruleset': None}},
                
                # Define tables
                {'add': {'table': {'family': 'ip', 'name': 'filter'}}},
                
                # Define chains
                {'add': {'chain': {
                    'family': 'ip',
                    'table': 'filter',
                    'name': 'INPUT',
                    'type': 'filter',
                    'hook': 'input',
                    'prio': 0,
                    'policy': 'drop'
                }}},
                
                # Default allow localhost
                {'add': {'rule': {
                    'family': 'ip',
                    'table': 'filter',
                    'chain': 'INPUT',
                    'expr': [
                        {'ct': {'state': 'related,established'}},
                        {'accept': None}
                    ]
                }}},
                {'add': {'rule': {
                    'family': 'ip',
                    'table': 'filter',
                    'chain': 'INPUT',
                    'expr': [
                        {'iifname': 'lo'},
                        {'accept': None}
                    ]
                }}},
                
                # Default allow ICMP
                {'add': {'rule': {
                    'family': 'ip',
                    'table': 'filter',
                    'chain': 'INPUT',
                    'expr': [
                        {'protocol': 'icmp'},
                        {'accept': None}
                    ]
                }}}
            ]
        }
    
    def apply_rules(self) -> bool:
        """
        Apply the current firewall rules to the system using nftables.
        
        Returns:
            bool: True if the operation was successful, False otherwise
        """
        if not self.nft:
            self.logger.log_error("Cannot apply rules: nftables not initialized")
            return False
            
        try:
            # Get current rules from config
            rules = self.get_rules()
            
            # Create a new ruleset
            ruleset = self._create_default_nftables_config()
            
            # Add user-defined rules
            for rule in rules:
                try:
                    nft_rule = self._convert_rule_to_nftables(rule)
                    ruleset['nftables'].append({
                        'add': {
                            'rule': {
                                'family': 'ip',
                                'table': nft_rule['table'],
                                'chain': nft_rule['chain'],
                                'expr': nft_rule['expr']
                            }
                        }
                    })
                except Exception as e:
                    self.logger.log_error(f"Error converting rule {rule.get('id')} to nftables: {e}")
            
            # Apply the ruleset
            success = self.nft.apply_ruleset(ruleset)
            
            if success:
                self.logger.log_firewall_event(
                    "RULES_APPLIED", 
                    f"Successfully applied {len(rules)} nftables rules"
                )
            else:
                self.logger.log_error("Failed to apply nftables ruleset")
                
            return success
            
        except Exception as e:
            self.logger.log_error(f"Error applying nftables rules: {e}")
            import traceback
            self.logger.log_error(f"Traceback: {traceback.format_exc()}")
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
                
            # Get the current settings
            settings = self.get_settings()
            
            # Update the language in settings
            settings['language'] = language
            
            # Update the settings in the config
            if hasattr(self, '_config') and hasattr(self._config, 'update_settings'):
                success = self._config.update_settings(settings)
            else:
                # Fallback to direct config update if _config is not available
                if not hasattr(self, 'config'):
                    self.config = {}
                if 'settings' not in self.config:
                    self.config['settings'] = {}
                self.config['settings'].update(settings)
                success = True
                
            if not success:
                self.logger.log_error(f"Failed to update language setting: {language}")
                return False
                
            # Update current language
            self.current_language = language
                
            # Log the language change
            self.logger.log_firewall_event(
                "LANGUAGE_CHANGED", 
                f"Changed language to {language}"
            )
            return True
            
        except Exception as e:
            self.logger.log_error(f"Error changing language: {e}")
            import traceback
            self.logger.log_error(f"Traceback: {traceback.format_exc()}")
            return False
    
    def get_rules(self):
        """
        Get the current firewall rules
        
        Returns:
            list: List of firewall rules
        """
        try:
            # Ensure _config is a FirewallConfig instance
            if not hasattr(self, '_config') or not hasattr(self._config, 'get_rules'):
                self.logger.log_error("Invalid or missing _config in FirewallManager")
                return []
                
            # Use the FirewallConfig's get_rules method
            rules = self._config.get_rules()
            
            # Ensure we always return a list
            if not isinstance(rules, list):
                self.logger.log_error("Rules is not a list, initializing empty rules list")
                rules = []
                
            return rules
            
        except Exception as e:
            self.logger.log_error(f"Error in FirewallManager.get_rules: {str(e)}")
            import traceback
            self.logger.log_error(f"Traceback: {traceback.format_exc()}")
            return []
    
    def add_rule(self, rule, skip_save=False):
        """
        Add a new firewall rule
        
        Args:
            rule (dict): The rule to add
            skip_save (bool): If True, don't save the rules to disk (used during import)
            
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
