# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Write a "Find this post at myea.blog/<slug>" header into each post Doc.

For every post linked from public/index.html, this sets the Google Doc's
DEFAULT page-header region, not body text, to:

    Find this post at myea.blog/<slug>

The displayed URL is hyperlinked to https://myea.blog/<slug>. The operation is
idempotent: if a Doc already has a default header, the script deletes and
recreates that default header.

Run after deploying the /<slug> redirects:

    uv run scripts/add_doc_headers.py --dry-run
    uv run scripts/add_doc_headers.py
    uv run scripts/add_doc_headers.py --only faith
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import tempfile
import threading
import time
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

SITE = "https://myea.blog"
PREFIX = "Find this post at "
DEFAULT_WORKERS = 8
WRITE_INTERVAL_SECONDS = 1.1
INDEX = Path(__file__).resolve().parent.parent / "public" / "index.html"
GOG_CRED = Path("~/Library/Application Support/gogcli/credentials.json").expanduser()

POST_RE = re.compile(
    r'href="(/[\w-]+)" data-doc="([\w-]+)"[^>]*>\s*'
    r'<span class="post-title">(.*?)</span>',
    re.S,
)


class WriteLimiter:
    def __init__(self, interval: float) -> None:
        self.interval = interval
        self.lock = threading.Lock()
        self.next_at = 0.0

    def wait(self) -> None:
        with self.lock:
            now = time.monotonic()
            if now < self.next_at:
                time.sleep(self.next_at - now)
                now = time.monotonic()
            self.next_at = now + self.interval


WRITE_LIMITER = WriteLimiter(WRITE_INTERVAL_SECONDS)


def get_access_token(account: str) -> str:
    with tempfile.TemporaryDirectory() as td:
        rt_path = os.path.join(td, "rt.json")
        subprocess.run(
            ["gog", "auth", "tokens", "export", account, "--out", rt_path, "--overwrite"],
            check=True,
            capture_output=True,
            text=True,
        )
        rt = json.load(open(rt_path))

    cred = json.load(open(GOG_CRED))
    cred = cred.get("installed") or cred.get("web") or cred
    data = urllib.parse.urlencode(
        {
            "client_id": cred["client_id"],
            "client_secret": cred["client_secret"],
            "refresh_token": rt["refresh_token"],
            "grant_type": "refresh_token",
        }
    ).encode()
    req = urllib.request.Request("https://oauth2.googleapis.com/token", data=data)
    return json.load(urllib.request.urlopen(req))["access_token"]


def open_json(req: urllib.request.Request, retries: int = 5) -> dict:
    for attempt in range(retries):
        try:
            return json.load(urllib.request.urlopen(req, timeout=30))
        except Exception as exc:
            if attempt == retries - 1:
                raise
            status = getattr(exc, "code", None)
            if status == 429:
                time.sleep(65)
            else:
                time.sleep(0.8 * (2**attempt))
    raise RuntimeError("unreachable")


def api_get(doc_id: str, token: str, fields: str) -> dict:
    encoded_fields = urllib.parse.quote(fields)
    url = f"https://docs.googleapis.com/v1/documents/{doc_id}?fields={encoded_fields}"
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}"})
    return open_json(req)


def batch_update(doc_id: str, token: str, requests: list[dict]) -> dict:
    WRITE_LIMITER.wait()
    req = urllib.request.Request(
        f"https://docs.googleapis.com/v1/documents/{doc_id}:batchUpdate",
        data=json.dumps({"requests": requests}).encode(),
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
    )
    return open_json(req)


def display_url(url: str) -> str:
    return re.sub(r"^https?://", "", url)


def header_text_end(header: dict) -> int:
    end = 0
    for block in header.get("content", []):
        paragraph = block.get("paragraph", {})
        for element in paragraph.get("elements", []):
            if "textRun" in element:
                end = max(end, int(element.get("endIndex", 0)))
    # Keep the final required newline in the header segment.
    return max(0, end - 1)


def set_header(doc_id: str, token: str, url: str) -> str:
    visible_url = display_url(url)
    text = f"{PREFIX}{visible_url}"
    doc = api_get(doc_id, token, "documentStyle,headers")
    style = doc.get("documentStyle", {})
    headers = doc.get("headers", {})
    existing = style.get("defaultHeaderId")
    if existing:
        requests = []
        end_index = header_text_end(headers.get(existing, {}))
        if end_index > 0:
            requests.append(
                {
                    "deleteContentRange": {
                        "range": {
                            "segmentId": existing,
                            "startIndex": 0,
                            "endIndex": end_index,
                        }
                    }
                }
            )
        requests.extend(
            [
                {
                    "insertText": {
                        "location": {"segmentId": existing, "index": 0},
                        "text": text,
                    }
                },
                {
                    "updateTextStyle": {
                        "range": {
                            "segmentId": existing,
                            "startIndex": len(PREFIX),
                            "endIndex": len(text),
                        },
                        "textStyle": {"link": {"url": url}},
                        "fields": "link",
                    }
                },
            ]
        )
        batch_update(doc_id, token, requests)
        return existing

    header_id = batch_update(doc_id, token, [{"createHeader": {"type": "DEFAULT"}}])[
        "replies"
    ][0]["createHeader"]["headerId"]
    batch_update(
        doc_id,
        token,
        [
            {"insertText": {"location": {"segmentId": header_id, "index": 0}, "text": text}},
            {
                "updateTextStyle": {
                    "range": {
                        "segmentId": header_id,
                        "startIndex": len(PREFIX),
                        "endIndex": len(text),
                    },
                    "textStyle": {"link": {"url": url}},
                    "fields": "link",
                }
            },
        ],
    )
    return header_id


def posts_from_index() -> list[tuple[str, str, str]]:
    return POST_RE.findall(INDEX.read_text())


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--account", default="alejoacelas@gmail.com")
    parser.add_argument("--only", help="limit to posts whose slug, doc id, or title contains this")
    parser.add_argument("--site", default=SITE, help="base URL for the header link")
    parser.add_argument("--workers", type=int, default=DEFAULT_WORKERS, help="parallel Doc updates")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    posts = posts_from_index()
    if not posts:
        sys.exit("No posts found in index.html; check POST_RE")

    if args.only:
        needle = args.only.lower().lstrip("/")
        posts = [
            post
            for post in posts
            if needle in f"{post[0].lstrip('/')} {post[1]} {post[2]}".lower()
        ]
        if not posts:
            sys.exit(f"--only {args.only!r} matched no posts")

    print(f"{len(posts)} post(s) to update:")
    for slug_path, _doc_id, title in posts:
        url = f"{args.site}{slug_path}"
        print(f"  {display_url(url)}  <-  {title}")

    if args.dry_run:
        print("\n(dry run; nothing written)")
        return

    workers = max(1, min(args.workers, len(posts)))
    token = get_access_token(args.account)
    failures = []

    def update_post(slug_path: str, doc_id: str, title: str) -> tuple[str, str, str, str | None]:
        url = f"{args.site}{slug_path}"
        try:
            set_header(doc_id, token, url)
            return "OK", url, title, None
        except Exception as exc:  # noqa: BLE001
            detail = getattr(exc, "read", lambda: b"")() or str(exc)
            return "FAIL", url, title, str(detail)

    print(f"\nUpdating with {workers} worker(s)...")
    with ThreadPoolExecutor(max_workers=workers) as executor:
        future_to_post = {
            executor.submit(update_post, slug_path, doc_id, title): (doc_id, title)
            for slug_path, doc_id, title in posts
        }
        for future in as_completed(future_to_post):
            doc_id, title = future_to_post[future]
            status, url, _title, detail = future.result()
            if detail:
                failures.append((title, doc_id, detail))
                print(f"  {status} {url} - {detail}")
            else:
                print(f"  {status}   {url}")

    if failures:
        print(f"\n{len(failures)} failed:")
        for title, doc_id, detail in failures:
            print(f"  - {title} ({doc_id}): {detail}")
        sys.exit(1)

    print(f"\nDone; {len(posts)} header(s) set.")


if __name__ == "__main__":
    main()
