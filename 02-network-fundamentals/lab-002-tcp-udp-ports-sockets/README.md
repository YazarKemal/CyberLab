# LAB-002: TCP, UDP, Ports and Sockets

- **Phase:** 02 — Network Fundamentals
- **Date:** 2026-08-09
- **Environment:** Android tablet, Termux, Python 3.x (standard library only)
- **Scope:** localhost only (`127.0.0.1`, `::1`)
- **Status:** In Progress

---

## 1. Theory

### What is a socket?

A **socket** is a programming abstraction for one endpoint of a network
connection. It is identified by the tuple:

```
(protocol, source_ip, source_port, destination_ip, destination_port)
```

When a Python program calls `socket()`, the operating system creates a data
structure inside the kernel that represents this endpoint. The program interacts
with it through a **file descriptor** — an integer handle, just like an open file.

Sockets were invented at UC Berkeley in 1983 as part of BSD Unix. The API —
`socket()`, `bind()`, `listen()`, `accept()`, `connect()`, `send()`, `recv()`,
`close()` — is called the **Berkeley Sockets API** and remains essentially
unchanged 40 years later. Every modern operating system implements it.

### IP address and port — the two-part address

An **IP address** identifies a host (a device) on a network. It answers the
question: *which machine?*

A **port** identifies a specific process (or service) on that host. It answers
the question: *which program on that machine?*

Together, `IP:port` is a complete address for one endpoint of a communication.

```
192.168.1.42:8080
 ^^^^^^^^^^^^  ^^^^
   host         process
```

Ports are 16-bit unsigned integers: **0 through 65535**.

| Port Range | Designation | Typical Use |
|------------|-------------|-------------|
| 0 | Reserved | Should not be used |
| 1–1023 | Well-known / system ports | HTTP (80), SSH (22), DNS (53) — require root to bind on Unix |
| 1024–49151 | Registered ports | User services, applications |
| 49152–65535 | Ephemeral / dynamic ports | Automatically assigned by OS for client connections |

### Source port vs. destination port

Every TCP connection and every UDP datagram carries **two** port numbers:

```
Source Port      Destination Port
~~~~~~~~~~~~     ~~~~~~~~~~~~~~~~~
The sender's     The recipient's
side of the      side of the
conversation     conversation
```

- The **destination port** tells the receiving OS which process should get the packet.
- The **source port** tells the receiving OS where to send the reply.

When you visit `https://example.com`, your browser:
1. Asks the OS for an **ephemeral port** (e.g., `49152`).
2. Sends a TCP packet from `your_ip:49152` to `example.com:443`.
3. The server replies from `example.com:443` to `your_ip:49152`.

The source port is how the OS knows which browser tab gets which response.

### TCP — Transmission Control Protocol

TCP is **connection-oriented** and **reliable**. It provides:

- **Ordered delivery** — bytes arrive in the order they were sent.
- **Error detection** — checksums detect corruption.
- **Retransmission** — lost packets are resent.
- **Flow control** — the receiver won't be overwhelmed.
- **Congestion control** — the network won't be overwhelmed.

These guarantees come at a cost: TCP requires a **three-way handshake** to
establish state on both ends before any application data can flow.

#### TCP three-way handshake

```
Client                              Server
------                              ------
socket()                            socket()
                                    bind()
                                    listen()

STATE: CLOSED                       STATE: LISTEN

connect() --- SYN (seq=x) ------->

STATE: SYN_SENT
                                    STATE: SYN_RCVD
          <--- SYN-ACK (seq=y, ack=x+1) ---

STATE: ESTABLISHED

          --- ACK (ack=y+1) ------>

                                    STATE: ESTABLISHED

          ============ CONNECTION ESTABLISHED ============

send()    --- data --------------->
          <--- data ---------------- recv()/send()

close()   --- FIN ----------------->
          <--- FIN-ACK -------------
          --- ACK -----------------> close()

STATE: CLOSED                       STATE: CLOSED
```

**SYN** — "I want to synchronize. Here's my starting sequence number."
**SYN-ACK** — "I acknowledge your SYN. Here's my starting sequence number."
**ACK** — "I acknowledge your SYN-ACK. We're connected."

After this handshake, both sides know:
- The other side is reachable.
- The other side agrees to communicate.
- The initial sequence numbers (used to track which bytes have been delivered).

### UDP — User Datagram Protocol

UDP is **connectionless** and **unreliable** (in the protocol sense — it does
not guarantee delivery). It provides:

- **No handshake** — send data immediately, no setup.
- **No connection state** — each datagram is independent.
- **No guaranteed delivery** — packets may be lost, duplicated, or reordered.
- **No flow control** — the sender can overwhelm the receiver.
- **No congestion control** — the sender can overwhelm the network.

Why use UDP at all? Because sometimes the application wants to manage these
concerns itself, or the cost of TCP's handshake and state management outweighs
the benefits. DNS, streaming video, VoIP, and online games all use UDP.

```
Client                              Server
------                              ------
socket()                            socket()
                                    bind()

sendto() --- datagram ----------->

          <--- datagram ----------- sendto()

No handshake. No persistent state. No connection.
```

### Berkeley Sockets API — the key calls

| Call | What it does | TCP | UDP |
|------|-------------|-----|-----|
| `socket()` | Creates a socket endpoint. Returns a file descriptor. | ✓ | ✓ |
| `bind()` | Assigns a local IP and port to the socket. | ✓ | ✓ |
| `listen()` | Marks a socket as passive (server). Sets the backlog queue depth. | ✓ | ✗ |
| `accept()` | Blocks until a client connects. Returns a **new** socket for that specific connection. | ✓ | ✗ |
| `connect()` | Initiates a connection to a remote socket. Triggers the TCP handshake. | ✓ | ✗ |
| `send()` / `sendall()` | Sends data on a connected socket. | ✓ | ✗ |
| `recv()` | Receives data from a connected socket. | ✓ | ✗ |
| `sendto()` | Sends a datagram to a specified address. | ✗ | ✓ |
| `recvfrom()` | Receives a datagram and the sender's address. | ✗ | ✓ |
| `close()` | Tears down the socket. Sends FIN on TCP. | ✓ | ✓ |
| `getsockname()` | Returns the socket's own (local) address. | ✓ | ✓ |
| `getpeername()` | Returns the connected peer's (remote) address. | ✓ | ✗ |

### Socket lifecycle — TCP server

```
socket()  →  bind()  →  listen()  →  accept()  →  recv()/send()  →  close()
                                           ↑                        │
                                           └──── (loop back) ───────┘
```

Each call to `accept()` returns a **new** socket. The original "listening
socket" only accepts new connections — it never sends or receives data. The
returned "connection socket" handles the actual communication with that
specific client.

### Socket lifecycle — TCP client

```
socket()  →  connect()  →  send()/recv()  →  close()
```

`connect()` triggers the three-way handshake. When it returns, the connection
is established and data can flow.

### Socket states

| State | Meaning |
|-------|---------|
| `CLOSED` | No socket exists. |
| `LISTEN` | A server socket is waiting for connection requests. Shown by `ss -tln` as a listening port. |
| `SYN_SENT` | Client sent SYN, waiting for SYN-ACK. |
| `SYN_RCVD` | Server received SYN, sent SYN-ACK, waiting for ACK. |
| `ESTABLISHED` | Connection is open. Data flows in both directions. |
| `FIN_WAIT` / `CLOSE_WAIT` / `TIME_WAIT` | Connection is being torn down. |

### Open port vs. closed port

- **Open port** — a process has called `bind()` and `listen()` on that port.
  The kernel will accept SYN packets destined for this port and complete the
  handshake.
- **Closed port** — no process is listening. The kernel responds to SYN with
  **RST (reset)**, telling the sender "nothing here." In some configurations
  the packets are simply dropped (filtered port).

A port is **only open while a process is listening on it**. When the process
exits, the kernel closes the port automatically.

### Ephemeral (dynamic) ports

When a client calls `connect()` without first calling `bind()`, the OS
automatically assigns a **temporary source port** from the ephemeral range
(typically 32768–60999 on Linux, 49152–65535 per IANA).

This is why a single browser can have dozens of simultaneous connections —
each gets its own source port, and the four-tuple `(src_ip, src_port, dst_ip,
dst_port)` uniquely identifies every connection.

---

## 2. Terminology

| Term | Definition |
|------|------------|
| **Socket** | A programming abstraction for a network endpoint: `(protocol, IP, port)`. |
| **IP address** | A numerical label identifying a host on a network. IPv4: 32 bits. IPv6: 128 bits. |
| **Port** | A 16-bit number (0–65535) identifying a specific process on a host. |
| **Source port** | The port on the sender's side. Often assigned ephemerally by the OS. |
| **Destination port** | The port on the receiver's side. Matches the port the server is listening on. |
| **TCP** | Transmission Control Protocol. Connection-oriented, reliable, ordered byte stream. |
| **UDP** | User Datagram Protocol. Connectionless, unreliable, datagram-based. |
| **Connection-oriented** | Both endpoints maintain state about the communication. Requires setup (handshake) and teardown. |
| **Connectionless** | Each message is independent. No state, no setup, no teardown. |
| **bind()** | Assigns a local address and port to a socket. "I will use this address." |
| **listen()** | Marks a socket as passive — it will accept incoming connections. TCP only. |
| **accept()** | Blocks until a client connects. Returns a new socket for that client. TCP only. |
| **connect()** | Initiates a connection to a remote address. Triggers the TCP handshake. |
| **send() / sendall()** | Transmits data on a connected socket. TCP only. |
| **recv()** | Reads data from a connected socket. TCP only. |
| **sendto() / recvfrom()** | Send and receive datagrams with explicit addresses. UDP. |
| **LISTEN** | A TCP socket state: waiting for incoming connection requests. |
| **ESTABLISHED** | A TCP socket state: connection is open, data flows. |
| **CLOSED** | No socket exists on this port. |
| **Open port** | A port on which a process is listening. |
| **Closed port** | A port on which no process is listening. SYN → RST. |
| **Ephemeral port** | A temporary port assigned by the OS for a client connection. |
| **Three-way handshake** | SYN → SYN-ACK → ACK. Establishes a TCP connection. |
| **getsockname()** | Returns the socket's own `(ip, port)` — useful for finding the OS-assigned source port. |
| **getpeername()** | Returns the connected peer's `(ip, port)`. Meaningful only after `connect()` or `accept()`. |
| **SO_REUSEADDR** | A socket option that allows rebinding to a port that was recently closed (avoids "Address already in use"). |

---

## 3. TCP Experiment

### Setup

Open **two** Termux sessions (or two terminals). In one, run the server. In the
other, run the client.

**Session 1 (Server):**
```bash
cd ~/CyberLab/02-network-fundamentals/lab-002-tcp-udp-ports-sockets
python src/tcp_server.py
```

The server binds to `127.0.0.1:8080`, calls `listen()`, and waits. It prints
its own address and then blocks on `accept()`.

**Session 2 (Client):**
```bash
cd ~/CyberLab/02-network-fundamentals/lab-002-tcp-udp-ports-sockets
python src/tcp_client.py
```

The client connects to `127.0.0.1:8080`, sends a message, receives the
response, prints the four-tuple using `getsockname()` and `getpeername()`,
and exits.

### What to watch

In the server output, note:
- The server's own address (should be `127.0.0.1:8080`).
- The client's address when it connects — especially the **source port**
  assigned by the OS. It will be an ephemeral port (high number).

In the client output, note:
- `getsockname()` — the client's own address, including the OS-assigned source port.
- `getpeername()` — the server's address (`127.0.0.1:8080`).

Run the client multiple times. Observe whether the source port changes.

### Expected output (example)

**Server:**
```
TCP Server listening on 127.0.0.1:8080
Waiting for connections...
Connection from ('127.0.0.1', 49152)
Received: Hello from TCP client!
Sent reply.
```

**Client:**
```
Connected to 127.0.0.1:8080
My local address: ('127.0.0.1', 49152)
Server address:    ('127.0.0.1', 8080)
Server response: Hello from TCP server! You said: Hello from TCP client!
```

---

## 4. Open vs. Closed Port Experiment

While `tcp_server.py` is running in session 1, run `port_check.py` in session 2:

```bash
python src/port_check.py 8080    # Server running → should report OPEN
python src/port_check.py 8081    # Nothing listening → should report CLOSED
```

Stop the server (Ctrl+C in session 1). Then check again:

```bash
python src/port_check.py 8080    # Server stopped → now CLOSED
```

### What this demonstrates

`port_check.py` attempts a TCP `connect()` to the target port. If the OS
completes the three-way handshake, the port was **open** (a process was
listening). If the OS returns "Connection refused," the kernel sent back a
RST — the port was **closed** (no process listening).

A port is open **only while a process is listening on it.** The moment the
server process exits, the port closes.

---

## 5. UDP Experiment

### Setup

**Session 1 (Server):**
```bash
cd ~/CyberLab/02-network-fundamentals/lab-002-tcp-udp-ports-sockets
python src/udp_server.py
```

**Session 2 (Client):**
```bash
cd ~/CyberLab/02-network-fundamentals/lab-002-tcp-udp-ports-sockets
python src/udp_client.py
```

### What to watch

- The UDP server does **not** call `listen()` or `accept()`. It calls `bind()`,
  then immediately calls `recvfrom()`.
- The UDP client does **not** call `connect()`. It calls `sendto()` with the
  server's address.
- `recvfrom()` returns both the data AND the sender's address — the server
  does not need a per-client socket.
- There is no persistent connection. Each `sendto()` is an independent datagram.

---

## 6. TCP vs. UDP Comparison

| Property | TCP (`SOCK_STREAM`) | UDP (`SOCK_DGRAM`) |
|----------|--------------------|--------------------|
| Connection model | Connection-oriented | Connectionless |
| Handshake | Three-way: SYN, SYN-ACK, ACK | None |
| Reliability | Guaranteed delivery, ordered | Best-effort, may lose/reorder |
| Data boundary | Byte stream (no message boundaries) | Message boundaries preserved |
| Server calls | `socket() → bind() → listen() → accept() → recv()/send()` | `socket() → bind() → recvfrom()/sendto()` |
| Client calls | `socket() → connect() → send()/recv()` | `socket() → sendto()/recvfrom()` |
| State | Both ends maintain connection state | No state between datagrams |
| Use cases | HTTP, SSH, email, file transfer | DNS, VoIP, streaming, gaming |
| Overhead | Higher (handshake, ACKs, retransmission) | Lower (8-byte header, no connection state) |

---

## 7. Android / Termux Notes

- All experiments in this lab use `127.0.0.1` exclusively. No packets leave the device.
- IPv6 (`::1`) support is optional — `socket_demo.py` attempts it and reports gracefully
  if unavailable.
- The ephemeral port range on Android/Linux is typically `32768–60999` but may vary.
- `SO_REUSEADDR` is set on all server sockets to avoid "Address already in use" errors
  when rapidly restarting servers during experimentation.
- If a port is unexpectedly "in use," wait ~60 seconds for `TIME_WAIT` state to expire,
  or use a different port.

---

## 8. Observation

Record your observations in `observations.md`. For each experiment, document:

1. Exact commands run and their output.
2. The source port assigned to the TCP client (does it change between runs?).
3. What `getsockname()` and `getpeername()` return — and what each means.
4. The difference in behavior when `port_check.py` targets an open vs. closed port.
5. The sequence of calls in the UDP server vs. the TCP server — what's missing and why.
6. Any errors or unexpected results.

---

## 9. Conclusion

After completing this lab, you should be able to:

1. **Write a working TCP server and client** from memory, explaining every call.
2. **Explain the three-way handshake** and why both `connect()` (client) and
   `accept()` (server) are required for TCP.
3. **Explain why UDP has no `listen()` or `accept()`** — because it has no
   connection state.
4. **Distinguish source port from destination port** and explain how the OS
   assigns ephemeral ports.
5. **Use `getsockname()` and `getpeername()`** to inspect both ends of a connection.
6. **Define "open port"** precisely — a port is open only while a process has
   called `bind()` and `listen()` on it.

---

## 10. Exercises

> These are for self-assessment. Determine the answers by running the experiments
> and inspecting the code — not by looking them up. For each question, explain
> not just what happened but **why** at the kernel and protocol level.

1. Why was port 8080 OPEN while `tcp_server.py` was running? What specific
   sequence of system calls made the kernel accept connections on this port?

2. Why did port 8080 become CLOSED after the server process was terminated?
   What cleans up the listening state, and when?

3. Why was port 8081 CLOSED? Trace the exact path of a SYN packet targeting
   port 8081 — what does the kernel do and why?

4. What ephemeral source ports did Android/Linux assign to our TCP clients?
   Record the actual ports from your experiment runs.

5. Did those ephemeral ports change between connections? Were they sequential?
   Why does the OS assign different ports instead of reusing the same one?

6. What does `getsockname()` tell us? When in the TCP lifecycle does it become
   meaningful? What does it return before `connect()` is called?

7. What does `getpeername()` tell us? Why is it available on a TCP socket
   after `connect()` but not on a UDP socket after `sendto()`?

8. What exactly does `bind()` do? What happens if you call `connect()` without
   first calling `bind()`? Who assigns the port in that case?

9. What exactly does `listen()` do? Why is it a separate call from `bind()`?
   What is the "backlog" parameter, and what happens when the backlog fills up?

10. What exactly does `accept()` return? Why does it return a **new** socket
    instead of using the original listening socket for communication?

11. Why does the UDP server not use `listen()`? What about UDP's design makes
    a "listening" state unnecessary?

12. Why does the UDP server not use `accept()`? How does the server know who
    sent each datagram without a per-client socket?

13. What is the practical difference between `SOCK_STREAM` and `SOCK_DGRAM`?
    Give a concrete example where you would choose one over the other and
    explain the tradeoff.

14. Which parts of the TCP three-way handshake (SYN → SYN-ACK → ACK) were
    handled by our Python program, and which were handled by the Linux kernel?
    What does `connect()` actually do — does it send the SYN, or does it ask
    the kernel to send it?

---

## References

- RFC 793 — Transmission Control Protocol (TCP)
- RFC 768 — User Datagram Protocol (UDP)
- RFC 6335 — Internet Assigned Numbers Authority (IANA) port ranges
- W. Richard Stevens, *UNIX Network Programming, Volume 1* (the canonical text)
- `man 7 socket` — Linux socket interface
- `man 7 tcp` — Linux TCP protocol
- `man 7 udp` — Linux UDP protocol
