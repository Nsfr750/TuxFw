#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import subprocess
import platform
from typing import List
from firewall.script.logger import get_logger

class WindowsFirewallController:
    """
    Manage Windows Firewall rules for VPN kill switch and split tunneling.
    Uses PowerShell NetSecurity cmdlets.
    """

    GROUP = "TuxFw VPN"

    def __init__(self):
        self.logger = get_logger("firewall.winfw")
        self.is_windows = platform.system().lower().startswith("win")

    def _run_ps(self, command: str) -> bool:
        if not self.is_windows:
            self.logger.warning("WindowsFirewallController used on non-Windows platform")
            return False
        try:
            completed = subprocess.run(
                ["powershell", "-NoProfile", "-NonInteractive", "-Command", command],
                capture_output=True,
                text=True,
                check=False,
            )
            if completed.returncode != 0:
                self.logger.error(f"PowerShell error ({completed.returncode}): {completed.stderr.strip()}")
                return False
            if completed.stdout.strip():
                self.logger.debug(completed.stdout.strip())
            return True
        except Exception as e:
            self.logger.error(f"PowerShell invocation failed: {e}")
            return False

    def _remove_group(self) -> None:
        cmd = (
            f"Get-NetFirewallRule -DisplayGroup '{self.GROUP}' | Remove-NetFirewallRule -Confirm:$false"
        )
        self._run_ps(cmd)

    def clear_group_rules(self) -> bool:
        return self._run_ps(
            f"Get-NetFirewallRule -DisplayGroup '{self.GROUP}' | Remove-NetFirewallRule -Confirm:$false"
        )

    # ---- Kill Switch ----
    def enable_kill_switch(self) -> bool:
        """
        Block all outbound on non-VPN interfaces (LAN/Wireless). Leaves RemoteAccess (VPN) allowed.
        """
        # Remove stale group rules first
        self._remove_group()
        # Block outbound on LAN
        block_lan = (
            "New-NetFirewallRule -DisplayName 'TuxFw_Kill_Block_LAN' "
            f"-DisplayGroup '{self.GROUP}' -Direction Outbound -Action Block -Profile Any "
            "-InterfaceType 'Lan' -Enabled True"
        )
        # Block outbound on Wireless
        block_wlan = (
            "New-NetFirewallRule -DisplayName 'TuxFw_Kill_Block_Wireless' "
            f"-DisplayGroup '{self.GROUP}' -Direction Outbound -Action Block -Profile Any "
            "-InterfaceType 'Wireless' -Enabled True"
        )
        ok1 = self._run_ps(block_lan)
        ok2 = self._run_ps(block_wlan)
        return ok1 and ok2

    def disable_kill_switch(self) -> bool:
        self._remove_group()
        return True

    # ---- Split Tunneling (Exclude mode recommended) ----
    def apply_split_tunneling_exclude(self, cidrs: List[str]) -> bool:
        """
        Exclude specific destinations from going via VPN by blocking them on RemoteAccess interface.
        Works with or without kill switch. If kill switch is enabled, those destinations won't go out at all
        unless additional routing/interface rules are set by the OS.
        """
        # Remove prior split entries
        self._run_ps(
            f"Get-NetFirewallRule -DisplayGroup '{self.GROUP}' | Where-Object {{$_.DisplayName -like 'TuxFw_Split_*'}} | Remove-NetFirewallRule -Confirm:$false"
        )
        ok_all = True
        for i, cidr in enumerate(cidrs or []):
            name = f"TuxFw_Split_Block_RemoteAccess_{i}"
            cmd = (
                f"New-NetFirewallRule -DisplayName '{name}' -DisplayGroup '{self.GROUP}' "
                "-Direction Outbound -Action Block -Profile Any -InterfaceType 'RemoteAccess' "
                f"-RemoteAddress '{cidr}' -Enabled True"
            )
            ok_all = self._run_ps(cmd) and ok_all
        return ok_all

    # ---- Route management (best-effort) ----
    def _get_interface_index(self, alias: str) -> int | None:
        cmd = (
            f"$if=(Get-NetIPInterface -InterfaceAlias '{alias}' -ErrorAction SilentlyContinue);"
            f"if($if){{$if.ifIndex}}"
        )
        if not self.is_windows:
            return None
        try:
            completed = subprocess.run(["powershell","-NoProfile","-NonInteractive","-Command", cmd], capture_output=True, text=True)
            if completed.returncode == 0 and completed.stdout.strip().isdigit():
                return int(completed.stdout.strip())
        except Exception:
            pass
        return None

    def clear_routes_for_interface(self, alias: str) -> bool:
        """Remove routes for a given interface alias that were likely added for split tunneling."""
        cmd = (
            f"Get-NetRoute -InterfaceAlias '{alias}' -ErrorAction SilentlyContinue | "
            f"Where-Object {{$_.RouteMetric -le 10}} | Remove-NetRoute -Confirm:$false"
        )
        return self._run_ps(cmd)

    def apply_routes_include(self, alias: str, cidrs: List[str]) -> bool:
        """Add routes for include-mode split tunneling bound to a specific interface alias."""
        if not cidrs:
            return True
        # First clear previously added low-metric routes
        self.clear_routes_for_interface(alias)
        ok_all = True
        for cidr in cidrs:
            # Best-effort: add route via interface alias with low metric
            cmd = (
                f"New-NetRoute -DestinationPrefix '{cidr}' -InterfaceAlias '{alias}' "
                f"-PolicyStore ActiveStore -RouteMetric 5 -ErrorAction SilentlyContinue"
            )
            ok_all = self._run_ps(cmd) and ok_all
        return ok_all

    def clear_split_tunneling(self) -> bool:
        return self._run_ps(
            f"Get-NetFirewallRule -DisplayGroup '{self.GROUP}' | Where-Object {{$_.DisplayName -like 'TuxFw_Split_*'}} | Remove-NetFirewallRule -Confirm:$false"
        )

    def apply_split_tunneling_include(self, cidrs: List[str]) -> bool:
        """
        Include-only: block ALL outbound on RemoteAccess, then allow only specified CIDRs via RemoteAccess.
        Note: Windows Firewall block generally overrides allow. Here we rely on rule order; we create an
        ALLOW rule set with higher priority by specifying -Action Allow and separate named rules, but in
        Windows Advanced Firewall, Block wins when policy conflicts. For practical purposes, include mode
        should be combined with route policy; here we approximate by first removing existing split rules,
        then adding a broad Block followed by Allow rules which can work depending on policy precedence.
        """
        # Remove old split rules
        self.clear_split_tunneling()
        ok_all = True
        # Broad block all on RemoteAccess
        block_all = (
            "New-NetFirewallRule -DisplayName 'TuxFw_Split_Block_RemoteAccess_All' "
            f"-DisplayGroup '{self.GROUP}' -Direction Outbound -Action Block -Profile Any "
            "-InterfaceType 'RemoteAccess' -Enabled True"
        )
        ok_all = self._run_ps(block_all) and ok_all
        # Allow specific CIDRs
        for i, cidr in enumerate(cidrs or []):
            name = f"TuxFw_Split_Allow_RemoteAccess_{i}"
            cmd = (
                f"New-NetFirewallRule -DisplayName '{name}' -DisplayGroup '{self.GROUP}' "
                "-Direction Outbound -Action Allow -Profile Any -InterfaceType 'RemoteAccess' "
                f"-RemoteAddress '{cidr}' -Enabled True"
            )
            ok_all = self._run_ps(cmd) and ok_all
        return ok_all
