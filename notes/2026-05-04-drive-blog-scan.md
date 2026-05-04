# Drive scan for blog candidates — 2026-05-04

Scan of all Google Docs modified in the last 3 weeks (since 2026-04-13). Of 214 docs, after filtering by title (looks like a blog post) and ownership (`'me' in owners`), 3 new posts were added to **myea.blog** in chronological position. Several other candidates were excluded — listed below for review.

## Added to myea.blog (3)

| Date (modified) | Title (sentence-cased) | Doc |
|---|---|---|
| 2026-04-24 | True ambition has barely been tried | `1chD3B4uqrmBIvEi42A3mrAiVuETNcOstYMtVDcDCxy8` |
| 2026-04-22 | Sad kindness | `1buWVCvkzImqXQ_rUlC6BaycBpohDCS-XpVW_CfJHU3o` |
| 2026-04-22 | Heretical fiction | `1OCIiej4JOMdQ4zUBw4UyJM-R0hYf1vyOUj1SyiO2Pj0` |

All 3 are owned by you, no "Jojo" mentions in body, no obvious identity flags. Brief content notes:
- *Sad kindness* — personal essay about your grandfather, your dad's depression, the divorce, growing up in Bucaramanga. Names family but no Jojo/Robin. Decide if the family detail is OK to be public.
- *Heretical fiction* — pitches for fictional accounts (an SBF you root for, Jesus as strict utilitarian).
- *True ambition has barely been tried* — personal essay on EA ambition, mentions CEA, GiveWell, "true ambition" as a frame.

## Excluded — flagged for your review

### Jojo / Robin reveals

| Doc | Why excluded |
|---|---|
| **Jojo's Home** (`1rM3FluD9B6G_163nS6bwkV4TszBPmFi3A3DZRkS3dLc`) | Owned by you, but it's a planning doc *for* Jojo — her priorities, her GPI colleagues by name (Bob Fisher, Loren Fryxel, Oscar Delaney, "Charlotte? GPI girl"), her career and health context. Title alone reveals Jojo. Not a blog post. |
| **Things I don't know about Jojo** (`1Y4JV4FfjlEmAHD5x7rfiIYAuPpnRwKogVNsD6ugr8vQ`) | Already excluded earlier — heavy Jojo content in title and body. Unchanged. |
| **My Pattern of Disregarding People's Immediate Preferences** (`1VNwliUBL3cJcYt4PGDgPu_4mby5ifaNTw5dtxRhvH3g`) | Already excluded earlier — recounts a sensitive incident with Robin and her supervisor. Has 2 stray "Jojo" mentions that need rename if you ever publish. |

### Owned by you but not a personal blog post

| Doc | Why |
|---|---|
| **2026-03 Blog: TIAP2** (`1DZ8JSrwmOV_11SBmN2uzOceW-69ejsM6OcU2FbhAfGk`) | *Looks* like one (has "Blog" in title), but it's actually a FAR.AI conference recap you're drafting — destined for `far.ai/news/...`. Not your personal voice; skip from myea.blog. |

### Not owned by you (shared by colleagues, easy to mistake for blog posts)

These all have blog-post-style titles but the ownership check (`'me' in owners`) excluded them — they're someone else's drafts you've been cc'd on. Worth knowing about so the name doesn't trick a future scan.

| Doc | Title | Owner clue |
|---|---|---|
| `1CTr3ATsXThN-YiN8Mjt5VBtsGm2bYNPHSTqaQNrdqTk` | AI skills blog post April 2025 v3 | Penguin / 80K shared |
| `168mJ1ItZ13G9_BrKkYpE_4u6wcdEB-D9WqY0vUs8Wkc` | Schools Should Have Ads | someone else's opinion piece |
| `1jp1KZgW_ng5dVvc2OgaPuguI9wlIZr5CR_VbjfXjJOg` | Thoughts about unknown unknowns | research notes (not yours) |
| `1UygTBVS4iRhOvUEbOPQeTpkEkDzciRkvyV_DtfT876A` | Thoughts about overvaluation of speculative interventions | research notes (not yours) |
| `1wseeiWdXJA1DXERH3qkgSPGFMTeBUgHWNziQsjcZ3ZY` | Death and Treatment Effects | research notes (not yours) |
| `1QqZxTE62N5PoMrZjIRSCplkfgtQfwRYl0ZMk0ruq9CI` | Rethinking AI Safety Career Development | working group strategy memo |
| `1g6mjKW8mFbKvhRb4E2VuUtp0dpfPuqPTJV40P9NNn4U` | Some Barc Diary entries | **Robin's diary** — internal-dialogue entries about her own struggles at GPI, her productivity shame, her time in Toulouse and Barcelona. Heavily reveals her even though "Jojo" never appears. Definitely not for the public blog. |

## Process notes

- Filter used: `modifiedTime > '2026-04-13T00:00:00' and mimeType = 'application/vnd.google-apps.document' and trashed = false and 'me' in owners` → 99 docs (down from 214 unfiltered).
- The ownership filter is what kept several blog-titled docs (above) out — added a note to `myea-blog/CLAUDE.md` so future scans always include it.
- Final myea.blog count: 14 → **17 posts**, in true chronological order (newest at top).
