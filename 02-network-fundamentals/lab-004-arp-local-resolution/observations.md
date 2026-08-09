# LAB-004 Observations

## Environment

| Property | Value |
|----------|-------|
| Device | Android tablet |
| OS | Linux 6.1.145-android14-11 (aarch64) |
| Platform | Termux |
| Python | 3.x (standard library) |
| Date | 2026-08-09 |
| Network | wlan0, 10.122.172.202/16 |

## Current Interface State

VERIFIED via `ifconfig`:

```
lo: flags=73<UP,LOOPBACK,RUNNING>  mtu 65536
    inet 127.0.0.1  netmask 255.0.0.0

wlan0: flags=4163<UP,BROADCAST,RUNNING,MULTICAST>  mtu 1500
    inet 10.122.172.202  netmask 255.255.0.0  broadcast 10.122.255.255
```

Two interfaces visible: `lo` (loopback) and `wlan0` (Wi-Fi). Both are UP.

## IPv4 Address

| Property | Value | Status |
|----------|-------|--------|
| Interface | wlan0 | VERIFIED |
| IPv4 address | 10.122.172.202 | VERIFIED (via ifconfig, 2026-08-09) |
| Netmask | 255.255.0.0 | VERIFIED |
| CIDR prefix | /16 | VERIFIED |
| Broadcast | 10.122.255.255 | VERIFIED |
| Previous LAB-001 value | 10.122.172.202/16 | Confirmed unchanged |

The address matches the historical LAB-001 observation. However, we
re-verified it today rather than assuming it was unchanged.

## MAC Visibility

| Property | Value | Status |
|----------|-------|--------|
| wlan0 MAC | 00:00:00:00:00:00:00:00:00:00:00:00:00:00:00:00 | LIMITATION |

Android reports an unusable hardware-address representation via `ifconfig` (shown
as `unspec` rather than `ether`, with all-zero bytes). **Verdict:** MAC visibility: VERIFIED that `ifconfig` exposed wlan0 with an
unusable/zeroed hardware-address representation. LIMITATION: the real
interface MAC address was not available to this Termux context.

## ARP / Neighbor Table Visibility

| Method | Status | Details |
|--------|--------|---------|
| `ip neigh` | UNAVAILABLE | `ip` executable not found on PATH |
| `arp -n` | BLOCKED | Permission denied accessing `/proc/net/arp` |
| `/proc/net/arp` | UNAVAILABLE | File does not exist on this system |

### ip neigh

The `ip` command (from iproute2) is not installed. This is expected on a
minimal Termux installation.

**Verdict:** ip neigh: UNAVAILABLE (tool not installed).

### arp -n

The `arp` command exists but fails with a permission error when trying to
read `/proc/net/arp`. This is an Android sandbox restriction — even though
the `arp` binary is present, it cannot access the kernel's ARP table.

**Verdict:** arp -n: BLOCKED (Android sandbox — Permission denied on
`/proc/net/arp`).

### /proc/net/arp

The file `/proc/net/arp` does not exist on this system.

**Verdict:** /proc/net/arp: UNAVAILABLE (path does not exist).

### Important distinction

We do NOT claim "the ARP cache is empty." The ARP cache content is NOT
VERIFIED. The Android sandbox prevents any observation of the kernel's
ARP table through the methods we tried.

This is a qualitatively different statement from "there are no ARP entries."
EMPTY means the table was readable and contained no entries. We never reached
that state — the table was never readable.

## Android / Termux Restrictions

| Restriction | Method affected | Type |
|-------------|----------------|------|
| MAC address unavailable (zeroed representation) | `ifconfig` wlan0 | LIMITATION |
| `/proc/net/arp` missing | `arp -n`, direct read | LIMITATION |
| `ip` (iproute2) not installed | `ip neigh` | UNAVAILABLE |
| `ifconfig wlan0` restricted | Per-interface query | LIMITATION |
| `ifconfig` (no args) works | Interface discovery | AVAILABLE |
| `/proc/net/dev` blocked | Interface statistics | LIMITATION |

Key finding: `ifconfig wlan0` fails because it tries to read `/proc/net/dev`
(blocked by Android), but `ifconfig` without arguments succeeds and shows
full wlan0 details. This is a useful discovery for future labs.

## Subnet Calculation

VERIFIED — auto-detected from current wlan0 state:

| Property | Value |
|----------|-------|
| Input | 10.122.172.202/16 |
| Source | AUTO-DETECTED (wlan0) — VERIFIED |
| Subnet mask | 255.255.0.0 |
| Network address | 10.122.0.0 |
| Broadcast | 10.122.255.255 |
| Host range | 10.122.0.1 – 10.122.255.254 |
| Usable hosts | 65,534 |
| Is host address? | True (not network, not broadcast) |

### Binary decomposition

```
Address:  00001010 01111010 10101100 11001010
Mask:     11111111 11111111 00000000 00000000

NETWORK bits (first 16):  00001010 01111010
HOST bits (last 16):      10101100 11001010
```

### Octet breakdown

| Octet | Address | Mask | Network | Broadcast |
|-------|---------|------|---------|-----------|
| 1 | 10 | 255 | 10 | 10 |
| 2 | 122 | 255 | 122 | 122 |
| 3 | 172 | 0 | 0 | 255 |
| 4 | 202 | 0 | 0 | 255 |

## Ethernet Frame Encoding

Note: The device interface is **wlan0 (Wi-Fi)**. `ethernet_frame.py` demonstrates
Ethernet II framing as an educational model. The actual 802.11 Wi-Fi MAC frame
header is more complex than a simple 14-byte Ethernet II header. No raw 802.11
frame was captured. No monitor mode was used. No packet was transmitted by the
offline encoder. ARP remains relevant to IPv4 address resolution on local IEEE
802 networks — the conceptual relationship is the same even though the link-layer
encapsulation differs.

VERIFIED — all MAC conversions round-trip correctly:

| Input MAC | Bytes (hex) | Round-trip |
|-----------|------------|------------|
| `aa:bb:cc:dd:ee:ff` | `aabbccddeeff` | ✓ |
| `02:00:00:00:00:01` | `020000000001` | ✓ |
| `ff:ff:ff:ff:ff:ff` | `ffffffffffff` | ✓ |
| `00:00:00:00:00:00` | `000000000000` | ✓ |
| `02:00:00:00:00:fe` | `0200000000fe` | ✓ |

## EtherType

| Protocol | Value | Bytes |
|----------|-------|-------|
| IPv4 | 0x0800 | `08 00` |
| ARP | 0x0806 | `08 06` |
| IPv6 | 0x86DD | `86 dd` |

VERIFIED via `struct.pack("!H", ...)`.

## Ethernet Header

- Header size: 14 bytes (6 dst + 6 src + 2 EtherType) ✓
- Construction and parse round-trip: ✓ (dst_mac, src_mac, ethertype all match)
- Full frame with 28-byte ARP payload: 42 bytes (unpadded educational serialization) ✓

Note: On a real physical Ethernet link, a 28-byte ARP payload requires
padding to meet minimum frame size requirements (64 bytes including FCS).
Actual on-wire frame length on this Wi-Fi interface: NOT VERIFIED.

## ARP Constants

| Constant | Value | Status |
|----------|-------|--------|
| HTYPE (Ethernet) | 1 | ✓ |
| PTYPE (IPv4) | 0x0800 | ✓ |
| HLEN (MAC bytes) | 6 | ✓ |
| PLEN (IPv4 bytes) | 4 | ✓ |
| OPER REQUEST | 1 | ✓ |
| OPER REPLY | 2 | ✓ |
| ARP packet size | 28 bytes | ✓ |

## ARP Request

VERIFIED — offline construction with documentation-space addresses
(192.0.2.0/24, RFC 5737):

| Field | Value | Status |
|-------|-------|--------|
| Sender MAC (SHA) | 02:00:00:00:00:01 | VERIFIED |
| Sender IPv4 (SPA) | 192.0.2.10 | VERIFIED |
| Target MAC (THA) | 00:00:00:00:00:00 | VERIFIED (zero — the question) |
| Target IPv4 (TPA) | 192.0.2.1 | VERIFIED |
| OPER | 1 (REQUEST) | VERIFIED |
| ARP packet size | 28 bytes | VERIFIED |
| Ethernet DST | ff:ff:ff:ff:ff:ff | VERIFIED (broadcast) |
| Ethernet+ARP frame | 42 bytes (unpadded educational serialization) | VERIFIED |

Round-trip encode→decode: ALL FIELDS VERIFIED ✓

## ARP Reply

VERIFIED — offline construction:

| Field | Value | Status |
|-------|-------|--------|
| Responder MAC (SHA) | 02:00:00:00:00:fe | VERIFIED |
| Responder IPv4 (SPA) | 192.0.2.1 | VERIFIED |
| Requester MAC (THA) | 02:00:00:00:00:01 | VERIFIED (known — the answer) |
| Requester IPv4 (TPA) | 192.0.2.10 | VERIFIED |
| OPER | 2 (REPLY) | VERIFIED |
| ARP packet size | 28 bytes | VERIFIED |
| Ethernet DST | 02:00:00:00:00:01 | VERIFIED (unicast to requester) |
| Ethernet+ARP frame | 42 bytes (unpadded educational serialization) | VERIFIED |

Round-trip encode→decode: ALL FIELDS VERIFIED ✓

## Request vs Reply Comparison

| Field | REQUEST | REPLY |
|-------|---------|-------|
| Ethernet destination | ff:ff:ff:ff:ff:ff | 02:00:00:00:00:01 |
| ARP OPER | REQUEST (1) | REPLY (2) |
| SHA | 02:00:00:00:00:01 | 02:00:00:00:00:fe |
| SPA | 192.0.2.10 | 192.0.2.1 |
| THA | 00:00:00:00:00:00 | 02:00:00:00:00:01 |
| TPA | 192.0.2.1 | 192.0.2.10 |

Key: THA is zero in REQUEST (unknown), filled in REPLY. REQUEST is broadcast,
REPLY is unicast.

## Packet Hexdump (ARP REQUEST wrapped in Ethernet)

```
Offset   Hex                                               Interpretation
-------- ------------------------------------------------- ----------------------------------------
00000000  ff ff ff ff ff ff 02 00  00 00 00 01 08 06 00 01  ← Ethernet DST = ff:ff:ff:ff:ff:ff (BROADCAST)
00000010  08 00 06 04 00 01 02 00  00 00 00 01 c0 00 02 0a  ← PTYPE = 0x0800 (IPv4)
00000020  00 00 00 00 00 00 c0 00  02 01                    ← THA = 00:00:00:00:00:00
```

Total: 42 bytes (unpadded educational Ethernet-II header + ARP payload). VERIFIED for our serializer. Actual on-wire frame length: NOT VERIFIED.

## Encode / Decode Verification

All encode→decode round-trips verified:

| Component | Verification | Status |
|-----------|-------------|--------|
| MAC text ↔ bytes (5 MACs) | All round-trip ✓ | PASS |
| Ethernet header (build → parse) | dst, src, EtherType all match | PASS |
| Ethernet frame (build → parse) | Payload preserved | PASS |
| ARP REQUEST (build → parse) | All 6 fields verified | PASS |
| ARP REPLY (build → parse) | All 6 fields verified | PASS |
| ARP REQUEST via dns_packet_demo | Full annotated hexdump matched | PASS |
| ARP REPLY via dns_packet_demo | Full annotated hexdump matched | PASS |

## Local vs Remote Resolution Model

VERIFIED — offline mathematical model, no actual traffic:

### Case A: 10.122.10.50 (same subnet)

| Check | Result |
|-------|--------|
| Subnet membership | ✓ 10.122.10.50 IS inside 10.122.0.0/16 |
| Decision | SAME SUBNET |
| ARP target | 10.122.10.50 itself |
| Layer-2 delivery | Direct, no router needed |

Mathematical verification:
```
10.122.10.50 & 255.255.0.0 = 10.122.0.0
Network & mask            = 10.122.0.0
Match → SAME SUBNET ✓
```

### Case B: 8.8.8.8 (off-subnet)

| Check | Result |
|-------|--------|
| Subnet membership | ✗ 8.8.8.8 is NOT inside 10.122.0.0/16 |
| Decision | OFF-SUBNET — requires router/gateway (PROTOCOL MODEL) |
| ARP target | Next-hop gateway's local address (not 8.8.8.8!) |
| Actual gateway IP | NOT VERIFIED |
| Actual gateway MAC | NOT VERIFIED |
| Layer-2 delivery | Via gateway MAC (INFERRED — route table not observed) |

Mathematical verification:
```
8.8.8.8 & 255.255.0.0  = 8.8.0.0
Network & mask          = 10.122.0.0
Mismatch → DIFFERENT SUBNET ✓
```

Routing classification: VERIFIED OFFLINE (math). Next-hop gateway ARP behavior:
PROTOCOL MODEL / INFERRED. A host never ARPs for an off-subnet internet
destination — it ARPs for the LOCAL next-hop address. The actual gateway IP
and MAC on this device were NOT VERIFIED (routing table not observed).

## Security Implications

### Why ARP has no authentication

ARP was designed in 1982 (RFC 826) for trusted local networks. The protocol
has no mechanism to verify that a sender is authorized to claim an IP→MAC
mapping. Any device on the local link can send an ARP reply claiming to be
any IP address.

### Attack classes (conceptual — NOT implemented)

| Attack | Mechanism |
|--------|-----------|
| ARP spoofing | Attacker sends forged ARP replies claiming to be the gateway |
| ARP poisoning | Attacker fills victim's cache with false IP→MAC mappings |
| MITM | Attacker intercepts traffic between two hosts by spoofing both |

### Defense concepts

- **Network segmentation** — limit broadcast domain size (VLANs)
- **Static ARP** — manually configured entries (not scalable)
- **Dynamic ARP Inspection (DAI)** — switch validates ARP against DHCP snooping
- **DHCP Snooping** — switch tracks legitimate IP→port bindings
- **TLS/encryption** — protects data confidentiality even if ARP is compromised
- **ARP monitoring** — detect anomalous MAC changes (e.g., arpwatch)

### IPv6 NDP comparison

IPv6's NDP (RFC 4861) addresses some of ARP's limitations:
- Uses multicast instead of broadcast (fewer hosts disturbed)
- Can leverage IPsec for authentication
- Combines address resolution, router discovery, and prefix discovery

However, NDP without SEND (Secure Neighbor Discovery) still lacks strong
authentication in practice.

## Unexpected Results

1. **`ifconfig wlan0` fails but `ifconfig` (no args) works.** Caused by
   `/proc/net/dev` being blocked by Android. The per-interface query tries to
   read device statistics and is denied, while the global query reads from a
   different source. This required adding a third auto-detection method
   (parse wlan0 block from full `ifconfig` output).

2. **`arp -n` reports "Permission denied" but `/proc/net/arp` doesn't exist.**
   The `arp` command likely tries to access ARP information through a kernel
   interface other than the `/proc/net/arp` file directly. The permission
   error comes from the Android sandbox blocking that access path.

3. **MAC address shown as `unspec` with 16 zero bytes.** Android reports
   `unspec` (unspecified) instead of `ether` (Ethernet) for wlan0, with the
   hardware address zeroed. This is an intentional Android privacy feature.

## Theory vs Observation

| Theoretical claim | Observation | Status |
|-------------------|-------------|--------|
| IPv4 address on wlan0 | 10.122.172.202 | VERIFIED |
| Subnet mask /16 | 255.255.0.0 | VERIFIED |
| MAC address visible via ifconfig | Zeroed by Android | LIMITATION |
| ARP cache readable via arp -n | Permission denied | BLOCKED |
| ARP cache readable via /proc/net/arp | File does not exist | UNAVAILABLE |
| ip neigh available | ip not installed | UNAVAILABLE |
| ARP packet is 28 bytes | 28 bytes | VERIFIED |
| ARP REQUEST THA = 00:00:00:00:00:00 | Zero | VERIFIED |
| ARP REQUEST is broadcast | ff:ff:ff:ff:ff:ff | VERIFIED |
| ARP REPLY is unicast | Requester's MAC | VERIFIED |
| Ethernet+ARP frame is 42 bytes | 42 (14 + 28) | VERIFIED |
| EtherType ARP = 0x0806 | 0x0806 | VERIFIED |
| EtherType IPv4 = 0x0800 | 0x0800 | VERIFIED |
| Same subnet → direct ARP | 10.122.10.50 in 10.122.0.0/16 | VERIFIED OFFLINE |
| Off-subnet → ARP for next-hop | 8.8.8.8 not in 10.122.0.0/16 | PROTOCOL MODEL / INFERRED |
| Actual gateway IP | Not observed | NOT VERIFIED |
| Actual gateway MAC | Not observed | NOT VERIFIED |
| MAC text ↔ bytes round-trip | All 5 test MACs verified | VERIFIED |
| ARP encode → decode | All fields for REQUEST and REPLY | VERIFIED |
| Encode → decode is idempotent | Full round-trip for all components | VERIFIED |

## Conclusion

LAB-004 successfully demonstrated the ARP protocol's structure, encoding, and
conceptual operation through offline construction and analysis. Key findings:

1. **Current wlan0 state confirmed**: 10.122.172.202/16 — same as LAB-001
   but independently re-verified.

2. **ARP packet structure understood**: 28 bytes, 8 fixed + 20 addresses.
   REQUEST (THA=zero, broadcast Ethernet) vs REPLY (THA=filled, unicast).

3. **Android severely limits ARP observability**: MAC zeroed, ARP table
   inaccessible, iproute2 not installed. These are platform LIMITATIONS,
   not experimental failures.

4. **Subnet math is deterministic**: /16 means 16 network bits, 16 host bits,
   65,534 usable addresses in 10.122.0.0/16.

5. **Routing decision is mathematical**: subnet membership check via
   `(dest_IP & mask) == (network & mask)` determines whether ARP targets
   the destination directly or the gateway.

6. **ARP's lack of authentication** (1982 design) enables local-network
   attacks — but encryption (TLS) and network segmentation provide defense
   in depth.

This lab did NOT transmit any frames, scan any hosts, or perform any ARP
spoofing. All experiments were offline or read-only local inspection.
