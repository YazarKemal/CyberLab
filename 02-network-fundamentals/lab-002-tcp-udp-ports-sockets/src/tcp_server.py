#!/usr/bin/env python3
"""
LAB-002: TCP Echo Server
========================

Binds to 127.0.0.1:<port>, listens for TCP connections, receives a UTF-8
message, sends back a response, and closes the connection.

This server demonstrates:
  - socket()  — create a socket
  - bind()    — assign a local address (127.0.0.1:8080)
  - listen()  — mark the socket as passive (accept incoming connections)
  - accept()  — block until a client connects, return a NEW socket
  - recv()    — read data from the connected client
  - sendall() — send data back to the client
  - close()   — tear down the connection
  - SO_REUSEADDR — allow re-binding to a recently-used port
  - Graceful shutdown on Ctrl+C (KeyboardInterrupt)

Usage:
  python src/tcp_server.py [port]

Default port: 8080
All connections are localhost-only.
"""

import socket
import sys


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

HOST = "127.0.0.1"          # Loopback only — never bind to external interfaces
DEFAULT_PORT = 8080
BACKLOG = 5                  # Maximum queued connections before refusing


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    port = int(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_PORT

    # ---- 1. Create the socket ----
    # AF_INET  = IPv4
    # SOCK_STREAM = TCP (reliable, ordered, connection-oriented)
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # ---- 2. Set SO_REUSEADDR ----
    # Without this, restarting the server quickly after closing may fail with
    # "Address already in use" because the port is in TIME_WAIT state.
    # SO_REUSEADDR tells the kernel: it's okay to re-bind to this port.
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    # ---- 3. Bind to a local address ----
    # This says: "I will receive data on 127.0.0.1:port."
    # Only processes on this device can connect (loopback is not routable).
    server_socket.bind((HOST, port))

    # ---- 4. Listen for connections ----
    # Mark the socket as a PASSIVE socket. The kernel will now:
    #   1. Accept SYN packets on this port.
    #   2. Complete the three-way handshake on our behalf.
    #   3. Queue established connections until we accept() them.
    # BACKLOG = maximum queue length.
    server_socket.listen(BACKLOG)

    local_addr = server_socket.getsockname()
    print(f"TCP Server listening on {local_addr[0]}:{local_addr[1]}")
    print(f"Backlog: {BACKLOG}")
    print("Waiting for connections... (Ctrl+C to stop)")
    print()

    try:
        while True:
            # ---- 5. Accept a connection ----
            # accept() BLOCKS until a client connects. It returns:
            #   conn  — a NEW socket dedicated to THIS client
            #   addr  — the client's (ip, port) tuple
            #
            # The original server_socket continues listening. The conn socket
            # is used for actual communication with this specific client.
            conn, client_addr = server_socket.accept()

            print(f"Connection from {client_addr[0]}:{client_addr[1]}")

            # Show both ends of the connection
            server_side = conn.getsockname()
            print(f"  Server side: {server_side[0]}:{server_side[1]}")
            print(f"  Client side: {client_addr[0]}:{client_addr[1]}")

            # ---- 6. Receive data ----
            # recv(1024) reads up to 1024 bytes. It blocks until data arrives
            # or the client closes. Returns b'' (empty bytes) on client close.
            data = conn.recv(1024)
            if data:
                message = data.decode("utf-8")
                print(f"  Received: {message}")

                # ---- 7. Send a response ----
                # sendall() guarantees ALL bytes are sent (may call send()
                # multiple times internally if the OS buffer is full).
                response = f"Hello from TCP server! You said: {message}"
                conn.sendall(response.encode("utf-8"))
                print(f"  Sent reply.")

            # ---- 8. Close the connection socket ----
            # Sends FIN to the client, starting the connection teardown.
            # Does NOT affect the listening socket.
            conn.close()
            print(f"  Connection closed.")
            print()

    except KeyboardInterrupt:
        print()
        print("Shutting down server...")

    finally:
        # ---- 9. Close the listening socket ----
        server_socket.close()
        print("Server stopped.")


if __name__ == "__main__":
    main()
