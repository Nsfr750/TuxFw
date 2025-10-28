#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTextEdit,
                             QPushButton, QGroupBox, QLabel, QTabWidget,
                             QListWidget, QListWidgetItem, QSplitter)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from firewall.lang.translations import translations


class HelpWindow(QWidget):
    """Window for displaying help information"""

    def __init__(self, parent, current_language):
        super().__init__(parent)
        self.current_language = current_language

        self.setWindowTitle(translations[self.current_language]['help'] or 'Help')
        self.setMinimumSize(700, 500)
        self.setWindowFlags(Qt.WindowType.Window)

        self.init_ui()

    def init_ui(self):
        """Initialize the UI"""
        layout = QVBoxLayout(self)

        # Header
        header_label = QLabel(translations[self.current_language]['help_title'] or 'Firewall Manager Help')
        header_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        header_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(header_label)

        # Create tab widget for different help sections
        self.tab_widget = QTabWidget()

        # Getting Started tab
        self.create_getting_started_tab()

        # Rules Management tab
        self.create_rules_tab()

        # Configuration tab
        self.create_config_tab()

        # Troubleshooting tab
        self.create_troubleshooting_tab()

        # About tab
        self.create_about_tab()

        layout.addWidget(self.tab_widget)

        # Footer with close button
        footer_layout = QHBoxLayout()
        footer_layout.addStretch()

        self.close_button = QPushButton(translations[self.current_language]['close'] or 'Close')
        self.close_button.clicked.connect(self.close)
        footer_layout.addWidget(self.close_button)

        footer_layout.addStretch()
        layout.addLayout(footer_layout)

    def create_getting_started_tab(self):
        """Create the getting started tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        content = QTextEdit()
        content.setReadOnly(True)
        content.setHtml(self.get_getting_started_html())
        layout.addWidget(content)

        self.tab_widget.addTab(tab, translations[self.current_language]['getting_started'] or 'Getting Started')

    def create_rules_tab(self):
        """Create the rules management tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        content = QTextEdit()
        content.setReadOnly(True)
        content.setHtml(self.get_rules_html())
        layout.addWidget(content)

        self.tab_widget.addTab(tab, translations[self.current_language]['rules_help'] or 'Rules Management')

    def create_config_tab(self):
        """Create the configuration tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        content = QTextEdit()
        content.setReadOnly(True)
        content.setHtml(self.get_config_html())
        layout.addWidget(content)

        self.tab_widget.addTab(tab, translations[self.current_language]['config_help'] or 'Configuration')

    def create_troubleshooting_tab(self):
        """Create the troubleshooting tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        content = QTextEdit()
        content.setReadOnly(True)
        content.setHtml(self.get_troubleshooting_html())
        layout.addWidget(content)

        self.tab_widget.addTab(tab, translations[self.current_language]['troubleshooting'] or 'Troubleshooting')

    def create_about_tab(self):
        """Create the about tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        content = QTextEdit()
        content.setReadOnly(True)
        content.setHtml(self.get_about_html())
        layout.addWidget(content)

        self.tab_widget.addTab(tab, translations[self.current_language]['about'] or 'About')

    def get_getting_started_html(self):
        """Get getting started HTML content"""
        if self.current_language == 'it':
            return """
            <h2>Guida Introduttiva</h2>
            <p><strong>Benvenuto in TuxFw - Gestore Firewall!</strong></p>

            <h3>Avvio rapido:</h3>
            <ol>
                <li><strong>Abilita Firewall:</strong> apri la scheda Stato e premi "Abilita Firewall"</li>
                <li><strong>Aggiungi Regole:</strong> usa la scheda Regole per creare/modificare regole</li>
                <li><strong>Monitoraggio:</strong> vai su <strong>Monitoraggio</strong> → <em>Dashboard</em> per grafici in tempo reale (Download/Upload) e avvisi sicurezza</li>
                <li><strong>Connessioni:</strong> in <em>Connessioni</em> vedi le sessioni attive (protocollo, processo, stato)</li>
                <li><strong>Sicurezza:</strong> in <em>Security</em> gestisci blocco IP/Paesi (GeoIP), rate limiting, reputazione IP (se abilitati)</li>
                <li><strong>VPN:</strong> in <em>VPN</em> seleziona e collega OpenVPN/WireGuard, attiva Kill Switch e Split Tunneling</li>
                <li><strong>Configurazione:</strong> usa la scheda Configurazione per impostazioni e lingua</li>
            </ol>

            <h3>Requisiti:</h3>
            <ul>
                <li>Python 3.7+</li>
                <li>PySide6 per l'interfaccia</li>
                <li>Privilegi di amministratore (regole firewall e VPN su Windows)</li>
                <li>Per GeoIP: file database MaxMind (GeoLite2-Country.mmdb)</li>
                <li>OpenVPN e/o WireGuard installati per la connessione VPN</li>
            </ul>

            <p><em>Nota: alcune funzioni (Kill Switch, Split Tunneling, servizi WireGuard) richiedono esecuzione come Amministratore su Windows.</em></p>
            """
        else:
            return """
            <h2>Getting Started</h2>
            <p><strong>Welcome to TuxFw - Firewall Manager!</strong></p>

            <h3>Quick Start:</h3>
            <ol>
                <li><strong>Enable Firewall:</strong> open the Status tab and click "Enable Firewall"</li>
                <li><strong>Add Rules:</strong> use the Rules tab to create/edit rules</li>
                <li><strong>Monitoring:</strong> go to <strong>Monitoring</strong> → <em>Dashboard</em> for real-time bandwidth charts and security alerts</li>
                <li><strong>Connections:</strong> in <em>Connections</em> view live sessions (protocol, process, status)</li>
                <li><strong>Security:</strong> in <em>Security</em> manage IP/Country blocking (GeoIP), rate limiting, IP reputation (if enabled)</li>
                <li><strong>VPN:</strong> in <em>VPN</em> select and connect OpenVPN/WireGuard, toggle Kill Switch and Split Tunneling</li>
                <li><strong>Configuration:</strong> use the Configuration tab for settings and language</li>
            </ol>

            <h3>Requirements:</h3>
            <ul>
                <li>Python 3.7+</li>
                <li>PySide6 for GUI</li>
                <li>Administrative privileges (Windows firewall rules and VPN)</li>
                <li>For GeoIP: MaxMind DB (GeoLite2-Country.mmdb)</li>
                <li>OpenVPN and/or WireGuard installed for VPN connection</li>
            </ul>

            <p><em>Note: Some features (Kill Switch, Split Tunneling, WireGuard service) require running as Administrator on Windows.</em></p>
            """

    def get_rules_html(self):
        """Get rules management HTML content"""
        if self.current_language == 'it':
            return """
            <h2>Gestione Regole Firewall</h2>
            <h3>Aggiungere Regole:</h3>
            <ol>
                <li>Apri la scheda Regole</li>
                <li>Clicca "Aggiungi Regola"</li>
                <li>Compila i dettagli (Nome, Protocollo, Porta, Direzione, Azione, Descrizione)</li>
                <li>Conferma con OK</li>
            </ol>
            <h3>Modificare/Eliminare:</h3>
            <p>Seleziona una regola e usa i pulsanti "Modifica" o "Elimina".</p>
            <h3>Tipi di Regola:</h3>
            <ul>
                <li><strong>ALLOW/BLOCK</strong></li>
                <li><strong>TCP/UDP/ICMP</strong></li>
            </ul>
            <h3>IDS & Monitoraggio:</h3>
            <p>L'IDS segnala attività sospette (es. porte sensibili, brute force). Vedi avvisi in Monitoraggio → Dashboard.</p>
            """
        else:
            return """
            <h2>Firewall Rules Management</h2>
            <h3>Adding Rules:</h3>
            <ol>
                <li>Open the Rules tab</li>
                <li>Click "Add Rule"</li>
                <li>Fill details (Name, Protocol, Port, Direction, Action, Description)</li>
                <li>Click OK to save</li>
            </ol>
            <h3>Edit/Delete:</h3>
            <p>Select a rule and use "Edit" or "Delete".</p>
            <h3>Rule Types:</h3>
            <ul>
                <li><strong>ALLOW/BLOCK</strong></li>
                <li><strong>TCP/UDP/ICMP</strong></li>
            </ul>
            <h3>IDS & Monitoring:</h3>
            <p>The IDS flags suspicious activity (e.g., sensitive ports, brute force). See alerts in Monitoring → Dashboard.</p>
            """

    def get_config_html(self):
        """Get configuration HTML content"""
        if self.current_language == 'it':
            return """
            <h2>Impostazioni di Configurazione</h2>
            <h3>Generali:</h3>
            <ul>
                <li><strong>Firewall Abilitato</strong></li>
                <li><strong>Politica Predefinita</strong> (ALLOW/BLOCK)</li>
                <li><strong>Logging</strong> e <strong>Lingua</strong></li>
            </ul>
            <h3>Sicurezza Avanzata:</h3>
            <ul>
                <li><strong>Rate Limiting</strong>: limita le richieste per IP</li>
                <li><strong>GeoIP</strong>: blocco paesi (necessita DB GeoLite2)</li>
                <li><strong>Reputazione IP</strong>: liste di minacce aggiornabili</li>
                <li><strong>Port Knocking</strong>: sequenza porte per accesso</li>
            </ul>
            <h3>VPN:</h3>
            <ul>
                <li>Zone con <code>is_vpn: true</code> e <code>vpn_config</code> (OpenVPN/WireGuard)</li>
                <li><strong>Kill Switch</strong> e <strong>Split Tunneling</strong> su Windows Firewall</li>
            </ul>
            <h3>Gestione Configurazione:</h3>
            <ul>
                <li>Salva/Carica/Reset</li>
            </ul>
            """
        else:
            return """
            <h2>Configuration Settings</h2>
            <h3>General:</h3>
            <ul>
                <li><strong>Firewall Enabled</strong></li>
                <li><strong>Default Policy</strong> (ALLOW/BLOCK)</li>
                <li><strong>Logging</strong> and <strong>Language</strong></li>
            </ul>
            <h3>Enhanced Security:</h3>
            <ul>
                <li><strong>Rate Limiting</strong>: limit requests per IP</li>
                <li><strong>GeoIP</strong>: country blocking (requires GeoLite2 DB)</li>
                <li><strong>IP Reputation</strong>: threat feeds updatable</li>
                <li><strong>Port Knocking</strong>: port sequence access</li>
            </ul>
            <h3>VPN:</h3>
            <ul>
                <li>Zones with <code>is_vpn: true</code> and <code>vpn_config</code> (OpenVPN/WireGuard)</li>
                <li><strong>Kill Switch</strong> and <strong>Split Tunneling</strong> via Windows Firewall</li>
            </ul>
            <h3>Config Management:</h3>
            <ul>
                <li>Save/Load/Reset</li>
            </ul>
            """

    def get_troubleshooting_html(self):
        """Get troubleshooting HTML content"""
        if self.current_language == 'it':
            return """
            <h2>Risoluzione Problemi</h2>
            <h3>Problemi Comuni:</h3>
            <h4>L'app non si avvia:</h4>
            <ul>
                <li>Python 3.7+ e PySide6 installati</li>
                <li>Esegui come Amministratore per modifiche firewall/VPN</li>
                <li>Controlla dipendenze (requirements.txt)</li>
            </ul>
            <h4>Regole non funzionano:</h4>
            <ul>
                <li>Verifica privilegi amministrativi</li>
                <li>Controlla servizio firewall di sistema</li>
                <li>Prova con regole semplici</li>
            </ul>
            <h4>VPN non si collega:</h4>
            <ul>
                <li>OpenVPN/WireGuard installati e nel PATH</li>
                <li>File .ovpn/.conf validi e accessibili</li>
                <li>Su Windows: esegui come Amministratore per servizi WireGuard</li>
            </ul>
            <h4>GeoIP disabilitato:</h4>
            <ul>
                <li>Scarica GeoLite2-Country.mmdb e imposta il percorso</li>
            </ul>
            <h3>Log di Sistema:</h3>
            <ul>
                <li><strong>Applicazione:</strong> logs/firewall_YYYY-MM-DD.log</li>
                <li><strong>Configurazione:</strong> config/firewall_config.json</li>
            </ul>
            """
        else:
            return """
            <h2>Troubleshooting</h2>
            <h3>Common Issues:</h3>
            <h4>App won't start:</h4>
            <ul>
                <li>Python 3.7+ and PySide6 installed</li>
                <li>Run as Administrator for firewall/VPN changes</li>
                <li>Check dependencies (requirements.txt)</li>
            </ul>
            <h4>Rules not working:</h4>
            <ul>
                <li>Verify administrative privileges</li>
                <li>Ensure system firewall service is active</li>
                <li>Test with simple rules</li>
            </ul>
            <h4>VPN won't connect:</h4>
            <ul>
                <li>OpenVPN/WireGuard installed and on PATH</li>
                <li>Valid .ovpn/.conf files accessible</li>
                <li>On Windows: run as Administrator for WireGuard services</li>
            </ul>
            <h4>GeoIP disabled:</h4>
            <ul>
                <li>Download GeoLite2-Country.mmdb and set its path</li>
            </ul>
            <h3>System Logs:</h3>
            <ul>
                <li><strong>Application:</strong> logs/firewall_YYYY-MM-DD.log</li>
                <li><strong>Configuration:</strong> config/firewall_config.json</li>
            </ul>
            """

    def get_about_html(self):
        """Get about HTML content"""
        if self.current_language == 'it':
            return """
            <h2>Informazioni su TuxFw</h2>
            <p><strong>TuxFw</strong> è un'interfaccia open-source per gestire regole firewall e monitorare la sicurezza di rete.</p>
            <h3>Funzionalità:</h3>
            <ul>
                <li>Gestione grafica delle regole</li>
                <li>Monitoraggio in tempo reale (grafici banda, connessioni)</li>
                <li>IDS con avvisi</li>
                <li>Sicurezza avanzata: Rate Limiting, GeoIP, Reputazione IP, Port Knocking</li>
                <li>Integrazione VPN: OpenVPN e WireGuard</li>
                <li>Kill Switch e Split Tunneling (Windows)</li>
                <li>Logging completo, profili e multilingua</li>
            </ul>
            <h3>Dettagli Tecnici:</h3>
            <ul>
                <li><strong>Framework:</strong> PySide6</li>
                <li><strong>Lingua:</strong> Python 3.7+</li>
                <li><strong>Licenza:</strong> GPLv3</li>
            </ul>
            <h3>Versione:</h3>
            <ul>
                <li><strong>Versione Attuale:</strong> 0.0.1</li>
                <li><strong>Sviluppatore:</strong> Nsfr750</li>
                <li><strong>Organizzazione:</strong> Tuxxle</li>
            </ul>
            <p><em>© Copyright 2025 Nsfr750 - All rights reserved</em></p>
            """
        else:
            return """
            <h2>About TuxFw</h2>
            <p><strong>TuxFw</strong> is an open-source UI for firewall rule management and network security monitoring.</p>
            <h3>Features:</h3>
            <ul>
                <li>Graphical rule management</li>
                <li>Real-time monitoring (bandwidth charts, connections)</li>
                <li>IDS alerts</li>
                <li>Enhanced Security: Rate Limiting, GeoIP, IP Reputation, Port Knocking</li>
                <li>VPN Integration: OpenVPN and WireGuard</li>
                <li>Kill Switch and Split Tunneling (Windows)</li>
                <li>Full logging, profiles, multi-language</li>
            </ul>
            <h3>Technical:</h3>
            <ul>
                <li><strong>Framework:</strong> PySide6</li>
                <li><strong>Language:</strong> Python 3.7+</li>
                <li><strong>License:</strong> GPLv3</li>
            </ul>
            <h3>Version:</h3>
            <ul>
                <li><strong>Current Version:</strong> 0.0.1</li>
                <li><strong>Developer:</strong> Nsfr750</li>
                <li><strong>Organization:</strong> Tuxxle</li>
            </ul>
            <p><em>© Copyright 2025 Nsfr750 - All rights reserved</em></p>
            """
