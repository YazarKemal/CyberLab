#!/usr/bin/env bash
# =============================================================================
# LAB-004: ARP Local Resolution — Experiment Helper
# =============================================================================
# Prints instructions for each experiment. Does NOT execute anything.
#
# Usage:
#   bash experiments.sh              All instructions
#   bash experiments.sh env          Experiment A only
#   bash experiments.sh subnet       Experiment B only
#   bash experiments.sh eth          Experiment C only
#   bash experiments.sh arp          Experiment D only
#   bash experiments.sh model        Experiment E only
# =============================================================================

LAB_DIR="$(cd "$(dirname "$0")" && pwd)"

section() {
    echo ""
    echo "============================================"
    echo "  $1"
    echo "============================================"
    echo ""
}
cmd() { echo "  $ $1"; echo ""; }

all() {
    echo "  LAB-004: ARP Local Resolution"
    echo "  ALL EXPERIMENTS ARE LOCAL/OFFLINE ONLY"
    echo "  NO NETWORK TRANSMISSION"
    echo ""

    section "Experiment A — Device Network State (READ-ONLY)"
    cmd "cd $LAB_DIR && python src/arp_environment.py"
    echo "  What to observe:"
    echo "    - Which interfaces are visible"
    echo "    - Current wlan0 IPv4 (if available)"
    echo "    - Whether MAC address is visible"
    echo "    - Whether ip neigh is available"
    echo "    - Whether arp -n is available"
    echo "    - Whether /proc/net/arp is readable"
    echo "    - Distinguish BLOCKED vs EMPTY vs UNAVAILABLE"
    echo ""

    section "Experiment B — Subnet Mathematics (OFFLINE)"
    cmd "cd $LAB_DIR && python src/subnet_math.py"
    echo "  What to observe:"
    echo "    - Whether current wlan0 address is detected or historical"
    echo "    - Subnet mask, network address, broadcast address"
    echo "    - Binary decomposition (network bits vs host bits)"
    echo "    - Octet-by-octet breakdown"
    echo "    - Number of usable host addresses in the subnet"
    echo ""

    section "Experiment C — Ethernet Frame Encoding (OFFLINE)"
    cmd "cd $LAB_DIR && python src/ethernet_frame.py"
    echo "  What to observe:"
    echo "    - MAC address text ↔ bytes conversion"
    echo "    - EtherType constants (0x0800, 0x0806, 0x86DD)"
    echo "    - Ethernet header size (14 bytes)"
    echo "    - Header construction and parsing round-trip"
    echo "    - Broadcast MAC: ff:ff:ff:ff:ff:ff"
    echo ""

    section "Experiment D — ARP Packet Construction (OFFLINE)"
    cmd "cd $LAB_DIR && python src/arp_packet_demo.py"
    echo "  What to observe:"
    echo "    - ARP REQUEST: 28 bytes, THA=00:00:00:00:00:00"
    echo "    - ARP REPLY:   28 bytes, THA=requester's MAC"
    echo "    - Ethernet wrapper: 14 + 28 = 42 bytes total"
    echo "    - Broadcast vs unicast Ethernet destination"
    echo "    - All encode → decode round-trips"
    echo "    - Request vs reply side-by-side comparison"
    echo ""

    section "Experiment E — Routing Decision Model (OFFLINE)"
    cmd "cd $LAB_DIR && python src/resolution_model.py"
    echo "  What to observe:"
    echo "    - 10.122.10.50: inside subnet → direct ARP"
    echo "    - 8.8.8.8: outside subnet → ARP for gateway"
    echo "    - Mathematical network prefix check"
    echo "    - Why IPv6 uses NDP instead of ARP"
    echo ""
}

case "${1:-all}" in
    all)    all ;;
    env)    section "Experiment A" && cmd "cd $LAB_DIR && python src/arp_environment.py" ;;
    subnet) section "Experiment B" && cmd "cd $LAB_DIR && python src/subnet_math.py" ;;
    eth)    section "Experiment C" && cmd "cd $LAB_DIR && python src/ethernet_frame.py" ;;
    arp)    section "Experiment D" && cmd "cd $LAB_DIR && python src/arp_packet_demo.py" ;;
    model)  section "Experiment E" && cmd "cd $LAB_DIR && python src/resolution_model.py" ;;
    *)      echo "Usage: bash experiments.sh [all|env|subnet|eth|arp|model]" ;;
esac
