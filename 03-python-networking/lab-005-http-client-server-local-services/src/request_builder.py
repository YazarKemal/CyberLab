#!/usr/bin/env python3
"""
LAB-005: HTTP Request Builder (Offline)
========================================

Builds HTTP requests offline — no socket connection.

Demonstrates:
  - GET, HEAD, POST request structure
  - CRLF line endings
  - Content-Length calculation
  - Blank line separator

Usage:
  python src/request_builder.py
"""

import sys
import os

sys.path.insert(0, os.path.dirname(__file__))
import http_message as http


def show_request(name: str, method: str, path: str,
                 headers: dict[str, str] | None = None,
                 body: str | None = None) -> None:
    """Build and display a request."""
    print("─" * 64)
    print(f"  {name}: {method} {path}")
    print("─" * 64)
    print()

    hdrs = headers.copy() if headers else {}
    hdrs.setdefault("Host", "localhost:8000")
    hdrs.setdefault("User-Agent", "CyberLab-LAB005")
    hdrs.setdefault("Connection", "close")

    if body is not None:
        body_bytes = body.encode("utf-8")
        hdrs["Content-Length"] = str(len(body_bytes))
        hdrs.setdefault("Content-Type", "text/plain")

    req = http.build_request(method, path, hdrs, body)
    text = req.decode("utf-8")

    print(f"  Raw request ({len(req)} bytes):")
    print(f"  {'─' * 56}")
    for line in text.split(http.CRLF):
        if line:
            print(f"  │ {line}")
        else:
            print(f"  │ (blank line)")
    print(f"  {'─' * 56}")
    print()

    # Verify CRLF
    crlf_count = text.count(http.CRLF)
    print(f"  CRLF count:         {crlf_count}")
    print(f"  Ends with CRLF CRLF: {'✓' if text.endswith(http.DOUBLE_CRLF) or text[-4:] == http.DOUBLE_CRLF else '✗'}")
    print(f"  Content-Length:     {hdrs.get('Content-Length', 'N/A')}")
    print(f"  Total bytes:        {len(req)}")
    print()


def main() -> None:
    print("=" * 64)
    print("  LAB-005: HTTP Request Builder (Offline)")
    print("  No sockets — message construction only")
    print("=" * 64)
    print()

    # GET /
    show_request("GET root", "GET", "/")

    # HEAD /
    show_request("HEAD root", "HEAD", "/")

    # GET /health
    show_request("GET health", "GET", "/health")

    # POST /echo
    show_request("POST echo", "POST", "/echo", body="hello from CyberLab")

    print("=" * 64)
    print("  Request builder complete.")
    print("=" * 64)


if __name__ == "__main__":
    main()
