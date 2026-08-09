# CyberLab — Learning Roadmap

This roadmap defines our educational journey through cybersecurity, organized into
10 progressive phases. Each phase builds on the knowledge and skills of previous ones.

---

## Phase 1 — Linux Fundamentals

**Directory:** `01-linux-fundamentals/`

### Concepts
- Linux architecture: kernel vs. userspace, system calls, process model
- File system hierarchy: FHS standard, inodes, mount points, `/proc`, `/sys`
- Permissions model: UIDs, GIDs, read/write/execute bits, setuid/setgid, capabilities
- Process management: `fork()`, `exec()`, signals, job control, daemons
- Shell scripting: bash fundamentals, pipes, redirection, text processing
- Package management: `apt`, `pkg` (Termux), dependencies

### Terminology
- **Kernel** — The core of the OS that manages hardware, memory, and processes.
- **Userspace** — Everything running outside the kernel: shells, apps, services.
- **System call (syscall)** — A controlled entry point from userspace into the kernel.
- **inode** — A data structure that stores metadata about a file (permissions, size, location).
- **setuid** — A permission bit that makes a program run as its owner, not the caller.
- **Daemon** — A background process, usually started at boot (e.g., `sshd`, `cron`).

### Practical Laboratories
1. Explore `/proc` — read process info, kernel parameters, network state without any tools.
2. Permission escalation puzzle — navigate a maze of directories with mixed permissions.
3. Write a simple daemon in bash that logs timestamps.
4. Trace a system call with `strace` (if available).
5. Build a minimal chroot jail.

### Programming Exercises
- Reimplement `ls -l` in Python using `os.stat()` and `pwd`/`grp` modules.
- Write a process tree visualizer reading `/proc`.
- Implement a simple shell with pipe support.

### Completion Criteria
- Can explain what happens when you type `ls -l` (from terminal to kernel and back).
- Can navigate the filesystem, manage permissions, and write shell scripts comfortably.
- Understand process ownership and the basics of privilege separation.

---

## Phase 2 — Networking Fundamentals

**Directory:** `02-network-fundamentals/`

### Concepts
- OSI model: all 7 layers, what each does, real protocol examples
- TCP/IP stack: IP, TCP, UDP, ICMP — header formats, state machines
- Addressing: MAC addresses, IPv4/IPv6, subnets, CIDR notation, routing
- DNS: resolution process, record types, caching, DNSSEC basics
- DHCP: DORA process (Discover, Offer, Request, Acknowledge)
- ARP: how IP addresses resolve to MAC addresses on a local network
- NAT: how private addresses reach the public internet

### Terminology
- **OSI Model** — Open Systems Interconnection model: Physical, Data Link, Network,
  Transport, Session, Presentation, Application.
- **TCP three-way handshake** — SYN → SYN-ACK → ACK. Establishes a connection.
- **CIDR** — Classless Inter-Domain Routing; `192.168.1.0/24` notation.
- **MTU** — Maximum Transmission Unit; largest packet size a link can carry.
- **TTL** — Time To Live; limits how many hops a packet can traverse.

### Practical Laboratories
1. Capture and analyze a TCP handshake with tcpdump.
2. Trace the path to a remote host and explain every hop shown by traceroute.
3. Write a DNS query by hand (construct the binary packet, send via UDP, parse reply).
4. Observe ARP traffic on a local network.
5. Build and analyze ICMP echo request/reply (ping) packets.

### Programming Exercises
- Implement a TCP three-way handshake simulator showing state transitions.
- Build a minimal DNS resolver in Python (send query, parse response).
- Write a traceroute implementation using UDP with incrementing TTL.

### Completion Criteria
- Can draw and label all layers of the OSI model with real protocol examples.
- Can explain every field in a TCP header.
- Can manually decode a DNS packet from hex.

---

## Phase 3 — Python Network Programming

**Directory:** `03-python-networking/`

### Concepts
- Sockets: `socket()`, `bind()`, `listen()`, `accept()`, `connect()`, `send()`, `recv()`
- Blocking vs. non-blocking I/O, `select()`, `epoll()`
- TCP server/client patterns: iterative, forking, threaded, async
- UDP communication: datagrams, reliability tradeoffs
- Raw sockets: constructing custom IP/TCP/UDP packets (theory; Android may limit)
- Application protocols: HTTP/1.1, SMTP, FTP — protocol state machines
- Serialization: JSON, binary formats, TLV (Type-Length-Value) encoding

### Terminology
- **Socket** — An endpoint for communication, identified by IP + port.
- **Raw socket** — A socket that gives access to the underlying packet headers.
- **select/poll/epoll** — I/O multiplexing: monitor many sockets from one thread.
- **TLV encoding** — Type-Length-Value: a common binary protocol pattern.

### Practical Laboratories
1. Build an echo server (single-threaded, then multi-threaded, then async).
2. Implement a port scanner from scratch — TCP connect scan, SYN scan (theory).
3. Build a minimal HTTP server that serves files from a directory.
4. Write an HTTP client that follows redirects and handles cookies.
5. Create a chat protocol with a custom binary format.

### Programming Exercises
- TCP port scanner with configurable timeout and banner grabbing.
- Mini HTTP/1.1 server handling GET, POST, and persistent connections.
- Protocol fuzzer: send malformed inputs to a server and observe behavior.

### Completion Criteria
- Can write a working TCP client and server from memory.
- Understands the tradeoffs between blocking, threaded, and async I/O models.
- Can implement a simple application-layer protocol.

---

## Phase 4 — Reconnaissance and Enumeration

**Directory:** `04-reconnaissance/`

### Concepts
- The reconnaissance lifecycle: passive → active → enumeration → vulnerability mapping
- OSINT: open-source intelligence gathering techniques
- Port scanning: TCP connect, SYN (half-open), FIN, NULL, Xmas scans — how they differ
- Service/version detection: banner grabbing, probe-and-match
- OS fingerprinting: TCP/IP stack quirks, TTL analysis, window size patterns
- DNS enumeration: zone transfers, brute-force subdomain discovery
- Web enumeration: directory brute-forcing, virtual host discovery

### Terminology
- **OSINT** — Open-Source Intelligence: information from publicly available sources.
- **SYN scan** — Send SYN, if SYN-ACK comes back the port is open; send RST (never complete handshake).
- **Banner grabbing** — Reading the welcome message a service sends on connect.
- **Zone transfer** — AXFR: copying an entire DNS zone from a nameserver.

### Practical Laboratories
1. Perform passive recon on your own GitHub profile — what can an attacker learn?
2. Build a TCP connect scanner and compare its speed/log footprint with nmap.
3. Write a banner grabber that identifies services on common ports.
4. DNS recon: enumerate subdomains of a domain you own.
5. Compare scan types: run connect, SYN, and FIN scans against localhost services.

### Programming Exercises
- Multi-threaded port scanner with service detection.
- Subdomain enumeration tool using wordlists.
- Shodan-like banner collector that fingerprints services.

### Completion Criteria
- Can conduct a complete reconnaissance workflow on an authorized target.
- Understands the strengths, weaknesses, and detectability of each scan type.
- Knows how to correlate recon findings to identify potential attack surfaces.

---

## Phase 5 — Web Application Security

**Directory:** `05-web-security/`

### Concepts
- HTTP deep dive: methods, headers, cookies, caching, CORS, CSP, HSTS
- Same-Origin Policy: what it is, why it exists, how it's bypassed
- OWASP Top 10: each vulnerability class, how it works, how to prevent it
- SQL Injection: error-based, UNION-based, blind (boolean, time-based)
- XSS: reflected, stored, DOM-based; CSP as defense
- CSRF: how it works, token-based protection, SameSite cookies
- Authentication: sessions vs. tokens (JWT), OAuth2 flow, password storage
- Server-side vulnerabilities: SSRF, XXE, deserialization, command injection

### Terminology
- **Same-Origin Policy (SOP)** — Scripts from one origin cannot access data from another.
- **CORS** — Cross-Origin Resource Sharing: a controlled relaxation of SOP.
- **SQLi** — SQL Injection: inserting SQL commands into application input.
- **XSS** — Cross-Site Scripting: injecting JavaScript into pages viewed by others.
- **CSRF** — Cross-Site Request Forgery: tricking a browser into making unwanted requests.
- **JWT** — JSON Web Token: a signed (and optionally encrypted) token for claims transfer.

### Practical Laboratories
1. Set up OWASP Juice Shop or DVWA and explore every vulnerability category.
2. Manual SQL injection: extract data from a vulnerable app without sqlmap.
3. XSS playground: craft payloads that bypass increasingly strict filters.
4. Analyze JWT tokens: decode, tamper with `alg=none`, crack weak HMAC secrets.
5. CSRF attack and defense: craft a malicious page, then implement token protection.

### Programming Exercises
- Build a vulnerable web app (intentionally) to understand each flaw from both sides.
- Write an HTTP request smuggler detector.
- Implement a web fuzzer that discovers hidden endpoints and parameters.

### Completion Criteria
- Can exploit and explain every OWASP Top 10 vulnerability.
- Can review source code and identify web security flaws.
- Understands the defense-in-depth approach to web security.

---

## Phase 6 — Authentication and Cryptography

**Directory:** `07-cryptography/` (note: cryptography is Phase 7 in directory numbering)

### Concepts
- Hashing: SHA-256, bcrypt, Argon2 — what makes a good password hash
- Symmetric encryption: AES (ECB, CBC, GCM), key sizes, IVs/nonces
- Asymmetric encryption: RSA, ECC — key generation, signing, encryption
- Key exchange: Diffie-Hellman (basic and ECDH), how TLS uses it
- TLS 1.3: handshake walkthrough, certificate chains, forward secrecy
- PKI: certificates, CAs, chain of trust, certificate pinning
- Classic ciphers: Caesar, Vigenère, Enigma — educational value for understanding patterns

### Terminology
- **Hash** — A one-way function mapping arbitrary data to a fixed-size digest.
- **Salt** — Random data added to a password before hashing to defeat rainbow tables.
- **IV/Nonce** — Initialization Vector / Number used Once: ensures identical plaintexts
  produce different ciphertexts.
- **Forward secrecy** — Compromising a long-term key does not decrypt past sessions.
- **Certificate chain** — End-entity → Intermediate CA → Root CA (trust anchor).

### Practical Laboratories
1. Implement AES-CBC encryption/decryption from the spec (then compare with OpenSSL).
2. Crack weak passwords with hashcat (against known hash lists).
3. Walk through a TLS 1.3 handshake with Wireshark — identify every message.
4. Build a minimal CA: generate root cert, sign intermediate, sign server certificate.
5. Implement the Diffie-Hellman key exchange with small numbers to build intuition.

### Programming Exercises
- Password strength checker that estimates entropy and crack time.
- File encryption tool using AES-GCM with an Argon2-derived key.
- Minimal TLS client that performs a handshake and verifies the certificate chain.

### Completion Criteria
- Can explain the TLS 1.3 handshake message by message.
- Understands when to use hashing vs. encryption vs. signing.
- Can implement cryptographic primitives correctly (and knows when NOT to roll your own).

---

## Phase 7 — Wireless / IEEE 802.11 Security

**Directory:** `06-wireless-security/`

### Concepts
- 802.11 frame structure: management, control, and data frames
- WiFi security evolution: WEP → WPA → WPA2 → WPA3
- The 4-way handshake: how WPA2 derives session keys
- WEP weaknesses: IV reuse, RC4 keystream recovery
- WPA2 weaknesses: KRACK attack on the 4-way handshake
- Monitor mode and packet injection (theory; limited on Android)
- Bluetooth security basics: pairing, LE Secure Connections

### Terminology
- **BSSID** — Basic Service Set Identifier: the MAC address of the access point.
- **SSID** — Service Set Identifier: the human-readable network name.
- **4-way handshake** — The exchange that proves both sides know the PMK and derives PTK.
- **PMK** — Pairwise Master Key: derived from the passphrase and SSID via PBKDF2.
- **PTK** — Pairwise Transient Key: per-session encryption key, derived during handshake.
- **Monitor mode** — WiFi adapter mode that captures all frames, not just those addressed to us.

### Practical Laboratories
1. Analyze 802.11 frame captures in Wireshark — identify beacon, probe, auth, association.
2. Simulate the WPA2 4-way handshake step by step in Python.
3. Crack a WPA2 handshake capture using a wordlist (against your own network).
4. Compare WEP, WPA, WPA2, WPA3 security properties in a table.
5. Study KRACK: replay the handshake message 3 attack in our simulator.

### Programming Exercises
- 802.11 frame parser that decodes beacon and probe request frames.
- WPA2 4-way handshake simulator showing key derivation.
- WiFi scanner that lists nearby networks (using Android API if available).

### Completion Criteria
- Can explain every step of the WPA2 4-way handshake.
- Understands the cryptographic weaknesses that broke WEP and WPA2.
- Can describe how WPA3 improves on WPA2 (SAE/dragonfly handshake).

---

## Phase 8 — CTF and Controlled Exploitation

**Directory:** `09-ctf/`

### Concepts
- Binary exploitation: buffer overflows, format strings, ROP chains
- Reverse engineering: disassembly (Ghidra/radare2), decompilation, patching
- Web exploitation: advanced SQLi, SSTI, deserialization attacks
- Privilege escalation: Linux enumeration, SUID abuse, kernel exploits
- Exploit development workflow: fuzzing → crash analysis → control → shellcode
- Common CTF categories: pwn, rev, web, crypto, forensics, misc

### Terminology
- **Buffer overflow** — Writing past the end of a buffer, overwriting adjacent memory.
- **ROP** — Return-Oriented Programming: chaining existing code snippets (gadgets).
- **Shellcode** — Machine code spawned as a payload, typically opening a shell.
- **ASLR** — Address Space Layout Randomization: randomizes memory addresses.
- **DEP/NX** — Data Execution Prevention / No-eXecute: marks data pages as non-executable.
- **Canary** — A stack value checked before function return to detect overflows.

### Practical Laboratories
1. Solve progressively harder picoCTF / OverTheWire challenges.
2. Stack buffer overflow: overflow a buffer, control EIP/RIP, spawn a shell.
3. Format string vulnerability: leak memory and write arbitrary values.
4. ROP chain: bypass NX by calling `system("/bin/sh")` via gadgets.
5. Reverse engineer a simple crackme binary.

### Programming Exercises
- Write a simple vulnerable C program (buffer overflow, format string).
- Build an exploit development helper: pattern generator, offset finder.
- Create a ROP gadget finder.

### Completion Criteria
- Can exploit a basic stack buffer overflow with ASLR and NX enabled.
- Can read x86/x86-64 assembly well enough to understand control flow.
- Has solved at least 20 CTF challenges across multiple categories.

---

## Phase 9 — Forensics

**Directory:** `08-forensics/`

### Concepts
- Digital evidence handling: chain of custody, write blockers, hashing
- Disk forensics: MBR/GPT, partition tables, file system internals (NTFS, ext4)
- Memory forensics: process listing, network connections, injected code
- Network forensics: flow analysis, protocol decoding, timeline reconstruction
- File carving: recovering files based on headers/footers (magic bytes)
- Steganography: LSB embedding, metadata hiding, detection techniques
- Anti-forensics: timestomping, log wiping, encryption, data hiding

### Terminology
- **Chain of custody** — Documentation tracking who handled evidence and when.
- **File carving** — Extracting files from raw disk images using file signatures.
- **Magic bytes** — The first few bytes of a file that identify its type.
- **Slack space** — Unused space between the end of a file and the end of its last cluster.
- **Timestomping** — Modifying file timestamps to mislead investigators.

### Practical Laboratories
1. Analyze a disk image: recover deleted files, examine MFT/inode tables.
2. Memory dump analysis: list processes, find hidden modules, extract strings.
3. Carve files from a raw disk image using header/footer signatures.
4. Extract hidden data from images using LSB steganalysis.
5. Reconstruct a timeline of user activity from log files.

### Programming Exercises
- File carver that scans raw data for known magic bytes and extracts files.
- Log parser that builds a timeline from multiple log sources.
- Memory dump string extractor with filtering for URLs, emails, and passwords.

### Completion Criteria
- Can acquire, hash, and analyze a forensic disk image.
- Knows how to recover deleted files and detect tampering.
- Can correlate evidence from disk, memory, and network sources.

---

## Phase 10 — Detection, Hardening and Defensive Security

**Directory:** `10-defensive-security/`

### Concepts
- Defense in depth: layered security across network, host, application, and data
- Threat modeling: STRIDE, attack trees, risk assessment
- System hardening: CIS benchmarks, minimal install, principle of least privilege
- Network defense: firewalls (iptables/nftables), IDS/IPS (Snort/Suricata), segmentation
- Logging and monitoring: auditd, syslog, SIEM concepts, detection engineering
- Incident response: preparation, detection, containment, eradication, recovery
- Threat intelligence: IoCs (Indicators of Compromise), TTPs, MITRE ATT&CK
- Endpoint security: HIDS, application allowlisting, EDR concepts

### Terminology
- **Defense in depth** — Multiple layers of security controls; no single point of failure.
- **IDS/IPS** — Intrusion Detection/Prevention System: detects (IDS) or blocks (IPS) attacks.
- **SIEM** — Security Information and Event Management: aggregates and correlates logs.
- **IoCs** — Indicators of Compromise: artifacts that suggest an intrusion (hashes, IPs, domains).
- **MITRE ATT&CK** — A knowledge base of adversary tactics, techniques, and procedures.
- **Least privilege** — Every process/user gets only the minimum access needed.

### Practical Laboratories
1. Harden a Linux system using CIS benchmark recommendations.
2. Configure iptables/nftables firewall rules and test them.
3. Deploy and tune Snort/Suricata IDS rules.
4. Set up centralized logging with auditd and analyze logs.
5. Simulate an incident: detect, contain, and document the response.

### Programming Exercises
- Log-based intrusion detection: detect brute force, port scans, and privilege escalation.
- Firewall rule analyzer that finds redundant or conflicting rules.
- MITRE ATT&CK navigator: map observed techniques to the framework.

### Completion Criteria
- Can design a defense-in-depth architecture for a small organization.
- Knows how to detect common attack patterns in logs.
- Can respond to and document a security incident methodically.

---

## Progress Tracking

| Phase | Title | Status |
|-------|-------|--------|
| 1 | Linux Fundamentals | Not Started |
| 2 | Networking Fundamentals | Not Started |
| 3 | Python Network Programming | Not Started |
| 4 | Reconnaissance and Enumeration | Not Started |
| 5 | Web Application Security | Not Started |
| 6 | Authentication and Cryptography | Not Started |
| 7 | Wireless / 802.11 Security | Not Started |
| 8 | CTF and Controlled Exploitation | Not Started |
| 9 | Forensics | Not Started |
| 10 | Detection, Hardening and Defensive Security | Not Started |

---

*This roadmap is a living document. Phases may be reordered or refined as we progress.*
