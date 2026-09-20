# Blog decisions

## Core decisions

### Publish only intended writing

- [Verify ownership, sharing and the pseudonym guard before inclusion](#verify-ownership-sharing-and-the-pseudonym-guard-before-inclusion).
- [Classify posts by their form and preserve the editorial ordering](#classify-posts-by-their-form-and-preserve-the-editorial-ordering).

### Keep links and derived text consistent

- [Treat the linked document subtitle as the canonical slug](#treat-the-linked-document-subtitle-as-the-canonical-slug).
- [Regenerate text from sources after index or document changes](#regenerate-text-from-sources-after-index-or-document-changes).

## Details

### Verify ownership, sharing and the pseudonym guard before inclusion

[AGENTS.md](AGENTS.md) requires Alejo-owned writing with the intended commenter access, excludes Jojo’s own writing and guards the private name in titles and bodies. The [text builder](scripts/build_llms_txt.py) aborts on the guarded name. A document being discoverable or recently edited is not enough to publish it.

### Classify posts by their form and preserve the editorial ordering

Use only draft, bullet points or cross-post. Coherent pieces count as drafts even when they contain bullets. Sort by Drive modification time, subject to the rule that inserted notes/cross-posts cannot lead and at most two sit between drafts; this keeps the homepage centered on sustained writing.

### Treat the linked document subtitle as the canonical slug

The [subtitle sync](scripts/sync_doc_subtitles.py) and [routing configuration](vercel.json) connect a stable Doc identity to a readable URL. If a served slug changes, retain a permanent redirect from the old route. Analytics should continue to key on the stable Doc ID.

### Regenerate text from sources after index or document changes

Edit [open-problems.md](open-problems.md) and the post index; generate Open Problems, llms.txt and all.txt with the existing scripts. Update modification times and order even when no new post is added. Cached unchanged Docs are an optimization, not authority to leave changed prose stale.
