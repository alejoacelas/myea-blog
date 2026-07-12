# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Put a subtle myea.blog/<slug> subtitle below each post Doc's title.

For every post linked from public/index.html, this writes:

    myea.blog/<slug>

as a linked, muted subtitle after the first body paragraph. The operation is
idempotent and removes the old repeating page header when present.

Run after deploying the /<slug> redirects:

    uv run scripts/sync_doc_subtitles.py --dry-run
    uv run scripts/sync_doc_subtitles.py
    uv run scripts/sync_doc_subtitles.py --only faith
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

SITE = "https://myea.blog"
SUBTITLE_FONT = "Arial"
SUBTITLE_FONT_SIZE = 11
SUBTITLE_COLOR = {"red": 0.275, "green": 0.467, "blue": 0.824}
DEFAULT_WORKERS = 8
WRITE_INTERVAL_SECONDS = 1.1
INDEX = Path(__file__).resolve().parent.parent / "public" / "index.html"

POST_RE = re.compile(
    r'href="(/[\w-]+)" data-doc="([\w-]+)"(?: data-tab="([\w.-]+)")?[^>]*>\s*'
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


def run_gog(args: list[str]) -> dict:
    result = subprocess.run(
        ["gog", *args, "-j", "--results-only", "--no-input"],
        check=True,
        capture_output=True,
        text=True,
    )
    return json.loads(result.stdout)


def api_get(doc_id: str, account: str, fields: str, tab_id: str = "") -> dict:
    del fields  # gog handles authentication and the full response is small enough here.
    args = ["docs", "raw", doc_id, "--account", account]
    if tab_id:
        args.extend(["--tab", tab_id])
    return run_gog(args)


def batch_update(doc_id: str, account: str, requests: list[dict]) -> dict:
    WRITE_LIMITER.wait()
    return run_gog(
        [
            "api", "call", "docs", "v1", "docs.documents.batchUpdate",
            "--account", account,
            "--params", json.dumps({"documentId": doc_id}),
            "--body", json.dumps({"requests": requests}),
            "--scope", "https://www.googleapis.com/auth/documents",
            "--allow-write", "--force",
        ]
    )


def display_url(url: str) -> str:
    return re.sub(r"^https?://", "", url)


def paragraph_text(block: dict) -> str:
    return "".join(
        element.get("textRun", {}).get("content", "")
        for element in block.get("paragraph", {}).get("elements", [])
    ).strip()


def normalized_title(text: str) -> str:
    return re.sub(r"[^\w]+", "", text.casefold())


def subtitle_style_is_current(block: dict, url: str) -> bool:
    runs = [
        element["textRun"]
        for element in block.get("paragraph", {}).get("elements", [])
        if element.get("textRun", {}).get("content", "").strip()
    ]
    if len(runs) != 1:
        return False
    style = runs[0].get("textStyle", {})
    color = style.get("foregroundColor", {}).get("color", {}).get("rgbColor", {})
    family = style.get("weightedFontFamily", {}).get("fontFamily")
    return (
        family in (None, SUBTITLE_FONT)  # Docs omits an explicit Arial override when it matches the default.
        and style.get("fontSize") == {"magnitude": SUBTITLE_FONT_SIZE, "unit": "PT"}
        and style.get("link", {}).get("url") == url
        and all(abs(color.get(channel, -1) - value) < 0.001 for channel, value in SUBTITLE_COLOR.items())
    )


def set_subtitle(
    doc_id: str, account: str, url: str, expected_title: str, tab_id: str = ""
) -> str:
    visible_url = display_url(url)
    doc = api_get(doc_id, account, "documentStyle,body.content", tab_id)

    def body_range(start: int, end: int) -> dict:
        value = {"startIndex": start, "endIndex": end}
        if tab_id:
            value["tabId"] = tab_id
        return value

    def body_location(index: int) -> dict:
        value = {"index": index}
        if tab_id:
            value["tabId"] = tab_id
        return value

    requests = []
    header_id = doc.get("documentStyle", {}).get("defaultHeaderId")
    if header_id:
        requests.append({"deleteHeader": {"headerId": header_id}})

    paragraphs = [block for block in doc.get("body", {}).get("content", []) if "paragraph" in block]
    title_position = next(
        (index for index, block in enumerate(paragraphs) if paragraph_text(block)), None
    )
    if title_position is None:
        raise ValueError("document has no title paragraph")

    title = paragraphs[title_position]
    actual_title = paragraph_text(title)
    if int(title["startIndex"]) != 1:
        raise ValueError(f"title starts at index {title['startIndex']}, not at the top")
    if normalized_title(actual_title) != normalized_title(expected_title):
        raise ValueError(
            f"first paragraph is {actual_title!r}, expected title {expected_title!r}"
        )
    if title.get("paragraph", {}).get("paragraphStyle", {}).get("namedStyleType") != "HEADING_1":
        requests.append(
            {
                "updateParagraphStyle": {
                    "range": body_range(int(title["startIndex"]), int(title["endIndex"])),
                    "paragraphStyle": {"namedStyleType": "HEADING_1"},
                    "fields": "namedStyleType",
                }
            }
        )
    following = paragraphs[title_position + 1] if title_position + 1 < len(paragraphs) else None
    existing_text = paragraph_text(following) if following else ""
    existing_subtitle = bool(
        re.fullmatch(r"(?:Find this post at )?myea\.blog/[\w-]+", existing_text)
    )
    blank_subtitles = []
    for blank in paragraphs[title_position + 2 :]:
        style = blank.get("paragraph", {}).get("paragraphStyle", {})
        if paragraph_text(blank) or style.get("namedStyleType") != "SUBTITLE":
            break
        blank_subtitles.append(blank)
    for blank in reversed(blank_subtitles):
        requests.append(
            {
                "deleteContentRange": {
                    "range": body_range(int(blank["startIndex"]), int(blank["endIndex"]))
                }
            }
        )
    if existing_text == visible_url and subtitle_style_is_current(following, url):
        if requests:
            batch_update(doc_id, account, requests)
        return visible_url

    if existing_subtitle:
        start = int(following["startIndex"])
        end = int(following["endIndex"]) - 1
        if end > start:
            requests.append(
                {"deleteContentRange": {"range": body_range(start, end)}}
            )
    else:
        start = int(title["endIndex"])

    text = visible_url
    inserted_text = text if existing_subtitle else f"{text}\n"
    requests.extend(
        [
            {"insertText": {"location": body_location(start), "text": inserted_text}},
            {
                "updateParagraphStyle": {
                    "range": body_range(start, start + len(text) + 1),
                    "paragraphStyle": {"namedStyleType": "SUBTITLE"},
                    "fields": "namedStyleType",
                }
            },
            {
                "updateTextStyle": {
                    "range": body_range(start, start + len(text)),
                    "textStyle": {
                        "foregroundColor": {"color": {"rgbColor": SUBTITLE_COLOR}},
                        "weightedFontFamily": {"fontFamily": SUBTITLE_FONT},
                        "fontSize": {"magnitude": SUBTITLE_FONT_SIZE, "unit": "PT"},
                        "link": {"url": url},
                    },
                    "fields": "foregroundColor,weightedFontFamily,fontSize,link",
                }
            },
        ]
    )
    batch_update(doc_id, account, requests)
    return visible_url


def posts_from_index() -> list[tuple[str, str, str, str]]:
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
            if needle in f"{post[0].lstrip('/')} {post[1]} {post[3]}".lower()
        ]
        if not posts:
            sys.exit(f"--only {args.only!r} matched no posts")

    print(f"{len(posts)} post(s) to update:")
    for slug_path, _doc_id, _tab_id, title in posts:
        url = f"{args.site}{slug_path}"
        print(f"  {display_url(url)}  <-  {title}")

    if args.dry_run:
        print("\n(dry run; nothing written)")
        return

    workers = max(1, min(args.workers, len(posts)))
    failures = []

    def update_post(slug_path: str, doc_id: str, tab_id: str, title: str) -> tuple[str, str, str, str | None]:
        url = f"{args.site}{slug_path}"
        try:
            set_subtitle(doc_id, args.account, url, title, tab_id)
            return "OK", url, title, None
        except Exception as exc:  # noqa: BLE001
            detail = getattr(exc, "read", lambda: b"")() or str(exc)
            return "FAIL", url, title, str(detail)

    print(f"\nUpdating with {workers} worker(s)...")
    with ThreadPoolExecutor(max_workers=workers) as executor:
        future_to_post = {
            executor.submit(update_post, slug_path, doc_id, tab_id, title): (doc_id, title)
            for slug_path, doc_id, tab_id, title in posts
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

    print(f"\nDone; {len(posts)} subtitle(s) set.")


if __name__ == "__main__":
    main()
