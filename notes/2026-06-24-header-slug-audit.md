# Header slug audit

Date: 2026-06-24.

Checked all 41 Google Docs linked from `public/index.html` by reading each Doc's real default page header via the Google Docs API (`documentStyle.defaultHeaderId` and `headers`). I compared the visible `myea.blog/<slug>` header text against the local homepage slug, then checked the actual text-run link attached to the visible URL.

## Changes Applied

The following Doc headers had newer canonical slugs than the local blog index, so the homepage hrefs, `llms.txt`, `all.txt`, and `vercel.json` redirects were updated:

| Old slug | New slug | Title |
|---|---|---|
| `virtue` | `let-die` | Should we let everyone die to stand by virtue? |
| `regret` | `stop-dread` | Stop feeling dread. Start feeling regret |
| `eag-playbook` | `success-playbook` | The EAG Playbook for Career Success |
| `ai-diffusion` | `identity-barrier` | Identity as a barrier to AI diffusion |
| `compound-on-your-own` | `cant-own` | You can't compound on your own |
| `art-engages` | `engaging-thing` | Art is the thing that engages you |

For each old slug, `vercel.json` now keeps a permanent redirect from the old URL to the new canonical slug, while the new canonical slug keeps the temporary Google Doc redirect.

## Header Link Repair

The six edited headers had correct visible text but still linked all or part of the visible URL to the old slug. I rewrote those six default page headers with `scripts/add_doc_headers.py`'s `set_header` helper so each header now displays `Find this post at myea.blog/<new-slug>` and links the visible URL to `https://myea.blog/<new-slug>`.

Final verification result: 41/41 linked Docs have matching local slug, header-visible slug, and header hyperlink target.
