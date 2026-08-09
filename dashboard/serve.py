#!/usr/bin/env python3
"""Read-only localhost dashboard for CyberLab.

The dashboard discovers completed/active labs from the repository and exposes a
small read-only JSON API for the browser UI. Standard library only.
"""

from __future__ import annotations

import json
import re
import subprocess
from datetime import datetime, timezone
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

HOST = "127.0.0.1"
PORT = 8765
DASHBOARD_DIR = Path(__file__).resolve().parent
REPO_ROOT = DASHBOARD_DIR.parent

PHASES = [
    (1, "Linux Fundamentals", "01-linux-fundamentals"),
    (2, "Networking Fundamentals", "02-network-fundamentals"),
    (3, "Python Network Programming", "03-python-networking"),
    (4, "Reconnaissance & Enumeration", "04-reconnaissance"),
    (5, "Web Application Security", "05-web-security"),
    (6, "Authentication & Cryptography", "07-cryptography"),
    (7, "Wireless / IEEE 802.11", "06-wireless-security"),
    (8, "CTF & Controlled Exploitation", "09-ctf"),
    (9, "Forensics", "08-forensics"),
    (10, "Detection & Defensive Security", "10-defensive-security"),
]

LAB_RE = re.compile(r"^lab-(\d+)(?:-(.*))?$", re.IGNORECASE)
VERIFIED_RE = re.compile(r"\bVERIFIED\b", re.IGNORECASE)


def git(*args: str) -> str:
    try:
        return subprocess.run(
            ["git", "-C", str(REPO_ROOT), *args],
            capture_output=True,
            text=True,
            timeout=3,
            check=False,
        ).stdout.strip()
    except (OSError, subprocess.SubprocessError):
        return ""


def read(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""


def verified(path: Path) -> int:
    return len(VERIFIED_RE.findall(read(path))) if path.exists() else 0


def lab_title(readme: Path, fallback: str) -> str:
    for line in read(readme).splitlines():
        if line.startswith("# "):
            title = re.sub(
                r"^LAB[- ]?\d+\s*[:—-]?\s*",
                "",
                line[2:].strip(),
                flags=re.IGNORECASE,
            )
            return title or fallback
    return fallback


def lab_summary(readme: Path) -> str:
    for line in read(readme).splitlines():
        text = line.strip()
        if text and not text.startswith(("#", "```", "|")) and len(text) >= 35:
            return text[:220]
    return "CyberLab eğitim laboratuvarı."


def discover_labs() -> list[dict]:
    labs: list[dict] = []

    for phase, phase_name, folder in PHASES:
        phase_dir = REPO_ROOT / folder
        if not phase_dir.is_dir():
            continue

        for candidate in sorted(phase_dir.iterdir()):
            if not candidate.is_dir():
                continue

            match = LAB_RE.match(candidate.name)
            if not match:
                continue

            number = int(match.group(1))
            fallback = (match.group(2) or "laboratory").replace("-", " ").title()
            observations = candidate / "observations.md"
            readme = candidate / "README.md"
            verified_count = verified(observations)

            labs.append(
                {
                    "id": f"LAB-{number:03d}",
                    "number": number,
                    "title": lab_title(readme, fallback),
                    "summary": lab_summary(readme),
                    "phase": phase,
                    "phase_name": phase_name,
                    "path": str(candidate.relative_to(REPO_ROOT)),
                    "complete": (
                        readme.exists()
                        and observations.exists()
                        and verified_count > 0
                    ),
                    "verified_count": verified_count,
                }
            )

    return sorted(labs, key=lambda item: (item["number"], item["phase"]))


def phase_status(labs: list[dict]) -> list[dict]:
    """Build honest phase state from what actually exists in the repository.

    Important semantics:
    - An empty phase is never silently marked complete.
    - The highest phase that currently contains labs remains ACTIVE, even when
      every discovered lab in that phase is complete. This prevents the UI from
      claiming that the next phase has started before a lab exists there.
    - Earlier phases with no discovered labs remain NOT_STARTED rather than 100%.
    - Once a later phase actually contains a lab, earlier non-empty phases whose
      discovered labs are all complete may be shown as DONE.

    Progress is therefore progress across *discovered labs*, not a claim that the
    entire curriculum for a phase has been exhausted.
    """

    populated_phases = sorted({lab["phase"] for lab in labs})
    current_phase = max(populated_phases, default=1)
    rows: list[dict] = []

    for number, name, folder in PHASES:
        phase_labs = [lab for lab in labs if lab["phase"] == number]
        completed = sum(1 for lab in phase_labs if lab["complete"])
        total = len(phase_labs)
        progress = round((completed / total) * 100) if total else 0

        if number == current_phase:
            status = "active"
        elif number < current_phase and total > 0 and completed == total:
            status = "done"
        elif total > 0:
            status = "active"
        else:
            status = "not_started"

        rows.append(
            {
                "number": number,
                "name": name,
                "folder": folder,
                "status": status,
                "progress": progress,
                "labs": total,
                "completed_labs": completed,
            }
        )

    return rows


def git_status() -> dict:
    branch = git("branch", "--show-current") or "unknown"
    porcelain = git("status", "--porcelain")
    head = git("rev-parse", "HEAD")
    log = git("log", "-8", "--date=short", "--pretty=format:%h%x09%ad%x09%s")
    commits: list[dict] = []

    for line in log.splitlines():
        parts = line.split("\t", 2)
        if len(parts) == 3:
            commits.append(
                {"sha": parts[0], "date": parts[1], "message": parts[2]}
            )

    return {
        "branch": branch,
        "dirty": bool(porcelain),
        "changes": len(porcelain.splitlines()) if porcelain else 0,
        "head": head,
        "head_short": head[:7] if head else "",
        "commits": commits,
    }


def status() -> dict:
    labs = discover_labs()
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "server": {"host": HOST, "port": PORT, "mode": "local-only"},
        "git": git_status(),
        "labs": labs,
        "phases": phase_status(labs),
    }


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(DASHBOARD_DIR), **kwargs)

    def log_message(self, fmt: str, *args) -> None:
        print(f"[dashboard] {self.address_string()} - {fmt % args}")

    def do_GET(self) -> None:  # noqa: N802
        if urlparse(self.path).path == "/api/status":
            body = json.dumps(status(), ensure_ascii=False, indent=2).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Cache-Control", "no-store")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return

        super().do_GET()


def main() -> None:
    server = ThreadingHTTPServer((HOST, PORT), Handler)
    print("CyberLab Command Center")
    print(f"Local dashboard: http://{HOST}:{PORT}")
    print("Read-only • localhost only • Ctrl+C to stop")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping dashboard…")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
