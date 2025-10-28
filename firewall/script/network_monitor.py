#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import time
import threading
import psutil
import socket
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass
from datetime import datetime
from firewall.script.logger import get_logger

@dataclass
class NetworkStats:
    """Container for network statistics"""
    bytes_sent: int = 0
    bytes_recv: int = 0
    packets_sent: int = 0
    packets_recv: int = 0
    errors_in: int = 0
    errors_out: int = 0
    drop_in: int = 0
    drop_out: int = 0

@dataclass
class ConnectionInfo:
    """Information about a network connection"""
    local_addr: str
    remote_addr: str
    status: str
    pid: int
    process_name: str
    protocol: str
    timestamp: float

class NetworkMonitor:
    """
    Monitors network traffic and connections in real-time
    """
    def __init__(self, update_interval: float = 1.0):
        """
        Initialize the network monitor
        
        Args:
            update_interval: How often to update stats (in seconds)
        """
        self.logger = get_logger("firewall.netmon")
        self.update_interval = update_interval
        self._running = False
        self._thread = None
        self._callbacks = []
        self._prev_stats = {}
        self._current_connections = []
        self._lock = threading.Lock()
        
    def start(self):
        """Start the network monitoring thread"""
        if self._running:
            return
            
        self._running = True
        self._thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self._thread.start()
        self.logger.info("Network monitoring started")
        
    def stop(self):
        """Stop the network monitoring thread"""
        self._running = False
        if self._thread:
            self._thread.join()
            self._thread = None
        self.logger.info("Network monitoring stopped")
        
    def register_callback(self, callback: Callable[[Dict, List[ConnectionInfo]], None]):
        """
        Register a callback to receive network updates
        
        Args:
            callback: Function that receives (stats, connections) as arguments
        """
        with self._lock:
            self._callbacks.append(callback)
            
    def _monitor_loop(self):
        """Main monitoring loop"""
        while self._running:
            try:
                # Get current network stats
                net_io = psutil.net_io_counters(pernic=True)
                net_conns = psutil.net_connections(kind='inet')
                
                # Calculate deltas
                current_time = time.time()
                stats = {}
                
                for nic, io in net_io.items():
                    prev = self._prev_stats.get(nic, {})
                    
                    stats[nic] = NetworkStats(
                        bytes_sent=io.bytes_sent,
                        bytes_recv=io.bytes_recv,
                        packets_sent=io.packets_sent,
                        packets_recv=io.packets_recv,
                        errors_in=io.errin,
                        errors_out=io.errout,
                        drop_in=io.dropin,
                        drop_out=io.dropout
                    )
                    
                # Update previous stats (store raw psutil counters for potential future delta calc)
                self._prev_stats = {nic: net_io[nic] for nic in net_io}
                
                # Process connections
                connections = []
                for conn in net_conns:
                    try:
                        local = f"{conn.laddr.ip}:{conn.laddr.port}" if conn.laddr else None
                        remote = f"{conn.raddr.ip}:{conn.raddr.port}" if conn.raddr else None
                        
                        if local or remote:  # Only include valid connections
                            connections.append(ConnectionInfo(
                                local_addr=local or "",
                                remote_addr=remote or "",
                                status=conn.status,
                                pid=conn.pid or 0,
                                process_name=psutil.Process(conn.pid).name() if conn.pid else "",
                                protocol=conn.type.name.lower(),
                                timestamp=current_time
                            ))
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        continue
                        
                # Update current connections
                with self._lock:
                    self._current_connections = connections
                
                # Notify callbacks
                for callback in self._callbacks:
                    try:
                        callback(stats, connections)
                    except Exception as e:
                        self.logger.error(f"Error in network monitor callback: {e}")
                
            except Exception as e:
                self.logger.error(f"Error in network monitor: {e}")
                
            # Wait for next update
            time.sleep(self.update_interval)
    
    def get_current_connections(self) -> List[ConnectionInfo]:
        """Get the current list of network connections"""
        with self._lock:
            return self._current_connections.copy()


class IntrusionDetectionSystem:
    """
    Basic Intrusion Detection System (IDS) for network traffic monitoring
    """
    def __init__(self):
        self.logger = get_logger("firewall.ids")
        self.rules = []
        self._load_default_rules()
        
    def _load_default_rules(self):
        """Load default IDS rules"""
        self.rules = [
            {
                "id": "port_scan_detection",
                "name": "Port Scan Detection",
                "description": "Detects potential port scanning activity",
                "severity": "high",
                "enabled": True
            },
            {
                "id": "brute_force_attempt",
                "name": "Brute Force Attempt",
                "description": "Detects multiple failed login attempts",
                "severity": "high",
                "enabled": True
            },
            {
                "id": "suspicious_connection",
                "name": "Suspicious Connection",
                "description": "Detects connections to known malicious IPs",
                "severity": "medium",
                "enabled": True
            }
        ]
    
    def analyze_connection(self, conn: ConnectionInfo) -> List[dict]:
        """
        Analyze a network connection for potential threats
        
        Args:
            conn: Connection to analyze
            
        Returns:
            List of detected threats (empty if none)
        """
        threats = []
        
        # Check for suspicious ports
        if conn.remote_addr and ":" in conn.remote_addr:
            _, port = conn.remote_addr.rsplit(":", 1)
            port = int(port)
            
            # Common suspicious ports
            suspicious_ports = {
                22: "SSH (potential brute force target)",
                23: "Telnet (insecure protocol)",
                80: "HTTP (potential web attack)",
                443: "HTTPS (potential web attack)",
                3389: "RDP (potential brute force target)",
                5900: "VNC (potential unauthorized access)",
            }
            
            if port in suspicious_ports and port not in [80, 443]:  # Common ports are less suspicious
                threats.append({
                    "rule_id": "suspicious_port",
                    "severity": "medium",
                    "description": f"Connection to potentially sensitive port {port} ({suspicious_ports[port]})",
                    "connection": conn
                })
        
        # Add more detection logic here
        
        return threats
    
    def get_rules(self) -> List[dict]:
        """Get all IDS rules"""
        return self.rules
    
    def update_rule(self, rule_id: str, enabled: bool) -> bool:
        """
        Enable or disable an IDS rule
        
        Args:
            rule_id: ID of the rule to update
            enabled: Whether to enable or disable the rule
            
        Returns:
            bool: True if rule was updated, False if not found
        """
        for rule in self.rules:
            if rule["id"] == rule_id:
                rule["enabled"] = enabled
                self.logger.info(f"Updated rule {rule_id}: enabled={enabled}")
                return True
        return False
