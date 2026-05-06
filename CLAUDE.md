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
