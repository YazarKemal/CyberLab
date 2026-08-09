# LAB-002 Observations

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
| Lab directory | `02-network-fundamentals/lab-002-tcp-udp-ports-sockets/` |
| Network scope | `127.0.0.1` only — no LAN, no internet, no remote hosts |

---

## TCP Server

**Command:** `python src/tcp_server.py`

**Status:** STARTED SUCCESSFULLY
**PID:** 4170 (VERIFIED)

**Output (startup):**
```
TCP Server listening on 127.0.0.1:8080
Backlog: 5
Waiting for connections... (Ctrl+C to stop)
```

**Binding:** `127.0.0.1:8080` (VERIFIED — port 8080 on loopback interface only)

**Socket options:** `SO_REUSEADDR` enabled (VERIFIED — allows rapid restart without "Address already in use" errors)

**Server lifecycle observed:**
```
socket() → bind(127.0.0.1, 8080) → listen(5) → accept() [blocked]
```

---

## Open Port Test

**Command:** `python src/port_check.py 8080`

**Server state:** tcp_server.py RUNNING (PID 4170)

**Result:**
```
Port 8080: OPEN

A TCP three-way handshake completed successfully.
This means a process is LISTENING on 127.0.0.1:8080.

Our connection details:
  Local:  127.0.0.1:39772
  Remote: 127.0.0.1:8080
```

**Verdict:** VERIFIED — Port 8080 is OPEN while tcp_server.py is running.

**What happened at the kernel level:**
1. `port_check.py` called `connect(127.0.0.1, 8080)`.
2. Kernel sent SYN to `127.0.0.1:8080`.
3. Kernel found tcp_server.py (PID 4170) in LISTEN state on port 8080.
4. Kernel completed the three-way handshake (SYN → SYN-ACK → ACK) on behalf of the server.
5. `connect()` returned successfully — port is OPEN.
6. Our ephemeral source port was `39772` (OS-assigned).

---

## Closed Port Test

**Command:** `python src/port_check.py 8081`

**Server state:** No process listening on port 8081 (VERIFIED — only tcp_server.py on 8080 was running)

**Result:**
```
Port 8081: CLOSED

The kernel responded with RST (reset).
No process is listening on 127.0.0.1:8081.

What happened at the protocol level:
  1. We sent SYN to 127.0.0.1:8081
  2. The kernel checked: is anyone listening on port 8081?
  3. Answer: NO → kernel sent RST back to us.
  4. Our connect() raised ConnectionRefusedError.
```

**Verdict:** VERIFIED — `ConnectionRefusedError` was raised. Port 8081 is CLOSED. No process has called `bind()` + `listen()` on this port.

**Key insight:** The `ConnectionRefusedError` is VERIFIED — we observed it directly. The mechanism (kernel sends TCP RST in response to SYN on a closed port) is INFERRED from normal TCP/kernel behavior. We did NOT capture packets to confirm the RST on the wire. On loopback, the kernel may optimize the rejection without sending an actual RST packet.

---

## TCP Client

**Command:** `python src/tcp_client.py` (run 3 times)

**Status:** ALL THREE CONNECTIONS SUCCEEDED

### Connection 1

```
Connecting to 127.0.0.1:8080...
Connected!
  My local address (getsockname):  127.0.0.1:32822
  Server address  (getpeername):  127.0.0.1:8080

TCP four-tuple for this connection:
  (127.0.0.1:32822)  ↔  (127.0.0.1:8080)
   ^-- source (ephemeral)        ^-- destination (server)

Sending: Hello from TCP client!
Server response: Hello from TCP server! You said: Hello from TCP client!
```

### Connection 2

```
  My local address (getsockname):  127.0.0.1:32828
  Server address  (getpeername):  127.0.0.1:8080
  (127.0.0.1:32828)  ↔  (127.0.0.1:8080)
Server response: Hello from TCP server! You said: Hello from TCP client!
```

### Connection 3

```
  My local address (getsockname):  127.0.0.1:32832
  Server address  (getpeername):  127.0.0.1:8080
  (127.0.0.1:32832)  ↔  (127.0.0.1:8080)
Server response: Hello from TCP server! You said: Hello from TCP client!
```

---

## TCP Endpoint Pair

VERIFIED four-tuple for the first connection:

```
(127.0.0.1:32822)  ↔  (127.0.0.1:8080)
```

| Field | Value | Source |
|-------|-------|--------|
| Client IP | `127.0.0.1` | `getsockname()` |
| Client port (ephemeral) | `32822` | `getsockname()` — OS-assigned |
| Server IP | `127.0.0.1` | `getpeername()` |
| Server port (well-known) | `8080` | `getpeername()` — we specified this |

Both endpoints are on the loopback interface. No packets left the device.

---

## Ephemeral Port Experiment

Three consecutive TCP connections to `127.0.0.1:8080`. The OS assigned a
different ephemeral source port to each:

| Connection | Ephemeral Source Port | OS-Assigned? |
|------------|----------------------|--------------|
| 1 | `32822` | Yes — `getsockname()` confirmed |
| 2 | `32828` | Yes |
| 3 | `32832` | Yes |

**Observations:**
- Each connection received a **different** source port. (VERIFIED)
- Ports were **not strictly sequential** (32822 → 32828 → 32832, gaps of +6
  and +4). This is VERIFIED from the recorded values.
- Ephemeral port allocation is controlled by the operating system and is
  **not required to be sequential.** The exact cause of the specific gaps
  observed was NOT VERIFIED. Other socket activity (such as the `port_check.py`
  connection that used ephemeral port `39772`) may influence allocation, but
  we did not trace kernel port assignment.
- All three ports are in the Linux ephemeral range (typically 32768–60999).
- This demonstrates why a single host can have thousands of simultaneous TCP
  connections — each is uniquely identified by a different source port.

**Separate experiment — port_check.py ephemeral port:**
The `port_check.py` connection (Open Port Test, above) used ephemeral source
port **`39772`** to connect to `127.0.0.1:8080`. This was a separate TCP
connection from the three `tcp_client.py` connections. Each call to `connect()`
— whether from `tcp_client.py` or `port_check.py` — receives its own ephemeral
port from the OS.

**Verdict:** VERIFIED — the OS assigns a fresh ephemeral port for each `connect()` call when the socket has not been explicitly bound.

---

## Server Shutdown Experiment

### Before shutdown (server PID 4170 running)

| Port | Status | Verdict |
|------|--------|---------|
| `8080` | OPEN | VERIFIED — `connect()` succeeded, handshake completed |

### After shutdown (PID 4170 terminated via `kill 4170`)

**Command:** `kill 4170` (exact PID, no killall/pkgill)

**Termination:** CONFIRMED — PID 4170 no longer exists

| Port | Status | Verdict |
|------|--------|---------|
| `8080` | CLOSED | VERIFIED — `connect()` raised `ConnectionRefusedError` |

```
Port 8080: CLOSED

The kernel responded with RST (reset).
No process is listening on 127.0.0.1:8080.
```

**Key insight:** A port is OPEN **only while a process is alive and has called `listen()` on it.** The moment the process exits, the kernel cleans up all its sockets. The port transitions from LISTEN to CLOSED automatically. There is no persistent "open port" — ports are owned by running processes.

### Summary

```
Server RUNNING:  127.0.0.1:8080 → OPEN   (VERIFIED)
Server STOPPED:  127.0.0.1:8080 → CLOSED (VERIFIED)
```

---

## UDP Experiment

### Server

**Command:** `python src/udp_server.py`
**PID:** 7876 (VERIFIED)
**Binding:** `127.0.0.1:9090`

**Server code confirmed (from source):**
- `socket(AF_INET, SOCK_DGRAM)` — creates UDP socket ✓
- `bind(127.0.0.1, 9090)` — claims the port ✓
- `recvfrom(1024)` — receives datagram + sender address ✓
- `sendto(response, client_addr)` — replies to sender ✓
- **No** `listen()` call — NOT PRESENT ✓
- **No** `accept()` call — NOT PRESENT ✓
- One socket handles ALL clients (no per-client socket) ✓

### Client

**Command:** `python src/udp_client.py`

**Result (VERIFIED):**
```
Before sendto — getsockname(): 0.0.0.0:0
  (No port assigned yet — OS assigns an ephemeral port on first send)

Sending datagram to 127.0.0.1:9090...
After sendto — getsockname(): 0.0.0.0:58462
  (OS assigned ephemeral port 58462)

Waiting for reply...
Received reply from 127.0.0.1:9090
  Message: Hello from UDP server! You said: Hello from UDP client!

NOTE: Unlike TCP, there is no persistent connection.
      Each sendto()/recvfrom() is an independent datagram.
      The server does not 'remember' us between datagrams.
```

### UDP Endpoint Pair (single datagram exchange)

```
Client (127.0.0.1:58462)  ──datagram──→  Server (127.0.0.1:9090)
Client (127.0.0.1:58462)  ←─datagram──  Server (127.0.0.1:9090)
```

| Field | Value | Source |
|-------|-------|--------|
| Client IP | `127.0.0.1` | Server `recvfrom()` return |
| Client port (ephemeral) | `58462` | Server `recvfrom()` return; client `getsockname()` after `sendto()` |
| Server IP | `127.0.0.1` | Client `recvfrom()` return |
| Server port | `9090` | Client specified in `sendto()` |

**Key difference from TCP:**
- Before `sendto()`, `getsockname()` returned `0.0.0.0:0` — no port assigned.
- After `sendto()`, the OS assigned ephemeral port `58462`.
- In TCP, `connect()` triggers port assignment + the three-way handshake simultaneously.
- In UDP, the first `sendto()` triggers port assignment. No handshake occurs.

### UDP Server Cleanup

**PID 7876 terminated:** VERIFIED — no Python processes remain.

---

## Socket Demo

**Command:** `python src/socket_demo.py`

### Address Families (VERIFIED)

| Constant | Value | Socket Creation |
|----------|-------|-----------------|
| `AF_INET` | `2` | ✓ Available |
| `AF_INET6` | `10` | ✓ Available |
| `AF_UNIX` | `1` | (not tested with socket creation, demonstrated by import) |

### Socket Types (VERIFIED)

| Constant | Value | Socket Creation |
|----------|-------|-----------------|
| `SOCK_STREAM` | `1` | ✓ Available (TCP) |
| `SOCK_DGRAM` | `2` | ✓ Available (UDP) |
| `SOCK_RAW` | `3` | Not tested (requires root) |

### IPv6 Status (VERIFIED)

| Test | Result |
|------|--------|
| IPv6 socket creation | ✓ AVAILABLE — `socket(AF_INET6, SOCK_STREAM)` succeeded |
| `::1` resolution | ✓ `getaddrinfo("::1", ...)` returned `['::1']` |
| `localhost` resolution (IPv6) | ✗ FAILED — `[Errno 7] No address associated with hostname` |
| Bind to `::1` | ✓ SUCCESS — bound to `::1:34997` |

**Verdict:** IPv6 sockets CAN be created and `::1` CAN be resolved and bound in this Termux environment. HOWEVER, `getaddrinfo("localhost", ..., AF_INET6)` failed — `/etc/hosts` contains `::1 ip6-localhost` but NOT `::1 localhost`, so `localhost` only resolves to IPv4 `127.0.0.1`. This is a configuration detail, not a kernel limitation.

**IPv6 statement:** IPv6 socket primitives are functional. IPv6 loopback connectivity was partially demonstrated (bind to `::1` succeeded). Full IPv6 loopback data exchange (connect + send/recv over `::1`) was not tested in this lab. IPv6 is NOT VERIFIED absent — it is partially available.

### inet_pton / inet_ntop (VERIFIED)

| Operation | Input | Output | Bytes |
|-----------|-------|--------|-------|
| `inet_pton(AF_INET, ...)` | `127.0.0.1` | `7f000001` | 4 bytes: `[127, 0, 0, 1]` |
| `inet_ntop(AF_INET, ...)` | `7f000001` | `127.0.0.1` | — |
| `inet_pton(AF_INET6, ...)` | `::1` | `00000000000000000000000000000001` | 16 bytes |
| `inet_ntop(AF_INET6, ...)` | 16-byte binary | `::1` | — |

### localhost Resolution (VERIFIED)

| Query | Result |
|-------|--------|
| `getaddrinfo("localhost", AF_INET)` | `127.0.0.1` |
| `getaddrinfo("localhost", AF_INET6)` | FAILED — `[Errno 7] No address associated with hostname` |

---

## Android / Termux Limitations

| Limitation | Impact | Type |
|------------|--------|------|
| `/proc/net/*` inaccessible | Cannot verify TCP socket states (LISTEN, ESTABLISHED) from outside Python | ANDROID SANDBOX — not fixable without root |
| `ss` command unavailable (`iproute2` not installed) | Cannot independently verify listening ports from shell | MISSING PACKAGE — fixable via `pkg install iproute2` |
| `netstat -tln` shows header only, no data rows | Cannot cross-validate port_check.py results with an independent tool | ANDROID SANDBOX — netstat reads `/proc/net/tcp` which is restricted |
| MAC addresses zeroed | Not relevant to this lab (all traffic is loopback) | ANDROID PRIVACY — not fixable |
| `getaddrinfo("localhost", AF_INET6)` fails | IPv6 localhost resolution requires explicit `::1` or `/etc/hosts` entry | CONFIGURATION — `/etc/hosts` has `::1 ip6-localhost` but not `::1 localhost` |

All experiments completed successfully despite these limitations. The Python `socket` module provided everything needed for loopback communication.

---

## Unexpected Results

### 1. Background process management was messier than expected

**Observation:** The first `tcp_server.py &` launched from a compound bash command
left a process (PID 4169) that survived the shell and continued holding port 8080.
A second launch attempt failed with "Address already in use." The original PID
was tracked down and terminated with `kill 4170` (the actual Python PID, found
via `pgrep`).

**Lesson:** In a lab environment, always track the PID explicitly and verify
port state before and after experiments. Multiple shell sessions and background
process management require careful bookkeeping.

### 2. Ephemeral ports were not sequential

**Observation:** Sequential ephemeral ports from three `tcp_client.py` runs
were `32822`, `32828`, `32832` — gaps of +6 and +4 instead of +1. (VERIFIED)

**Explanation:** Ephemeral port allocation is controlled by the operating system
and is NOT required to be sequential. The OS guarantees that each active
connection receives a **unique** four-tuple `(src_ip, src_port, dst_ip, dst_port)`,
not that ports are assigned consecutively. The exact cause of these specific
gaps was NOT VERIFIED — we did not trace kernel port allocation to determine
what (if anything) consumed the intermediate port numbers between our runs.

### 3. netstat -tln shows header but no data rows

**Observation:** `netstat -tln` ran without error but displayed only the column
headers with no connection rows.

**Explanation (INFERRED, consistent with LAB-001 findings):** `netstat` reads
`/proc/net/tcp` which is restricted on Android. The tool runs but sees an empty
or inaccessible socket table, so it prints the header and nothing else.

---

## Theory vs. Observation

| Theoretical Claim | Observation | Match? |
|-------------------|-------------|--------|
| TCP requires `socket() → bind() → listen() → accept()` on the server | `tcp_server.py` uses exactly this sequence | ✓ VERIFIED |
| `connect()` triggers the three-way handshake | `connect()` returned successfully, connection was established | ✓ VERIFIED |
| The OS assigns an ephemeral source port when `connect()` is called without prior `bind()` | Three connections got different source ports (32822, 32828, 32832) | ✓ VERIFIED |
| A closed port causes `connect()` to fail with connection refused | `port_check.py 8081` raised `ConnectionRefusedError` | ✓ VERIFIED |
| Closed-port kernel response is TCP RST | Not directly observed (no packet capture) | INFERRED from TCP specification |
| A port closes when the listening process exits | After `kill 4170`, `port_check.py 8080` showed CLOSED | ✓ VERIFIED |
| UDP has no `listen()` or `accept()` | `udp_server.py` uses `bind()` + `recvfrom()` only | ✓ VERIFIED |
| UDP `sendto()` triggers ephemeral port assignment | `getsockname()` returned `0.0.0.0:0` before, then a real port after `sendto()` | ✓ VERIFIED |
| `getsockname()` returns the local endpoint | Returned `127.0.0.1:32822` for first TCP client | ✓ VERIFIED |
| `getpeername()` returns the remote endpoint | Returned `127.0.0.1:8080` for all TCP client runs | ✓ VERIFIED |
| `inet_pton` converts string → binary | `127.0.0.1` → `7f000001` | ✓ VERIFIED |
| IPv6 sockets can be created on this device | `socket(AF_INET6, SOCK_STREAM)` succeeded | ✓ VERIFIED |
| `::1` can be resolved and bound | `bind(::1, ...)` succeeded | ✓ VERIFIED |

---

## Conclusion

### What was experimentally demonstrated

1. **TCP connection lifecycle** — server calls `bind()` + `listen()` + `accept()`;
   client calls `connect()`. The three-way handshake completes, and data flows
   in both directions. (VERIFIED)

2. **Open vs. closed ports** — Port 8080 was OPEN while `tcp_server.py` ran;
   port 8081 was CLOSED (no listener); port 8080 became CLOSED after the server
   process was killed. A port is open ONLY while a process is alive and
   listening. (VERIFIED)

3. **Ephemeral ports** — Three TCP connections were assigned source ports
   `32822`, `32828`, and `32832` by the OS. Each connection gets a unique source
   port from the ephemeral range. (VERIFIED)

4. **UDP is connectionless** — No `listen()`, no `accept()`, no handshake.
   The first `sendto()` triggers ephemeral port assignment (`getsockname()`
   changed from `0.0.0.0:0` to `0.0.0.0:58462`). (VERIFIED)

5. **`getsockname()` and `getpeername()` work** — They reveal both endpoints
   of a TCP connection, including the OS-assigned ephemeral source port.
   (VERIFIED)

6. **`inet_pton` / `inet_ntop` are reversible** — `127.0.0.1` ↔ `7f000001`
   (4 bytes); `::1` ↔ 16 bytes. (VERIFIED)

7. **IPv6 primitives are partially available** — Sockets create, `::1` resolves
   and binds. `localhost` over IPv6 does not resolve (hosts file limitation).
   (VERIFIED with caveats)

### What was inferred (not directly observed)

- The kernel (not the Python process) handles the SYN/SYN-ACK/ACK of the
  three-way handshake. This is INFERRED from behavior consistent with the TCP
  specification — `connect()` blocks until the handshake completes, but we
  did not capture packets to confirm each flag.

- The kernel sends a TCP RST in response to SYN on a closed port. This is
  INFERRED from the `ConnectionRefusedError` we observed, combined with the
  TCP specification. We did not capture packets to confirm the RST on the wire.
  On loopback, the kernel may optimize the rejection without sending an actual
  RST packet.

### What could not be verified

- Actual SYN/SYN-ACK/ACK packet exchange (would require packet capture —
  `/proc/net/` is restricted on this Android device).

- TCP state transitions at the kernel level (LISTEN → SYN_RCVD → ESTABLISHED).

- Whether `port_check.py 8081` received an actual TCP RST packet or the kernel
  returned an error through a faster loopback-only code path.

- The exact cause of ephemeral port gaps (+6, +4 between consecutive
  `tcp_client.py` runs). The gaps are VERIFIED but their cause (other socket
  activity, kernel allocation algorithm, etc.) was NOT VERIFIED.

---

## Cleanup Verification

| Process | PID | Cleanup Method | Status |
|---------|-----|----------------|--------|
| tcp_server.py | 4170 | `kill 4170` | PASS — port 8080 confirmed CLOSED after termination |
| udp_server.py | 7876 | `kill 7876` | PASS — process no longer running |
| Residual processes | — | `pgrep -la python` returns exit code 1 (no matches) | PASS |

**TCP server cleanup:** PASS
**UDP server cleanup:** PASS
**No Python processes remain:** VERIFIED
