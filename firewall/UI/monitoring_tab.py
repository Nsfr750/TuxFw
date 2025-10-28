#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTabWidget,
                             QTableWidget, QTableWidgetItem, QHeaderView,
                             QPushButton, QLabel, QComboBox, QGroupBox,
                             QFormLayout, QSplitter, QProgressBar, QTextEdit, QCheckBox,
                             QLineEdit, QListWidget, QListWidgetItem, QSpinBox)
from PySide6.QtCharts import QChart, QChartView, QLineSeries, QValueAxis
from PySide6.QtCore import Qt, QTimer, Signal, Slot
from PySide6.QtGui import QColor, QBrush, QFont
from datetime import datetime

class MonitoringTab(QWidget):
    """Tab for monitoring network traffic and security events"""
    
    def __init__(self, parent=None, firewall_manager=None):
        """Initialize the monitoring tab"""
        super().__init__(parent)
        self.firewall = firewall_manager
        # Chart state
        self._chart_time = 0
        self._chart_window = 60  # last N points
        self._last_bytes = {"bytes_recv": None, "bytes_sent": None}
        self._last_ts = None
        self.setup_ui()
        self.setup_connections()
        
    def setup_ui(self):
        """Set up the UI components"""
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(5, 5, 5, 5)
        self.layout.setSpacing(10)
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        
        # Add tabs
        self.tab_widget.addTab(self.create_dashboard_tab(), "Dashboard")
        self.tab_widget.addTab(self.create_connections_tab(), "Connections")
        self.tab_widget.addTab(self.create_vpn_tab(), "VPN")
        self.tab_widget.addTab(self.create_ids_tab(), "Intrusion Detection")
        self.tab_widget.addTab(self.create_security_tab(), "Security")
        
        self.layout.addWidget(self.tab_widget)
    
    def create_dashboard_tab(self):
        """Create the dashboard tab with network statistics"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Network stats group
        stats_group = QGroupBox("Network Statistics")
        stats_layout = QVBoxLayout()
        
        # Interface selector
        self.interface_combo = QComboBox()
        self.interface_combo.addItem("All Interfaces")
        stats_layout.addWidget(QLabel("Network Interface:"))
        stats_layout.addWidget(self.interface_combo)
        
        # Stats table
        self.stats_table = QTableWidget(0, 4)
        self.stats_table.setHorizontalHeaderLabels(["Interface", "Download", "Upload", "Connections"])
        self.stats_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        stats_layout.addWidget(self.stats_table)

        stats_group.setLayout(stats_layout)

        # Bandwidth charts group
        charts_group = QGroupBox("Bandwidth (Mbps)")
        charts_layout = QVBoxLayout()

        # Download chart
        self.series_down = QLineSeries()
        self.chart_down = QChart()
        self.chart_down.addSeries(self.series_down)
        self.chart_down.setTitle("Download")
        self.axis_x_down = QValueAxis()
        self.axis_x_down.setRange(0, self._chart_window)
        self.axis_x_down.setLabelFormat("%.0f")
        self.axis_x_down.setTitleText("Time (ticks)")
        self.axis_y_down = QValueAxis()
        self.axis_y_down.setRange(0, 100)
        self.axis_y_down.setLabelFormat("%.1f")
        self.axis_y_down.setTitleText("Mbps")
        self.chart_down.addAxis(self.axis_x_down, Qt.AlignBottom)
        self.chart_down.addAxis(self.axis_y_down, Qt.AlignLeft)
        self.series_down.attachAxis(self.axis_x_down)
        self.series_down.attachAxis(self.axis_y_down)
        self.view_down = QChartView(self.chart_down)

        # Upload chart
        self.series_up = QLineSeries()
        self.chart_up = QChart()
        self.chart_up.addSeries(self.series_up)
        self.chart_up.setTitle("Upload")
        self.axis_x_up = QValueAxis()
        self.axis_x_up.setRange(0, self._chart_window)
        self.axis_x_up.setLabelFormat("%.0f")
        self.axis_x_up.setTitleText("Time (ticks)")
        self.axis_y_up = QValueAxis()
        self.axis_y_up.setRange(0, 100)
        self.axis_y_up.setLabelFormat("%.1f")
        self.axis_y_up.setTitleText("Mbps")
        self.chart_up.addAxis(self.axis_x_up, Qt.AlignBottom)
        self.chart_up.addAxis(self.axis_y_up, Qt.AlignLeft)
        self.series_up.attachAxis(self.axis_x_up)
        self.series_up.attachAxis(self.axis_y_up)
        self.view_up = QChartView(self.chart_up)

        charts_layout.addWidget(self.view_down)
        charts_layout.addWidget(self.view_up)
        charts_group.setLayout(charts_layout)

        # Alerts group
        alerts_group = QGroupBox("Security Alerts")
        alerts_layout = QVBoxLayout()
        
        self.alerts_table = QTableWidget(0, 4)
        self.alerts_table.setHorizontalHeaderLabels(["Time", "Severity", "Source", "Description"])
        self.alerts_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        alerts_layout.addWidget(self.alerts_table)
        
        alerts_group.setLayout(alerts_layout)
        
        # Add to splitter
        splitter = QSplitter(Qt.Vertical)
        splitter.addWidget(stats_group)
        splitter.addWidget(charts_group)
        splitter.addWidget(alerts_group)
        splitter.setStretchFactor(0, 2)
        splitter.setStretchFactor(1, 2)
        splitter.setStretchFactor(2, 3)
        
        layout.addWidget(splitter)
        return tab

    def create_security_tab(self):
        """Create the Security management tab (IP/Country blocking)"""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # IP Blocking group
        ip_group = QGroupBox("IP Blocking")
        ip_layout = QVBoxLayout()

        ip_controls = QHBoxLayout()
        self.ip_input = QLineEdit()
        self.ip_input.setPlaceholderText("Enter IP address (e.g., 192.168.1.10)")
        self.ip_duration = QSpinBox()
        self.ip_duration.setRange(60, 86400)
        self.ip_duration.setValue(3600)
        self.ip_duration.setSuffix(" s")
        self.block_ip_btn = QPushButton("Block IP")
        self.unblock_ip_btn = QPushButton("Unblock Selected")
        self.refresh_ip_btn = QPushButton("Refresh")

        ip_controls.addWidget(QLabel("IP:"))
        ip_controls.addWidget(self.ip_input)
        ip_controls.addWidget(QLabel("Duration:"))
        ip_controls.addWidget(self.ip_duration)
        ip_controls.addWidget(self.block_ip_btn)
        ip_controls.addWidget(self.unblock_ip_btn)
        ip_controls.addStretch()
        ip_controls.addWidget(self.refresh_ip_btn)

        self.blocked_ip_list = QListWidget()

        ip_layout.addLayout(ip_controls)
        ip_layout.addWidget(self.blocked_ip_list)
        ip_group.setLayout(ip_layout)

        # Country Blocking group
        country_group = QGroupBox("Country Blocking")
        country_layout = QVBoxLayout()

        country_controls = QHBoxLayout()
        self.country_input = QLineEdit()
        self.country_input.setMaxLength(2)
        self.country_input.setPlaceholderText("Country code (e.g., RU)")
        self.block_country_btn = QPushButton("Block Country")
        self.unblock_country_btn = QPushButton("Unblock Selected")
        self.refresh_country_btn = QPushButton("Refresh")

        country_controls.addWidget(QLabel("Country:"))
        country_controls.addWidget(self.country_input)
        country_controls.addWidget(self.block_country_btn)
        country_controls.addWidget(self.unblock_country_btn)
        country_controls.addStretch()
        country_controls.addWidget(self.refresh_country_btn)

        self.blocked_country_list = QListWidget()

        country_layout.addLayout(country_controls)
        country_layout.addWidget(self.blocked_country_list)
        country_group.setLayout(country_layout)

        # Add groups
        layout.addWidget(ip_group)
        layout.addWidget(country_group)

        return tab
    
    def create_connections_tab(self):
        """Create the connections monitoring tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Connection controls
        controls = QHBoxLayout()
        self.refresh_btn = QPushButton("Refresh")
        self.export_btn = QPushButton("Export to CSV")
        self.auto_refresh = QCheckBox("Auto-refresh (5s)")
        
        controls.addWidget(self.refresh_btn)
        controls.addWidget(self.export_btn)
        controls.addStretch()
        controls.addWidget(self.auto_refresh)
        
        # Connection table
        self.connections_table = QTableWidget(0, 6)
        self.connections_table.setHorizontalHeaderLabels([
            "Protocol", "Local Address", "Remote Address", "Status", "Process", "PID"
        ])
        self.connections_table.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        
        layout.addLayout(controls)
        layout.addWidget(self.connections_table)
        
        return tab
    
    def create_vpn_tab(self):
        """Create the VPN management tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # VPN Controls (selector, kill switch, split tunneling)
        top_controls = QGroupBox("VPN Controls")
        tc_layout = QFormLayout()

        # VPN selector
        self.vpn_selector = QComboBox()
        self.vpn_selector.setEditable(False)
        tc_layout.addRow(QLabel("VPN:"), self.vpn_selector)

        # Kill switch toggle
        self.killswitch_check = QCheckBox("Enable Kill Switch (Windows Firewall)")
        tc_layout.addRow(self.killswitch_check)

        # Split tunneling controls
        split_group = QGroupBox("Split Tunneling")
        split_layout = QVBoxLayout()
        split_row = QHBoxLayout()
        self.split_mode = QComboBox()
        self.split_mode.addItems(["exclude", "include"])  # exclude: list won't go via VPN; include: only list via VPN
        self.split_route_input = QLineEdit()
        self.split_route_input.setPlaceholderText("CIDR or IP (e.g., 1.2.3.0/24 or 8.8.8.8)")
        self.split_add_btn = QPushButton("Add")
        self.split_remove_btn = QPushButton("Remove Selected")
        self.split_apply_btn = QPushButton("Apply")
        split_row.addWidget(QLabel("Mode:"))
        split_row.addWidget(self.split_mode)
        split_row.addSpacing(10)
        split_row.addWidget(QLabel("Route:"))
        split_row.addWidget(self.split_route_input)
        split_row.addWidget(self.split_add_btn)
        split_row.addWidget(self.split_remove_btn)
        split_row.addWidget(self.split_apply_btn)
        self.split_routes_list = QListWidget()
        split_layout.addLayout(split_row)
        split_layout.addWidget(self.split_routes_list)
        split_group.setLayout(split_layout)

        top_controls.setLayout(tc_layout)
        layout.addWidget(top_controls)
        layout.addWidget(split_group)

        # VPN status group
        status_group = QGroupBox("VPN Status")
        status_layout = QFormLayout()
        
        self.vpn_status = QLabel("Not Connected")
        self.vpn_status.setStyleSheet("font-weight: bold; color: red;")
        self.vpn_interface = QLabel("N/A")
        self.vpn_ip = QLabel("N/A")
        self.vpn_uptime = QLabel("00:00:00")
        
        status_layout.addRow("Status:", self.vpn_status)
        status_layout.addRow("Interface:", self.vpn_interface)
        status_layout.addRow("IP Address:", self.vpn_ip)
        status_layout.addRow("Uptime:", self.vpn_uptime)
        
        # VPN controls
        self.vpn_connect_btn = QPushButton("Connect")
        self.vpn_disconnect_btn = QPushButton("Disconnect")
        self.vpn_configure_btn = QPushButton("Configure...")
        
        controls = QHBoxLayout()
        controls.addWidget(self.vpn_connect_btn)
        controls.addWidget(self.vpn_disconnect_btn)
        controls.addStretch()
        controls.addWidget(self.vpn_configure_btn)
        
        status_layout.addRow(controls)
        status_group.setLayout(status_layout)
        
        # VPN log
        log_group = QGroupBox("VPN Log")
        log_layout = QVBoxLayout()
        
        self.vpn_log = QTextEdit()
        self.vpn_log.setReadOnly(True)
        self.vpn_log.setFontFamily("Courier")
        
        log_controls = QHBoxLayout()
        self.clear_log_btn = QPushButton("Clear Log")
        self.save_log_btn = QPushButton("Save Log...")
        
        log_controls.addWidget(self.clear_log_btn)
        log_controls.addStretch()
        log_controls.addWidget(self.save_log_btn)
        
        log_layout.addWidget(self.vpn_log)
        log_layout.addLayout(log_controls)
        log_group.setLayout(log_layout)
        
        # Add to layout
        layout.addWidget(status_group)
        layout.addWidget(log_group)
        
        return tab
    
    def create_ids_tab(self):
        """Create the Intrusion Detection System tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # IDS status
        status_group = QGroupBox("IDS Status")
        status_layout = QHBoxLayout()
        
        self.ids_status = QLabel("Active")
        self.ids_status.setStyleSheet("font-weight: bold; color: green;")
        self.threats_blocked = QLabel("Threats Blocked: 0")
        self.last_threat = QLabel("Last Threat: Never")
        
        status_layout.addWidget(QLabel("Status: "))
        status_layout.addWidget(self.ids_status)
        status_layout.addStretch()
        status_layout.addWidget(self.threats_blocked)
        status_layout.addStretch()
        status_layout.addWidget(self.last_threat)
        
        status_group.setLayout(status_layout)
        
        # IDS rules
        rules_group = QGroupBox("Detection Rules")
        rules_layout = QVBoxLayout()
        
        self.rules_table = QTableWidget(0, 4)
        self.rules_table.setHorizontalHeaderLabels(["Enabled", "Rule", "Severity", "Description"])
        self.rules_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.rules_table.verticalHeader().setVisible(False)
        
        # Add some sample rules (in a real app, these would come from the IDS)
        self.rules = [
            (True, "Port Scan Detection", "High", "Detects potential port scanning activity"),
            (True, "Brute Force Attempt", "High", "Detects multiple failed login attempts"),
            (True, "Suspicious Connection", "Medium", "Detects connections to known malicious IPs"),
            (False, "HTTP Exploit Attempt", "Critical", "Detects known web application exploits"),
            (True, "DNS Tunneling", "Medium", "Detects potential DNS tunneling attempts")
        ]
        
        self.rules_table.setRowCount(len(self.rules))
        for i, (enabled, rule, severity, desc) in enumerate(self.rules):
            # Enabled checkbox
            item = QTableWidgetItem()
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            item.setCheckState(Qt.Checked if enabled else Qt.Unchecked)
            self.rules_table.setItem(i, 0, item)
            
            # Rule name
            self.rules_table.setItem(i, 1, QTableWidgetItem(rule))
            
            # Severity with color coding
            severity_item = QTableWidgetItem(severity)
            if severity == "High" or severity == "Critical":
                severity_item.setForeground(QBrush(QColor(200, 0, 0)))
            elif severity == "Medium":
                severity_item.setForeground(QBrush(QColor(200, 100, 0)))
            self.rules_table.setItem(i, 2, severity_item)
            
            # Description
            self.rules_table.setItem(i, 3, QTableWidgetItem(desc))
        
        rules_controls = QHBoxLayout()
        self.enable_all_btn = QPushButton("Enable All")
        self.disable_all_btn = QPushButton("Disable All")
        self.apply_rules_btn = QPushButton("Apply Changes")
        
        rules_controls.addWidget(self.enable_all_btn)
        rules_controls.addWidget(self.disable_all_btn)
        rules_controls.addStretch()
        rules_controls.addWidget(self.apply_rules_btn)
        
        rules_layout.addWidget(self.rules_table)
        rules_layout.addLayout(rules_controls)
        rules_group.setLayout(rules_layout)
        
        # Add to layout
        layout.addWidget(status_group)
        layout.addWidget(rules_group)
        
        return tab
    
    def setup_connections(self):
        """Set up signal/slot connections"""
        # Connect to firewall manager signals if available
        if self.firewall and hasattr(self.firewall, 'signals'):
            self.firewall.signals.network_stats_updated.connect(self.update_network_stats)
            self.firewall.signals.connection_detected.connect(self.add_connection)
            self.firewall.signals.intrusion_detected.connect(self.add_alert)
            self.firewall.signals.vpn_status_changed.connect(self.update_vpn_status)
            if hasattr(self.firewall.signals, 'vpn_log_line'):
                self.firewall.signals.vpn_log_line.connect(self.vpn_log.append)
        
        # Connect UI controls
        self.refresh_btn.clicked.connect(self.refresh_connections)
        self.auto_refresh.stateChanged.connect(self.toggle_auto_refresh)
        self.interface_combo.currentIndexChanged.connect(self._on_interface_changed)
        # VPN controls
        self.vpn_selector.currentIndexChanged.connect(self.on_vpn_selected)
        self.killswitch_check.toggled.connect(self.toggle_kill_switch)
        self.split_add_btn.clicked.connect(self.add_split_route)
        self.split_remove_btn.clicked.connect(self.remove_selected_split_route)
        self.split_apply_btn.clicked.connect(self.apply_split_tunneling)
        self.vpn_connect_btn.clicked.connect(self.connect_vpn)
        self.vpn_disconnect_btn.clicked.connect(self.disconnect_vpn)
        self.clear_log_btn.clicked.connect(self.vpn_log.clear)
        
        # Set up auto-refresh timer
        self.refresh_timer = QTimer(self)
        self.refresh_timer.timeout.connect(self.refresh_connections)
        
        # Initial refresh
        self.refresh_connections()
        self.refresh_security()
        self.refresh_vpn_list()
        self.load_split_tunneling()

        # Connect security actions
        self.block_ip_btn.clicked.connect(self.block_ip)
        self.unblock_ip_btn.clicked.connect(self.unblock_selected_ip)
        self.refresh_ip_btn.clicked.connect(self.refresh_security)
        self.block_country_btn.clicked.connect(self.block_country)
        self.unblock_country_btn.clicked.connect(self.unblock_selected_country)
        self.refresh_country_btn.clicked.connect(self.refresh_security)
    
    # Slots for handling updates from the firewall manager
    
    @Slot(dict)
    def update_network_stats(self, stats):
        """Update network statistics display"""
        # Update interface list in combo box
        current_interfaces = {self.interface_combo.itemText(i) for i in range(1, self.interface_combo.count())}
        new_interfaces = set(stats['interfaces'].keys()) - current_interfaces
        
        for iface in new_interfaces:
            self.interface_combo.addItem(iface)
        
        # Update stats table
        self.stats_table.setRowCount(len(stats['interfaces']))
        
        for i, (iface, data) in enumerate(stats['interfaces'].items()):
            self.stats_table.setItem(i, 0, QTableWidgetItem(iface))
            self.stats_table.setItem(i, 1, QTableWidgetItem(f"{data['bytes_recv'] / (1024*1024):.2f} MB"))
            self.stats_table.setItem(i, 2, QTableWidgetItem(f"{data['bytes_sent'] / (1024*1024):.2f} MB"))
            self.stats_table.setItem(i, 3, QTableWidgetItem(str(data.get('connections', 0))))

        # Compute bandwidth and update charts (Mbps)
        sel = self.interface_combo.currentText()
        sum_recv = 0
        sum_sent = 0
        if sel and sel != "All Interfaces" and sel in stats['interfaces']:
            sum_recv = stats['interfaces'][sel].get('bytes_recv', 0)
            sum_sent = stats['interfaces'][sel].get('bytes_sent', 0)
        else:
            for d in stats['interfaces'].values():
                sum_recv += d.get('bytes_recv', 0)
                sum_sent += d.get('bytes_sent', 0)

        now = datetime.now().timestamp()
        rate_down_mbps = 0.0
        rate_up_mbps = 0.0
        if self._last_bytes['bytes_recv'] is not None and self._last_ts is not None and now > self._last_ts:
            delta_t = now - self._last_ts
            delta_down = max(0, sum_recv - self._last_bytes['bytes_recv'])
            delta_up = max(0, sum_sent - self._last_bytes['bytes_sent'])
            # bytes to Mbps
            rate_down_mbps = (delta_down * 8.0) / (1_000_000.0 * delta_t)
            rate_up_mbps = (delta_up * 8.0) / (1_000_000.0 * delta_t)

        self._last_bytes['bytes_recv'] = sum_recv
        self._last_bytes['bytes_sent'] = sum_sent
        self._last_ts = now

        self._append_chart_points(rate_down_mbps, rate_up_mbps)
    
    @Slot(dict)
    def add_connection(self, conn):
        """Add a new connection to the connections table"""
        row = self.connections_table.rowCount()
        self.connections_table.insertRow(row)
        
        self.connections_table.setItem(row, 0, QTableWidgetItem(conn.get('protocol', '')))
        self.connections_table.setItem(row, 1, QTableWidgetItem(conn.get('local_addr', '')))
        self.connections_table.setItem(row, 2, QTableWidgetItem(conn.get('remote_addr', '')))
        
        status_item = QTableWidgetItem(conn.get('status', ''))
        if conn.get('status') == 'ESTABLISHED':
            status_item.setForeground(QBrush(QColor(0, 150, 0)))  # Green for established
        self.connections_table.setItem(row, 3, status_item)
        
        self.connections_table.setItem(row, 4, QTableWidgetItem(conn.get('process_name', '')))
        self.connections_table.setItem(row, 5, QTableWidgetItem(str(conn.get('pid', ''))))
        
        # Auto-scroll to bottom
        self.connections_table.scrollToBottom()
    
    @Slot(dict)
    def add_alert(self, alert):
        """Add a new security alert"""
        row = self.alerts_table.rowCount()
        self.alerts_table.insertRow(row)
        
        # Format time
        timestamp = datetime.fromisoformat(alert.get('timestamp', datetime.now().isoformat()))
        time_str = timestamp.strftime("%H:%M:%S")
        
        self.alerts_table.setItem(row, 0, QTableWidgetItem(time_str))
        
        # Severity with color coding
        severity = alert.get('severity', 'info').capitalize()
        severity_item = QTableWidgetItem(severity)
        
        if severity.lower() in ['high', 'critical']:
            severity_item.setForeground(QBrush(QColor(200, 0, 0)))  # Red
            severity_item.setFont(QFont("", weight=QFont.Bold))
        elif severity.lower() == 'medium':
            severity_item.setForeground(QBrush(QColor(200, 100, 0)))  # Orange
        else:
            severity_item.setForeground(QBrush(QColor(0, 100, 200)))  # Blue
        
        self.alerts_table.setItem(row, 1, severity_item)
        
        # Source and description
        source = alert.get('connection', {}).get('remote_addr', 'N/A')
        self.alerts_table.setItem(row, 2, QTableWidgetItem(source))
        self.alerts_table.setItem(row, 3, QTableWidgetItem(alert.get('description', 'No description')))
        
        # Update threat counter if this is a new threat
        if 'threat' in alert.get('description', '').lower():
            current = int(self.threats_blocked.text().split(':')[-1].strip())
            self.threats_blocked.setText(f"Threats Blocked: {current + 1}")
            self.last_threat.setText(f"Last Threat: {time_str}")
        
        # Auto-scroll to bottom
        self.alerts_table.scrollToBottom()
    
    @Slot(dict)
    def update_vpn_status(self, status):
        """Update VPN status display"""
        # Handle either {name: status} or plain status dict
        selected = self.vpn_selector.currentText().strip()
        sdict = status
        if isinstance(status, dict) and selected and selected in status:
            sdict = status[selected]
        if not isinstance(sdict, dict):
            return
        if sdict.get('connected', False):
            self.vpn_status.setText("Connected")
            self.vpn_status.setStyleSheet("font-weight: bold; color: green;")
            self.vpn_interface.setText(sdict.get('interface', sdict.get('config', {}).get('interface', 'N/A')))
            self.vpn_ip.setText(sdict.get('ip_address', 'N/A'))
            self.vpn_connect_btn.setEnabled(False)
            self.vpn_disconnect_btn.setEnabled(True)
        else:
            self.vpn_status.setText("Not Connected")
            self.vpn_status.setStyleSheet("font-weight: bold; color: red;")
            self.vpn_interface.setText("N/A")
            self.vpn_ip.setText("N/A")
            self.vpn_connect_btn.setEnabled(True)
            self.vpn_disconnect_btn.setEnabled(False)
    
    # UI control slots
    
    def refresh_connections(self):
        """Refresh the connections table"""
        if self.firewall:
            self.connections_table.setRowCount(0)  # Clear existing rows
            connections = self.firewall.get_network_connections()
            for conn in connections:
                self.add_connection(conn)
    
    def toggle_auto_refresh(self, state):
        """Toggle auto-refresh of connections"""
        if state == Qt.Checked:
            self.refresh_timer.start(5000)  # 5 seconds
        else:
            self.refresh_timer.stop()
    
    def connect_vpn(self):
        """Connect to VPN"""
        if self.firewall:
            name = self.vpn_selector.currentText().strip() or "default"
            self.firewall.connect_vpn(name)
    
    def disconnect_vpn(self):
        """Disconnect from VPN"""
        if self.firewall:
            name = self.vpn_selector.currentText().strip() or "default"
            self.firewall.disconnect_vpn(name)

    # ----- VPN controls helpers -----
    def refresh_vpn_list(self):
        if not self.firewall:
            return
        names = self.firewall.get_vpn_list() if hasattr(self.firewall, 'get_vpn_list') else []
        self.vpn_selector.blockSignals(True)
        self.vpn_selector.clear()
        self.vpn_selector.addItems(names or ["default"])
        self.vpn_selector.blockSignals(False)

    def on_vpn_selected(self, idx):
        self.load_split_tunneling()

    def toggle_kill_switch(self, checked):
        if not self.firewall:
            return
        name = self.vpn_selector.currentText().strip() or "default"
        self.firewall.set_kill_switch(name, bool(checked))

    def load_split_tunneling(self):
        if not self.firewall:
            return
        name = self.vpn_selector.currentText().strip() or "default"
        cfg = self.firewall.get_split_tunneling(name)
        mode = (cfg.get('mode') or 'exclude').lower()
        routes = cfg.get('routes') or []
        i = max(0, self.split_mode.findText(mode))
        self.split_mode.setCurrentIndex(i)
        self.split_routes_list.clear()
        for r in routes:
            self.split_routes_list.addItem(QListWidgetItem(r))

    def add_split_route(self):
        route = self.split_route_input.text().strip()
        if not route:
            return
        self.split_routes_list.addItem(QListWidgetItem(route))
        self.split_route_input.clear()

    def remove_selected_split_route(self):
        row = self.split_routes_list.currentRow()
        if row >= 0:
            self.split_routes_list.takeItem(row)

    def apply_split_tunneling(self):
        if not self.firewall:
            return
        name = self.vpn_selector.currentText().strip() or "default"
        mode = self.split_mode.currentText().lower()
        routes = [self.split_routes_list.item(i).text() for i in range(self.split_routes_list.count())]
        self.firewall.set_split_tunneling(name, mode, routes)

    # ----- Charts helpers -----
    def _on_interface_changed(self, idx):
        # Reset counters and clear series when switching interface
        self._last_bytes = {"bytes_recv": None, "bytes_sent": None}
        self._last_ts = None
        self._chart_time = 0
        self.series_down.clear()
        self.series_up.clear()
        # reset axes
        self.axis_x_down.setRange(0, self._chart_window)
        self.axis_x_up.setRange(0, self._chart_window)

    def _append_chart_points(self, down_mbps: float, up_mbps: float):
        self._chart_time += 1
        self.series_down.append(self._chart_time, down_mbps)
        self.series_up.append(self._chart_time, up_mbps)
        # Trim to window
        for series in (self.series_down, self.series_up):
            if series.count() > self._chart_window:
                series.removePoints(0, series.count() - self._chart_window)
        # Adjust X axis to keep window sliding
        if self._chart_time > self._chart_window:
            start = self._chart_time - self._chart_window
            end = self._chart_time
            self.axis_x_down.setRange(start, end)
            self.axis_x_up.setRange(start, end)

    # ----- Security management slots -----
    def refresh_security(self):
        """Refresh lists of blocked IPs and countries"""
        if not self.firewall:
            return
        # Blocked IPs
        self.blocked_ip_list.clear()
        for ip, until_ts in sorted(self.firewall.get_blocked_ips().items(), key=lambda x: x[0]):
            item = QListWidgetItem(f"{ip} (until {datetime.fromtimestamp(until_ts).strftime('%H:%M:%S')})")
            item.setData(Qt.ItemDataRole.UserRole, ip)
            self.blocked_ip_list.addItem(item)
        # Blocked countries
        self.blocked_country_list.clear()
        for cc in self.firewall.get_blocked_countries():
            item = QListWidgetItem(cc)
            item.setData(Qt.ItemDataRole.UserRole, cc)
            self.blocked_country_list.addItem(item)

    def block_ip(self):
        if not self.firewall:
            return
        ip = self.ip_input.text().strip()
        if not ip:
            return
        duration = int(self.ip_duration.value())
        if self.firewall.block_ip(ip, duration):
            self.ip_input.clear()
            self.refresh_security()

    def unblock_selected_ip(self):
        if not self.firewall:
            return
        item = self.blocked_ip_list.currentItem()
        if not item:
            return
        ip = item.data(Qt.ItemDataRole.UserRole)
        if self.firewall.unblock_ip(ip):
            self.refresh_security()

    def block_country(self):
        if not self.firewall:
            return
        cc = self.country_input.text().strip().upper()
        if len(cc) != 2:
            return
        if self.firewall.block_country(cc):
            self.country_input.clear()
            self.refresh_security()

    def unblock_selected_country(self):
        if not self.firewall:
            return
        item = self.blocked_country_list.currentItem()
        if not item:
            return
        cc = item.data(Qt.ItemDataRole.UserRole)
        if self.firewall.unblock_country(cc):
            self.refresh_security()


if __name__ == "__main__":
    # For testing the tab by itself
    import sys
    from PySide6.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    
    # Create a test tab with no firewall manager
    tab = MonitoringTab()
    tab.show()
    
    sys.exit(app.exec())
