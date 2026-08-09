# LAB-003: DNS Name Resolution

- **Phase:** 02 — Network Fundamentals
- **Date:** 2026-08-09
- **Environment:** Android tablet, Termux, Python 3.x (standard library only)
- **Scope:** localhost only (`127.0.0.1`, `::1`)
- **Status:** Complete

---

## 1. Theory

### Why DNS exists

Computers route packets using IP addresses (e.g., `93.184.216.34`). Humans
remember names (e.g., `example.com`). The **Domain Name System (DNS)** bridges
these two worlds — it translates human-readable domain names into
machine-routable IP addresses.

DNS is:
- **Hierarchical** — organized as a tree from root (`.`) through TLDs (`.com`,
  `.org`) to individual domains.
- **Distributed** — no single server holds the entire database. Authority is
  delegated down the tree.
- **Cached** — resolvers cache answers to reduce load and latency.

### The name resolution process

```
Application
    |
    | "what is the IP for example.com?"
    v
Resolver (getaddrinfo / gethostbyname)
    |
    +---- /etc/hosts  (checked FIRST — static local mappings)
    |
    +---- DNS          (queried if hosts doesn't have the answer)
    |
    v
IP address (93.184.216.34)
```

On Linux, the order is controlled by `/etc/nsswitch.conf` (`hosts: files dns`
means check files first, then DNS). Android uses a simplified resolver.

### /etc/hosts vs. DNS

| | `/etc/hosts` | DNS |
|---|---|---|
| Where | Local file on the device | Network service |
| Speed | Instant (no network) | Requires UDP round-trip |
| Authority | Local admin | Delegated through DNS hierarchy |
| Updates | Manual editing | Dynamic, propagated |
| Use case | Loopback, dev overrides, small networks | Internet-scale name resolution |

`/etc/hosts` is checked FIRST. If a name is found there, DNS is never queried.
This is why `localhost` always resolves to `127.0.0.1` without any DNS server.

### DNS Protocol Overview

DNS primarily uses **UDP** on port 53. Why UDP?

1. **Low overhead** — no handshake, no connection state. A query is a single
   datagram exchange (request → response).
2. **Speed** — DNS is in the critical path of every connection. TCP's handshake
   would add latency to every DNS lookup.
3. **Stateless** — a DNS server can handle thousands of queries per second
   without maintaining per-client state.

DNS **can** also use TCP on port 53 for:
- Responses larger than 512 bytes (truncation).
- Zone transfers (AXFR) between DNS servers.

### DNS roles (conceptual)

| Role | Description |
|------|-------------|
| **Resolver** | The client-side library (e.g., `getaddrinfo()`) that applications call. It may consult `/etc/hosts`, a local cache, and DNS servers. |
| **Recursive resolver** | A DNS server that does the work of chasing the delegation chain for you (e.g., your ISP's DNS, `8.8.8.8`). |
| **Authoritative server** | A DNS server that holds the definitive records for a domain. It answers from its own data, not from cache. |

Our lab builds a tiny **authoritative server** for the educational zone
`lab.local`.

### Key Record Types

| Type | Value | Description |
|------|-------|-------------|
| **A** | 1 | IPv4 address — 4 bytes. `example.com A → 93.184.216.34` |
| **AAAA** | 28 | IPv6 address — 16 bytes. `example.com AAAA → 2606:2800:220:1:248:1893:25c8:1946` |
| NS | 2 | Nameserver — delegates authority |
| CNAME | 5 | Canonical name — alias |
| MX | 15 | Mail exchanger |

### DNS Message Format

```
+------------------+
| Header           | 12 bytes — ID, flags, counts
+------------------+
| Question         | QNAME + QTYPE + QCLASS
+------------------+
| Answer           | Resource Records answering the question
+------------------+
| Authority        | RRs pointing to authoritative servers
+------------------+
| Additional       | RRs holding related data (e.g., A for NS names)
+------------------+
```

Our educational implementation only handles Header + Question + Answer for
A and AAAA record types.

### DNS Header (12 bytes)

```
 0  1  2  3  4  5  6  7  8  9 10 11 12 13 14 15
+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
|                   ID                            |
+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
|QR| Opcode  |AA|TC|RD|RA| Z  |    RCODE        |
+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
|                  QDCOUNT                         |
+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
|                  ANCOUNT                         |
+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
|                  NSCOUNT                         |
+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
|                  ARCOUNT                         |
+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
```

| Flag | Bit | Meaning |
|------|-----|---------|
| QR | 15 | 0 = Query, 1 = Response |
| AA | 10 | Authoritative Answer |
| RD | 8 | Recursion Desired (client asks server to recurse) |
| RA | 7 | Recursion Available (server says it can recurse) |
| RCODE | 3–0 | Response code: 0=NOERROR, 3=NXDOMAIN |

### QNAME Encoding (DNS Labels)

Domain names are NOT sent as plain text on the wire. Instead, each label is
prefixed by its byte length, and the sequence ends with `00` (root):

```
"lab.local"
    ↓
03 6c 61 62     ← 3 bytes: "lab"
05 6c 6f 63 61 6c ← 5 bytes: "local"
00              ← root terminator
```

This encoding:
- Avoids delimiters (no "." on the wire).
- Supports arbitrary binary labels (though uncommon).
- Limits labels to 63 bytes (length fits in 6 bits; top 2 bits used for compression pointers).

### Transaction ID

Every DNS query includes a 16-bit **transaction ID** chosen by the client.
The server copies it into the response. The client uses it to:
1. Match responses to outstanding queries.
2. Reject stale or spoofed replies with wrong TXIDs.

This is DNS's basic integrity mechanism — but 16 bits (65536 values) is not
cryptographically strong. Modern DNS security uses DNSSEC for authentication
and DoH/DoT for transport encryption.

### DNS Query/Response Flow

```
Client (127.0.0.1:random)          Server (127.0.0.1:53535)
----------------------------       -------------------------
socket(SOCK_DGRAM)                 socket(SOCK_DGRAM)
                                   bind(53535)

Transaction ID = 0xABCD
QNAME = lab.local
QTYPE = A
QCLASS = IN

sendto() ---- 27 bytes ---------->
                                   recvfrom()
                                   decode: TXID=0xABCD
                                           QNAME=lab.local
                                           QTYPE=A
                                   lookup: lab.local A → 127.0.0.42
                                   encode response

          <--- 52 bytes ---------- sendto()
recvfrom()
TXID check: 0xABCD == 0xABCD ✓
ANSWER = 127.0.0.42
TTL = 300
```

### Network Byte Order

DNS uses **big-endian** (network byte order) for all multi-byte integers.
In Python, `struct.pack("!H", 1)` produces `00 01` — the `!` prefix means
"network byte order." This is critical: if the client and server used
different byte orders, the transaction ID and counts would be garbled.

---

## 2. Terminology

| Term | Definition |
|------|------------|
| **Hostname** | A human-readable name for a device (e.g., `localhost`, `webserver`). |
| **Domain name** | A hierarchical name in the DNS tree (e.g., `example.com`, `lab.local`). |
| **Resolver** | The client-side library that translates names to addresses. |
| **DNS server** | A program that answers DNS queries from its zone data or via recursion. |
| **DNS query** | A UDP datagram containing a header + question section. |
| **DNS response** | A UDP datagram containing a header + question + answer section. |
| **Recursive resolver** | A DNS server that follows the delegation chain on behalf of clients. |
| **Authoritative server** | A DNS server that holds the official records for a zone. |
| **A record** | Maps a domain name to an IPv4 address (4 bytes). QTYPE = 1. |
| **AAAA record** | Maps a domain name to an IPv6 address (16 bytes). QTYPE = 28. |
| **QNAME** | The domain name being queried, in DNS label encoding. |
| **QTYPE** | The type of record being requested (1=A, 28=AAAA, etc.). |
| **QCLASS** | The class of the query — almost always IN (Internet, value 1). |
| **TTL** | Time To Live — how long (in seconds) a record may be cached before re-querying. |
| **Transaction ID** | A 16-bit random value that correlates a DNS response with its query. |
| **DNS flags** | A 16-bit field encoding QR, AA, RD, RA, and RCODE. |
| **QDCOUNT** | Number of entries in the question section (usually 1). |
| **ANCOUNT** | Number of entries in the answer section. |
| **Network byte order** | Big-endian — the standard byte order for network protocols. |
| **DNS label encoding** | [length_byte][label_bytes]... with `00` root terminator. |
| **/etc/hosts** | A local file checked BEFORE DNS for name→address mappings. |
| **getaddrinfo()** | The standard socket API function for name resolution. |
| **UDP port 53** | The standard port for DNS queries. Requires root to bind. |
| **UDP port 53535** | Our educational port — avoids the root requirement. |

---

## 3. Experiments

### Experiment A — Local Name Resolution

```bash
python src/local_resolution.py
```

Investigates how `localhost` resolves on THIS device using only `/etc/hosts`
and the standard resolver API. No external DNS.

### Experiment B — Offline DNS Packet Construction

```bash
python src/dns_packet_demo.py
```

Builds a complete DNS query for `lab.local A` entirely offline. Shows every
byte with annotations. Demonstrates QNAME encoding and header construction.

### Experiment C — DNS A Query

**Session 1:**
```bash
python src/dns_server.py --once --debug
```

**Session 2:**
```bash
python src/dns_client.py lab.local A
```

Queries our educational server at `127.0.0.1:53535` for the A record of
`lab.local`. Expected: `127.0.0.42`.

### Experiment D — DNS AAAA Query

```bash
python src/dns_server.py --once --debug    # Session 1
python src/dns_client.py lab.local AAAA    # Session 2
```

Expected: `::1`.

### Experiment E — Transaction IDs

Run multiple queries and observe that each gets a different random TXID,
and each response matches its corresponding query's TXID.

---

## 4. DNS Message Structure (Implemented Subset)

```
DNS Query (27 bytes for lab.local):
┌─────────────────────┐
│ Header (12 bytes)   │  ID, FLAGS, QDCOUNT=1, ANCOUNT=0, NSCOUNT=0, ARCOUNT=0
├─────────────────────┤
│ Question (15 bytes) │  QNAME (11) + QTYPE (2) + QCLASS (2)
└─────────────────────┘

DNS Response — A (52 bytes):
┌─────────────────────┐
│ Header (12 bytes)   │  ID, FLAGS (QR=1,AA=1), QDCOUNT=1, ANCOUNT=1
├─────────────────────┤
│ Question (15 bytes) │  QNAME (11) + QTYPE (2) + QCLASS (2)  [echoed]
├─────────────────────┤
│ Answer (25 bytes)   │  NAME (11) + TYPE (2) + CLASS (2) + TTL (4)
│                     │  + RDLENGTH (2) + RDATA (4)
└─────────────────────┘

DNS Response — AAAA (64 bytes):
Same structure as A response but RDATA is 16 bytes instead of 4.
```

---

## 5. Source Files

| File | Purpose |
|------|---------|
| `dns_message.py` | Educational DNS encoder/decoder — header, QNAME, questions, answers, hexdumps |
| `local_resolution.py` | Investigate localhost resolution via getaddrinfo and /etc/hosts |
| `dns_server.py` | Minimal authoritative server for `lab.local` on `127.0.0.1:53535` |
| `dns_client.py` | DNS client that builds queries, sends via UDP, parses responses |
| `dns_packet_demo.py` | Offline packet construction with byte-level annotation |

---

## 6. Android / Termux Notes

- All experiments use `127.0.0.1` — no external DNS servers.
- Port 53 is privileged — our server uses port `53535` instead.
- `/etc/hosts` maps `::1` to `ip6-localhost`, not `localhost` — this is why
  `getaddrinfo("localhost", AF_INET6)` fails while `::1` still works directly.
- UDP is available without root — our DNS server works fine on the high port.

---

## 7. Observation

Record your observations in `observations.md`. The file contains the actual
results from executing all five experiments on this device.

---

## 8. Conclusion

After completing this lab, you should be able to:

1. **Explain how DNS translates names to IP addresses** — including the roles
   of `/etc/hosts`, resolvers, and DNS servers.
2. **Read and write DNS wire format** — encode and decode headers, QNAME labels,
   questions, and answer records by hand.
3. **Build a working DNS client and server** — using only Python `struct` and
   UDP sockets.
4. **Explain transaction IDs** — why they exist, how they work, and their
   security limitations.
5. **Distinguish A from AAAA records** — and understand why AAAA responses are
   12 bytes larger.
6. **Understand QNAME encoding** — and why domain names are length-prefixed on
   the wire rather than dot-separated.
7. **Recognize that our implementation is educational** — it is NOT a production
   DNS server and lacks recursion, caching, compression, DNSSEC, and many other
   features of real DNS implementations.

---

## 9. Exercises

> These are for self-assessment. Determine the answers by running the experiments
> and inspecting the code — not by looking them up.

1. What is the difference between a hostname and an IP address? Why do we need
   both? What would happen if we only had IP addresses and no names?

2. What role does `/etc/hosts` play in name resolution? Why is it checked before
   DNS? Give a practical scenario where you would edit this file.

3. What does `getaddrinfo()` do? What arguments does it take and what does it
   return? Why does it support multiple address families?

4. Why does DNS use transaction IDs? What would happen if a DNS client received
   a response with the wrong transaction ID? Why are 16-bit TXIDs not considered
   cryptographically secure?

5. What is QNAME? How is `lab.local` represented in DNS wire format? Why are
   labels length-prefixed rather than using dots as separators?

6. What is QTYPE 1? How many bytes of RDATA does an A record response contain?
   How is `127.0.0.42` represented in those bytes?

7. What is QTYPE 28? Why does an AAAA response contain 12 more bytes than an A
   response? Is the query size different?

8. What does QCLASS IN mean? What other classes exist (conceptually), and why is
   IN the only one you will encounter in practice?

9. What is TTL? Why do DNS records have a TTL? What happens when the TTL expires?
   What value did our educational server use and why?

10. Why did our server use UDP instead of TCP? What are the tradeoffs? Under
    what circumstances does DNS use TCP?

11. Why did we use port 53535 instead of port 53? What would happen if we tried
    to bind to port 53 in Termux without root?

12. Why must the response transaction ID match the query? Where in the server
    code is the TXID copied? What would happen if the server generated a new
    random TXID for each response?

13. What information in our DNS packet travels as raw bytes rather than text?
    How does the receiver know where the QNAME ends and the QTYPE begins?

14. Why is our implementation not a production DNS server? List at least five
    features that a real DNS server has that ours does not.

15. On this Android/Termux device, `getaddrinfo("localhost", AF_INET6)` fails
    but `getaddrinfo("::1", AF_INET6)` succeeds. Explain exactly why, using
    the evidence from `/etc/hosts`.

---

## References

- RFC 1035 — Domain Names — Implementation and Specification
- RFC 3596 — DNS Extensions to Support IP Version 6 (AAAA records)
- RFC 6891 — Extension Mechanisms for DNS (EDNS0)
- `man 3 getaddrinfo` — Linux resolver API
- `man 5 hosts` — /etc/hosts file format
- `man 5 resolv.conf` — Resolver configuration
