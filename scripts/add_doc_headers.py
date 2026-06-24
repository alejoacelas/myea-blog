# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Write a "Find this post at <url>" running page header into each post Doc.

For every post linked from public/index.html, sets the Google Doc's DEFAULT
page-header region (NOT body text) to:

    Find this post at https://myea.blog/<slug>

with the URL hyperlinked. Idempotent: if the Doc already has a default
header, it is deleted and recreated, so re-running is safe.

RUN THIS AT DEPLOY TIME, AFTER the /<slug> redirects are live in production
(otherwise the header links 404). The page header does NOT leak into the
`gdoc cat` body extraction used by build_llms_txt.py, so the LLM text files
do not need regenerating for this change. See
notes/2026-06-24-gdoc-header-experiment.md for the method writeup.

    uv run scripts/add_doc_headers.py --dry-run       # preview
    uv run scripts/add_doc_headers.py                 # all posts
    uv run scripts/add_doc_headers.py --only immortal # one post (slug/id/title)

Requires the Google Docs write scope (auth/documents); the user's `gog`
`docs` service already has it. Only the DEFAULT header is managed; a Doc
configured with a distinct first-page header is left untouched there.
"""
import argparse
import json
import os
import re
import subprocess
import sys
import tempfile
import urllib.parse
import urllib.request
from pathlib import Path

SITE = "https://myea.blog"
PREFIX = "Find this post at "
INDEX = Path(__file__).resolve().parent.parent / "public" / "index.html"
GOG_CRED = Path("~/Library/Application Support/gogcli/credentials.json").expanduser()

POST_RE = re.compile(
    r'href="(/[\w-]+)" data-doc="([\w-]+)"[^>]*>\s*'
    r'<span class="post-title">(.*?)</span>',
    re.S,
)


def get_access_token(account: str) -> str:
    with tempfile.TemporaryDirectory() as td:
        rt_path = os.path.join(td, "rt.json")
        subprocess.run(
            ["gog", "auth", "tokens", "export", account, "--out", rt_path, "--overwrite"],
            check=True, capture_output=True, text=True,
        )
        rt = json.load(open(rt_path))
    cred = json.load(open(GOG_CRED))
    cred = cred.get("installed") or cred.get("web") or cred
    data = urllib.parse.urlencode({
        "client_id": cred["client_id"],
        "client_secret": cred["client_secret"],
        "refresh_token": rt["refresh_token"],
        "grant_type": "refresh_token",
    }).encode()
    resp = urllib.request.urlopen(
        urllib.request.Request("https://oauth2.googleapis.com/token", data=data)
    )
    return json.load(resp)["access_token"]


def api_get(doc_id: str, token: str, fields: str) -> dict:
    url = f"https://docs.googleapis.com/v1/documents/{doc_id}?fields={urllib.parse.quote(fields)}"
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}"})
    return json.load(urllib.request.urlopen(req))


def batch_update(doc_id: str, token: str, requests: list) -> dict:
    req = urllib.request.Request(
        f"https://docs.googleapis.com/v1/documents/{doc_id}:batchUpdate",
        data=json.dumps({"requests": requests}).encode(),
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
    )
    return json.load(urllib.request.urlopen(req))


def set_header(doc_id: str, token: str, url: str) -> str:
    text = f"{PREFIX}{url}"
    style = api_get(doc_id, token, "documentStyle").get("documentStyle", {})
    existing = style.get("defaultHeaderId")
    if existing:
        batch_update(doc_id, token, [{"deleteHeader": {"headerId": existing}}])
    header_id = batch_update(doc_id, token, [{"createHeader": {"type": "DEFAULT"}}])[
        "replies"
    ][0]["createHeader"]["headerId"]
    batch_update(doc_id, token, [
        {"insertText": {"location": {"segmentId": header_id, "index": 0}, "text": text}},
        {"updateTextStyle": {
            "range": {"segmentId": header_id, "startIndex": len(PREFIX), "endIndex": len(text)},
            "textStyle": {"link": {"url": url}},
            "fields": "link",
        }},
    ])
    return header_id


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--account", default="alejoacelas@gmail.com")
    ap.add_argument("--only", help="limit to posts whose slug, doc id, or title contains this")
    ap.add_argument("--site", default=SITE, help="base URL for the header link")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()

    posts = POST_RE.findall(INDEX.read_text())
    if not posts:
        sys.exit("No posts found in index.html — check POST_RE")
    if a.only:
        needle = a.only.lower().lstrip("/")
        posts = [p for p in posts if needle in (p[0].lstrip("/") + " " + p[1] + " " + p[2]).lower()]
        if not posts:
            sys.exit(f"--only {a.only!r} matched no posts")

    print(f"{len(posts)} post(s) to update:")
    for slug_path, _doc_id, title in posts:
        print(f"  {a.site}{slug_path}  <-  {title}")
    if a.dry_run:
        print("\n(dry run — nothing written)")
        return

    token = get_access_token(a.account)
    failures = []
    for slug_path, doc_id, title in posts:
        url = f"{a.site}{slug_path}"
        try:
            set_header(doc_id, token, url)
            print(f"  OK   {url}")
        except Exception as e:  # noqa: BLE001 — report and continue
            detail = getattr(e, "read", lambda: b"")() or str(e)
            failures.append((title, doc_id, detail))
            print(f"  FAIL {url} — {detail}")

    if failures:
        print(f"\n{len(failures)} failed:")
        for title, doc_id, detail in failures:
            print(f"  - {title} ({doc_id}): {detail}")
        sys.exit(1)
    print(f"\nDone — {len(posts)} header(s) set.")


if __name__ == "__main__":
    main()
