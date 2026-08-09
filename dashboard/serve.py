#!/usr/bin/env python3
"""Local-only dashboard server for CyberLab.

Serves static dashboard files and a read-only /api/status endpoint generated
from the local repository. No third-party dependencies and no remote access.
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

LAB_DIR_RE = re.compile(r"^lab-(\d+)(?:-(.*))?$", re.IGNORECASE)
VERIFIED_RE = re.compile(r"\bVERIFIED\b", re.IGNORECASE)


def run_git(*args: str) -> str:
    try:
        completed = subprocess.run(
            ["git", "-C", str(REPO_ROOT), *args],
            capture_output=True,
            text=True,
            timeout=3,
            check=False,
        )
        return completed.stdout.strip()
    except (OSError, subprocess.SubprocessError):
        return ""


def title_from_readme(readme: Path, fallback: str) -> str:
    if not readme.exists():
        return fallback
    try:
        for line in readme.read_text(encoding="utf-8", errors="replace").splitlines():
            if line.startswith("# "):
                title = line[2:].strip()
                title = re.sub(r"^LAB[- ]?\d+\s*[:—-]?\s*", "", title, flags=re.IGNORECASE)
                return title or fallback
    except OSError:
        pass
    return fallback


def summary_from_readme(readme: Path) -> str:
    if not readme.exists():
        return "Laboratuvar klasörü keşfedildi."
    try:
        lines = readme.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError:
        return "Laboratuvar klasörü keşfedildi."

    for line in lines:
        clean = line.strip()
        if not clean or clean.startswith("#") or clean.startswith("```") or clean.startswith("|"):
            continue
        if len(clean) >= 35:
            return clean[:220]
    return "CyberLab eğitim laboratuvarı."


def verified_count(observations: Path) -> int:
    if not observations.exists():
        return 0
    try:
        text = observations.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return 0
    return len(VERIFIED_RE.findall(text))


def discover_labs() -> list[dict]:
    labs: list[dict] = []

    for phase_number, phase_name, folder_name in PHASES:
        phase_dir = REPO_ROOT / folder_name
        if not phase_dir.is_dir():
            continue

        for candidate in sorted(phase_dir.iterdir()):
            if not candidate.is_dir():
                continue
            match = LAB_DIR_RE.match(candidate.name)
            if not match:
                continue

            lab_number = int(match.group(1))
            slug = (match.group(2) or "laboratory").replace("-", " ").strip()
            readme = candidate / "README.md"
            observations = candidate / "observations.md"
            title = title_from_readme(readme, slug.title())
            complete = readme.exists() and observations.exists() and observations.stat().st_size > 0

            labs.append(
                {
                    "id": f"LAB-{lab_number:03d}",
                    "number": lab_number,
                    "title": title,
                    "summary": summary_from_readme(readme),
                    "phase": phase_number,
                    "phase_name": phase_name,
                    "path": str(candidate.relative_to(REPO_ROOT)),
                    "complete": complete,
                    "verified_count": verified_count(observations),
                }
            )

    labs.sort(key=lambda item: (item["number"], item["phase"]))
    return labs


def phase_status(labs: list[dict]) -> list[dict]:
    phase_rows: list[dict] = []
    first_pending_seen = False

    for number, name, folder_name in PHASES:
        phase_labs = [lab for lab in labs if lab["phase"] == number]
        if phase_labs and all(lab["complete"] for lab in phase_labs):
            status = "done"
            progress = 100
        elif phase_labs:
            done = sum(1 for lab in phase_labs if lab["complete"])
            progress = round((done / len(phase_labs)) * 100)
            status = "active"
            first_pending_seen = True
        elif not first_pending_seen:
            status = "active"
            progress = 0
            first_pending_seen = True
        else:
            status = "pending"
            progress = 0

        phase_rows.append(
            {
                "number": number,
                "name": name,
                "folder": folder_name,
                "status": status,
                "progress": progress,
                "labs": len(phase_labs),
            }
        )

    return phase_rows


def git_status() -> dict:
    branch = run_git("branch", "--show-current") or "unknown"
    porcelain = run_git("status", "--porcelain")
    head = run_git("rev-parse", "HEAD")
    log_text = run_git("log", "-8", "--date=short", "--pretty=format:%h%x09%ad%x09%s")

    commits = []
    for line in log_text.splitlines():
        parts = line.split("\t", 2)
        if len(parts) == 3:
            commits.append({"sha": parts[0], "date": parts[1], "message": parts[2]})

    return {
        "branch": branch,
        "dirty": bool(porcelain),
        "changes": len(porcelain.splitlines()) if porcelain else 0,
        "head": head,
        "head_short": head[:7] if head else "",
        "commits": commits,
    }


def build_status() -> dict:
    labs = discover_labs()
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "server": {"host": HOST, "port": PORT, "mode": "local-only"},
        "git": git_status(),
        "labs": labs,
        "phases": phase_status(labs),
    }


class CyberLabHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(DASHBOARD_DIR), **kwargs)

    def log_message(self, fmt: str, *args) -> None:
        print(f"[dashboard] {self.address_string()} - {fmt % args}")

    def do_GET(self) -> None:  # noqa: N802
        path = urlparse(self.path).path
        if path == "/api/status":
            payload = json.dumps(build_status(), ensure_ascii=False, indent=2).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Cache-Control", "no-store")
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)
            return

        super().do_GET()


def main() -> None:
    server = ThreadingHTTPServer((HOST, PORT), CyberLabHandler)
    print("CyberLab Command Center")
    print(f"Local dashboard: http://{HOST}:{PORT}")
    print("Scope: localhost only")
    print("Press Ctrl+C to stop.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping dashboard…")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
