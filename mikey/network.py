"""HTTPS connections that try IPv4 first.

Some networks drop IPv6 connections to Groq part-way through a request, and
urllib, unlike a browser, does not fall back to IPv4 on its own.
"""

from __future__ import annotations

import http.client
import socket
import urllib.request


def connect_ipv4_first(
    address: tuple[str, int], timeout: float | None, source_address=None
) -> socket.socket:
    """Open a TCP connection over IPv4, falling back to any address family."""
    host, port = address
    try:
        ipv4_address = socket.getaddrinfo(host, port, socket.AF_INET, socket.SOCK_STREAM)[0][4]
        return socket.create_connection(ipv4_address, timeout, source_address)
    except OSError:
        return socket.create_connection(address, timeout, source_address)


class IPv4FirstHTTPSConnection(http.client.HTTPSConnection):
    """HTTPS connection that prefers IPv4; IPv6 drops Groq requests on some networks."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._create_connection = connect_ipv4_first


class IPv4FirstHTTPSHandler(urllib.request.HTTPSHandler):
    def do_open(self, http_class, req, **http_conn_args):
        return super().do_open(IPv4FirstHTTPSConnection, req, **http_conn_args)


ipv4_first_opener = urllib.request.build_opener(IPv4FirstHTTPSHandler)
