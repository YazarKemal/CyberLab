#!/usr/bin/env python3
"""
LAB-002: Educational Port Checker (Localhost Only)
===================================================

Checks whether a TCP port on 127.0.0.1 is OPEN or CLOSED by attempting a
TCP connect(). This is the simplest possible check — a single connect()
call — and it works because of how the kernel responds to SYN packets:

  OPEN PORT:   Server has called listen() on this port.
               Client sends SYN → Server sends SYN-ACK → Client sends ACK.
               connect() succeeds. The three-way handshake completes.

  CLOSED PORT: No process is listening on this port.
               Client sends SYN → Kernel sends RST (reset).
               connect() raises ConnectionRefusedError.

This is NOT a port scanner. It:
  - Only checks one port at a time.
  - Only checks 127.0.0.1 (hard-coded).
  - Uses a full TCP connect (completes the handshake).
  - Does NOT support subnet scanning, remote hosts, SYN scanning, or
    any form of evasion.

Usage:
  python src/port_check.py <port>

Example:
  python src/port_check.py 8080    # Check if tcp_server.py is running
  python src/port_check.py 8081    # Check if anything is on 8081
"""

import socket
import sys


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

HOST = "127.0.0.1"          # LOCALHOST ONLY — hard-coded, cannot be changed
TIMEOUT = 2                  # Seconds to wait for connect() to complete


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    if len(sys.argv) != 2:
        print("Usage: python src/port_check.py <port>")
        print("Example: python src/port_check.py 8080")
        print()
        print("This tool ONLY checks 127.0.0.1 (localhost).")
        print("It does NOT scan remote hosts or networks.")
        sys.exit(1)

    try:
        port = int(sys.argv[1])
    except ValueError:
        print(f"ERROR: '{sys.argv[1]}' is not a valid port number.")
        sys.exit(1)

    if port < 1 or port > 65535:
        print(f"ERROR: Port must be between 1 and 65535, not {port}.")
        sys.exit(1)

    print(f"Checking TCP port {port} on {HOST}...")
    print()

    # ---- 1. Create a TCP socket ----
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(TIMEOUT)

    try:
        # ---- 2. Attempt to connect ----
        # connect() triggers the TCP three-way handshake:
        #   Our host → 127.0.0.1:port : SYN
        #
        # If a process is LISTENING on that port:
        #   127.0.0.1:port → Our host : SYN-ACK
        #   Our host → 127.0.0.1:port : ACK
        #   connect() returns successfully → PORT IS OPEN
        #
        # If NO process is listening:
        #   127.0.0.1:port → Our host : RST (reset)
        #   connect() raises ConnectionRefusedError → PORT IS CLOSED
        sock.connect((HOST, port))

        # If we get here, the handshake succeeded.
        print(f"Port {port}: OPEN")
        print()
        print("A TCP three-way handshake completed successfully.")
        print(f"This means a process is LISTENING on {HOST}:{port}.")
        print()
        print("Our connection details:")
        print(f"  Local:  {sock.getsockname()[0]}:{sock.getsockname()[1]}")
        print(f"  Remote: {sock.getpeername()[0]}:{sock.getpeername()[1]}")

    except ConnectionRefusedError:
        # The kernel sent back RST — nothing is listening.
        print(f"Port {port}: CLOSED")
        print()
        print("The kernel responded with RST (reset).")
        print(f"No process is listening on {HOST}:{port}.")
        print()
        print("What happened at the protocol level:")
        print(f"  1. We sent SYN to {HOST}:{port}")
        print(f"  2. The kernel checked: is anyone listening on port {port}?")
        print(f"  3. Answer: NO → kernel sent RST back to us.")
        print(f"  4. Our connect() raised ConnectionRefusedError.")

    except socket.timeout:
        # No response at all — the port might be filtered (firewall).
        print(f"Port {port}: FILTERED (timeout)")
        print()
        print("No response received. The port may be blocked by a firewall.")
        print("(On localhost, this is unusual — it may indicate a kernel")
        print("configuration that drops rather than rejects packets.)")

    finally:
        sock.close()


if __name__ == "__main__":
    main()
