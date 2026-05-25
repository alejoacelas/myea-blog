# Drive blog sweep - 2026-05-25

Cutoff: newest published doc before this sweep was `The Giving Tree` (`1AGnij3eQ7Dgn1caTaU4pjJcsLpdc-QEyfTLYEfmpIOA`), created `2026-05-10T08:46:47.825Z`.

Drive query:

```text
'me' in owners and createdTime > '2026-05-10T08:46:47.825Z' and mimeType = 'application/vnd.google-apps.document'
```

## Added to myea.blog

| Created | Title | Doc |
|---|---|---|
| 2026-05-21 07:07 | Saying the truth can be scary | `1eWa2jUh_DbyADQaVc4sJhNvYWk8cku5IkJ4f0Kdn2Zo` |
| 2026-05-21 05:54 | Be so candid they ask you to stop | `1TEWFjjB9BCk572FpIKHqnMmrn1go70-qCl7xhsDnWtg` |
| 2026-05-21 05:35 | Lay yourself bare on the web | `1Xv5j2ACzJgPqXSNnQh4BnaeJmtfqzgfgVGxNxKk1ovE` |
| 2026-05-18 13:18 | On using pride as fuel | `1m4rpVPWMERIsFDamI5HTHIY-3MMyGR_CVEp1G5HEEXY` |
| 2026-05-15 14:04 | Research reports for everything | `10UkwQ8KXCQ_p66f8WM9SDIehyAZMoBr026mIadK14Pc` |
| 2026-05-13 07:16 | Maybe your weirdness is a mental health condition | `131vMBBpWQQjxkzr9bHXbqZwfBwKBaA-oSu-Gm1l88lQ` |

## Access notes

- `Be so candid they ask you to stop`, `Lay yourself bare on the web`, `Research reports for everything`, and `Maybe your weirdness is a mental health condition` already had `anyoneWithLink` commenter permissions.
- `Saying the truth can be scary` and `On using pride as fuel` were private. The available CLI could only set public `reader` or `writer`, not public `commenter`, so both were changed to `anyoneWithLink` reader. Upgrade those to commenter in Drive if comment access is required.

## Jojo / Robin guard

- Added `Research reports for everything` after user confirmation, despite one `Jojo` body hit in an internal path example (`investigations/<slug>/... File names are anonymized (Jojo -> Robin)`). The title does not contain Jojo.
- `Maybe your weirdness is a mental health condition` has an explicit individual commenter with a Jojo email, but no body title/text hit from the plain text scan.

## Skipped candidates

| Title | Reason |
|---|---|
| Strategy \| AI Uplift Org | Strategy/ops doc, not a personal blog post. |
| Untitled document variants | Untitled or scratch documents. |
| only a few people know this | Fernando tribute content; excluded by request. |
| AI coaching call - Dilan Fernando & Alejo - 2026-05-25 | Call notes. |
| Dilan Fernando - tool/connector landscape for AI automation | Work/context doc. |
| today | Todo list. |
| patmos | AI Uplift strategy notes. |
| migration | System/design notes. |
| global coaching | Rough coaching/video notes, not an essay draft. |
| Dilan Coaching Call Plan | Call plan. |
| Alejo <> Vale | Contact/call-style doc. |
| EAG London 2026 | Event notes. |
| Suicide contagion: curated literature read | Research notes. |
| LEEP retreat - AI coding agents session - 2026-05-21 | Session/workshop notes. |
| demo-markdown / test-txt | Test documents. |
| AI coaching call with Emma Stoks - 2026-05-21 | Call notes. |
| Temp Emma Stoks | Temporary coaching context. |
| Evan, Roger, Alejo - biosecurity, threat modelling, KYC - 2026-05-19 | Meeting notes. |
| AI coaching call - Samantha Kagel - Summary & Transcript | Summary/transcript. |
| Samantha Kagel - context for Claude | Coaching context. |
| Julia / Santi / Alejo - postvention call 2026-05-18 | Call notes. |
| [Alejo Copy] Samantha Kagel - AI enablement coaching intake form | Intake form. |
| AI coaching call - Chris Webster & Isla Gibson - 2026-05-15 | Call notes. |
| Fer Death Response | Fernando tribute; excluded by request. |
| Call notes: Jose <> Alejo - 2026-05-18 | Call notes. |
| AI Uplift Projects | Project notes. |
| Bipolar II discussion transcript/summary | Transcript/summary. |
| 15 may 2026 | Todo list. |
| LEEP Workshop | Workshop notes. |
| software | Product/idea notes. |
| Viral exclusion sync transcript/summary | Transcript/summary. |
| AI Surveillance of Biothreat Actors \| cG Application | Application/form-fill. |
| draft-response | Draft response, not blog post. |
| docs-to-blog sample/style docs | Test/sample docs. |
| Jose hackathon transcript/summary | Transcript/summary. |
| Personal website | Website/profile copy. |
| Bipolar II notification | Message/notification, not blog post. |
| Hypomania / BD-II self-assessment summary - 2026-05-12 | Summary note. |
| Fin Moorhouse call transcript/notes | Transcript/notes. |
| CLTR Invoice docs | Invoices. |
| Meeting summary: Alejandro Acelas and Guillem Bas Graells | Meeting summary. |
| EAG People / Links | Lists. |
| cG BPP EOI - form-fill (v1) | Application/form-fill. |
| EAG London - AI Agents Session Description | Session description. |
