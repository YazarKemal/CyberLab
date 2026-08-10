#!/usr/bin/env python3
"""
LAB-005: Educational HTTP/1.x Message Helpers
==============================================

Implements simple educational helpers for constructing and parsing
HTTP/1.x messages. NOT a production-grade HTTP parser.

Teaches:
  - CRLF line endings (\\r\\n)
  - Request line / status line structure
  - Header formatting
  - Body separation (blank line = \\r\\n\\r\\n)

Usage:
  python src/http_message.py
"""

CRLF = "\r\n"
CRLF_BYTES = b"\r\n"
DOUBLE_CRLF = "\r\n\r\n"
DOUBLE_CRLF_BYTES = b"\r\n\r\n"


def build_request_line(method: str, path: str, version: str = "HTTP/1.1") -> str:
    """Build a request line: 'GET / HTTP/1.1'."""
    return f"{method} {path} {version}"


def build_status_line(version: str, status_code: int, reason: str) -> str:
    """Build a status line: 'HTTP/1.1 200 OK'."""
    return f"{version} {status_code} {reason}"


def build_headers(headers: dict[str, str]) -> str:
    """Build header lines: 'Host: localhost\\r\\nContent-Type: text/plain\\r\\n'."""
    lines = [f"{k}: {v}" for k, v in headers.items()]
    return CRLF.join(lines)


def build_request(method: str, path: str, headers: dict[str, str],
                  body: str | bytes | None = None, version: str = "HTTP/1.1") -> bytes:
    """
    Build a complete HTTP request.

    Returns bytes ready for socket.sendall().
    """
    req_line = build_request_line(method, path, version)
    header_block = build_headers(headers)

    if body is not None:
        if isinstance(body, str):
            body_bytes = body.encode("utf-8")
        else:
            body_bytes = body
    else:
        body_bytes = None

    message = CRLF.join([req_line, header_block])

    if body_bytes is not None:
        message += DOUBLE_CRLF
        message_bytes = message.encode("utf-8") + body_bytes
    else:
        message += DOUBLE_CRLF
        message_bytes = message.encode("utf-8")

    return message_bytes


def build_response(status_code: int, reason: str, headers: dict[str, str],
                   body: str | bytes | None = None, version: str = "HTTP/1.1") -> bytes:
    """
    Build a complete HTTP response.

    Returns bytes ready for socket.sendall().
    """
    status = build_status_line(version, status_code, reason)
    header_block = build_headers(headers)

    message = CRLF.join([status, header_block])

    if body is not None:
        if isinstance(body, str):
            body_bytes = body.encode("utf-8")
        else:
            body_bytes = body
        message += DOUBLE_CRLF
        message_bytes = message.encode("utf-8") + body_bytes
    else:
        message += DOUBLE_CRLF
        message_bytes = message.encode("utf-8")

    return message_bytes


def parse_start_line(data: bytes) -> dict:
    """
    Parse the first line (request or status) from raw HTTP bytes.

    Returns dict with start_line, method/path/version (request)
    or version/status_code/reason (response).
    """
    text = data.decode("utf-8", errors="replace")
    first_crlf = text.find(CRLF)
    if first_crlf == -1:
        raise ValueError("No CRLF found — not a valid HTTP/1.x start line")

    start_line = text[:first_crlf]
    parts = start_line.split(" ", 2)

    result = {"start_line": start_line, "_next_offset": first_crlf + 2}

    if len(parts) == 3:
        if parts[0].startswith("HTTP/"):
            # Response: "HTTP/1.1 200 OK"
            result["version"] = parts[0]
            result["status_code"] = int(parts[1])
            result["reason"] = parts[2]
            result["type"] = "response"
        else:
            # Request: "GET / HTTP/1.1"
            result["method"] = parts[0]
            result["path"] = parts[1]
            result["version"] = parts[2]
            result["type"] = "request"
    else:
        result["type"] = "unknown"
        result["parts"] = parts

    return result


def parse_headers(data: bytes, offset: int) -> dict:
    """
    Parse headers from raw HTTP bytes starting at offset.

    Returns dict mapping header names to values, plus _next_offset
    pointing to the byte after the blank line.
    """
    text = data[offset:].decode("utf-8", errors="replace")
    blank_pos = text.find(DOUBLE_CRLF)
    if blank_pos == -1:
        raise ValueError("No header/body separator (blank line) found")

    header_section = text[:blank_pos]
    raw_headers = {}

    for line in header_section.split(CRLF):
        if ":" in line:
            key, _, value = line.partition(":")
            raw_headers[key.strip()] = value.strip()

    body_offset = offset + blank_pos + len(DOUBLE_CRLF)
    return {
        "headers": raw_headers,
        "_next_offset": body_offset,
    }


def parse_response(data: bytes) -> dict:
    """
    Parse a complete HTTP response into structured fields.

    EDUCATIONAL PARSER — not RFC-complete.
    """
    start = parse_start_line(data)
    if start.get("type") != "response":
        raise ValueError(f"Expected HTTP response, got {start.get('type', 'unknown')}")

    headers_result = parse_headers(data, start["_next_offset"])
    body_offset = headers_result["_next_offset"]

    body = data[body_offset:] if body_offset < len(data) else b""

    return {
        "version": start.get("version", ""),
        "status_code": start.get("status_code", 0),
        "reason": start.get("reason", ""),
        "headers": headers_result["headers"],
        "body": body,
        "body_length": len(body),
    }


def hexdump(data: bytes, title: str = "") -> str:
    """Format bytes as hex + ASCII dump."""
    lines = []
    if title:
        lines.append(f"  {title} ({len(data)} bytes)")
    lines.append(f"  {'Offset':<8} {'Hex':<49} {'ASCII'}")
    lines.append(f"  {'-'*8} {'-'*49} {'-'*16}")

    for i in range(0, len(data), 16):
        chunk = data[i:i + 16]
        hex_part = " ".join(f"{b:02x}" for b in chunk)
        ascii_part = "".join(chr(b) if 32 <= b < 127 else "." for b in chunk)
        lines.append(f"  {i:08x}  {hex_part:<49s} {ascii_part}")

    return "\n".join(lines)


def main() -> None:
    print("=" * 64)
    print("  LAB-005: HTTP/1.x Message Helpers")
    print("=" * 64)
    print()

    # 1. Basic constants
    print("─" * 64)
    print("  1. HTTP/1.x Line Endings")
    print("─" * 64)
    print()
    crlf_hex = CRLF_BYTES.hex()
    print(f"  CRLF:       \\r\\n  →  bytes 0x{crlf_hex} ({CRLF_BYTES.hex(' ')} )")
    print(f"  Blank line: \\r\\n\\r\\n → separates headers from body")
    print()

    # 2. Build a request
    print("─" * 64)
    print("  2. Build GET Request")
    print("─" * 64)
    print()

    req = build_request(
        "GET", "/health",
        {"Host": "localhost", "User-Agent": "CyberLab-LAB005", "Connection": "close"}
    )
    print(f"  Request text:")
    for line in req.decode("utf-8").split("\r\n"):
        if line:
            print(f"    {line}")
        else:
            print(f"    (blank — header/body separator)")
    print(f"  Request bytes: {len(req)}")
    assert req.endswith(DOUBLE_CRLF_BYTES) or req[-4:] == DOUBLE_CRLF_BYTES
    print(f"  Ends with CRLF CRLF: ✓")
    print()

    # 3. Build a response
    print("─" * 64)
    print("  3. Build 200 Response")
    print("─" * 64)
    print()

    resp = build_response(
        200, "OK",
        {"Content-Type": "text/plain", "Content-Length": "7"},
        "healthy"
    )
    print(f"  Response text:")
    for line in resp.decode("utf-8").split("\r\n"):
        print(f"    {line}")
    print(f"  Response bytes: {len(resp)}")
    print()

    # 4. Parse the response we just built
    print("─" * 64)
    print("  4. Parse Verification (Round-Trip)")
    print("─" * 64)
    print()

    parsed = parse_response(resp)
    print(f"  Version:      {parsed['version']}  ✓" if parsed['version'] == "HTTP/1.1" else f"  Version: {parsed['version']} ✗")
    print(f"  Status:       {parsed['status_code']}  ✓" if parsed['status_code'] == 200 else f"  Status: {parsed['status_code']} ✗")
    print(f"  Reason:       {parsed['reason']}  ✓" if parsed['reason'] == "OK" else f"  Reason: {parsed['reason']} ✗")
    print(f"  Content-Type: {parsed['headers'].get('Content-Type', 'N/A')}  ✓")
    print(f"  Content-Len:  {parsed['headers'].get('Content-Length', 'N/A')}  ✓")
    body_str = parsed['body'].decode("utf-8")
    print(f"  Body:         '{body_str}'  ✓" if body_str == "healthy" else f"  Body: '{body_str}' ✗")
    print()

    # 5. Request parsing
    print("─" * 64)
    print("  5. Request Line Parsing")
    print("─" * 64)
    print()

    req_parsed = parse_start_line(req)
    print(f"  Method:   {req_parsed.get('method', 'N/A')}")
    print(f"  Path:     {req_parsed.get('path', 'N/A')}")
    print(f"  Version:  {req_parsed.get('version', 'N/A')}")
    print(f"  Type:     {req_parsed.get('type', 'N/A')}")
    print()

    print("=" * 64)
    print("  HTTP message helpers ready.")
    print("=" * 64)


if __name__ == "__main__":
    main()
