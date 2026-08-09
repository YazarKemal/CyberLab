#!/usr/bin/env python3
"""
LAB-002: TCP Client
===================

Connects to a TCP server on 127.0.0.1:<port>, sends a message, receives
the response, and displays both endpoints of the connection.

This client demonstrates:
  - socket()      — create a socket
  - connect()     — initiate the TCP three-way handshake (SYN → SYN-ACK → ACK)
  - sendall()     — send data reliably
  - recv()        — receive the server's response
  - getsockname() — "what is MY address and port?"
  - getpeername() — "what is the SERVER's address and port?"
  - close()       — tear down the connection (sends FIN)
  - Ephemeral ports — the OS assigns a temporary source port automatically

Usage:
  python src/tcp_client.py [port]

Default port: 8080
Target is ALWAYS 127.0.0.1 (localhost only).
"""

import socket
import sys


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

HOST = "127.0.0.1"          # Loopback only — never connect to external hosts
DEFAULT_PORT = 8080


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    port = int(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_PORT

    # ---- 1. Create the socket ----
    # AF_INET = IPv4, SOCK_STREAM = TCP
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    print(f"Connecting to {HOST}:{port}...")

    try:
        # ---- 2. Connect to the server ----
        # connect() triggers the TCP three-way handshake:
        #   Client → Server: SYN
        #   Server → Client: SYN-ACK
        #   Client → Server: ACK
        #
        # When connect() returns, the handshake is complete and the connection
        # is ESTABLISHED. The kernel also assigns an EPHEMERAL SOURCE PORT if
        # we haven't called bind() (which we haven't — this is normal).
        client_socket.connect((HOST, port))

        # ---- 3. Inspect both ends of the connection ----
        # getsockname() = MY local address (IP + source port)
        #                 The source port was assigned by the OS.
        # getpeername() = the REMOTE address (server's IP + port)
        my_addr = client_socket.getsockname()
        peer_addr = client_socket.getpeername()

        print(f"Connected!")
        print(f"  My local address (getsockname):  {my_addr[0]}:{my_addr[1]}")
        print(f"  Server address  (getpeername):  {peer_addr[0]}:{peer_addr[1]}")
        print()

        print("TCP four-tuple for this connection:")
        print(f"  ({my_addr[0]}:{my_addr[1]})  ↔  ({peer_addr[0]}:{peer_addr[1]})")
        print(f"   ^-- source (ephemeral)        ^-- destination (server)")
        print()

        # ---- 4. Send a message ----
        # sendall() guarantees all bytes are delivered (or raises an error).
        message = "Hello from TCP client!"
        print(f"Sending: {message}")
        client_socket.sendall(message.encode("utf-8"))

        # ---- 5. Receive the response ----
        # recv(1024) reads up to 1024 bytes from the server.
        # It blocks until data arrives or the server closes the connection.
        response = client_socket.recv(1024)
        print(f"Server response: {response.decode('utf-8')}")

    except ConnectionRefusedError:
        print(f"ERROR: Connection refused — is the TCP server running on port {port}?")
        sys.exit(1)

    except socket.timeout:
        print("ERROR: Connection timed out.")
        sys.exit(1)

    finally:
        # ---- 6. Close the socket ----
        # Sends FIN to the server, triggering the connection teardown:
        #   Client → Server: FIN
        #   Server → Client: FIN-ACK
        #   Client → Server: ACK
        client_socket.close()
        print()
        print("Connection closed.")


if __name__ == "__main__":
    main()
