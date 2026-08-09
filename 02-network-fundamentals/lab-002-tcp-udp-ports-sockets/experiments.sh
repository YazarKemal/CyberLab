#!/usr/bin/env bash
# =============================================================================
# LAB-002: TCP, UDP, Ports and Sockets — Experiment Runner
# =============================================================================
# This script prints instructions for running each experiment. It does NOT
# launch servers or clients automatically — you control when they start/stop.
#
# Usage:
#   bash experiments.sh                Print all instructions
#   bash experiments.sh tcp            TCP experiment instructions only
#   bash experiments.sh port           Port check experiment instructions only
#   bash experiments.sh udp            UDP experiment instructions only
#   bash experiments.sh socket-types   Socket types demo only
#
# All experiments are localhost-only (127.0.0.1). No external hosts.
# =============================================================================

set -e

LAB_DIR="$(cd "$(dirname "$0")" && pwd)"
SRC_DIR="$LAB_DIR/src"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

section() {
    echo ""
    echo -e "${CYAN}============================================${NC}"
    echo -e "${CYAN}  $1${NC}"
    echo -e "${CYAN}============================================${NC}"
    echo ""
}

cmd() {
    echo -e "  ${GREEN}\$ ${1}${NC}"
    echo ""
}

note() {
    echo -e "  ${YELLOW}Note:${NC} $1"
    echo ""
}

# =============================================================================
# All experiments
# =============================================================================

all_instructions() {
    echo ""
    echo "  LAB-002: TCP, UDP, Ports and Sockets"
    echo "  ===================================="
    echo ""
    echo "  All experiments use 127.0.0.1 only. No external network access."
    echo ""
    echo "  You will need TWO (or three) Termux sessions open to $LAB_DIR"
    echo ""
    echo "  ┌─────────────────────────────────────┐"
    echo "  │  Session 1: Run servers             │"
    echo "  │  Session 2: Run clients and checks  │"
    echo "  └─────────────────────────────────────┘"
    echo ""

    section "Experiment 1 — TCP Server and Client"

    echo "  Step 1 (Session 1) — Start the TCP server:"
    cmd "cd $LAB_DIR && python src/tcp_server.py"

    echo "  Step 2 (Session 2) — Run the TCP client:"
    cmd "cd $LAB_DIR && python src/tcp_client.py"

    echo "  Step 3 (Session 2) — Run the client again (watch the source port):"
    cmd "cd $LAB_DIR && python src/tcp_client.py"

    echo "  Step 4 (Session 2) — Run the client a third time:"
    cmd "cd $LAB_DIR && python src/tcp_client.py"

    echo "  What to observe:"
    echo "    • Server prints the client's address and source port."
    echo "    • Client prints getsockname() (its own address) and getpeername() (server)."
    echo "    • Does the client's source port change between runs?"
    echo ""

    section "Experiment 2 — Open vs. Closed Port"

    echo "  Keep tcp_server.py running in Session 1."
    echo ""
    echo "  Step 1 (Session 2) — Check port 8080 (server is running → OPEN):"
    cmd "cd $LAB_DIR && python src/port_check.py 8080"

    echo "  Step 2 (Session 2) — Check port 8081 (nothing listening → CLOSED):"
    cmd "cd $LAB_DIR && python src/port_check.py 8081"

    echo "  Step 3 (Session 1) — Stop the server with Ctrl+C."
    echo ""
    echo "  Step 4 (Session 2) — Check port 8080 again (server stopped → now CLOSED):"
    cmd "cd $LAB_DIR && python src/port_check.py 8080"

    echo "  What to observe:"
    echo "    • Port 8080 is OPEN only while tcp_server.py is running."
    echo "    • Port 8081 is CLOSED — nothing is listening there."
    echo "    • After stopping the server, port 8080 becomes CLOSED."
    echo ""

    section "Experiment 3 — UDP Server and Client"

    echo "  Step 1 (Session 1) — Start the UDP server:"
    cmd "cd $LAB_DIR && python src/udp_server.py"

    echo "  Step 2 (Session 2) — Run the UDP client:"
    cmd "cd $LAB_DIR && python src/udp_client.py"

    echo "  Step 3 (Session 2) — Run the client again:"
    cmd "cd $LAB_DIR && python src/udp_client.py"

    echo "  Step 4 (Session 2) — Stop the server (Ctrl+C in Session 1),"
    echo "  then run the client once more:"
    cmd "cd $LAB_DIR && python src/udp_client.py"

    echo "  What to observe:"
    echo "    • UDP server does NOT call listen() or accept()."
    echo "    • recvfrom() returns both data AND the sender's address."
    echo "    • When the server is stopped, the client still 'sends' —"
    echo "      UDP is connectionless; there is no error unless you try to recv()."
    echo ""

    section "Experiment 4 — Socket Types"

    echo "  Run the socket demo (only one session needed):"
    cmd "cd $LAB_DIR && python src/socket_demo.py"

    echo "  What to observe:"
    echo "    • AF_INET, AF_INET6, AF_UNIX — address families."
    echo "    • SOCK_STREAM, SOCK_DGRAM — socket types."
    echo "    • IPv6 may or may not be available — the demo handles both cases."
    echo ""
}

# =============================================================================
# Per-experiment quick reference
# =============================================================================

tcp_instructions() {
    section "TCP Experiment"
    echo "  Session 1 (server):"
    cmd "cd $LAB_DIR && python src/tcp_server.py"
    echo "  Session 2 (client):"
    cmd "cd $LAB_DIR && python src/tcp_client.py"
}

port_instructions() {
    section "Port Check Experiment"
    echo "  First, ensure tcp_server.py is running in another session."
    echo ""
    echo "  Check open port:"
    cmd "cd $LAB_DIR && python src/port_check.py 8080"
    echo "  Check closed port:"
    cmd "cd $LAB_DIR && python src/port_check.py 8081"
    echo "  Stop the server, then check 8080 again:"
    cmd "cd $LAB_DIR && python src/port_check.py 8080"
}

udp_instructions() {
    section "UDP Experiment"
    echo "  Session 1 (server):"
    cmd "cd $LAB_DIR && python src/udp_server.py"
    echo "  Session 2 (client):"
    cmd "cd $LAB_DIR && python src/udp_client.py"
}

socket_types_instructions() {
    section "Socket Types Demo"
    cmd "cd $LAB_DIR && python src/socket_demo.py"
}

# =============================================================================
# Main
# =============================================================================

case "${1:-all}" in
    all)
        all_instructions
        ;;
    tcp)
        tcp_instructions
        ;;
    port)
        port_instructions
        ;;
    udp)
        udp_instructions
        ;;
    socket-types|socket|types)
        socket_types_instructions
        ;;
    *)
        echo "Usage: bash experiments.sh [all|tcp|port|udp|socket-types]"
        exit 1
        ;;
esac

echo ""
echo -e "${CYAN}============================================${NC}"
echo -e "${CYAN}  Remember: record your observations in observations.md${NC}"
echo -e "${CYAN}============================================${NC}"
echo ""
