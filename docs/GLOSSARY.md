# Cybersecurity Glossary

A living glossary of cybersecurity terminology. Terms are added as they are
introduced in labs and experiments. Each definition aims for clarity and
conceptual understanding, not just a one-line summary.

## How to Use

- Terms are organized alphabetically.
- Each entry includes: the term, its category, and a clear definition.
- Where helpful, entries include related terms and real-world analogies.
- This glossary grows with the project — terms are added as we encounter them.

---

## A

### ACL (Access Control List)
**Category:** System Security
A list of permissions attached to an object (file, directory, network resource)
that specifies which users or system processes can access it and what operations
they can perform.

### AES (Advanced Encryption Standard)
**Category:** Cryptography
A symmetric block cipher standardized by NIST. Operates on 128-bit blocks with
key sizes of 128, 192, or 256 bits. The most widely used symmetric encryption
algorithm today.

### APT (Advanced Persistent Threat)
**Category:** Threat Intelligence
A sophisticated, long-term cyberattack in which an intruder establishes an
undetected presence in a network to steal sensitive data over time. Usually
attributed to nation-state actors.

### ARP (Address Resolution Protocol)
**Category:** Networking
A protocol that maps IP addresses to MAC (hardware) addresses on a local network.
ARP is stateless and trust-based — it has no authentication mechanism, which
makes ARP spoofing possible.

---

## B

### Botnet
**Category:** Malware
A network of compromised computers ("bots" or "zombies") controlled by an
attacker ("botmaster"). Used for DDoS attacks, spam distribution, credential
stuffing, and cryptocurrency mining.

### Buffer Overflow
**Category:** Exploitation
A condition where a program writes data beyond the allocated boundary of a
fixed-length buffer, overwriting adjacent memory. Exploitable to alter program
control flow — historically one of the most common vulnerability classes.

---

## C

### CA (Certificate Authority)
**Category:** Cryptography / PKI
A trusted entity that issues digital certificates. The CA verifies the identity
of the certificate requester and signs the certificate with its own private key.
Browsers and operating systems ship with a pre-installed set of trusted CAs.

### CIDR (Classless Inter-Domain Routing)
**Category:** Networking
A notation for IP address ranges: `192.168.1.0/24` means the first 24 bits are
the network prefix, leaving 8 bits for hosts (256 addresses). Replaced the old
Class A/B/C system.

### CORS (Cross-Origin Resource Sharing)
**Category:** Web Security
A mechanism that allows a web page to request resources from a different origin
(domain, protocol, or port) than its own. Relaxes the Same-Origin Policy in a
controlled way via HTTP headers.

### CSRF (Cross-Site Request Forgery)
**Category:** Web Security
An attack that forces an authenticated user to execute unwanted actions on a web
application. The attacker's page makes a request to the target site, and the
browser automatically includes the user's cookies.

### CVE (Common Vulnerabilities and Exposures)
**Category:** Vulnerability Management
A unique identifier for a publicly known security vulnerability. Format:
`CVE-YYYY-NNNNN`. Maintained by MITRE.

---

## D

### DDoS (Distributed Denial of Service)
**Category:** Network Attacks
An attack that overwhelms a target with traffic from many distributed sources
(botnets, amplification/reflection) to make it unavailable to legitimate users.

### DHCP (Dynamic Host Configuration Protocol)
**Category:** Networking
A protocol that automatically assigns IP addresses and network configuration
to devices. Uses the DORA process: Discover, Offer, Request, Acknowledge.

### DNS (Domain Name System)
**Category:** Networking
The "phone book" of the internet — translates human-readable domain names
(`example.com`) to IP addresses (`93.184.216.34`). Hierarchical, distributed,
and foundational to virtually all internet communication.

---

## E

### Exploit
**Category:** Exploitation
A piece of code, data, or a sequence of commands that takes advantage of a
vulnerability to cause unintended behavior in software or hardware.

---

## F

### Firewall
**Category:** Network Defense
A system that monitors and controls network traffic based on predetermined
security rules. Can be network-based (hardware appliance) or host-based (software
like iptables, nftables).

### Fuzzing (Fuzz Testing)
**Category:** Vulnerability Discovery
An automated testing technique that provides invalid, unexpected, or random data
as input to a program. The goal is to find crashes and bugs that indicate
vulnerabilities.

---

## H

### Hash Function
**Category:** Cryptography
A one-way mathematical function that maps data of arbitrary size to a fixed-size
output ("digest"). Properties: deterministic, quick to compute, infeasible to
reverse, and collision-resistant (two different inputs should not produce the
same hash).

### Honeypot
**Category:** Defensive Security
A decoy system designed to attract, detect, and analyze attackers. Appears
vulnerable and valuable but is isolated and heavily monitored.

---

## I

### IDS / IPS (Intrusion Detection/Prevention System)
**Category:** Defensive Security
- **IDS** — Monitors network traffic or host activity for suspicious behavior
  and generates alerts.
- **IPS** — Like an IDS but can also block detected threats in real time.

### IoC (Indicator of Compromise)
**Category:** Threat Intelligence
An artifact observed on a network or in an operating system that indicates a
computer intrusion with high confidence. Examples: known malicious IP addresses,
file hashes of malware, unusual registry changes.

---

## J

### JWT (JSON Web Token)
**Category:** Authentication
A compact, URL-safe token format used for representing claims between two parties.
Consists of three Base64-encoded parts: header, payload, and signature. Commonly
used for stateless authentication in web APIs.

---

## M

### MITM (Man-in-the-Middle Attack)
**Category:** Network Attacks
An attack where the attacker secretly relays and possibly alters communications
between two parties who believe they are communicating directly with each other.
Example: ARP spoofing to intercept traffic on a local network.

### MITRE ATT&CK
**Category:** Threat Intelligence
A globally accessible knowledge base of adversary tactics, techniques, and
procedures (TTPs) based on real-world observations. Used for threat modeling,
detection engineering, and red teaming.

---

## N

### NAT (Network Address Translation)
**Category:** Networking
A method of remapping one IP address space into another by modifying network
address information in packet headers. Allows multiple devices on a private
network to share a single public IP address.

---

## O

### OSINT (Open-Source Intelligence)
**Category:** Reconnaissance
Intelligence collected from publicly available sources: search engines, social
media, public records, DNS records, code repositories, etc.

### OWASP (Open Web Application Security Project)
**Category:** Web Security
A nonprofit foundation that produces freely available articles, methodologies,
documentation, tools, and technologies for web application security. Best known
for the OWASP Top 10 list of web application security risks.

---

## P

### Payload
**Category:** Exploitation
The component of an exploit or attack that performs the malicious action —
opening a shell, exfiltrating data, installing malware, etc.

### PKI (Public Key Infrastructure)
**Category:** Cryptography
The set of hardware, software, policies, and procedures needed to create, manage,
distribute, use, store, and revoke digital certificates. Built around the concept
of trust anchors (root CAs).

### Privilege Escalation
**Category:** System Security
Gaining higher access rights than originally granted. Vertical: user → root.
Horizontal: user A → user B. Often the second stage of an attack after initial access.

---

## R

### Ransomware
**Category:** Malware
Malware that encrypts the victim's files and demands payment (ransom) for the
decryption key. Modern variants also exfiltrate data and threaten to publish it.

### RCE (Remote Code Execution)
**Category:** Vulnerability Class
A vulnerability that allows an attacker to execute arbitrary code on a remote
system. Generally the most severe class of vulnerability.

### ROP (Return-Oriented Programming)
**Category:** Exploitation
A technique that chains together short sequences of existing code ("gadgets")
that each end with a `ret` instruction, allowing an attacker to execute arbitrary
computation despite NX/DEP protections.

---

## S

### Same-Origin Policy (SOP)
**Category:** Web Security
A fundamental browser security mechanism that restricts how a document or script
loaded from one origin can interact with resources from another origin. Defined
by scheme (protocol), host (domain), and port.

### SIEM (Security Information and Event Management)
**Category:** Defensive Security
A system that aggregates log data from many sources, correlates events, and
provides real-time analysis, alerting, and dashboards for security monitoring.

### SQL Injection (SQLi)
**Category:** Web Security
A code injection technique where SQL statements are inserted into application
input, allowing an attacker to read, modify, or delete database contents.

### SSL/TLS
**Category:** Cryptography
- **SSL** (Secure Sockets Layer) — Deprecated predecessor of TLS.
- **TLS** (Transport Layer Security) — Cryptographic protocol that provides
  secure communication over a network. TLS 1.3 is the current standard.

### Steganography
**Category:** Data Hiding
The practice of concealing a message, file, or data within another message,
file, or medium (e.g., hiding text in the least significant bits of an image).
Unlike cryptography, the goal is to hide the existence of the message itself.

---

## T

### TCP (Transmission Control Protocol)
**Category:** Networking
A connection-oriented, reliable transport protocol. Provides ordered, error-checked
delivery of data between applications. Uses a three-way handshake (SYN, SYN-ACK, ACK)
to establish connections.

### TTP (Tactics, Techniques, and Procedures)
**Category:** Threat Intelligence
A framework for describing how adversaries operate:
- **Tactics** — The "why" (goals: initial access, persistence, exfiltration)
- **Techniques** — The "how" (methods: spear phishing, pass-the-hash)
- **Procedures** — The specific implementation details

---

## U

### UDP (User Datagram Protocol)
**Category:** Networking
A connectionless transport protocol. No handshake, no guaranteed delivery, no
ordering — just fire and forget. Used where speed matters more than reliability
(DNS, streaming, VoIP).

---

## V

### VPN (Virtual Private Network)
**Category:** Networking
A technology that creates an encrypted tunnel between a device and a network,
protecting traffic from interception and masking the device's IP address.

### Vulnerability
**Category:** General
A weakness in a system, application, or process that can be exploited to violate
the system's security policy (confidentiality, integrity, or availability).

---

## W

### WAF (Web Application Firewall)
**Category:** Defensive Security
A firewall that monitors, filters, and blocks HTTP traffic to and from a web
application. Operates at Layer 7 (application layer) and can detect SQLi, XSS,
and other web attacks.

### WEP / WPA / WPA2 / WPA3
**Category:** Wireless Security
WiFi security protocol generations:
- **WEP** — Wired Equivalent Privacy (1999). Cryptographically broken, trivial to crack.
- **WPA** — WiFi Protected Access (2003). Interim fix using TKIP.
- **WPA2** — (2004). Uses AES-CCMP. Vulnerable to KRACK (key reinstallation attack).
- **WPA3** — (2018). Uses SAE (Simultaneous Authentication of Equals) handshake.

---

## X

### XSS (Cross-Site Scripting)
**Category:** Web Security
An injection attack where malicious scripts are injected into otherwise
trustworthy websites. Types: reflected (non-persistent), stored (persistent),
and DOM-based.

---

## Z

### Zero-Day
**Category:** Vulnerability Management
A vulnerability that is unknown to the vendor and for which no patch exists.
"Zero days" since the vendor has had zero days to fix it since discovery.

---

*Last updated: 2026-08-09*
*New terms are added as they appear in labs and experiments.*
