#!/usr/bin/env python3
"""
LAB-005: HTTP Response Parser (Educational)
============================================

EDUCATIONAL HTTP/1.x PARSER — not RFC-complete.

Parses HTTP responses into:
  - version
  - status code
  - reason phrase
  - headers
  - body

Demonstrates with hardcoded responses first, then can be used
to parse responses captured by raw_http_client.py.

Usage:
  python src/response_parser.py
"""

import sys
import os

sys.path.insert(0, os.path.dirname(__file__))
import http_message as http


def show_parsed(data: bytes, label: str) -> None:
    """Parse and display an HTTP response."""
    print("─" * 64)
    print(f"  {label}")
    print("─" * 64)
    print()

    print(http.hexdump(data, "Raw response bytes:"))
    print()

    try:
        parsed = http.parse_response(data)
        print(f"  Version:      {parsed['version']}")
        print(f"  Status code:  {parsed['status_code']}")
        print(f"  Reason:       {parsed['reason']}")
        print(f"  Headers:")
        for k, v in parsed["headers"].items():
            print(f"    {k}: {v}")
        body_preview = parsed["body"][:200].decode("utf-8", errors="replace")
        print(f"  Body ({parsed['body_length']} bytes):")
        for line in body_preview.splitlines():
            print(f"    {line}")
        if parsed["body_length"] > 200:
            print(f"    ... ({parsed['body_length'] - 200} more bytes)")
        print()
        print(f"  Parse: ✓ SUCCESS")
    except Exception as e:
        print(f"  Parse: ✗ FAILED — {e}")
    print()


def main() -> None:
    print("=" * 64)
    print("  LAB-005: HTTP Response Parser (Educational)")
    print("=" * 64)
    print()

    # ── Hardcoded test responses ─────────────────────────────────────

    # Test 1: Simple 200
    resp1 = http.build_response(
        200, "OK",
        {"Content-Type": "text/plain", "Content-Length": "7",
         "Connection": "close"},
        "healthy"
    )
    show_parsed(resp1, "Test 1: 200 OK (text/plain)")

    # Test 2: JSON response
    resp2 = http.build_response(
        200, "OK",
        {"Content-Type": "application/json", "Content-Length": "41",
         "Connection": "close"},
        '{"service":"CyberLab LAB-005","status":"ok"}'
    )
    show_parsed(resp2, "Test 2: 200 OK (application/json)")

    # Test 3: 404
    resp3 = http.build_response(
        404, "Not Found",
        {"Content-Type": "application/json", "Content-Length": "0",
         "Connection": "close"},
        ""
    )
    show_parsed(resp3, "Test 3: 404 Not Found")

    # Test 4: No body (like HEAD response)
    resp4 = http.build_response(
        200, "OK",
        {"Content-Type": "text/plain", "Content-Length": "7",
         "Connection": "close"},
        None
    )
    data4 = resp4.rsplit(http.DOUBLE_CRLF_BYTES, 1)[0] + http.DOUBLE_CRLF_BYTES
    show_parsed(data4, "Test 4: 200 OK (no body — like HEAD)")

    print("=" * 64)
    print("  Response parser complete.")
    print("  Label: EDUCATIONAL HTTP/1.x PARSER — not RFC-complete.")
    print("=" * 64)


if __name__ == "__main__":
    main()
