#!/usr/bin/env python3
"""
LAB-004: Ethernet II Frame Encoder/Decoder
===========================================

Educational implementation of Ethernet II frame structure.

Frame layout (RFC 894):

+----------------------+ 6 bytes
| Destination MAC      |
+----------------------+ 6 bytes
| Source MAC           |
+----------------------+ 2 bytes
| EtherType            |
+----------------------+
| Payload              | 46–1500 bytes
+----------------------+

Key EtherType values:
  0x0800  IPv4
  0x0806  ARP
  0x86DD  IPv6

Usage:
  python src/ethernet_frame.py
"""

import struct
import sys


# ── EtherType constants ────────────────────────────────────────────────────
ETHERTYPE_IPV4 = 0x0800
ETHERTYPE_ARP  = 0x0806
ETHERTYPE_IPV6 = 0x86DD

ETHERTYPE_NAMES = {
    ETHERTYPE_IPV4: "IPv4",
    ETHERTYPE_ARP:  "ARP",
    ETHERTYPE_IPV6: "IPv6",
}

# ── MAC address helpers ────────────────────────────────────────────────────
BROADCAST_MAC = "ff:ff:ff:ff:ff:ff"
ZERO_MAC = "00:00:00:00:00:00"

HEADER_SIZE = 14  # 6 + 6 + 2


def mac_to_bytes(mac: str) -> bytes:
    """Convert 'aa:bb:cc:dd:ee:ff' → b'\\xaa\\xbb\\xcc\\xdd\\xee\\xff'."""
    if ":" in mac:
        hex_parts = mac.split(":")
    elif "-" in mac:
        hex_parts = mac.split("-")
    else:
        raise ValueError(f"MAC format unrecognized: {mac!r}")

    if len(hex_parts) != 6:
        raise ValueError(f"MAC must have 6 octets, got {len(hex_parts)}: {mac!r}")

    return bytes(int(h, 16) for h in hex_parts)


def bytes_to_mac(data: bytes) -> str:
    """Convert b'\\xaa\\xbb\\xcc\\xdd\\xee\\xff' → 'aa:bb:cc:dd:ee:ff'."""
    if len(data) < 6:
        raise ValueError(f"Need at least 6 bytes for MAC, got {len(data)}")
    return ":".join(f"{b:02x}" for b in data[:6])


def ethertype_name(etype: int) -> str:
    """Return human-readable name for an EtherType value."""
    return ETHERTYPE_NAMES.get(etype, f"0x{etype:04x}")


def build_header(dst_mac: str, src_mac: str, ethertype: int) -> bytes:
    """
    Build a 14-byte Ethernet II header.

    Args:
        dst_mac: Destination MAC (colon-separated hex)
        src_mac: Source MAC (colon-separated hex)
        ethertype: EtherType value (e.g., 0x0806 for ARP)

    Returns:
        14 bytes: [dst(6) | src(6) | type(2)]
    """
    dst = mac_to_bytes(dst_mac)
    src = mac_to_bytes(src_mac)
    etype = struct.pack("!H", ethertype)
    return dst + src + etype


def parse_header(data: bytes, offset: int = 0) -> dict:
    """
    Parse a 14-byte Ethernet II header.

    Returns a dict with dst_mac, src_mac, ethertype, ethertype_name,
    and _next_offset (offset + HEADER_SIZE).
    """
    if len(data) < offset + HEADER_SIZE:
        raise ValueError(
            f"Data too short for Ethernet header: "
            f"{len(data)} bytes at offset {offset}, need {HEADER_SIZE}"
        )

    dst = bytes_to_mac(data[offset:offset + 6])
    src = bytes_to_mac(data[offset + 6:offset + 12])
    etype = struct.unpack("!H", data[offset + 12:offset + 14])[0]

    return {
        "dst_mac": dst,
        "src_mac": src,
        "ethertype": etype,
        "ethertype_name": ethertype_name(etype),
        "_next_offset": offset + HEADER_SIZE,
    }


def build_frame(dst_mac: str, src_mac: str, ethertype: int, payload: bytes) -> bytes:
    """Build a complete Ethernet II frame (header + payload)."""
    return build_header(dst_mac, src_mac, ethertype) + payload


def parse_frame(data: bytes, offset: int = 0) -> dict:
    """
    Parse a complete Ethernet II frame.

    Returns header dict plus the payload bytes.
    """
    header = parse_header(data, offset)
    payload_start = header["_next_offset"]
    header["payload"] = data[payload_start:]
    header["payload_length"] = len(header["payload"])
    return header


def hexdump(data: bytes, title: str = "", offset: int = 0) -> str:
    """Format bytes as a hex dump."""
    lines = []
    if title:
        lines.append(f"  {title}")
    lines.append(f"  {'Offset':<8} {'Hex':<49} {'ASCII'}")
    lines.append(f"  {'-'*8} {'-'*49} {'-'*16}")

    for i in range(0, len(data), 16):
        chunk = data[i:i + 16]
        hex_part = " ".join(f"{b:02x}" for b in chunk)
        ascii_part = "".join(chr(b) if 32 <= b < 127 else "." for b in chunk)
        lines.append(f"  {offset+i:08x}  {hex_part:<49s} {ascii_part}")

    return "\n".join(lines)


def main() -> None:
    print("=" * 64)
    print("  LAB-004: Ethernet II Frame Encoder/Decoder")
    print("=" * 64)
    print()

    # ── MAC Conversion ─────────────────────────────────────────────────
    print("─" * 64)
    print("  1. MAC Address Conversion")
    print("─" * 64)
    print()

    test_macs = [
        "aa:bb:cc:dd:ee:ff",
        "02:00:00:00:00:01",
        "ff:ff:ff:ff:ff:ff",
        "00:00:00:00:00:00",
        "02:00:00:00:00:fe",
    ]

    for mac in test_macs:
        raw = mac_to_bytes(mac)
        back = bytes_to_mac(raw)
        ok = "✓" if mac == back else "✗"
        print(f"  {mac}  →  {raw.hex()}  →  {back}  {ok}")

    # ── EtherType Constants ────────────────────────────────────────────
    print()
    print("─" * 64)
    print("  2. EtherType Constants")
    print("─" * 64)
    print()
    for etype, name in ETHERTYPE_NAMES.items():
        packed = struct.pack("!H", etype)
        print(f"  {name:<6} = 0x{etype:04x}  →  bytes {packed.hex()}")

    # ── Header Construction ────────────────────────────────────────────
    print()
    print("─" * 64)
    print("  3. Ethernet II Header (ARP Request Example)")
    print("─" * 64)
    print()

    dst = BROADCAST_MAC
    src = "02:00:00:00:00:01"
    etype = ETHERTYPE_ARP

    header = build_header(dst, src, etype)

    print(f"  Destination:  {dst}")
    print(f"  Source:       {src}")
    print(f"  EtherType:    0x{etype:04x} ({ethertype_name(etype)})")
    print(f"  Header size:  {len(header)} bytes (6 + 6 + 2)")
    print()
    print(hexdump(header, "Ethernet II Header (14 bytes):"))

    # ── Header Parsing ─────────────────────────────────────────────────
    print()
    print("─" * 64)
    print("  4. Parse Verification (Round-Trip)")
    print("─" * 64)
    print()

    parsed = parse_header(header)
    print(f"  Parsed dst_mac:         {parsed['dst_mac']}  {'✓' if parsed['dst_mac'] == dst else '✗'}")
    print(f"  Parsed src_mac:         {parsed['src_mac']}  {'✓' if parsed['src_mac'] == src else '✗'}")
    print(f"  Parsed ethertype:       0x{parsed['ethertype']:04x}  {'✓' if parsed['ethertype'] == etype else '✗'}")
    print(f"  Parsed ethertype_name:  {parsed['ethertype_name']}  {'✓' if parsed['ethertype_name'] == ethertype_name(etype) else '✗'}")
    print()

    # ── Full Frame ─────────────────────────────────────────────────────
    print("─" * 64)
    print("  5. Full Frame (with dummy payload)")
    print("─" * 64)
    print()

    payload = b"\x00" * 28  # ARP payload placeholder
    frame = build_frame(dst, src, etype, payload)
    print(f"  Total frame size: {len(frame)} bytes ({HEADER_SIZE} header + {len(payload)} payload)")
    print()

    parsed_frame = parse_frame(frame)
    print(f"  Parsed payload length: {parsed_frame['payload_length']} bytes")
    print(f"  Payload matches:       {'✓' if parsed_frame['payload'] == payload else '✗'}")

    print()
    print("=" * 64)
    print("  Ethernet frame encoder/decoder ready.")
    print("  All encode→decode round-trips verified.")
    print("=" * 64)


if __name__ == "__main__":
    main()
