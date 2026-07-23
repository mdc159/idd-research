---
date: 2026-07-23
worker: scribe (claude)
type: report
mission: ""
source: "bibliotec cookbook/bootstrap.md run on the Windows node"
---

# Windows node bootstrap — 2026-07-23

Record that the Windows node was brought into the fleet per bibliotec cookbook/bootstrap.md:

- Prerequisites: git, gh, herdr, pi, uv present; `just` was missing and installed via winget.
- bibliotec cloned to ~/.claude/skills/library (main @ 24b0672); LIBRARY_REPO_URL confirmed.
- Fleet bootstrap stanza written to ~/.claude/CLAUDE.md (did not previously exist), with a node note about version caveats.
- Roles pulled: builder, scribe, workhorse to ~/.claude/agents/; verifier-herdr persona fetched from mdc159/herdr-verifier.
- Smoke test: PASS with caveat. GLM-5.2 via zai provider wrote FLEET-SMOKE-OK 2026-07-23 zai/glm-5.2 to its artifact from inside a herdr pane — but only headless (pi --mode json -p). Interactive first-prompt delivery is broken on this node's herdr 0.7.2-preview: the known first-prompt swallow occurred live, and 0.7.2 has no send-keys or agent prompt to recover. CLI surface differs from the playbook (agent send / agent wait --status single-state vs prompt / --until; no pane run; no pane wait-output; agents cannot be seated in existing panes; Windows needs pi.cmd not pi as argv[0]).
- Not yet operational on this node: the certified verifier pairs (no herdr-verifier checkout, kimi/codex providers unverified, interactive delivery broken). Root fix: herdr update to >=0.7.5 (user decision pending), then clone herdr-verifier and key providers.
- Pi version 0.80.10 vs playbook-verified 0.81.1.
