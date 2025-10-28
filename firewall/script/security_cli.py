# firewall/scripts/security_cli.py
import argparse
import asyncio
from firewall.script.firewall_manager import FirewallManager

async def main():
    parser = argparse.ArgumentParser(description="Firewall Security CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)
    
    # Block country
    block_parser = subparsers.add_parser("block-country")
    block_parser.add_argument("country_code", help="2-letter country code to block")
    
    # Unblock country
    unblock_parser = subparsers.add_parser("unblock-country")
    unblock_parser.add_argument("country_code", help="2-letter country code to unblock")
    
    # Block IP
    block_ip_parser = subparsers.add_parser("block-ip")
    block_ip_parser.add_argument("ip", help="IP address to block")
    block_ip_parser.add_argument("--duration", type=int, default=3600, 
                               help="Duration to block in seconds")
    
    # Unblock IP
    unblock_ip_parser = subparsers.add_parser("unblock-ip")
    unblock_ip_parser.add_argument("ip", help="IP address to unblock")
    
    # List blocked countries
    subparsers.add_parser("list-blocked-countries")
    
    # List blocked IPs
    subparsers.add_parser("list-blocked-ips")
    
    args = parser.parse_args()
    
    # Initialize firewall manager
    fw = FirewallManager()
    
    if args.command == "block-country":
        fw.security.geo_blocker.block_country(args.country_code.upper())
        print(f"Blocked country: {args.country_code.upper()}")
    
    elif args.command == "unblock-country":
        fw.security.geo_blocker.unblock_country(args.country_code.upper())
        print(f"Unblocked country: {args.country_code.upper()}")
    
    elif args.command == "block-ip":
        fw.security.block_ip(args.ip, args.duration)
        print(f"Blocked IP {args.ip} for {args.duration} seconds")
    
    elif args.command == "unblock-ip":
        fw.security.unblock_ip(args.ip)
        print(f"Unblocked IP {args.ip}")
    
    elif args.command == "list-blocked-countries":
        print("Blocked countries:")
        for country in sorted(fw.security.geo_blocker.blocked_countries):
            print(f"  - {country}")
    
    elif args.command == "list-blocked-ips":
        print("Blocked IPs:")
        for ip, unblock_time in fw.security.blocked_ips.items():
            time_left = max(0, unblock_time - time.time())
            print(f"  - {ip} (unblocks in {int(time_left)}s)")

if __name__ == "__main__":
    asyncio.run(main())