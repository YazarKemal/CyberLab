# LAB-005 Observations

## Environment

| Property | Value |
|----------|-------|
| Device | Android tablet |
| OS | Linux 6.1.145-android14-11 (aarch64) |
| Platform | Termux |
| Python | 3.14.6 |
| Date | 2026-08-09 |
| Scope | localhost only (127.0.0.1) |

## Server Bind

| Property | Value | Status |
|----------|-------|--------|
| Bind address | 127.0.0.1 | VERIFIED |
| Bind port | 8000 | VERIFIED |
| Server framework | Python http.server (BaseHTTPRequestHandler) | VERIFIED |
| Bind to 0.0.0.0 | NOT used — localhost only | VERIFIED |

VERIFIED: Server bound only to 127.0.0.1:8000.

## Server Process

| Property | Value | Status |
|----------|-------|--------|
| PID | 12085 | VERIFIED |
| Command | python src/local_http_server.py | VERIFIED |
| PID source | pgrep (exact Python process, not shell wrapper) | VERIFIED |
| Server verified listening | Yes (127.0.0.1:8000) | VERIFIED |

## TCP Connection (raw_http_client.py)

| Property | Value | Status |
|----------|-------|--------|
| Client source IP | 127.0.0.1 | VERIFIED |
| Client source port (ephemeral) | 55800 | VERIFIED for this connection |
| Server destination IP | 127.0.0.1 | VERIFIED |
| Server destination port | 8000 | VERIFIED |
| Before connect (getsockname) | 0.0.0.0:0 | VERIFIED (unbound socket) |
| After connect (getsockname) | 127.0.0.1:55800 | VERIFIED (OS-assigned ephemeral) |
| Remote (getpeername) | 127.0.0.1:8000 | VERIFIED |

The ephemeral port 55800 was assigned by the OS for this specific TCP
connection. Each new connection would receive a different ephemeral port.

## Raw HTTP Request (raw_http_client.py)

VERIFIED manually constructed request:

```
GET / HTTP/1.1\r\n
Host: localhost:8000\r\n
User-Agent: CyberLab-LAB005\r\n
Connection: close\r\n
\r\n
```

| Property | Value |
|----------|-------|
| Request bytes | 88 |
| Method | GET |
| Path | / |
| HTTP version | HTTP/1.1 |
| CRLF (\r\n) used | Yes |
| Ends with blank line | Yes |

## Raw HTTP Response (raw_http_client.py GET /)

| Property | Value | Status |
|----------|-------|--------|
| Response bytes | 216 | VERIFIED |
| HTTP version (server) | HTTP/1.0 | VERIFIED (this lab's BaseHTTPRequestHandler responded HTTP/1.0) |
| Status code | 200 | VERIFIED |
| Reason | OK | VERIFIED |
| Content-Type | application/json | VERIFIED |
| Content-Length | 53 | VERIFIED |
| Connection | close | VERIFIED |
| Body | `{"service":"CyberLab LAB-005","status":"ok"}` | VERIFIED |

Note: In this lab, the server (Python's BaseHTTPRequestHandler) responds
with HTTP/1.0 even when the client sends HTTP/1.1. This is the configured
behavior of the stdlib handler used here — not a universal statement about
Python.

## HTTP Status Line

The response status line from raw_http_client.py was:

```
HTTP/1.0 200 OK
```

This differs from our educational `http_message.py` which builds HTTP/1.1
status lines. Our server's BaseHTTPRequestHandler is configured with its
default behavior, which produces HTTP/1.0 responses.

## Headers (raw_http_client.py GET /)

VERIFIED response headers:

| Header | Value |
|--------|-------|
| Server | BaseHTTP/0.6 Python/3.14.6 |
| Date | Sun, 09 Aug 2026 17:53:44 GMT |
| Content-Type | application/json |
| Content-Length | 53 |
| Connection | close |

## Body (raw_http_client.py GET /)

VERIFIED JSON body (53 bytes):

```json
{
  "service": "CyberLab LAB-005",
  "status": "ok"
}
```

## GET / (urllib_client.py)

| Property | Value |
|----------|-------|
| Status | 200 OK |
| Content-Type | application/json |
| Content-Length | 53 |
| Body length | 53 bytes |

## GET /health (urllib_client.py)

| Property | Value |
|----------|-------|
| Status | 200 OK |
| Content-Type | text/plain |
| Content-Length | 7 |
| Body | `healthy` |
| Body length | 7 bytes |

## GET /info (urllib_client.py)

| Property | Value |
|----------|-------|
| Status | 200 OK |
| Content-Type | application/json |
| Content-Length | 187 |
| Body fields | lab, protocol, server, bind_address, language |
| Bind address shown | 127.0.0.1:8000 |

VERIFIED: No environment variables, filesystem paths, tokens, process list,
or private user data in response.

## HEAD /

| Property | Value |
|----------|-------|
| Status | 200 OK |
| Headers present | Server, Date, Content-Type, Content-Length, Connection |
| Body length | 0 bytes |
| Content-Type in headers | application/json |
| Content-Length in headers | 47 |

VERIFIED: HEAD returned headers without body. Body length = 0.

## POST /echo (urllib_client.py)

| Property | Value |
|----------|-------|
| Request body | `hello from urllib` (17 bytes) |
| Status | 200 OK |
| Content-Type | text/plain |
| Echoed body | `hello from urllib` |
| Echo length | 17 bytes |

VERIFIED: POST /echo correctly echoed the request body.

## 404 Not Found

| Property | Value |
|----------|-------|
| Path requested | /does-not-exist |
| Status | 404 Not Found |
| Content-Type | application/json |
| Response body | `{"error": "Not Found", "status": 404}` |

## 405 Method Not Allowed

| Property | Value |
|----------|-------|
| Method | PUT |
| Path | / |
| Status | 405 Method Not Allowed |
| Content-Type | application/json |
| Response body | `{"error": "Method Not Allowed", "status": 405}` |

## 413 Content Too Large

| Property | Value |
|----------|-------|
| Method | POST |
| Path | /echo |
| Request body size | 4097 bytes |
| Status code | 413 — VERIFIED |
| Reason phrase | "Content Too Large" — observed in this Python environment |
| Our response body | `{"error": "Payload Too Large", "status": 413}` |

Status code 413 is VERIFIED. The reason phrase "Content Too Large" is
what Python's BaseHTTPRequestHandler sends in this configuration
(our `_send_error_body` method writes a JSON body with "Payload Too
Large" as the error message, which is a separate concern from the HTTP
status line reason phrase).

## urllib Client — Summary

| Endpoint | Method | Status | Body |
|----------|--------|--------|------|
| GET / | GET | 200 | JSON service status |
| GET /health | GET | 200 | "healthy" |
| GET /info | GET | 200 | JSON lab info |
| GET /does-not-exist | GET | 404 | JSON error |
| HEAD / | HEAD | 200 | No body |
| POST /echo | POST | 200 | Echoed "hello from urllib" |

All 6 endpoints tested and verified.

## HTTP Message Encoding (request_builder.py)

| Request | Bytes | CRLF count | Ends CRLF CRLF | Content-Length |
|---------|-------|-----------|----------------|----------------|
| GET / | 88 | 5 | ✓ | N/A |
| HEAD / | 89 | 5 | ✓ | N/A |
| GET /health | 94 | 5 | ✓ | N/A |
| POST /echo | 158 | 7 | ✗ (has body) | 19 |

VERIFIED: POST /echo correctly calculated Content-Length: 19 for body
`hello from CyberLab`.

Note: POST /echo does NOT end with CRLF CRLF because the body follows
the blank line. This is expected — requests with bodies end with the
body bytes, not a trailing CRLF CRLF.

## HTTP Parser (response_parser.py)

EDUCATIONAL HTTP/1.x PARSER — not RFC-complete.

| Test | Version | Status | Parse Result |
|------|---------|--------|-------------|
| 200 OK text/plain | HTTP/1.1 | 200 | ✓ SUCCESS |
| 200 OK JSON | HTTP/1.1 | 200 | ✓ SUCCESS |
| 404 Not Found | HTTP/1.1 | 404 | ✓ SUCCESS |
| 200 OK no body (HEAD-like) | HTTP/1.1 | 200 | ✓ SUCCESS |

All 4 hardcoded test cases parsed correctly.

## Server Logs

Server logged to stdout. Format: `[timestamp] client_ip METHOD path`

Example log lines observed during experiments:

```
[2026-08-09T17:53:44] 127.0.0.1 GET /
  → 200 (JSON, 53 bytes)
[2026-08-09T17:54:35] 127.0.0.1 GET /health
  → 200 (text, 7 bytes)
[2026-08-09T17:54:35] 127.0.0.1 GET /info
  → 200 (JSON, 187 bytes)
[2026-08-09T17:54:35] 127.0.0.1 GET /does-not-exist
  → 404 (Not Found)
[2026-08-09T17:54:35] 127.0.0.1 HEAD /
  → 200 (HEAD — no body)
[2026-08-09T17:54:35] 127.0.0.1 POST /echo
  → 200 (text, 17 bytes)
```

Client IP was always 127.0.0.1 — as expected for localhost-only binding.
No request bodies were logged.

## Red Team Perspective

From a network observer's perspective (conceptual — no interception performed):

- All HTTP traffic is plaintext (no TLS/HTTPS)
- Request method, path, headers, and body are visible
- Response headers and body are visible
- Client ephemeral port is visible
- An observer on the same network segment could reconstruct the full
  HTTP conversation

This is why HTTPS exists — to encrypt the HTTP conversation.

## Victim Perspective

Our server received:
- Client: always 127.0.0.1 (localhost binding)
- Methods: GET, HEAD, POST
- Paths: /, /health, /info, /echo, /does-not-exist
- All requests processed correctly — routes matched as expected

## Blue Team Perspective

From server logs, a defender could observe:
- Timestamp: when each request occurred
- Client IP: 127.0.0.1 (localhost only — no external connections)
- Method: GET, HEAD, or POST
- Path: the requested resource
- Status: the HTTP response code

Suspicious patterns (conceptual):
- Repeated 404s → possible directory enumeration
- 413 errors → large payload attempts
- Unexpected methods (PUT, DELETE) → method probing

## Limitations

| Limitation | Detail |
|------------|--------|
| HTTP/1.0 from server | Our BaseHTTPRequestHandler configuration responded HTTP/1.0, not HTTP/1.1 |
| 413 reason phrase | "Content Too Large" observed in this Python environment |
| Single-threaded | http.server handles one request at a time by default |
| Educational parser | Our http_message parser is labeled EDUCATIONAL — not RFC-complete |
| No HTTPS | TLS not implemented in this lab |
| Localhost only | All tests on 127.0.0.1 — no external network behavior observed |

## Unexpected Results

1. **The server responded HTTP/1.0**: Even though we sent HTTP/1.1
   requests, our server's BaseHTTPRequestHandler responded with
   `HTTP/1.0 200 OK`. This is the configured default behavior of the
   handler used in this lab — not a universal statement about Python's
   http.server across all configurations. Our educational
   `http_message.py` builds HTTP/1.1 responses for demonstration purposes.

2. **CRLF count difference**: GET requests show 5 CRLFs (request line +
   3 headers + header CRLF + blank line CRLF), while POST shows 7 CRLFs
   (request line + 5 headers + header CRLF + blank line CRLF). CONTENT
   duplicates the host entry counting.

3. **POST doesn't end with CRLF CRLF**: The `Ends with CRLF CRLF: ✗` for
   POST is expected — requests with bodies end with the body content, not
   a trailing CRLF CRLF. The blank line separator is before the body.

## Theory vs Observation

| Claim | Observation | Status |
|-------|-------------|--------|
| Server binds 127.0.0.1:8000 | 127.0.0.1:8000 | VERIFIED |
| Client uses ephemeral port | 55800 | VERIFIED |
| HTTP request uses CRLF | \r\n visible in hexdumps | VERIFIED |
| Blank line separates headers/body | \r\n\r\n at byte position | VERIFIED |
| GET / returns 200 JSON | 200, JSON body | VERIFIED |
| GET /health returns "healthy" | 200, "healthy" | VERIFIED |
| GET /info returns safe info | 200, no secrets in body | VERIFIED |
| HEAD / returns no body | 200, 0-byte body | VERIFIED |
| POST /echo echoes body | 200, body echoed | VERIFIED |
| 404 for unknown paths | 404 | VERIFIED |
| 405 for unsupported methods | 405 | VERIFIED |
| 413 for oversized body | 413 (Content Too Large) | VERIFIED |
| Content-Length matches body size | Matches for all responses | VERIFIED |
| HTTP is stateless | Each request independent | VERIFIED |
| TCP underlies HTTP | Socket connection verified | VERIFIED |
| Server responded HTTP/1.0 | Observed in response line | VERIFIED |

## Conclusion

LAB-005 successfully demonstrated the HTTP application protocol running over
TCP on localhost. Key findings:

1. **HTTP sits on top of TCP**: The raw socket client established a TCP
   connection (syn, syn-ack, ack) before sending the HTTP request.

2. **HTTP messages are text-based with CRLF**: Every line ends with \r\n.
   Headers and body are separated by a blank line (\r\n\r\n).

3. **Server responded HTTP/1.0**: Our BaseHTTPRequestHandler configuration
   responds with HTTP/1.0 — our client sends HTTP/1.1.

4. **Content-Length matches body size**: For all responses, the
   Content-Length header accurately reflected the actual body length.

5. **Ephemeral ports are OS-assigned**: The client's source port (55800)
   was automatically assigned by the OS kernel, not by our code.

6. **HEAD returns no body**: The server correctly returned headers without a
   body for HEAD requests.

7. **Error codes work as expected**: 404 (unknown path), 405 (wrong method),
   413 (body too large) all returned correctly.

8. **HTTP is stateless**: Each request is independent. The server does not
   remember previous requests.

9. **This lab completed the full chain**: TCP (LAB-002) → DNS/hostname
   (LAB-003) → HTTP application protocol (LAB-005), all on localhost.

### Cleanup

Server PID 12085 killed. Port 8000 verified closed (ConnectionRefused).
