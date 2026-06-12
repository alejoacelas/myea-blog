# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Build llms.txt and llms-full.txt from the posts listed in index.html.

Reads every Google Doc linked from index.html (via the `gdoc` CLI) and
concatenates the full text into llms-full.txt, newest first, matching the
order on the page. Also writes llms.txt, the conventional short index.

Run from the repo root after adding a post to index.html:

    uv run scripts/build_llms_txt.py

Aborts if any post body mentions "Jojo" (must be rewritten to "Robin"
before the text can be published — see CLAUDE.md).
"""

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE = "https://myea.blog"

POST_RE = re.compile(
    r'href="(https://docs\.google\.com/document/d/([\w-]+)/edit)"[^>]*>\s*'
    r'<span class="post-title">(.*?)</span>',
    re.S,
)


def fetch_doc(doc_id: str) -> str:
    result = subprocess.run(
        ["gdoc", "cat", doc_id, "--no-images", "--quiet"],
        capture_output=True,
        text=True,
        check=True,
    )
    text = result.stdout
    # gdoc leaves base64 image definitions and refs behind; strip them
    # (they bloat the file and their base64 can false-positive name scans).
    text = re.sub(r"^\[image\d+\]:\s*<data:.*$", "", text, flags=re.M)
    text = re.sub(r"!?\[\]\[image\d+\]", "", text)
    return re.sub(r"\n{3,}", "\n\n", text).strip()


def main() -> None:
    html = (ROOT / "index.html").read_text()
    posts = POST_RE.findall(html)
    if not posts:
        sys.exit("No posts found in index.html — check POST_RE")

    print(f"Found {len(posts)} posts in index.html")

    bodies = []
    jojo_hits = []
    for url, doc_id, title in posts:
        print(f"  fetching: {title}")
        text = fetch_doc(doc_id)
        if re.search(r"jojo", text, re.I):
            jojo_hits.append(title)
        # Drop a leading H1 if it duplicates the post title; we add our own.
        text = re.sub(r"\A#\s+.*?\n+", "", text)
        bodies.append(f"# {title}\n\nSource: {url}\n\n{text}")

    if jojo_hits:
        sys.exit(
            "ABORTING — 'Jojo' found in the body of: "
            + ", ".join(jojo_hits)
            + ". Rewrite to 'Robin' in the Doc, then re-run."
        )

    header = (
        "# My EA Blog\n\n"
        f"> Personal essays and drafts by Alejandro Acelas ({SITE}). "
        "This file contains the full text of every post, newest first. "
        "All posts are drafts.\n"
    )

    full = header + "\n---\n\n" + "\n\n---\n\n".join(bodies) + "\n"
    (ROOT / "llms-full.txt").write_text(full)

    index_lines = [f"- [{title}]({url})" for url, _, title in posts]
    index = (
        header
        + "\n## Full text\n\n"
        + f"- [All posts in one file]({SITE}/llms-full.txt)\n"
        + "\n## Posts\n\n"
        + "\n".join(index_lines)
        + "\n"
    )
    (ROOT / "llms.txt").write_text(index)

    print(f"Wrote llms-full.txt ({len(full):,} chars) and llms.txt")


if __name__ == "__main__":
    main()
