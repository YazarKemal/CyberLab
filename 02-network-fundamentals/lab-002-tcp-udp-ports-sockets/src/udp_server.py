#!/usr/bin/env python3
"""
LAB-002: UDP Echo Server
========================

Binds to 127.0.0.1:<port>, receives UDP datagrams, prints the sender's
address, and sends back a response.

This server demonstrates what UDP does NOT have:
  - No listen() — UDP is connectionless; there is no "listening" state.
  - No accept() — No per-client socket is created. One socket handles all.
  - No connection state — each datagram is independent.

Instead, the server:
  - Calls bind() to claim a port.
  - Calls recvfrom() to receive datagrams — this returns both the data
    AND the sender's address.
  - Calls sendto() to reply to that specific sender.

Compare this file with tcp_server.py to see exactly what TCP adds.

Usage:
  python src/udp_server.py [port]

Default port: 9090
All traffic is localhost-only.
"""

import socket
import sys


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

HOST = "127.0.0.1"
DEFAULT_PORT = 9090
BUFFER_SIZE = 1024


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    port = int(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_PORT

    # ---- 1. Create the socket ----
    # AF_INET  = IPv4
    # SOCK_DGRAM = UDP (connectionless, datagram-based)
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # ---- 2. Set SO_REUSEADDR ----
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    # ---- 3. Bind to a local address ----
    # Only bind() is needed. There is NO listen() and NO accept() for UDP.
    # After bind(), the socket can immediately receive datagrams from anyone
    # who sends to this (host, port).
    server_socket.bind((HOST, port))

    local_addr = server_socket.getsockname()
    print(f"UDP Server bound to {local_addr[0]}:{local_addr[1]}")
    print("Waiting for datagrams... (Ctrl+C to stop)")
    print()
    print("NOTE: UDP has no listen(), no accept(), no per-client socket.")
    print("      One socket receives datagrams from ALL senders.")
    print()

    try:
        while True:
            # ---- 4. Receive a datagram ----
            # recvfrom() returns a tuple:
            #   data — the raw bytes received (up to BUFFER_SIZE)
            #   addr — the sender's (ip, port)
            #
            # There is no connection — the kernel just delivers whatever
            # datagram arrives next, regardless of who sent it.
            data, client_addr = server_socket.recvfrom(BUFFER_SIZE)
            message = data.decode("utf-8")

            print(f"Received datagram from {client_addr[0]}:{client_addr[1]}")
            print(f"  Data: {message}")

            # ---- 5. Send a response ----
            # sendto() sends a datagram to a specific address.
            # Unlike TCP, there is no guarantee it arrives.
            response = f"Hello from UDP server! You said: {message}"
            server_socket.sendto(response.encode("utf-8"), client_addr)
            print(f"  Sent reply to {client_addr[0]}:{client_addr[1]}")
            print()

    except KeyboardInterrupt:
        print()
        print("Shutting down UDP server...")

    finally:
        server_socket.close()
        print("Server stopped.")


if __name__ == "__main__":
    main()
