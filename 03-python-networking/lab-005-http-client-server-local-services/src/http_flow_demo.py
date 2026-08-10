#!/usr/bin/env python3
"""
LAB-005: HTTP Flow Demo
========================

Prints the conceptual flow from client application through TCP
to the HTTP server and back. No sockets — pure documentation.

Also demonstrates the full resolution chain from previous labs:

  LAB-002: TCP sockets
       ↓
  LAB-003: DNS / hostname resolution
       ↓
  LAB-004: ARP / local address resolution
       ↓
  LAB-005: HTTP application protocol

Usage:
  python src/http_flow_demo.py
"""


def main() -> None:
    print("=" * 64)
    print("  LAB-005: HTTP Flow Demo")
    print("  Conceptual — no sockets used")
    print("=" * 64)

    # ── Full chain ───────────────────────────────────────────────────
    print()
    print("╔" + "═" * 62 + "╗")
    print("║" + "  THE FULL CHAIN: Browser to Server".center(62) + "║")
    print("╚" + "═" * 62 + "╝")
    print()
    print("""
  Browser / Client Application
          |
          | URL: http://127.0.0.1:8000/health
          v
  Hostname Resolution
          |
          | For localhost: /etc/hosts → 127.0.0.1 (LAB-003)
          | No DNS query needed — local resolution
          v
  IP Address: 127.0.0.1
          |
          | TCP connection (LAB-002)
          | Client: 127.0.0.1:<ephemeral>
          | Server: 127.0.0.1:8000
          v
  HTTP Request (LAB-005)
          |
          | GET /health HTTP/1.1
          | Host: localhost:8000
          | Connection: close
          |
          v
  Server Application
          |
          | Process request
          | Route: /health → 200 OK
          v
  HTTP Response (LAB-005)
          |
          | HTTP/1.1 200 OK
          | Content-Type: text/plain
          | Content-Length: 7
          |
          | healthy
          v
  Client receives response
""")

    # ── Protocol stack ────────────────────────────────────────────────
    print("╔" + "═" * 62 + "╗")
    print("║" + "  PROTOCOL STACK (LAB-005)".center(62) + "║")
    print("╚" + "═" * 62 + "╝")
    print()
    print("""
  ┌─────────────────────────┐
  │  HTTP                   │  Application Layer
  │  GET / POST / status    │  (This lab)
  └───────────┬─────────────┘
              │
  ┌───────────▼─────────────┐
  │  TCP                    │  Transport Layer
  │  reliable byte stream   │  (LAB-002)
  │  port 8000              │
  └───────────┬─────────────┘
              │
  ┌───────────▼─────────────┐
  │  IPv4                   │  Network Layer
  │  127.0.0.1              │  (LAB-001)
  └───────────┬─────────────┘
              │
  ┌───────────▼─────────────┐
  │  Loopback               │  Link Layer
  │  lo interface           │
  └─────────────────────────┘
""")

    # ── HTTP message structure ────────────────────────────────────────
    print("╔" + "═" * 62 + "╗")
    print("║" + "  HTTP MESSAGE STRUCTURE".center(62) + "║")
    print("╚" + "═" * 62 + "╝")
    print()
    print("""
  Request:
  ┌─────────────────────────┐
  │ GET /health HTTP/1.1    │ ← Request line (method, path, version)
  ├─────────────────────────┤
  │ Host: localhost:8000    │ ← Headers (key: value)
  │ User-Agent: CyberLab    │
  │ Connection: close       │
  ├─────────────────────────┤
  │                         │ ← Blank line (\\r\\n\\r\\n)
  ├─────────────────────────┤
  │ (optional body)         │ ← Body (not present for GET)
  └─────────────────────────┘

  Response:
  ┌─────────────────────────┐
  │ HTTP/1.1 200 OK         │ ← Status line (version, code, reason)
  ├─────────────────────────┤
  │ Content-Type: text/plain│ ← Headers
  │ Content-Length: 7       │
  │ Connection: close       │
  ├─────────────────────────┤
  │                         │ ← Blank line (\\r\\n\\r\\n)
  ├─────────────────────────┤
  │ healthy                 │ ← Body
  └─────────────────────────┘
""")

    # ── Client/Server ports ───────────────────────────────────────────
    print("╔" + "═" * 62 + "╗")
    print("║" + "  CLIENT / SERVER PORTS".center(62) + "║")
    print("╚" + "═" * 62 + "╝")
    print()
    print("""
  Client                          Server
  ──────                          ──────
  Source IP:      127.0.0.1       Bind IP:     127.0.0.1
  Source Port:    <ephemeral>     Bind Port:   8000 (our lab port)

  The OS assigns the client an ephemeral (temporary) source port.
  Each new TCP connection gets a different ephemeral port.

  HTTP default port:  80  (not used here — requires root)
  HTTPS default port: 443 (not used here — TLS not implemented)

  This lab intentionally uses port 8000 to avoid root requirements.
""")

    # ── Stateless HTTP ────────────────────────────────────────────────
    print("╔" + "═" * 62 + "╗")
    print("║" + "  STATELESS PROTOCOL".center(62) + "║")
    print("╚" + "═" * 62 + "╝")
    print()
    print("""
  HTTP is a stateless protocol. Each request/response exchange is
  independent. The server does not remember previous requests from
  the same client.

  State (like login sessions, shopping carts) is built on top of HTTP
  using mechanisms like:
    - Cookies (Set-Cookie / Cookie headers)
    - Session tokens
    - URL parameters

  These are NOT implemented in LAB-005.
""")

    # ── Red / Victim / Blue ───────────────────────────────────────────
    print("╔" + "═" * 62 + "╗")
    print("║" + "  RED TEAM / VICTIM / BLUE TEAM VIEW".center(62) + "║")
    print("╚" + "═" * 62 + "╝")
    print()
    print("""
  RED TEAM VIEW (attacker perspective — conceptual only):

    An attacker who can observe or modify the network sees:
    - HTTP method and path (GET /admin, POST /login)
    - Headers (User-Agent, Cookie values)
    - Request/response bodies (plaintext — no encryption)

    This is why HTTPS (HTTP over TLS) exists.
    NO attack is performed in this lab.

  VICTIM VIEW (service perspective):

    Our server sees exactly what arrives:
    - Client IP: 127.0.0.1 (always, since we only bind localhost)
    - Method: GET, HEAD, POST
    - Path: /, /health, /info, /echo
    - Headers and body

    The server logs: timestamp, client IP, method, path, status.

  BLUE TEAM VIEW (defender perspective):

    From server logs, a defender can observe:
    - Who connected (127.0.0.1 — localhost only)
    - What method was used (GET, POST, etc.)
    - What path was requested
    - What HTTP status was returned
    - When the request occurred (timestamp)

    Suspicious patterns a defender might look for:
    - Repeated 404 responses (directory enumeration)
    - Repeated 405 responses (method probing)
    - Unusually large request bodies
    - Unexpected paths or methods

    Our lab logs these fields safely for educational observation.
""")

    print("=" * 64)
    print("  Flow demo complete.")
    print("=" * 64)


if __name__ == "__main__":
    main()
