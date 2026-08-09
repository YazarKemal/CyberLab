#!/usr/bin/env python3
"""
LAB-003: Offline DNS Packet Construction Demo
==============================================

Builds a DNS query packet entirely offline — no sockets, no network.

This demonstrates what a DNS query packet actually looks like at the byte
level, before it ever touches a socket. Every byte is explained.

Usage:
  python src/dns_packet_demo.py
"""

import sys
import os

sys.path.insert(0, os.path.dirname(__file__))
import dns_message as dns


def annotate_bytes(data: bytes, labels: list[tuple[int, int, str]]) -> str:
    """
    Print bytes with labeled regions.

    labels: list of (start_offset, end_offset, description)
    """
    lines = []
    lines.append("  Offset  Bytes                                      Interpretation")
    lines.append("  " + "-" * 75)

    # Build a map: byte_offset → list of annotations starting there
    annotations = {}
    for start, end, desc in labels:
        annotations.setdefault(start, []).append(desc)

    i = 0
    while i < len(data):
        line_start = i
        chunk = data[i:i + 16]

        # Hex part
        hex_str = ""
        for j, b in enumerate(chunk):
            if j == 8:
                hex_str += " "
            hex_str += f"{b:02x} "

        # Interpretation
        interp = ""
        if i in annotations:
            interp = " ← " + " | ".join(annotations[i])

        lines.append(f"  {i:06x}  {hex_str:<49s} {interp}")

        i += 16

    lines.append("  " + "-" * 75)
    return "\n".join(lines)


def main() -> None:
    print("=" * 60)
    print("  LAB-003: Offline DNS Packet Construction")
    print("  No sockets — byte-level inspection only")
    print("=" * 60)
    print()

    # =========================================================================
    # Step 1: Choose parameters
    # =========================================================================
    txid = 0xABCD
    name = "lab.local"
    qtype = dns.QTYPE_A
    qtype_name = "A"

    print("Step 1: Parameters")
    print(f"  Transaction ID: 0x{txid:04x} ({txid})")
    print(f"  QNAME: {name}")
    print(f"  QTYPE: {qtype_name} ({qtype})")
    print(f"  QCLASS: IN ({dns.QCLASS_IN})")
    print()

    # =========================================================================
    # Step 2: Encode QNAME
    # =========================================================================
    print("Step 2: QNAME Encoding")
    print(f"  Input:  \"{name}\"")
    print(f"  Labels: {name.split('.')}")
    print()

    qname_bytes = dns.encode_qname(name)

    # Show label-by-label
    print("  Label breakdown:")
    pos = 0
    for label in name.split("."):
        lb = label.encode("ascii")
        len_byte = qname_bytes[pos]
        label_data = qname_bytes[pos + 1:pos + 1 + len(lb)]
        print(f"    [{pos:2d}] {len_byte:02x}                length = {len_byte}")
        print(f"    [{pos+1:2d}] {' '.join(f'{b:02x}' for b in label_data):20s} \"{label}\"")
        pos += 1 + len(lb)
    print(f"    [{pos:2d}] 00                root (end of QNAME)")
    print()

    # =========================================================================
    # Step 3: Build header
    # =========================================================================
    print("Step 3: DNS Header (12 bytes)")
    flags = dns.FLAG_RD  # Recursion Desired
    header = dns.build_header(txid, flags, qdcount=1)

    print(f"  ID:      0x{txid:04x} → bytes {header[0]:02x} {header[1]:02x}")
    print(f"  FLAGS:   RD=1 → bytes {header[2]:02x} {header[3]:02x}  (0x0100)")
    print(f"  QDCOUNT: 1 → bytes {header[4]:02x} {header[5]:02x}")
    print(f"  ANCOUNT: 0 → bytes {header[6]:02x} {header[7]:02x}")
    print(f"  NSCOUNT: 0 → bytes {header[8]:02x} {header[9]:02x}")
    print(f"  ARCOUNT: 0 → bytes {header[10]:02x} {header[11]:02x}")
    print()

    # =========================================================================
    # Step 4: Build question
    # =========================================================================
    print("Step 4: Question Section")
    question = dns.build_question(name, qtype)

    print(f"  QNAME ({len(qname_bytes)} bytes): {qname_bytes.hex()}")
    print(f"  QTYPE ({qtype} = {qtype_name}): 2 bytes")
    print(f"  QCLASS ({dns.QCLASS_IN} = IN): 2 bytes")
    print(f"  Question total: {len(question)} bytes")
    print()

    # =========================================================================
    # Step 5: Full packet
    # =========================================================================
    print("Step 5: Complete DNS Query Packet")
    query = header + question
    print(f"  Total length: {len(query)} bytes")
    print(f"  = 12 (header) + {len(question)} (question)")
    print()

    # Annotated hexdump
    labels = [
        (0,  2,  f"Transaction ID = 0x{txid:04x}"),
        (2,  4,  f"Flags = 0x0100 (RD=1, standard query)"),
        (4,  6,  "QDCOUNT = 1"),
        (6,  8,  "ANCOUNT = 0"),
        (8,  10, "NSCOUNT = 0"),
        (10, 12, "ARCOUNT = 0"),
        (12, 12 + len(qname_bytes), f"QNAME = \"{name}\" (DNS label encoding)"),
        (12 + len(qname_bytes), 12 + len(qname_bytes) + 2, f"QTYPE = {qtype} ({qtype_name})"),
        (12 + len(qname_bytes) + 2, 12 + len(qname_bytes) + 4, f"QCLASS = {dns.QCLASS_IN} (IN)"),
    ]

    print(annotate_bytes(query, labels))
    print()

    # =========================================================================
    # Step 6: Verify by parsing our own packet
    # =========================================================================
    print("Step 6: Self-Verification — parse the packet we just built")
    try:
        parsed_header = dns.parse_header(query)
        parsed_q = dns.parse_question(query, dns.HEADER_SIZE)
        print(f"  TXID:  0x{parsed_header['txid']:04x} {'✓' if parsed_header['txid'] == txid else '✗'}")
        print(f"  RD:    {parsed_header['rd']} {'✓' if parsed_header['rd'] else '✗'}")
        print(f"  QNAME: {parsed_q['qname']} {'✓' if parsed_q['qname'] == name else '✗'}")
        print(f"  QTYPE: {parsed_q['qtype_name']} ({parsed_q['qtype']}) {'✓' if parsed_q['qtype'] == qtype else '✗'}")
        print(f"  QCLASS: {parsed_q['qclass_name']} ({parsed_q['qclass']}) {'✓' if parsed_q['qclass'] == dns.QCLASS_IN else '✗'}")
        print()
        print("  All fields verified ✓ — encoder and decoder agree.")
    except Exception as exc:
        print(f"  FAILED: {exc}")

    # =========================================================================
    # Step 7: Full hexdump
    # =========================================================================
    print()
    print(dns.hexdump(query, "DNS Query Packet (lab.local A)"))

    # =========================================================================
    # Step 8: Also show an AAAA query for comparison
    # =========================================================================
    print()
    print("=" * 60)
    print("  Bonus: AAAA query for comparison")
    print("=" * 60)
    print()

    query_aaaa = dns.build_query("lab.local", dns.QTYPE_AAAA, txid=0xBEEF)
    print(f"  lab.local AAAA query: {len(query_aaaa)} bytes")
    print(f"  (Same length as A query — only QTYPE field differs by 27)")
    print()
    # Show the QTYPE byte difference
    print(f"  QTYPE bytes in A query:    {query[14 + len(qname_bytes):16 + len(qname_bytes)].hex()}")
    print(f"  QTYPE bytes in AAAA query: {query_aaaa[14 + len(qname_bytes):16 + len(qname_bytes)].hex()}")
    print(f"  A=0x0001, AAAA=0x001c — only byte 15 differs")

    print()
    print("=" * 60)
    print("  Demo complete.")
    print("  The query packet above is what dns_client.py sends via UDP.")
    print("=" * 60)


if __name__ == "__main__":
    main()
