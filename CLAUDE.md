# CLAUDE.md — Instructions for Claude Code Sessions

## Project Identity

This is **CyberLab**, the personal cybersecurity education laboratory of YazarKemal.
It runs on an **Android tablet via Termux**, with **Python** as the primary language.

**This is an educational project.** Every activity here is about learning how
security mechanisms work internally — not about attacking real systems.

## Core Directives

### 1. Explain, Don't Just Invoke
When introducing technical terminology (e.g., "SYN flood", "ARP poisoning", "padding oracle"),
explain the concept before using it. Assume the user wants to understand the *mechanism*,
not just the result. Prefer protocol-level understanding over wrapping tools blindly.

### 2. Structure Lab Work as Science
For every experiment or lab, organize thinking into four sections:
- **Theory** — What principle or mechanism is being explored? How does it work normally?
- **Experiment** — What exactly are we doing? Commands, code, configuration.
- **Observation** — What happened? Include actual output, logs, packet captures.
- **Conclusion** — What did we learn? How does this connect to real-world security?

### 3. Keep Experiments Reproducible
- Document exact commands and their expected output.
- Note environment prerequisites (Python version, installed packages, OS config).
- Use version-controlled scripts, not ad-hoc shell history.
- Tag or note Android/Termux-specific limitations when they apply.

### 4. Authorized Scope — Read Before Any Security Action
All practical security testing is STRICTLY limited to:
- `localhost` and this device
- Our own networks (home lab, personal WiFi)
- Deliberately vulnerable applications (DVWA, Juice Shop, Metasploitable, etc.)
- CTF challenge systems
- Systems for which we have explicit written authorization

**Before running any network scan, packet capture, or exploit:**
1. Verify the target is in the authorized scope.
2. State the target explicitly in your response.
3. If there is any doubt, ask before proceeding.

### 5. Protect Secrets and Sensitive Data
- **Never** write API keys, tokens, or credentials into any file.
- Use `.env` files (gitignored) for secrets.
- Reference secrets in code via `os.getenv("VARIABLE_NAME")`.
- **Never** commit packet captures (`.pcap`, `.pcapng`) that may contain sensitive traffic.
- **Never** commit scan results that reveal information about real networks.
- The `captures/` and `logs/` directories are gitignored — use them for volatile data.

### 6. Build Before Buying
When educationally valuable:
1. First, implement a simplified version ourselves (e.g., a basic port scanner, a simple
   HTTP client, a minimal ARP spoofer).
2. Then, compare with the professional tool (nmap, curl, ettercap).
3. Discuss differences: what did the professional tool handle that ours didn't?

This builds genuine understanding that memorizing `nmap -sS -p-` never will.

### 7. Android / Termux Awareness
- We run on an Android tablet. Some operations require root (not assumed).
- Raw socket operations (`AF_PACKET`, `SOCK_RAW`) may be restricted.
- `/proc` and `/sys` may have limited visibility.
- Termux prefix is `/data/data/com.termux/files/usr`.
- Python packages with C extensions may need `build-essential` in Termux.
- WiFi monitor mode is generally not available on Android without custom firmware.
- Always note when an experiment is limited by the Android environment.

### 8. File Boundaries
- **Do not** modify, create, or delete files outside the `CyberLab/` repository
  unless explicitly asked.
- Within CyberLab, organize work by phase directory (e.g., `02-network-fundamentals/`
  for networking experiments).

### 9. Lab Report Template
When creating a lab report, use this structure:
```markdown
# Lab: [Title]
- **Phase:** [e.g., 02-network-fundamentals]
- **Date:** YYYY-MM-DD
- **Environment:** [Android/Termux, Python version, key packages]

## Theory
[Explain the underlying concepts and mechanisms.]

## Experiment
[Step-by-step: what we did, commands run, code written.]

## Observation
[What we saw: output, packet captures, logs, screenshots.]

## Conclusion
[What we learned. How this applies to real security. What to explore next.]
```

### 10. Code Style
- Python code should be clear and well-commented — educational, not clever.
- Use type hints where they aid understanding.
- Prefer standard library over external dependencies when the goal is learning.
- Script names should be descriptive: `tcp_handshake_sim.py`, not `lab1.py`.

### 11. Git Practices
- Commit with meaningful messages describing what was done and why.
- Each logical unit (a completed lab, a new tool, documentation) gets its own commit.
- Never commit to `main` directly without the user asking — always confirm first.
- End commit messages with:
  `Co-Authored-By: Claude <noreply@anthropic.com>`

### 12. Tone
- Be patient and thorough. This is a learning environment.
- Celebrate understanding, not just results.
- When something doesn't work, treat debugging as a learning opportunity.
- Use "we" — this is a collaborative learning journey.
