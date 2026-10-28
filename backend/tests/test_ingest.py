import os
import tempfile
from datetime import datetime, timedelta, timezone

import httpx
import pytest

os.environ.setdefault("HALIO_DB", os.path.join(tempfile.mkdtemp(), "ingest-api.db"))
os.environ.pop("RADAR_TOKEN", None)

from fastapi.testclient import TestClient  # noqa: E402

from halio.api import app  # noqa: E402
from halio.ingest import coverage  # noqa: E402
from halio.ingest.fetcher import make_client, run_once  # noqa: E402
from halio.ingest.parse import FeedError, parse_feed  # noqa: E402
from halio.ingest.sources import BLIND_SPOTS, SOURCES, Source  # noqa: E402
from halio.ingest.store import SensorStore  # noqa: E402

NOW = datetime(2026, 10, 28, 12, 0, tzinfo=timezone.utc)

RSS = """<?xml version="1.0"?><rss version="2.0"><channel>
<item><title><![CDATA[Gempa M5,1 guncang Cianjur]]></title><link>https://x.test/a</link><guid>a</guid>
<pubDate>Wed, 28 Oct 2026 11:58:00 +0000</pubDate><description>&lt;p&gt;BMKG mencatat &lt;b&gt;gempa&lt;/b&gt;&lt;/p&gt;</description></item>
<item><title>[SALAH] Kabar tanpa tanggal</title><link>https://x.test/b</link><guid>b</guid></item>
<item><title>Tanpa tautan</title></item>
</channel></rss>"""

ATOM = """<?xml version="1.0"?><feed xmlns="http://www.w3.org/2005/Atom"><entry>
<title>Entri Atom</title><link href="https://x.test/atom"/><id>tag:x,1</id><updated>2026-10-28T11:00:00Z</updated>
<summary>Ringkasan</summary></entry></feed>"""


def src(sid="s1", cadence=120, quiet=3600):
    return Source(sid, sid, f"https://feed.test/{sid}", "berita", cadence_s=cadence, max_quiet_s=quiet)


@pytest.fixture
def store(tmp_path):
    return SensorStore(tmp_path / "sensor.db")


# --- parsing ------------------------------------------------------------
def test_parse_rss_keeps_minimal_metadata_and_skips_incomplete_items():
    items = parse_feed(RSS.encode())
    assert [i.guid for i in items] == ["a", "b"]
    assert items[0].title == "Gempa M5,1 guncang Cianjur"
    assert items[0].published == "2026-10-28T11:58:00+00:00"
    assert items[0].snippet == "BMKG mencatat gempa"          # markup stripped
    assert items[1].published is None                          # TurnBackHoax-style feed without dates


def test_parse_atom():
    (item,) = parse_feed(ATOM.encode())
    assert item.url == "https://x.test/atom" and item.published == "2026-10-28T11:00:00+00:00"


def test_parse_rejects_entity_bombs_oversize_and_garbage():
    bomb = b'<?xml version="1.0"?><!DOCTYPE r [<!ENTITY a "aaaa">]><rss><channel><item><title>&a;</title></item></channel></rss>'
    for bad in (bomb, b"x" * 3_000_001, b"<rss><unclosed>"):
        with pytest.raises(FeedError):
            parse_feed(bad)


def test_same_headline_gets_same_fingerprint_across_sources():
    a = parse_feed(RSS.encode())[0]
    b = parse_feed(RSS.replace("Gempa M5,1 guncang Cianjur", "GEMPA  M5,1 guncang Cianjur!").encode())[0]
    assert a.fingerprint == b.fingerprint


# --- store: dedupe + backfill ----------------------------------------------
def test_first_poll_is_backfill_then_new_items_count(store):
    s = src()
    items = parse_feed(RSS.encode())
    store.record_fetch(s, NOW, status="ok", latency_ms=50, items=items)
    assert store.recent_items() == []                          # history is not news
    assert store.item_stats(NOW - timedelta(hours=24))[s.id]["n_window"] == 0

    more = parse_feed(RSS.replace("</channel>", '<item><title>Baru</title><link>https://x.test/c</link><guid>c</guid></item></channel>').encode())
    assert store.record_fetch(s, NOW + timedelta(minutes=2), status="ok", latency_ms=60, items=more) == 1
    assert [i["title"] for i in store.recent_items()] == ["Baru"]
    # same items again: nothing new
    assert store.record_fetch(s, NOW + timedelta(minutes=4), status="ok", latency_ms=60, items=more) == 0


def test_seen_delay_ignores_future_published_times(store):
    s = src()
    store.record_fetch(s, NOW, status="ok", latency_ms=10, items=[])
    ok = parse_feed(RSS.encode())[:1]                           # published 11:58, seen 12:02 -> 240 s
    store.record_fetch(s, NOW + timedelta(minutes=2), status="ok", latency_ms=10, items=ok)
    future = parse_feed(ATOM.replace("2026-10-28T11:00:00Z", "2026-10-28T13:00:00Z").encode())
    store.record_fetch(s, NOW + timedelta(minutes=4), status="ok", latency_ms=10, items=future)
    assert store.seen_delays(NOW - timedelta(hours=1))[s.id] == [240.0]


# --- fetcher: conditional GET, failures, backoff ---------------------------
def test_conditional_get_and_304_keeps_etag(store):
    calls = []

    def handler(req: httpx.Request) -> httpx.Response:
        calls.append(req.headers.get("if-none-match"))
        if req.headers.get("if-none-match") == '"v1"':
            return httpx.Response(304)
        return httpx.Response(200, content=RSS.encode(), headers={"etag": '"v1"'})

    client = make_client(transport=httpx.MockTransport(handler))
    s = src()
    run_once(store, client, [s], now=NOW)
    run_once(store, client, [s], now=NOW + timedelta(minutes=3))
    assert calls == [None, '"v1"']
    st = store.state(s.id)
    assert st["etag"] == '"v1"' and st["last_status"] == "304" and st["fails"] == 0


def test_failures_back_off_and_mark_source_dead(store):
    client = make_client(transport=httpx.MockTransport(lambda r: httpx.Response(404)))
    s = src(cadence=120)
    t = NOW
    for _ in range(3):
        run_once(store, client, [s], now=t)
        t += timedelta(hours=1)                                 # always due again
    st = store.state(s.id)
    assert st["fails"] == 3 and st["last_error"] == "HTTP 404"
    assert coverage.classify(s, st, None, t) == "mati"
    # backoff: after the third failure the next attempt is pushed past the base cadence
    assert datetime.fromisoformat(st["next_due"]) - (t - timedelta(hours=1)) >= timedelta(seconds=120 * 8)
    assert store.due([s], t - timedelta(hours=1) + timedelta(seconds=120)) == []


def test_network_error_is_reported_not_raised(store):
    def boom(req):
        raise httpx.ConnectError("down")

    client = make_client(transport=httpx.MockTransport(boom))
    run_once(store, client, [src()], now=NOW)
    assert store.state("s1")["last_error"] == "ConnectError"


# --- coverage classification ---------------------------------------------------
def test_classify_live_stale_and_paused(store):
    s = src(cadence=120, quiet=3600)
    assert coverage.classify(s, None, None, NOW) == "belum"

    store.record_fetch(s, NOW, status="ok", latency_ms=10, items=[])
    fresh = {"newest_pub": "2026-10-28T11:50:00+00:00"}
    st = store.state(s.id)
    assert coverage.classify(s, st, fresh, NOW + timedelta(seconds=60)) == "hidup"
    old = {"newest_pub": "2026-10-28T09:00:00+00:00"}
    assert coverage.classify(s, st, old, NOW + timedelta(seconds=60)) == "basi"
    assert coverage.classify(s, st, fresh, NOW + timedelta(hours=1)) == "tertunda"   # poller stopped


def test_undated_feed_is_judged_by_first_seen(store):
    s = src(cadence=300, quiet=3600)
    store.record_fetch(s, NOW, status="ok", latency_ms=10, items=parse_feed(RSS.encode()))
    st = store.state(s.id)
    stats = {"newest_pub": None, "newest_seen": None}
    assert coverage.classify(s, st, stats, NOW + timedelta(seconds=100)) == "hidup"   # just started watching
    store.record_fetch(s, NOW + timedelta(hours=2), status="304", latency_ms=10)
    assert coverage.classify(s, store.state(s.id), stats, NOW + timedelta(hours=2, seconds=30)) == "basi"


def test_build_report_shape(store):
    live, dead = src("live"), src("dead")
    client = make_client(transport=httpx.MockTransport(
        lambda r: httpx.Response(200, content=RSS.encode()) if "live" in str(r.url) else httpx.Response(500)))
    run_once(store, client, [live, dead], now=NOW)
    report = coverage.build(store, NOW + timedelta(seconds=30), [live, dead])
    by_id = {r["id"]: r for r in report["sources"]}
    assert by_id["live"]["status"] == "hidup" and by_id["dead"]["status"] == "belum"
    assert report["sources_total"] == 2 and report["counts"]["hidup"] == 1
    assert {b["id"] for b in report["blind_spots"]} == {b.id for b in BLIND_SPOTS}
    assert "bukan seluruh ruang informasi" in report["disclaimer"]


# --- registry + API ------------------------------------------------------------
def test_registry_is_sane():
    ids = [s.id for s in SOURCES]
    assert len(ids) == len(set(ids)) >= 20
    assert all(s.url.startswith("https://") and s.cadence_s >= 60 and s.max_quiet_s > s.cadence_s for s in SOURCES)
    assert all(b.tier in ("B", "C") for b in BLIND_SPOTS)


def test_coverage_api_before_any_polling():
    client = TestClient(app)
    r = client.get("/api/sensor/coverage")
    assert r.status_code == 200
    body = r.json()
    assert body["polling"] is False and body["sources_total"] == len(SOURCES)
    assert client.get("/api/sensor/items?limit=5").json() == {"items": []}
    assert client.get("/coverage").status_code == 200
