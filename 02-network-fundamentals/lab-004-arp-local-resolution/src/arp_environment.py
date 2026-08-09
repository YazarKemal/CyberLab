#!/usr/bin/env python3
"""
LAB-004: ARP Environment Inspection
====================================

Safely inspects only locally exposed OS state related to ARP and neighbors.

Attempts multiple methods WITHOUT installing any packages:

- ifconfig (if present)
- ip neigh (if the command already exists)
- arp -n (if the command already exists)
- /proc/net/arp (if readable)

For each method reports: AVAILABLE, BLOCKED, UNAVAILABLE, or EMPTY.

Usage:
  python src/arp_environment.py
"""

import os
import sys
import subprocess
import socket


STATUS_AVAILABLE = "AVAILABLE"
STATUS_BLOCKED = "BLOCKED"
STATUS_UNAVAILABLE = "UNAVAILABLE"
STATUS_EMPTY = "EMPTY"


def separator(title: str) -> None:
    print()
    print("─" * 64)
    print(f"  {title}")
    print("─" * 64)
    print()


def check_command(name: str, args: list[str]) -> dict:
    """Try running a command and return structured result."""
    result = {
        "method": name,
        "command": f"{name} {' '.join(args)}",
        "status": STATUS_UNAVAILABLE,
        "stdout": "",
        "stderr": "",
        "returncode": None,
        "details": "",
    }

    try:
        proc = subprocess.run(
            [name, *args],
            capture_output=True, text=True, timeout=5, check=False
        )
        result["returncode"] = proc.returncode
        result["stdout"] = proc.stdout.strip()
        result["stderr"] = proc.stderr.strip()

        if proc.returncode == 0:
            if result["stdout"]:
                result["status"] = STATUS_AVAILABLE
            else:
                result["status"] = STATUS_EMPTY
                result["details"] = "Command succeeded but produced no output."
        else:
            if "Permission denied" in result["stderr"]:
                result["status"] = STATUS_BLOCKED
                result["details"] = f"Permission denied: {result['stderr'][:120]}"
            elif "No such file" in result["stderr"] or "not found" in result["stderr"]:
                result["status"] = STATUS_UNAVAILABLE
                result["details"] = "Command not found."
            else:
                result["status"] = STATUS_BLOCKED
                result["details"] = f"Return code {proc.returncode}: {result['stderr'][:120]}"

    except FileNotFoundError:
        result["status"] = STATUS_UNAVAILABLE
        result["details"] = f"'{name}' executable not found on PATH."
    except subprocess.TimeoutExpired:
        result["status"] = STATUS_BLOCKED
        result["details"] = f"Command timed out after 5 seconds."
    except OSError as e:
        result["status"] = STATUS_BLOCKED
        result["details"] = f"OS error: {e}"

    return result


def check_proc_net_arp() -> dict:
    """Try to read /proc/net/arp."""
    result = {
        "method": "/proc/net/arp",
        "command": "open('/proc/net/arp')",
        "status": STATUS_UNAVAILABLE,
        "stdout": "",
        "stderr": "",
        "returncode": None,
        "details": "",
    }

    path = "/proc/net/arp"
    if not os.path.exists(path):
        result["status"] = STATUS_UNAVAILABLE
        result["details"] = f"'{path}' does not exist on this system."
        return result

    try:
        with open(path, "r") as f:
            content = f.read().strip()
        lines = [l for l in content.splitlines() if l.strip()]
        if len(lines) <= 1:  # header only
            result["status"] = STATUS_EMPTY
            result["stdout"] = content
            result["details"] = "File readable but contains only header (no ARP entries)."
        else:
            result["status"] = STATUS_AVAILABLE
            result["stdout"] = content
            result["details"] = f"{len(lines) - 1} ARP entry/entries found."
    except PermissionError as e:
        result["status"] = STATUS_BLOCKED
        result["details"] = f"PermissionError: {e}. Android sandbox prevents reading /proc/net/arp."
    except OSError as e:
        result["status"] = STATUS_BLOCKED
        result["details"] = f"OS error: {e}"

    return result


def check_interface_info() -> dict:
    """Gather local interface information safely."""
    result = {
        "method": "ifconfig",
        "command": "ifconfig",
        "status": STATUS_UNAVAILABLE,
        "stdout": "",
        "stderr": "",
        "returncode": None,
        "details": "",
        "interfaces": [],
        "wlan0": None,
    }

    try:
        # Try ifconfig first
        proc = subprocess.run(
            ["ifconfig"],
            capture_output=True, text=True, timeout=5, check=False
        )
        result["returncode"] = proc.returncode
        result["stdout"] = proc.stdout.strip()
        result["stderr"] = proc.stderr.strip()

        if proc.returncode == 0:
            if result["stdout"]:
                result["status"] = STATUS_AVAILABLE
                # Parse interface names
                for line in result["stdout"].splitlines():
                    if line and not line.startswith(" "):
                        iface = line.split()[0].rstrip(":")
                        result["interfaces"].append(iface)

                # Try to extract wlan0 info
                try:
                    wlan_proc = subprocess.run(
                        ["ifconfig", "wlan0"],
                        capture_output=True, text=True, timeout=5, check=False
                    )
                    if wlan_proc.returncode == 0 and wlan_proc.stdout.strip():
                        import re
                        wlan_out = wlan_proc.stdout
                        wlan_info = {}
                        m = re.search(r"inet\s+([\d.]+)", wlan_out)
                        if m:
                            wlan_info["ipv4"] = m.group(1)
                        m = re.search(r"netmask\s+([\d.]+)", wlan_out)
                        if m:
                            wlan_info["netmask"] = m.group(1)
                        m = re.search(r"ether\s+(([0-9a-fA-F]{2}:){5}[0-9a-fA-F]{2})", wlan_out)
                        if m:
                            wlan_info["mac"] = m.group(1)
                        result["wlan0"] = wlan_info
                except (OSError, subprocess.SubprocessError):
                    pass

        elif "Permission denied" in result.get("stderr", ""):
            result["status"] = STATUS_BLOCKED
            result["details"] = "Permission denied."
        else:
            # ifconfig failed — try ip addr
            result["method"] = "ip addr"
            result["command"] = "ip addr"
            try:
                ip_proc = subprocess.run(
                    ["ip", "addr"],
                    capture_output=True, text=True, timeout=5, check=False
                )
                result["returncode"] = ip_proc.returncode
                result["stdout"] = ip_proc.stdout.strip()
                result["stderr"] = ip_proc.stderr.strip()

                if ip_proc.returncode == 0 and result["stdout"]:
                    result["status"] = STATUS_AVAILABLE
                    for line in result["stdout"].splitlines():
                        if line.strip() and line[0].isdigit():
                            parts = line.strip().split(":")
                            if len(parts) >= 2:
                                iface = parts[1].strip().split("@")[0]
                                result["interfaces"].append(iface)
            except (OSError, subprocess.SubprocessError):
                pass

    except FileNotFoundError:
        result["status"] = STATUS_UNAVAILABLE
        result["details"] = "'ifconfig' not found."
    except subprocess.TimeoutExpired:
        result["status"] = STATUS_BLOCKED
        result["details"] = "Command timed out."
    except OSError as e:
        result["status"] = STATUS_BLOCKED
        result["details"] = f"OS error: {e}"

    return result


def main() -> None:
    print("=" * 64)
    print("  LAB-004: ARP Environment Inspection")
    print("  Localhost-only — no network probing")
    print("=" * 64)

    results = []

    # 1. Interface information
    separator("1. Interface Information")
    iface_result = check_interface_info()
    results.append(iface_result)
    print(f"  Method:    {iface_result['method']}")
    print(f"  Status:    {iface_result['status']}")
    if iface_result["interfaces"]:
        print(f"  Interfaces found: {', '.join(iface_result['interfaces'])}")
    if iface_result["wlan0"]:
        print(f"  wlan0 details:")
        for k, v in iface_result["wlan0"].items():
            print(f"    {k}: {v}")
    if iface_result["details"]:
        print(f"  Detail:    {iface_result['details']}")
    if iface_result["stdout"]:
        print()
        print("  Raw output:")
        for line in iface_result["stdout"].splitlines()[:20]:
            print(f"    {line}")

    # 2. ip neigh
    separator("2. ip neigh (Neighbor Table)")
    ip_neigh = check_command("ip", ["neigh"])
    results.append(ip_neigh)
    print(f"  Status:    {ip_neigh['status']}")
    if ip_neigh["details"]:
        print(f"  Detail:    {ip_neigh['details']}")
    if ip_neigh["stdout"]:
        print()
        for line in ip_neigh["stdout"].splitlines():
            print(f"    {line}")

    # 3. arp -n
    separator("3. arp -n (ARP Cache)")
    arp_cmd = check_command("arp", ["-n"])
    results.append(arp_cmd)
    print(f"  Status:    {arp_cmd['status']}")
    if arp_cmd["details"]:
        print(f"  Detail:    {arp_cmd['details']}")
    if arp_cmd["stdout"]:
        print()
        for line in arp_cmd["stdout"].splitlines():
            print(f"    {line}")

    # 4. /proc/net/arp
    separator("4. /proc/net/arp (Kernel ARP Table)")
    proc_arp = check_proc_net_arp()
    results.append(proc_arp)
    print(f"  Status:    {proc_arp['status']}")
    if proc_arp["details"]:
        print(f"  Detail:    {proc_arp['details']}")
    if proc_arp["stdout"]:
        print()
        for line in proc_arp["stdout"].splitlines()[:20]:
            print(f"    {line}")

    # 5. Python socket — local hostname
    separator("5. Python Socket — Local Information")
    try:
        hostname = socket.gethostname()
        print(f"  Hostname:        {hostname}")
    except OSError:
        print(f"  Hostname:        (not available)")
    try:
        fqdn = socket.getfqdn()
        print(f"  FQDN:            {fqdn}")
    except OSError:
        print(f"  FQDN:            (not available)")

    # 6. Summary
    separator("6. Summary")
    print(f"  {'Method':<25} {'Status':<15}")
    print(f"  {'-'*25} {'-'*15}")
    for r in results:
        print(f"  {r['method']:<25} {r['status']:<15}")
    print()
    print("  Key:")
    print(f"    {STATUS_AVAILABLE:<14} — data successfully retrieved")
    print(f"    {STATUS_EMPTY:<14} — command worked but returned no data")
    print(f"    {STATUS_BLOCKED:<14} — permission denied or sandboxed")
    print(f"    {STATUS_UNAVAILABLE:<14} — tool not present on this system")
    print()
    print("=" * 64)


if __name__ == "__main__":
    main()
