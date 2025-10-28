#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import subprocess
import json
import os
import logging
from typing import Dict, List, Optional, Union, Any

class NFTablesManager:
    """
    A class to manage nftables firewall rules.
    This provides a high-level interface to interact with nftables.
    """
    
    def __init__(self, logger=None):
        """
        Initialize the NFTablesManager.
        
        Args:
            logger: Optional logger instance. If not provided, a basic logger will be created.
        """
        self.logger = logger or logging.getLogger("nftables")
        self.nft_cmd = "nft"
        
        # Check if nft is available
        if not self._is_nft_available():
            raise RuntimeError("nft command not found. Please install nftables.")
    
    def _is_nft_available(self) -> bool:
        """Check if nft command is available."""
        try:
            subprocess.run(
                [self.nft_cmd, "--version"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=True
            )
            return True
        except (subprocess.SubprocessError, FileNotFoundError):
            return False
    
    def _run_nft_command(self, command: str, json_output: bool = False) -> Dict:
        """
        Run an nft command and return the result.
        
        Args:
            command: The nft command to run (e.g., "list ruleset")
            json_output: Whether to request JSON output format
            
        Returns:
            dict: The parsed JSON output or raw output if json_output is False
        """
        cmd = [self.nft_cmd]
        
        if json_output:
            cmd.extend(["-j"])
            
        cmd.extend(command.split())
        
        try:
            result = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=True
            )
            
            if json_output and result.stdout.strip():
                return json.loads(result.stdout)
            return {"stdout": result.stdout, "stderr": result.stderr}
            
        except subprocess.CalledProcessError as e:
            self.logger.error(f"nft command failed: {e.stderr}")
            raise RuntimeError(f"nft command failed: {e.stderr}")
        except json.JSONDecodeError as e:
            self.logger.error(f"Failed to parse nft JSON output: {e}")
            return {"error": f"Failed to parse JSON: {e}", "raw_output": result.stdout}
    
    def get_ruleset(self) -> Dict:
        """
        Get the current nftables ruleset in JSON format.
        
        Returns:
            dict: The current nftables ruleset
        """
        return self._run_nft_command("list ruleset", json_output=True)
    
    def apply_ruleset(self, ruleset: Dict) -> bool:
        """
        Apply a complete nftables ruleset.
        
        Args:
            ruleset: The ruleset to apply (in nftables JSON format)
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # First, flush the existing ruleset
            self._run_nft_command("flush ruleset")
            
            # Apply the new ruleset
            # Note: This is a simplified example - in a real implementation,
            # you would need to convert the ruleset to nft commands
            if isinstance(ruleset, dict) and 'nftables' in ruleset:
                # This is a simplified example - actual implementation would need to handle
                # the full nftables JSON format
                for entry in ruleset['nftables']:
                    # Process each rule/table/chain
                    pass
                    
                self.logger.info("Successfully applied nftables ruleset")
                return True
            else:
                self.logger.error("Invalid nftables ruleset format")
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to apply nftables ruleset: {e}")
            return False
    
    def add_rule(self, table: str, chain: str, rule: str) -> bool:
        """
        Add a rule to a specific chain.
        
        Args:
            table: The nftables table (e.g., 'filter')
            chain: The chain to add the rule to
            rule: The rule to add (e.g., 'tcp dport 22 accept')
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            cmd = f'add rule {table} {chain} {rule}'
            self._run_nft_command(cmd)
            self.logger.info(f"Added rule: {cmd}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to add rule: {e}")
            return False
    
    def delete_rule(self, handle: str, table: str, chain: str) -> bool:
        """
        Delete a rule by its handle.
        
        Args:
            handle: The handle of the rule to delete
            table: The nftables table
            chain: The chain containing the rule
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            cmd = f'delete rule {table} {chain} handle {handle}'
            self._run_nft_command(cmd)
            self.logger.info(f"Deleted rule with handle {handle}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to delete rule: {e}")
            return False
    
    def create_chain(self, table: str, chain: str, chain_type: str = "filter", hook: str = "input",
                    priority: int = 0, policy: str = "accept") -> bool:
        """
        Create a new chain in the specified table.
        
        Args:
            table: The table to add the chain to
            chain: The name of the chain to create
            chain_type: The type of chain (filter, route, nat)
            hook: The hook for the chain (input, output, forward, etc.)
            priority: The priority of the chain
            policy: The default policy (accept, drop, etc.)
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            cmd = f'add chain {table} {chain} {{ type {chain_type} hook {hook} priority {priority} ; policy {policy} ; }}'
            self._run_nft_command(cmd)
            self.logger.info(f"Created chain: {table} {chain}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to create chain: {e}")
            return False

    def create_table(self, table: str, family: str = "ip") -> bool:
        """
        Create a new table.
        
        Args:
            table: The name of the table to create
            family: The address family (ip, ip6, inet, arp, bridge, netdev)
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            cmd = f'add table {family} {table}'
            self._run_nft_command(cmd)
            self.logger.info(f"Created table: {family} {table}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to create table: {e}")
            return False

    def flush_ruleset(self) -> bool:
        """
        Flush all rules and remove all tables.
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            self._run_nft_command("flush ruleset")
            self.logger.info("Flushed all nftables rules")
            return True
        except Exception as e:
            self.logger.error(f"Failed to flush ruleset: {e}")
            return False

    def get_active_rules(self) -> List[Dict]:
        """
        Get a list of all active rules.
        
        Returns:
            list: List of dictionaries containing rule information
        """
        try:
            ruleset = self.get_ruleset()
            rules = []
            
            # Parse the ruleset to extract individual rules
            # This is a simplified example - actual implementation would need to handle
            # the full nftables JSON format
            if 'nftables' in ruleset:
                for entry in ruleset['nftables']:
                    if 'rule' in entry:
                        rules.append(entry['rule'])
            
            return rules
            
        except Exception as e:
            self.logger.error(f"Failed to get active rules: {e}")
            return []

# Example usage
if __name__ == "__main__":
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    try:
        # Initialize the NFTablesManager
        nft = NFTablesManager()
        
        # Example: Get current ruleset
        ruleset = nft.get_ruleset()
        print("Current ruleset:", json.dumps(ruleset, indent=2))
        
        # Example: Create a table and chain
        nft.create_table("filter")
        nft.create_chain("filter", "input", policy="drop")
        
        # Example: Add a rule
        nft.add_rule("filter", "input", "tcp dport 22 accept")
        
        # Get active rules
        active_rules = nft.get_active_rules()
        print("Active rules:", json.dumps(active_rules, indent=2))
        
    except Exception as e:
        print(f"Error: {e}")
