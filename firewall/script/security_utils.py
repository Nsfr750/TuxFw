# firewall/script/security_utils.py
import ipaddress
import time
from collections import defaultdict, deque
from datetime import datetime, timedelta
try:  # pragma: no cover - optional dependency
    import requests
except ImportError:  # pragma: no cover - runtime fallback
    requests = None  # type: ignore
from typing import Dict, List, Optional, Set, Tuple
import json
import os
import logging
from dataclasses import dataclass, field
from enum import Enum

try:  # pragma: no cover - optional dependency
    import geoip2.database  # type: ignore
except ImportError:  # pragma: no cover - runtime fallback
    geoip2 = None  # type: ignore

logger = logging.getLogger("firewall.security")

class SecurityAction(Enum):
    ALLOW = "allow"
    BLOCK = "block"
    RATE_LIMIT = "rate_limit"
    GEO_BLOCK = "geo_block"
    REPUTATION_BLOCK = "reputation_block"

@dataclass
class RateLimitConfig:
    max_requests: int = 100  # Max requests
    time_window: int = 60    # Time window in seconds

class IPReputationChecker:
    def __init__(self, update_interval: int = 3600):
        self.threat_feeds = [
            "https://www.binarydefense.com/banlist.txt",
            "https://lists.blocklist.de/lists/ssh.txt",
            # Add more threat feeds as needed
        ]
        self.bad_ips: Set[str] = set()
        self.last_updated: Optional[datetime] = None
        self.update_interval = update_interval
        self.available = requests is not None

        if not self.available:
            logger.warning(
                "Requests library not installed. IP reputation updates will be disabled until requests is available."
            )
        
    async def update_threat_feeds(self):
        """Update the list of malicious IPs from threat feeds"""
        if not self.available:
            return

        current_time = datetime.utcnow()
        if (self.last_updated is None or 
            (current_time - self.last_updated).total_seconds() > self.update_interval):
            try:
                for feed in self.threat_feeds:
                    response = requests.get(feed, timeout=10)
                    if response.status_code == 200:
                        self.bad_ips.update(
                            line.strip() for line in response.text.splitlines() 
                            if line.strip() and not line.startswith('#')
                        )
                self.last_updated = current_time
                logger.info(f"Updated threat feeds with {len(self.bad_ips)} malicious IPs")
            except Exception as e:
                logger.error(f"Failed to update threat feeds: {e}")

    def is_malicious(self, ip: str) -> bool:
        """Check if an IP is in the malicious IP list"""
        return ip in self.bad_ips

class RateLimiter:
    def __init__(self, config: Optional[Dict[str, RateLimitConfig]] = None):
        self.config = config or {
            "default": RateLimitConfig()
        }
        self.requests: Dict[str, Dict[str, deque[float]]] = defaultdict(
            lambda: defaultdict(deque)
        )

    def is_rate_limited(self, ip: str, endpoint: str = "default") -> bool:
        """Check if an IP has exceeded the rate limit for a specific endpoint"""
        if endpoint not in self.config:
            endpoint = "default"
            
        config = self.config[endpoint]
        now = time.time()
        
        # Remove old requests outside the time window
        while (self.requests[ip][endpoint] and 
               now - self.requests[ip][endpoint][0] > config.time_window):
            self.requests[ip][endpoint].popleft()
        
        # Check if rate limit exceeded
        if len(self.requests[ip][endpoint]) >= config.max_requests:
            return True
            
        # Record this request
        self.requests[ip][endpoint].append(now)
        return False

class GeoIPBlocker:
    def __init__(self, geoip_db_path: str = None):
        self.geoip_db = None
        self.blocked_countries: Set[str] = set()
        self.available = geoip2 is not None

        if not self.available:
            logger.warning(
                "GeoIP2 library not installed. GeoIP blocking will be disabled until geoip2 is available."
            )
            return

        try:
            if geoip_db_path and os.path.exists(geoip_db_path):
                self.geoip_db = geoip2.database.Reader(geoip_db_path)  # type: ignore[attr-defined]
                logger.info("GeoIP database loaded successfully")
            else:
                logger.warning("GeoIP database path not provided or file missing. GeoIP blocking disabled.")
                self.available = False
        except Exception as e:
            logger.error(f"Failed to load GeoIP database: {e}")
            self.available = False

    def block_country(self, country_code: str):
        """Add a country to the block list"""
        self.blocked_countries.add(country_code.upper())

    def unblock_country(self, country_code: str):
        """Remove a country from the block list"""
        self.blocked_countries.discard(country_code.upper())

    def is_country_blocked(self, ip: str) -> bool:
        """Check if an IP belongs to a blocked country"""
        if not self.available or not self.geoip_db or not self.blocked_countries:
            return False
            
        try:
            response = self.geoip_db.country(ip)
            return response.country.iso_code.upper() in self.blocked_countries
        except Exception as e:
            logger.error(f"GeoIP lookup failed for {ip}: {e}")
            return False

class PortKnocking:
    def __init__(self, sequence: List[int] = None, window: int = 10):
        self.sequence = sequence or [1000, 2000, 3000]  # Default knock sequence
        self.window = window  # Time window in seconds for the knock sequence
        self.sequence_length = len(self.sequence)
        self.knock_attempts: Dict[str, List[Tuple[float, int]]] = {}
        
    def add_knock(self, ip: str, port: int) -> bool:
        """Record a port knock attempt"""
        now = time.time()
        
        # Clean up old knocks
        if ip in self.knock_attempts:
            self.knock_attempts[ip] = [
                (t, p) for t, p in self.knock_attempts[ip] 
                if now - t <= self.window
            ]
        
        # Add new knock
        if ip not in self.knock_attempts:
            self.knock_attempts[ip] = []
        self.knock_attempts[ip].append((now, port))
        
        # Check if sequence matches
        return self._check_sequence(ip)
    
    def _check_sequence(self, ip: str) -> bool:
        """Check if the knock sequence matches the required sequence"""
        if ip not in self.knock_attempts:
            return False
            
        ports = [p for _, p in self.knock_attempts[ip]]
        if len(ports) < self.sequence_length:
            return False
            
        # Check if the last N ports match our sequence
        return ports[-self.sequence_length:] == self.sequence

class EnhancedSecurity:
    def __init__(self, geoip_db_path: str = None):
        self.rate_limiter = RateLimiter()
        self.geo_blocker = GeoIPBlocker(geoip_db_path)
        self.ip_reputation = IPReputationChecker()
        self.port_knocking = PortKnocking()
        self.blocked_ips: Dict[str, float] = {}  # IP -> unblock_time
        
    async def check_security(self, ip: str, port: int = None) -> SecurityAction:
        """Check all security measures for an IP"""
        # Check if IP is temporarily blocked
        if ip in self.blocked_ips:
            if time.time() < self.blocked_ips[ip]:
                return SecurityAction.BLOCK
            del self.blocked_ips[ip]
        
        # Check rate limiting
        if self.rate_limiter.is_rate_limited(ip):
            self.blocked_ips[ip] = time.time() + 300  # Block for 5 minutes
            return SecurityAction.RATE_LIMIT
            
        # Check GeoIP blocking
        if self.geo_blocker.is_country_blocked(ip):
            return SecurityAction.GEO_BLOCK
            
        # Check IP reputation (async update if needed)
        await self.ip_reputation.update_threat_feeds()
        if self.ip_reputation.is_malicious(ip):
            return SecurityAction.REPUTATION_BLOCK
            
        # Check port knocking if port is provided
        if port and self.port_knocking.add_knock(ip, port):
            return SecurityAction.ALLOW
        elif port:  # If port was provided but knock sequence didn't match
            return SecurityAction.BLOCK
            
        return SecurityAction.ALLOW

    def block_ip(self, ip: str, duration: int = 3600):
        """Block an IP for the specified duration (in seconds)"""
        self.blocked_ips[ip] = time.time() + duration

    def unblock_ip(self, ip: str):
        """Unblock an IP"""
        self.blocked_ips.pop(ip, None)