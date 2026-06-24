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
import re
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

SITE_DIR = Path(__file__).resolve().parent.parent / "public"
SITE = "https://myea.blog"
ALL_POSTS_FILENAME = "all.txt"
DEFAULT_WORKERS = 8

POST_RE = re.compile(
    r'<a class="post-link" href="([^"]+)"(?: data-doc="([\w-]+)")?[^>]*>\s*'
    r'<span class="post-title">(.*?)</span>',
    re.S,
)

DOC_URL_RE = re.compile(r"/document/d/([\w-]+)")


def fetch_doc(doc_id: str) -> str:
    result = subprocess.run(
        ["gdoc", "cat", doc_id, "--no-images", "--quiet"],
        capture_output=True,
        text=True,
        check=True,
    )
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
    args = parser.parse_args()

    html = (SITE_DIR / "index.html").read_text()
    raw_posts = POST_RE.findall(html)
    if not raw_posts:
        sys.exit("No posts found in index.html — check POST_RE")

    posts: list[tuple[str, str, str]] = []
    for href, data_doc, title in raw_posts:
        doc_id = data_doc
        if not doc_id:
            match = DOC_URL_RE.search(href)
            doc_id = match.group(1) if match else ""
        if not doc_id:
            sys.exit(f"No Google Doc id found for post: {title}")
        source_url = f"{SITE}{href}" if href.startswith("/") else href
        posts.append((source_url, doc_id, title))

    print(f"Found {len(posts)} posts in index.html")

    bodies: list[str | None] = [None] * len(posts)
    jojo_hits: list[tuple[int, str]] = []

    def fetch_post(index: int, url: str, doc_id: str, title: str) -> tuple[int, str, str | None]:
        text = fetch_doc(doc_id)
        jojo_hit = title if re.search(r"jojo", text, re.I) else None
        # gdoc may emit a tab label before the document title. Drop that and
        # then drop the document's own H1 because we add the index title.
        text = re.sub(r"\A#\s+Tab\s+\d+\n+", "", text, flags=re.I)
        text = re.sub(r"\A#\s+.*?\n+", "", text)
        return index, f"# {title}\n\nSource: {url}\n\n{text}", jojo_hit

    workers = max(1, min(args.workers, len(posts)))
    print(f"Fetching with {workers} worker(s)")
    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = []
        for index, (url, doc_id, title) in enumerate(posts):
            print(f"  fetching: {title}")
            futures.append(executor.submit(fetch_post, index, url, doc_id, title))
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

    index_lines = [f"- [{title}]({url})" for url, _, title in posts]
    index = (
        header
        + "\n## Full text\n\n"
        + f"- [All posts in one file]({SITE}/{ALL_POSTS_FILENAME})\n"
        + "\n## Posts\n\n"
        + "\n".join(index_lines)
        + "\n"
    )
    (SITE_DIR / "llms.txt").write_text(index)

    print(f"Wrote {ALL_POSTS_FILENAME} ({len(full):,} chars) and llms.txt")


if __name__ == "__main__":
    main()
