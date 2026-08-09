#!/usr/bin/env bash
# =============================================================================
# LAB-001: Know Your Host — Shell Inspection Commands
# =============================================================================
# Purpose: Inspect THIS device's network environment using safe, local-only
#          commands. No external hosts are contacted. No packages are installed.
#
# Usage:   bash commands.sh
#          Or run individual sections by copying commands into your terminal.
#
# Platform: Android / Termux — some commands may be restricted or unavailable.
#           Each section handles missing tools gracefully.
# =============================================================================

set -e  # Exit on error (but we handle expected failures section by section)

echo "============================================"
echo "  LAB-001: Know Your Host — Shell Inspection"
echo "  $(date)"
echo "============================================"
echo ""

# ------------------------------------------------------------------
# 1. OPERATING SYSTEM AND KERNEL
# ------------------------------------------------------------------
# uname prints system information:
#   -a  : all info (kernel name, hostname, kernel release, version, machine, OS)
#   -r  : kernel release only
#   -m  : machine hardware name (e.g., aarch64 for 64-bit ARM)
echo "--- 1. System Information ---"
echo ""
echo "\$ uname -a"
uname -a 2>/dev/null || echo "(uname not available)"

echo ""
echo "\$ uname -r"
uname -r 2>/dev/null || echo "(uname not available)"

echo ""
echo "\$ uname -m"
uname -m 2>/dev/null || echo "(uname not available)"

echo ""
echo "\$ whoami"
whoami 2>/dev/null || echo "(whoami not available)"

echo ""
# Android uses a special hostname path; try both
echo "\$ hostname"
hostname 2>/dev/null || cat /proc/sys/kernel/hostname 2>/dev/null || echo "(hostname not available)"

echo ""

# ------------------------------------------------------------------
# 2. NETWORK INTERFACES
# ------------------------------------------------------------------
# "ip addr show" is the modern Linux command for interface inspection.
# It replaces the older "ifconfig" (deprecated, may not exist on Android).
#
# Key fields in the output:
#   inet  <ip>/<prefix>     → IPv4 address with CIDR prefix length
#   inet6 <ip>/<prefix>     → IPv6 address
#   link/ether <mac>        → MAC (hardware) address
#   mtu <bytes>             → Maximum Transmission Unit
#   state UP/DOWN           → Interface state
#   LOOPBACK                → Flag indicating loopback interface
echo "--- 2. Network Interfaces ---"
echo ""
echo "\$ ip addr show"
ip addr show 2>/dev/null || {
    echo "(ip command not found — trying ifconfig)"
    ifconfig 2>/dev/null || echo "(no interface inspection tool available)"
}

echo ""

# ------------------------------------------------------------------
# 2b. Interface statistics from /proc
# ------------------------------------------------------------------
# /proc/net/dev contains byte/packet counters per interface.
# This is a kernel-provided file — no tools needed.
echo "--- 2b. Interface Statistics (from /proc/net/dev) ---"
echo ""
echo "\$ cat /proc/net/dev"
cat /proc/net/dev 2>/dev/null || echo "(cannot read /proc/net/dev — permission denied)"

echo ""
echo "Columns: bytes-recv packets-recv errs-recv drop-recv | bytes-sent packets-sent errs-sent drop-sent"

echo ""

# ------------------------------------------------------------------
# 3. ROUTING TABLE
# ------------------------------------------------------------------
# "ip route show" displays the kernel's routing table.
# "default via <ip>" is the default gateway.
echo "--- 3. Routing Table and Default Gateway ---"
echo ""
echo "\$ ip route show"
ip route show 2>/dev/null || {
    echo "(ip command not found — trying route)"
    route -n 2>/dev/null || echo "(no routing tool available)"
}

echo ""
echo "Look for: 'default via <IP> dev <interface>' — that<BIT>s your gateway."

# Alternative: read /proc/net/route (hex-encoded, but always available)
echo ""
echo "\$ cat /proc/net/route (hex-encoded routing table)"
cat /proc/net/route 2>/dev/null || echo "(cannot read /proc/net/route)"

echo ""

# ------------------------------------------------------------------
# 4. DNS CONFIGURATION
# ------------------------------------------------------------------
# /etc/resolv.conf lists DNS nameservers.
# On Android, DNS may also be configured via properties or netd.
echo "--- 4. DNS Configuration ---"
echo ""
echo "\$ cat /etc/resolv.conf"
cat /etc/resolv.conf 2>/dev/null || echo "(cannot read /etc/resolv.conf)"

echo ""
# Try Android-specific DNS properties
echo "\$ getprop net.dns1"
getprop net.dns1 2>/dev/null || echo "(getprop not available)"


echo ""
echo "\$ getprop net.dns2"
getprop net.dns2 2>/dev/null || echo ""

echo ""

# ------------------------------------------------------------------
# 5. LOCAL HOSTS FILE
# ------------------------------------------------------------------
# /etc/hosts is checked BEFORE DNS for name resolution.
echo "--- 5. Local Hosts File ---"
echo ""
echo "\$ cat /etc/hosts"
cat /etc/hosts 2>/dev/null || echo "(cannot read /etc/hosts)"

echo ""

# ------------------------------------------------------------------
# 6. LISTENING SOCKETS
# ------------------------------------------------------------------
# "ss" (socket statistics) is the modern replacement for netstat.
#   -t : TCP only
#   -l : listening sockets
#   -n : numeric (don't resolve names — faster, more secure)
#   -p : show process (may need root)
echo "--- 6. Listening TCP Sockets ---"
echo ""
echo "\$ ss -tln"
ss -tln 2>/dev/null || {
    echo "(ss not found — trying netstat)"
    netstat -tln 2>/dev/null || echo "(no socket inspection tool available)"
}

echo ""
echo "Columns: State | Recv-Q | Send-Q | Local Address:Port | Peer Address:Port"

echo ""
# Alternative: read /proc/net/tcp (hex-encoded, needs decoding)
echo "\$ cat /proc/net/tcp (hex-encoded, listening ports only)"
cat /proc/net/tcp 2>/dev/null | awk 'NR==1 || $4=="0A" {print}' || echo "(cannot read /proc/net/tcp)"

echo ""

# ------------------------------------------------------------------
# 7. ARP CACHE
# ------------------------------------------------------------------
# The ARP cache maps IP addresses to MAC addresses on the local network.
# This only contains hosts we have recently communicated with.
echo "--- 7. ARP Cache (Neighbor Table) ---"
echo ""
echo "\$ ip neigh show"
ip neigh show 2>/dev/null || {
    echo "(ip command not found — trying arp)"
    arp -n 2>/dev/null || echo "(no ARP inspection tool available)"
}

echo ""
echo "STATE values: REACHABLE (recently used), STALE (aging), FAILED (unreachable)"

echo ""

# ------------------------------------------------------------------
# 8. PROTOCOL STATISTICS
# ------------------------------------------------------------------
# /proc/net/snmp contains SNMP counters for IP, TCP, UDP, ICMP.
echo "--- 8. Protocol Statistics (TCP, UDP from /proc/net/snmp) ---"
echo ""
echo "\$ cat /proc/net/snmp"
cat /proc/net/snmp 2>/dev/null || echo "(cannot read /proc/net/snmp)"

echo ""
echo "Key counters: InSegs (TCP segments received), OutSegs (sent),"
echo "RetransSegs (retransmissions — high values suggest network problems)"

echo ""

# ------------------------------------------------------------------
# 9. CONNECTIVITY SELF-CHECK (LOCAL ONLY)
# ------------------------------------------------------------------
# These do NOT contact any remote hosts. They test the local TCP/IP stack.
echo "--- 9. Local Connectivity Self-Check ---"
echo ""

echo "\$ ping -c 2 127.0.0.1 (IPv4 loopback)"
ping -c 2 -W 1 127.0.0.1 2>/dev/null || echo "(ping not available)"

echo ""

echo "\$ ping -c 2 ::1 (IPv6 loopback)"
ping -c 2 -W 1 ::1 2>/dev/null || echo "(IPv6 ping not available)"

echo ""

# ------------------------------------------------------------------
# 10. NETWORK FILESYSTEM TOUR (/proc/net/)
# ------------------------------------------------------------------
# The /proc filesystem exposes kernel networking state as virtual files.
# No tools required — just cat. However, Android may restrict some entries.
echo "--- 10. /proc/net/ Filesystem Tour ---"
echo ""

for f in /proc/net/arp /proc/net/dev /proc/net/route /proc/net/tcp /proc/net/udp /proc/net/tcp6 /proc/net/if_inet6; do
    echo "\$ cat $f"
    cat "$f" 2>/dev/null || echo "(cannot read $f — restricted on this device)"
    echo ""
done

echo "============================================"
echo "  Inspection complete."
echo "  Record your observations in observations.md"
echo "============================================"
