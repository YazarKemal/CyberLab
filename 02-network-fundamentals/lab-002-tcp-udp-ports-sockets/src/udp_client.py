#!/usr/bin/env python3
"""
LAB-002: UDP Client
===================

Sends a UDP datagram to a server on 127.0.0.1:<port>, then waits for a reply.

This client demonstrates:
  - socket(AF_INET, SOCK_DGRAM) — create a UDP socket
  - sendto() — send a datagram to a specific (host, port)
  - recvfrom() — receive a datagram and learn who sent it
  - NO connect() — UDP is connectionless
  - NO persistent connection state

Compare this file with tcp_client.py to see exactly what TCP adds:
  - TCP calls connect() to establish a connection (handshake).
  - UDP just fires a datagram with sendto() — no setup, no handshake.
  - TCP uses send()/recv() on an established connection.
  - UDP uses sendto()/recvfrom() with explicit addresses each time.

Usage:
  python src/udp_client.py [port]

Default port: 9090
Target is ALWAYS 127.0.0.1 (localhost only).
"""

import socket
import sys


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

HOST = "127.0.0.1"
DEFAULT_PORT = 9090
TIMEOUT = 3  # seconds to wait for a reply before giving up


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    port = int(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_PORT

    # ---- 1. Create the socket ----
    # AF_INET = IPv4, SOCK_DGRAM = UDP
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # Set a timeout so we don't block forever if the server is down.
    # UDP is connectionless — if nobody is listening, sendto() still
    # "succeeds" (the datagram is sent into the void), but recvfrom()
    # would block forever without a timeout.
    client_socket.settimeout(TIMEOUT)

    # ---- 2. Check our local address ----
    # Since we didn't call bind(), the OS hasn't assigned a port yet.
    # getsockname() returns (0.0.0.0, 0) — no port assigned until we send.
    before_addr = client_socket.getsockname()
    print(f"Before sendto — getsockname(): {before_addr[0]}:{before_addr[1]}")
    print(f"  (No port assigned yet — OS assigns an ephemeral port on first send)")
    print()

    print(f"Sending datagram to {HOST}:{port}...")

    try:
        # ---- 3. Send a datagram ----
        # sendto() sends data AND specifies the destination.
        # The OS assigns an ephemeral source port at this moment.
        message = "Hello from UDP client!"
        client_socket.sendto(message.encode("utf-8"), (HOST, port))

        # ---- 4. Check our address again (now the OS has assigned a port) ----
        after_addr = client_socket.getsockname()
        print(f"After sendto — getsockname(): {after_addr[0]}:{after_addr[1]}")
        print(f"  (OS assigned ephemeral port {after_addr[1]})")
        print()

        # ---- 5. Wait for a reply ----
        # recvfrom() returns (data, sender_address). We learn who replied
        # from the returned address tuple — no prior connection needed.
        print("Waiting for reply...")
        data, server_addr = client_socket.recvfrom(1024)

        print(f"Received reply from {server_addr[0]}:{server_addr[1]}")
        print(f"  Message: {data.decode('utf-8')}")
        print()
        print("NOTE: Unlike TCP, there is no persistent connection.")
        print("      Each sendto()/recvfrom() is an independent datagram.")
        print("      The server does not 'remember' us between datagrams.")

    except socket.timeout:
        print(f"ERROR: No reply received within {TIMEOUT} seconds.")
        print("  This could mean:")
        print("    1. The UDP server is not running.")
        print("    2. The datagram was lost (UDP does not guarantee delivery).")
        print("  Unlike TCP, UDP has no built-in way to know if data arrived.")

    finally:
        client_socket.close()


if __name__ == "__main__":
    main()
