# Ethics and Responsible Conduct

## Why This Document Exists

Cybersecurity knowledge is powerful. The same skills that protect systems can
also compromise them. This document defines the ethical boundaries within which
CyberLab operates. It exists not as legal advice, but as a personal commitment
to responsible practice.

## Core Principles

### 1. Authorization is Not Optional
Never test, scan, or probe any system without explicit authorization. "It's
publicly accessible" is not authorization. "I'm just curious" is not authorization.
"If I don't do anything harmful" is not authorization.

Authorized targets are:
- Your own devices and accounts
- Your own networks (home WiFi, personal VPS)
- Deliberately vulnerable applications running on your own infrastructure
- CTF challenge platforms you have registered for
- Systems for which you have written documentation of authorization

### 2. Do No Harm
Even on authorized targets:
- Do not disrupt services others rely on
- Do not access, modify, or delete data that isn't yours
- Do not leave systems in a compromised state after testing
- Clean up after experiments: remove backdoors, restore configurations

### 3. Protect Privacy
- Do not capture traffic from networks you don't own
- Do not store, share, or publish data that could identify others
- Anonymize any data used in reports or writeups
- Be especially careful with packet captures — they may contain passwords,
  cookies, or personal information

### 4. Responsible Disclosure
If you discover a vulnerability in someone else's system:
- Do not exploit it further than necessary to confirm it
- Report it privately to the owner with clear reproduction steps
- Give reasonable time for a fix before any public discussion
- Never demand payment or threaten exposure

### 5. Legal Compliance
- Know the computer crime laws in your jurisdiction
- In Turkey: Article 243-246 of the Turkish Penal Code (TCK) covers computer crimes
- The CFAA (US) and Computer Misuse Act (UK) may apply to systems hosted in those countries
- Ignorance of the law is not a defense

## Educational Purpose

CyberLab exists for one reason: **education**. Every experiment, every tool,
every lab is designed to build understanding. This is not a platform for:

- Attacking real systems
- Harassing or intimidating others
- Financial fraud or theft
- Political activism or hacktivism
- Developing malware for distribution

## Red Flags — When to Stop and Reconsider

Stop immediately and seek guidance if:
- You're about to test something and feel the need to hide it
- You're not sure if you have permission
- The target belongs to someone who would be angry if they knew
- You're feeling pressure (from yourself or others) to cross a boundary
- The potential impact of a mistake is higher than you can accept

## Professional Ethics Reference

- **(ISC)² Code of Ethics** — The gold standard for security professionals
- **ACM Code of Ethics** — Computing professionals' ethical framework
- **SANS IT Code of Ethics** — Practical ethics for security practitioners
- **Offensive Security Code of Conduct** — Ethics for penetration testers

## Personal Commitment

By using this repository, I commit to:
1. Using these skills to protect, not harm
2. Always obtaining authorization before testing
3. Respecting the privacy and property of others
4. Continuing to learn about the ethical dimensions of security work
5. Stopping and asking when I'm uncertain about the right course of action

---

*"With great power comes great responsibility." — Not just a Spider-Man quote,
but the fundamental truth of cybersecurity work.*
