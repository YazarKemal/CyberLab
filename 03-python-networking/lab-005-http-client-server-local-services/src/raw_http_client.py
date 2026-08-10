#!/usr/bin/env python3
"""
LAB-005: Raw HTTP Client (Socket-Level)
=========================================

Connects ONLY to 127.0.0.1:8000 using raw sockets.

Manually constructs an HTTP/1.1 GET request, sends it via TCP,
and receives/decodes the response.

Usage:
  python src/raw_http_client.py
  python src/raw_http_client.py /health
  python src/raw_http_client.py /info
"""

import socket
import sys

HOST = "127.0.0.1"
PORT = 8000
TIMEOUT = 5


def build_get(path: str) -> bytes:
    """Manually construct an HTTP/1.1 GET request."""
    request = (
        f"GET {path} HTTP/1.1\r\n"
        f"Host: localhost:{PORT}\r\n"
        f"User-Agent: CyberLab-LAB005\r\n"
        f"Connection: close\r\n"
        f"\r\n"
    )
    return request.encode("utf-8")


def main() -> None:
    path = sys.argv[1] if len(sys.argv) > 1 else "/"

    # 1. Build request
    request_bytes = build_get(path)

    print("=" * 64)
    print("  LAB-005: Raw HTTP Client (Socket-Level)")
    print(f"  Target: {HOST}:{PORT}")
    print("=" * 64)
    print()

    print("─" * 64)
    print("  1. HTTP Request (manually constructed)")
    print("─" * 64)
    print()
    print(f"  Request text:")
    for line in request_bytes.decode("utf-8").split("\r\n"):
        if line:
            print(f"    {line}")
        else:
            print(f"    (blank — end of headers)")
    print(f"  Request bytes: {len(request_bytes)}")
    print()

    # 2. Connect via TCP
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(TIMEOUT)

    print("─" * 64)
    print("  2. TCP Connection")
    print("─" * 64)
    print()

    before = sock.getsockname()
    print(f"  Before connect — getsockname(): {before[0]}:{before[1]}")

    sock.connect((HOST, PORT))

    after = sock.getsockname()
    remote = sock.getpeername()
    print(f"  After connect — getsockname():  {after[0]}:{after[1]}")
    print(f"  Remote endpoint — getpeername(): {remote[0]}:{remote[1]}")
    print()

    # 3. Send request
    print("─" * 64)
    print("  3. Send Request")
    print("─" * 64)
    print()
    sock.sendall(request_bytes)
    print(f"  Sent {len(request_bytes)} bytes to {HOST}:{PORT}")
    print()

    # 4. Receive response
    print("─" * 64)
    print("  4. Receive Response")
    print("─" * 64)
    print()

    response = b""
    try:
        while True:
            chunk = sock.recv(4096)
            if not chunk:
                break
            response += chunk
    except socket.timeout:
        pass

    sock.close()
    print(f"  Received {len(response)} bytes")
    print()

    # 5. Display response
    print("─" * 64)
    print("  5. Response (decoded)")
    print("─" * 64)
    print()

    text = response.decode("utf-8", errors="replace")
    lines = text.split("\r\n")
    in_body = False
    for line in lines:
        if not in_body and line == "":
            in_body = True
            print(f"    (blank — header/body separator)")
        elif line:
            print(f"    {line}")

    print()
    print("=" * 64)
    print(f"  Raw client complete. {len(request_bytes)}B sent, {len(response)}B received.")
    print("=" * 64)


if __name__ == "__main__":
    main()
