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
        self.find_log_files()
        if self.log_files:
            self.log_combo.setCurrentIndex(0)
            self.load_selected_log()
        
        # Setup auto-refresh timer
        self.refresh_timer = QTimer(self)
        self.refresh_timer.timeout.connect(self.auto_refresh_log)
        
        # Load initial log files
        self.load_log_files()

    def setup_styles(self):
        """Set up the dark theme styles with improved contrast and readability"""
        self.setStyleSheet("""
            /* Base styles */
            QWidget {
                background-color: #1e1e1e;
                color: #f0f0f0;
                font-family: 'Segoe UI', Arial, sans-serif;
                border: none;
            }
            
            /* Text and input fields */
            QTextEdit, QPlainTextEdit, QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox {
                background-color: #252526;
                color: #f0f0f0;
                border: 1px solid #3e3e42;
                border-radius: 3px;
                padding: 5px;
                selection-background-color: #264f78;
                selection-color: #ffffff;
            }
            
            /* Buttons */
            QPushButton {
                background-color: #333333;
                color: #f0f0f0;
                border: 1px solid #3e3e42;
                border-radius: 3px;
                padding: 5px 12px;
                min-width: 80px;
            }
            
            QPushButton:hover {
                background-color: #3e3e42;
                border: 1px solid #505050;
            }
            
            QPushButton:pressed {
                background-color: #2a2a2a;
            }
            
            /* Scroll bars */
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
            
            /* Group boxes */
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
            }
            QTextEdit, QLineEdit, QComboBox, QPushButton, QToolButton {
                background-color: #1e1e1e;
                border: 1px solid #3a3a3a;
                padding: 5px;
                border-radius: 3px;
                color: #e0e0e0;
            }
            QPushButton:hover, QToolButton:hover {
                background-color: #2a2a2a;
                border-color: #4a4a4a;
            }
            QPushButton:pressed, QToolButton:pressed {
                background-color: #1a1a1a;
            }
            QPushButton:disabled, QToolButton:disabled {
                color: #666;
                background-color: #2a2a2a;
            }
            QLineEdit:focus, QComboBox:focus, QPushButton:focus {
                border: 1px solid #0078d7;
            }
            QComboBox::drop-down {
                border: none;
            }
            QStatusBar {
                background-color: #1e1e1e;
                border-top: 1px solid #3a3a3a;
                padding: 2px 5px;
            }
            QProgressBar {
                border: 1px solid #3a3a3a;
                border-radius: 3px;
                text-align: center;
                background: #1e1e1e;
            }
            QProgressBar::chunk {
                background-color: #0078d7;
                width: 10px;
                margin: 0.5px;
            }
        """)
        
        # Define highlight colors for different log levels
        self.highlight_formats = {
            'ERROR': self.create_text_format('#ff6b6b', '#2b2b2b', True),  # Red
            'WARNING': self.create_text_format('#ffcc00', '#2b2b2b', True),  # Yellow
            'INFO': self.create_text_format('#4ec9b0', '#2b2b2b'),  # Teal
            'DEBUG': self.create_text_format('#9cdcfe', '#2b2b2b'),  # Light Blue
            'CRITICAL': self.create_text_format('#ff0000', '#ffffff', True),  # Bright Red
            'SEARCH': self.create_text_format('#000000', '#ffff55', True),  # Yellow highlight for search
        }

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
        top_controls = QHBoxLayout()
        
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
        
        self.level_combo = QComboBox()
        self.level_combo.addItem("All Levels", "ALL")
        self.level_combo.addItem("Debug+", "DEBUG")
        self.level_combo.addItem("Info+", "INFO")
        self.level_combo.addItem("Warning+", "WARNING")
        self.level_combo.addItem("Error+", "ERROR")
        self.level_combo.addItem("Critical", "CRITICAL")
        self.level_combo.currentIndexChanged.connect(self.filter_log_levels)
        
        # Search box
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText(self.translations[self.current_language].get('search', 'Search...'))
        self.search_edit.textChanged.connect(self.filter_log_levels)
        
        # Search buttons
        self.search_prev_btn = QToolButton()
        self.search_prev_btn.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_ArrowUp))
        self.search_prev_btn.setToolTip(self.translations[self.current_language].get('previous_match', 'Previous match'))
        self.search_prev_btn.clicked.connect(lambda: self.search_text(forward=False))
        
        self.search_next_btn = QToolButton()
        self.search_next_btn.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_ArrowDown))
        self.search_next_btn.setToolTip(self.translations[self.current_language].get('next_match', 'Next match'))
        self.search_next_btn.clicked.connect(lambda: self.search_text(forward=True))
        
        # Add controls to layout
        controls_layout.addWidget(QLabel(self.translations[self.current_language].get('log_file', 'Log File:')))
        controls_layout.addWidget(self.log_combo)
        controls_layout.addSpacing(10)
        controls_layout.addWidget(QLabel(self.translations[self.current_language].get('log_level', 'Log Level:')))
        controls_layout.addWidget(self.level_combo)
        controls_layout.addSpacing(10)
        controls_layout.addWidget(QLabel(self.translations[self.current_language].get('search', 'Search:')))
        controls_layout.addWidget(self.search_edit)
        controls_layout.addWidget(self.search_prev_btn)
        controls_layout.addWidget(self.search_next_btn)
        controls_layout.addStretch()
        
        # Auto-refresh toggle
        self.auto_refresh_cb = QCheckBox(self.translations[self.current_language].get('auto_refresh', 'Auto-refresh'))
        self.auto_refresh_cb.stateChanged.connect(self.toggle_auto_refresh)
        controls_layout.addWidget(self.auto_refresh_cb)
        
        # Main log display
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setFont(QFont("Consolas", 10))
        
        # Status bar
        self.status_bar = QHBoxLayout()
        self.status_label = QLabel()
        self.line_count_label = QLabel()
        self.status_bar.addWidget(self.status_label)
        self.status_bar.addStretch()
        self.status_bar.addWidget(self.line_count_label)
        
        # Action buttons
        btn_layout = QHBoxLayout()
        
        self.clear_btn = QPushButton(self.translations[self.current_language].get('clear_logs', 'Clear Log'))
        self.clear_btn.clicked.connect(self.clear_current_log)
        
        self.export_btn = QPushButton(self.translations[self.current_language].get('export', 'Export'))
        
        # Add Close button
        self.close_btn = QPushButton(self.translations[self.current_language].get('close', 'Close'))
        self.close_btn.clicked.connect(self.close)
        
        btn_layout.addWidget(self.clear_btn)
        btn_layout.addWidget(self.export_btn)
        btn_layout.addStretch()
        btn_layout.addWidget(self.close_btn)
        
        # Assemble main layout
        main_layout.addLayout(controls_layout)
        main_layout.addWidget(self.log_text, 1)
        main_layout.addLayout(btn_layout)
        main_layout.addLayout(self.status_bar)
        
        self.setLayout(main_layout)

    def create_text_format(self, fg_color, bg_color='transparent', bold=False):
        """Create a text format with the given colors and style"""
        fmt = QTextCharFormat()
        fmt.setForeground(QColor(fg_color))
        if bg_color != 'transparent':
            fmt.setBackground(QColor(bg_color))
        if bold:
            fmt.setFontWeight(QFont.Weight.Bold)
        return fmt

    def load_log_files(self):
        """Load available log files"""
        try:
            if hasattr(self.logger, 'get_log_files'):
                self.log_files = self.logger.get_log_files()
            else:
                # Fallback: look for log files in logs directory
                import glob
                if not os.path.exists('logs'):
                    os.makedirs('logs')
                self.log_files = sorted(glob.glob("logs/*.log"))
            
            self.log_combo.blockSignals(True)
            self.log_combo.clear()
            
            # Add log files to the combo box
            for log_file in self.log_files:
                display_name = os.path.basename(log_file)
                self.log_combo.addItem(display_name, log_file)
            
            # Select the first log file by default if available
            if self.log_files:
                self.log_combo.setCurrentIndex(0)
                self.current_log_file = self.log_files[0]
                self.load_selected_log()
            else:
                self.status_label.setText("No log files found")
                self.log_text.clear()
                
            self.log_combo.blockSignals(False)
            
        except Exception as e:
            error_msg = f"Error loading log files: {str(e)}"
            self.status_label.setText(error_msg)
            self.logger.log_error(error_msg, "ViewLogs.load_log_files")
            QMessageBox.critical(
                self,
                self.translations[self.current_language].get('error', 'Error'),
                error_msg
            )

    def highlight_log_levels(self):
        """Apply syntax highlighting to log levels"""
        if not hasattr(self, 'log_text') or not hasattr(self, 'highlight_formats'):
            return
            
        cursor = self.log_text.textCursor()
        cursor.beginEditBlock()
        
        try:
            # Clear existing formatting
            cursor.select(QTextCursor.SelectionType.Document)
            cursor.setCharFormat(QTextCharFormat())
            
            # Apply highlighting for each log level
            for level, fmt in self.highlight_formats.items():
                if level == 'SEARCH':
                    continue  # Search highlighting is handled separately
                    
                # Create a regex pattern to match the log level
                pattern = QRegularExpression(f"\\b{re.escape(level)}\\b", 
                                           QRegularExpression.PatternOption.CaseInsensitiveOption)
                
                if not pattern.isValid():
                    continue
                
                # Find and format all matches
                cursor.movePosition(QTextCursor.MoveOperation.Start)
                while True:
                    match = self.log_text.document().find(pattern, cursor)
                    if match.isNull() or match.isNull():
                        break
                    
                    # Apply the format
                    cursor.setPosition(match.selectionStart())
                    cursor.setPosition(match.selectionEnd(), QTextCursor.MoveMode.KeepAnchor)
                    cursor.mergeCharFormat(fmt)
                    
                    # Move to the end of this match
                    cursor.setPosition(match.selectionEnd())
        finally:
            cursor.endEditBlock()

    def filter_log_levels(self):
        """Filter log messages by log level and search text"""
        if not hasattr(self, 'log_text') or not hasattr(self, 'level_combo'):
            return
            
        # Get filter criteria
        current_level = self.level_combo.currentData()
        search_text = self.search_edit.text().lower()
        
        # If no filters are active, show all content
        if current_level == 'ALL' and not search_text:
            self.log_text.setPlainText(self._original_log_content)
            self.highlight_log_levels()
            self.update_status()
            return
            
        # Get the original content if we don't have it
        if not hasattr(self, '_original_log_content'):
            self._original_log_content = self.log_text.toPlainText()
            
        if not self._original_log_content:
            return
            
        # Define log level priorities
        level_priorities = {
            'DEBUG': 0, 'INFO': 1, 'WARNING': 2, 'ERROR': 3, 'CRITICAL': 4
        }
        min_priority = level_priorities.get(current_level, 0) if current_level != 'ALL' else -1
        
        # Compile regex for log level detection
        log_level_regex = re.compile(r'^(\d{2}:\d{2}:\d{2})\s+(DEBUG|INFO|WARNING|ERROR|CRITICAL)\s+', re.IGNORECASE)
        
        # Filter lines
        filtered_lines = []
        for line in self._original_log_content.split('\n'):
            if not line.strip():
                continue
                
            # Check log level
            line_level = 'DEBUG'
            match = log_level_regex.match(line)
            if match:
                line_level = match.group(2).upper()
                
            # Check if line matches level filter
            level_ok = (current_level == 'ALL' or 
                       level_priorities.get(line_level, 0) >= min_priority)
                
            # Check if line matches search text
            search_ok = not search_text or search_text in line.lower()
            
            if level_ok and search_ok:
                filtered_lines.append(line)
        
        # Update display
        self.update_log_display('\n'.join(filtered_lines))
        self.update_status(len(filtered_lines), current_level, search_text)

    def update_log_display(self, content):
        """Update the log display with the given content"""
        # Save scroll position
        scroll_bar = self.log_text.verticalScrollBar()
        scroll_pos = scroll_bar.value() if scroll_bar else 0
        
        # Update content
        self.log_text.setPlainText(content)
        
        # Reapply highlighting
        self.highlight_log_levels()
        
        # Restore scroll position if possible
        if scroll_bar and scroll_pos <= scroll_bar.maximum():
            scroll_bar.setValue(scroll_pos)

    def update_status(self, filtered_count=0, current_level='ALL', search_text=''):
        """Update the status bar with current filter information"""
        if not hasattr(self, '_original_log_content'):
            return
            
        total_lines = len(self._original_log_content.split('\n'))
        
        # Build status text
        status_parts = []
        
        if current_level != 'ALL':
            status_parts.append(f"{current_level}+")
            
        if search_text:
            status_parts.append(f'"{search_text}"')
            
        if status_parts:
            status_text = f"{self.translations[self.current_language].get('filtered_by', 'Filtered by')}: {', '.join(status_parts)}"
            self.status_label.setText(status_text)
        else:
            self.status_label.setText(self.translations[self.current_language].get('showing_all', 'Showing all entries'))
        
        # Update line count
        self.line_count_label.setText(
            f"{filtered_count} {self.translations[self.current_language].get('of', 'of')} "
            f"{total_lines} {self.translations[self.current_language].get('entries', 'entries')}"
        )

    def clear_current_log(self):
        """Clear the current log file"""
        if not hasattr(self, 'current_log_file') or not self.current_log_file or not os.path.exists(self.current_log_file):
            return
            
        reply = QMessageBox.question(
            self,
            self.translations[self.current_language].get('confirm_clear', 'Confirm Clear'),
            self.translations[self.current_language].get('confirm_clear_msg', 'Are you sure you want to clear this log file? This cannot be undone.'),
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
                self.status_label.setText(self.translations[self.current_language].get('log_cleared', 'Log file cleared'))
                self.line_count_label.setText('0 lines')
                
            except Exception as e:
                self.status_label.setText(f"{self.translations[self.current_language].get('error_clearing', 'Error clearing log')}: {str(e)}")
                self.logger.log_error(f"Failed to clear log file: {e}", "ViewLogs.clear_current_log")

    def search_text(self, forward=True):
        """Search for text in the log"""
        if not hasattr(self, 'log_text') or not hasattr(self, 'search_edit'):
            return
            
        search_text = self.search_edit.text()
        if not search_text:
            self.filter_log_levels()  # Re-apply filters without search
            return
            
        # Clear previous search highlights
        self.clear_search_highlights()
    def closeEvent(self, event):
        """Handle window close event"""
        self.refresh_timer.stop()
        event.accept()
        
    def on_log_file_changed(self, index):
        """Handle log file selection change"""
        if index >= 0:
            self.load_selected_log()
    
    def load_selected_log(self):
        """Load the selected log file"""
        try:
            current_data = self.log_combo.currentData()
            if not current_data:
                return

            log_file = current_data
            self.current_log_file = log_file  # Ensure current_log_file is set
            
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
                
                # Update text
                self.log_text.setPlainText(content)
                
                # Apply highlighting first
                self.highlight_log_levels()
                
                # Then apply filters
                self.filter_log_levels()
                
                # Restore cursor and scroll position if possible
                if cursor_pos < len(content):
                    cursor.setPosition(min(cursor_pos, len(content)))
                    self.log_text.setTextCursor(cursor)
                
                # Re-enable updates
                self.log_text.setUpdatesEnabled(True)
                
                # Force update the display
                self.log_text.viewport().update()
                
                # Restore scroll position after a short delay
                QTimer.singleShot(50, lambda: scroll_bar.setValue(min(scroll_pos, scroll_bar.maximum())))
                
                # Update status
                visible_lines = sum(1 for line in content.splitlines() if line.strip())
                self.status_label.setText(
                    f"{translations[self.current_language].get('loaded', 'Loaded')}: "
                    f"{os.path.basename(log_file)} ({visible_lines} {translations[self.current_language].get('lines', 'lines')})"
                )
                
            else:
                self.log_text.clear()
                self.status_label.setText(translations[self.current_language].get('log_not_found', 'Log file not found'))

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
