# Programmatically adding a page header to a Google Doc — experiment report

Date: 2026-06-24. Goal: find the best way to add a running **page header** (the header region that repeats at the top of each page) to a blog-post Google Doc, with text like `Find this post at https://myea.blog/<slug>` and a working hyperlink. Done hands-on against a throwaway test Doc (created and moved to Drive trash at the end).

## TL;DR / Recommendation

- **`gdoc` CLI cannot do it.** No subcommand touches the header region (checked every subcommand's help).
- **Use the Google Docs REST API**: `documents.batchUpdate` with `createHeader` (type `DEFAULT`) → capture the returned `headerId` → second `batchUpdate` with `insertText` (targeting `segmentId = headerId`, `index: 0`) plus `updateTextStyle` to apply the hyperlink. This produces a **real page header**, confirmed by reading it back via `documents.get?fields=headers`.
- **Body extraction is NOT polluted** for the path this project actually uses. `gdoc cat ... --no-images --quiet` (exactly what `scripts/build_llms_txt.py` calls) and `gog docs export --format md` both return body-only output with zero header leakage. **Caveat:** `gog docs export --format txt` DOES leak the header (it lands as the first line). The project doesn't use the txt path, so this is safe — but worth knowing.
- **Auth:** needs the `https://www.googleapis.com/auth/documents` scope. The user's `gog` `docs` service already has it (scopes: `auth/drive` + `auth/documents`), so no re-consent is needed.

## 1. Can `gdoc` set/insert text into the page-header region?

**No.** `gdoc`'s subcommands are: `update auth ls find cat tabs cells toc add-tab edit write insert pull push comments comment reply resolve reopen delete-comment comment-info images info share new cp`. Grepping every subcommand's `--help` for "header" returns nothing. `insert`/`write` only operate on tab *bodies* (`--position {start,end}` of the tab body). There is no header/footer concept anywhere in the CLI.

## 2. The Google Docs API approach (tested, working)

Three-step flow, two `batchUpdate` calls:

1. `createHeader` with `type: "DEFAULT"` → returns `replies[0].createHeader.headerId` (e.g. `kix.d6aysmczvxob`).
2. `insertText` at `{segmentId: <headerId>, index: 0}` — header text starts at **index 0** (not 1 like the body; the first text run's `startIndex` reads back as absent/0).
3. `updateTextStyle` over `{segmentId: <headerId>, startIndex: len(prefix), endIndex: len(prefix)+len(url)}` with `textStyle.link.url` and `fields: "link"`.

### Index gotcha (cost me one iteration)

Header segment text is **0-indexed**. With prefix `"Find this post at "` (18 chars) and inserting at index 0, the URL link range is `[18, 18+len(url))`. My first attempt used `[19, ...]` (assuming a body-style index-1 start) and the link began one char late ("ttps://..." instead of "https://..."). Read-back via `documents.get` is how I caught it. The script below has the correct math.

### Read-back confirmation (final, correct run)

`GET documents/<id>?fields=headers` returned one header segment with runs:

```
text='Find this post at '            link=None
text='https://myea.blog/test-slug'   link={'url': 'https://myea.blog/test-slug'}
```

Link cleanly covers the whole URL; prefix unlinked. This is a genuine header region, not body text.

### Reusable script (parameterized by doc ID + URL)

Saved during the experiment as a PEP-723 `uv run` script. It mints a fresh access token from the `gog`-stored refresh token + OAuth client, so it needs no manual token handling:

```python
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Add a DEFAULT page header to a Google Doc with a hyperlinked URL.
Usage: uv run add_header.py <DOC_ID> <URL> [--text-prefix "Find this post at "] [--account EMAIL]
"""
import argparse, json, subprocess, os, tempfile, urllib.request, urllib.parse, pathlib

GOG_CRED = pathlib.Path(os.path.expanduser("~/Library/Application Support/gogcli/credentials.json"))

def get_access_token(account):
    with tempfile.TemporaryDirectory() as td:
        rt_path = os.path.join(td, "rt.json")
        subprocess.run(["gog","auth","tokens","export",account,"--out",rt_path,"--overwrite"],
                       check=True, capture_output=True, text=True)
        rt = json.load(open(rt_path))
    cred = json.load(open(GOG_CRED)); cred = cred.get("installed") or cred.get("web") or cred
    data = urllib.parse.urlencode({"client_id":cred["client_id"],"client_secret":cred["client_secret"],
                                   "refresh_token":rt["refresh_token"],"grant_type":"refresh_token"}).encode()
    return json.load(urllib.request.urlopen(urllib.request.Request("https://oauth2.googleapis.com/token", data=data)))["access_token"]

def batch_update(doc_id, token, requests):
    req = urllib.request.Request(f"https://docs.googleapis.com/v1/documents/{doc_id}:batchUpdate",
                                 data=json.dumps({"requests":requests}).encode(),
                                 headers={"Authorization":f"Bearer {token}","Content-Type":"application/json"})
    return json.load(urllib.request.urlopen(req))

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("doc_id"); ap.add_argument("url")
    ap.add_argument("--text-prefix", default="Find this post at ")
    ap.add_argument("--account", default="alejoacelas@gmail.com")
    a = ap.parse_args()
    token = get_access_token(a.account)
    header_id = batch_update(a.doc_id, token, [{"createHeader":{"type":"DEFAULT"}}])["replies"][0]["createHeader"]["headerId"]
    text = f"{a.text_prefix}{a.url}"; ls = len(a.text_prefix); le = ls + len(a.url)
    batch_update(a.doc_id, token, [
        {"insertText":{"location":{"segmentId":header_id,"index":0},"text":text}},
        {"updateTextStyle":{"range":{"segmentId":header_id,"startIndex":ls,"endIndex":le},
                            "textStyle":{"link":{"url":a.url}},"fields":"link"}}])
    print(json.dumps({"ok":True,"headerId":header_id,"text":text,"link_range":[ls,le]}))

if __name__ == "__main__":
    main()
```

Run: `uv run add_header.py <DOC_ID> https://myea.blog/<slug>`

### Equivalent raw-curl version (if you'd rather not use the script)

```bash
AT=<access-token-with-documents-scope>
DOC=<doc-id>
# Step 1: create header, capture headerId from replies[0].createHeader.headerId
curl -s -X POST "https://docs.googleapis.com/v1/documents/${DOC}:batchUpdate" \
  -H "Authorization: Bearer ${AT}" -H "Content-Type: application/json" \
  -d '{"requests":[{"createHeader":{"type":"DEFAULT"}}]}'
# Step 2: insert text + link (HID = headerId from step 1; 18 = len("Find this post at "))
curl -s -X POST "https://docs.googleapis.com/v1/documents/${DOC}:batchUpdate" \
  -H "Authorization: Bearer ${AT}" -H "Content-Type: application/json" \
  -d '{"requests":[
        {"insertText":{"location":{"segmentId":"HID","index":0},"text":"Find this post at https://myea.blog/SLUG"}},
        {"updateTextStyle":{"range":{"segmentId":"HID","startIndex":18,"endIndex":40},
                            "textStyle":{"link":{"url":"https://myea.blog/SLUG"}},"fields":"link"}}]}'
```

Idempotency note: re-running `createHeader` on a doc that already has a DEFAULT header errors. For a re-runnable workflow, first `documents.get?fields=headers`; if a header exists, either `deleteHeader` (tested, works: `{"deleteHeader":{"headerId":"..."}}`) and recreate, or clear/replace its text in place. `documentStyle.defaultHeaderId` tells you the active one.

## 3. Body-pollution finding (the load-bearing concern)

After adding the header, on the same test doc:

| Extraction method | Header text in output? |
|---|---|
| `gdoc cat <id>` | **No** (count 0) |
| `gdoc cat <id> --no-images --quiet` (← exact flags in `scripts/build_llms_txt.py`) | **No** (count 0) |
| `gog docs export --format md` | **No** (count 0) |
| `gog docs export --format txt` | **Yes** — header is the first line |

`scripts/build_llms_txt.py` reads bodies via `subprocess.run(["gdoc","cat",doc_id,"--no-images","--quiet"], ...)`. That path is clean, so **adding page headers will not contaminate `llms.txt` / `all.txt`.** The only leaky path is the plain-text export, which the project does not use. (Plausible reason: txt is a flat dump that inlines header/footer regions; md and the gdoc structured walk keep them separate.)

## 4. Auth / scope requirements

- The Docs API write (`batchUpdate`) requires `https://www.googleapis.com/auth/documents`.
- `gog auth services` shows the `docs` service is authorized with `auth/drive` + `auth/documents`. Verified by minting a token and confirming `documents` is in the returned `scope`.
- Token-minting path used: `gog auth tokens export <email> --out <file> --overwrite` gives the refresh token; OAuth client (`client_id`/`client_secret`) is in `~/Library/Application Support/gogcli/credentials.json`; exchange at `https://oauth2.googleapis.com/token` (grant_type=refresh_token) yields a ~1h access token. The script does this automatically per run. The exported refresh-token file contains a secret — the script writes it to a temp dir and deletes it; in the manual run I trashed it afterward.

## Cleanup done

- Test doc `1MENLvluc__TeFsKL3FgVCU-a0rMyy0Oc4vG2KhqnHQw` moved to Drive trash via `gog drive delete -y` (`trashed: true`, `deleted: false` — not permanently deleted).
- Exported refresh-token and access-token files trashed; transient `gog` drive-downloads trashed.
- No real document was touched.
