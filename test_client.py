#!/usr/bin/env python3
import socket
from argparse import ArgumentParser
from ipaddress import IPv4Address
from struct import pack

from server import PKT_HDR

if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument('host', type=IPv4Address)
    parser.add_argument('port', type=int)
    parser.add_argument('test_run', type=int)
    parser.add_argument('signal', type=int)
    args = parser.parse_args()

    print("Connecting...")
    sock = socket.create_connection((args.host.exploded, args.port))
    print("Connected!")
    payload = PKT_HDR + pack("Qb", args.test_run, args.signal)
    print(f"Sending {payload}...")
    sock.send(payload)
