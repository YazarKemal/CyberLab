#!/usr/bin/env python3
"""
LAB-001: Know Your Host — Network Interface Inspector
=====================================================

Inspects THIS device's network environment using ONLY the Python standard
library. No external packages. No network connections to remote hosts.

What this script teaches:
  - Reading kernel state from /proc/net/ (the virtual filesystem)
  - Using the socket module for hostname/DNS queries
  - Parsing structured text output from system tools
  - Graceful handling of Android/Termux restrictions

Usage:
  python src/interface_info.py

Author: CyberLab / LAB-001
Date:   2026-08-09
"""

import os
import socket
import subprocess
import sys
import struct
import array
import fcntl
import platform


# =============================================================================
# Utility helpers
# =============================================================================

def section(title: str) -> None:
    """Print a labeled section header."""
    print()
    print(f"--- {title} ---")
    print()


def try_or(callable_, fallback="(restricted)"):
    """Call something; return fallback string on any exception."""
    try:
        return callable_()
    except Exception as exc:
        return f"{fallback} [{type(exc).__name__}: {exc}]"


def read_file(path: str) -> str | None:
    """Read a file, return its content as a string, or None if unreadable."""
    try:
        with open(path, "r") as fh:
            return fh.read().strip()
    except (PermissionError, FileNotFoundError, OSError) as exc:
        print(f"  (cannot read {path}: {exc})")
        return None


def run_command(cmd: list[str]) -> str | None:
    """Run a command via subprocess, return its stdout, or None on failure."""
    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=5
        )
        return result.stdout.strip() or "(empty output)"
    except FileNotFoundError:
        print(f"  (command not found: {cmd[0]})")
        return None
    except subprocess.TimeoutExpired:
        print(f"  (timeout: {' '.join(cmd)})")
        return None
    except Exception as exc:
        print(f"  (error running {' '.join(cmd)}: {exc})")
        return None


# =============================================================================
# Section 1 — System Information
# =============================================================================

def show_system_info() -> None:
    section("1. System Information")

    print(f"  Python version : {sys.version.split()[0]}")
    print(f"  Platform       : {platform.platform()}")
    print(f"  Architecture   : {platform.machine()}")
    print(f"  Processor      : {platform.processor()}")

    uname = os.uname()
    print(f"  Kernel (uname) : {uname.sysname} {uname.release}")
    print(f"  Node name      : {uname.nodename}")
    print(f"  OS             : {uname.sysname}")

    hostname = try_or(socket.gethostname)
    print(f"  Hostname       : {hostname}")


# =============================================================================
# Section 2 — Network Interfaces via /proc/net/dev
# =============================================================================

def parse_proc_net_dev() -> list[dict]:
    """
    Parse /proc/net/dev which looks like:

    Inter-|   Receive  |  Transmit
     face |bytes packets ... | bytes packets ...
        lo: 12345    100 ...   12345    100 ...
      wlan0: 67890    200 ...   67890    200 ...

    Returns a list of dicts with interface name and statistics.
    """
    content = read_file("/proc/net/dev")
    if content is None:
        return []

    interfaces = []
    for line in content.splitlines():
        if ":" not in line:
            continue  # skip header rows
        name, _, stats = line.partition(":")
        name = name.strip()
        fields = stats.split()
        if len(fields) < 10:
            continue
        interfaces.append({
            "name": name,
            "rx_bytes": int(fields[0]),
            "rx_packets": int(fields[1]),
            "rx_errs": int(fields[2]),
            "rx_drop": int(fields[3]),
            "tx_bytes": int(fields[8]),
            "tx_packets": int(fields[9]),
            "tx_errs": int(fields[10]),
            "tx_drop": int(fields[11]),
        })
    return interfaces


def show_interfaces_from_proc() -> None:
    section("2. Network Interfaces (from /proc/net/dev)")

    interfaces = parse_proc_net_dev()
    if not interfaces:
        print("  (no interface data available)")
        return

    print(f"  {'Interface':<12} {'RX bytes':>12} {'RX pkts':>10} {'TX bytes':>12} {'TX pkts':>10}")
    print(f"  {'-'*12} {'-'*12} {'-'*10} {'-'*12} {'-'*10}")
    for iface in interfaces:
        print(
            f"  {iface['name']:<12} "
            f"{iface['rx_bytes']:>12,} "
            f"{iface['rx_packets']:>10,} "
            f"{iface['tx_bytes']:>12,} "
            f"{iface['tx_packets']:>10,}"
        )


# =============================================================================
# Section 3 — Interface Details via 'ip addr show'
# =============================================================================

def show_ip_addr() -> None:
    section("3. Interface Details (ip addr show)")

    output = run_command(["ip", "addr", "show"])
    if output is None:
        # Fall back to ifconfig
        output = run_command(["ifconfig"])
    if output is None:
        print("  (no interface detail tool available)")
        return

    print(output)


# =============================================================================
# Section 4 — Routing Table via 'ip route show'
# =============================================================================

def show_routing() -> None:
    section("4. Routing Table (ip route show)")

    output = run_command(["ip", "route", "show"])
    if output is None:
        output = run_command(["route", "-n"])
    if output:
        print(output)

    # Also try /proc/net/route (hex-encoded, always available on Linux)
    content = read_file("/proc/net/route")
    if content:
        print()
        print("  /proc/net/route (hex-encoded):")
        print(f"  {content.splitlines()[0] if content else ''}")  # header
        for line in content.splitlines()[1:]:
            print(f"  {line}")


# =============================================================================
# Section 5 — IPv6 Addresses via /proc/net/if_inet6
# =============================================================================

def show_ipv6_addresses() -> None:
    section("5. IPv6 Addresses (from /proc/net/if_inet6)")

    content = read_file("/proc/net/if_inet6")
    if content is None:
        print("  (IPv6 info not available — kernel may not have IPv6 loaded)")
        return

    print("  Format: <hex-address> <ifindex> <prefixlen> <scope> <flags> <ifname>")
    print()
    for line in content.splitlines():
        parts = line.split()
        if len(parts) >= 6:
            raw_addr = parts[0]
            # Expand the 32-hex-digit address into colon-separated groups
            grouped = ":".join(
                raw_addr[i:i+4] for i in range(0, 32, 4)
            )
            prefix_len = parts[2]
            ifname = parts[5]
            scope = parts[3]
            scope_names = {"00": "global", "20": "link-local", "40": "site-local"}
            scope_str = scope_names.get(scope, f"scope={scope}")
            print(f"  {grouped}/{prefix_len}  {scope_str}  {ifname}")


# =============================================================================
# Section 6 — DNS Configuration
# =============================================================================

def show_dns_config() -> None:
    section("6. DNS Configuration")

    # /etc/resolv.conf
    content = read_file("/etc/resolv.conf")
    if content:
        print("  /etc/resolv.conf:")
        for line in content.splitlines():
            line = line.strip()
            if line and not line.startswith("#"):
                print(f"    {line}")
    else:
        print("  (cannot read /etc/resolv.conf)")

    # Android getprop fallback
    for prop in ["net.dns1", "net.dns2", "net.dns3"]:
        output = run_command(["getprop", prop])
        if output and output != "(empty output)":
            print(f"  {prop}: {output}")

    # Try resolving our own hostname to see DNS in action (local only, no network)
    try:
        fqdn = socket.getfqdn()
        print(f"  FQDN (via socket.getfqdn): {fqdn}")
    except Exception as exc:
        print(f"  FQDN lookup failed: {exc}")


# =============================================================================
# Section 7 — Listening Sockets via 'ss'
# =============================================================================

def show_listening_sockets() -> None:
    section("7. Listening TCP Sockets (ss -tln)")

    output = run_command(["ss", "-tln"])
    if output is None:
        output = run_command(["netstat", "-tln"])
    if output:
        print(output)
    else:
        print("  (no socket inspection tool available)")

    # Also read /proc/net/tcp for listening sockets (state 0A = LISTEN)
    print()
    print("  /proc/net/tcp (listening only, state=0A):")
    content = read_file("/proc/net/tcp")
    if content:
        lines = content.splitlines()
        if lines:
            print(f"  {lines[0]}")  # header
        for line in lines[1:]:
            parts = line.split()
            if len(parts) >= 4 and parts[3] == "0A":
                # Decode hex local_address (IP:port in hex, little-endian)
                local_hex = parts[1]
                ip_hex, _, port_hex = local_hex.partition(":")
                try:
                    # IP is stored as 4 bytes in hex, little-endian
                    ip_int = int(ip_hex, 16)
                    ip_bytes = struct.pack("<I", ip_int)
                    ip_str = socket.inet_ntop(socket.AF_INET, ip_bytes)
                    port = int(port_hex, 16)
                    print(f"  LISTEN  {ip_str}:{port}")
                except (ValueError, struct.error, OSError):
                    print(f"  LISTEN  (raw: {local_hex})")


# =============================================================================
# Section 8 — /etc/hosts
# =============================================================================

def show_hosts_file() -> None:
    section("8. Local Hosts File (/etc/hosts)")

    content = read_file("/etc/hosts")
    if content:
        for line in content.splitlines():
            line = line.strip()
            if line and not line.startswith("#"):
                print(f"  {line}")
    else:
        print("  (cannot read /etc/hosts)")


# =============================================================================
# Section 9 — Socket Module Demo (LOCAL ONLY)
# =============================================================================

def socket_demo() -> None:
    """
    Demonstrate Python socket module concepts without contacting any remote host.
    All operations are purely local: address resolution, socket creation,
    and structure decoding.
    """
    section("9. Socket Module Demonstrations (local only)")

    # 9a. Show available address families and socket types
    print("  9a. Address families and socket types:")
    families = [
        ("AF_INET", socket.AF_INET, "IPv4"),
        ("AF_INET6", socket.AF_INET6, "IPv6"),
        ("AF_UNIX", socket.AF_UNIX, "Unix domain (local)"),
    ]
    for name, value, desc in families:
        print(f"      {name} = {value}  ({desc})")

    types_ = [
        ("SOCK_STREAM", socket.SOCK_STREAM, "TCP (reliable, ordered)"),
        ("SOCK_DGRAM", socket.SOCK_DGRAM, "UDP (datagrams)"),
        ("SOCK_RAW", socket.SOCK_RAW, "Raw (requires root)"),
    ]
    for name, value, desc in types_:
        print(f"      {name} = {value}  ({desc})")

    # 9b. Resolve localhost (does NOT contact DNS — reads /etc/hosts)
    print()
    print("  9b. Resolving 'localhost' (from /etc/hosts, not DNS):")
    for family_name, family, _ in families[:2]:  # AF_INET, AF_INET6
        try:
            result = socket.getaddrinfo("localhost", None, family=family)
            for fam, typ, proto, canon, addr in result:
                print(f"      {family_name}: {addr[0]}  (canonical: {canon})")
        except socket.gaierror as exc:
            print(f"      {family_name}: resolution failed — {exc}")

    # 9c. Resolve our own hostname
    print()
    print("  9c. Resolving our own hostname:")
    hostname = try_or(socket.gethostname)
    try:
        result = socket.getaddrinfo(hostname, None)
        for fam, typ, proto, canon, addr in result:
            if addr[0] not in ("127.0.0.1", "::1"):
                print(f"      {hostname} → {addr[0]}  (family={fam})")
    except socket.gaierror as exc:
        print(f"      {hostname}: resolution failed — {exc}")

    # 9d. Decode the sockaddr structures for 127.0.0.1 and ::1
    print()
    print("  9d. Binary sockaddr representations:")
    # IPv4 loopback: 127.0.0.1:8080 → packed binary form
    ipv4_binary = socket.inet_pton(socket.AF_INET, "127.0.0.1")
    print(f"      inet_pton(AF_INET, '127.0.0.1') → {ipv4_binary.hex()}")
    print(f"        (4 bytes: {list(ipv4_binary)} — one byte per octet)")

    # IPv6 loopback: ::1 → packed binary form
    ipv6_binary = socket.inet_pton(socket.AF_INET6, "::1")
    print(f"      inet_pton(AF_INET6, '::1') → {ipv6_binary.hex()}")
    print(f"        (16 bytes: {list(ipv6_binary)})")

    # 9e. Decode the address back
    print()
    print("  9e. Round-trip: binary → inet_ntop → string:")
    roundtrip_v4 = socket.inet_ntop(socket.AF_INET, ipv4_binary)
    roundtrip_v6 = socket.inet_ntop(socket.AF_INET6, ipv6_binary)
    print(f"      AF_INET:  {ipv4_binary.hex()} → {roundtrip_v4}")
    print(f"      AF_INET6: {ipv6_binary.hex()} → {roundtrip_v6}")


# =============================================================================
# Section 10 — /proc/net/ Tour (Protocol Statistics)
# =============================================================================

def show_proc_net_stats() -> None:
    section("10. Protocol Statistics (/proc/net/snmp)")

    content = read_file("/proc/net/snmp")
    if content is None:
        print("  (cannot read /proc/net/snmp)")
        return

    # Parse the key-value format: one header line, one value line per protocol
    lines = content.splitlines()
    for i in range(0, len(lines), 2):
        if i + 1 >= len(lines):
            break
        proto = lines[i].strip()
        values = lines[i + 1].strip()
        print(f"  {proto}")
        # Print selected key fields
        header_parts = proto.split()
        value_parts = values.split()
        if len(header_parts) == len(value_parts):
            for h, v in zip(header_parts[:8], value_parts[:8]):
                print(f"    {h}: {v}")
            if len(header_parts) > 8:
                print(f"    ... (+ {len(header_parts) - 8} more fields)")
        print()


# =============================================================================
# Section 11 — Summary: What kind of network are we on?
# =============================================================================

def show_summary() -> None:
    section("11. Summary — What Kind of Network Are We On?")

    # Determine if we're behind NAT by checking for private IPs
    private_ranges = [
        ("10.0.0.0/8",     lambda b: b[0] == 10),
        ("172.16.0.0/12",  lambda b: b[0] == 172 and 16 <= b[1] <= 31),
        ("192.168.0.0/16", lambda b: b[0] == 192 and b[1] == 168),
    ]

    # Try to get our non-loopback IPv4 address
    our_ip = None
    try:
        # Connect to a non-existent local socket to get the bound address
        # This does NOT send any packets — socket is never connected.
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(0)
        # Binding to 0.0.0.0 and reading getsockname won't give us the right IP.
        # Instead, try the traditional "connect to a non-local address" trick.
        # BUT: we promised no external contact. We'll use getsockname after a
        # non-connecting operation, or parse ip addr output.
        s.close()
    except Exception:
        pass

    # Parse ip addr output to find our addresses
    output = run_command(["ip", "addr", "show"])
    if output is None:
        output = run_command(["ifconfig"])

    our_ips = []
    is_nat = False
    if output:
        for line in output.splitlines():
            line = line.strip()
            if line.startswith("inet ") and "127.0.0.1" not in line:
                # "inet 192.168.1.42/24 ..."
                parts = line.split()
                ip_cidr = parts[1] if len(parts) > 1 else "?"
                our_ips.append(ip_cidr)
                # Check private range
                ip_str = ip_cidr.split("/")[0]
                octets = ip_str.split(".")
                if len(octets) == 4:
                    b = tuple(int(o) for o in octets)
                    for range_name, check in private_ranges:
                        if check(b):
                            is_nat = True
                            break

    if our_ips:
        print("  Non-loopback IP addresses found:")
        for ip in our_ips:
            private_marker = " ← PRIVATE (NAT)" if is_nat else ""
            print(f"    {ip}{private_marker}")
    else:
        print("  (could not determine non-loopback IP addresses)")

    print()
    if is_nat:
        print("  VERDICT: This device is behind NAT.")
        print("  Outbound traffic appears to come from the router's public IP,")
        print("  not from any of the addresses listed above.")
    else:
        print("  VERDICT: This device appears to have a public IP address,")
        print("  or the IP could not be classified.")

    # Check for IPv6 connectivity
    ipv6_found = False
    if output:
        for line in output.splitlines():
            if "inet6 " in line:
                ipv6_found = True
                break

    print(f"  IPv6 present: {'Yes' if ipv6_found else 'No'}")

    print()
    print("  RECOMMENDATION:")
    print("    Complete the observations.md template with the data shown above.")
    print("    Then sketch a diagram showing:")
    print("    [Your Device] ←→ [Default Gateway] ←→ [DNS Server] ←→ Internet")


# =============================================================================
# Main
# =============================================================================

def main() -> None:
    print("=" * 60)
    print("  LAB-001: Network Interface Inspector")
    print("  Python standard library only — no packages, no network calls")
    print("=" * 60)

    show_system_info()
    show_interfaces_from_proc()
    show_ip_addr()
    show_routing()
    show_ipv6_addresses()
    show_dns_config()
    show_listening_sockets()
    show_hosts_file()
    socket_demo()
    show_proc_net_stats()
    show_summary()

    print()
    print("=" * 60)
    print("  Inspection complete.")
    print("  Next step: fill in observations.md with the data above.")
    print("=" * 60)


if __name__ == "__main__":
    main()
