# LAB-004: ARP Local Resolution

- **Phase:** 02 — Network Fundamentals
- **Date:** 2026-08-09
- **Environment:** Android tablet, Termux, Python 3.x (standard library only)
- **Scope:** offline + local inspection only — no network transmission
- **Status:** Complete

---

## 1. Theory

### OSI Layer 2 vs Layer 3

| Layer | Name | Address Type | Example | Scope |
|-------|------|-------------|---------|-------|
| 3 | Network | IP address | `10.122.172.202` | Global / routable |
| 2 | Data Link | MAC address | `aa:bb:cc:dd:ee:ff` | Local link only |

Layer 3 (IP) gets a packet to the correct **network**. Layer 2 (Ethernet/Wi-Fi)
gets a frame to the correct **device on that network**. Both are required for
delivery on a shared medium like Ethernet or Wi-Fi.

### The Address Resolution Problem

When a host wants to send an IP packet to another host on the same subnet, it
knows the destination IP address — but Ethernet and Wi-Fi frames are addressed
by **MAC address**, not IP address. The sender must discover:

> "What MAC address belongs to IP address X on this local link?"

This is the problem ARP solves.

### What ARP Is (and Is Not)

```
DNS:   example.com   →   93.184.216.34    (name → IP)
ARP:   10.122.10.50  →   aa:bb:cc:dd:ee:ff  (local IP → MAC)
```

- **DNS** translates domain names to IP addresses. It works across the internet.
- **ARP** translates local IP addresses to link-layer (MAC) addresses. It works
  only on the local subnet.

ARP does NOT translate domain names. ARP does NOT work across routers.

### The Full Resolution Chain

```
Application
    ↓
DNS (example.com → 93.184.216.34)
    ↓
Destination IPv4 (93.184.216.34)
    ↓
Routing decision: is 93.184.216.34 on my subnet?
   / \
 YES  NO
  |    |
  |    └── Next-hop: default gateway
  |
Local destination
    ↓
ARP: who has this IP? → MAC address
    ↓
Ethernet/Wi-Fi frame delivery
```

### ARP Protocol (RFC 826)

ARP operates as a separate protocol directly on top of the link layer
(EtherType `0x0806`). It is NOT carried inside IP packets.

#### ARP Request (broadcast)

```
Ethernet header:
  DST: ff:ff:ff:ff:ff:ff  (broadcast — reaches every device on the link)
  SRC: sender's MAC
  EtherType: 0x0806 (ARP)

ARP payload (28 bytes):
  HTYPE = 1 (Ethernet)
  PTYPE = 0x0800 (IPv4)
  HLEN  = 6  (MAC address = 6 bytes)
  PLEN  = 4  (IPv4 address = 4 bytes)
  OPER  = 1  (REQUEST)

  SHA = sender's MAC          (02:00:00:00:00:01)
  SPA = sender's IPv4         (192.0.2.10)
  THA = 00:00:00:00:00:00     (ZERO — this is the question!)
  TPA = target's IPv4         (192.0.2.1)

Conceptual: "Who has 192.0.2.1? Tell 192.0.2.10"
```

#### ARP Reply (unicast)

```
Ethernet header:
  DST: requester's MAC       (unicast — only the requester needs this)
  SRC: responder's MAC
  EtherType: 0x0806 (ARP)

ARP payload (28 bytes):
  OPER  = 2  (REPLY)

  SHA = responder's MAC       (02:00:00:00:00:fe)
  SPA = responder's IPv4      (192.0.2.1)
  THA = requester's MAC       (02:00:00:00:00:01 — filled in!)
  TPA = requester's IPv4      (192.0.2.10)

Conceptual: "192.0.2.1 is at 02:00:00:00:00:fe"
```

### ARP Packet Layout (28 bytes)

```
Offset  Size  Field
 0       2    HTYPE  — Hardware Type (Ethernet = 1)
 2       2    PTYPE  — Protocol Type (IPv4 = 0x0800)
 4       1    HLEN   — Hardware Address Length (MAC = 6)
 5       1    PLEN   — Protocol Address Length (IPv4 = 4)
 6       2    OPER   — Operation (REQUEST = 1, REPLY = 2)
 8       6    SHA    — Sender Hardware Address
14       4    SPA    — Sender Protocol Address
18       6    THA    — Target Hardware Address
24       4    TPA    — Target Protocol Address
```

### Ethernet II Frame

`ethernet_frame.py` demonstrates Ethernet II framing as an **educational model**
for understanding ARP encapsulation. Important caveats:

- The device interface is **wlan0 (Wi-Fi)**, not an Ethernet NIC.
- The actual 802.11 Wi-Fi MAC frame header is more complex than the simple
  14-byte Ethernet II header (it includes additional fields such as Frame
  Control, Duration, Sequence Control, and potentially 4 address fields).
- No raw 802.11 frame was captured. No monitor mode was used.
- No packet was transmitted by the offline encoder.
- ARP remains relevant to IPv4 address resolution on local IEEE 802 networks
  (including Wi-Fi) — the conceptual relationship is the same, even though
  the link-layer encapsulation differs.

```
+----------------------+ 6 bytes  Destination MAC
+----------------------+ 6 bytes  Source MAC
+----------------------+ 2 bytes  EtherType (0x0806 for ARP)
+----------------------+
| ARP Payload (28 B)   | 28–1500 bytes
+----------------------+
```

Our educational serializer emits: **14 (Ethernet II header) + 28 (ARP) = 42 bytes**.

This is the UNPADDED EDUCATIONAL ETHERNET-II HEADER + ARP PAYLOAD size. On a
real physical Ethernet link, a 28-byte ARP payload would require padding to
meet the minimum Ethernet frame size (64 bytes including FCS, or 60 bytes
without). We did NOT transmit or capture a real physical Ethernet frame, so
the actual on-wire frame length on this Android Wi-Fi interface is NOT VERIFIED.

### Key EtherType Values

| EtherType | Protocol |
|-----------|----------|
| `0x0800` | IPv4 |
| `0x0806` | ARP |
| `0x86DD` | IPv6 |

### Subnet Mathematics

An IPv4 address with CIDR notation (`10.122.172.202/16`) tells us:

- **/16** = the first 16 bits are the **network prefix**
- The remaining 16 bits are the **host identifier**
- All devices sharing the same network prefix are on the same subnet
- They can communicate directly at Layer 2 (via ARP)

```
  10       122      172      202
  00001010 01111010 10101100 11001010
  └─────── NETWORK ───────┘└─── HOST ────┘
  (16 bits)                (16 bits)

  Subnet mask:   255.255.0.0
  Network:       10.122.0.0
  Broadcast:     10.122.255.255
  Host range:    10.122.0.1 – 10.122.255.254
  Usable hosts:  65,534
```

### Routing Decision

Before ARP can even be attempted, the host must decide WHOSE MAC to ask for:

| Destination | Decision | ARP target |
|-------------|----------|------------|
| Same subnet (e.g., `10.122.10.50`) | Direct delivery | Destination's own MAC |
| Different subnet (e.g., `8.8.8.8`) | Via router | Next-hop gateway's MAC (PROTOCOL MODEL — actual gateway NOT VERIFIED) |

```
Same subnet:
  Host → ARP for 10.122.10.50 → MAC of 10.122.10.50 → direct frame

Different subnet:
  Host → ARP for gateway → MAC of gateway → frame to gateway
  Gateway → routes IP packet toward 8.8.8.8

**Note:** The actual gateway IP and MAC were NOT VERIFIED in this experiment.
The routing table was not observed. The behavior described is the PROTOCOL
MODEL — what a correctly configured IPv4 host WOULD do for an off-subnet
destination.
```

**Critical insight:** A host never ARPs for an off-subnet internet destination.
It ARPs for the LOCAL next-hop address (typically the default gateway) instead.
The actual gateway IP and MAC on this device were NOT VERIFIED.

### Why IPv6 Does Not Use ARP

IPv6 replaces ARP with **Neighbor Discovery Protocol (NDP)**, part of ICMPv6
(RFC 4861).

| | ARP (IPv4) | NDP (IPv6) |
|---|---|---|
| Delivery | Broadcast (every host processes) | Multicast (only interested hosts) |
| Protocol | Standalone (EtherType 0x0806) | Carried in ICMPv6 over IPv6 |
| Scope | Address resolution only | Address resolution + router discovery + prefix discovery + DAD |
| Security | No built-in authentication | Can use IPsec; Secure Neighbor Discovery (SEND) defined |

---

## 2. Terminology

| Term | Definition |
|------|------------|
| **MAC address** | 48-bit hardware identifier for a network interface. Usually written as `aa:bb:cc:dd:ee:ff`. |
| **IPv4 address** | 32-bit network-layer address. Usually written in dotted-decimal: `192.168.1.1`. |
| **CIDR** | Classless Inter-Domain Routing. `IP/prefix` notation: `10.0.0.1/24`. |
| **Subnet mask** | 32-bit value where `1` bits mark the network portion. `/24` = `255.255.255.0`. |
| **Network address** | The first address in a subnet (host bits all zero). Identifies the subnet itself. |
| **Broadcast address** | The last address in a subnet (host bits all one). Sent to all hosts on the subnet. |
| **Host address** | Any address between network and broadcast. Assigned to a device. |
| **ARP** | Address Resolution Protocol. Resolves IPv4 → MAC on a local link. |
| **ARP request** | Broadcast query: "Who has this IP address?" |
| **ARP reply** | Unicast answer: "I have this IP address. My MAC is X." |
| **ARP cache / neighbor table** | A table mapping known IP→MAC pairs, avoiding repeated ARP queries. |
| **Broadcast MAC** | `ff:ff:ff:ff:ff:ff` — received by all devices on the link. |
| **EtherType** | 2-byte field in the Ethernet header identifying the upper-layer protocol. |
| **Ethernet II frame** | The standard Ethernet frame format: 6B dst + 6B src + 2B type + payload. |
| **HTYPE** | Hardware type field in ARP. `1` = Ethernet. |
| **PTYPE** | Protocol type field in ARP. `0x0800` = IPv4. |
| **HLEN** | Hardware address length. `6` for MAC addresses. |
| **PLEN** | Protocol address length. `4` for IPv4 addresses. |
| **OPER** | ARP operation. `1` = REQUEST, `2` = REPLY. |
| **SHA** | Sender Hardware Address — the sender's MAC. |
| **SPA** | Sender Protocol Address — the sender's IPv4. |
| **THA** | Target Hardware Address. Zero in a REQUEST (unknown). |
| **TPA** | Target Protocol Address — the IPv4 being asked about. |
| **Default gateway** | The router that forwards packets to destinations outside the local subnet. |
| **NDP** | Neighbor Discovery Protocol — IPv6's replacement for ARP. |

---

## 3. Experiments

### Experiment A — Device Network State (READ-ONLY INSPECTION)

```bash
python src/arp_environment.py
```

Inspects `ifconfig`/`ip addr`, `ip neigh`, `arp -n`, and `/proc/net/arp`.
Reports each as AVAILABLE, BLOCKED, UNAVAILABLE, or EMPTY. No network probing.

### Experiment B — Subnet Mathematics (OFFLINE)

```bash
python src/subnet_math.py
```

Calculates subnet mask, network address, broadcast address, host range, and
binary decomposition from the local IPv4/CIDR (or historical fallback).

### Experiment C — Ethernet Frame Encoding (OFFLINE)

```bash
python src/ethernet_frame.py
```

Demonstrates MAC text↔bytes conversion, EtherType constants, Ethernet II header
construction and parsing. Verifies encode→decode round-trip.

### Experiment D — ARP Packet Construction (OFFLINE)

```bash
python src/arp_packet_demo.py
```

Builds ARP REQUEST and ARP REPLY using documentation-space addresses
(`192.0.2.0/24`, RFC 5737). Wraps them in Ethernet frames. Shows annotated
hexdumps. Verifies all encode→decode round-trips. **No network transmission.**

### Experiment E — Routing Decision Model (OFFLINE)

```bash
python src/resolution_model.py
```

Models the subnet membership check mathematically. Determines whether
`10.122.10.50` (same subnet) and `8.8.8.8` (different subnet) would trigger
direct ARP or gateway ARP. Includes IPv6 NDP comparison.

---

## 4. Source Files

| File | Purpose |
|------|---------|
| `arp_environment.py` | Safe local inspection of interfaces, MAC, ARP table, neighbor cache |
| `subnet_math.py` | CIDR calculations: mask, network, broadcast, binary decomposition |
| `ethernet_frame.py` | Educational Ethernet II frame encoder/decoder |
| `arp_packet.py` | ARP packet encoder/decoder (REQUEST + REPLY) |
| `arp_packet_demo.py` | Offline construction of full Ethernet+ARP frames with hexdumps |
| `resolution_model.py` | Offline model: routing decision → ARP target selection |

---

## 5. Android / Termux Notes

- All experiments are local/offline — no network transmission.
- `ip addr` and `ifconfig` may or may not be available; the scripts handle
  graceful degradation.
- `/proc/net/arp` is typically blocked by Android sandbox — this is a
  documented LIMITATION, not a bug.
- `arp -n` and `ip neigh` may be missing (no `net-tools` or `iproute2`).
- The previously observed wlan0 address (`10.122.172.202/16`) is used only
  as a labelled historical fallback if auto-detection fails.
- MAC address may be hidden (zeroed) by Android — this is a platform
  limitation, not an error.

---

## 6. Why This Matters for Security

ARP was designed in 1982 for a trusted local network. It has **no built-in
authentication** — any device on the link can claim to be any IP address.

This enables attack classes (conceptual — NOT implemented in this lab):

- **ARP spoofing** — an attacker sends forged ARP replies associating their
  MAC with someone else's IP (typically the gateway).
- **ARP poisoning** — the attacker fills the victim's ARP cache with false
  entries.
- **Man-in-the-Middle (MITM)** — by spoofing both sides of a conversation,
  the attacker can intercept and potentially modify traffic.

Defense concepts:

- **Network segmentation** — limit the blast radius of ARP attacks.
- **Static ARP entries** — manually configured IP→MAC mappings (not scalable).
- **Dynamic ARP Inspection (DAI)** — switches validate ARP packets against
  DHCP snooping databases.
- **DHCP Snooping** — switches track which IPs are assigned to which ports.
- **TLS / encryption** — even if ARP is compromised, end-to-end encryption
  protects data confidentiality.
- **ARP monitoring** — detect anomalous ARP changes (e.g., gateway MAC
  suddenly changing).

---

## 7. Observation

Record your observations in `observations.md`. The file contains the actual
results from executing all five experiments on this device.

---

## 8. Conclusion

After completing this lab, you should be able to:

1. **Explain why IP alone is insufficient** on shared-medium networks — you
   need a link-layer address (MAC) for actual frame delivery.
2. **Describe the ARP request/reply exchange** — broadcast request (who has
   this IP?), unicast reply (I have it, my MAC is X).
3. **Encode and decode ARP packets by hand** — 28 bytes: 8-byte fixed header
   + 20 bytes of addresses.
4. **Distinguish ARP from DNS** — ARP translates local IP→MAC; DNS translates
   domain name→IP. Different layers, different scopes.
5. **Calculate subnet properties** from CIDR notation — subnet mask, network
   address, broadcast address, binary decomposition.
6. **Explain the routing decision** — same-subnet destinations get direct ARP;
   off-subnet destinations go through the default gateway.
7. **Understand why ARP has no authentication** — it was designed for trusted
   local networks in 1982. This has security implications.
8. **Know why IPv6 abandoned ARP** — replaced by NDP (ICMPv6), which uses
   multicast instead of broadcast and combines multiple functions.

---

## 9. Exercises

> These are for self-assessment. Determine the answers by running the
> experiments and inspecting the code — not by looking them up.

1. What problem does ARP solve? Why can't a host send an IP packet directly
   over Ethernet without knowing the destination MAC address?

2. What is the difference between an IPv4 address and a MAC address? Which
   OSI layers do they belong to conceptually?

3. Why is an ARP request normally sent to the broadcast MAC address
   (`ff:ff:ff:ff:ff:ff`)? What would happen if it were sent to a specific
   unicast MAC?

4. Why is an ARP reply normally sent as a unicast? Who needs the information
   it contains?

5. What does EtherType `0x0806` mean? What does EtherType `0x0800` mean? Why
   are they necessary in an Ethernet frame?

6. Why is THA set to `00:00:00:00:00:00` in an ARP request? What would happen
   if it were filled with a wrong MAC address?

7. What does `OPER=1` mean? What does `OPER=2` mean? Where exactly in the
   ARP packet is the OPER field located?

8. For a `/16` prefix, how many bits belong to the network portion? How many
   usable host addresses exist in the subnet? Show your calculation.

9. If a host at `10.122.172.202/16` wants to reach `8.8.8.8`, why would it
   NOT send an ARP request for `8.8.8.8`? Whose MAC address does it actually
   need?

10. What is the relationship between ARP and a routing decision? Which comes
    first — the routing decision or the ARP query?

11. An ARP request is 28 bytes. An ARP reply is also 28 bytes. Why are they
    the same size even though the reply contains "more information"?

12. Why does IPv6 not use ARP? What protocol replaces it, and what advantages
    does the replacement offer?

13. Why can ARP spoofing exist conceptually? What property (or lack of
    property) in the ARP protocol design allows it?

14. Why does TLS still matter even on a compromised local network where ARP
    spoofing is possible?

15. If `/proc/net/arp` returns a permission error on Android, does that mean
    the ARP cache is empty? Explain the distinction between BLOCKED and EMPTY.

16. What Android/Termux limitations did our experiments reveal about:
    - MAC address visibility?
    - ARP/neighbor table access?
    - Available networking tools?

17. On `10.122.172.202/16`, is `10.122.255.255` a valid host address? Why or
    why not?

18. What is the exact byte length of an Ethernet II frame carrying an ARP
    packet? Break it down: what contributes to the 42 bytes?

---

## References

- RFC 826 — An Ethernet Address Resolution Protocol (ARP)
- RFC 894 — A Standard for the Transmission of IP Datagrams over Ethernet Networks
- RFC 4861 — Neighbor Discovery for IP version 6 (IPv6)
- RFC 5737 — IPv4 Address Blocks Reserved for Documentation
- RFC 4632 — Classless Inter-domain Routing (CIDR)
- RFC 5227 — IPv4 Address Conflict Detection
- `man 7 arp` — Linux ARP kernel module documentation
