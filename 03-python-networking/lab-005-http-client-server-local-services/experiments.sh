#!/usr/bin/env bash
# =============================================================================
# LAB-005: HTTP — Experiment Helper
# =============================================================================
# Prints instructions for each experiment. Does NOT execute anything.
#
# Usage:
#   bash experiments.sh              All instructions
#   bash experiments.sh server       Experiment A only
#   bash experiments.sh client       Experiments B-I only
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
    echo "  LAB-005: HTTP Client, Server, Local Services"
    echo "  ALL EXPERIMENTS ARE LOCALHOST-ONLY (127.0.0.1:8000)"
    echo "  NO INTERNET, NO LAN, NO SCANNING"
    echo ""

    section "Experiment A — Start HTTP Server"
    cmd "cd $LAB_DIR && python src/local_http_server.py &"
    echo "  Capture the Python PID (not the shell job PID)."
    echo "  Verify with:  python3 -c \"import socket; s=socket.socket(); s.connect(('127.0.0.1',8000)); print('OK'); s.close()\""
    echo ""

    section "Experiment B — Raw HTTP Client (Socket-Level)"
    cmd "cd $LAB_DIR && python src/raw_http_client.py /"
    cmd "cd $LAB_DIR && python src/raw_http_client.py /health"
    echo "  What to observe: ephemeral port, raw bytes, response headers/body."
    echo ""

    section "Experiment C — High-Level HTTP Client (urllib)"
    cmd "cd $LAB_DIR && python src/urllib_client.py"
    echo ""

    section "Experiment D — HEAD Request"
    cmd "cd $LAB_DIR && python src/raw_http_client.py /"
    echo "  (urllib_client.py also tests HEAD /)"
    echo "  Verify: 200 status, headers present, body length = 0."
    echo ""

    section "Experiment E — 404 Not Found"
    cmd "cd $LAB_DIR && python3 -c \"
import urllib.request as u
try: u.urlopen(u.Request('http://127.0.0.1:8000/does-not-exist'))
except Exception as e: print(e.code, e.reason)\""
    echo ""

    section "Experiment F — 405 Method Not Allowed"
    cmd "cd $LAB_DIR && python3 -c \"
import urllib.request as u
try: u.urlopen(u.Request('http://127.0.0.1:8000/', method='PUT'))
except Exception as e: print(e.code, e.reason)\""
    echo ""

    section "Experiment G — 413 Payload Too Large"
    cmd "cd $LAB_DIR && python3 -c \"
import urllib.request as u
body = 'A' * 4097
try: u.urlopen(u.Request('http://127.0.0.1:8000/echo', data=body.encode(), method='POST'))
except Exception as e: print(e.code, e.reason)\""
    echo ""

    section "Experiment H — HTTP Message Encoding (Offline)"
    cmd "cd $LAB_DIR && python src/request_builder.py"
    echo ""

    section "Experiment I — HTTP Response Parser (Offline)"
    cmd "cd $LAB_DIR && python src/response_parser.py"
    echo ""

    section "Cleanup"
    cmd "kill <PID>    # Use the exact PID from Experiment A"
    echo "  Verify:  python3 -c \"import socket; s=socket.socket(); s.connect(('127.0.0.1',8000))\""
    echo "  Expected: ConnectionRefusedError"
    echo ""
}

case "${1:-all}" in
    all)    all ;;
    server) section "Experiment A" && cmd "cd $LAB_DIR && python src/local_http_server.py" ;;
    client) all ;;
    *)      echo "Usage: bash experiments.sh [all|server|client]" ;;
esac
