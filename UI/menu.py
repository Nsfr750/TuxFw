#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from PySide6.QtGui import QAction
from lang.translations import translations


class MenuManager:
    """Menu functionality detached from main application"""

    def __init__(self, parent, current_language):
        self.parent = parent
        self.current_language = current_language

    def create_menu_bar(self):
        """Create the menu bar"""
        menubar = self.parent.menuBar()

        # File menu
        file_menu = menubar.addMenu(translations[self.current_language]['menu_file'])
        exit_action = QAction(translations[self.current_language]['exit'], self.parent)
        exit_action.triggered.connect(self.parent.close)
        file_menu.addAction(exit_action)

        # Language menu
        language_menu = menubar.addMenu(translations[self.current_language]['menu_language'])
        english_action = QAction(translations[self.current_language]['english'], self.parent)
        english_action.triggered.connect(lambda: self.parent.change_language('en'))
        language_menu.addAction(english_action)

        italian_action = QAction(translations[self.current_language]['italian'], self.parent)
        italian_action.triggered.connect(lambda: self.parent.change_language('it'))
        language_menu.addAction(italian_action)

        # Help menu
        help_menu = menubar.addMenu(translations[self.current_language]['menu_help'])

        # View Logs
        logs_action = QAction(translations[self.current_language]['logs'], self.parent)
        logs_action.triggered.connect(self.parent.show_logs)
        help_menu.addAction(logs_action)

        help_menu.addSeparator()

        # Help
        help_action = QAction(translations[self.current_language]['help'], self.parent)
        help_action.triggered.connect(self.parent.show_help)
        help_menu.addAction(help_action)

        # Sponsors
        sponsors_action = QAction(translations[self.current_language]['sponsors'], self.parent)
        sponsors_action.triggered.connect(self.parent.show_sponsors)
        help_menu.addAction(sponsors_action)

        help_menu.addSeparator()

        # About (existing)
        about_action = QAction(translations[self.current_language]['about'], self.parent)
        about_action.triggered.connect(self.parent.about_dialog.show_about)
        help_menu.addAction(about_action)

    def retranslate_menu(self):
        """Retranslate menu items"""
        menubar = self.parent.menuBar()

        # Update menu texts
        for action in menubar.actions():
            menu_text = action.text()
            if menu_text == 'File':
                action.setText(translations[self.current_language]['menu_file'])
            elif menu_text == 'Language':
                action.setText(translations[self.current_language]['menu_language'])
            elif menu_text == 'Help':
                action.setText(translations[self.current_language]['menu_help'])

            # Update submenu items
            if hasattr(action, 'menu') and action.menu():
                for sub_action in action.menu().actions():
                    sub_text = sub_action.text()
                    if sub_text == 'Exit':
                        sub_action.setText(translations[self.current_language]['exit'])
                    elif sub_text == 'English':
                        sub_action.setText(translations[self.current_language]['english'])
                    elif sub_text == 'Italian':
                        sub_action.setText(translations[self.current_language]['italian'])
                    elif sub_text == 'Logs':
                        sub_action.setText(translations[self.current_language]['logs'])
                    elif sub_text == 'Help':
                        sub_action.setText(translations[self.current_language]['help'])
                    elif sub_text == 'Sponsors':
                        sub_action.setText(translations[self.current_language]['sponsors'])
                    elif sub_text == 'About':
                        sub_action.setText(translations[self.current_language]['about'])
