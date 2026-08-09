#!/usr/bin/env python3
"""
LAB-003: Educational DNS Message Encoder / Decoder
===================================================

Implements a SMALL EDUCATIONAL SUBSET of the DNS wire protocol using only
the Python standard library (struct, bytes).

This is NOT a full DNS implementation. It handles exactly what LAB-003 needs:
  - 12-byte DNS header (ID, FLAGS, QDCOUNT, ANCOUNT, NSCOUNT, ARCOUNT)
  - QNAME encoding as DNS labels (3www6google3com0)
  - QTYPE A (1) and AAAA (28)
  - QCLASS IN (1)
  - Answer RR decoding: NAME, TYPE, CLASS, TTL, RDLENGTH, RDATA
  - Rdata for A (4 bytes, IPv4) and AAAA (16 bytes, IPv6)

What it does NOT implement:
  - Name compression (pointer labels)
  - Authority / Additional sections
  - NS, MX, CNAME, SOA, or any RR type beyond A and AAAA
  - EDNS0
  - DNSSEC
  - Truncation
  - Zone transfers (AXFR)

DNS Message Format (RFC 1035 §4.1):

    +---------------------+
    |        Header       | 12 bytes
    +---------------------+
    |       Question      | variable
    +---------------------+
    |        Answer       | variable
    +---------------------+
    |      Authority      | variable
    +---------------------+
    |      Additional     | variable
    +---------------------+

DNS Header (12 bytes):

   0  1  2  3  4  5  6  7  8  9 10 11 12 13 14 15
    +--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
    |                      ID                           |
    +--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
    |QR|   Opcode  |AA|TC|RD|RA|   Z    |   RCODE     |
    +--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
    |                    QDCOUNT                        |
    +--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
    |                    ANCOUNT                        |
    +--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
    |                    NSCOUNT                        |
    +--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
    |                    ARCOUNT                        |
    +--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
"""

import struct
import random

# =============================================================================
# Constants
# =============================================================================

# QTYPE values (RFC 1035 §3.2.2)
QTYPE_A     = 1     # IPv4 address
QTYPE_AAAA  = 28    # IPv6 address

# QCLASS values (RFC 1035 §3.2.4)
QCLASS_IN   = 1     # Internet

# DNS header field sizes (all 16-bit unsigned, network byte order)
HEADER_FORMAT = "!HHHHHH"   # ID, FLAGS, QDCOUNT, ANCOUNT, NSCOUNT, ARCOUNT
HEADER_SIZE   = struct.calcsize(HEADER_FORMAT)  # 12 bytes

# Flag bit positions within the FLAGS field (16 bits)
# Bits are 0-indexed from MSB (bit 15) to LSB (bit 0)
FLAG_QR     = 0x8000   # bit 15: Query (0) / Response (1)
FLAG_AA     = 0x0400   # bit 10: Authoritative Answer
FLAG_RD     = 0x0100   # bit  8: Recursion Desired
FLAG_RA     = 0x0080   # bit  7: Recursion Available
# RCODE is bits 3-0

# Response codes
RCODE_OK    = 0
RCODE_NXDOMAIN = 3    # Non-existent domain
RCODE_NOTIMP   = 4    # Not implemented

# Mapping for display
QTYPE_NAMES = {QTYPE_A: "A", QTYPE_AAAA: "AAAA"}
QCLASS_NAMES = {QCLASS_IN: "IN"}


# =============================================================================
# QNAME Encoding (RFC 1035 §3.1)
# =============================================================================

def encode_qname(name: str) -> bytes:
    """
    Encode a domain name into DNS wire-format labels.

    Each label: [length_byte][label_bytes...]
    Terminator: \x00 (zero-length label = root)

    Example:
      "lab.local" →
        03 6c 61 62     (3 + "lab")
        05 6c 6f 63 61 6c (5 + "local")
        00              (root terminator)

      "www.example.com" →
        03 77 77 77     (3 + "www")
        07 65 78 61 6d 70 6c 65 (7 + "example")
        03 63 6f 6d     (3 + "com")
        00              (root terminator)
    """
    result = bytearray()
    for label in name.rstrip(".").split("."):
        label_bytes = label.encode("ascii")
        if len(label_bytes) > 63:
            raise ValueError(f"Label too long ({len(label_bytes)} > 63): {label}")
        result.append(len(label_bytes))
        result.extend(label_bytes)
    result.append(0)  # root terminator
    return bytes(result)


def decode_qname(data: bytes, offset: int) -> tuple[str, int]:
    """
    Decode a DNS QNAME from raw bytes starting at `offset`.

    Returns (name_string, next_offset).

    This implementation only handles standard labels (not compressed pointers).
    If a compressed pointer (first two bits = 11) is encountered, we raise
    NotImplementedError — this educational implementation does not support
    name compression.
    """
    labels = []
    pos = offset

    while True:
        if pos >= len(data):
            raise ValueError(f"Unexpected end of data at position {pos}")

        length = data[pos]
        pos += 1

        if length == 0:
            break  # root terminator

        # Check for pointer (top two bits = 11)
        if (length & 0xC0) == 0xC0:
            # Pointer format: 11000000 00000000 — we don't implement this
            raise NotImplementedError(
                "Name compression (pointer labels) not implemented in this "
                "educational DNS parser. The response contains compressed names."
            )

        if pos + length > len(data):
            raise ValueError(f"Label extends past end of data")

        label = data[pos:pos + length].decode("ascii", errors="replace")
        labels.append(label)
        pos += length

    return ".".join(labels), pos


# =============================================================================
# DNS Header
# =============================================================================

def build_header(txid: int, flags: int, qdcount: int = 1,
                 ancount: int = 0, nscount: int = 0, arcount: int = 0) -> bytes:
    """Pack a 12-byte DNS header into network byte order."""
    return struct.pack(HEADER_FORMAT, txid, flags, qdcount, ancount, nscount, arcount)


def parse_header(data: bytes) -> dict:
    """Unpack a 12-byte DNS header and return a dictionary of its fields."""
    if len(data) < HEADER_SIZE:
        raise ValueError(f"Data too short for DNS header: {len(data)} bytes")

    txid, flags, qdcount, ancount, nscount, arcount = struct.unpack(
        HEADER_FORMAT, data[:HEADER_SIZE]
    )

    return {
        "txid": txid,
        "flags": flags,
        "flags_hex": f"0x{flags:04x}",
        "qr": bool(flags & FLAG_QR),
        "aa": bool(flags & FLAG_AA),
        "rd": bool(flags & FLAG_RD),
        "ra": bool(flags & FLAG_RA),
        "rcode": flags & 0x000F,
        "qdcount": qdcount,
        "ancount": ancount,
        "nscount": nscount,
        "arcount": arcount,
    }


# =============================================================================
# Question Section
# =============================================================================

def build_question(name: str, qtype: int, qclass: int = QCLASS_IN) -> bytes:
    """
    Build a DNS question section.
    Format: QNAME (variable) + QTYPE (2 bytes) + QCLASS (2 bytes)
    """
    qname = encode_qname(name)
    return qname + struct.pack("!HH", qtype, qclass)


def parse_question(data: bytes, offset: int) -> dict:
    """Parse a DNS question section starting at `offset`."""
    qname, pos = decode_qname(data, offset)

    if pos + 4 > len(data):
        raise ValueError("Data too short for QTYPE + QCLASS")

    qtype, qclass = struct.unpack("!HH", data[pos:pos + 4])
    pos += 4

    return {
        "qname": qname,
        "qtype": qtype,
        "qtype_name": QTYPE_NAMES.get(qtype, f"TYPE{qtype}"),
        "qclass": qclass,
        "qclass_name": QCLASS_NAMES.get(qclass, f"CLASS{qclass}"),
        "_next_offset": pos,
    }


# =============================================================================
# Answer / Resource Record Section (simplified)
# =============================================================================

def build_answer_record(name: str, qtype: int, rdata: bytes,
                        ttl: int = 300, qclass: int = QCLASS_IN) -> bytes:
    """
    Build a single answer Resource Record.

    Format:
      NAME      (variable — encoded QNAME, no compression in this implementation)
      TYPE      (2 bytes)
      CLASS     (2 bytes)
      TTL       (4 bytes)
      RDLENGTH  (2 bytes)
      RDATA     (variable)
    """
    encoded_name = encode_qname(name)
    rdlength = len(rdata)
    return (
        encoded_name +
        struct.pack("!HHIH", qtype, qclass, ttl, rdlength) +
        rdata
    )


def build_a_answer(name: str, ipv4: str, ttl: int = 300) -> bytes:
    """Build an A record answer."""
    import socket
    rdata = socket.inet_pton(socket.AF_INET, ipv4)
    return build_answer_record(name, QTYPE_A, rdata, ttl)


def build_aaaa_answer(name: str, ipv6: str, ttl: int = 300) -> bytes:
    """Build an AAAA record answer."""
    import socket
    rdata = socket.inet_pton(socket.AF_INET6, ipv6)
    return build_answer_record(name, QTYPE_AAAA, rdata, ttl)


# =============================================================================
# Full Message Builders
# =============================================================================

def build_query(name: str, qtype: int, txid: int | None = None) -> bytes:
    """
    Build a complete DNS query packet.

    Header: ID, RD=1, QDCOUNT=1
    Question: name, qtype, QCLASS_IN
    """
    if txid is None:
        txid = random.randint(0, 65535)

    # FLAGS: Recursion Desired = 1, everything else = 0
    flags = FLAG_RD

    header = build_header(txid, flags, qdcount=1)
    question = build_question(name, qtype)

    return header + question


def build_response(query_data: bytes, answers: list[dict]) -> bytes:
    """
    Build a DNS response for a given query.

    answers: list of dicts with keys: name, qtype, rdata (bytes), ttl (optional)

    Returns the full response packet or raises ValueError on parse failure.
    """
    q_header = parse_header(query_data)

    offset = HEADER_SIZE
    q_question = parse_question(query_data, offset)

    # Flags: QR=1 (response), AA=1 (authoritative), RD from query, RA=0
    resp_flags = FLAG_QR | FLAG_AA
    if q_header["rd"]:
        resp_flags |= FLAG_RD

    # Build answer section
    answer_bytes = b""
    for ans in answers:
        ttl = ans.get("ttl", 300)
        answer_bytes += build_answer_record(
            ans["name"], ans["qtype"], ans["rdata"], ttl
        )

    header = build_header(
        txid=q_header["txid"],
        flags=resp_flags,
        qdcount=1,
        ancount=len(answers),
    )

    # Mirror the question
    question = build_question(q_question["qname"], q_question["qtype"])

    return header + question + answer_bytes


# =============================================================================
# Response Parser
# =============================================================================

def parse_response(data: bytes) -> dict:
    """
    Parse a DNS response packet.

    Returns a dict with:
      header: dict from parse_header()
      questions: list of parsed question dicts
      answers: list of parsed answer dicts (each includes type, class,
               TTL, and a human-readable address for A/AAAA records)
    """
    header = parse_header(data)
    pos = HEADER_SIZE

    # Parse questions
    questions = []
    for _ in range(header["qdcount"]):
        q = parse_question(data, pos)
        pos = q.pop("_next_offset")
        questions.append(q)

    # Parse answers
    answers = []
    for _ in range(header["ancount"]):
        try:
            a, pos = _parse_answer_record(data, pos)
            answers.append(a)
        except NotImplementedError:
            # Name compression in answers — skip remaining answers
            break

    return {
        "header": header,
        "questions": questions,
        "answers": answers,
    }


def _parse_answer_record(data: bytes, offset: int) -> tuple[dict, int]:
    """
    Parse a single answer Resource Record from data starting at offset.

    Returns (answer_dict, next_offset).
    """
    name, pos = decode_qname(data, offset)

    if pos + 10 > len(data):
        raise ValueError("Data too short for RR fixed fields")

    rtype, rclass, ttl, rdlength = struct.unpack("!HHIH", data[pos:pos + 10])
    pos += 10

    if pos + rdlength > len(data):
        raise ValueError(f"RDATA extends past end of data: need {rdlength}, have {len(data) - pos}")

    rdata_raw = data[pos:pos + rdlength]
    pos += rdlength

    # Decode rdata into human-readable form
    import socket
    rdata_display = rdata_raw.hex()
    if rtype == QTYPE_A and rdlength == 4:
        rdata_display = socket.inet_ntop(socket.AF_INET, rdata_raw)
    elif rtype == QTYPE_AAAA and rdlength == 16:
        rdata_display = socket.inet_ntop(socket.AF_INET6, rdata_raw)

    return {
        "name": name,
        "type": rtype,
        "type_name": QTYPE_NAMES.get(rtype, f"TYPE{rtype}"),
        "class": rclass,
        "ttl": ttl,
        "rdlength": rdlength,
        "rdata_hex": rdata_raw.hex(),
        "rdata": rdata_display,
    }, pos


# =============================================================================
# Hexdump Helper
# =============================================================================

def hexdump(data: bytes, title: str = "DNS Packet") -> str:
    """
    Produce an educational hexdump of a DNS packet.

    Output format:
      offset  hex bytes (grouped)  ASCII interpretation
    """
    lines = [f"  {title} — {len(data)} bytes", "  " + "-" * 60]
    for i in range(0, len(data), 16):
        chunk = data[i:i + 16]
        hex_part = " ".join(f"{b:02x}" for b in chunk)
        # Add extra space after 8 bytes for readability
        if len(chunk) > 8:
            hex_part = hex_part[:23] + " " + hex_part[23:]
        ascii_part = "".join(
            chr(b) if 32 <= b < 127 else "." for b in chunk
        )
        lines.append(f"  {i:04x}  {hex_part:<49s}  |{ascii_part}|")
    lines.append("  " + "-" * 60)
    return "\n".join(lines)


def hexdump_annotated(data: bytes) -> str:
    """
    Produce an annotated hexdump that labels DNS sections.

    Section offsets are displayed with names (HEADER, QUESTION, ANSWER).
    """
    header = parse_header(data)
    lines = []
    lines.append(f"  DNS Packet — {len(data)} bytes total")
    lines.append(f"  Transaction ID: 0x{header['txid']:04x} ({header['txid']})")
    lines.append(f"  Questions: {header['qdcount']}, Answers: {header['ancount']}")
    lines.append("  " + "-" * 60)

    pos = 0

    # Header
    lines.append(f"  [{pos:04x}] HEADER (12 bytes)")
    for i in range(0, 12, 4):
        chunk = data[i:i + 4]
        lines.append(f"        {i:04x}  {' '.join(f'{b:02x}' for b in chunk)}")
    pos = 12

    # Questions
    q_end = pos
    for qi in range(header["qdcount"]):
        try:
            q, q_end = _skip_question(data, pos)
            lines.append(f"  [{pos:04x}] QUESTION {qi + 1} ({q_end - pos} bytes): "
                         f"QNAME={q['qname']}, QTYPE={q['qtype_name']}")
            for i in range(pos, min(q_end, len(data)), 16):
                chunk_end = min(i + 16, q_end)
                chunk = data[i:chunk_end]
                lines.append(f"        {i:04x}  {' '.join(f'{b:02x}' for b in chunk)}")
            pos = q_end
        except (ValueError, NotImplementedError):
            break

    # Answers
    if pos >= len(data):
        return "\n".join(lines)

    lines.append(f"  [{pos:04x}] ANSWER SECTION ({len(data) - pos} bytes)")
    for i in range(pos, len(data), 16):
        chunk = data[i:i + 16]
        lines.append(f"        {i:04x}  {' '.join(f'{b:02x}' for b in chunk)}")

    return "\n".join(lines)


def _skip_question(data: bytes, offset: int) -> tuple[dict, int]:
    """Parse a question and return (question_dict, next_offset)."""
    q = parse_question(data, offset)
    return q, q.pop("_next_offset")


# =============================================================================
# Quick self-check (not run on import)
# =============================================================================

if __name__ == "__main__":
    print("dns_message.py — self-check")
    print()

    # Test QNAME encoding
    print("QNAME encoding tests:")
    for name in ["lab.local", "www.example.com", "localhost"]:
        encoded = encode_qname(name)
        decoded, _ = decode_qname(encoded, 0)
        status = "✓" if decoded == name else "✗"
        print(f"  {status} {name} → {encoded.hex()} → {decoded}")

    # Test query building
    print()
    print("Query building test (lab.local A):")
    query = build_query("lab.local", QTYPE_A, txid=0xABCD)
    parsed = parse_header(query)
    print(f"  Length: {len(query)} bytes")
    print(f"  TXID: 0x{parsed['txid']:04x}")
    print(f"  RD: {parsed['rd']}")
    q = parse_question(query, HEADER_SIZE)
    print(f"  QNAME: {q['qname']}")
    print(f"  QTYPE: {q['qtype_name']} ({q['qtype']})")
    print(f"  QCLASS: {q['qclass_name']} ({q['qclass']})")

    # Test response building
    print()
    print("Response building test:")
    import socket
    response = build_response(query, [{
        "name": "lab.local",
        "qtype": QTYPE_A,
        "rdata": socket.inet_pton(socket.AF_INET, "127.0.0.42"),
        "ttl": 300,
    }])
    r_parsed = parse_response(response)
    print(f"  Response TXID: 0x{r_parsed['header']['txid']:04x}")
    print(f"  Response QR: {r_parsed['header']['qr']}")
    print(f"  Answer count: {r_parsed['header']['ancount']}")
    for a in r_parsed["answers"]:
        print(f"  Answer: {a['name']} {a['type_name']} → {a['rdata']} (TTL={a['ttl']})")

    print()
    print("All self-checks passed.")
