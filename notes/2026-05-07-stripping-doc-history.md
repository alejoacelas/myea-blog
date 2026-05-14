# Stripping edit history from published blog Docs

## TL;DR

- **Version history is not the leak you think it is.** In Google Docs, `File → Version history` is visible only to **Editors**. Your blog Docs are shared "anyone with link, **commenter**", so the public literally cannot see who edited what or when. Jojo's name in the *edit log* is invisible to readers of myea.blog.
- **The real leak is comments and suggesting-mode edits.** Both show the author's name, and both are visible to commenters. Concrete example found in `1VNwliUBL3cJcYt4PGDgPu_4mby5ifaNTw5dtxRhvH3g` ("My pattern of disregarding…"): a comment by "Blitz" anchored to the literal text "Jojo" asks "pseudonym?". That comment exposes the real name to anyone with the link.
- **Cheapest fix: just delete the offending comments.** Same URL, single operation, no copies, no two-version problem.
- **Make-a-copy is overkill** for the version-history concern, but it's the only way to also wipe suggestions and any historical attribution that ever leaked in. It costs you a new URL and (with the API) loses comments.

## What's exposed at each share level

| To a viewer/commenter (public) | To an editor |
|---|---|
| Current doc text | Current doc text |
| Comments + comment authors | Comments + comment authors |
| Suggestions (suggester names) | Suggestions (suggester names) |
| — | Version history (every revision + author) |
| — | "Show editors" attribution overlay |

So if her name only ever appeared in versioning/edit attribution, you're already safe. If it ever appeared in a comment thread or suggestion, that survives until you delete it.

## Options

### Option A — Surgical comment deletion (recommended)

Same URL. Just remove the bad comments.

```
gdoc comments <doc-id>            # find offending comment IDs
gdoc delete-comment <doc-id> <comment-id>
```

Pros: no URL change, no duplicates, no lost comments other than the bad one.
Cons: doesn't help if her name was left in a *suggestion* (suggesting-mode edit) — those are different objects. Check by opening the doc with "Show suggested edits" on. If she has any pending suggestions, accept/reject them (which retires the attribution).

### Option B — Make a copy via API (what `gdoc cp` does)

What you get:
- New doc ID + URL.
- No edit history at all.
- **No comments preserved** (Drive API's `files.copy` doesn't carry comments).
- All current text intact.

Then: update `index.html` to point to the new URL, share new doc as commenter, and delete the original. End state = exactly one doc, clean.

Pros: nukes everything historical in one shot.
Cons: loses good comments too. Old URL breaks for anyone who shared it externally.

### Option C — Make a copy via Web UI with "Copy comments and suggestions"

Drive's `Make a copy` dialog has a checkbox for this; the API does not expose it. So this is a **manual** step.

What you get:
- New ID + URL.
- No version history.
- Comments and suggestions preserved, **with original author names attached**.

→ This does **not** solve the Jojo problem if her name is in comments — it carries the comments over verbatim. Only useful if your concern was strictly version history (in which case Option A solves it for free).

### Option D — Copy then re-add only good comments

Copy via API (no comments), then walk the original's comments, filter out bad ones, and re-post the rest via `gdoc comment`. Re-posted comments are attributed to **you**, not to the original commenters, which loses provenance but also strips Jojo. Anchoring to specific text in the new doc is fiddly.

Probably not worth the effort vs. Option A.

## Tests run

- **Test 1 — `gdoc cp` clean copy of "My pattern of disregarding…"**
  - Source: `1VNwliUBL3cJcYt4PGDgPu_4mby5ifaNTw5dtxRhvH3g`
  - Copy: <https://docs.google.com/document/d/1p9Ii6Ynh79AFgD9cjbalBDktEjap-XKuDq2kxngvqoA/edit>
  - Result: full text preserved, **0 comments**, no edit history, attributed to Alejo. Shared anyone-with-link reader for inspection.

## Recommended path

1. **For the immediate Jojo exposure**: run `gdoc comments <id>` on each post and `gdoc delete-comment` the ones that mention or are anchored to her name. Also accept/reject any pending suggestions from her account.
2. **If you also want to wipe edit history defensively** (paranoid mode, since commenters can't see it anyway): use Option B per post. Workflow:
   - `gdoc cp <old-id> "<sentence-case title>"`
   - `gog drive share <new-id> --to anyone --role commenter -y` (note: `gog drive share` only accepts reader/writer; for commenter use `gdoc share` with specific emails or set it manually in the UI — gap to fix in tooling)
   - Update `index.html` link
   - `gog drive trash <old-id>` once the new link is live and indexed
3. **Don't bother with Option C** — copies the very thing you're trying to remove.

## Open gap in tooling

`gog drive share --to anyone` only supports `reader|writer`, not `commenter`. To set anyone-with-link-comment programmatically, fall back to a raw Drive API call or set it in the UI.
