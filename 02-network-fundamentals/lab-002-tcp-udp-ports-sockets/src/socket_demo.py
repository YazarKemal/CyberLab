#!/usr/bin/env python3
"""
LAB-002: Socket Types and Address Families Demonstration
=========================================================

Demonstrates the socket module's constants and concepts WITHOUT making
any network connections.

This script shows:
  - Address families: AF_INET (IPv4), AF_INET6 (IPv6), AF_UNIX (local IPC)
  - Socket types: SOCK_STREAM (TCP), SOCK_DGRAM (UDP), SOCK_RAW (raw)
  - What each combination means
  - Whether IPv6 is available on this device
  - How inet_pton/inet_ntop convert between string and binary forms
  - How getaddrinfo resolves localhost for both IPv4 and IPv6
  - The difference between a stream and a datagram

All operations are local. No network connections are established.
"""

import socket
import sys


# =============================================================================
# Section 1 — Address Families
# =============================================================================

def show_address_families() -> None:
    print("=" * 55)
    print("  1. ADDRESS FAMILIES")
    print("=" * 55)
    print()
    print("  An address family determines the FORMAT of addresses used")
    print("  with a socket. It answers: what kind of network are we on?")
    print()

    families = [
        ("AF_INET",  socket.AF_INET,  "IPv4 — 32-bit addresses like 127.0.0.1"),
        ("AF_INET6", socket.AF_INET6, "IPv6 — 128-bit addresses like ::1"),
        ("AF_UNIX",  socket.AF_UNIX,  "Unix domain — filesystem paths for local IPC"),
    ]

    for name, value, description in families:
        print(f"  {name:12s} = {value:<4d}  {description}")

    print()
    print("  AF_INET + SOCK_STREAM = TCP over IPv4 (the most common combination)")
    print("  AF_INET + SOCK_DGRAM  = UDP over IPv4")
    print("  AF_UNIX + SOCK_STREAM = Local process communication (like a pipe)")
    print()

    # Try creating sockets of each type to see which are available
    print("  Testing socket creation:")
    print()

    tests = [
        (socket.AF_INET,  socket.SOCK_STREAM, "AF_INET + SOCK_STREAM"),
        (socket.AF_INET,  socket.SOCK_DGRAM,  "AF_INET + SOCK_DGRAM"),
        (socket.AF_INET6, socket.SOCK_STREAM, "AF_INET6 + SOCK_STREAM"),
        (socket.AF_INET6, socket.SOCK_DGRAM,  "AF_INET6 + SOCK_DGRAM"),
    ]

    for family, sock_type, label in tests:
        try:
            s = socket.socket(family, sock_type)
            s.close()
            print(f"    ✓ {label} — available")
        except OSError as exc:
            print(f"    ✗ {label} — {exc}")


# =============================================================================
# Section 2 — Socket Types
# =============================================================================

def show_socket_types() -> None:
    print()
    print("=" * 55)
    print("  2. SOCKET TYPES")
    print("=" * 55)
    print()
    print("  A socket type determines HOW data is sent and received.")
    print("  It answers: what guarantees does the transport provide?")
    print()

    types_ = [
        ("SOCK_STREAM", socket.SOCK_STREAM,
         "TCP — reliable, ordered, connection-oriented byte stream.",
         [
             "  • Data arrives in the order it was sent.",
             "  • Lost packets are retransmitted.",
             "  • No message boundaries: send('AB') + send('CD') may arrive as 'ABCD'",
             "  • Requires connect() / accept() handshake.",
             "  • Used by: HTTP, SSH, SMTP, FTP.",
         ]),
        ("SOCK_DGRAM", socket.SOCK_DGRAM,
         "UDP — connectionless, unreliable, message-oriented datagrams.",
         [
             "  • Each datagram is independent — no ordering guarantee.",
             "  • Datagrams may be lost, duplicated, or reordered.",
             "  • Message boundaries preserved: each sendto() = one recvfrom().",
             "  • No connect() needed; no handshake.",
             "  • Used by: DNS, VoIP, streaming, online games.",
         ]),
        ("SOCK_RAW", socket.SOCK_RAW,
         "Raw — direct access to IP layer. Requires root/CAP_NET_RAW.",
         [
             "  • Bypasses TCP/UDP — you construct IP headers yourself.",
             "  • Used by: ping (ICMP), nmap SYN scan, custom protocols.",
             "  • NOT available without root privileges.",
         ]),
    ]

    for name, value, summary, details in types_:
        print(f"  {name:14s} = {value}")
        print(f"  {summary}")
        for detail in details:
            print(detail)
        print()


# =============================================================================
# Section 3 — IPv6 Check
# =============================================================================

def show_ipv6_status() -> None:
    print("=" * 55)
    print("  3. IPv6 AVAILABILITY")
    print("=" * 55)
    print()

    # Try to create an IPv6 socket
    try:
        s = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
        s.close()
        print("  IPv6 socket creation: AVAILABLE")
    except OSError as exc:
        print(f"  IPv6 socket creation: UNAVAILABLE ({exc})")
        print("  (This is expected on some Android/Termux configurations.)")
        print("  (IPv6 may still work at the kernel level but be restricted for apps.)")
        return

    # Try to resolve ::1
    try:
        result = socket.getaddrinfo("::1", None, socket.AF_INET6, socket.SOCK_STREAM)
        addresses = [addr[4][0] for addr in result]
        print(f"  ::1 resolution: {addresses}")
    except socket.gaierror as exc:
        print(f"  ::1 resolution: FAILED ({exc})")

    # Try to resolve localhost over IPv6
    try:
        result = socket.getaddrinfo("localhost", None, socket.AF_INET6)
        addresses = [addr[4][0] for addr in result]
        print(f"  localhost (IPv6): {addresses}")
    except socket.gaierror as exc:
        print(f"  localhost (IPv6): FAILED ({exc})")

    print()
    print("  Note: Even if IPv6 sockets can be created, IPv6 connectivity")
    print("  requires kernel support and (for non-loopback) router support.")
    print("  This lab only uses ::1, which requires no external infrastructure.")

    # Try to bind to ::1
    print()
    print("  Attempting to bind to ::1...")
    try:
        s = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind(("::1", 0))  # port 0 = OS picks a free port
        bound_addr = s.getsockname()
        print(f"  ✓ Successfully bound to {bound_addr[0]}:{bound_addr[1]}")
        s.close()
    except OSError as exc:
        print(f"  ✗ Cannot bind to ::1: {exc}")
        print("  (IPv6 loopback is not available in this environment.)")


# =============================================================================
# Section 4 — inet_pton / inet_ntop Review
# =============================================================================

def show_address_conversion() -> None:
    print()
    print("=" * 55)
    print("  4. ADDRESS CONVERSION (inet_pton / inet_ntop)")
    print("=" * 55)
    print()
    print("  inet_pton = 'presentation to network' — string → binary")
    print("  inet_ntop = 'network to presentation' — binary → string")
    print()
    print("  Every IP address on the wire is just raw bytes.")
    print("  These functions convert between human and machine forms.")
    print()

    # IPv4
    ipv4_str = "127.0.0.1"
    ipv4_bin = socket.inet_pton(socket.AF_INET, ipv4_str)
    ipv4_roundtrip = socket.inet_ntop(socket.AF_INET, ipv4_bin)

    print(f"  IPv4: '{ipv4_str}'")
    print(f"    → inet_pton → {ipv4_bin.hex()} ({len(ipv4_bin)} bytes: {list(ipv4_bin)})")
    print(f"    → inet_ntop → '{ipv4_roundtrip}'")
    print()

    # IPv6
    if _ipv6_available():
        ipv6_str = "::1"
        ipv6_bin = socket.inet_pton(socket.AF_INET6, ipv6_str)
        ipv6_roundtrip = socket.inet_ntop(socket.AF_INET6, ipv6_bin)

        print(f"  IPv6: '{ipv6_str}'")
        print(f"    → inet_pton → {ipv6_bin.hex()} ({len(ipv6_bin)} bytes)")
        print(f"    → inet_ntop → '{ipv6_roundtrip}'")
    else:
        print("  IPv6: SKIPPED (not available in this environment)")

    print()
    print("  This is why an IPv4 packet header has 32 bits for addresses")
    print("  and an IPv6 packet header has 128 bits for addresses.")
    print("  The 'human readable' form is just a display convention.")


# =============================================================================
# Section 5 — localhost Resolution
# =============================================================================

def show_localhost_resolution() -> None:
    print()
    print("=" * 55)
    print("  5. LOCALHOST RESOLUTION")
    print("=" * 55)
    print()
    print("  getaddrinfo() resolves a hostname to socket addresses.")
    print("  It reads /etc/hosts and (for non-local names) queries DNS.")
    print()
    print("  Resolving 'localhost'...")
    print()

    for family_name, family in [("AF_INET (IPv4)", socket.AF_INET),
                                 ("AF_INET6 (IPv6)", socket.AF_INET6)]:
        try:
            results = socket.getaddrinfo("localhost", None, family, socket.SOCK_STREAM)
            for fam, typ, proto, canon, addr in results:
                print(f"    {family_name}: {addr[0]}  (canonical name: {canon or '(none)'})")
        except socket.gaierror as exc:
            print(f"    {family_name}: resolution failed — {exc}")

    print()
    print("  'localhost' always resolves to a loopback address (127.0.0.1 or ::1).")
    print("  This is guaranteed by /etc/hosts on every Unix system.")


# =============================================================================
# Helper
# =============================================================================

def _ipv6_available() -> bool:
    """Check if IPv6 sockets can be created."""
    try:
        s = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
        s.close()
        return True
    except OSError:
        return False


# =============================================================================
# Main
# =============================================================================

def main() -> None:
    print()
    print("╔═══════════════════════════════════════════════════════╗")
    print("║  LAB-002: Socket Types and Address Families           ║")
    print("║  Python standard library only — no network calls      ║")
    print("╚═══════════════════════════════════════════════════════╝")

    show_address_families()
    show_socket_types()
    show_ipv6_status()
    show_address_conversion()
    show_localhost_resolution()

    print()
    print("=" * 55)
    print("  Demonstration complete.")
    print()
    print("  Key takeaway:")
    print("    AF_INET + SOCK_STREAM = TCP over IPv4 (stream of bytes)")
    print("    AF_INET + SOCK_DGRAM  = UDP over IPv4 (individual datagrams)")
    print("    AF_UNIX + SOCK_STREAM = Local IPC (like PostgreSQL socket)")
    print()
    print("  Next step: run the TCP and UDP experiments to see these")
    print("  concepts in action.")
    print("=" * 55)
    print()


if __name__ == "__main__":
    main()
