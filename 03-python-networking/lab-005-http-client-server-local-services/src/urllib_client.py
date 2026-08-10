#!/usr/bin/env python3
"""
LAB-005: High-Level HTTP Client (urllib)
=========================================

Uses Python's urllib.request to interact with our local server.

Connects ONLY to http://127.0.0.1:8000/

Tests: GET /, /health, /info | POST /echo

This demonstrates the difference between a high-level client (urllib)
and a low-level client (raw sockets).

Usage:
  python src/urllib_client.py
"""

import urllib.request
import urllib.error
import json

BASE = "http://127.0.0.1:8000"


def test_get(path: str, label: str) -> None:
    """Perform a GET request and display results."""
    url = f"{BASE}{path}"
    print("─" * 64)
    print(f"  GET {path}  —  {label}")
    print("─" * 64)
    print(f"  URL: {url}")
    print()

    try:
        with urllib.request.urlopen(url, timeout=5) as resp:
            print(f"  Status:        {resp.status} {resp.reason}")
            print(f"  Version:       HTTP/1.1")  # urllib uses HTTP/1.1
            print(f"  Content-Type:  {resp.headers.get('Content-Type', 'N/A')}")
            print(f"  Content-Length: {resp.headers.get('Content-Length', 'N/A')}")
            body = resp.read()
            text = body.decode("utf-8", errors="replace")
            print(f"  Body ({len(body)} bytes):")
            for line in text.splitlines():
                print(f"    {line}")
    except urllib.error.HTTPError as e:
        print(f"  Status: {e.code} {e.reason}")
        body = e.read()
        print(f"  Body ({len(body)} bytes):")
        for line in body.decode("utf-8", errors="replace").splitlines():
            print(f"    {line}")
    except Exception as e:
        print(f"  ERROR: {e}")
    print()


def test_post(path: str, body_text: str) -> None:
    """Perform a POST request and display results."""
    url = f"{BASE}{path}"
    body_bytes = body_text.encode("utf-8")
    print("─" * 64)
    print(f"  POST {path}  —  echo body")
    print("─" * 64)
    print(f"  URL: {url}")
    print(f"  Request body: '{body_text}' ({len(body_bytes)} bytes)")
    print()

    try:
        req = urllib.request.Request(url, data=body_bytes, method="POST")
        req.add_header("Content-Type", "text/plain")
        with urllib.request.urlopen(req, timeout=5) as resp:
            print(f"  Status:        {resp.status} {resp.reason}")
            print(f"  Content-Type:  {resp.headers.get('Content-Type', 'N/A')}")
            body = resp.read()
            text = body.decode("utf-8", errors="replace")
            print(f"  Echoed body ({len(body)} bytes):")
            for line in text.splitlines():
                print(f"    {line}")
    except urllib.error.HTTPError as e:
        print(f"  Status: {e.code} {e.reason}")
        body = e.read()
        print(f"  Body ({len(body)} bytes):")
        for line in body.decode("utf-8", errors="replace").splitlines():
            print(f"    {line}")
    except Exception as e:
        print(f"  ERROR: {e}")
    print()


def test_head(path: str) -> None:
    """Perform a HEAD request and display headers only."""
    url = f"{BASE}{path}"
    print("─" * 64)
    print(f"  HEAD {path}")
    print("─" * 64)
    print(f"  URL: {url}")
    print()

    try:
        req = urllib.request.Request(url, method="HEAD")
        with urllib.request.urlopen(req, timeout=5) as resp:
            print(f"  Status:        {resp.status} {resp.reason}")
            print(f"  Headers:")
            for k, v in resp.headers.items():
                print(f"    {k}: {v}")
            body = resp.read()
            print(f"  Body length:   {len(body)} bytes (should be 0)")
    except Exception as e:
        print(f"  ERROR: {e}")
    print()


def main() -> None:
    print("=" * 64)
    print("  LAB-005: High-Level HTTP Client (urllib)")
    print(f"  Target: {BASE}/")
    print("=" * 64)
    print()

    test_get("/", "JSON status")
    test_get("/health", "plain text health check")
    test_get("/info", "lab information")
    test_get("/does-not-exist", "404 test")
    test_head("/")
    test_post("/echo", "hello from urllib")

    print("=" * 64)
    print("  urllib client complete.")
    print("=" * 64)


if __name__ == "__main__":
    main()
