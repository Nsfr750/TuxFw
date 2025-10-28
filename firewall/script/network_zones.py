#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json
import ipaddress
import subprocess
import platform
import shutil
from typing import Dict, List, Optional, Set, Tuple
from dataclasses import dataclass
from pathlib import Path
from firewall.script.logger import get_logger

@dataclass
class NetworkZone:
    """Represents a network zone with its properties"""
    name: str
    description: str
    networks: List[str]  # List of CIDR notation networks
    interfaces: List[str]  # Network interface names
    is_vpn: bool = False
    vpn_config: Optional[dict] = None
    tags: List[str] = None
    
    def __post_init__(self):
        self.tags = self.tags or []
        if self.is_vpn and not self.vpn_config:
            self.vpn_config = {}

class ZoneManager:
    """Manages network zones and their configurations"""
    
    def __init__(self, config_dir: str = None):
        """
        Initialize the ZoneManager
        
        Args:
            config_dir: Directory to store zone configurations
        """
        self.logger = get_logger("firewall.zones")
        self.config_dir = config_dir or os.path.join("config", "zones")
        self.zones: Dict[str, NetworkZone] = {}
        self._load_zones()
        
    def _load_zones(self):
        """Load zones from configuration directory"""
        try:
            os.makedirs(self.config_dir, exist_ok=True)
            
            # Load default zones if no config exists
            if not os.listdir(self.config_dir):
                self._create_default_zones()
                return
                
            # Load zones from config files
            for file in Path(self.config_dir).glob("*.json"):
                try:
                    with open(file, 'r') as f:
                        data = json.load(f)
                        zone = NetworkZone(**data)
                        self.zones[zone.name.lower()] = zone
                except Exception as e:
                    self.logger.error(f"Error loading zone from {file}: {e}")
                    
        except Exception as e:
            self.logger.error(f"Error initializing zone manager: {e}")
            raise
    
    def _create_default_zones(self):
        """Create default network zones"""
        default_zones = [
            {
                "name": "LAN",
                "description": "Local Area Network",
                "networks": ["192.168.0.0/16", "10.0.0.0/8", "172.16.0.0/12"],
                "interfaces": ["eth0", "wlan0"],
                "is_vpn": False,
                "tags": ["trusted"]
            },
            {
                "name": "WAN",
                "description": "Wide Area Network (Internet)",
                "networks": ["0.0.0.0/0"],
                "interfaces": ["ppp0", "ppp1"],
                "is_vpn": False,
                "tags": ["untrusted"]
            },
            {
                "name": "DMZ",
                "description": "Demilitarized Zone",
                "networks": [],
                "interfaces": ["dmz0"],
                "is_vpn": False,
                "tags": ["semi-trusted"]
            }
        ]
        
        for zone_data in default_zones:
            zone = NetworkZone(**zone_data)
            self.zones[zone.name.lower()] = zone
            self.save_zone(zone)
    
    def save_zone(self, zone: NetworkZone) -> bool:
        """
        Save a zone to disk
        
        Args:
            zone: The zone to save
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            os.makedirs(self.config_dir, exist_ok=True)
            zone_file = os.path.join(self.config_dir, f"{zone.name.lower()}.json")
            
            with open(zone_file, 'w') as f:
                zone_data = {
                    "name": zone.name,
                    "description": zone.description,
                    "networks": zone.networks,
                    "interfaces": zone.interfaces,
                    "is_vpn": zone.is_vpn,
                    "vpn_config": zone.vpn_config or {},
                    "tags": zone.tags
                }
                json.dump(zone_data, f, indent=2)
                
            # Attach log sink if supported
            try:
                sink = lambda line, _n=name: self._emit_log(_n, line)
                if hasattr(self.vpn_clients[name], 'set_log_sink'):
                    self.vpn_clients[name].set_log_sink(sink)
            except Exception:
                pass
            return True
            
        except Exception as e:
            self.logger.error(f"Error saving zone {zone.name}: {e}")
            return False
    
    def get_zone(self, name: str) -> Optional[NetworkZone]:
        """Get a zone by name"""
        return self.zones.get(name.lower())
    
    def get_all_zones(self) -> List[NetworkZone]:
        """Get all configured zones"""
        return list(self.zones.values())
    
    def add_zone(self, zone: NetworkZone) -> bool:
        """
        Add a new zone
        
        Args:
            zone: The zone to add
            
        Returns:
            bool: True if added successfully, False if zone already exists
        """
        if zone.name.lower() in self.zones:
            return False
            
        self.zones[zone.name.lower()] = zone
        return self.save_zone(zone)
    
    def update_zone(self, name: str, **kwargs) -> bool:
        """
        Update an existing zone
        
        Args:
            name: Name of the zone to update
            **kwargs: Zone properties to update
            
        Returns:
            bool: True if updated successfully, False if zone not found
        """
        zone = self.get_zone(name)
        if not zone:
            return False
            
        for key, value in kwargs.items():
            if hasattr(zone, key):
                setattr(zone, key, value)
                
        return self.save_zone(zone)
    
    def delete_zone(self, name: str) -> bool:
        """
        Delete a zone
        
        Args:
            name: Name of the zone to delete
            
        Returns:
            bool: True if deleted successfully, False otherwise
        """
        zone = self.get_zone(name)
        if not zone:
            return False
            
        try:
            zone_file = os.path.join(self.config_dir, f"{name.lower()}.json")
            if os.path.exists(zone_file):
                os.remove(zone_file)
                
            del self.zones[name.lower()]
            return True
            
        except Exception as e:
            self.logger.error(f"Error deleting zone {name}: {e}")
            return False
    
    def find_zone_for_ip(self, ip: str) -> Optional[NetworkZone]:
        """
        Find which zone an IP address belongs to
        
        Args:
            ip: IP address to check
            
        Returns:
            NetworkZone or None if no matching zone found
        """
        try:
            ip_obj = ipaddress.ip_address(ip)
            
            for zone in self.zones.values():
                for network in zone.networks:
                    try:
                        if ip_obj in ipaddress.ip_network(network, strict=False):
                            return zone
                    except ValueError:
                        continue
                        
        except ValueError:
            pass
            
        return None


class VPNAPI:
    """Base class for VPN integration"""
    
    def __init__(self, config: dict = None):
        self.config = config or {}
        self.logger = get_logger("firewall.vpn")
        self.connected = False
    
    def connect(self) -> bool:
        """Establish VPN connection"""
        raise NotImplementedError
    
    def disconnect(self) -> bool:
        """Terminate VPN connection"""
        raise NotImplementedError
    
    def get_status(self) -> dict:
        """Get current VPN status"""
        raise NotImplementedError
    
    def get_config(self) -> dict:
        """Get current VPN configuration"""
        return self.config
    
    def update_config(self, config: dict) -> bool:
        """Update VPN configuration"""
        self.config.update(config)
        return True


class OpenVPNClient(VPNAPI):
    """OpenVPN client implementation"""
    
    def __init__(self, config: dict = None):
        super().__init__(config)
        self.process: Optional[subprocess.Popen] = None
        self.exe = self.config.get("exe", "openvpn")
        self.config_path = self.config.get("config_path")  # .ovpn
        self.args: List[str] = list(self.config.get("args", []))
        # Windows-specific process flags
        self._creationflags = 0x08000000 if platform.system().lower().startswith("win") else 0
        # Logging
        self._log_sink = None
        self._reader_thread = None
        self._stop_read = False

    def set_log_sink(self, sink):
        self._log_sink = sink
    
    def connect(self) -> bool:
        try:
            if self.connected and self.process and self.process.poll() is None:
                self.logger.info("OpenVPN already connected")
                return True

            if not shutil.which(self.exe):
                self.logger.error(f"OpenVPN executable not found: {self.exe}")
                return False

            cmd: List[str] = [self.exe]
            if self.args:
                cmd += self.args
            elif self.config_path:
                cmd += ["--config", self.config_path]
            else:
                self.logger.error("OpenVPN requires either args or config_path in configuration")
                return False

            self.logger.info(f"Starting OpenVPN: {' '.join(cmd)}")
            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                creationflags=self._creationflags,
                text=True,
            )
            # Start reader thread to stream stdout
            if self.process.stdout is not None and self._log_sink is not None:
                self._stop_read = False
                import threading
                def _reader():
                    try:
                        for line in self.process.stdout:
                            if self._stop_read:
                                break
                            try:
                                self._log_sink(line.rstrip())
                            except Exception:
                                pass
                    except Exception:
                        pass
                self._reader_thread = threading.Thread(target=_reader, daemon=True)
                self._reader_thread.start()
            self.connected = True
            return True
        except Exception as e:
            self.logger.error(f"OpenVPN connection failed: {e}")
            self.connected = False
            return False
    
    def disconnect(self) -> bool:
        try:
            if self.process and self.process.poll() is None:
                self.logger.info("Terminating OpenVPN process...")
                self.process.terminate()
                try:
                    self.process.wait(timeout=10)
                except Exception:
                    self.process.kill()
            # Stop reader
            self._stop_read = True
            if self._reader_thread and self._reader_thread.is_alive():
                try:
                    self._reader_thread.join(timeout=2)
                except Exception:
                    pass
            self.connected = False
            return True
        except Exception as e:
            self.logger.error(f"Error disconnecting from OpenVPN: {e}")
            return False
    
    def get_status(self) -> dict:
        # Best-effort check process
        if self.process and self.process.poll() is not None:
            self.connected = False
        return {
            "connected": self.connected,
            "protocol": "OpenVPN",
            "config": self.config,
        }


class WireGuardClient(VPNAPI):
    """WireGuard client implementation (stub)."""
    
    def __init__(self, config: dict = None):
        super().__init__(config)
        self.interface = self.config.get("interface", "wg0")
        self.exe = self.config.get("exe", "wireguard")  # wireguard.exe CLI on Windows
        self.exec_args: List[str] = list(self.config.get("args", []))  # optional direct args mode
        self.config_path = self.config.get("config_path")  # .conf
        self.name = self.config.get("name") or (Path(self.config_path).stem if self.config_path else "wg0")
        self.mode = self.config.get("mode", "service").lower()  # 'service' or 'exec'
        self._creationflags = 0x08000000 if platform.system().lower().startswith("win") else 0
    
    def connect(self) -> bool:
        try:
            if self.connected:
                self.logger.info("WireGuard already connected")
                return True

            if self.exec_args:
                # Run provided command directly
                if not shutil.which(self.exe):
                    self.logger.error(f"WireGuard executable not found: {self.exe}")
                    return False
                cmd = [self.exe] + self.exec_args
                self.logger.info(f"Starting WireGuard (exec args): {' '.join(cmd)}")
                p = subprocess.run(cmd, capture_output=True, text=True, creationflags=self._creationflags)
                if p.returncode != 0:
                    self.logger.error(f"WireGuard failed: {p.stderr.strip()}")
                    return False
                self.connected = True
                return True

            # Default Windows service approach
            if not shutil.which(self.exe):
                self.logger.error(f"WireGuard CLI not found: {self.exe}")
                return False
            if not self.config_path or not os.path.exists(self.config_path):
                self.logger.error("WireGuard requires config_path for service mode")
                return False
            cmd = [self.exe, "/installtunnelservice", self.config_path]
            self.logger.info(f"Installing WireGuard tunnel service: {' '.join(cmd)}")
            p = subprocess.run(cmd, capture_output=True, text=True, creationflags=self._creationflags)
            if p.returncode != 0:
                self.logger.error(f"WireGuard install failed: {p.stderr.strip()}")
                return False
            self.connected = True
            return True
        except Exception as e:
            self.logger.error(f"WireGuard connection failed: {e}")
            self.connected = False
            return False
    
    def disconnect(self) -> bool:
        try:
            if not self.connected:
                return True

            if self.exec_args:
                # No-op: assume external command controls teardown
                self.connected = False
                return True

            if not shutil.which(self.exe):
                self.connected = False
                return True
            # Uninstall service by name; if name not provided, try from config_path stem
            tunnel_name = self.name
            cmd = [self.exe, "/uninstalltunnelservice", tunnel_name]
            self.logger.info(f"Uninstalling WireGuard tunnel service: {' '.join(cmd)}")
            p = subprocess.run(cmd, capture_output=True, text=True, creationflags=self._creationflags)
            if p.returncode != 0:
                self.logger.error(f"WireGuard uninstall failed: {p.stderr.strip()}")
                # Still mark disconnected to avoid stuck state
            self.connected = False
            return True
        except Exception as e:
            self.logger.error(f"Error disconnecting WireGuard: {e}")
            return False
    
    def get_status(self) -> dict:
        return {
            "connected": self.connected,
            "protocol": "WireGuard",
            "interface": self.interface,
            "config": self.config,
        }

class VPNManager:
    """Manages VPN connections and configurations"""
    
    def __init__(self, zone_manager: ZoneManager = None):
        self.logger = get_logger("firewall.vpn.manager")
        self.zone_manager = zone_manager or ZoneManager()
        self.vpn_clients = {}
        self._status_callbacks = []
        self._log_callbacks = []
        # Simple state for security features
        self._kill_switch: set[str] = set()  # VPN names with kill switch on
        self._split_tunnel: dict[str, dict] = {}  # name -> {mode: 'include'|'exclude', routes: [cidr]}
        self._load_vpn_configs()
    
    def _load_vpn_configs(self):
        """Load VPN configurations from zones"""
        for zone in self.zone_manager.get_all_zones():
            if zone.is_vpn and zone.vpn_config:
                self._init_vpn_client(zone.name, zone.vpn_config)
    
    def _init_vpn_client(self, name: str, config: dict) -> bool:
        """Initialize a VPN client"""
        try:
            vpn_type = config.get("type", "openvpn").lower()
            
            if vpn_type == "openvpn":
                self.vpn_clients[name] = OpenVPNClient(config)
            elif vpn_type == "wireguard":
                self.vpn_clients[name] = WireGuardClient(config)
            else:
                self.logger.warning(f"Unsupported VPN type: {vpn_type}")
                return False
                
            return True
            
        except Exception as e:
            self.logger.error(f"Error initializing VPN client {name}: {e}")
            return False
    
    def connect_vpn(self, name: str) -> bool:
        """Connect to a VPN"""
        if name not in self.vpn_clients:
            self.logger.error(f"No VPN configuration found for {name}")
            return False
            
        ok = self.vpn_clients[name].connect()
        if ok:
            self._emit_status(name)
        return ok
    
    def disconnect_vpn(self, name: str) -> bool:
        """Disconnect from a VPN"""
        if name not in self.vpn_clients:
            self.logger.error(f"No active VPN connection found for {name}")
            return False
            
        ok = self.vpn_clients[name].disconnect()
        if ok:
            self._emit_status(name)
        return ok
    
    def get_vpn_status(self, name: str = None) -> dict:
        """Get VPN status"""
        if name:
            if name not in self.vpn_clients:
                return {"error": f"No VPN configuration found for {name}"}
            return self.vpn_clients[name].get_status()
        
        # Return status for all VPNs
        return {name: client.get_status() for name, client in self.vpn_clients.items()}

    # ---- Status callbacks for UI integration ----
    def register_status_callback(self, cb):
        if cb not in self._status_callbacks:
            self._status_callbacks.append(cb)

    def _emit_status(self, name: str):
        status = self.get_vpn_status(name)
        for cb in list(self._status_callbacks):
            try:
                cb({name: status} if isinstance(status, dict) else status)
            except Exception as e:
                self.logger.error(f"VPN status callback error: {e}")

    # ---- Log callbacks ----
    def register_log_callback(self, cb):
        if cb not in self._log_callbacks:
            self._log_callbacks.append(cb)

    def _emit_log(self, name: str, line: str):
        payload = {"name": name, "line": line}
        for cb in list(self._log_callbacks):
            try:
                cb(payload)
            except Exception as e:
                self.logger.error(f"VPN log callback error: {e}")

    # ---- Kill switch (logical state; nftables handled by FirewallManager) ----
    def enable_kill_switch(self, name: str) -> bool:
        self._kill_switch.add(name)
        self._emit_status(name)
        return True

    def disable_kill_switch(self, name: str) -> bool:
        self._kill_switch.discard(name)
        self._emit_status(name)
        return True

    def is_kill_switch_enabled(self, name: str) -> bool:
        return name in self._kill_switch

    # ---- Split tunneling (store policy only; enforcement external) ----
    def set_split_tunneling(self, name: str, mode: str, routes: list[str]) -> bool:
        mode = mode.lower().strip()
        if mode not in ("include", "exclude"):
            self.logger.error("Split tunneling mode must be 'include' or 'exclude'")
            return False
        self._split_tunnel[name] = {"mode": mode, "routes": routes or []}
        # Persist to zone config if zone exists
        try:
            zone = self.zone_manager.get_zone(name)
            if zone:
                zcfg = zone.vpn_config or {}
                zcfg['split_tunneling'] = {"mode": mode, "routes": routes or []}
                zone.vpn_config = zcfg
                self.zone_manager.save_zone(zone)
        except Exception as e:
            self.logger.error(f"Failed saving split tunneling to zone {name}: {e}")
        self._emit_status(name)
        return True

    def get_split_tunneling(self, name: str) -> dict:
        # Prefer in-memory; fall back to zone config
        cfg = self._split_tunnel.get(name)
        if cfg:
            return cfg
        try:
            zone = self.zone_manager.get_zone(name)
            if zone and zone.vpn_config and 'split_tunneling' in zone.vpn_config:
                return zone.vpn_config['split_tunneling']
        except Exception:
            pass
        return {"mode": "exclude", "routes": []}
    
    def add_vpn_zone(self, name: str, config: dict) -> bool:
        """
        Add a new VPN zone
        
        Args:
            name: Name of the zone
            config: VPN configuration
            
        Returns:
            bool: True if added successfully, False otherwise
        """
        # Create or update zone
        zone = self.zone_manager.get_zone(name)
        if zone:
            zone.is_vpn = True
            zone.vpn_config = config
        else:
            zone = NetworkZone(
                name=name,
                description=config.get("description", "VPN Zone"),
                networks=config.get("networks", []),
                interfaces=config.get("interfaces", []),
                is_vpn=True,
                vpn_config=config,
                tags=["vpn"]
            )
        
        # Save zone and initialize VPN client
        if self.zone_manager.save_zone(zone):
            return self._init_vpn_client(name, config)
            
        return False
