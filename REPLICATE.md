# REPLICATE

## Workspace structure and shared instructions

The human wanted simpler folders and shared agent instructions while preserving existing work.

- Moved the repository from work/writing/blog to me/blog; declared project context and made CLAUDE.md import AGENTS.md. Preserved the previous differing Claude instructions in .agent-history/.

Agent session 01a072fe-84d6-73f3-b37e-3bb912088c38 · Commits blog: ed59b03

## Group personal sites

The human wanted to remove unstarted personal projects and simplify the remaining folders.

- Moved `me/blog` to `me/sites/blog`, preserving repository history and site files.

Agent session 01a0b90b-7ae3-7ed1-bb2f-fde3ad5d78d3 · Commits dotfiles: 5ceaed4

## Agent instructions cleanup — 2026-09-19

Alejo asked to refresh project instructions and remove redundant Claude instruction files where native AGENTS.md loading is available.

- Updated the applicable instructions and removed redundant local Claude copies; distinct content and preserved snapshots remain.
- Checked instruction references and shared-context freshness; native Claude loading requires 2.1.277+ with the built-in feature enabled.

Agent session 01a0b915-3eb2-78b2-9add-6ba48ad9a3b1 · Commits 4cacf57d547de8b39d9ae11b396f2bd8b8b3efe7

## Explicit startup instructions

Alejo wanted shared instructions selected deliberately at startup, without copied text or automatic parent inheritance.

- Removed agent-context YAML and generated shared text; retained project-specific instructions locally.
- Shared groups: none. Selection now lives in the machine's context registry; startup does not rewrite this file.

Agent session 01a0b915-3eb2-78b2-9add-6ba48ad9a3b1 · Commits bffc562
