#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from PySide6.QtGui import QAction, QActionGroup
from firewall.lang.translations import translations


class MenuManager:
    """Menu functionality detached from main application"""

    def __init__(self, parent, current_language):
        self.parent = parent
        self.current_language = current_language
        
        # Initialize action variables
        self.action_exit = None
        self.action_english = None
        self.action_italian = None
        self.action_view_logs = None
        self.action_help = None
        self.action_sponsor = None
        self.action_about = None
        
        # Initialize language actions group
        self.language_actions = None

    def create_menu_bar(self):
        """Create the menu bar"""
        menubar = self.parent.menuBar()

        # File menu
        file_menu = menubar.addMenu(translations[self.current_language]['menu_file'])
        self.action_exit = QAction(translations[self.current_language]['exit'], self.parent)
        self.action_exit.triggered.connect(self.parent.close)
        file_menu.addAction(self.action_exit)

        # Language menu
        language_menu = menubar.addMenu(translations[self.current_language]['menu_language'])
        
        # Create action group for language selection
        self.language_actions = QActionGroup(self.parent)
        self.language_actions.setExclusive(True)
        
        # English
        self.action_english = QAction(translations[self.current_language]['english'], self.parent)
        self.action_english.setCheckable(True)
        self.action_english.setData('en')
        self.action_english.triggered.connect(lambda: self.parent.change_language('en'))
        language_menu.addAction(self.action_english)
        self.language_actions.addAction(self.action_english)
        
        # Italian
        self.action_italian = QAction(translations[self.current_language]['italian'], self.parent)
        self.action_italian.setCheckable(True)
        self.action_italian.setData('it')
        self.action_italian.triggered.connect(lambda: self.parent.change_language('it'))
        language_menu.addAction(self.action_italian)
        self.language_actions.addAction(self.action_italian)
        
        # Set current language as checked
        if self.current_language == 'en':
            self.action_english.setChecked(True)
        else:
            self.action_italian.setChecked(True)

        # Help menu
        help_menu = menubar.addMenu(translations[self.current_language]['menu_help'])

        # Help
        self.action_help = QAction(translations[self.current_language]['help'], self.parent)
        self.action_help.triggered.connect(self.parent.show_help)
        help_menu.addAction(self.action_help)

        help_menu.addSeparator()

        # About
        self.action_about = QAction(translations[self.current_language]['about'], self.parent)
        self.action_about.triggered.connect(self.show_about)
        help_menu.addAction(self.action_about)

        # Sponsors
        self.action_sponsor = QAction(translations[self.current_language]['sponsors'], self.parent)
        self.action_sponsor.triggered.connect(self.parent.show_sponsors)
        help_menu.addAction(self.action_sponsor)

        help_menu.addSeparator()

        # View Logs
        self.action_view_logs = QAction(translations[self.current_language]['logs'], self.parent)
        self.action_view_logs.triggered.connect(self.parent.show_logs)
        help_menu.addAction(self.action_view_logs)

    def show_about(self):
        """Show the about dialog"""
        if not hasattr(self.parent, 'about_dialog') or self.parent.about_dialog is None:
            from UI.about import AboutDialog
            self.parent.about_dialog = AboutDialog(self.parent, self.current_language)
        self.parent.about_dialog.show()

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
