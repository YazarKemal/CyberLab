# CyberLab — Personal Cybersecurity Laboratory

**Author:** YazarKemal
**Platform:** Android (Termux) + Python
**Focus:** Understanding security from first principles, not memorizing tools.

## Purpose

CyberLab is a controlled, educational cybersecurity laboratory. Every experiment
here is about understanding *how* and *why* security mechanisms work — from the
protocol level up — rather than blindly running Kali Linux commands.

## Philosophy

1. **Theory first** — Understand the protocol, algorithm, or mechanism.
2. **Implement** — Build a simplified version ourselves where educationally useful.
3. **Test** — Run it in our controlled lab environment.
4. **Compare** — Contrast our implementation with professional tools.
5. **Document** — Record theory, experiment, observations, and conclusions.

## Authorized Scope

All practical security testing is strictly limited to:
- `localhost` and our own devices
- Our own networks
- Deliberately vulnerable applications (e.g., OWASP Juice Shop, DVWA)
- CTF challenge systems
- Systems for which we have explicit written authorization

## Environment

- **Device:** Android tablet
- **Terminal:** Termux
- **Language:** Python (primary)
- **Version Control:** Git + GitHub
- **AI Assistant:** Claude Code CLI

## Repository Structure

```
CyberLab/
├── 01-linux-fundamentals/      # Linux internals, permissions, processes
├── 02-network-fundamentals/    # TCP/IP, OSI model, packet structure
├── 03-python-networking/       # Sockets, scapy, protocol implementations
├── 04-reconnaissance/          # Enumeration, OSINT, scanning (authorized only)
├── 05-web-security/            # OWASP Top 10, HTTP, sessions, XSS, SQLi
├── 06-wireless-security/       # 802.11, WPA, monitor mode theory
├── 07-cryptography/            # Symmetric, asymmetric, hashing, TLS internals
├── 08-forensics/               # Disk, memory, network forensics
├── 09-ctf/                     # Capture The Flag writeups and practice
├── 10-defensive-security/      # Hardening, monitoring, incident response
├── tools/                      # Our own educational tools and scripts
├── labs/                       # Isolated lab environments and configurations
├── docs/                       # Documentation, glossary, roadmap, ethics
├── reports/                    # Lab reports and findings
└── scripts/                    # Utility and setup scripts
```

## Getting Started

```bash
# Clone the repository
git clone https://github.com/YazarKemal/CyberLab.git
cd CyberLab

# Create a virtual environment
python -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Read the roadmap
cat docs/ROADMAP.md
```

## Important Rules

- **Never** expose API keys, credentials, or tokens — use `.env` files
- **Never** commit scan captures containing sensitive information
- **Never** run scans or attacks against systems you do not own or have permission to test
- **Always** document your commands, observations, and conclusions
- **Always** keep experiments reproducible

## License

This project is for personal education. All content is my own work unless otherwise noted.
