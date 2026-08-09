# LAB-001: Know Your Host

- **Phase:** 02 — Network Fundamentals
- **Date:** 2026-08-09
- **Environment:** Android tablet, Termux, Python 3.x (standard library only)
- **Status:** In Progress

---

## Theory

Every device on a network has an identity. Before we send, receive, or intercept
traffic, we must understand the networking environment of the device we are working
on. This lab is about answering one question: **"What does this device look like
to the network?"**

### 1. The Kernel and Userspace

The Linux kernel manages all hardware — including network interfaces. Userspace
programs (shell commands, Python scripts) talk to the kernel through:

- **System calls** (`socket()`, `bind()`, `connect()`, `send()`, `recv()`)
- **Virtual filesystems** (`/proc`, `/sys`) that expose kernel state as readable files
- **Netlink sockets** used by tools like `ip`, `ss`, and `nft`

> On Android, some `/proc` entries are restricted for security. Where a file is
> unreadable, we note the restriction and work around it.

### 2. Network Interfaces

A **network interface** is the logical or physical point where a device connects
to a network. Think of it as a door: packets enter and leave through it.

| Interface | Typical Meaning |
|-----------|----------------|
| `lo` | Loopback — traffic to itself (`127.0.0.1`, `::1`) |
| `wlan0` | WiFi interface (common on Android) |
| `eth0` | Ethernet (wired) interface |
| `rmnet0` | Mobile data interface (Android cellular) |
| `dummy0` | Virtual interface for testing |
| `tun0` / `tap0` | VPN tunnel interfaces |

Each interface has:
- A **MAC address** (Layer 2) — burned into the hardware, 48 bits, written as `aa:bb:cc:dd:ee:ff`
- One or more **IP addresses** (Layer 3) — assigned by DHCP or manually
- **Flags** — `UP` (active), `BROADCAST` (can send to all), `MULTICAST`, `LOOPBACK`

### 3. IPv4 and IPv6

**IPv4** — 32-bit address, written as 4 decimal octets: `192.168.1.42`
- ~4.3 billion possible addresses (many reserved)
- Still the dominant protocol on the internet

**IPv6** — 128-bit address, written as 8 groups of 4 hex digits: `fe80::1a2b:3c4d:5e6f:7a8b`
- Vast address space; designed to replace IPv4
- Link-local addresses (`fe80::/10`) are automatically assigned on every interface
- Often runs alongside IPv4 ("dual stack")

### 4. Private IP Addresses

RFC 1918 reserves these IPv4 ranges for private networks. They are not routable
on the public internet and require NAT to reach external hosts:

| Range | CIDR | Typical Use |
|-------|------|-------------|
| `10.0.0.0` — `10.255.255.255` | `10.0.0.0/8` | Large corporate networks |
| `172.16.0.0` — `172.31.255.255` | `172.16.0.0/12` | Medium networks |
| `192.168.0.0` — `192.168.255.255` | `192.168.0.0/16` | Home / small networks |

> If your device has an address in one of these ranges, it is behind NAT —
> your router is sharing one public IP among all devices on your local network.

### 5. Subnets and CIDR Notation

CIDR (Classless Inter-Domain Routing) notation: `192.168.1.42/24`

The `/24` means "the first 24 bits are the network prefix; the remaining 8 bits
identify hosts on this network."

| CIDR | Subnet Mask | Hosts | Notes |
|------|-------------|-------|-------|
| `/8` | `255.0.0.0` | 16,777,214 | Class A size |
| `/16` | `255.255.0.0` | 65,534 | Class B size |
| `/24` | `255.255.255.0` | 254 | Home LAN typical |
| `/32` | `255.255.255.255` | 1 | Single host |

To calculate: `hosts = 2^(32 - prefix_length) - 2` (subtract network and broadcast addresses).

### 6. Default Gateway

The **default gateway** is the router that forwards traffic from the local network
to other networks (usually the internet). In the routing table, it appears as
`default via <IP>` or `0.0.0.0/0`. Without a default gateway, the device can
only communicate with hosts on the same local subnet.

### 7. DNS (Domain Name System)

DNS translates human-readable names (`www.example.com`) into machine-routable
IP addresses (`93.184.216.34`). The DNS server addresses are configured in
`/etc/resolv.conf`. When you open a URL, your device sends a UDP packet to port 53
of the DNS server asking "what is the IP for this name?"

### 8. Loopback and Localhost

The **loopback** interface (`lo`) is a virtual interface. Traffic sent to it
stays inside the device — it never reaches the wire. Addresses:
- IPv4: `127.0.0.1` (and the entire `127.0.0.0/8` range)
- IPv6: `::1`

Why it matters: services under development, databases, and inter-process
communication often listen on `127.0.0.1` to accept only local connections.

### 9. Sockets

A **socket** is a programming abstraction: one endpoint of a network connection.
Identified by the tuple `(protocol, source_ip, source_port, dest_ip, dest_port)`.
Sockets are created with the `socket()` system call and are the fundamental
building block of all network programming.

### 10. The TCP/IP Stack

The **TCP/IP stack** is the kernel's implementation of the Internet Protocol
suite. It handles:

| Layer | Responsibility | Example Protocols |
|-------|---------------|-------------------|
| Application | User-facing protocols | HTTP, DNS, SSH, SMTP |
| Transport | End-to-end reliability / datagrams | TCP, UDP |
| Network | Routing and addressing | IP, ICMP |
| Link | Physical addressing, media access | Ethernet, WiFi (802.11) |

When a Python script calls `socket.connect(("example.com", 80))`, the kernel
handles DNS resolution, TCP handshake, IP routing, and ARP resolution — all
transparently.

---

## Experiment

### Step 1: Shell Inspection

Run `bash commands.sh` (or each command individually) to inspect the device's
network environment from the shell.

We will collect:
- OS and kernel version (`uname -a`)
- User identity (`whoami`)
- Network interfaces and their addresses (`ip addr show`)
- Routing table and default gateway (`ip route show`)
- DNS configuration (`cat /etc/resolv.conf`)
- Hosts file (`cat /etc/hosts`)
- Open listening sockets (`ss -tlnp` or `netstat -tlnp`)

### Step 2: Python Inspection

Run `python src/interface_info.py` to perform the same inspection from Python
using only the standard library (`socket`, `os`, `subprocess`). Compare the output
with the shell commands — they should agree.

### Step 3: Sketch Your Environment

Based on the collected data, draw and label:
- Your device's hostname, interfaces, and IP addresses
- The subnet each interface belongs to
- The default gateway
- Which DNS server(s) are configured
- Whether you are behind NAT

---

## Observation

Record your observations in `observations.md`. For each interface found, document:

1. Interface name and type
2. IPv4 address and subnet mask (in CIDR notation)
3. IPv6 addresses (link-local and global, if any)
4. MAC address
5. Interface flags (UP, BROADCAST, MULTICAST, LOOPBACK)
6. MTU (Maximum Transmission Unit)

Also record:
- Hostname
- Default gateway IP
- DNS server IPs
- Any restricted files or commands (common on Android/Termux)

---

## Conclusion

After completing this lab, you should be able to:

1. **Identify every network interface** on your device and explain its role.
2. **Explain CIDR notation** and calculate the number of hosts in a subnet.
3. **Determine whether your device is behind NAT** by examining its IP addresses.
4. **Trace what happens** when a program opens a socket — from the `socket()` call
   down to the hardware interface.
5. **Read a routing table** and identify the default gateway.
6. **Understand the difference** between link-local, private, and public IP addresses.

Most importantly, you should now see your device not as a "black box that connects
to WiFi" but as a **specific, inspectable node** on a network with concrete
addresses, routes, and interfaces — all of which you can examine and understand.

---

## Exercises

> These are for self-assessment. Do not provide answers in this file.

1. What is the difference between the `lo` interface and the `wlan0` interface?
   Why does `127.0.0.1` always refer to the same host regardless of which device
   you are on?

2. Convert the subnet mask `255.255.255.240` to CIDR notation. How many usable
   host addresses does it provide? Show your calculation.

3. Your device has IP `192.168.1.42/24`. Is `192.168.1.255` a usable host address?
   Why or why not?

4. Run `ping 127.0.0.1` and `ping ::1`. Which IP version does each use? What is
   the practical difference between IPv4 and IPv6 loopback?

5. Your device has a `192.168.1.x` address, but `curl ifconfig.me` reports a
   completely different IP. Explain why. What network device is responsible for
   this translation?

6. What entries exist in `/etc/hosts`? Why does this file exist when DNS already
   does the same job of name → IP mapping?

7. If you delete the default gateway route, what happens to your ability to
   reach `8.8.8.8`? What about `192.168.1.1` (on the same subnet)? Explain why.

8. Open a Python REPL. Create a socket with `socket.socket(socket.AF_INET,
   socket.SOCK_STREAM)`. What do `AF_INET` and `SOCK_STREAM` mean? What other
   values exist and when would you use them?

9. The `ss` command shows "listening" sockets. What does it mean for a socket to
   be in the LISTEN state? Who is it listening for?

10. Your DNS server is at `192.168.1.1`. Is that address on your local network,
    or remote? If local, what program on that host is actually performing DNS
    resolution for you? (Hint: it's not a full DNS resolver — it forwards.)

---

## References

- RFC 1918 — Address Allocation for Private Internets
- RFC 4632 — Classless Inter-domain Routing (CIDR)
- RFC 4291 — IPv6 Addressing Architecture
- `man 7 ip` — Linux IP protocol family
- `man 7 socket` — Linux socket interface
- `man 8 ip` — `ip` command manual
