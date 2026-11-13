"""PinnedTransport: the address checked is the address connected to (no DNS rebinding between check and connect)."""

import socket

import httpx
import pytest

from halio.safefetch import PinnedTransport


def _resolver(*answers):
    # resolver buatan buat nyatet berapa kali DNS dipanggil & ngembaliin IP sesuai skenario tes
    calls = []

    def resolve(host, port, type=0):
        calls.append(host)
        return [(socket.AF_INET6 if ":" in a else socket.AF_INET, socket.SOCK_STREAM, 6, "", (a, port)) for a in answers]
    resolve.calls = calls
    return resolve


def _capture():
    seen = {}

    def handler(request):
        seen["url"], seen["host"], seen["sni"] = str(request.url), request.headers["host"], request.extensions.get("sni_hostname")
        return httpx.Response(200, text="ok")
    return seen, httpx.MockTransport(handler)


def test_connects_to_the_checked_ip_and_keeps_host_and_sni():
    # konek langsung ke IP yg udah lolos cek sambil tetep njaga header Host sm SNI buat sertifikat TLS
    seen, inner = _capture()
    resolve = _resolver("93.184.215.14")
    with httpx.Client(transport=PinnedTransport(inner=inner, resolver=resolve)) as c:
        assert c.get("https://www.example.org/a?b=1").text == "ok"
    assert seen["url"] == "https://93.184.215.14/a?b=1"
    assert seen["host"] == "www.example.org" and seen["sni"] == "www.example.org"
    assert resolve.calls == ["www.example.org"]          # DNS cuma boleh di-resolve sekali biar nutup celah DNS rebinding


def test_plain_http_has_no_sni_but_keeps_host():
    seen, inner = _capture()
    with httpx.Client(transport=PinnedTransport(inner=inner, resolver=_resolver("93.184.215.14"))) as c:
        c.get("http://example.org:8080/x")
    assert seen["url"] == "http://93.184.215.14:8080/x" and seen["host"] == "example.org:8080" and seen["sni"] is None


# kl hasil DNS nyelipin satu aja IP lokal / privat / metadata cloud, langsung putus koneksinya
@pytest.mark.parametrize("answers", [("127.0.0.1",), ("10.0.0.5",), ("169.254.169.254",), ("93.184.215.14", "192.168.1.1"), ("::1",)])
def test_refuses_any_non_public_answer(answers):
    _, inner = _capture()
    with httpx.Client(transport=PinnedTransport(inner=inner, resolver=_resolver(*answers))) as c, pytest.raises(httpx.ConnectError):
        c.get("https://rebind.example/")


def test_refuses_private_ip_literals_without_dns():
    # nembak IP privat mentah2 langsung ditolak tanpa perlu nanya DNS dulu
    _, inner = _capture()
    resolve = _resolver("93.184.215.14")
    with httpx.Client(transport=PinnedTransport(inner=inner, resolver=resolve)) as c, pytest.raises(httpx.ConnectError):
        c.get("http://127.0.0.1:8000/api/radar")
    assert resolve.calls == []


def test_unresolvable_name_is_a_connect_error():
    # domain gaib yg gagal resolve harus rapi dilempar jadi ConnectError
    def fail(host, port, type=0):
        raise socket.gaierror("no such host")
    _, inner = _capture()
    with httpx.Client(transport=PinnedTransport(inner=inner, resolver=fail)) as c, pytest.raises(httpx.ConnectError):
        c.get("https://nope.invalid/")
