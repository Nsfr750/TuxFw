#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import re
import json
import csv
from datetime import datetime
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QPushButton,
    QLabel, QComboBox, QFileDialog, QMessageBox, QSplitter, QFrame,
    QLineEdit, QCheckBox, QToolButton, QSizePolicy, QMenu, QGroupBox, QStyle
)
from PySide6.QtCore import Qt, QTimer, QRegularExpression, QSize
from PySide6.QtGui import QFont, QTextCharFormat, QColor, QTextCursor, QAction, QIcon
from firewall.lang.translations import translations

class ViewLogsWindow(QWidget):
    """Enhanced log viewer with search, filtering, and dark theme support"""

    def __init__(self, parent, current_language, logger):
        super().__init__(parent)
        self.current_language = current_language
        self.logger = logger
        self.log_files = []
        self.current_log_file = None
        self.auto_refresh = False
        self.auto_refresh_interval = 5000  # 5 seconds
        self.search_matches = []
        self.current_match = -1
        self._original_log_content = ""
        
        # Initialize highlight formats for log levels
        self.highlight_formats = {
            'DEBUG': self.create_text_format('#888888'),
            'INFO': self.create_text_format('#4CAF50'),
            'WARNING': self.create_text_format('#FFC107'),
            'ERROR': self.create_text_format('#F44336', bold=True),
            'CRITICAL': self.create_text_format('#FF4081', bold=True),
            'SEARCH': self.create_text_format('#000000', '#FFFF00')
        }

        self.setWindowTitle(f"{translations[self.current_language].get('logs', 'Logs')} - TuxFw")
        self.setMinimumSize(1000, 700)
        self.setWindowFlags(Qt.WindowType.Window)
        
        # Initialize UI
        self.init_ui()
        self.setup_styles()
        
        # Set up auto-refresh timer
        self.refresh_timer = QTimer(self)
        self.refresh_timer.timeout.connect(self.load_selected_log)
        
        # Load initial log files
        self.load_log_files()

    def setup_styles(self):
        """Set up the dark theme styles with improved contrast and readability"""
        self.setStyleSheet("""
            QWidget {
                background-color: #2b2b2b;
                color: #e0e0e0;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QTextEdit, QLineEdit, QComboBox {
                background-color: #1e1e1e;
                border: 1px solid #3e3e3e;
                border-radius: 4px;
                padding: 5px;
                color: #e0e0e0;
            }
            QPushButton, QToolButton {
                background-color: #3a3a3a;
                border: 1px solid #4a4a4a;
                border-radius: 4px;
                padding: 5px 10px;
                min-width: 80px;
            }
            QPushButton:hover, QToolButton:hover {
                background-color: #4a4a4a;
            }
            QPushButton:pressed, QToolButton:pressed {
                background-color: #2a2a2a;
            }
            QLabel {
                color: #e0e0e0;
            }
            QGroupBox {
                border: 1px solid #3e3e3e;
                border-radius: 4px;
                margin-top: 10px;
                padding-top: 15px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)

    def create_text_format(self, fg_color, bg_color='transparent', bold=False):
        """Create a text format with the given colors and style"""
        fmt = QTextCharFormat()
        fmt.setForeground(QColor(fg_color))
        if bg_color != 'transparent':
            fmt.setBackground(QColor(bg_color))
        if bold:
            fmt.setFontWeight(QFont.Weight.Bold)
        return fmt

    def init_ui(self):
        """Initialize the UI components"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(8, 8, 8, 8)
        main_layout.setSpacing(8)

        # Top controls
        controls_layout = QHBoxLayout()
        
        # Log file selection
        file_group = QGroupBox(translations[self.current_language].get('log_file', 'Log File'))
        file_layout = QHBoxLayout()
        
        self.log_combo = QComboBox()
        self.log_combo.setMinimumWidth(300)
        self.log_combo.currentIndexChanged.connect(self.on_log_file_changed)
        
        refresh_btn = QToolButton()
        refresh_btn.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_BrowserReload))
        refresh_btn.setToolTip(translations[self.current_language].get('refresh', 'Refresh'))
        refresh_btn.clicked.connect(self.load_log_files)
        
        file_layout.addWidget(QLabel(translations[self.current_language].get('select_log', 'Log File:')), 0)
        file_layout.addWidget(self.log_combo, 1)
        file_layout.addWidget(refresh_btn, 0)
        file_group.setLayout(file_layout)
        
        # Log level filter
        level_group = QGroupBox(translations[self.current_language].get('log_level', 'Log Level'))
        level_layout = QHBoxLayout()
        
        self.level_combo = QComboBox()
        self.level_combo.addItem("All Levels", "ALL")
        self.level_combo.addItem("Debug+", "DEBUG")
        self.level_combo.addItem("Info+", "INFO")
        self.level_combo.addItem("Warning+", "WARNING")
        self.level_combo.addItem("Error+", "ERROR")
        self.level_combo.addItem("Critical", "CRITICAL")
        self.level_combo.currentIndexChanged.connect(self.filter_log_levels)
        
        level_layout.addWidget(QLabel(translations[self.current_language].get('filter', 'Filter:')), 0)
        level_layout.addWidget(self.level_combo, 1)
        level_group.setLayout(level_layout)
        
        # Search box
        search_group = QGroupBox(translations[self.current_language].get('search', 'Search'))
        search_layout = QHBoxLayout()
        
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText(translations[self.current_language].get('search_placeholder', 'Search...'))
        self.search_edit.textChanged.connect(self.filter_log_levels)
        
        self.search_prev_btn = QToolButton()
        self.search_prev_btn.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_ArrowUp))
        self.search_prev_btn.setToolTip(translations[self.current_language].get('previous_match', 'Previous match'))
        self.search_prev_btn.clicked.connect(lambda: self.search_text(forward=False))
        
        self.search_next_btn = QToolButton()
        self.search_next_btn.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_ArrowDown))
        self.search_next_btn.setToolTip(translations[self.current_language].get('next_match', 'Next match'))
        self.search_next_btn.clicked.connect(lambda: self.search_text(forward=True))
        
        search_layout.addWidget(self.search_edit, 1)
        search_layout.addWidget(self.search_prev_btn)
        search_layout.addWidget(self.search_next_btn)
        search_group.setLayout(search_layout)
        
        # Auto-refresh controls
        refresh_group = QGroupBox(translations[self.current_language].get('auto_refresh', 'Auto Refresh'))
        refresh_layout = QHBoxLayout()
        
        self.auto_refresh_cb = QCheckBox(translations[self.current_language].get('enable_auto_refresh', 'Enable'))
        self.auto_refresh_cb.stateChanged.connect(self.toggle_auto_refresh)
        
        self.refresh_interval = QComboBox()
        self.refresh_interval.addItems(['1', '2', '5', '10', '30', '60'])
        self.refresh_interval.setCurrentText('5')
        self.refresh_interval.setMaximumWidth(80)
        self.refresh_interval.currentTextChanged.connect(self.update_refresh_interval)
        
        refresh_layout.addWidget(self.auto_refresh_cb)
        refresh_layout.addWidget(QLabel(translations[self.current_language].get('interval_seconds', 'Interval (s):')))
        refresh_layout.addWidget(self.refresh_interval)
        refresh_layout.addStretch()
        refresh_group.setLayout(refresh_layout)
        
        # Add groups to controls layout
        controls_layout.addWidget(file_group, 2)
        controls_layout.addWidget(level_group, 1)
        controls_layout.addWidget(search_group, 2)
        controls_layout.addWidget(refresh_group, 2)
        
        # Log display
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setFont(QFont("Consolas", 10))
        
        # Status bar
        status_bar = QHBoxLayout()
        
        self.status_label = QLabel(translations[self.current_language].get('ready', 'Ready'))
        self.status_label.setStyleSheet("color: #888888;")
        
        self.line_count_label = QLabel("0 lines")
        self.line_count_label.setStyleSheet("color: #888888;")
        self.line_count_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        
        status_bar.addWidget(self.status_label, 1)
        status_bar.addWidget(self.line_count_label)
        
        # Action buttons
        button_layout = QHBoxLayout()
        
        self.clear_btn = QPushButton(translations[self.current_language].get('clear', 'Clear'))
        self.clear_btn.clicked.connect(self.clear_current_log)
        
        self.export_btn = QPushButton(translations[self.current_language].get('export', 'Export...'))
        self.export_btn.clicked.connect(self.export_log)
        
        close_btn = QPushButton(translations[self.current_language].get('close', 'Close'))
        close_btn.clicked.connect(self.close)
        
        button_layout.addStretch()
        button_layout.addWidget(self.clear_btn)
        button_layout.addWidget(self.export_btn)
        button_layout.addWidget(close_btn)
        
        # Add everything to main layout
        main_layout.addLayout(controls_layout)
        main_layout.addWidget(self.log_text, 1)
        main_layout.addLayout(status_bar)
        main_layout.addLayout(button_layout)
        
        # Set initial state
        self.update_ui_state()

    def update_ui_state(self):
        """Update the enabled/disabled state of UI elements"""
        has_log = bool(self.current_log_file and os.path.exists(self.current_log_file))
        self.clear_btn.setEnabled(has_log)
        self.export_btn.setEnabled(has_log)
        self.search_prev_btn.setEnabled(has_log and bool(self.search_matches))
        self.search_next_btn.setEnabled(has_log and bool(self.search_matches))

    def load_log_files(self):
        """Load available log files"""
        try:
            # Save current selection
            current_log = self.log_combo.currentData()
            
            # Clear and repopulate
            self.log_combo.clear()
            self.log_files = []
            
            # Add default log file
            log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'logs')
            default_log = os.path.join(log_dir, 'firewall.log')
            
            if os.path.exists(default_log):
                self.log_files.append(default_log)
                self.log_combo.addItem(os.path.basename(default_log), default_log)
            
            # Add other log files if they exist
            if os.path.exists(log_dir):
                for file in os.listdir(log_dir):
                    if file.endswith('.log') and file != 'firewall.log':
                        log_path = os.path.join(log_dir, file)
                        self.log_files.append(log_path)
                        self.log_combo.addItem(file, log_path)
            
            # Restore selection if possible
            if current_log in self.log_files:
                index = self.log_combo.findData(current_log)
                if index >= 0:
                    self.log_combo.setCurrentIndex(index)
            elif self.log_combo.count() > 0:
                self.log_combo.setCurrentIndex(0)
                
        except Exception as e:
            self.logger.log_error(f"Failed to load log files: {e}", "ViewLogs.load_log_files")
            QMessageBox.critical(self, 
                               translations[self.current_language].get('error', 'Error'),
                               f"Failed to load log files: {str(e)}")

    def load_selected_log(self):
        """Load the selected log file"""
        try:
            current_data = self.log_combo.currentData()
            if not current_data:
                return

            log_file = current_data
            self.current_log_file = log_file
            
            if os.path.exists(log_file):
                # Disable updates while loading for better performance
                self.log_text.setUpdatesEnabled(False)
                
                # Save scroll position
                scroll_bar = self.log_text.verticalScrollBar()
                scroll_pos = scroll_bar.value()
                
                # Save cursor position
                cursor = self.log_text.textCursor()
                cursor_pos = cursor.position()
                
                # Read file content
                with open(log_file, 'r', encoding='utf-8', errors='replace') as f:
                    content = f.read()
                
                # Store original content for filtering
                self._original_log_content = content
                
                # Update display
                self.log_text.setPlainText(content)
                
                # Apply highlighting and filters
                self.highlight_log_levels()
                
                # Restore scroll position
                if scroll_pos <= scroll_bar.maximum():
                    scroll_bar.setValue(scroll_pos)
                
                # Update status
                line_count = len(content.splitlines())
                self.line_count_label.setText(f"{line_count} lines")
                self.status_label.setText(translations[self.current_language].get('log_loaded', 'Log loaded'))
                
                # Log the action
                self.logger.log_firewall_event("LOG_LOADED", f"Loaded log file: {log_file}")
                
            else:
                self.status_label.setText(translations[self.current_language].get('log_not_found', 'Log file not found'))
                
        except Exception as e:
            error_msg = f"Failed to load log file: {str(e)}"
            self.status_label.setText(error_msg)
            self.logger.log_error(error_msg, "ViewLogs.load_selected_log")
            
        finally:
            self.log_text.setUpdatesEnabled(True)
            self.update_ui_state()

    def highlight_log_levels(self):
        """Apply syntax highlighting to log levels"""
        if not hasattr(self, '_original_log_content'):
            return
            
        cursor = self.log_text.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.Start)
        
        # Clear existing formatting
        cursor.select(QTextCursor.SelectionType.Document)
        cursor.setCharFormat(QTextCharFormat())
        
        # Apply highlighting for each log level
        for level, fmt in self.highlight_formats.items():
            if level == 'SEARCH':
                continue  # Skip search highlighting here
                
            pattern = fr"\b{level}\b"
            self.highlight_pattern(pattern, fmt)
        
        # Apply search highlighting if needed
        search_text = self.search_edit.text().strip()
        if search_text:
            self.highlight_pattern(re.escape(search_text), self.highlight_formats['SEARCH'], case_sensitive=False)
        
        # Restore cursor position
        cursor.movePosition(QTextCursor.MoveOperation.Start)
        self.log_text.setTextCursor(cursor)

    def highlight_pattern(self, pattern, fmt, case_sensitive=True):
        """Helper method to highlight text matching a pattern"""
        cursor = self.log_text.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.Start)
        
        regex = QRegularExpression(pattern)
        if not case_sensitive:
            regex.setPatternOptions(QRegularExpression.PatternOption.CaseInsensitiveOption)
        
        # Find all matches
        matches = []
        search_cursor = self.log_text.document().find(regex)
        while not search_cursor.isNull():
            matches.append((search_cursor.selectionStart(), search_cursor.selectionEnd()))
            search_cursor = self.log_text.document().find(regex, search_cursor)
        
        # Apply formatting to all matches
        for start, end in matches:
            cursor.setPosition(start)
            cursor.setPosition(end, QTextCursor.MoveMode.KeepAnchor)
            cursor.mergeCharFormat(fmt)

    def filter_log_levels(self):
        """Filter log messages by log level and search text"""
        if not hasattr(self, '_original_log_content') or not self._original_log_content:
            return
            
        try:
            # Get current filter level
            current_level = self.level_combo.currentData()
            search_text = self.search_edit.text().lower()
            
            # Split content into lines
            lines = self._original_log_content.splitlines()
            filtered_lines = []
            
            # Define log level order for filtering
            level_order = {'DEBUG': 0, 'INFO': 1, 'WARNING': 2, 'ERROR': 3, 'CRITICAL': 4}
            min_level = level_order.get(current_level, 0) if current_level != 'ALL' else -1
            
            # Filter lines
            for line in lines:
                line_upper = line.upper()
                level_match = False
                
                # Check if line contains any log level
                for level in level_order:
                    if level in line_upper:
                        if current_level == 'ALL' or level_order[level] >= min_level:
                            level_match = True
                        break
                
                # If level matches, check search text
                if level_match and (not search_text or search_text in line.lower()):
                    filtered_lines.append(line)
            
            # Update display
            cursor = self.log_text.textCursor()
            scroll_pos = self.log_text.verticalScrollBar().value()
            
            self.log_text.setPlainText('\n'.join(filtered_lines))
            self.highlight_log_levels()
            
            # Restore scroll position if possible
            if scroll_pos <= self.log_text.verticalScrollBar().maximum():
                self.log_text.verticalScrollBar().setValue(scroll_pos)
            
            # Update status
            self.line_count_label.setText(f"{len(filtered_lines)} of {len(lines)} lines")
            
            # Update search matches
            self.search_matches = [i for i, line in enumerate(filtered_lines) if search_text in line.lower()]
            self.current_match = -1
            
            # Update UI
            self.update_ui_state()
            
        except Exception as e:
            self.logger.log_error(f"Error filtering logs: {e}", "ViewLogs.filter_log_levels")

    def search_text(self, forward=True):
        """Search for text in the log"""
        if not hasattr(self, 'search_edit') or not self.search_edit.text():
            return
            
        if not self.search_matches:
            return
            
        # Move to next/previous match
        if forward:
            self.current_match = (self.current_match + 1) % len(self.search_matches)
        else:
            self.current_match = (self.current_match - 1) % len(self.search_matches)
        
        # Highlight the match
        cursor = self.log_text.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.Start)
        
        # Move to the matching line
        line_number = self.search_matches[self.current_match]
        cursor.movePosition(QTextCursor.MoveOperation.Down, QTextCursor.MoveMode.MoveAnchor, line_number)
        
        # Select the line
        cursor.movePosition(QTextCursor.MoveOperation.StartOfLine)
        cursor.movePosition(QTextCursor.MoveOperation.EndOfLine, QTextCursor.MoveMode.KeepAnchor)
        
        # Center the view on the match
        self.log_text.setTextCursor(cursor)
        self.log_text.centerCursor()
        
        # Update status
        self.status_label.setText(f"Match {self.current_match + 1} of {len(self.search_matches)}")

    def toggle_auto_refresh(self, state):
        """Toggle auto-refresh of logs
        
        Args:
            state (int): The state of the checkbox (2 for checked, 0 for unchecked)
        """
        self.auto_refresh = state == Qt.Checked
        self.update_refresh_interval()
        
        if self.auto_refresh:
            self.status_label.setText(f"Auto-refresh enabled ({self.auto_refresh_interval//1000}s)")
        else:
            self.refresh_timer.stop()
            self.status_label.setText("Auto-refresh disabled")
        
        self.logger.log_firewall_event(
            "AUTO_REFRESH_TOGGLED", 
            f"Auto-refresh {'enabled' if self.auto_refresh else 'disabled'} (interval: {self.auto_refresh_interval//1000}s)"
        )
    
    def update_refresh_interval(self):
        """Update the auto-refresh interval based on user selection"""
        try:
            interval_seconds = int(self.refresh_interval.currentText())
            self.auto_refresh_interval = interval_seconds * 1000  # Convert to milliseconds
            
            if self.auto_refresh:
                self.refresh_timer.stop()
                self.refresh_timer.start(self.auto_refresh_interval)
                self.status_label.setText(f"Auto-refresh enabled ({interval_seconds}s)")
                
            self.logger.log_firewall_event(
                "REFRESH_INTERVAL_CHANGED",
                f"Refresh interval set to {interval_seconds} seconds"
            )
        except (ValueError, AttributeError) as e:
            self.logger.log_error(
                f"Failed to update refresh interval: {e}",
                "ViewLogs.update_refresh_interval"
            )

    def clear_current_log(self):
        """Clear the current log file"""
        if not self.current_log_file or not os.path.exists(self.current_log_file):
            return
            
        reply = QMessageBox.question(
            self,
            translations[self.current_language].get('confirm_clear', 'Confirm Clear'),
            translations[self.current_language].get('clear_log_confirm', 'Are you sure you want to clear this log file?'),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                # Clear the file
                with open(self.current_log_file, 'w', encoding='utf-8') as f:
                    f.write('')
                
                # Update the display
                self.log_text.clear()
                self.search_matches = []
                self.current_match = -1
                self._original_log_content = ""
                
                # Update status
                self.status_label.setText(translations[self.current_language].get('log_cleared', 'Log file cleared'))
                self.line_count_label.setText('0 lines')
                
                # Log the action
                self.logger.log_firewall_event("LOG_CLEARED", f"Cleared log file: {self.current_log_file}")
                
            except Exception as e:
                error_msg = f"Failed to clear log file: {str(e)}"
                self.status_label.setText(error_msg)
                self.logger.log_error(error_msg, "ViewLogs.clear_current_log")

    def export_log(self):
        """Export the current log to a file"""
        if not hasattr(self, '_original_log_content') or not self._original_log_content:
            return
            
        try:
            # Get save file name
            file_name, _ = QFileDialog.getSaveFileName(
                self,
                translations[self.current_language].get('export_log', 'Export Log'),
                '',
                "Text Files (*.txt);;All Files (*)"
            )
            
            if file_name:
                # Ensure .txt extension
                if not file_name.lower().endswith('.txt'):
                    file_name += '.txt'
                
                # Write content to file
                with open(file_name, 'w', encoding='utf-8') as f:
                    f.write(self._original_log_content)
                
                # Update status
                self.status_label.setText(f"{translations[self.current_language].get('log_exported', 'Log exported to')}: {file_name}")
                self.logger.log_firewall_event("LOG_EXPORTED", f"Exported log to: {file_name}")
                
        except Exception as e:
            error_msg = f"Failed to export log: {str(e)}"
            self.status_label.setText(error_msg)
            self.logger.log_error(error_msg, "ViewLogs.export_log")

    def closeEvent(self, event):
        """Handle window close event"""
        # Stop the refresh timer
        if hasattr(self, 'refresh_timer') and self.refresh_timer.isActive():
            self.refresh_timer.stop()
        
        # Clean up
        if hasattr(self, 'parent') and hasattr(self.parent, 'view_logs_window'):
            self.parent.view_logs_window = None
        
        event.accept()

    def on_log_file_changed(self, index):
        """Handle log file selection change"""
        if index >= 0:
            self.load_selected_log()
