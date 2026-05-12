# myea.blog

Single-page index of writing drafts. Each entry links to a Google Doc.

## Stack

- Plain `index.html`. No framework, no build step.

## Deployment

- **Platform:** Vercel
- **Project:** `2026-04-10-my-ea-blog` (org `alejandros-projects-a115cc74`)
- **Domain:** myea.blog
- **Deploy:** `vercel deploy --prod` from this directory.

## Conventions

- **Post titles:** start from the **Google Doc's actual title** (run `gdoc info <doc-id>` to fetch), then **sentence-case** it — only the first word and proper nouns (names, AI, EV, EA, Robin, Toulouse, Claude, etc.) keep capitals. Don't paraphrase the title even if the Doc one is rough; just lowercase the non-proper words.
- **Draft tags:** every entry shows `[draft]`. Don't introduce new variants like `[really unpolished draft]`.
- **Order:** newest at the top. **Preserve the existing order of posts already in `index.html`** — the order reflects when each was *drafted*, not when it was last edited. The user routinely re-edits old Docs to polish them; using `modifiedTime` to sort would bounce old posts back to the top, which he doesn't want. When adding a new post, insert it at the chronological position implied by its first-publish date (use the Doc's `createdTime` if you need a reference, or just place it relative to the surrounding posts you can date), then leave everything else untouched.
- **Ownership check:** before adding any new post, confirm Alejo *owns* the Doc — many docs in his Drive are shared by friends/colleagues and just look like blog posts by title. Use Drive query `'me' in owners` (e.g., `gog drive search --raw-query "... and 'me' in owners"`).
- **Jojo / Robin guard:** never publish a post whose **title** contains "Jojo" (her real name); never publish a post that's actually her writing rather than Alejo's; check the body for "Jojo" mentions and flag any rewrite needs (the pseudonym in public is **Robin**).
- **Preserve old URLs:** whenever you rename, move, or remove a page (e.g. renaming `live-with-me.html` to `housing.html`, or changing a route slug), add a redirect in `vercel.json` from the old path to the new one so existing bookmarks and shared links keep working. Use the `redirects` array with `permanent: true`. Don't skip this even when the old link "probably isn't shared anywhere" — the cost of adding a redirect is trivial and the cost of a broken link surfacing later is not.

## Sweep workflow — publishing new drafts

When asked to sweep Drive for new posts and publish them, follow this order:

1. **Find the cutoff.** Read the topmost Doc ID in `index.html`, then `gog drive get <id> --select createdTime` to get its `createdTime`. That timestamp is the cutoff — only consider Docs created strictly after it.
2. **Query Drive.** `gog drive search --raw-query "'me' in owners and createdTime > '<cutoff>' and mimeType = 'application/vnd.google-apps.document'" --max 100 -j --results-only --select "id,name,createdTime"`. The `'me' in owners` clause enforces the ownership rule — don't drop it.
3. **Filter by title.** Drop anything obviously not a blog post: `Call`/`Meeting`/`Transcript`/`Summary`, `Invoice`, `EOI`/`Application`/`Expression of Interest`, `Untitled document`, contact-list-style names (`<X> <> <Y>`), and anything already linked from `index.html`. What remains is the candidate set.
4. **Read each candidate** with `gdoc cat <id>` and decide: essay-style personal writing → publish; form-fill / job application / reading list / scratch notes → skip. Borderline recruiting docs that reference `myea.blog` and read like an essay (e.g. "What I'm looking for in my next manager") count as blog posts.
5. **Run the Jojo / Robin guard** on each survivor — check both the title and the body for "Jojo". Title hit → skip outright. Body hit → flag to the user before publishing and offer to rewrite the mention to "Robin".
6. **Confirm comment access.** `gog drive permissions <id> -j --results-only` and look for `{"id": "anyoneWithLink", "role": "commenter", "type": "anyone"}`. If missing, fix in the Drive UI — `gog drive share --to=anyone --role=...` only supports `reader|writer`, not `commenter`, so the CLI can't set this directly. Flag any doc you couldn't bring up to commenter so the user can do it manually.
7. **Insert into `index.html`** above the previous newest entry, sorted by `createdTime` descending among the new batch. Apply the sentence-case rule from the Conventions section.
8. **Report skipped candidates** at the end of the run (with a one-line reason for each) so the user can sanity-check the filter. This is especially important for borderline docs you chose not to publish.
9. **Deploy + commit.** `vercel deploy --prod`, then a git commit summarizing the new posts.
