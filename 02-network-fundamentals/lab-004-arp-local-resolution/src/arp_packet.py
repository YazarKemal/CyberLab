#!/usr/bin/env python3
"""
LAB-004: ARP Packet Encoder/Decoder
====================================

Manually encode/decode ARP packets for Ethernet + IPv4.

ARP message layout (RFC 826):

Offset  Size  Field
 0       2    HTYPE  — Hardware Type (Ethernet = 1)
 2       2    PTYPE  — Protocol Type (IPv4 = 0x0800)
 4       1    HLEN   — Hardware Address Length (MAC = 6)
 5       1    PLEN   — Protocol Address Length (IPv4 = 4)
 6       2    OPER   — Operation (REQUEST=1, REPLY=2)
 8       6    SHA    — Sender Hardware Address
14       4    SPA    — Sender Protocol Address
18       6    THA    — Target Hardware Address
24       4    TPA    — Target Protocol Address
Total: 28 bytes

Usage:
  python src/arp_packet.py
"""

import struct
import sys
import os

# Add parent src dir to path so arp_packet_demo can import us,
# and we can optionally use ethernet_frame for wrapping.

sys.path.insert(0, os.path.dirname(__file__))

# ── Constants ──────────────────────────────────────────────────────────────
HTYPE_ETHERNET = 1
PTYPE_IPV4 = 0x0800
HLEN_ETHER = 6
PLEN_IPV4 = 4

OPER_REQUEST = 1
OPER_REPLY   = 2

OPER_NAMES = {OPER_REQUEST: "REQUEST", OPER_REPLY: "REPLY"}

ARP_PACKET_SIZE = 28  # total ARP payload for Ethernet+IPv4

# ── Address conversion ─────────────────────────────────────────────────────

def ip_to_bytes(ip: str) -> bytes:
    """Convert '192.0.2.10' → b'\\xc0\\x00\\x02\\x0a'."""
    parts = ip.split(".")
    if len(parts) != 4:
        raise ValueError(f"Expected 4 octets, got {len(parts)}: {ip!r}")
    return bytes(int(p) for p in parts)


def bytes_to_ip(data: bytes, offset: int = 0) -> str:
    """Convert b'\\xc0\\x00\\x02\\x0a' → '192.0.2.10'."""
    return ".".join(str(b) for b in data[offset:offset + 4])


def mac_to_bytes(mac: str) -> bytes:
    """Convert 'aa:bb:cc:dd:ee:ff' → b'\\xaa\\xbb\\xcc\\xdd\\xee\\xff'."""
    if ":" in mac:
        parts = mac.split(":")
    elif "-" in mac:
        parts = mac.split("-")
    else:
        raise ValueError(f"Unrecognized MAC format: {mac!r}")
    if len(parts) != 6:
        raise ValueError(f"MAC must have 6 octets, got {len(parts)}: {mac!r}")
    return bytes(int(h, 16) for h in parts)


def bytes_to_mac(data: bytes, offset: int = 0) -> str:
    """Convert 6 bytes → 'aa:bb:cc:dd:ee:ff'."""
    return ":".join(f"{b:02x}" for b in data[offset:offset + 6])


# ── ARP Packet Build/Parse ─────────────────────────────────────────────────
# ARP format string for struct: "!HHBBH" = 2+2+1+1+2 = 8 bytes fixed header
# Followed by 6(SHA)+4(SPA)+6(THA)+4(TPA) = 20 bytes of addresses
_ARP_FIXED = "!HHBBH"  # HTYPE, PTYPE, HLEN, PLEN, OPER


def build_arp(
    oper: int,
    sha: str,
    spa: str,
    tha: str,
    tpa: str,
    *,
    htype: int = HTYPE_ETHERNET,
    ptype: int = PTYPE_IPV4,
    hlen: int = HLEN_ETHER,
    plen: int = PLEN_IPV4,
) -> bytes:
    """
    Build an ARP packet (28 bytes for Ethernet + IPv4).

    Args:
        oper: OPER_REQUEST (1) or OPER_REPLY (2)
        sha:  Sender Hardware Address (MAC, e.g. '02:00:00:00:00:01')
        spa:  Sender Protocol Address (IPv4, e.g. '192.0.2.10')
        tha:  Target Hardware Address (MAC, zero for REQUEST)
        tpa:  Target Protocol Address (IPv4)

    Returns:
        28 bytes of ARP packet.
    """
    fixed = struct.pack(_ARP_FIXED, htype, ptype, hlen, plen, oper)
    sha_b = mac_to_bytes(sha)
    spa_b = ip_to_bytes(spa)
    tha_b = mac_to_bytes(tha)
    tpa_b = ip_to_bytes(tpa)
    return fixed + sha_b + spa_b + tha_b + tpa_b


def parse_arp(data: bytes, offset: int = 0) -> dict:
    """
    Parse a 28-byte ARP packet.

    Returns a dict with all fields decoded into human-readable values.
    """
    if len(data) < offset + ARP_PACKET_SIZE:
        raise ValueError(
            f"Data too short for ARP packet: "
            f"{len(data)} bytes at offset {offset}, need {ARP_PACKET_SIZE}"
        )

    htype, ptype, hlen, plen, oper = struct.unpack(
        _ARP_FIXED, data[offset:offset + 8]
    )

    sha = bytes_to_mac(data, offset + 8)
    spa = bytes_to_ip(data, offset + 14)
    tha = bytes_to_mac(data, offset + 18)
    tpa = bytes_to_ip(data, offset + 24)

    return {
        "htype": htype,
        "htype_name": "Ethernet" if htype == HTYPE_ETHERNET else f"Unknown({htype})",
        "ptype": ptype,
        "ptype_name": "IPv4" if ptype == PTYPE_IPV4 else f"0x{ptype:04x}",
        "hlen": hlen,
        "plen": plen,
        "oper": oper,
        "oper_name": OPER_NAMES.get(oper, f"Unknown({oper})"),
        "sha": sha,
        "spa": spa,
        "tha": tha,
        "tpa": tpa,
        "_next_offset": offset + ARP_PACKET_SIZE,
    }


def build_arp_request(sha: str, spa: str, tpa: str) -> bytes:
    """
    Build an ARP REQUEST packet.

    THA is set to 00:00:00:00:00:00 (unknown — the question being asked).
    """
    return build_arp(OPER_REQUEST, sha, spa, "00:00:00:00:00:00", tpa)


def build_arp_reply(sha: str, spa: str, tha: str, tpa: str) -> bytes:
    """
    Build an ARP REPLY packet.

    SHA/SPA = the responder (who has this IP)
    THA/TPA = the requester (who asked the question)
    """
    return build_arp(OPER_REPLY, sha, spa, tha, tpa)


def arp_hexdump(data: bytes, title: str = "ARP Packet") -> str:
    """Hex dump with ARP field annotations."""
    lines = []
    lines.append(f"  {title} ({len(data)} bytes)")
    lines.append(f"  {'Offset':<8} {'Hex':<49} {'Field'}")
    lines.append(f"  {'-'*8} {'-'*49} {'-'*30}")

    annotations = {
        0:  "HTYPE (Hardware Type)",
        2:  "PTYPE (Protocol Type)",
        4:  "HLEN (HW addr length)",
        5:  "PLEN (Proto addr length)",
        6:  "OPER (Operation)",
        8:  "SHA (Sender HW Address)",
        14: "SPA (Sender Proto Address)",
        18: "THA (Target HW Address)",
        24: "TPA (Target Proto Address)",
    }

    i = 0
    while i < len(data):
        chunk = data[i:i + 16]
        hex_str = ""
        for j, b in enumerate(chunk):
            if j == 8:
                hex_str += " "
            hex_str += f"{b:02x} "

        field = ""
        if i in annotations:
            field = "← " + annotations[i]
        elif i == 28:
            field = "← (ARP packet ends at byte 28)"

        lines.append(f"  {i:08x}  {hex_str:<49s} {field}")
        i += 16

    return "\n".join(lines)


def main() -> None:
    print("=" * 64)
    print("  LAB-004: ARP Packet Encoder/Decoder")
    print("=" * 64)
    print()

    # ── Constants ──────────────────────────────────────────────────────
    print("─" * 64)
    print("  1. ARP Constants")
    print("─" * 64)
    print()
    print(f"  HTYPE Ethernet:  {HTYPE_ETHERNET}")
    print(f"  PTYPE IPv4:      0x{PTYPE_IPV4:04x}")
    print(f"  HLEN (MAC):      {HLEN_ETHER} bytes")
    print(f"  PLEN (IPv4):     {PLEN_IPV4} bytes")
    print(f"  OPER REQUEST:    {OPER_REQUEST}")
    print(f"  OPER REPLY:      {OPER_REPLY}")
    print(f"  Total ARP size:  {ARP_PACKET_SIZE} bytes (8 fixed + 6+4+6+4)")

    # ── ARP Request ────────────────────────────────────────────────────
    print()
    print("─" * 64)
    print("  2. ARP REQUEST — Build & Parse")
    print("─" * 64)
    print()

    request = build_arp_request(
        sha="02:00:00:00:00:01",
        spa="192.0.2.10",
        tpa="192.0.2.1",
    )

    print(f"  Conceptual: Who has 192.0.2.1? Tell 192.0.2.10")
    print(f"  Packet size: {len(request)} bytes")
    print()
    print(arp_hexdump(request, "ARP REQUEST Packet"))

    # Parse back
    print()
    req_parsed = parse_arp(request)
    print(f"  Parsed:")
    print(f"    HTYPE: {req_parsed['htype']} ({req_parsed['htype_name']})")
    print(f"    PTYPE: 0x{req_parsed['ptype']:04x} ({req_parsed['ptype_name']})")
    print(f"    HLEN:  {req_parsed['hlen']}")
    print(f"    PLEN:  {req_parsed['plen']}")
    print(f"    OPER:  {req_parsed['oper']} ({req_parsed['oper_name']})")
    print(f"    SHA:   {req_parsed['sha']}  ← sender's MAC")
    print(f"    SPA:   {req_parsed['spa']}  ← sender's IP")
    print(f"    THA:   {req_parsed['tha']}  ← zero (unknown)")
    print(f"    TPA:   {req_parsed['tpa']}  ← target IP being asked about")

    # Verify
    ok = all([
        req_parsed["oper"] == OPER_REQUEST,
        req_parsed["sha"] == "02:00:00:00:00:01",
        req_parsed["spa"] == "192.0.2.10",
        req_parsed["tha"] == "00:00:00:00:00:00",
        req_parsed["tpa"] == "192.0.2.1",
    ])
    print()
    print(f"  Request round-trip verification: {'✓ ALL MATCH' if ok else '✗ MISMATCH'}")

    # ── ARP Reply ──────────────────────────────────────────────────────
    print()
    print("─" * 64)
    print("  3. ARP REPLY — Build & Parse")
    print("─" * 64)
    print()

    reply = build_arp_reply(
        sha="02:00:00:00:00:fe",
        spa="192.0.2.1",
        tha="02:00:00:00:00:01",
        tpa="192.0.2.10",
    )

    print(f"  Conceptual: 192.0.2.1 is at 02:00:00:00:00:fe")
    print(f"  Packet size: {len(reply)} bytes")
    print()
    print(arp_hexdump(reply, "ARP REPLY Packet"))

    # Parse back
    print()
    rep_parsed = parse_arp(reply)
    print(f"  Parsed:")
    print(f"    OPER:  {rep_parsed['oper']} ({rep_parsed['oper_name']})")
    print(f"    SHA:   {rep_parsed['sha']}  ← responder's MAC")
    print(f"    SPA:   {rep_parsed['spa']}  ← responder's IP")
    print(f"    THA:   {rep_parsed['tha']}  ← requester's MAC")
    print(f"    TPA:   {rep_parsed['tpa']}  ← requester's IP")

    ok = all([
        rep_parsed["oper"] == OPER_REPLY,
        rep_parsed["sha"] == "02:00:00:00:00:fe",
        rep_parsed["spa"] == "192.0.2.1",
        rep_parsed["tha"] == "02:00:00:00:00:01",
        rep_parsed["tpa"] == "192.0.2.10",
    ])
    print()
    print(f"  Reply round-trip verification: {'✓ ALL MATCH' if ok else '✗ MISMATCH'}")

    # ── Request vs Reply Comparison ────────────────────────────────────
    print()
    print("─" * 64)
    print("  4. Request vs Reply — Key Differences")
    print("─" * 64)
    print()
    print(f"  {'Field':<6} {'REQUEST':<25} {'REPLY':<25}")
    print(f"  {'-'*6} {'-'*25} {'-'*25}")
    print(f"  {'OPER':<6} {req_parsed['oper_name']:<25} {rep_parsed['oper_name']:<25}")
    print(f"  {'SHA':<6}  {req_parsed['sha']:<25} {rep_parsed['sha']:<25}")
    print(f"  {'SPA':<6}  {req_parsed['spa']:<25} {rep_parsed['spa']:<25}")
    print(f"  {'THA':<6}  {req_parsed['tha']:<25} {rep_parsed['tha']:<25}")
    print(f"  {'TPA':<6}  {req_parsed['tpa']:<25} {rep_parsed['tpa']:<25}")
    print()
    print("  Request THA = 00:00:00:00:00:00 (unknown — the question)")
    print("  Reply THA   = requester's actual MAC (the answer)")

    print()
    print("=" * 64)
    print("  ARP encoder/decoder ready.")
    print("=" * 64)


if __name__ == "__main__":
    main()
