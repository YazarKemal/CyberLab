#!/usr/bin/env python3
"""
LAB-003: Local Name Resolution Investigation
=============================================

Investigates how "localhost" resolves on THIS device using ONLY local
mechanisms:
  - socket.getaddrinfo() — the standard resolver API
  - socket.gethostbyname_ex() — alternative resolution
  - /etc/hosts — the local hosts file (if readable)

No DNS servers are contacted. No external hosts are queried.
All resolution is local.

Usage:
  python src/local_resolution.py
"""

import socket
import sys


def section(title: str) -> None:
    print()
    print(f"--- {title} ---")
    print()


def try_read_file(path: str) -> str | None:
    """Read a file, return contents or None."""
    try:
        with open(path, "r") as fh:
            return fh.read()
    except (PermissionError, FileNotFoundError, OSError) as exc:
        print(f"  Cannot read {path}: {exc}")
        return None


def main() -> None:
    print("=" * 55)
    print("  LAB-003: Local Name Resolution Investigation")
    print("  No external DNS — local mechanisms only")
    print("=" * 55)

    # ------------------------------------------------------------------
    # 1. localhost — IPv4
    # ------------------------------------------------------------------
    section("1. getaddrinfo('localhost', None, AF_INET)")

    try:
        results = socket.getaddrinfo("localhost", None, socket.AF_INET)
        print(f"  Addresses found: {len(results)}")
        for fam, typ, proto, canon, addr in results:
            print(f"    family={fam} ({'AF_INET' if fam == socket.AF_INET else fam})")
            print(f"    address: {addr[0]}")
            print(f"    canonical: {canon or '(none)'}")
    except socket.gaierror as exc:
        print(f"  FAILED: {exc}")

    # ------------------------------------------------------------------
    # 2. localhost — IPv6
    # ------------------------------------------------------------------
    section("2. getaddrinfo('localhost', None, AF_INET6)")

    try:
        results = socket.getaddrinfo("localhost", None, socket.AF_INET6)
        print(f"  Addresses found: {len(results)}")
        for fam, typ, proto, canon, addr in results:
            print(f"    address: {addr[0]}")
            print(f"    canonical: {canon or '(none)'}")
    except socket.gaierror as exc:
        print(f"  FAILED: {exc}")
        print(f"  Error code: {exc.errno if hasattr(exc, 'errno') else 'N/A'}")
        print("  (This means localhost does not resolve to ::1 on this system)")

    # ------------------------------------------------------------------
    # 3. localhost — unspecified (both families)
    # ------------------------------------------------------------------
    section("3. getaddrinfo('localhost', None) — all families")

    try:
        results = socket.getaddrinfo("localhost", None)
        print(f"  Addresses found: {len(results)}")
        for fam, typ, proto, canon, addr in results:
            fam_name = {socket.AF_INET: "AF_INET",
                        socket.AF_INET6: "AF_INET6",
                        socket.AF_UNIX: "AF_UNIX"}.get(fam, str(fam))
            print(f"    [{fam_name}] {addr[0]}")
    except socket.gaierror as exc:
        print(f"  FAILED: {exc}")

    # ------------------------------------------------------------------
    # 4. gethostbyname_ex
    # ------------------------------------------------------------------
    section("4. socket.gethostbyname_ex('localhost')")

    try:
        hostname, aliases, addresses = socket.gethostbyname_ex("localhost")
        print(f"  Hostname: {hostname}")
        print(f"  Aliases: {aliases}")
        print(f"  Addresses: {addresses}")
    except socket.gaierror as exc:
        print(f"  FAILED: {exc}")

    # ------------------------------------------------------------------
    # 5. /etc/hosts
    # ------------------------------------------------------------------
    section("5. /etc/hosts")
    content = try_read_file("/etc/hosts")
    if content:
        print("  Contents:")
        for line in content.splitlines():
            line = line.strip()
            if line and not line.startswith("#"):
                print(f"    {line}")
        print()
        # Parse and report
        print("  Parsed mappings:")
        for line in content.splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split()
            if len(parts) >= 2:
                ip = parts[0]
                names = parts[1:]
                for name in names:
                    print(f"    {name:30s} → {ip}")

    # ------------------------------------------------------------------
    # 6. getaddrinfo — ::1 direct
    # ------------------------------------------------------------------
    section("6. getaddrinfo('::1', None, AF_INET6) — direct IPv6 loopback")

    try:
        results = socket.getaddrinfo("::1", None, socket.AF_INET6)
        print(f"  Addresses found: {len(results)}")
        for fam, typ, proto, canon, addr in results:
            print(f"    address: {addr[0]}")
    except socket.gaierror as exc:
        print(f"  FAILED: {exc}")

    # ------------------------------------------------------------------
    # 7. getfqdn
    # ------------------------------------------------------------------
    section("7. socket.getfqdn()")
    try:
        fqdn = socket.getfqdn()
        print(f"  FQDN: {fqdn}")
    except Exception as exc:
        print(f"  FAILED: {exc}")

    # ------------------------------------------------------------------
    # 8. gethostname
    # ------------------------------------------------------------------
    section("8. socket.gethostname()")
    try:
        hostname = socket.gethostname()
        print(f"  Hostname: {hostname}")
    except Exception as exc:
        print(f"  FAILED: {exc}")

    # ------------------------------------------------------------------
    # Summary
    # ------------------------------------------------------------------
    section("Summary")
    print("  Key findings to record in observations.md:")
    print("    • What does localhost resolve to over AF_INET?")
    print("    • What does localhost resolve to over AF_INET6?")
    print("    • Does /etc/hosts contain ::1? If so, under what name?")
    print("    • Is there a discrepancy between /etc/hosts and getaddrinfo()?")
    print("=" * 55)


if __name__ == "__main__":
    main()
