# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Build llms.txt and all.txt from the posts listed in index.html.

Reads every Google Doc linked from index.html (via the `gdoc` CLI) and
concatenates the full text into all.txt, newest first, matching the
order on the page. Also writes llms.txt, the conventional short index.

Run from the repo root after adding a post to index.html:

    uv run scripts/build_llms_txt.py

Aborts if any post body mentions "Jojo" (must be rewritten to "Robin"
before the text can be published — see CLAUDE.md).
"""

import argparse
import json
import re
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

SITE_DIR = Path(__file__).resolve().parent.parent / "public"
SITE = "https://myea.blog"
ALL_POSTS_FILENAME = "all.txt"
DEFAULT_WORKERS = 8
CACHE = Path(__file__).resolve().parent.parent / ".llms-build-cache.json"

POST_RE = re.compile(
    r'<li[^>]*data-modified-time="([^"]+)"[^>]*>\s*'
    r'<a class="post-link" href="([^"]+)"(?: data-doc="([\w-]+)")?'
    r'(?: data-tab="([\w.-]+)")?[^>]*>\s*'
    r'<span class="post-title">(.*?)</span>',
    re.S,
)

DOC_URL_RE = re.compile(r"/document/d/([\w-]+)")


def previous_bodies() -> dict[str, str]:
    """Return already-generated post sections, keyed by their source URL."""
    path = SITE_DIR / ALL_POSTS_FILENAME
    if not path.exists():
        return {}
    full = path.read_text()
    starts = list(re.finditer(r"(?m)^# .+\n\nSource: (\S+)\n", full))
    bodies = {}
    for index, match in enumerate(starts):
        end = starts[index + 1].start() if index + 1 < len(starts) else len(full)
        section = full[match.start():end]
        section = re.sub(r"\n\n---\n\n\Z", "", section).rstrip()
        bodies[match.group(1)] = section
    return bodies


def read_cache() -> dict[str, dict[str, str]]:
    if not CACHE.exists():
        return {}
    try:
        data = json.loads(CACHE.read_text())
    except (json.JSONDecodeError, OSError):
        return {}
    return data.get("posts", {}) if data.get("version") == 1 else {}


def fetch_doc(doc_id: str, tab_id: str) -> str:
    result = None
    for attempt in range(3):
        result = subprocess.run(
            ["gdoc", "cat", doc_id, "--no-images", "--quiet"]
            + (["--tab", tab_id] if tab_id else []),
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            break
        if attempt < 2:
            time.sleep(0.5 * (2**attempt))
    if result is None or result.returncode:
        detail = (result.stderr if result else "gdoc did not run").strip()
        raise RuntimeError(f"gdoc failed for {doc_id}: {detail}")
    text = result.stdout
    text = re.sub(r"\AUpdate available:.*\n", "", text)
    text = re.sub(r"\Aaccount:.*\n", "", text)
    # gdoc leaves base64 image definitions and refs behind; strip them
    # (they bloat the file and their base64 can false-positive name scans).
    text = re.sub(r"^\[image\d+\]:\s*<data:.*$", "", text, flags=re.M)
    text = re.sub(r"!?\[\]\[image\d+\]", "", text)
    text = "\n".join(line.rstrip() for line in text.splitlines())
    return re.sub(r"\n{3,}", "\n\n", text).strip()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workers", type=int, default=DEFAULT_WORKERS, help="parallel Doc fetches")
    parser.add_argument("--full", action="store_true", help="fetch every Doc instead of reusing unchanged text")
    args = parser.parse_args()

    html = (SITE_DIR / "index.html").read_text()
    raw_posts = POST_RE.findall(html)
    if not raw_posts:
        sys.exit("No posts found in index.html — check POST_RE")

    posts: list[tuple[str, str, str, str, str]] = []
    for modified_time, href, data_doc, tab_id, title in raw_posts:
        doc_id = data_doc
        if not doc_id:
            match = DOC_URL_RE.search(href)
            doc_id = match.group(1) if match else ""
        if not doc_id:
            sys.exit(f"No Google Doc id found for post: {title}")
        source_url = f"{SITE}{href}" if href.startswith("/") else href
        posts.append((source_url, doc_id, title, modified_time, tab_id))

    print(f"Found {len(posts)} posts in index.html")

    bodies: list[str | None] = [None] * len(posts)
    jojo_hits: list[tuple[int, str]] = []
    old_bodies = previous_bodies()
    cache = read_cache()
    reused = 0

    for index, (url, doc_id, title, modified_time, tab_id) in enumerate(posts):
        cached = cache.get(f"{doc_id}:{tab_id}")
        if cached is None and not tab_id:
            cached = cache.get(doc_id, {})
        cached = cached or {}
        body = old_bodies.get(url)
        if not args.full and body and cached.get("modified_time") == modified_time:
            bodies[index] = body
            reused += 1
            if re.search(r"jojo", body, re.I):
                jojo_hits.append((index, title))

    def fetch_post(index: int, url: str, doc_id: str, tab_id: str, title: str) -> tuple[int, str, str | None]:
        text = fetch_doc(doc_id, tab_id)
        jojo_hit = title if re.search(r"jojo", text, re.I) else None
        # gdoc may emit a tab label before the document title. Drop that and
        # then drop the document's own H1 because we add the index title.
        text = re.sub(r"\A#\s+Tab\s+\d+\n+", "", text, flags=re.I)
        text = re.sub(r"\A#\s+.*?\n+", "", text)
        text = re.sub(
            rf"\A#\s+{re.escape(title)}\s*\n+", "", text, flags=re.I
        )
        text = re.sub(rf"\A{re.escape(title)}\s*\n+", "", text, flags=re.I)
        # The public URL already appears in Source; omit the linked Doc subtitle.
        text = re.sub(
            r"(?m)^#{0,2}\s*\[?myea\.blog/[\w-]+\]?(?:\(https://myea\.blog/[\w-]+\))?\s*\n+",
            "",
            text,
            count=1,
        )
        text = re.sub(r"(?m)^#{1,6}\s*$\n?", "", text)
        return index, f"# {title}\n\nSource: {url}\n\n{text}", jojo_hit

    pending = [
        (index, url, doc_id, title, tab_id)
        for index, (url, doc_id, title, _modified_time, tab_id) in enumerate(posts)
        if bodies[index] is None
    ]
    print(f"Reusing {reused} unchanged post(s); fetching {len(pending)}")
    if pending:
        workers = max(1, min(args.workers, len(pending)))
        print(f"Fetching with {workers} worker(s)")
        with ThreadPoolExecutor(max_workers=workers) as executor:
            futures = []
            for index, url, doc_id, title, tab_id in pending:
                print(f"  fetching: {title}")
                futures.append(executor.submit(fetch_post, index, url, doc_id, tab_id, title))
            for future in as_completed(futures):
                index, body, jojo_hit = future.result()
                bodies[index] = body
                if jojo_hit:
                    jojo_hits.append((index, jojo_hit))

    if jojo_hits:
        jojo_hits.sort()
        sys.exit(
            "ABORTING — 'Jojo' found in the body of: "
            + ", ".join(title for _, title in jojo_hits)
            + ". Rewrite to 'Robin' in the Doc, then re-run."
        )

    if any(body is None for body in bodies):
        sys.exit("ABORTING — one or more posts failed to fetch.")
    ordered_bodies = [body for body in bodies if body is not None]

    header = (
        "# My EA Blog\n\n"
        f"> Personal essays, drafts, cross-posts, and bullet-point notes by Alejandro Acelas ({SITE}). "
        "This file contains the full text of every post, newest first.\n"
    )

    full = header + "\n---\n\n" + "\n\n---\n\n".join(ordered_bodies) + "\n"
    (SITE_DIR / ALL_POSTS_FILENAME).write_text(full)

    index_lines = [f"- [{title}]({url})" for url, _, title, _, _ in posts]
    index = (
        header
        + "\n## Full text\n\n"
        + f"- [All posts in one file]({SITE}/{ALL_POSTS_FILENAME})\n"
        + "\n## Posts\n\n"
        + "\n".join(index_lines)
        + "\n"
    )
    (SITE_DIR / "llms.txt").write_text(index)

    CACHE.write_text(
        json.dumps(
            {
                "version": 1,
                "posts": {
                    f"{doc_id}:{tab_id}": {"modified_time": modified_time, "source_url": url}
                    for url, doc_id, _title, modified_time, tab_id in posts
                },
            },
            indent=2,
            sort_keys=True,
        )
        + "\n"
    )

    print(f"Wrote {ALL_POSTS_FILENAME} ({len(full):,} chars) and llms.txt")


if __name__ == "__main__":
    main()
