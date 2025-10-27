#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTextEdit,
                             QPushButton, QGroupBox, QLabel, QComboBox,
                             QFileDialog, QMessageBox, QSplitter, QFrame)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont
from lang.translations import translations


class ViewLogsWindow(QWidget):
    """Window for viewing and managing log files"""

    def __init__(self, parent, current_language, logger):
        super().__init__(parent)
        self.current_language = current_language
        self.logger = logger
        self.log_files = []

        self.setWindowTitle(translations[self.current_language]['logs'] or 'View Logs')
        self.setMinimumSize(800, 600)
        self.setWindowFlags(Qt.WindowType.Window)

        self.init_ui()
        self.load_log_files()

    def init_ui(self):
        """Initialize the UI"""
        layout = QVBoxLayout(self)

        # Controls group
        controls_group = QGroupBox(translations[self.current_language]['logs'] or 'Logs')
        controls_layout = QHBoxLayout()

        # Log file selector
        self.log_combo = QComboBox()
        self.log_combo.currentTextChanged.connect(self.load_selected_log)
        controls_layout.addWidget(QLabel(translations[self.current_language]['select_log'] or 'Select Log:'))
        controls_layout.addWidget(self.log_combo)

        # Buttons
        self.refresh_button = QPushButton(translations[self.current_language]['refresh'] or 'Refresh')
        self.refresh_button.clicked.connect(self.load_log_files)
        controls_layout.addWidget(self.refresh_button)

        self.clear_button = QPushButton(translations[self.current_language]['clear_logs'] or 'Clear Current')
        self.clear_button.clicked.connect(self.clear_current_log)
        controls_layout.addWidget(self.clear_button)

        self.export_button = QPushButton(translations[self.current_language]['export'] or 'Export')
        self.export_button.clicked.connect(self.export_log)
        controls_layout.addWidget(self.export_button)

        controls_layout.addStretch()
        controls_group.setLayout(controls_layout)

        # Log display area
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setFont(QFont("Consolas", 9))
        self.log_text.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)

        # Main layout
        layout.addWidget(controls_group)
        layout.addWidget(self.log_text)

        # Status bar
        self.status_label = QLabel("Ready")
        layout.addWidget(self.status_label)

    def load_log_files(self):
        """Load available log files"""
        try:
            if hasattr(self.logger, 'get_log_files'):
                self.log_files = self.logger.get_log_files()
            else:
                # Fallback: look for log files in logs directory
                import glob
                self.log_files = sorted(glob.glob("logs/*.log"))

            self.log_combo.clear()
            for log_file in self.log_files:
                display_name = os.path.basename(log_file)
                self.log_combo.addItem(display_name, log_file)

            if self.log_files:
                self.status_label.setText(f"Found {len(self.log_files)} log files")
                # Load the most recent log file
                self.log_combo.setCurrentIndex(0)
                self.load_selected_log()
            else:
                self.status_label.setText("No log files found")
                self.log_text.clear()

        except Exception as e:
            self.status_label.setText(f"Error loading log files: {str(e)}")
            self.logger.log_error(f"Failed to load log files: {e}", context="ViewLogs.load_log_files")

    def load_selected_log(self):
        """Load the selected log file"""
        try:
            current_data = self.log_combo.currentData()
            if not current_data:
                return

            log_file = current_data
            if os.path.exists(log_file):
                with open(log_file, 'r', encoding='utf-8') as f:
                    content = f.read()

                self.log_text.setPlainText(content)
                self.status_label.setText(f"Loaded: {os.path.basename(log_file)} ({len(content)} chars)")
            else:
                self.log_text.clear()
                self.status_label.setText("Log file not found")

        except Exception as e:
            self.log_text.clear()
            self.status_label.setText(f"Error loading log: {str(e)}")
            self.logger.log_error(f"Failed to load log file {log_file}: {e}", context="ViewLogs.load_selected_log")

    def clear_current_log(self):
        """Clear the currently selected log file"""
        try:
            current_data = self.log_combo.currentData()
            if not current_data:
                QMessageBox.warning(self, translations[self.current_language]['warning'] or 'Warning',
                                  "No log file selected")
                return

            reply = QMessageBox.question(self, translations[self.current_language]['confirm'] or 'Confirm',
                                       f"Clear the selected log file? This cannot be undone.",
                                       QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

            if reply == QMessageBox.StandardButton.Yes:
                log_file = current_data
                with open(log_file, 'w', encoding='utf-8') as f:
                    f.write("")  # Clear the file

                self.load_selected_log()
                self.status_label.setText("Log file cleared")
                self.logger.log_firewall_event("LOG_CLEARED", f"Log file cleared: {os.path.basename(log_file)}")

        except Exception as e:
            self.status_label.setText(f"Error clearing log: {str(e)}")
            self.logger.log_error(f"Failed to clear log file: {e}", context="ViewLogs.clear_current_log")

    def export_log(self):
        """Export the current log to a file"""
        try:
            current_data = self.log_combo.currentData()
            if not current_data:
                QMessageBox.warning(self, translations[self.current_language]['warning'] or 'Warning',
                                  "No log file selected")
                return

            default_name = os.path.basename(current_data).replace('.log', '_export.txt')
            file_path, _ = QFileDialog.getSaveFileName(self, translations[self.current_language]['export'] or 'Export Log',
                                                     default_name, "Text Files (*.txt);;All Files (*)")

            if file_path:
                content = self.log_text.toPlainText()
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)

                self.status_label.setText(f"Log exported to: {file_path}")
                self.logger.log_firewall_event("LOG_EXPORTED", f"Log exported to: {file_path}")

        except Exception as e:
            self.status_label.setText(f"Error exporting log: {str(e)}")
            self.logger.log_error(f"Failed to export log: {e}", context="ViewLogs.export_log")
