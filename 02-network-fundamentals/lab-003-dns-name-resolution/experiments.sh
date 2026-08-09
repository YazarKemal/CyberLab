#!/usr/bin/env bash
# =============================================================================
# LAB-003: DNS Name Resolution — Experiment Helper
# =============================================================================
# Prints instructions for each experiment. Does NOT launch servers/clients.
#
# Usage:
#   bash experiments.sh              All instructions
#   bash experiments.sh resolver     Experiment A only
#   bash experiments.sh packet       Experiment B only
#   bash experiments.sh dns          Experiments C/D/E only
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
    echo "  LAB-003: DNS Name Resolution"
    echo "  ALL EXPERIMENTS ARE LOCALHOST-ONLY"
    echo ""
    echo "  You will need TWO Termux sessions open to:"
    echo "    $LAB_DIR"
    echo ""

    section "Experiment A — Local Name Resolution"
    cmd "cd $LAB_DIR && python src/local_resolution.py"
    echo "  What to observe: localhost resolution for AF_INET and AF_INET6,"
    echo "  /etc/hosts contents, discrepancies between hosts and getaddrinfo()."
    echo ""

    section "Experiment B — Offline DNS Packet Construction"
    cmd "cd $LAB_DIR && python src/dns_packet_demo.py"
    echo "  What to observe: QNAME encoding, header fields, packet structure,"
    echo "  byte-level breakdown of a DNS query."
    echo ""

    section "Experiment C — DNS A Query (127.0.0.1:53535)"
    echo "  Step 1 (Session 1): Start the educational DNS server:"
    cmd "cd $LAB_DIR && python src/dns_server.py --once --debug"
    echo "  Step 2 (Session 2): Query the A record:"
    cmd "cd $LAB_DIR && python src/dns_client.py lab.local A"
    echo ""

    section "Experiment D — DNS AAAA Query (127.0.0.1:53535)"
    echo "  Step 1 (Session 1): Restart server if needed:"
    cmd "cd $LAB_DIR && python src/dns_server.py --once --debug"
    echo "  Step 2 (Session 2): Query the AAAA record:"
    cmd "cd $LAB_DIR && python src/dns_client.py lab.local AAAA"
    echo ""

    section "Experiment E — Transaction IDs"
    echo "  Run multiple queries sequentially and observe TXID values:"
    cmd "cd $LAB_DIR && python src/dns_client.py lab.local A"
    cmd "cd $LAB_DIR && python src/dns_client.py lab.local A"
    cmd "cd $LAB_DIR && python src/dns_client.py lab.local A"
    echo "  Each query gets a random TXID. The response TXID must match."
    echo ""
}

case "${1:-all}" in
    all)       all ;;
    resolver)  section "Experiment A" && cmd "cd $LAB_DIR && python src/local_resolution.py" ;;
    packet)    section "Experiment B" && cmd "cd $LAB_DIR && python src/dns_packet_demo.py" ;;
    dns)       all ;;  # C/D/E all use the same tools
    *)         echo "Usage: bash experiments.sh [all|resolver|packet|dns]" ;;
esac
