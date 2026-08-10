# Lab 005: HTTP — Client, Server, Local Services

- **Phase:** 03-python-networking
- **Date:** 2026-08-09
- **Environment:** Android tablet / Termux / Python 3.14.6
- **Scope:** localhost only (127.0.0.1:8000)
- **Status:** COMPLETE — experiments executed, results verified

---

## Overview

LAB-005 implements and explores the **Hypertext Transfer Protocol (HTTP/1.x)**
from first principles. We build an educational HTTP message builder/parser,
a local HTTP server with real routing, and two clients (raw socket and
high-level urllib). All communication is on localhost only — no internet,
no LAN, no scanning.

**This is the third protocol in the stack after TCP (LAB-002) and DNS
(LAB-003). Together they form the complete client-to-server chain:**

```
Browser/Client → URL → Hostname → DNS → IP → TCP → HTTP Request → Server → HTTP Response → Client
```

---

## Theory

### The Application Layer

The OSI model has seven layers. HTTP lives at **Layer 7 — the Application
Layer**. This is the layer closest to the end user. While TCP (Layer 4)
provides a reliable byte stream and IP (Layer 3) handles routing, HTTP
defines the *meaning* of those bytes: what the client wants and what the
server sends back.

```
┌─────────────────────────┐
│  HTTP                   │  Application Layer (This lab)
│  GET / POST / status    │
└───────────┬─────────────┘
            │
┌───────────▼─────────────┐
│  TCP                    │  Transport Layer (LAB-002)
│  reliable byte stream   │
│  port 8000              │
└───────────┬─────────────┘
            │
┌───────────▼─────────────┐
│  IPv4                   │  Network Layer (LAB-001)
│  127.0.0.1              │
└───────────┬─────────────┘
            │
┌───────────▼─────────────┐
│  Loopback               │  Link Layer
│  lo interface           │
└─────────────────────────┘
```

### What is HTTP?

HTTP (Hypertext Transfer Protocol) is a **request-response protocol** that
runs on top of TCP. A client opens a TCP connection to a server, sends an
HTTP request, and the server sends back an HTTP response. The connection
may then be closed or reused.

**Key properties of HTTP/1.x:**

| Property | Meaning |
|----------|---------|
| Text-based | Messages are human-readable ASCII text |
| Request-response | Client asks, server answers |
| Stateless | Each request is independent; server remembers nothing |
| CRLF line endings | Every line ends with `\r\n` (carriage return + line feed) |
| Headers + body | Metadata (headers) separated from data (body) by a blank line |

### HTTP Default Ports

| Protocol | Default Port | Why |
|----------|-------------|-----|
| HTTP | 80 | Standard port for unencrypted web traffic |
| HTTPS | 443 | Standard port for TLS-encrypted HTTP |

This lab uses port **8000** intentionally — ports below 1024 require root
privileges on Unix systems. Port 8000 is a common convention for
development HTTP servers.

### HTTP Message Structure

Every HTTP message follows this format:

```
Start-Line\r\n          ← Request line or Status line
Header-Name: value\r\n  ← Zero or more headers
Header-Name: value\r\n
\r\n                     ← Blank line (separator)
[optional body]         ← Raw bytes (length given by Content-Length)
```

#### Request Format

```
METHOD<SPACE>PATH<SPACE>HTTP/1.1\r\n
Header: value\r\n
\r\n
[body]
```

Example — a GET request:
```
GET /health HTTP/1.1\r\n
Host: localhost:8000\r\n
User-Agent: CyberLab-LAB005\r\n
Connection: close\r\n
\r\n
```

Example — a POST request with body:
```
POST /echo HTTP/1.1\r\n
Host: localhost:8000\r\n
Content-Type: text/plain\r\n
Content-Length: 19\r\n
User-Agent: CyberLab-LAB005\r\n
Connection: close\r\n
\r\n
hello from CyberLab
```

#### Response Format

```
HTTP/1.1<SPACE>STATUS-CODE<SPACE>REASON\r\n
Header: value\r\n
\r\n
[body]
```

Example:
```
HTTP/1.1 200 OK\r\n
Content-Type: text/plain\r\n
Content-Length: 7\r\n
Connection: close\r\n
\r\n
healthy
```

### HTTP Methods

HTTP methods (also called "verbs") tell the server what action the client
wants to perform:

| Method | Purpose | Has Body? | Safe? | Idempotent? |
|--------|---------|-----------|-------|-------------|
| GET | Retrieve a resource | No | Yes | Yes |
| HEAD | Like GET but no body in response | No | Yes | Yes |
| POST | Submit data to be processed | Yes | No | No |
| PUT | Create or replace a resource | Yes | No | Yes |
| DELETE | Remove a resource | May | No | Yes |
| PATCH | Partial update | Yes | No | No |
| OPTIONS | Ask which methods are supported | No | Yes | Yes |

- **Safe**: Does not modify server state (GET, HEAD, OPTIONS)
- **Idempotent**: Repeating the same request has the same effect (GET, PUT, DELETE)

In this lab we implement GET, HEAD, and POST. PUT, DELETE, PATCH, and
OPTIONS return 405 Method Not Allowed.

### HTTP Status Codes

Status codes are three-digit numbers grouped by the first digit:

| Range | Category | Examples |
|-------|----------|----------|
| 1xx | Informational | 100 Continue |
| 2xx | Success | 200 OK, 201 Created |
| 3xx | Redirection | 301 Moved Permanently, 302 Found |
| 4xx | Client Error | 400 Bad Request, 404 Not Found, 405 Method Not Allowed, 413 Payload Too Large |
| 5xx | Server Error | 500 Internal Server Error, 502 Bad Gateway |

This lab demonstrates:
- **200 OK**: Request succeeded
- **404 Not Found**: The requested path does not exist
- **405 Method Not Allowed**: The method is not supported for this path
- **413 Content Too Large**: The request body exceeds the server's limit. Status code 413 is defined by RFC 7231 as "Payload Too Large"; the reason phrase "Content Too Large" was observed in this Python environment.

### Important HTTP Headers

| Header | Direction | Purpose |
|--------|-----------|---------|
| Host | Request | Which hostname the request targets (required in HTTP/1.1) |
| User-Agent | Request | Identifies the client software |
| Content-Type | Both | The media type of the body (e.g., `text/plain`, `application/json`) |
| Content-Length | Both | The size of the body in bytes |
| Connection | Both | Controls connection persistence (`close` or `keep-alive`) |
| Server | Response | Identifies the server software |
| Date | Response | When the response was generated |

### URL, URI, Query String, Percent Encoding

- **URI** (Uniform Resource Identifier): A string that identifies a resource.
- **URL** (Uniform Resource Locator): A URI that also tells you *how to find*
  the resource (includes the scheme like `http://` and the host).
- **Query string**: The part after `?` in a URL — `?key=value&other=123`.
  Not used in this lab but essential knowledge.
- **Percent encoding**: Special characters in URLs are encoded as `%XX` where
  XX is the hex value of the byte. For example, space becomes `%20`.

### Stateless Protocol

HTTP is **stateless**. Each request-response exchange is independent. The
server does not remember anything about previous requests from the same
client.

This is a fundamental design choice:
- **Advantage**: Simple to implement, easy to scale horizontally.
- **Challenge**: How do we build things like login sessions and shopping
  carts?

State is built *on top of* HTTP using:
- **Cookies**: `Set-Cookie` (server → client) and `Cookie` (client → server) headers
- **Session tokens**: A random string the server issues; the client sends it back
- **URL parameters**: Embedding state in links (fragile, not recommended)

None of these are implemented in LAB-005 — our server is purely stateless.

### CRLF — The Line Ending

HTTP/1.x uses **CRLF** (`\r\n`, bytes `0x0D 0x0A`) as line endings. This comes
from the Telnet heritage of early internet protocols.

- `\r` (carriage return, CR, 0x0D): Move the cursor to the beginning of the line
- `\n` (line feed, LF, 0x0A): Move the cursor down one line

A **blank line** (`\r\n\r\n`) separates headers from the body. This is how
the parser knows where headers end and body begins.

### HTTP vs HTTPS

| Property | HTTP | HTTPS |
|----------|------|-------|
| Encryption | None (plaintext) | TLS encrypted |
| Default port | 80 | 443 |
| URL scheme | `http://` | `https://` |
| Certificate | None | Server presents X.509 certificate |
| Visibility | All traffic visible to observer | Only IP and port visible |

HTTP sends everything in plaintext. Anyone who can observe the network
(malicious Wi-Fi access point, compromised router, packet sniffer) can
read the full conversation: method, path, headers, cookies, body.

HTTPS wraps HTTP inside TLS (Transport Layer Security), which provides:
1. **Encryption**: No one can read the traffic.
2. **Authentication**: The server proves its identity with a certificate.
3. **Integrity**: The data cannot be modified in transit without detection.

This lab is HTTP-only. We note the security implications conceptually.

---

## The Full Chain: From Browser to Server

When you type `http://127.0.0.1:8000/health` into a browser (or
our client code), here is what happens:

```
Step 1: PARSE URL
  Scheme: http      → use HTTP protocol, port 8000
  Host:   127.0.0.1 → loopback IP (no DNS needed)
  Port:   8000      → explicit port
  Path:   /health   → the resource we want

Step 2: RESOLVE HOSTNAME (LAB-003)
  localhost → /etc/hosts → 127.0.0.1
  No DNS query needed for localhost.

Step 3: ESTABLISH TCP CONNECTION (LAB-002)
  Client creates a socket, OS assigns ephemeral port (e.g., 55800).
  TCP three-way handshake: SYN → SYN-ACK → ACK.
  Now we have a reliable byte stream between:
    127.0.0.1:55800 ←→ 127.0.0.1:8000

Step 4: SEND HTTP REQUEST (LAB-005)
  Client sends bytes over the TCP connection:
    GET /health HTTP/1.1\r\n
    Host: localhost:8000\r\n
    User-Agent: CyberLab-LAB005\r\n
    Connection: close\r\n
    \r\n

Step 5: SERVER PROCESSES REQUEST
  Server parses the request line: method=GET, path=/health, version=HTTP/1.1.
  Server parses headers: Host, User-Agent, Connection.
  Server routes: /health → do_GET → 200 OK with body "healthy".

Step 6: SEND HTTP RESPONSE
  Server sends bytes back over the same TCP connection:
    HTTP/1.0 200 OK\r\n
    Server: BaseHTTP/0.6 Python/3.14.6\r\n
    Date: Sun, 09 Aug 2026 17:53:44 GMT\r\n
    Content-Type: text/plain\r\n
    Content-Length: 7\r\n
    Connection: close\r\n
    \r\n
    healthy

Step 7: CLIENT RECEIVES RESPONSE
  Client reads bytes from the socket.
  Client parses: status=200, headers, body="healthy".
  Client displays or processes the result.

Step 8: CONNECTION CLOSED
  "Connection: close" → server closes the TCP connection.
  TCP four-way teardown: FIN → ACK ← FIN → ACK.
```

### Red Team / Victim / Blue Team Views

**Red Team (attacker perspective — conceptual only):**

An attacker who can observe the network sees plaintext:
- HTTP method and path (`GET /admin`, `POST /login`)
- Headers including `Cookie` values (session tokens!)
- Request and response bodies
- This is why HTTPS exists — to encrypt the entire HTTP conversation

**Victim (service perspective):**

Our server sees exactly what arrives:
- Client IP: 127.0.0.1 (always, because we bind localhost only)
- Method, path, headers, and body
- All requests are from our own device

**Blue Team (defender perspective):**

From server logs, a defender can observe:
- Timestamp of each request
- Client IP address (source)
- HTTP method used
- Path requested
- HTTP status code returned

Suspicious patterns a defender might look for:
- Repeated 404 responses → directory enumeration attempt
- Repeated 405 responses → method probing
- Unusually large request bodies → buffer overflow or DoS attempts
- Unexpected paths or methods → reconnaissance

### Security Concepts (Conceptual Only)

This is an educational lab — no attacks are performed. These concepts
are introduced for awareness:

- **Input validation**: Never trust client input. Validate method, path,
  headers, and body before processing. Our server validates path existence,
  method support, and body size (MAX_BODY = 4096).

- **Authentication and authorization**: HTTP itself provides no
  authentication. Real servers use mechanisms like session cookies, JWT
  tokens, or HTTP Basic Auth (Base64-encoded credentials in headers).

- **Sessions and cookies**: Since HTTP is stateless, servers use
  `Set-Cookie` headers to link requests from the same client into a
  session.

- **CORS** (Cross-Origin Resource Sharing): A browser security mechanism
  that controls which origins can access a server's resources. Not
  relevant on localhost but essential for web security.

- **CSRF** (Cross-Site Request Forgery): An attack where a malicious site
  tricks a user's browser into making unwanted requests to a server where
  the user is authenticated.

- **XSS** (Cross-Site Scripting): Injecting malicious scripts into web
  pages viewed by other users. Mitigated by proper output encoding.

- **SQL injection**: Inserting malicious SQL through HTTP parameters.
  Mitigated by parameterized queries. Not relevant to our in-memory server
  but a critical web security concept.

---

## Lab Structure

```
lab-005-http-client-server-local-services/
├── README.md                    ← This file
├── observations.md              ← VERIFIED experiment results
├── experiments.sh               ← Experiment helper (instructions only)
└── src/
    ├── http_message.py          ← Educational HTTP/1.x message builder/parser (292 lines)
    ├── local_http_server.py     ← Local HTTP server — 127.0.0.1:8000 only (187 lines)
    ├── raw_http_client.py       ← Raw socket HTTP client (134 lines)
    ├── urllib_client.py         ← High-level urllib HTTP client (133 lines)
    ├── request_builder.py       ← Offline HTTP request construction (91 lines)
    ├── response_parser.py       ← Educational HTTP response parser (112 lines)
    └── http_flow_demo.py        ← Conceptual diagrams and flow explanation (225 lines)
```

### Component Descriptions

#### http_message.py — Educational HTTP/1.x Message Helpers

Implements the core HTTP message primitives:
- `build_request_line(method, path, version)` — "GET / HTTP/1.1"
- `build_status_line(version, code, reason)` — "HTTP/1.1 200 OK"
- `build_headers(headers_dict)` — "Host: localhost\r\nConnection: close"
- `build_request(method, path, headers, body)` — Complete request as bytes
- `build_response(status, reason, headers, body)` — Complete response as bytes
- `parse_start_line(data)` — Extract method/path/version or version/code/reason
- `parse_headers(data, offset)` — Parse headers from raw bytes
- `parse_response(data)` — Full response → structured dict
- `hexdump(data, title)` — Formatted hex+ASCII dump for educational display

**Label: EDUCATIONAL HTTP/1.x PARSER — not RFC-complete.**

Constants:
- `CRLF = "\r\n"`
- `DOUBLE_CRLF = "\r\n\r\n"` — the header/body separator

#### local_http_server.py — Local HTTP Server

A real HTTP server using Python's `http.server` module:

| Setting | Value |
|---------|-------|
| Host | 127.0.0.1 (never 0.0.0.0) |
| Port | 8000 |
| Max body size | 4096 bytes |
| Framework | http.server.HTTPServer + BaseHTTPRequestHandler |

Routes:

| Method | Path | Response |
|--------|------|----------|
| GET | / | 200 — JSON `{"service":"CyberLab LAB-005","status":"ok"}` |
| GET | /health | 200 — text/plain `healthy` |
| GET | /info | 200 — JSON with lab metadata |
| HEAD | / | 200 — headers only, no body |
| POST | /echo | 200 — echoes the request body |
| Any | /anything-else | 404 — JSON error |
| PUT/DELETE/PATCH/OPTIONS | Any | 405 — JSON error |

Security properties:
- Binds **only** to 127.0.0.1 — not reachable from the network
- Body size limited to 4096 bytes
- No environment variables or secrets in responses
- No filesystem access or process information exposed

#### raw_http_client.py — Raw Socket Client

Manually constructs an HTTP/1.1 request and sends it via a raw TCP socket:
- Builds the request as a string with CRLF line endings
- Creates a TCP socket, connects to 127.0.0.1:8000
- Shows `getsockname()` before and after `connect()` (ephemeral port)
- Shows `getpeername()` after connect (server endpoint)
- Sends the request, receives the response, displays both

This is the educational "from scratch" approach — we see every byte.

#### urllib_client.py — High-Level Client

Uses Python's `urllib.request` to test all server endpoints:
- GET / — JSON status
- GET /health — plain text health check
- GET /info — lab information
- GET /does-not-exist — 404 test
- HEAD / — headers without body
- POST /echo — echo body back

This demonstrates the "professional tool" approach for comparison.

#### request_builder.py — Offline Request Construction

Builds HTTP requests without any network connection:
- GET /, HEAD /, GET /health, POST /echo
- Verifies CRLF line endings
- Calculates Content-Length for POST
- Reports byte counts and structure

#### response_parser.py — Educational Response Parser

Parses hardcoded HTTP responses into structured fields:
- 200 OK (text/plain)
- 200 OK (application/json)
- 404 Not Found
- HEAD-like response (status line + headers, no body)
- Each test case shows hexdump + parsed fields

#### http_flow_demo.py — Conceptual Flow

Prints ASCII diagrams of:
- The full chain: Browser → DNS → IP → TCP → HTTP → Server
- The protocol stack: HTTP / TCP / IP / Loopback
- HTTP request and response message structure
- Client/server ports and ephemeral port assignment
- Stateless protocol concept
- Red Team / Victim / Blue Team views

---

## Experiments

All nine experiments were executed. Results are documented in
`observations.md` with VERIFIED / INFERRED / NOT VERIFIED / LIMITATION
status marking.

| Experiment | Component | What It Tests |
|-----------|-----------|---------------|
| A | local_http_server.py | Start server, verify PID and port |
| B | raw_http_client.py | Raw TCP → HTTP GET request/response |
| C | urllib_client.py | High-level client, all endpoints |
| D | urllib_client.py | HEAD request — headers without body |
| E | — | 404 Not Found for unknown path |
| F | — | 405 Method Not Allowed for PUT |
| G | — | 413 Payload Too Large for oversized body |
| H | request_builder.py | Offline message encoding, CRLF verification |
| I | response_parser.py | Educational parser, 4 test cases |

**Key results:**
- Server PID 12085, bound to 127.0.0.1:8000
- Raw client ephemeral port: 55800
- All HTTP methods and status codes verified: 200, 404, 405, 413
- HEAD returned 0-byte body
- POST /echo correctly echoed the request body
- Our BaseHTTPRequestHandler configuration responded HTTP/1.0
- Content-Length matched actual body size for all responses

---

## Exercises

> These exercises test understanding, not memorization. For each, think
> about *why* before looking at the answer.

1. **What does CRLF stand for, and why does HTTP use it instead of just `\n`?**
   Explain the historical context.

2. **Why does this lab use port 8000 instead of port 80?** What would
   happen if we tried to bind to port 80 on this Android/Termux
   environment?

3. **What is the difference between GET and HEAD?** Write a scenario where
   HEAD is useful.

4. **In this lab, the server responded with HTTP/1.0 even when the client
   sent HTTP/1.1.** Why does Python's BaseHTTPRequestHandler default to
   HTTP/1.0? Is this a bug, or expected behavior for this configuration?

5. **What is an ephemeral port?** Why does the client not use port 8000
   as its source port?

6. **HTTP is described as "stateless."** What does this mean? Give an
   example of something that would be difficult to build on a stateless
   protocol without additional mechanisms.

7. **Look at the raw HTTP response bytes.** Where exactly is the blank
   line that separates headers from body? What would happen if the blank
   line were missing?

8. **Why does the POST request show fewer "Ends with CRLF CRLF: ✓" checks
   than GET?** Is this an error, or is it expected behavior?

9. **What is the purpose of the `Host` header in HTTP/1.1?** Why is it
   required even when connecting directly to an IP address?

10. **Explain the relationship between Content-Length and the body.** What
    happens if Content-Length is larger than the actual body? What if it's
    smaller?

11. **Our server's HTTP status line returned the reason phrase "Content
    Too Large" for status code 413.** The RFC 7231 reason phrase is
    "Payload Too Large." Why might our stdlib configuration report a
    different phrase? Is the reason phrase normative or advisory?

12. **What is the difference between `http://127.0.0.1:8000` and
    `https://127.0.0.1:8000`?** Why don't we use HTTPS in this lab?

13. **If you run `raw_http_client.py` twice in a row, will the ephemeral
    port be the same?** Explain why or why not.

14. **Draw the TCP three-way handshake for LAB-005.** Label the five key
    pieces of information: client IP, client port, server IP, server port,
    and the three TCP flags.

15. **What happens in our server if you send a GET request to `/` with a
    body?** Think about what the server reads and whether it would cause
    an error.

16. **Why does our server explicitly bind to 127.0.0.1 instead of
    0.0.0.0?** What is the security implication of binding to 0.0.0.0?

17. **If someone on the same Wi-Fi network tried to connect to
    `http://<our-tablet-IP>:8000/`, would it work?** Explain using what
    you know about our bind address.

18. **Compare `raw_http_client.py` with `urllib_client.py`.** What does
    urllib handle automatically that the raw client must do manually?
    This is the "Build Before Buying" comparison.

19. **Our `/info` endpoint returns JSON.** What kinds of information
    should a production server *never* include in an info/about endpoint?
    Why?

20. **Explain the full chain for `http://example.com/index.html`.** What
    happens at each layer: URL parsing, DNS resolution, TCP connection,
    HTTP request, server processing, HTTP response? (Conceptual — we
    don't connect to the internet in this lab.)

21. **What is the difference between HTTP and HTTPS in terms of what a
    network observer can see?** Be specific about each part of the
    message (method, path, headers, body).

22. **If you wanted to add a `DELETE /messages/<id>` endpoint to our
    server, what would you need to change?** Where would you add the
    handler? How would you extract the `<id>` from the path?

23. **Our server has `MAX_BODY = 4096`.** What happens if a legitimate
    client needs to send 10 KB of data? How would you handle large
    uploads in a production system?

24. **What HTTP status code should a server return if a client sends a
    request with `Transfer-Encoding: chunked` that the server doesn't
    understand?** What about a request with an HTTP method the server
    has never heard of?

25. **Explain how cookies enable state on top of a stateless protocol.**
    Walk through a login sequence: first request (POST /login), response
    (Set-Cookie), second request (GET /dashboard with Cookie header).

---

## Build Before Buying

This lab follows CyberLab's "Build Before Buying" philosophy:

| What We Built | Professional Equivalent | What We Learned |
|---------------|------------------------|-----------------|
| `http_message.py` | Full HTTP parser (httptools, http-parser) | CRLF, request line, status line, headers, body separation |
| `local_http_server.py` | nginx, Apache, gunicorn | Routing, method dispatch, status codes, Content-Type |
| `raw_http_client.py` | curl, wget | TCP sockets, request construction, response parsing |
| `request_builder.py` | HTTP client libraries | Message encoding, Content-Length calculation |
| `response_parser.py` | Browser/HTTP client response parser | Structured parsing, hexdump analysis |

**What the professional tools handle that ours doesn't:**
- Chunked transfer encoding
- Keep-alive connection reuse
- Pipelining (multiple requests on one connection)
- Full RFC 7230-7235 compliance
- TLS/HTTPS
- Compression (gzip, brotli)
- Cache control (ETag, If-Modified-Since)
- Range requests (partial content)
- CORS headers
- Authentication (Basic, Bearer, Digest)

---

## References

- **RFC 7230**: HTTP/1.1 Message Syntax and Routing
- **RFC 7231**: HTTP/1.1 Semantics and Content
- **RFC 7232**: HTTP/1.1 Conditional Requests
- **RFC 7233**: HTTP/1.1 Range Requests
- **RFC 7234**: HTTP/1.1 Caching
- **RFC 7235**: HTTP/1.1 Authentication
- **RFC 2616**: HTTP/1.1 (obsolete, superseded by 7230-7235)
- **RFC 1945**: HTTP/1.0 (informational)
- **Python http.server**: https://docs.python.org/3/library/http.server.html
- **Python urllib.request**: https://docs.python.org/3/library/urllib.request.html

---

## Lab Progression

```
LAB-001: Know Your Host               (Network layer — IP addressing)
LAB-002: TCP, UDP, Ports and Sockets  (Transport layer — sockets, SYN/ACK)
LAB-003: DNS Name Resolution          (Application layer — hostname → IP)
LAB-004: ARP & Local Network Resolution (Link layer — IP → MAC)
LAB-005: HTTP Client/Server & Local Services (Application layer — request/response)
                                ↑
                         THIS LAB
```

LAB-005 completes the layers from L2 (ARP) through L7 (HTTP), demonstrating
how each layer builds on the one below it.

---

*This is an educational HTTP/1.x implementation. It is NOT production-grade.
Do not expose our server to a network — it binds localhost only. Do NOT
commit or push without review.*
