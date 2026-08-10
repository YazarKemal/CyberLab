#!/usr/bin/env python3
"""
LAB-005: Local HTTP Server (Educational)
=========================================

Binds ONLY to 127.0.0.1:8000. Never 0.0.0.0.

Routes:
  GET  /           → 200 JSON {"service":"CyberLab LAB-005","status":"ok"}
  GET  /health     → 200 plain text "healthy"
  GET  /info       → 200 JSON (safe static lab info only)
  HEAD /           → 200 (headers only, no body)
  POST /echo       → 200 (echoes small text body, max 4096 bytes)

Error responses:
  404  Not Found       — unknown path
  405  Method Not Allowed — unsupported method on known path
  413  Payload Too Large  — POST /echo body > 4096 bytes

Logs: timestamp, client IP, method, path, status
Since only localhost is allowed, expected client IP = 127.0.0.1.

Usage:
  python src/local_http_server.py
  python src/local_http_server.py --once   (handle one request and exit)
"""

import json
import sys
import time
from http.server import HTTPServer, BaseHTTPRequestHandler

HOST = "127.0.0.1"
PORT = 8000
MAX_BODY = 4096


class LabHandler(BaseHTTPRequestHandler):
    """Educational HTTP request handler for LAB-005."""

    # Silence default logging; we log our own format.
    def log_message(self, fmt: str, *args) -> None:
        timestamp = time.strftime("%Y-%m-%dT%H:%M:%S")
        client = self.client_address[0]
        method = self.command
        path = self.path
        # Determine status from the response we'll send
        print(f"[{timestamp}] {client} {method} {path}", flush=True)

    def _send_json(self, status: int, data: dict) -> None:
        body = json.dumps(data, indent=2).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Connection", "close")
        self.end_headers()
        self.wfile.write(body)
        # Log status after sending
        print(f"  → {status} (JSON, {len(body)} bytes)", flush=True)

    def _send_text(self, status: int, text: str) -> None:
        body = text.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "text/plain")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Connection", "close")
        self.end_headers()
        self.wfile.write(body)
        print(f"  → {status} (text, {len(body)} bytes)", flush=True)

    def _send_error_body(self, status: int, message: str) -> None:
        data = {"error": message, "status": status}
        body = json.dumps(data, indent=2).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Connection", "close")
        self.end_headers()
        self.wfile.write(body)
        print(f"  → {status} ({message})", flush=True)

    def _read_body(self) -> bytes:
        content_length = int(self.headers.get("Content-Length", 0))
        if content_length > MAX_BODY:
            return b""  # caller will check and send 413
        return self.rfile.read(content_length)

    # ── GET ────────────────────────────────────────────────────────────

    def do_GET(self) -> None:
        if self.path == "/":
            self._send_json(200, {
                "service": "CyberLab LAB-005",
                "status": "ok",
            })
        elif self.path == "/health":
            self._send_text(200, "healthy")
        elif self.path == "/info":
            self._send_json(200, {
                "lab": "LAB-005",
                "protocol": "HTTP/1.1",
                "server": "CyberLab Educational HTTP Server",
                "bind_address": f"{HOST}:{PORT}",
                "language": "Python standard library (http.server)",
            })
        else:
            self._send_error_body(404, "Not Found")

    # ── HEAD ───────────────────────────────────────────────────────────

    def do_HEAD(self) -> None:
        if self.path == "/":
            body = json.dumps({
                "service": "CyberLab LAB-005",
                "status": "ok",
            }).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Connection", "close")
            self.end_headers()
            # No body written for HEAD
            print(f"  → 200 (HEAD — no body)", flush=True)
        else:
            self.send_response(404)
            self.send_header("Content-Length", "0")
            self.send_header("Connection", "close")
            self.end_headers()
            print(f"  → 404 (HEAD — not found)", flush=True)

    # ── POST ───────────────────────────────────────────────────────────

    def do_POST(self) -> None:
        if self.path == "/echo":
            content_length = int(self.headers.get("Content-Length", 0))
            if content_length > MAX_BODY:
                self._send_error_body(413, "Payload Too Large")
                return
            body = self.rfile.read(content_length)
            self._send_text(200, body.decode("utf-8", errors="replace"))
        else:
            self._send_error_body(404, "Not Found")

    # ── Catch unsupported methods on known paths ────────────────────────

    def do_PUT(self) -> None:
        self._send_error_body(405, "Method Not Allowed")

    def do_DELETE(self) -> None:
        self._send_error_body(405, "Method Not Allowed")

    def do_PATCH(self) -> None:
        self._send_error_body(405, "Method Not Allowed")

    def do_OPTIONS(self) -> None:
        self._send_error_body(405, "Method Not Allowed")


def main() -> None:
    import argparse
    parser = argparse.ArgumentParser(description="LAB-005 Educational HTTP Server")
    parser.add_argument("--once", action="store_true",
                        help="Handle one request and exit")
    args = parser.parse_args()

    server = HTTPServer((HOST, PORT), LabHandler)
    print(f"CyberLab LAB-005 HTTP Server")
    print(f"Bind: {HOST}:{PORT}")
    print(f"PID:  {__import__('os').getpid()}")
    print(f"Routes: GET /, /health, /info | HEAD / | POST /echo")
    print(f"Ctrl+C to stop")
    print()

    if args.once:
        server.handle_request()
        print("(single request handled — exiting)")
    else:
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            print("\nServer stopped.")
        finally:
            server.server_close()


if __name__ == "__main__":
    main()
