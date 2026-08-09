# LAB-001: Observations

- **Date:** 2026-08-09
- **Device:** Android tablet (Termux)
- **Inspector:** YazarKemal

---

## Theory

Before sending or receiving network traffic, we must understand what the local
device looks like to the network. This lab inspects the host using two
approaches — shell commands and a Python script — and then cross-validates the
results.

The key concepts under investigation:

| Concept | What we are looking for |
|----------|------------------------|
| Network interfaces | Which physical and virtual interfaces exist? What are their IP addresses, netmasks, and MTUs? |
| Loopback | Does `127.0.0.1` respond? What is the latency? |
| IPv4 addressing | Is the device's address in a private (RFC 1918) range? |
| IPv6 addressing | Can we detect any IPv6 addresses? Does `::1` respond? |
| Subnet and CIDR | What prefix lengths are configured? How large is the local subnet? |
| Default gateway | Where does outbound traffic go? (Routing table.) |
| DNS | Which nameservers are configured? |
| MAC addresses | What hardware addresses are bound to each interface? |
| Listening sockets | Is any service accepting connections on this device? |
| Android sandboxing | Which kernel /proc interfaces are restricted in this environment? |

---

## Experiment

### Method

Two independent inspection passes were performed:

1. **Shell inspection** — `bash commands.sh`, a script of safe local commands
   (`uname`, `whoami`, `ifconfig`, `netstat`, `ping`, `cat /etc/hosts`, and
   attempts to read `/proc/net/*` and `/etc/resolv.conf`).

2. **Python inspection** — `python src/interface_info.py`, a standard-library-only
   script using `os.uname()`, `socket.getaddrinfo()`, `socket.inet_pton()`,
   `socket.inet_ntop()`, `subprocess` calls to `ifconfig` / `netstat` / `route`,
   and file reads of `/proc/net/*` and `/etc/hosts`.

All tools were run from the Termux environment on the Android tablet. No
packages were installed. No external hosts were contacted. No packets were sent
beyond the loopback `ping` self-tests.

### Commands executed

See `commands.sh` for the full shell script and `src/interface_info.py` for the
Python equivalent. Key commands:

```
uname -a
whoami
ifconfig
netstat -tln
ping -c 2 127.0.0.1
ping -c 2 ::1
cat /etc/hosts
cat /etc/resolv.conf
cat /proc/net/dev
cat /proc/net/route
cat /proc/net/tcp
cat /proc/net/if_inet6
getprop net.dns1
getprop net.dns2
```

---

## Observation

### System Information

| Field | Value |
|-------|-------|
| Kernel version | `Linux 6.1.145-android14-11-abX230XXS6BZG2` |
| Kernel release | `6.1.145-android14-11` |
| Machine architecture | `aarch64` (64-bit ARM) |
| Python version | `3.14.6` |
| Platform | `Android-16-aarch64-64bit` |
| Hostname | `localhost` |
| User (UID) | `u0_a47` |

### Network Interfaces

#### Interface: `lo` (Loopback)

| Property | Value |
|----------|-------|
| Type | Loopback (virtual) |
| State | `UP`, `LOOPBACK`, `RUNNING` |
| IPv4 address | `127.0.0.1` |
| Netmask | `255.0.0.0` |
| CIDR prefix | `/8` |
| IPv6 address(es) | Not detected |
| MTU | `65536` bytes |
| MAC address | Not applicable (virtual interface — `ifconfig` reports `unspec`) |

#### Interface: `wlan0` (WiFi)

| Property | Value |
|----------|-------|
| Type | WiFi (physical) |
| State | `UP`, `BROADCAST`, `RUNNING`, `MULTICAST` |
| IPv4 address | `10.122.172.202` |
| Netmask | `255.255.0.0` |
| CIDR prefix | `/16` |
| Broadcast address | `10.122.255.255` |
| IPv6 address(es) | Not detected |
| MTU | `1500` bytes |
| MAC address | **Unavailable** — `ifconfig` reports `unspec` (all zeros). Android sandboxes the hardware address from apps. |

### Address Classification

`10.122.172.202/16` falls within the RFC 1918 private range `10.0.0.0/8`.

| Private Range | CIDR | Matches? |
|---------------|------|----------|
| `10.0.0.0/8` | `10.0.0.0/8` | **Yes** — `10.122.x.x` is within `10.0.0.0/8` |
| `172.16.0.0/12` | `172.16.0.0/12` | No |
| `192.168.0.0/16` | `192.168.0.0/16` | No |

**Conclusion about NAT:** The device's IPv4 address is in a private range, which
is **consistent with** being behind NAT. However, NAT was not directly verified
because:
- The routing table could not be read (no default gateway identified).
- No external-address check was performed (would require contacting a host
  outside the local network — out of scope for this lab).
- The presence of NAT is **likely/inferred** but not experimentally demonstrated
  by this lab.

### Routing

| Method attempted | Result |
|------------------|--------|
| `ip route show` | Tool unavailable — `iproute2` is not installed in this Termux environment |
| `route -n` | Returned: `INET (IPv4) not configured in this system.` |
| `cat /proc/net/route` | Permission denied — Android sandbox restriction |

**The default gateway could not be determined** from the tools available in this
environment. This is a combination of:
- Missing tooling (`iproute2` not installed).
- Android sandbox restrictions (kernel networking state in `/proc/net/` is
  inaccessible to the app context).

### DNS Configuration

| Method attempted | Result |
|------------------|--------|
| `cat /etc/resolv.conf` | File does not exist (`ENOENT`) — Android does not use this traditional path |
| `getprop net.dns1` | Returned empty — DNS property not exposed to this app context |
| `getprop net.dns2` | Returned empty — same restriction |
| `socket.getfqdn()` (Python) | Returned `localhost` — no configured FQDN |

**DNS server addresses could not be determined.** Android manages DNS through
`netd`, and the configuration is not exposed to unprivileged app contexts like
Termux.

### Listening Sockets

| Method attempted | Result |
|------------------|--------|
| `ss -tln` | Tool unavailable — `iproute2` is not installed |
| `netstat -tln` | Ran successfully. Header displayed. **No listening TCP services observed.** |
| `cat /proc/net/tcp` | Permission denied — Android sandbox restriction |

**No TCP services were found listening** on this device in the current Termux
environment. This is expected for a stock Android tablet without server software
running.

### Loopback Connectivity

| Test | Result |
|------|--------|
| `ping -c 2 127.0.0.1` | **Success** — 2 packets transmitted, 2 received, 0% loss |
| RTT min/avg/max | `0.086 / 0.113 / 0.141 ms` |
| `ping -c 2 ::1` | **Not available** — `ping6` or IPv6 ping support not present |

IPv4 loopback is functional with sub-millisecond latency. IPv6 loopback could
not be tested.

### `/etc/hosts`

```
127.0.0.1       localhost
::1             ip6-localhost
```

Standard minimal entries. No custom hostname mappings. The `::1` entry exists
but the IPv6 loopback ping tool was unavailable, so IPv6 loopback connectivity
remains unverified.

### Python Socket Experiment

The Python script's §9 ("Socket Module Demonstrations") performed purely local
operations — no network packets were sent by this section.

| Operation | Input | Output |
|-----------|-------|--------|
| `inet_pton(AF_INET, ...)` | `"127.0.0.1"` | `7f 00 00 01` (4 bytes) |
| `inet_pton(AF_INET6, ...)` | `"::1"` | 15 zero bytes + `01` (16 bytes) |
| `inet_ntop(AF_INET, ...)` | `7f 00 00 01` | `"127.0.0.1"` |
| `inet_ntop(AF_INET6, ...)` | 16-byte `::1` binary | `"::1"` |
| `getaddrinfo("localhost", ...)` | `AF_INET` | `127.0.0.1` |
| `getaddrinfo("localhost", ...)` | `AF_INET6` | Failed — no address available |

**Key learning from this section:**
- `inet_pton` ("presentation to network") converts human-readable IP strings into
  the raw bytes that travel inside packet headers. Every IPv4 address on the wire
  is exactly 4 bytes.
- `inet_ntop` ("network to presentation") performs the reverse.
- IPv6 addresses are 16 bytes (128 bits) — 4× the size of IPv4 (32 bits).
- `AF_UNIX` (value `1`) was also listed, demonstrating that the socket API is used
  for local inter-process communication (IPC), not just network communication.

### Address Families and Socket Types

From Python's `socket` module, verified locally:

| Constant | Value | Meaning |
|----------|-------|---------|
| `AF_INET` | `2` | IPv4 address family |
| `AF_INET6` | `10` | IPv6 address family |
| `AF_UNIX` | `1` | Unix domain sockets (local IPC) |
| `SOCK_STREAM` | `1` | Stream socket — TCP (reliable, ordered, connection-oriented) |
| `SOCK_DGRAM` | `2` | Datagram socket — UDP (unreliable, unordered, connectionless) |
| `SOCK_RAW` | `3` | Raw socket — direct access to IP layer (requires root/CAP_NET_RAW) |

---

## Limitations

### Tooling limitations (missing packages — fixable)

These are tools that could be installed in Termux if needed. Their absence is
not a security restriction.

| Missing tool | Package | Provides |
|--------------|---------|----------|
| `ip` | `iproute2` | `ip addr`, `ip route`, `ip neigh` |
| `ss` | `iproute2` | Socket statistics (modern `netstat` replacement) |
| `ping6` / IPv6 ping | (varies) | IPv6 loopback connectivity test |

### Android sandbox restrictions (not fixable without root)

These are deliberate Android security controls. The app context (`u0_a47`) is
prevented from reading kernel networking state.

| Restricted resource | Error | Reason |
|---------------------|-------|--------|
| `/proc/net/dev` | `Permission denied (EACCES)` | Interface statistics |
| `/proc/net/route` | `Permission denied (EACCES)` | Routing table |
| `/proc/net/tcp` | `Permission denied (EACCES)` | TCP socket table |
| `/proc/net/udp` | `Permission denied (EACCES)` | UDP socket table |
| `/proc/net/tcp6` | `Permission denied (EACCES)` | IPv6 TCP socket table |
| `/proc/net/if_inet6` | `Permission denied (EACCES)` | IPv6 interface addresses |
| `/proc/net/arp` | `Permission denied (EACCES)` | ARP cache |
| `/proc/net/snmp` | `Permission denied (EACCES)` | Protocol statistics |
| `/etc/resolv.conf` | `No such file (ENOENT)` | DNS configuration (Android does not use this file) |
| `getprop net.dns*` | Returns empty | DNS properties not exposed to app context |
| MAC address | `unspec` (all zeros) | Android hides hardware addresses from apps |
| IPv6 loopback ping | No `ping6` tool available | Could not test `::1` connectivity |
| Routing (`route -n`) | Returns "not configured" | Kernel routing table not accessible from app context |

### Scope limitations (by design)

This lab intentionally did not:
- Contact any external hosts (no internet access).
- Scan other devices on the local network.
- Install additional packages.
- Attempt privilege escalation or sandbox escape.

---

## Conclusion

### What was demonstrated

1. **The device has two network interfaces:**
   - `lo` at `127.0.0.1/8`, MTU 65536 — functional, sub-millisecond loopback.
   - `wlan0` at `10.122.172.202/16`, MTU 1500 — active WiFi interface in a
     private (RFC 1918) address range.

2. **IPv4 loopback is operational.**
   `ping 127.0.0.1` confirmed the local TCP/IP stack is working correctly.

3. **`inet_pton` / `inet_ntop` form a reversible mapping**
   between human-readable IP addresses and the raw bytes carried in packet headers.
   Verified for both IPv4 (4 bytes) and IPv6 (16 bytes).

4. **No listening TCP services were detected**
   on this device via `netstat -tln`.

5. **Android sandboxes the Termux app context.**
   The entire `/proc/net/` filesystem is inaccessible, DNS configuration is hidden,
   MAC addresses are zeroed, and the routing table cannot be read. These are
   security controls, not bugs — they limit what a compromised app could learn
   about the host network.

6. **Python's `socket` module provides everything needed**
   for low-level address manipulation (`inet_pton`, `inet_ntop`), resolution
   (`getaddrinfo`), and socket creation — all without external packages.

### What could not be determined

- **Default gateway** — routing table inaccessible (sandbox + missing `iproute2`).
- **DNS server addresses** — Android does not expose them to this app context.
- **MAC address** — zeroed by Android's privacy protections.
- **IPv6 connectivity** — `::1` ping tool unavailable; `/proc/net/if_inet6`
  inaccessible; `getaddrinfo` for `localhost` over `AF_INET6` returned no address.
  IPv6 may or may not be present on this device — we simply cannot tell from this
  environment.
- **NAT status** — The private IP (`10.122.172.202/16`) is **consistent with**
  NAT, but NAT was not directly observed (no external-address comparison, no
  gateway inspection).

---

## What I Learned

1. **Android is not a standard Linux system.** From a networking perspective,
   much of the traditional interface (`/proc/net/`, `/etc/resolv.conf`, `route`,
   unrestricted `ifconfig`) is either absent or sandboxed. This is by design.
   Understanding what is *missing* is as instructive as understanding what is
   present.

2. **"Can't tell" is a valid scientific result.** Several questions in this lab
   could not be answered from the available environment. That's a finding, not a
   failure. An investigator must always distinguish between "X is absent" and
   "X could not be observed."

3. **`inet_pton` and `inet_ntop` make IP addressing concrete.** Seeing
   `127.0.0.1` become the four bytes `7f 00 00 01` bridges the gap between
   human-readable addresses and the raw binary that moves across a network.
   Every IP address — every packet — is just bytes.

4. **Tool availability matters.** The `iproute2` suite (`ip`, `ss`) is the
   modern standard for Linux networking. Its absence forced fallback to older
   tools (`ifconfig`, `netstat`), some of which also had restricted output on
   Android. Knowing both old and new interfaces is practical for real-world
   environments.

5. **Private addressing alone does not prove NAT.** A `10.x.x.x` address is a
   strong signal, but confirming NAT requires observing the address translation
   itself — typically by comparing the internal address with the externally
   visible address. That experiment belongs in a later lab.

6. **The socket API is broader than networking.** `AF_UNIX` is a reminder that
   sockets connect local processes, not just remote hosts. The same `send()` /
   `recv()` abstraction works across both domains.
