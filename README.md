<!--ai-->
# My EA Blog
<!--/ai-->

<!--ai-->
Single-page index of Alejandro Acelas's writing — drafts, cross-posts, and bullet-point notes — each linking to a Google Doc. Live at [myea.blog](https://myea.blog).
<!--/ai-->

<!--ai-->
Static HTML/CSS/JS in `public/`, with small Vercel functions in `api/` for click analytics. See [`AGENTS.md`](AGENTS.md) for how posts are classified, sorted, and deployed.
<!--/ai-->

<!--ai-->
Edit [`open-problems.md`](open-problems.md), then run `npm run build` to update the Open Problems page.
<!--/ai-->

<!--ai-->
Run `npm run update` after changing the post index. It rebuilds the static page and the LLM text files, fetching only Docs whose recorded modification time changed.
<!--/ai-->
