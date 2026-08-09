#!/usr/bin/env python3
"""
LAB-004: Subnet Mathematics
============================

Given an IPv4 address with CIDR prefix length, calculate:

- subnet mask
- network address
- broadcast address
- binary decomposition showing which bits are network vs host

Uses only `ipaddress` from the Python standard library.

Usage:
  python src/subnet_math.py                          # auto-detect or historical
  python src/subnet_math.py 10.122.172.202/16        # explicit input
  python src/subnet_math.py 192.168.1.50/24          # any IPv4/CIDR
"""

import ipaddress
import sys
import socket
import struct
import subprocess


def binary_str(ip_int: int, is_v4: bool = True) -> str:
    """Format an IP integer as 8-bit-grouped binary string."""
    if is_v4:
        octets = [(ip_int >> shift) & 0xFF for shift in (24, 16, 8, 0)]
        return " ".join(f"{o:08b}" for o in octets)
    return bin(ip_int)


def get_wlan0_ip() -> tuple[str, int] | None:
    """
    Try to determine the current wlan0 IPv4 and prefix length.

    Returns (address, prefixlen) or None if unavailable.
    """
    # Method 1: ip addr show wlan0 (if iproute2 is present)
    try:
        result = subprocess.run(
            ["ip", "addr", "show", "wlan0"],
            capture_output=True, text=True, timeout=3, check=False
        )
        if result.returncode == 0:
            import re
            for line in result.stdout.splitlines():
                m = re.search(r"inet\s+([\d.]+)/(\d+)", line)
                if m:
                    return (m.group(1), int(m.group(2)))
    except (OSError, subprocess.SubprocessError):
        pass

    # Method 2: ifconfig wlan0
    try:
        result = subprocess.run(
            ["ifconfig", "wlan0"],
            capture_output=True, text=True, timeout=3, check=False
        )
        import re
        for line in result.stdout.splitlines():
            m = re.search(r"inet\s+([\d.]+)\s+netmask\s+([\d.]+)", line)
            if m:
                addr = m.group(1)
                mask = m.group(2)
                prefix = sum(bin(int(o)).count("1") for o in mask.split("."))
                return (addr, prefix)
    except (OSError, subprocess.SubprocessError):
        pass

    # Method 3: ifconfig (no args) — parse wlan0 block
    # On Android, ifconfig wlan0 may fail due to /proc/net/dev restrictions
    # while ifconfig alone succeeds.
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
                    return (addr, prefix)
            elif in_wlan0 and not line.strip():
                in_wlan0 = False
    except (OSError, subprocess.SubprocessError):
        pass

    return None


def calculate(ip_str: str, prefix: int, source: str) -> None:
    """Perform and display subnet calculations for a given IPv4/CIDR."""

    print("=" * 64)
    print("  LAB-004: Subnet Mathematics")
    print("=" * 64)
    print()
    print(f"Input:   {ip_str}/{prefix}")
    print(f"Source:  {source}")
    print()

    # Build the network object
    net = ipaddress.IPv4Network(f"{ip_str}/{prefix}", strict=False)
    addr = ipaddress.IPv4Address(ip_str)
    addr_int = int(addr)

    # Subnet mask
    mask_int = int(net.netmask)
    mask_octets = [(mask_int >> shift) & 0xFF for shift in (24, 16, 8, 0)]
    mask_str = ".".join(str(o) for o in mask_octets)

    # Network address
    net_int = int(net.network_address)

    # Broadcast address
    bcast_int = int(net.broadcast_address)

    # Number of hosts
    host_bits = 32 - prefix
    total_hosts = (2 ** host_bits) - 2  # exclude network and broadcast

    print("─" * 64)
    print("  1. Basic Calculations")
    print("─" * 64)
    print()
    print(f"  Subnet mask:     {mask_str}  (/ {prefix})")
    print(f"  Network address: {net.network_address}")
    print(f"  Broadcast:       {net.broadcast_address}")
    print(f"  Host range:      {net.network_address + 1} – {net.broadcast_address - 1}")
    print(f"  Usable hosts:    {total_hosts:,}")
    print()
    print(f"  IP address:      {ip_str}")
    print(f"  Is network addr? {addr_int == net_int}")
    print(f"  Is broadcast?    {addr_int == bcast_int}")
    print(f"  Is host addr?    {addr_int != net_int and addr_int != bcast_int}")

    # Binary decomposition
    print()
    print("─" * 64)
    print("  2. Binary Decomposition")
    print("─" * 64)
    print()

    addr_bin = [(addr_int >> shift) & 0xFF for shift in (24, 16, 8, 0)]
    mask_bin = [(mask_int >> shift) & 0xFF for shift in (24, 16, 8, 0)]
    net_bin = [(net_int >> shift) & 0xFF for shift in (24, 16, 8, 0)]
    bcast_bin = [(bcast_int >> shift) & 0xFF for shift in (24, 16, 8, 0)]

    # Print address binary
    print(f"  Address:  {ip_str:>15s}")
    print(f"  Binary:   {' '.join(f'{o:08b}' for o in addr_bin)}")
    print(f"  Decimal:  {'  '.join(str(o).rjust(3) for o in addr_bin)}")
    print()
    print(f"  Mask:     {mask_str:>15s}  (/ {prefix})")
    print(f"  Binary:   {' '.join(f'{o:08b}' for o in mask_bin)}")

    # Mark network vs host bits
    print()
    print(f"  Prefix length = {prefix} bits")
    print(f"  ┌{'─' * (prefix + prefix // 8 * 1)}┬{'─' * ((32 - prefix) + (32 - prefix) // 8 * 0)}┐")
    net_bit_str = ""
    host_bit_str = ""
    for i, o in enumerate(addr_bin):
        for bit in range(7, -1, -1):
            byte_pos = i * 8 + (7 - bit)
            if byte_pos < prefix:
                net_bit_str += str((o >> bit) & 1)
                host_bit_str += " "
            else:
                net_bit_str += " "
                host_bit_str += str((o >> bit) & 1)
        net_bit_str += " "
        host_bit_str += " "

    print(f"  │ {net_bit_str.strip()}│ {host_bit_str.strip()}│")
    print(f"  │{' NETWORK '.center(len(net_bit_str))}│{' HOST '.center(len(host_bit_str))}│")
    print(f"  └{'─' * (prefix + prefix // 8 * 1)}┴{'─' * ((32 - prefix) + (32 - prefix) // 8 * 0)}┘")

    # Show what each octet contributes
    print()
    print("─" * 64)
    print("  3. Octet-by-Octet Breakdown")
    print("─" * 64)
    print()
    print(f"  {'Octet':<8} {'Address':>10} {'Mask':>10} {'Network':>10} {'Broadcast':>10}")
    print(f"  {'-'*8:<8} {'-'*10:>10} {'-'*10:>10} {'-'*10:>10} {'-'*10:>10}")
    for i in range(4):
        print(f"  {i+1:<8} {addr_bin[i]:>10} {mask_bin[i]:>10} {net_bin[i]:>10} {bcast_bin[i]:>10}")

    # CIDR explanation
    print()
    print("─" * 64)
    print("  4. What /16 Means")
    print("─" * 64)
    print()
    print(f"  /{prefix} = the first {prefix} bits identify the NETWORK.")
    print(f"  The remaining {32 - prefix} bits identify the HOST within that network.")
    print()
    print(f"  All devices in {net.network_address}/{prefix} share the same")
    print(f"  network prefix. They can communicate directly at Layer 2")
    print(f"  (via ARP + Ethernet/Wi-Fi) without a router.")
    print()
    print(f"  A destination OUTSIDE {net.network_address}/{prefix} requires")
    print(f"  a router (default gateway) to forward the packet beyond the")
    print(f"  local subnet.")
    print()
    print("=" * 64)


def main() -> None:
    if len(sys.argv) > 1:
        # Explicit input
        cidr = sys.argv[1]
        try:
            if "/" not in cidr:
                print(f"ERROR: Expected format IPv4/CIDR, got '{cidr}'")
                print("Example: python src/subnet_math.py 10.122.172.202/16")
                sys.exit(1)
            addr_str, pref_str = cidr.split("/")
            prefix = int(pref_str)
            ipaddress.IPv4Address(addr_str)  # validate
            calculate(addr_str, prefix, "COMMAND-LINE INPUT")
        except (ValueError, ipaddress.AddressValueError) as e:
            print(f"ERROR: Invalid IPv4/CIDR — {e}")
            sys.exit(1)
    else:
        # Auto-detect or fall back to historical
        print("Attempting to detect current wlan0 IPv4 address...")
        print()
        detected = get_wlan0_ip()

        if detected:
            addr, prefix = detected
            calculate(addr, prefix, "AUTO-DETECTED (wlan0) — VERIFIED")
        else:
            # Use historical value with clear labelling
            HISTORICAL_ADDR = "10.122.172.202"
            HISTORICAL_PREFIX = 16
            print("WARNING: Could not detect current wlan0 address.")
            print("Falling back to HISTORICAL value from LAB-001.")
            print()
            calculate(
                HISTORICAL_ADDR,
                HISTORICAL_PREFIX,
                "HISTORICAL INPUT (LAB-001) — NOT CURRENTLY RE-VERIFIED"
            )


if __name__ == "__main__":
    main()
