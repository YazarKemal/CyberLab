# CyberLab — Laboratory Rules and Procedures

## Purpose of This Document

This document defines the operational rules for CyberLab. It ensures that every
experiment is safe, contained, reproducible, and educational. Rules apply to all
practical work across all phases.

---

## 1. Environment Rules

### 1.1 Isolation
- All attack/defense experiments run against deliberately vulnerable, isolated targets.
- Production systems, personal devices of others, and public services are NEVER targets.
- When in doubt about isolation, use a dedicated lab network or virtual machines.

### 1.2 Android / Termux Constraints
- We run on an Android tablet via Termux — a non-rooted environment by default.
- Raw socket operations, packet injection, and monitor mode are generally unavailable.
- Some `/proc` entries are restricted. Adapt experiments accordingly.
- Note when an experiment's fidelity is limited by the environment.

### 1.3 State Management
- Before starting an experiment, note the current system state.
- After completing an experiment, restore the system to its previous state.
- This includes: removing test files, stopping test services, restoring configs.
- "Leave no trace" on any system that isn't yours.

---

## 2. Documentation Rules

### 2.1 Lab Reports
Every practical lab MUST produce a lab report. Reports live in the appropriate
phase directory and follow this naming convention:
```
01-linux-fundamentals/lab_reports/YYYY-MM-DD-title.md
```

### 2.2 Required Sections
Each report must include:
- **Theory** — The concept being explored, explained clearly
- **Experiment** — Exact commands, code, and configuration used
- **Observation** — What happened: output, logs, metrics, screenshots
- **Conclusion** — What we learned and how it connects to real security

### 2.3 Reproducibility
- Another person (or your future self) should be able to reproduce every result.
- Document exact versions: `python --version`, `pip freeze` for relevant packages.
- Scripts are preferred over ad-hoc shell commands.
- Note any assumptions about the environment.

---

## 3. Code Rules

### 3.1 Educational Clarity Over Cleverness
- Write code that teaches. Comments should explain the "why," not the "what."
- Use descriptive variable names. Avoid single-letter names except for loop indices.
- Break complex operations into steps with intermediate variables.

### 3.2 Security-Sensitive Code
- Tools that perform scanning, exploitation, or attack simulation MUST include:
  - A clear docstring stating the educational purpose.
  - Target validation (refuse to run without an explicit target).
  - A `--dry-run` or confirmation prompt for potentially disruptive operations.
- Never build automation that removes human decision-making from attack steps.

### 3.3 Dependencies
- Phase-specific requirements go in a `requirements.txt` inside the phase directory.
- Prefer standard library when the goal is understanding the internals.
- Use external libraries when the goal is learning how to use professional tools.

---

## 4. Data Handling Rules

### 4.1 Secrets
- API keys, tokens, and credentials go in `.env` files — NEVER in source code.
- `.env` is in `.gitignore`. Verify before committing.
- Reference secrets via `os.getenv("VARIABLE_NAME")` with a clear error if missing.
- Never log or print secrets.

### 4.2 Captures and Logs
- Packet captures (`.pcap`, `.pcapng`) go in `captures/` — gitignored.
- Experiment logs go in `logs/` — gitignored.
- Before sharing captures, sanitize them: remove your IPs, MACs, credentials.
- Never commit captures containing traffic from networks you don't own.

### 4.3 Personal Data
- Do not collect, store, or process personal data of others.
- Anonymize any data used in reports (replace real usernames, IPs, emails).
- Treat all data as sensitive by default.

---

## 5. Tool Usage Rules

### 5.1 "Understand Before Using"
For each security tool we use (nmap, Wireshark, Metasploit, Burp Suite, etc.):
1. First, understand what it does and how it works internally.
2. Implement a simplified version ourselves where educationally valuable.
3. Then use the professional tool, understanding what it adds.

### 5.2 Tool Documentation
When using a new tool, document:
- What the tool does (one paragraph).
- Key commands and flags we used.
- What those flags actually do under the hood.
- Output interpretation: what each field means.

### 5.3 No Blind Script-Kiddie Behavior
- Do not run commands you don't understand.
- If a tutorial says "run this," understand what it does before running it.
- Ask questions. This is a learning environment.

---

## 6. Safety Rules

### 6.1 Rate Limiting
- When scanning, use reasonable timing (`-T2` or `-T3`, not `-T5`).
- Do not flood networks with traffic, even your own.
- Respect rate limits on any external APIs used for OSINT.

### 6.2 Destructive Testing
- Never run destructive tests (DoS, resource exhaustion) against shared infrastructure.
- Even on your own devices, understand the potential for data loss.
- Back up important data before experiments that modify system state.

### 6.3 Malware Handling
- Never download or execute real malware, even in a lab environment.
- Study malware techniques through code examples and CTF challenges.
- If you need to analyze a real sample, use an air-gapped VM.

---

## 7. Git Rules

### 7.1 What to Commit
- Source code, documentation, lab reports, configurations.
- Small, focused commits with descriptive messages.

### 7.2 What NOT to Commit
- Secrets, credentials, API keys (`.env` files).
- Packet captures, scan results, or logs with sensitive data.
- Large binary files (use `.gitignore` or Git LFS if needed).
- Virtual machine images or disk images.

### 7.3 Commit Messages
- Use the format: `phase-NN: brief description of change`
- Example: `phase-02: add TCP handshake lab report`
- End with: `Co-Authored-By: Claude <noreply@anthropic.com>`

---

## 8. Learning Rules

### 8.1 Depth Over Breadth
It's better to deeply understand one vulnerability class than to superficially
know ten. Master the fundamentals before moving on.

### 8.2 Question Everything
- Why does this work?
- What assumptions is this built on?
- What happens if I change this parameter?
- How would a defender detect this?
- How would I protect against this?

### 8.3 The "Feynman Test"
If you can't explain a concept clearly in your own words, you don't fully
understand it yet. Write explanations in lab reports as if teaching someone else.

### 8.4 Connect the Dots
- How does this networking concept relate to that web vulnerability?
- How does this crypto primitive protect that wireless protocol?
- Cybersecurity is interconnected — build a mental model of the whole system.

---

## 9. Collaboration Rules

### 9.1 Working with AI (Claude Code)
- Claude Code is a learning partner, not an answer key.
- Ask "why" and "how" — don't just accept generated code.
- Use AI to explain concepts, suggest experiments, and review your understanding.
- CLAUDE.md contains the complete instructions for AI-assisted sessions.

### 9.2 External Resources
- Cite sources: blog posts, papers, documentation, CTF writeups.
- Prefer primary sources (RFCs, official docs) over secondary (tutorials, summaries).
- Keep a bibliography of useful resources in each phase directory.

---

## 10. Emergency Procedures

### 10.1 If Something Goes Wrong
1. Stop immediately. Do not try to "fix" it by trying more things.
2. Document what happened — what command, what was the expected result, what was actual?
3. Assess impact — did this affect anything outside the lab?
4. Restore to a known good state.
5. Update the lab report with what went wrong and why — failures are learning opportunities.

### 10.2 If You Accidentally Test a Wrong Target
1. Stop all activity immediately.
2. Document what happened and what was accessed.
3. If the target is a service you use (your email, bank, etc.):
   - Change your passwords.
   - Check for any unusual activity.
   - Contact the service provider if necessary.
4. Add the incident to your learning record.

---

*These rules evolve as the lab grows. Review and update them periodically.*
*Last updated: 2026-08-09*
