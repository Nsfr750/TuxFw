# Security Policy

## Supported Versions

| Version | Supported          |
|--------:|:-------------------|
|  0.1.x  | :white_check_mark: |
| < 0.1.0 | :x:                |

## Enhanced Security (v0.1.0)

TuxFw includes optional security modules designed to detect and limit suspicious activity:

- **Rate Limiting**: Sliding-window requests per IP.
- **GeoIP Blocking**: Country-based blocking using MaxMind GeoLite2.
- **IP Reputation**: Threat-feed lookups (configurable feeds); periodic updates.
- **Port Knocking**: Simple sequence-based access control.

Components:

- `firewall/script/security_utils.py` – Core implementation of rate limiter, GeoIP, reputation, port knocking.
- `firewall/script/network_monitor.py` – Live connections feeding IDS/alerts.
- `firewall/script/firewall_manager.py` – Emits alerts/signals to the UI.

### Configuration

Security settings can be set in configuration (e.g., `config/configuration.json`), and/or by application defaults:

- Rate limits per endpoint (window and max requests)
- Blocked country codes
- Threat feed URLs and update intervals
- Port-knocking sequence and window

### Dependencies

- `geoip2`, `requests`, `aiohttp` (for GeoIP and threat feeds)
- GeoLite2 database file (Country), not bundled; user must provide path

### Privacy

- Threat feeds are fetched over HTTPS from configurable URLs.
- No telemetry is sent by TuxFw.

## VPN Enforcement

On Windows, TuxFw can enforce:

- **Kill Switch**: Block outbound traffic on non‑VPN interfaces.
- **Split Tunneling**: Include/Exclude destinations using Windows Firewall rules; per‑VPN persistence.

Notes:

- Requires Administrator privileges.
- WireGuard service control uses `wireguard.exe`; OpenVPN runs as a child process.
- Include‑mode may require additional route configuration for strict policy; TuxFw applies Windows Firewall rules and can optionally manage routes.

## Logging & Monitoring

- Security events and alerts are surfaced in the Monitoring → Dashboard.
- OpenVPN stdout can be streamed to the VPN log panel.
- Consider log retention/rotation policies suitable for your environment.

## Reporting a Vulnerability

Please report vulnerabilities via [GitHub Issues](https://github.com/Nsfr750/TuxFw/issues) or contact [Nsfr750](mailto:nsfr750@yandex.com). Do not include sensitive information in public issues.

## Security Updates

Security updates will be released as minor/patch versions (e.g., 0.1.1, 0.1.2). Always run the latest release.

## Security Disclosures

Public disclosures will be made through GitHub Security Advisories.
