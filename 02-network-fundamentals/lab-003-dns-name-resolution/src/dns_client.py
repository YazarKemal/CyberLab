#!/usr/bin/env python3
"""
LAB-003: Educational DNS Client (Localhost Only)
=================================================

Queries ONLY 127.0.0.1:53535 — our own educational DNS server.

This client:
  1. Generates a random transaction ID.
  2. Encodes a DNS query (header + question).
  3. Sends the query via UDP to the server.
  4. Receives the response.
  5. Verifies the response transaction ID matches the query.
  6. Decodes and displays the answer.

Usage:
  python src/dns_client.py lab.local A       # Query A record
  python src/dns_client.py lab.local AAAA    # Query AAAA record

Target: 127.0.0.1:53535 (ALWAYS — hard-coded)
"""

import socket
import sys
import os
import random

sys.path.insert(0, os.path.dirname(__file__))
import dns_message as dns


HOST = "127.0.0.1"
PORT = 53535
TIMEOUT = 3  # seconds


def main() -> None:
    if len(sys.argv) != 3:
        print("Usage: python src/dns_client.py <name> <A|AAAA>")
        print("Example: python src/dns_client.py lab.local A")
        print()
        print(f"Target: {HOST}:{PORT} (hard-coded — educational server only)")
        sys.exit(1)

    name = sys.argv[1]
    qtype_str = sys.argv[2].upper()

    qtype_map = {"A": dns.QTYPE_A, "AAAA": dns.QTYPE_AAAA}
    if qtype_str not in qtype_map:
        print(f"ERROR: Unknown query type '{qtype_str}'. Use A or AAAA.")
        sys.exit(1)

    qtype = qtype_map[qtype_str]

    # ---- 1. Generate transaction ID ----
    txid = random.randint(0, 65535)

    # ---- 2. Build the query ----
    query = dns.build_query(name, qtype, txid=txid)

    print(f"DNS Query: {name} {qtype_str}")
    print(f"  Transaction ID: 0x{txid:04x} ({txid})")
    print(f"  Target: {HOST}:{PORT}")
    print(f"  Query packet: {len(query)} bytes")
    print()

    # ---- 3. Send query via UDP ----
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(TIMEOUT)

    # Show our local address before send
    before = sock.getsockname()
    print(f"  Before sendto — getsockname(): {before[0]}:{before[1]}")

    try:
        sock.sendto(query, (HOST, PORT))

        # Show our local address after send (OS assigned ephemeral port)
        after = sock.getsockname()
        print(f"  After sendto — getsockname():  {after[0]}:{after[1]}")
        print()

        # ---- 4. Receive response ----
        print("Waiting for response...")
        data, server_addr = sock.recvfrom(512)

        print(f"Received {len(data)} bytes from {server_addr[0]}:{server_addr[1]}")
        print()

        # ---- 5. Verify transaction ID ----
        resp_header = dns.parse_header(data)
        resp_txid = resp_header["txid"]

        print(f"  Query TXID:  0x{txid:04x}")
        print(f"  Response TXID: 0x{resp_txid:04x}")
        if resp_txid == txid:
            print(f"  TXID match: ✓")
        else:
            print(f"  TXID match: ✗ MISMATCH — response does not match our query!")
        print()

        # ---- 6. Parse and display response ----
        print(f"Response header:")
        print(f"  QR: {resp_header['qr']} (1 = response)")
        print(f"  AA: {resp_header['aa']} (1 = authoritative)")
        print(f"  RD: {resp_header['rd']}")
        print(f"  RA: {resp_header['ra']}")
        print(f"  RCODE: {resp_header['rcode']}")
        print(f"  QDCOUNT: {resp_header['qdcount']}")
        print(f"  ANCOUNT: {resp_header['ancount']}")

        # Parse questions
        pos = dns.HEADER_SIZE
        for qi in range(resp_header["qdcount"]):
            q = dns.parse_question(data, pos)
            print(f"  Question {qi}: {q['qname']} {q['qtype_name']} {q['qclass_name']}")
            pos = q["_next_offset"]

        # Parse answers
        if resp_header["ancount"] == 0:
            print()
            if resp_header["rcode"] == dns.RCODE_NXDOMAIN:
                print("  Result: NXDOMAIN — name does not exist in zone.")
            else:
                print("  Result: NO ANSWER — no records of this type.")
        else:
            resp = dns.parse_response(data)
            print()
            for ai, a in enumerate(resp["answers"]):
                print(f"  Answer {ai}:")
                print(f"    Name:  {a['name']}")
                print(f"    Type:  {a['type_name']} ({a['type']})")
                print(f"    TTL:   {a['ttl']} seconds")
                print(f"    Data:  {a['rdata']}")
                print()

        # ---- 7. Hexdump ----
        print(dns.hexdump(data, "DNS Response Packet"))

    except socket.timeout:
        print(f"ERROR: No response within {TIMEOUT} seconds.")
        print(f"  Is dns_server.py running on {HOST}:{PORT}?")
        sys.exit(1)

    finally:
        sock.close()


if __name__ == "__main__":
    main()
