#!/usr/bin/env python3
"""
LAB-004: Address Resolution Decision Model
===========================================

OFFLINE/THEORY model. No network transmission.

Given a local host with IPv4/CIDR, determine mathematically whether a
destination address is on the same subnet or requires a router.

This models the routing decision that determines what ARP actually asks for:
  - Same subnet → ARP for the destination's own MAC
  - Different subnet → ARP for the default gateway's MAC

Usage:
  python src/resolution_model.py
  python src/resolution_model.py 10.122.172.202/16
"""

import ipaddress
import sys
import struct
import socket


def same_subnet(local_cidr: str, destination_ip: str) -> bool:
    """
    Check if destination_ip is in the same subnet as local_cidr.

    This is the exact check a host uses to decide whether to ARP
    for the destination directly or for the gateway.
    """
    local_net = ipaddress.IPv4Network(local_cidr, strict=False)
    dest_addr = ipaddress.IPv4Address(destination_ip)
    return dest_addr in local_net


def model_resolution(local_cidr: str, local_ip: str, destinations: list[tuple[str, str]]) -> None:
    """
    Model the ARP resolution decision for each destination.

    destinations: list of (label, ip_address)
    """
    local_net = ipaddress.IPv4Network(local_cidr, strict=False)

    print("=" * 64)
    print("  LAB-004: Address Resolution Decision Model")
    print("  OFFLINE THEORY — No network transmission")
    print("=" * 64)
    print()
    print(f"  Local host:    {local_ip}")
    print(f"  CIDR prefix:   /{local_net.prefixlen}")
    print(f"  Network:       {local_net.network_address}")
    print(f"  Subnet mask:   {local_net.netmask}")
    print(f"  Broadcast:     {local_net.broadcast_address}")
    print()

    for label, dest in destinations:
        print("─" * 64)
        print(f"  Destination: {label} ({dest})")
        print("─" * 64)
        print()

        dest_addr = ipaddress.IPv4Address(dest)
        is_local = dest_addr in local_net

        if is_local:
            print(f"  ✓ {dest} IS inside {local_net.network_address}/{local_net.prefixlen}")
            print()
            print(f"  Decision: SAME SUBNET")
            print()
            print(f"  What happens:")
            print(f"    1. Host checks: is {dest} in my subnet? → YES")
            print(f"    2. Host sends ARP request for {dest} directly.")
            print(f"    3. ARP question: 'Who has {dest}? Tell {local_ip}'")
            print(f"    4. If {dest} is online, it replies with its MAC.")
            print(f"    5. Host can then send Ethernet frames directly to")
            print(f"       {dest}'s MAC address (Layer-2 delivery).")
            print()
            print(f"  Layer-2 target: MAC address of {dest} itself")
        else:
            print(f"  ✗ {dest} is NOT inside {local_net.network_address}/{local_net.prefixlen}")
            print()
            print(f"  Decision: OFF-SUBNET — requires router/gateway (PROTOCOL MODEL)")
            print()
            print(f"  What happens (conceptual — routing table NOT observed):")
            print(f"    1. Host checks: is {dest} in my subnet? → NO")
            print(f"    2. Host would look up default gateway in its routing table.")
            print(f"    3. Host would send ARP request for the GATEWAY's local IP.")
            print(f"    4. ARP question: 'Who has (gateway)? Tell {local_ip}'")
            print(f"    5. Gateway would reply with its MAC.")
            print(f"    6. Host encapsulates the IP packet (destined for {dest})")
            print(f"       inside an Ethernet frame addressed to the gateway's MAC.")
            print(f"    7. Gateway receives it, strips Ethernet header, sees the")
            print(f"       IP destination is {dest}, and routes it onward.")
            print()
            print(f"  Layer-2 target: MAC of the LOCAL NEXT-HOP (typically default gateway)")
            print(f"                   Actual gateway IP on this device: NOT VERIFIED")
            print(f"                   Actual gateway MAC on this device: NOT VERIFIED")
            print()
            print(f"  This is the PROTOCOL MODEL — what a correctly configured")
            print(f"  IPv4 host WOULD do. The actual routing table was not observed.")
            print()
            print(f"  IMPORTANT: The host does NOT ARP for {dest} directly.")
            print(f"  ARP operates only on the local link. {dest} is beyond it.")

        # Show the math
        print()
        dest_int = int(dest_addr)
        net_int = int(local_net.network_address)
        mask_int = int(local_net.netmask)

        dest_net_part = (dest_int & mask_int) >> (32 - local_net.prefixlen)
        local_net_part = (net_int & mask_int) >> (32 - local_net.prefixlen)

        print(f"  Mathematical check:")
        print(f"    Destination & Mask = {dest_int & mask_int:032b} = {ipaddress.IPv4Address(dest_int & mask_int)}")
        print(f"    Network    & Mask = {net_int & mask_int:032b} = {ipaddress.IPv4Address(net_int & mask_int)}")
        print(f"    Network prefix     = {net_int & mask_int:032b}"[:local_net.prefixlen])
        if is_local:
            print(f"    Match → SAME SUBNET")
        else:
            print(f"    Mismatch → DIFFERENT SUBNET")
        print()


def main() -> None:
    # Determine local CIDR
    if len(sys.argv) > 1:
        local_cidr = sys.argv[1]
    else:
        # Try auto-detect
        local_cidr = None
        try:
            import subprocess
            result = subprocess.run(
                ["ip", "addr", "show", "wlan0"],
                capture_output=True, text=True, timeout=3, check=False
            )
            if result.returncode == 0:
                import re
                for line in result.stdout.splitlines():
                    m = re.search(r"inet\s+([\d.]+)/(\d+)", line)
                    if m:
                        local_cidr = f"{m.group(1)}/{m.group(2)}"
                        break
        except (OSError, subprocess.SubprocessError):
            pass

        if not local_cidr:
            try:
                result = subprocess.run(
                    ["ifconfig", "wlan0"],
                    capture_output=True, text=True, timeout=3, check=False
                )
                import re
                m = re.search(r"inet\s+([\d.]+)\s+netmask\s+([\d.]+)", result.stdout)
                if m:
                    addr = m.group(1)
                    mask = m.group(2)
                    prefix = sum(bin(int(o)).count("1") for o in mask.split("."))
                    local_cidr = f"{addr}/{prefix}"
            except (OSError, subprocess.SubprocessError):
                pass

        if not local_cidr:
            # Method 3: ifconfig (no args) — parse wlan0 block
            try:
                result = subprocess.run(
                    ["ifconfig"],
                    capture_output=True, text=True, timeout=3, check=False
                )
                import re
                in_wlan0 = False
                for line in result.stdout.splitlines():
                    if line.startswith("wlan0"):
                        in_wlan0 = True
                    elif in_wlan0 and line.strip() and line[0] in (" ", "\t"):
                        m = re.search(r"inet\s+([\d.]+)\s+netmask\s+([\d.]+)", line)
                        if m:
                            addr = m.group(1)
                            mask = m.group(2)
                            prefix = sum(bin(int(o)).count("1") for o in mask.split("."))
                            local_cidr = f"{addr}/{prefix}"
                            break
                    elif in_wlan0 and not line.strip():
                        in_wlan0 = False
            except (OSError, subprocess.SubprocessError):
                pass

    if not local_cidr:
        # HISTORICAL fallback
        local_cidr = "10.122.172.202/16"
        print("WARNING: Could not auto-detect wlan0 address.")
        print(f"Using HISTORICAL value from LAB-001: {local_cidr}")
        print("This may NOT reflect the current network state.")
        print()

    # Parse
    net = ipaddress.IPv4Network(local_cidr, strict=False)
    local_ip = str(net.network_address + 0)
    # Actually we want the host address from the CIDR
    if "/" in local_cidr:
        local_ip = local_cidr.split("/")[0]
    else:
        local_ip = str(net.network_address)

    # Test destinations
    destinations = [
        ("Case A — inside subnet", "10.122.10.50"),
        ("Case B — outside subnet (Google DNS)", "8.8.8.8"),
    ]

    model_resolution(local_cidr, local_ip, destinations)

    # Bonus: explain why ARP is not needed for IPv6
    print("═" * 64)
    print("  Bonus: Why IPv6 Does Not Use ARP")
    print("═" * 64)
    print()
    print("  IPv6 replaces ARP with Neighbor Discovery Protocol (NDP),")
    print("  which is part of ICMPv6 (RFC 4861).")
    print()
    print("  Key differences:")
    print("    ARP (IPv4):  Standalone protocol, EtherType 0x0806")
    print("    NDP (IPv6):  Uses ICMPv6 messages over IPv6 (EtherType 0x86DD)")
    print()
    print("  Why the change?")
    print("    1. ARP uses broadcast → every host must process every ARP request.")
    print("       NDP uses multicast → only interested hosts receive queries.")
    print("    2. NDP combines multiple functions: address resolution, router")
    print("       discovery, prefix discovery, duplicate address detection.")
    print("    3. NDP can carry additional options (MTU, prefixes, routes).")
    print("    4. ARP is inherently IPv4-only (4-byte protocol addresses).")
    print("       NDP works with 128-bit IPv6 addresses natively.")
    print()
    print("  NDP message types for address resolution:")
    print("    Neighbor Solicitation (NS)   — 'Who has this IPv6 address?'")
    print("    Neighbor Advertisement (NA)  — 'I have this IPv6 address.'")
    print()
    print("  Conceptual similarity:")
    print("    ARP Request  ≈ NS (Neighbor Solicitation)")
    print("    ARP Reply    ≈ NA (Neighbor Advertisement)")
    print("  But NDP rides on top of IPv6, not as a separate EtherType.")
    print()

    print("=" * 64)
    print("  Resolution model complete.")
    print("=" * 64)


if __name__ == "__main__":
    main()
