"""Outbound fetches of user-supplied or model-supplied URLs without DNS rebinding.

Checking "does this name resolve to a public address?" and then letting httpx resolve the name AGAIN to connect leaves a
gap: a hostile DNS server can answer with a public address the first time and 127.0.0.1 or 169.254.169.254 the second.
PinnedTransport resolves once, refuses the request if ANY answer is not a global address, and connects to that exact IP.
The Host header and the TLS server name (SNI, and therefore certificate verification) stay the original hostname.
"""

from __future__ import annotations

import ipaddress
import socket

import httpx


class PinnedTransport(httpx.BaseTransport):
    def __init__(self, inner: httpx.BaseTransport | None = None, resolver=socket.getaddrinfo):
        self.inner = inner or httpx.HTTPTransport()
        self.resolve = resolver

    def _address(self, request: httpx.Request) -> str:
        host = request.url.host
        try:
            addresses = [str(ipaddress.ip_address(host))]
        except ValueError:
            port = request.url.port or (443 if request.url.scheme == "https" else 80)
            try:
                addresses = [info[4][0] for info in self.resolve(host, port, type=socket.SOCK_STREAM)]
            except (socket.gaierror, UnicodeError) as exc:
                raise httpx.ConnectError("domain_tidak_ditemukan", request=request) from exc
        if not addresses or any(not ipaddress.ip_address(a.split("%")[0]).is_global for a in addresses):
            raise httpx.ConnectError("alamat_jaringan_tidak_publik", request=request)
        return addresses[0].split("%")[0]

    def handle_request(self, request: httpx.Request) -> httpx.Response:
        host = request.url.host
        address = self._address(request)
        if address != host:
            # The Host header was set from the original URL when the request was built; only where we connect changes.
            request.url = request.url.copy_with(host=address)
            if request.url.scheme == "https":
                request.extensions = {**request.extensions, "sni_hostname": host}
        return self.inner.handle_request(request)

    def close(self) -> None:
        self.inner.close()
