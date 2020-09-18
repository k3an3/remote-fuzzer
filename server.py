#!/usr/bin/env python3
import datetime
import socket
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter, FileType, SUPPRESS
from concurrent.futures.thread import ThreadPoolExecutor
from ipaddress import IPv4Address
from struct import unpack
from threading import Lock
from traceback import print_exc
from typing import Tuple

import colorful as colorful

LOG_MSG = "Test run: {}, result: {}"
PKT_HDR = b"FUZZ"


class LogWriter:
    def __init__(self, log_file: FileType = None, quiet: bool = False):
        self.log_file = log_file
        self.lock = Lock()
        self.quiet = quiet

    def error(self, msg: str):
        self._write(msg, colorful.red)

    def info(self, msg: str):
        self._write(msg)

    def success(self, msg: str):
        self._write(msg, colorful.green)

    def warn(self, msg: str):
        self._write(msg, colorful.orange)

    def _write(self, msg: str, color: str = colorful.white):
        self.lock.acquire()
        line = "[{}] {}{}{}\n".format(
            datetime.datetime.now().isoformat(),
            color,
            msg,
            colorful.reset)
        if self.log_file:
            self.log_file.write(line)
        if not self.quiet:
            print(line, end='')
        self.lock.release()


def create_server_socket(host: str, port: int) -> socket:
    server_socket = socket.create_server((host, port))
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.listen()
    return server_socket


def handle_connection(conn: socket, addr: Tuple[str, int], log: LogWriter, debug: bool = False) -> None:
    try:
        data = conn.recv(32)
        if debug:
            print(data)
        if data[0:4] != PKT_HDR:
            log.warn("Invalid header!")
        test_run = unpack("<Q", data[4:12])[0]
        signal = data[12]
        if not signal:
            log.success(LOG_MSG.format(test_run, signal))
        else:
            log.error(LOG_MSG.format(test_run, signal))
    except:
        print_exc()
    finally:
        conn.shutdown(socket.SHUT_RDWR)
        conn.close()


def main(args):
    log = LogWriter(args.log_file, args.quiet)
    log.info(f"Starting server on {args.bind_host}:{args.bind_port}...")
    server_socket = create_server_socket(args.bind_host.exploded, args.bind_port)
    try:
        with ThreadPoolExecutor(max_workers=args.workers) as executor:
            while True:
                conn, addr = server_socket.accept()
                if args.debug:
                    print(f"Got connection from {addr[0]}")
                executor.submit(handle_connection, conn, addr, log, args.debug)
    except KeyboardInterrupt:
        print()
        log.warn("Received SIGINT; shutting down...")
        server_socket.shutdown(socket.SHUT_RDWR)
        server_socket.close()


if __name__ == '__main__':
    parser = ArgumentParser(formatter_class=ArgumentDefaultsHelpFormatter)
    parser.add_argument('-b', '--bind-host', default=IPv4Address("0.0.0.0"), type=IPv4Address,
                        help="Address to bind the server to.")
    parser.add_argument('-p', '--bind-port', default=1337, type=int, help="Port to bind the server to.")
    parser.add_argument('-f', '--log-file', type=FileType('w'), help="File to store log output.")
    parser.add_argument('-q', '--quiet', action='store_true', help="Whether to suppress printed output.")
    parser.add_argument('-d', '--debug', action='store_true', help=SUPPRESS)
    parser.add_argument('-w', '--workers', default=None, type=int,
                        help="Maximum number of worker threads to spawn.")
    parser.add_argument('-l', '--loud', action='store_true', help="Whether to log normal test runs in addition to "
                                                                  "crashes.")
    main(parser.parse_args())
