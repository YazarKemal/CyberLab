# LAB-003 Observations

- **Date:** 2026-08-09
- **Device:** Android tablet (Termux)
- **Inspector:** YazarKemal

---

## Environment

| Field | Value |
|-------|-------|
| Kernel | Linux 6.1.145-android14-11 |
| Architecture | aarch64 |
| Python | 3.14.6 |
| Platform | Android-16-aarch64-64bit |
| Hostname | localhost |
| User | u0_a47 |
| Lab scope | `127.0.0.1` only — no external DNS, no internet |

---

## Local Name Resolution

### AF_INET (IPv4)

**Command:** `getaddrinfo("localhost", None, AF_INET)`

| Result | Value |
|--------|-------|
| Addresses returned | 2 |
| Both addresses | `127.0.0.1` |
| Canonical name | `(none)` |
| Verdict | **VERIFIED** — localhost resolves to `127.0.0.1` via AF_INET |

### AF_INET6 (IPv6)

**Command:** `getaddrinfo("localhost", None, AF_INET6)`

| Result | Value |
|--------|-------|
| Outcome | **FAILED** |
| Error | `[Errno 7] No address associated with hostname` |
| Verdict | **VERIFIED** — `localhost` does NOT resolve to `::1` via AF_INET6 |

### Unspecified (all families)

**Command:** `getaddrinfo("localhost", None)`

| Result | Value |
|--------|-------|
| Addresses returned | 2 |
| Both | `127.0.0.1` (AF_INET) |
| IPv6 addresses | 0 |
| Verdict | **VERIFIED** — only IPv4 loopback addresses returned |

### gethostbyname_ex

**Command:** `gethostbyname_ex("localhost")`

| Result | Value |
|--------|-------|
| Hostname | `localhost` |
| Aliases | `[]` (none) |
| Addresses | `['127.0.0.1']` |
| Verdict | **VERIFIED** — consistent with getaddrinfo results |

### ::1 Direct Resolution

**Command:** `getaddrinfo("::1", None, AF_INET6)`

| Result | Value |
|--------|-------|
| Addresses returned | 2 |
| Both | `::1` |
| Verdict | **VERIFIED** — `::1` CAN be resolved directly. The failure above is specific to the name `localhost` over AF_INET6, not to IPv6 resolution in general. |

---

## /etc/hosts

**File contents (VERIFIED):**

```
127.0.0.1       localhost
::1             ip6-localhost
```

**Parsed mappings:**

| Name | Address | Family |
|------|---------|--------|
| `localhost` | `127.0.0.1` | IPv4 |
| `ip6-localhost` | `::1` | IPv6 |

### Key discrepancy (VERIFIED)

`/etc/hosts` maps `::1` to `ip6-localhost`, NOT to `localhost`.

This explains why:
- `getaddrinfo("localhost", AF_INET6)` → **FAILS**
- `getaddrinfo("::1", AF_INET6)` → **SUCCEEDS**
- `getaddrinfo("ip6-localhost", AF_INET6)` → would likely succeed (not tested)

The resolver follows `/etc/hosts` literally. There is no `::1 localhost` entry,
so `localhost` has no IPv6 address. This is a **configuration detail** of
Android/Termux, not a kernel or protocol limitation.

**Verdict:** VERIFIED — the discrepancy between IPv4 and IPv6 localhost
resolution is caused by the `/etc/hosts` file contents.

---

## DNS Header

**From our educational implementation (dns_message.py):**

| Field | Bytes | Offset | Description |
|-------|-------|--------|-------------|
| ID | 2 | 0 | Transaction identifier — correlates query with response |
| FLAGS | 2 | 2 | QR, Opcode, AA, TC, RD, RA, Z, RCODE |
| QDCOUNT | 2 | 4 | Number of questions (1 in our queries) |
| ANCOUNT | 2 | 6 | Number of answers (0 in query, 1 in response) |
| NSCOUNT | 2 | 8 | Number of authority RRs (0 in our implementation) |
| ARCOUNT | 2 | 10 | Number of additional RRs (0 in our implementation) |
| **Total** | **12** | — | Fixed header size |

**Packed with:** `struct.pack("!HHHHHH", ...)` — network byte order (big-endian).

---

## QNAME Encoding

### lab.local → wire format (VERIFIED)

```
Input:   lab.local

Labels:
  lab   = 3 bytes → 03 6c 61 62
  local = 5 bytes → 05 6c 6f 63 61 6c
  root  = 0 bytes → 00

Wire:   036c6162056c6f63616c00
        ^^        ^^          ^^
        |         |           root terminator
        |         label 2: "local" (5 bytes)
        label 1: "lab" (3 bytes)

Total: 11 bytes
```

**Verdict:** VERIFIED — `encode_qname("lab.local")` produces 11 bytes. Each label is prefixed by its length. The sequence ends with `00` (zero-length root label).

---

## Offline Packet Construction

### DNS query for lab.local A (VERIFIED)

| Property | Value |
|----------|-------|
| Transaction ID | `0xABCD` (43981) |
| Flags | `0x0100` (RD=1, standard query) |
| QDCOUNT | 1 |
| QNAME | `lab.local` (11 bytes) |
| QTYPE | `0x0001` (A) |
| QCLASS | `0x0001` (IN) |
| **Total packet length** | **27 bytes** (12 header + 15 question) |

### Full hexdump (VERIFIED)

```
0000  ab cd 01 00 00 01 00 00  00 00 00 00 03 6c 61 62   |.............lab|
0010  05 6c 6f 63 61 6c 00 00  01 00 01                  |.local.....|
```

### Byte-level annotation

| Offset | Bytes | Field |
|--------|-------|-------|
| 0x00 | `ab cd` | Transaction ID = 0xABCD |
| 0x02 | `01 00` | Flags = 0x0100 (RD=1) |
| 0x04 | `00 01` | QDCOUNT = 1 |
| 0x06 | `00 00` | ANCOUNT = 0 |
| 0x08 | `00 00` | NSCOUNT = 0 |
| 0x0A | `00 00` | ARCOUNT = 0 |
| 0x0C | `03 6c 61 62` | QNAME label 1: "lab" |
| 0x0F | `05 6c 6f 63 61 6c` | QNAME label 2: "local" |
| 0x15 | `00` | QNAME root terminator |
| 0x16 | `00 01` | QTYPE = 1 (A) |
| 0x18 | `00 01` | QCLASS = 1 (IN) |

**Self-verification:** Encoder/decoder round-trip: TXID, QNAME, QTYPE, QCLASS all match. ✓

---

## Local DNS Server

**Command:** `python src/dns_server.py --once`
**Binding:** `127.0.0.1:53535` (VERIFIED — NOT port 53)
**Socket type:** `AF_INET, SOCK_DGRAM` (UDP)
**Zone data served:**

| Name | Type | Value | TTL |
|------|------|-------|-----|
| `lab.local` | A | `127.0.0.42` | 300 |
| `lab.local` | AAAA | `::1` | 300 |

**No listen() or accept() calls** — UDP server, consistent with LAB-002 findings.

---

## A Query

### Experiment C — lab.local A (VERIFIED)

| Property | Value |
|----------|-------|
| **Client** | |
| Transaction ID (query) | `0xDA83` (55939) |
| Client ephemeral port | `58702` |
| Query packet length | **27 bytes** |
| Query before send | `getsockname()` = `0.0.0.0:0` |
| Query after send | `getsockname()` = `0.0.0.0:58702` |
| **Server** | |
| Server port | `53535` |
| Server received from | `127.0.0.1:58702` |
| Server decoded QNAME | `lab.local` |
| Server decoded QTYPE | A (1) |
| **Response** | |
| Transaction ID (response) | `0xDA83` |
| TXID match | **✓ VERIFIED** |
| Response packet length | **52 bytes** |
| Answer TTL | 300 seconds |
| Answer data | **`127.0.0.42`** |
| Flags | QR=1 (response), AA=1 (authoritative), RD=1, RA=0 |
| Response RCODE | 0 (NOERROR) |

### UDP endpoint pair (A query)

```
Client (127.0.0.1:58702)  →  Server (127.0.0.1:53535)
Client (127.0.0.1:58702)  ←  Server (127.0.0.1:53535)
```

### A response hexdump (VERIFIED)

```
0000  da 83 85 00 00 01 00 01  00 00 00 00 03 6c 61 62   |.............lab|
0010  05 6c 6f 63 61 6c 00 00  01 00 01 03 6c 61 62 05   |.local......lab.|
0020  6c 6f 63 61 6c 00 00 01  00 01 00 00 01 2c 00 04   |local........,..|
0030  7f 00 00 2a                                        |...*|
```

**Key bytes:**
- `da 83` — TXID (matches query)  
- `85 00` — Flags: QR=1, AA=1, RD=1  
- `00 01` — QDCOUNT=1  
- `00 01` — ANCOUNT=1  
- `00 00 01 2c` — TTL = 300  
- `00 04` — RDLENGTH = 4 (IPv4 address)  
- `7f 00 00 2a` — RDATA = `127.0.0.42`

---

## AAAA Query

### Experiment D — lab.local AAAA (VERIFIED)

| Property | Value |
|----------|-------|
| **Client** | |
| Transaction ID (query) | `0x27AC` (10156) |
| Client ephemeral port | `56355` |
| Query packet length | **27 bytes** |
| **Response** | |
| Transaction ID (response) | `0x27AC` |
| TXID match | **✓ VERIFIED** |
| Response packet length | **64 bytes** |
| Answer data | **`::1`** |
| Response RCODE | 0 (NOERROR) |

### Why AAAA response is larger than A response

| Field | A | AAAA | Difference |
|-------|---|------|------------|
| QTYPE in question | 1 | 28 | Same size (2 bytes) |
| RDATA length | 4 bytes | 16 bytes | +12 bytes |
| Total response | 52 bytes | 64 bytes | **+12 bytes** |

The only difference is the RDATA size: IPv4 address = 4 bytes, IPv6 address = 16 bytes.
The response is 12 bytes larger because of this, NOT because of any protocol difference.

### AAAA response hexdump (VERIFIED)

```
0000  27 ac 85 00 00 01 00 01  00 00 00 00 03 6c 61 62   |'............lab|
0010  05 6c 6f 63 61 6c 00 00  1c 00 01 03 6c 61 62 05   |.local......lab.|
0020  6c 6f 63 61 6c 00 00 1c  00 01 00 00 01 2c 00 10   |local........,..|
0030  00 00 00 00 00 00 00 00  00 00 00 00 00 00 00 01   |................|
```

**Key bytes:**
- `00 1c` — QTYPE = 28 (AAAA) in question  
- `00 10` — RDLENGTH = 16 (IPv6 address)  
- `00 ... 01` — RDATA = `::1` (15 zero bytes + 0x01)

---

## Transaction IDs

### All observed transaction IDs

| Query | TXID (hex) | TXID (dec) | Type | Response TXID | Match? |
|-------|-----------|------------|------|---------------|--------|
| A (experiment C) | `0xDA83` | 55939 | A | `0xDA83` | ✓ VERIFIED |
| AAAA (experiment D) | `0x27AC` | 10156 | AAAA | `0x27AC` | ✓ VERIFIED |
| A (experiment E, run 3) | `0x5C0B` | 23563 | A | `0x5C0B` | ✓ VERIFIED |

Additional queries from experiment E server logs:
- Query to `127.0.0.1:42934` — served, response sent
- Query to `127.0.0.1:35668` — served, response sent
- Query to `127.0.0.1:54667` — served, response sent

**Observations:**
- Every query had a **different** transaction ID. (VERIFIED)
- Every response TXID **matched** its query TXID. (VERIFIED)
- TXIDs came from `random.randint(0, 65535)` in `dns_client.py`.
- The server echoes the TXID — it does NOT generate its own. (VERIFIED from `dns_server.py` source: `txid=q_header["txid"]`).

**Security note (educational):** Matching transaction IDs allow a DNS client to
correlate responses with queries and reject stale or misdirected replies. However,
16-bit TXIDs provide only 65536 possible values — a motivated attacker on the
same network could attempt to guess them. DNS over HTTPS (DoH) and DNS over TLS
(DoT) address this and other security limitations. Our educational implementation
does NOT provide production-level DNS security.

---

## UDP Endpoint Pairs

| Experiment | Client Endpoint | Server Endpoint | Query Size | Response Size |
|------------|----------------|-----------------|------------|---------------|
| A query (C) | `127.0.0.1:58702` | `127.0.0.1:53535` | 27 bytes | 52 bytes |
| AAAA query (D) | `127.0.0.1:56355` | `127.0.0.1:53535` | 27 bytes | 64 bytes |
| A query (E, run 3) | `127.0.0.1:41800` | `127.0.0.1:53535` | 27 bytes | 52 bytes |

**Observed:**
- Server port is constant (`53535`) — `bind()` fixed it. (VERIFIED)
- Client port changes each time — OS-assigned ephemeral port. (VERIFIED, consistent with LAB-002)
- Query size is always 27 bytes — same QNAME, same QTYPE size. (VERIFIED)
- Response size depends on answer RDATA: 52 (A, 4-byte IPv4) vs 64 (AAAA, 16-byte IPv6). (VERIFIED)

---

## Packet Hexdump Summary

### DNS Query (always 27 bytes for lab.local)

```
XXXX  TT TT 01 00 00 01 00 00  00 00 00 00 03 6c 61 62
0010  05 6c 6f 63 61 6c 00  QQ  QQ 00 01
```
- `TT TT` = Transaction ID (2 bytes, varies per query)
- `QQ QQ` = QTYPE: `00 01` (A) or `00 1c` (AAAA)

### DNS Response — A (52 bytes)

Header (12) + Question (15) + Answer (25: QNAME 11 + TYPE 2 + CLASS 2 + TTL 4 + RDLENGTH 2 + RDATA 4)

### DNS Response — AAAA (64 bytes)

Header (12) + Question (15) + Answer (37: QNAME 11 + TYPE 2 + CLASS 2 + TTL 4 + RDLENGTH 2 + RDATA 16)

---

## Android / Termux Limitations

| Limitation | Impact | Type |
|------------|--------|------|
| `getaddrinfo("localhost", AF_INET6)` fails | IPv6 localhost resolution unavailable by that name | CONFIGURATION — `/etc/hosts` maps `::1` to `ip6-localhost` only |
| `::1` direct resolution works | IPv6 loopback is functional, just not named `localhost` | VERIFIED |
| Port 53 requires root | Server uses port `53535` instead | ANDROID SECURITY — standard Unix restriction |
| No `/etc/resolv.conf` (LAB-001 finding) | Cannot inspect system DNS configuration | ANDROID SANDBOX |
| No external DNS | All queries are to our own `127.0.0.1:53535` server | LAB DESIGN — intentional |

---

## Unexpected Results

### 1. Bonus section in dns_packet_demo.py showed incorrect QTYPE bytes

**Observation:** The "Bonus" AAAA comparison in `dns_packet_demo.py` showed QTYPE bytes as `0001` for both A and AAAA queries. This is a display bug in the demo script (wrong offset calculation), NOT an encoding bug in `dns_message.py`. The actual server correctly decoded the AAAA query (QTYPE 28 = `0x001c`), confirming the wire format was correct.

**Verdict:** The dns_message library encodes correctly. The demo's comparison section has a cosmetic off-by-one in its offset calculation. Not fixed for this lab — noted as an observation.

### 2. Background server orchestration worked reliably with --once

**Observation:** Using `--once` mode with background processes (`&`) and `wait` worked cleanly for all experiments. No residual processes. Each server handled exactly one query and exited.

---

## Theory vs. Observation

| Theoretical Claim | Observation | Match? |
|-------------------|-------------|--------|
| DNS QNAME uses [len][label]...[len][label]\x00 encoding | `lab.local` → `036c6162056c6f63616c00` | ✓ VERIFIED |
| DNS header is 12 bytes, big-endian | `struct.pack("!HHHHHH", ...)` produces 12 correct bytes | ✓ VERIFIED |
| Transaction ID correlates query with response | All 3 observed TXIDs matched between query and response | ✓ VERIFIED |
| DNS uses UDP (SOCK_DGRAM) | Server uses `recvfrom()`/`sendto()`, no `listen()`/`accept()` | ✓ VERIFIED |
| A record returns 4-byte IPv4 address | Response RDATA = `7f 00 00 2a` = `127.0.0.42` | ✓ VERIFIED |
| AAAA record returns 16-byte IPv6 address | Response RDATA = 15 zero bytes + `01` = `::1` | ✓ VERIFIED |
| DNS response echoes the question section | All response hexdumps contain the original QNAME and QTYPE | ✓ VERIFIED |
| TTL is a 4-byte field in the answer | Observed TTL = `00 00 01 2c` = 300 | ✓ VERIFIED |
| `localhost` resolves to `127.0.0.1` via /etc/hosts | `getaddrinfo` returned `127.0.0.1` | ✓ VERIFIED |
| `::1` resolution works when addressed directly | `getaddrinfo("::1", AF_INET6)` returned `::1` | ✓ VERIFIED |
| DNS response is larger for AAAA than A | 52 vs 64 bytes, exactly +12 (16 − 4 for RDATA) | ✓ VERIFIED |
| Query packet size is independent of QTYPE | Both A and AAAA queries were 27 bytes | ✓ VERIFIED |

---

## Conclusion

### What was experimentally demonstrated

1. **Name resolution on this device** — `localhost` resolves to `127.0.0.1` (IPv4 only). IPv6 loopback (`::1`) is functional but mapped to `ip6-localhost`, not `localhost`, in `/etc/hosts`. (VERIFIED)

2. **DNS wire format** — We encoded and decoded DNS headers, QNAME labels, questions, and answers entirely in Python using `struct` and manual byte construction. The encoder/decoder round-trips correctly. (VERIFIED)

3. **QNAME encoding** — `lab.local` becomes 11 bytes on the wire: `03 6c 61 62 05 6c 6f 63 61 6c 00`. Each label is prefixed by its byte length. (VERIFIED)

4. **Transaction IDs** — The client generates a random 16-bit TXID. The server copies it into the response. The client verifies the match. This is DNS's mechanism for correlating replies with queries. (VERIFIED)

5. **A and AAAA queries** — Both use the same 27-byte query format (only the QTYPE field differs: `0x0001` vs `0x001c`). Responses differ by exactly 12 bytes (IPv4 = 4 bytes RDATA, IPv6 = 16 bytes RDATA). (VERIFIED)

6. **UDP for DNS** — Our server used `SOCK_DGRAM` with `recvfrom()`/`sendto()`. No `listen()`, no `accept()`, no persistent connection. Each query is a single datagram exchange. (VERIFIED, consistent with LAB-002 UDP findings)

7. **This is not a production DNS server** — Our implementation handles exactly two names (`lab.local` A and AAAA), has no recursion, no caching, no compression, no EDNS0, and no security. It is purely educational. (BY DESIGN)

### What was inferred (not directly observed)

- The kernel routes UDP datagrams to the correct process based on port number. (INFERRED from socket API behavior — consistent with LAB-002 UDP findings.)

### What could not be verified

- Actual external DNS resolution (blocked by lab scope — no internet).
- DNS over TCP (port 53/tcp) — our server only implements UDP.
- Name compression in responses (we use uncompressed names — easier to read and implement).
- Real DNS server behavior (caching, recursion, zone transfers).

---

## Cleanup Verification

| Process | Cleanup Method | Status |
|---------|---------------|--------|
| dns_server.py (all instances) | `--once` mode — auto-exits after one query | PASS |
| Residual Python processes | `pgrep -la python` returns exit code 1 | PASS |
| Sockets in TIME_WAIT | N/A — UDP has no TIME_WAIT | N/A |

**Server cleanup:** PASS — no residual processes.
