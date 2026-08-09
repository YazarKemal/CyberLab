#!/usr/bin/env python3
"""
LAB-003: Educational DNS Server (Localhost Only)
=================================================

A minimal educational DNS server that serves exactly two records:

  lab.local  A     → 127.0.0.42
  lab.local  AAAA  → ::1

Binds ONLY to 127.0.0.1:53535 (NOT port 53 — that requires root).

This server:
  - Receives one DNS query at a time (UDP datagram).
  - Decodes the transaction ID, QNAME, and QTYPE.
  - Builds a matching response with the same transaction ID.
  - Returns A or AAAA record as appropriate.
  - Supports --once mode (process one query and exit).
  - Supports --debug mode (print query details).

This is NOT a production DNS server. It does not:
  - Perform recursion
  - Handle NS, MX, CNAME, or other RR types
  - Implement caching
  - Validate queries
  - Handle EDNS0
  - Support TCP

Usage:
  python src/dns_server.py            # Run until Ctrl+C
  python src/dns_server.py --once     # Handle one query then exit
  python src/dns_server.py --debug    # Print query details
"""

import socket
import sys
import os

# Import our educational DNS message library
sys.path.insert(0, os.path.dirname(__file__))
import dns_message as dns


HOST = "127.0.0.1"
PORT = 53535
BUFFER_SIZE = 512

# Educational zone data
ZONE = {
    "lab.local": {
        dns.QTYPE_A:    ("127.0.0.42", 300),
        dns.QTYPE_AAAA: ("::1", 300),
    },
}


def build_error_response(query_data: bytes, rcode: int) -> bytes | None:
    """Build a response with no answers and the given RCODE."""
    try:
        q_header = dns.parse_header(query_data)
        q = dns.parse_question(query_data, dns.HEADER_SIZE)

        resp_flags = dns.FLAG_QR | dns.FLAG_AA
        if q_header["rd"]:
            resp_flags |= dns.FLAG_RD
        resp_flags |= rcode  # RCODE in low 4 bits

        header = dns.build_header(q_header["txid"], resp_flags, qdcount=1, ancount=0)
        question = dns.build_question(q["qname"], q["qtype"])
        return header + question
    except Exception:
        return None


def handle_query(data: bytes, client_addr: tuple, debug: bool = False) -> bytes | None:
    """Process one DNS query and return the response bytes."""
    try:
        header = dns.parse_header(data)
        q = dns.parse_question(data, dns.HEADER_SIZE)
    except Exception as exc:
        print(f"  Parse error: {exc}")
        return None

    txid = header["txid"]
    qname = q["qname"]
    qtype = q["qtype"]
    qtype_name = dns.QTYPE_NAMES.get(qtype, f"TYPE{qtype}")

    if debug:
        print(f"  Query from {client_addr[0]}:{client_addr[1]}:")
        print(f"    TXID:  0x{txid:04x} ({txid})")
        print(f"    QNAME: {qname}")
        print(f"    QTYPE: {qtype_name} ({qtype})")
        print(f"    Flags: RD={header['rd']}")

    # Look up in our educational zone
    name_records = ZONE.get(qname)
    if name_records is None:
        print(f"    → NXDOMAIN (no records for {qname})")
        return build_error_response(data, dns.RCODE_NXDOMAIN)

    rdata_info = name_records.get(qtype)
    if rdata_info is None:
        # Name exists but not this type — return empty answer (NOERROR, ancount=0)
        print(f"    → NOERROR (no {qtype_name} record for {qname})")
        try:
            resp_flags = dns.FLAG_QR | dns.FLAG_AA
            if header["rd"]:
                resp_flags |= dns.FLAG_RD
            r_header = dns.build_header(txid, resp_flags, qdcount=1, ancount=0)
            r_question = dns.build_question(qname, qtype)
            return r_header + r_question
        except Exception:
            return None

    ip_str, ttl = rdata_info

    # Build rdata
    if qtype == dns.QTYPE_A:
        rdata = socket.inet_pton(socket.AF_INET, ip_str)
    elif qtype == dns.QTYPE_AAAA:
        rdata = socket.inet_pton(socket.AF_INET6, ip_str)
    else:
        print(f"    → NOTIMP (unsupported type)")
        return build_error_response(data, dns.RCODE_NOTIMP)

    # Build full response
    response = dns.build_response(data, [{
        "name": qname,
        "qtype": qtype,
        "rdata": rdata,
        "ttl": ttl,
    }])

    print(f"    → {qtype_name} {ip_str} (TTL={ttl})")
    return response


def main() -> None:
    once = "--once" in sys.argv
    debug = "--debug" in sys.argv

    server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, PORT))

    local = server.getsockname()
    print(f"Educational DNS Server on {local[0]}:{local[1]}")
    print(f"Serving: lab.local A → 127.0.0.42, AAAA → ::1")
    print(f"Mode: {'single-shot' if once else 'continuous'} {'(debug)' if debug else ''}")
    print(f"NOT a production DNS server — educational only.")
    print()

    try:
        while True:
            if once:
                print("Waiting for one query...")
            else:
                print("Waiting for queries... (Ctrl+C to stop)")

            data, client_addr = server.recvfrom(BUFFER_SIZE)
            print(f"Received {len(data)} bytes from {client_addr[0]}:{client_addr[1]}")

            response = handle_query(data, client_addr, debug=debug)

            if response:
                server.sendto(response, client_addr)
                print(f"  Sent {len(response)} byte response")
            else:
                print(f"  Could not build response")

            print()

            if once:
                print("Single-shot mode — exiting.")
                break

    except KeyboardInterrupt:
        print()
        print("Shutting down...")

    finally:
        server.close()
        print("Server stopped.")


if __name__ == "__main__":
    main()
