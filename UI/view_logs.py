#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import re
from datetime import datetime
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QPushButton, QGroupBox, 
    QLabel, QComboBox, QFileDialog, QMessageBox, QSplitter, QFrame, 
    QLineEdit, QCheckBox, QToolButton, QSizePolicy, QMenu, QProgressBar
)
from PySide6.QtCore import Qt, QTimer, QRegularExpression
from PySide6.QtGui import QFont, QTextCharFormat, QColor, QTextCursor, QAction, QIcon
from PySide6.QtWidgets import QStyle
from lang.translations import translations


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
        self.highlight_formats = {}
        self.search_matches = []
        self.current_match = -1

        self.setWindowTitle(f"{translations[self.current_language].get('logs', 'Logs')} - TuxFw")
        self.setMinimumSize(1000, 700)
        self.setWindowFlags(Qt.WindowType.Window)
        
        # Initialize UI
        self.init_ui()
        self.setup_styles()
        
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
        
        refresh_btn = QPushButton()
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
        
        # Add to top controls
        top_controls.addWidget(file_group, 3)
        top_controls.addWidget(refresh_group, 2)
        
        # Search and filter controls
        search_group = QGroupBox(translations[self.current_language].get('search_filter', 'Search & Filter'))
        search_layout = QHBoxLayout()
        
        # Search input
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText(translations[self.current_language].get('search_placeholder', 'Search logs...'))
        self.search_input.textChanged.connect(self.highlight_search_terms)
        
        # Case sensitivity
        self.case_sensitive_cb = QCheckBox(translations[self.current_language].get('case_sensitive', 'Case Sensitive'))
        self.case_sensitive_cb.stateChanged.connect(self.highlight_search_terms)
        
        # Regex toggle
        self.regex_cb = QCheckBox('RegEx')
        self.regex_cb.stateChanged.connect(self.highlight_search_terms)
        
        # Navigation buttons
        nav_layout = QHBoxLayout()
        nav_layout.setSpacing(2)
        
        self.prev_match_btn = QToolButton()
        self.prev_match_btn.setIcon(self.style().standardIcon(self.style().SP_ArrowUp))
        self.prev_match_btn.setToolTip(translations[self.current_language].get('previous_match', 'Previous match'))
        self.prev_match_btn.clicked.connect(self.previous_match)
        
        self.next_match_btn = QToolButton()
        self.next_match_btn.setIcon(self.style().standardIcon(self.style().SP_ArrowDown))
        self.next_match_btn.setToolTip(translations[self.current_language].get('next_match', 'Next match'))
        self.next_match_btn.clicked.connect(self.next_match)
        
        nav_layout.addWidget(self.prev_match_btn)
        nav_layout.addWidget(self.next_match_btn)
        
        # Add to search layout
        search_layout.addWidget(self.search_input, 4)
        search_layout.addWidget(self.case_sensitive_cb, 1)
        search_layout.addWidget(self.regex_cb, 0)
        search_layout.addLayout(nav_layout, 0)
        search_group.setLayout(search_layout)
        
        # Log level filter
        level_group = QGroupBox(translations[self.current_language].get('log_levels', 'Log Levels'))
        level_layout = QHBoxLayout()
        
        self.level_buttons = {}
        for level in ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']:
            btn = QCheckBox(level)
            btn.setChecked(True)
            btn.stateChanged.connect(self.filter_log_levels)
            self.level_buttons[level] = btn
            level_layout.addWidget(btn)
        
        level_layout.addStretch()
        level_group.setLayout(level_layout)
        
        # Action buttons
        btn_layout = QHBoxLayout()
        
        self.clear_btn = QPushButton(translations[self.current_language].get('clear_logs', 'Clear Log'))
        self.clear_btn.clicked.connect(self.clear_current_log)
        
        self.export_btn = QPushButton(translations[self.current_language].get('export', 'Export'))
        self.export_btn.clicked.connect(self.export_log)
        
        # Add a menu to the export button for different formats
        export_menu = QMenu()
        export_txt = export_menu.addAction('Text (.txt)')
        export_csv = export_menu.addAction('CSV (.csv)')
        export_json = export_menu.addAction('JSON (.json)')
        
        export_txt.triggered.connect(lambda: self.export_log('txt'))
        export_csv.triggered.connect(lambda: self.export_log('csv'))
        export_json.triggered.connect(lambda: self.export_log('json'))
        
        self.export_btn.setMenu(export_menu)
        
        btn_layout.addWidget(self.clear_btn)
        btn_layout.addWidget(self.export_btn)
        btn_layout.addStretch()
        
        # Log display area
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setFont(QFont('Consolas', 9))
        self.log_text.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)
        
        # Status bar
        status_bar = QHBoxLayout()
        
        self.status_label = QLabel(translations[self.current_language].get('ready', 'Ready'))
        self.status_label.setStyleSheet('padding: 2px 5px;')
        
        self.line_count_label = QLabel('0 lines')
        self.line_count_label.setStyleSheet('padding: 2px 5px; border-left: 1px solid #3a3a3a;')
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximum(100)
        self.progress_bar.setMaximumHeight(16)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.hide()
        
        status_bar.addWidget(self.status_label, 1)
        status_bar.addWidget(self.line_count_label, 0)
        status_bar.addWidget(self.progress_bar, 2)
        
        # Assemble main layout
        main_layout.addLayout(top_controls, 0)
        main_layout.addWidget(search_group, 0)
        main_layout.addWidget(level_group, 0)
        main_layout.addWidget(self.log_text, 1)
        main_layout.addLayout(btn_layout, 0)
        main_layout.addLayout(status_bar, 0)

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
                self.load_log_file(self.current_log_file)
            else:
                self.status_label.setText("No log files found")
                self.log_text.clear()
                
            self.log_combo.blockSignals(False)
            
        except Exception as e:
            self.status_label.setText(f"Error loading log files: {str(e)}")
            self.logger.log_error(f"Failed to load log files: {e}", "ViewLogs.load_log_files")
            # Clear and disable UI elements on error
            self.log_combo.clear()
            self.log_text.clear()
            self.log_combo.setEnabled(False)
            self.clear_btn.setEnabled(False)
            self.export_btn.setEnabled(False)
    
    def load_log_file(self, file_path):
        """Load and display the specified log file"""
        try:
            self.progress_bar.show()
            self.progress_bar.setValue(0)
            self.status_label.setText(f"{translations[self.current_language].get('loading', 'Loading')} {os.path.basename(file_path)}...")
            
            # Read the file in chunks to handle large files
            chunk_size = 8192
            total_size = os.path.getsize(file_path)
            bytes_read = 0
            
            self.log_text.clear()
            cursor = self.log_text.textCursor()
            
            with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                while True:
                    chunk = f.read(chunk_size)
                    if not chunk:
                        break
                        
                    cursor.insertText(chunk)
                    bytes_read += len(chunk)
                    progress = int((bytes_read / total_size) * 100)
                    self.progress_bar.setValue(progress)
                    QApplication.processEvents()
            
            # Apply syntax highlighting
            self.highlight_log_levels()
            
            # Update line count
            line_count = self.log_text.document().lineCount()
            self.line_count_label.setText(f"{line_count} {translations[self.current_language].get('lines', 'lines')}")
            
            # Scroll to bottom
            self.log_text.verticalScrollBar().setValue(self.log_text.verticalScrollBar().maximum())
            
            self.status_label.setText(f"{translations[self.current_language].get('loaded', 'Loaded')} {os.path.basename(file_path)}")
            
        except Exception as e:
            self.status_label.setText(f"{translations[self.current_language].get('error_loading', 'Error loading')} {os.path.basename(file_path)}: {str(e)}")
            self.logger.log_error(f"Failed to load log file {file_path}: {e}", "ViewLogs.load_log_file")
        
        finally:
            self.progress_bar.hide()
    
    def highlight_log_levels(self):
        """Apply syntax highlighting to log levels"""
        if not self.log_text.toPlainText():
            return
            
        cursor = self.log_text.textCursor()
        cursor.movePosition(cursor.Start)
        cursor.beginEditBlock()
        
        # Clear existing formatting
        cursor.select(cursor.Document)
        cursor.setCharFormat(QTextCharFormat())
        cursor.clearSelection()
        
        # Apply highlighting for each log level
        for level, fmt in self.highlight_formats.items():
            if level == 'SEARCH':
                continue  # Skip search highlights for now
                
            self.highlight_text(fr'\b{level}\b', fmt)
        
        cursor.endEditBlock()
    
    def highlight_text(self, pattern, text_format):
        """Highlight text matching the given pattern"""
        cursor = self.log_text.textCursor()
        cursor.movePosition(cursor.Start)
        
        # Create a regex pattern
        flags = 0 if self.case_sensitive_cb.isChecked() else re.IGNORECASE
        if not self.regex_cb.isChecked():
            pattern = re.escape(pattern)
            
        try:
            regex = re.compile(pattern, flags)
        except re.error:
            return  # Invalid regex
            
        # Find all matches
        self.search_matches = []
        text = self.log_text.toPlainText()
        for match in regex.finditer(text):
            self.search_matches.append(match.span())
            
        # Highlight matches
        for start, end in self.search_matches:
            cursor.setPosition(start)
            cursor.movePosition(cursor.Right, cursor.KeepAnchor, end - start)
            cursor.mergeCharFormat(text_format)
    
    def highlight_search_terms(self):
        """Highlight search terms in the log"""
        search_text = self.search_input.text().strip()
        if not search_text:
            self.highlight_log_levels()
            self.current_match = -1
            self.update_navigation_buttons()
            return
            
        # First, reapply log level highlighting
        self.highlight_log_levels()
        
        # Then apply search highlighting
        if search_text:
            flags = QTextDocument.FindFlags()
            if self.case_sensitive_cb.isChecked():
                flags |= QTextDocument.FindCaseSensitively
                
            # Find all matches
            self.search_matches = []
            cursor = self.log_text.textCursor()
            cursor.movePosition(cursor.Start)
            
            while True:
                cursor = self.log_text.document().find(search_text, cursor, flags)
                if cursor.isNull():
                    break
                self.search_matches.append((cursor.selectionStart(), cursor.selectionEnd()))
            
            # Highlight matches
            cursor = self.log_text.textCursor()
            cursor.beginEditBlock()
            
            for start, end in self.search_matches:
                cursor.setPosition(start)
                cursor.movePosition(cursor.Right, cursor.KeepAnchor, end - start)
                cursor.mergeCharFormat(self.highlight_formats['SEARCH'])
            
            cursor.endEditBlock()
            
            # Update navigation buttons
            self.current_match = -1
            self.update_navigation_buttons()
    
    def update_navigation_buttons(self):
        """Update the state of navigation buttons"""
        has_matches = len(self.search_matches) > 0
        self.prev_match_btn.setEnabled(has_matches)
        self.next_match_btn.setEnabled(has_matches)
        
        if has_matches:
            self.status_label.setText(f"{len(self.search_matches)} {translations[self.current_language].get('matches_found', 'matches found')}")
        else:
            self.status_label.setText(translations[self.current_language].get('no_matches', 'No matches found'))
    
    def next_match(self):
        """Move to the next search match"""
        if not self.search_matches:
            return
            
        self.current_match = (self.current_match + 1) % len(self.search_matches)
        self.scroll_to_match()
    
    def previous_match(self):
        """Move to the previous search match"""
        if not self.search_matches:
            return
            
        self.current_match = (self.current_match - 1) % len(self.search_matches)
        self.scroll_to_match()
    
    def scroll_to_match(self):
        """Scroll to the current search match"""
        if not self.search_matches or self.current_match < 0:
            return
            
        start, end = self.search_matches[self.current_match]
        
        cursor = self.log_text.textCursor()
        cursor.setPosition(start)
        cursor.movePosition(cursor.Right, cursor.KeepAnchor, end - start)
        self.log_text.setTextCursor(cursor)
        self.log_text.centerCursor()
        
        # Update status
        self.status_label.setText(f"{self.current_match + 1} {translations[self.current_language].get('of', 'of')} {len(self.search_matches)}")
    
    def on_log_file_changed(self, index):
        """Handle log file selection change"""
        if index < 0 or index >= len(self.log_files):
            return
            
        self.current_log_file = self.log_files[index]
        self.load_log_file(self.current_log_file)
    
    def toggle_auto_refresh(self, state):
        """Toggle auto-refresh of the log file"""
        self.auto_refresh = state == Qt.Checked
        if self.auto_refresh:
            self.refresh_timer.start(self.auto_refresh_interval)
        else:
            self.refresh_timer.stop()
    
    def update_refresh_interval(self, interval_str):
        """Update the auto-refresh interval"""
        try:
            self.auto_refresh_interval = int(interval_str) * 1000  # Convert to milliseconds
            if self.auto_refresh:
                self.refresh_timer.start(self.auto_refresh_interval)
        except ValueError:
            pass
    
    def auto_refresh_log(self):
        """Auto-refresh the current log file"""
        if self.auto_refresh and self.current_log_file and os.path.exists(self.current_log_file):
            self.load_log_file(self.current_log_file)
    
    def filter_log_levels(self):
        """Filter log messages by log level"""
        # This is a placeholder for log level filtering
        # Implementation would depend on how log levels are formatted in the log file
        pass
    
    def clear_current_log(self):
        """Clear the current log file"""
        if not self.current_log_file:
            return
            
        reply = QMessageBox.question(
            self,
            translations[self.current_language].get('confirm_clear', 'Confirm Clear'),
            translations[self.current_language].get('confirm_clear_msg', 'Are you sure you want to clear this log file? This cannot be undone.'),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                with open(self.current_log_file, 'w', encoding='utf-8') as f:
                    f.write('')
                
                self.load_log_file(self.current_log_file)
                self.status_label.setText(translations[self.current_language].get('log_cleared', 'Log file cleared'))
                self.logger.log_firewall_event("LOG_CLEARED", f"Cleared log file: {os.path.basename(self.current_log_file)}")
                
            except Exception as e:
                self.status_label.setText(f"{translations[self.current_language].get('error_clearing', 'Error clearing log')}: {str(e)}")
                self.logger.log_error(f"Failed to clear log file: {e}", "ViewLogs.clear_current_log")
    
    def export_log(self, format='txt'):
        """Export the current log to a file"""
        if not self.current_log_file:
            return
            
        try:
            default_name = os.path.splitext(os.path.basename(self.current_log_file))[0]
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                translations[self.current_language].get('export_log', 'Export Log'),
                f"{default_name}.{format}",
                f"{format.upper()} (*.{format});;All Files (*)"
            )
            
            if file_path:
                content = self.log_text.toPlainText()
                
                if format == 'csv':
                    # Convert log lines to CSV format
                    import csv
                    lines = content.split('\n')
                    with open(file_path, 'w', newline='', encoding='utf-8') as f:
                        writer = csv.writer(f)
                        writer.writerow(['Timestamp', 'Level', 'Message'])
                        for line in lines:
                            # Simple CSV conversion - adjust based on your log format
                            parts = line.split(' - ', 2)
                            if len(parts) >= 3:
                                writer.writerow(parts)
                            else:
                                writer.writerow(['', '', line])
                                
                elif format == 'json':
                    # Convert log lines to JSON format
                    import json
                    lines = content.split('\n')
                    log_entries = []
                    for line in lines:
                        # Simple JSON conversion - adjust based on your log format
                        parts = line.split(' - ', 2)
                        if len(parts) >= 3:
                            log_entries.append({
                                'timestamp': parts[0],
                                'level': parts[1],
                                'message': parts[2]
                            })
                        else:
                            log_entries.append({'message': line})
                    
                    with open(file_path, 'w', encoding='utf-8') as f:
                        json.dump(log_entries, f, indent=2)
                        
                else:  # Plain text
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                
                self.status_label.setText(f"{translations[self.current_language].get('log_exported', 'Log exported to')} {os.path.basename(file_path)}")
                self.logger.log_firewall_event("LOG_EXPORTED", f"Exported log to {file_path}")
                
        except Exception as e:
            self.status_label.setText(f"{translations[self.current_language].get('error_exporting', 'Error exporting log')}: {str(e)}")
            self.logger.log_error(f"Failed to export log: {e}", "ViewLogs.export_log")
    
    def closeEvent(self, event):
        """Handle window close event"""
        self.refresh_timer.stop()
        event.accept()
        
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
