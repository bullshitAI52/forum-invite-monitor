#!/usr/bin/env python3
"""Small browser-based monitor for new posts in the configured section."""
import argparse
import json
import os
import re
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
SEEN = DATA / "seen_tids.txt"
STATUS = DATA / "status.json"
TZ = ZoneInfo("Asia/Shanghai")
URL = os.environ.get("T66Y_SECTION_URL", "https://www.t66y.com/thread0806.php?fid=7")


def load_seen():
    return {x.strip() for x in SEEN.read_text().splitlines()} if SEEN.exists() else set()


def save_seen(tids):
    DATA.mkdir(exist_ok=True)
    SEEN.write_text("\n".join(sorted(tids)) + "\n", encoding="utf-8")


def write_status(**extra):
    DATA.mkdir(exist_ok=True)
    old = json.loads(STATUS.read_text()) if STATUS.exists() else {}
    old.update(last_run=datetime.now(TZ).isoformat(), **extra)
    STATUS.write_text(json.dumps(old, ensure_ascii=False, indent=2), encoding="utf-8")


def extract_posts(page):
    """Extract likely thread links without assuming one exact forum skin."""
    rows = []
    for link in page.locator("a").all():
        href = link.get_attribute("href") or ""
        text = " ".join((link.inner_text() or "").split())
        match = re.search(r"(?:tid=|/)(\d{5,})(?:\.html)?", href)
        if match and text:
            rows.append({"tid": match.group(1), "title": text, "url": page.url if href.startswith("#") else page.url.rsplit("/", 1)[0] + "/" + href.lstrip("/")})
    unique = {}
    for row in rows:
        unique.setdefault(row["tid"], row)
    return list(unique.values())


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--headed", action="store_true")
    args = parser.parse_args()
    seen = load_seen()
    first_run = not SEEN.exists()
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=not args.headed)
        page = browser.new_page()
        page.goto(URL, wait_until="domcontentloaded", timeout=60_000)
        page.wait_for_timeout(1500)
        posts = extract_posts(page)
        current = {p["tid"] for p in posts}
        new_posts = [] if first_run else [p for p in posts if p["tid"] not in seen]
        save_seen(seen | current)
        write_status(new_threads_total=len(new_posts), last_error=None, notes="baseline created" if first_run else f"found {len(new_posts)} new threads")
        print("baseline created" if first_run else f"new threads: {len(new_posts)}")
        for post in new_posts:
            print(f"- {post['tid']} {post['title']} {post['url']}")
        browser.close()


if __name__ == "__main__":
    main()
