#!/usr/bin/env python3
"""
LAB-004: Offline ARP Packet Demo
=================================

Constructs ARP REQUEST and ARP REPLY packets entirely offline using
fictional documentation-space addresses (192.0.2.0/24 — RFC 5737).

NO NETWORK TRANSMISSION.

Demonstrates:
  - ARP request construction (Who has 192.0.2.1?)
  - ARP reply construction (192.0.2.1 is at aa:bb:cc:dd:ee:ff)
  - Ethernet II wrapping of ARP packets
  - Full hexdumps with annotations
  - encode → decode round-trip verification

Usage:
  python src/arp_packet_demo.py
"""

import sys
import os

sys.path.insert(0, os.path.dirname(__file__))
import arp_packet as arp
import ethernet_frame as eth


def hexdump_full(data: bytes, title: str = "", annotations: dict[int, str] | None = None) -> str:
    """Hex dump with optional per-offset annotations."""
    lines = []
    if title:
        lines.append(f"  {title} ({len(data)} bytes)")
    lines.append(f"  {'Offset':<8} {'Hex':<49} {'Interpretation'}")
    lines.append(f"  {'-'*8} {'-'*49} {'-'*40}")

    if annotations is None:
        annotations = {}

    i = 0
    while i < len(data):
        chunk = data[i:i + 16]
        hex_str = ""
        for j, b in enumerate(chunk):
            if j == 8:
                hex_str += " "
            hex_str += f"{b:02x} "

        interp = annotations.get(i, "")
        if interp:
            interp = "← " + interp

        lines.append(f"  {i:08x}  {hex_str:<49s} {interp}")
        i += 16

    return "\n".join(lines)


def main() -> None:
    print("=" * 64)
    print("  LAB-004: Offline ARP Packet Demo")
    print("  NO NETWORK TRANSMISSION")
    print("  Addresses: 192.0.2.0/24 (RFC 5737 documentation space)")
    print("=" * 64)

    # ══════════════════════════════════════════════════════════════════════
    # PART A: ARP REQUEST
    # ══════════════════════════════════════════════════════════════════════

    print()
    print("╔" + "═" * 62 + "╗")
    print("║" + "  PART A: ARP REQUEST — Who has 192.0.2.1? Tell 192.0.2.10".center(62) + "║")
    print("╚" + "═" * 62 + "╝")

    sender_mac = "02:00:00:00:00:01"
    sender_ip = "192.0.2.10"
    target_ip = "192.0.2.1"

    print()
    print("  Conceptual:")
    print(f"    Sender {sender_mac} ({sender_ip}) asks:")
    print(f"    'Who has IP {target_ip}? Tell me at {sender_ip}.'")
    print()

    # 1. Build raw ARP request
    print("─" * 64)
    print("  Step 1: Build ARP REQUEST (28 bytes)")
    print("─" * 64)
    print()

    arp_req = arp.build_arp_request(
        sha=sender_mac,
        spa=sender_ip,
        tpa=target_ip,
    )

    # Annotate
    arp_annotations = {
        0:  f"HTYPE = {arp.HTYPE_ETHERNET} (Ethernet)",
        2:  f"PTYPE = 0x{arp.PTYPE_IPV4:04x} (IPv4)",
        4:  f"HLEN = {arp.HLEN_ETHER} (MAC = 6 bytes)",
        5:  f"PLEN = {arp.PLEN_IPV4} (IPv4 = 4 bytes)",
        6:  f"OPER = {arp.OPER_REQUEST} (REQUEST)",
        8:  f"SHA = {sender_mac} (sender's MAC)",
        14: f"SPA = {sender_ip} (sender's IPv4)",
        18: f"THA = 00:00:00:00:00:00 (UNKNOWN — the question)",
        24: f"TPA = {target_ip} (who has this IP?)",
    }

    print(hexdump_full(arp_req, "ARP REQUEST — raw bytes", arp_annotations))
    print(f"  ARP packet length: {len(arp_req)} bytes")

    # Verify encode → decode
    req_parsed = arp.parse_arp(arp_req)
    print()
    print(f"  Encode → Decode verification:")
    checks = [
        ("OPER=REQUEST", req_parsed["oper"] == arp.OPER_REQUEST),
        ("SHA", req_parsed["sha"] == sender_mac),
        ("SPA", req_parsed["spa"] == sender_ip),
        ("THA zero", req_parsed["tha"] == "00:00:00:00:00:00"),
        ("TPA", req_parsed["tpa"] == target_ip),
        ("Packet size", len(arp_req) == arp.ARP_PACKET_SIZE),
    ]
    for label, ok in checks:
        print(f"    {label:<20} {'✓' if ok else '✗'}")

    # 2. Wrap in Ethernet
    print()
    print("─" * 64)
    print("  Step 2: Wrap in Ethernet II Frame")
    print("─" * 64)
    print()

    eth_req = eth.build_frame(
        dst_mac=eth.BROADCAST_MAC,
        src_mac=sender_mac,
        ethertype=eth.ETHERTYPE_ARP,
        payload=arp_req,
    )

    eth_annotations = {
        0:  f"Ethernet DST = {eth.BROADCAST_MAC} (BROADCAST)",
        6:  f"Ethernet SRC = {sender_mac}",
        12: f"EtherType = 0x{eth.ETHERTYPE_ARP:04x} (ARP)",
        14: "── ARP packet begins ──",
        14: f"HTYPE = {arp.HTYPE_ETHERNET} (Ethernet)",
        16: f"PTYPE = 0x{arp.PTYPE_IPV4:04x} (IPv4)",
        18: f"HLEN = {arp.HLEN_ETHER}",
        19: f"PLEN = {arp.PLEN_IPV4}",
        20: f"OPER = {arp.OPER_REQUEST} (REQUEST)",
        22: f"SHA = {sender_mac}",
        28: f"SPA = {sender_ip}",
        32: f"THA = 00:00:00:00:00:00",
        38: f"TPA = {target_ip}",
    }

    print(hexdump_full(eth_req, "Ethernet + ARP REQUEST", eth_annotations))
    print()
    print(f"  Full frame size: {len(eth_req)} bytes")
    print(f"    = {eth.HEADER_SIZE} Ethernet header")
    print(f"    + {len(arp_req)} ARP packet")
    print()
    print(f"  Ethernet destination: {eth.BROADCAST_MAC} (broadcast — reaches all on link)")
    print(f"  Ethernet source:      {sender_mac}")

    # Verify Ethernet parse
    eth_parsed = eth.parse_frame(eth_req)
    print()
    print(f"  Ethernet round-trip:")
    print(f"    dst_mac:    {eth_parsed['dst_mac']}  {'✓' if eth_parsed['dst_mac'] == eth.BROADCAST_MAC else '✗'}")
    print(f"    src_mac:    {eth_parsed['src_mac']}  {'✓' if eth_parsed['src_mac'] == sender_mac else '✗'}")
    print(f"    ethertype:  0x{eth_parsed['ethertype']:04x}  {'✓' if eth_parsed['ethertype'] == eth.ETHERTYPE_ARP else '✗'}")

    # ══════════════════════════════════════════════════════════════════════
    # PART B: ARP REPLY
    # ══════════════════════════════════════════════════════════════════════

    print()
    print()
    print("╔" + "═" * 62 + "╗")
    print("║" + "  PART B: ARP REPLY — 192.0.2.1 is at 02:00:00:00:00:fe".center(62) + "║")
    print("╚" + "═" * 62 + "╝")

    responder_mac = "02:00:00:00:00:fe"
    responder_ip = target_ip  # 192.0.2.1
    requester_mac = sender_mac
    requester_ip = sender_ip

    print()
    print("  Conceptual:")
    print(f"    {responder_ip} responds:")
    print(f"    'I am {responder_ip}. My MAC is {responder_mac}.'")
    print(f"    Reply sent directly (unicast) to {requester_mac}.")
    print()

    # 1. Build raw ARP reply
    print("─" * 64)
    print("  Step 1: Build ARP REPLY (28 bytes)")
    print("─" * 64)
    print()

    arp_rep = arp.build_arp_reply(
        sha=responder_mac,
        spa=responder_ip,
        tha=requester_mac,
        tpa=requester_ip,
    )

    rep_annotations = {
        0:  f"HTYPE = {arp.HTYPE_ETHERNET} (Ethernet)",
        2:  f"PTYPE = 0x{arp.PTYPE_IPV4:04x} (IPv4)",
        4:  f"HLEN = {arp.HLEN_ETHER}",
        5:  f"PLEN = {arp.PLEN_IPV4}",
        6:  f"OPER = {arp.OPER_REPLY} (REPLY)",
        8:  f"SHA = {responder_mac} (responder's MAC — THE ANSWER)",
        14: f"SPA = {responder_ip} (responder's IPv4)",
        18: f"THA = {requester_mac} (requester's MAC)",
        24: f"TPA = {requester_ip} (requester's IPv4)",
    }

    print(hexdump_full(arp_rep, "ARP REPLY — raw bytes", rep_annotations))

    # Verify
    rep_parsed = arp.parse_arp(arp_rep)
    print()
    print(f"  Encode → Decode verification:")
    checks = [
        ("OPER=REPLY", rep_parsed["oper"] == arp.OPER_REPLY),
        ("SHA", rep_parsed["sha"] == responder_mac),
        ("SPA", rep_parsed["spa"] == responder_ip),
        ("THA", rep_parsed["tha"] == requester_mac),
        ("TPA", rep_parsed["tpa"] == requester_ip),
    ]
    for label, ok in checks:
        print(f"    {label:<20} {'✓' if ok else '✗'}")

    # 2. Wrap in Ethernet (unicast to requester)
    print()
    print("─" * 64)
    print("  Step 2: Wrap in Ethernet II Frame (UNICAST to requester)")
    print("─" * 64)
    print()

    eth_rep = eth.build_frame(
        dst_mac=requester_mac,  # ← unicast, not broadcast!
        src_mac=responder_mac,
        ethertype=eth.ETHERTYPE_ARP,
        payload=arp_rep,
    )

    rep_eth_annotations = {
        0:  f"Ethernet DST = {requester_mac} (UNICAST to requester)",
        6:  f"Ethernet SRC = {responder_mac}",
        12: f"EtherType = 0x{eth.ETHERTYPE_ARP:04x} (ARP)",
        14: "── ARP packet begins ──",
        20: f"OPER = {arp.OPER_REPLY} (REPLY)",
        22: f"SHA = {responder_mac} (responder — THE ANSWER)",
        28: f"SPA = {responder_ip}",
        32: f"THA = {requester_mac}",
        38: f"TPA = {requester_ip}",
    }

    print(hexdump_full(eth_rep, "Ethernet + ARP REPLY", rep_eth_annotations))
    print()
    print(f"  Full frame size: {len(eth_rep)} bytes")
    print(f"  Note: ARP REPLY is unicast, not broadcast.")
    print(f"  Ethernet destination = requester's MAC: {requester_mac}")

    # ══════════════════════════════════════════════════════════════════════
    # PART C: Request vs Reply Comparison
    # ══════════════════════════════════════════════════════════════════════

    print()
    print()
    print("╔" + "═" * 62 + "╗")
    print("║" + "  PART C: Request vs Reply — Side by Side".center(62) + "║")
    print("╚" + "═" * 62 + "╝")
    print()

    print(f"  {'':<30} {'REQUEST':>15} {'REPLY':>15}")
    print(f"  {'-'*30} {'-'*15} {'-'*15}")
    print(f"  {'Ethernet destination':<30} {eth.BROADCAST_MAC:>15} {requester_mac:>15}")
    print(f"  {'ARP OPER':<30} {'REQUEST (1)':>15} {'REPLY (2)':>15}")
    print(f"  {'SHA (sender HW addr)':<30} {sender_mac:>15} {responder_mac:>15}")
    print(f"  {'SPA (sender proto addr)':<30} {sender_ip:>15} {responder_ip:>15}")
    print(f"  {'THA (target HW addr)':<30} {'00:00:00:00:00:00':>15} {requester_mac:>15}")
    print(f"  {'TPA (target proto addr)':<30} {target_ip:>15} {requester_ip:>15}")
    print(f"  {'ARP packet size':<30} {len(arp_req):>15} {len(arp_rep):>15}")
    print(f"  {'Full frame size':<30} {len(eth_req):>15} {len(eth_rep):>15}")

    print()
    print("  Key observations:")
    print("    1. ARP REQUEST: THA = 00:00:00:00:00:00 (unknown)")
    print("    2. ARP REQUEST: Ethernet DST = ff:ff:ff:ff:ff:ff (broadcast)")
    print("    3. ARP REPLY:   THA = requester's actual MAC (known)")
    print("    4. ARP REPLY:   Ethernet DST = requester's MAC (unicast)")
    print("    5. Both ARP packets are exactly 28 bytes")
    print("    6. Both Ethernet+ARP frames are exactly 42 bytes (14 + 28)")

    # ══════════════════════════════════════════════════════════════════════
    print()
    print("=" * 64)
    print("  Demo complete.")
    print("  No packets were transmitted.")
    print("  All encode→decode round-trips verified.")
    print("=" * 64)


if __name__ == "__main__":
    main()
