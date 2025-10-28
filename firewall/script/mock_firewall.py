#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
from typing import Dict, List, Optional, Any, Tuple

class MockFirewall:
    """
    A mock firewall implementation for development and testing.
    This provides the same interface as NFTablesManager but doesn't require nftables.
    """
    
    def __init__(self, logger=None):
        self.logger = logger or logging.getLogger("mock_firewall")
        self.rules = []
        self.logger.info("Initialized MockFirewall for development")
    
    def _run_command(self, command: str, json_output: bool = False) -> Dict:
        """Mock implementation of command execution"""
        self.logger.debug(f"Mock command: {command}")
        return {"status": "success", "message": "Mock command executed"}
    
    def get_ruleset(self) -> Dict:
        """Get the current mock ruleset"""
        return {"nftables": [{"rule": rule} for rule in self.rules]}
    
    def add_rule(self, table: str, chain: str, rule: str) -> bool:
        """Add a mock rule"""
        rule_obj = {
            "table": table,
            "chain": chain,
            "rule": rule,
            "handle": len(self.rules) + 1
        }
        self.rules.append(rule_obj)
        self.logger.info(f"Added mock rule: {rule_obj}")
        return True
    
    def delete_rule(self, handle: str, table: str, chain: str) -> bool:
        """Delete a mock rule"""
        try:
            handle_int = int(handle)
            self.rules = [r for r in self.rules if r.get('handle') != handle_int]
            self.logger.info(f"Deleted mock rule with handle {handle}")
            return True
        except (ValueError, TypeError):
            self.logger.error(f"Invalid handle: {handle}")
            return False
    
    def flush_ruleset(self) -> bool:
        """Flush all mock rules"""
        self.rules = []
        self.logger.info("Flushed all mock rules")
        return True
    
    def get_rules(self) -> List[Dict]:
        """Get all mock rules"""
        return self.rules.copy()
    
    def __getattr__(self, name):
        """Forward any unimplemented methods to a no-op"""
        def method(*args, **kwargs):
            self.logger.warning(f"Called unimplemented method: {name} with args: {args}, kwargs: {kwargs}")
            return {"status": "success", "message": f"Mock {name} called"}
        return method
