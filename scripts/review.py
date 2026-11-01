from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from halio.config import settings  # noqa: E402
from halio.review import send_reply  # noqa: E402
from halio.store import Store  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description="Antrean pemeriksa manusia Halio (jalankan hanya di server tepercaya)")
    sub = parser.add_subparsers(dest="command", required=True)
    listing = sub.add_parser("list")
    listing.add_argument("type", choices=["appeals", "escalations"])
    listing.add_argument("--all", action="store_true")
    resolve = sub.add_parser("resolve")
    resolve.add_argument("type", choices=["appeals", "escalations"])
    resolve.add_argument("id", type=int)
    resolve.add_argument("--response", required=True)
    resolve.add_argument("--no-send", action="store_true")
    args = parser.parse_args()
    store = Store(settings.db_path)
    if args.command == "list":
        print(json.dumps(store.review_items(args.type, open_only=not args.all), ensure_ascii=False, indent=2))
        return
    items = {i["id"]: i for i in store.review_items(args.type, open_only=False)}
    if args.id not in items:
        raise SystemExit("Tiket tidak ditemukan")
    if args.type == "escalations" and not args.no_send:
        send_reply(items[args.id], args.response)
    store.resolve_review(args.type, args.id, args.response)
    print(f"Tiket {args.id} selesai")


if __name__ == "__main__":
    main()
