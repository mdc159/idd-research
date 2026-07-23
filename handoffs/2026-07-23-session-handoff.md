---
date: 2026-07-23
worker: orchestrator
type: handoff
mission: ""
source: "pre-contract record, was SESSION-HANDOFF-2026-07-23.md"
---

# Session Handoff — 2026-07-23 (Agentic Terminal Stack)

You are the incoming **orchestrator** — any capable agent (Claude, Hermes, or other) holds this role by loading the playbook. Orchestrate and verify; delegate bulk work to workers; you do not do grunt work.

## Fleet state note (2026-07-23, end of session)
The fleet was fully reset after this handoff was written: all panes closed, nothing preexisting is running. Fire everything up from scratch per bibliotec `cookbook/bootstrap.md` and the playbook — everything needed is documented there, in the four repos, and on the Linear board. (The overlap rule still applies whenever an outgoing orchestrator IS alive: don't close it on arrival; it retires on the user's word.) Also since this handoff was written: all four repos are PUBLIC, and main on bibliotec/herdr-verifier/idd-research is mechanically locked — changes land by pull request only.

## First actions
1. Read `~/.claude/skills/library/playbook/SKILL.md` (bibliotec) — it is the operating procedure and the authority order. Then `playbook/lessons.md` for what was retired and why.
2. Check the live board: Linear project **Agentic Terminal Stack** (team: 1215 labs) — issues 121-62…121-69 are the plan, priorities set.
3. Verify fleet state yourself (`herdr agent list`) — never trust this document over the running system.

## Where everything lives (four PUBLIC repos, github.com/mdc159; main is PR-only on the first three)
| Repo | Contents |
|---|---|
| `bibliotec` | Source of truth: playbook (routing tiers, canonical launch, Check-out Gauntlet, naming convention), lessons, fact-source map, role definitions (`agents/`), catalog, bootstrap |
| `herdr-verifier` | Verifier harness + calibration spec, briefs, scorecard, tracked run evidence |
| `idd-research` | IndyDevDan repo analyses, portability patterns, drift audit, sanitize report, this handoff |
| `stack-vault` | Vault cluster (documentation/narrative — not procedure) + vault house style |

Local checkouts on this node: `~/.claude/skills/library`, `~/Projects/herdr-verifier`, `~/Projects/IDD`, vault at its OS-specific root (the stack-vault repo root).

## State (2026-07-23)
- **Verifier loop FULLY VALIDATED LIVE**: happy path, honest deviation, and FAIL→FEEDBACK→escalation all proven on live agents. A weak builder failed 3 consecutive rounds; K3 caught each with accurate diagnoses; watcher auto-sent corrective prompts; cap 3 raised the human escalation. Evidence: `herdr-verifier/runs/`, `calibration/scorecard.md`.
- **Check-out Gauntlet** (user-approved, in playbook): checked out — GLM-5.2 (builder), Kimi K3 (verifier). Not checked out — Qwen3.5-9B. Verified work from checked-out pairs ships on VERIFIED alone; orchestrator sees only escalations. Re-cert monthly (Linear 121-68).
- **Repos sanitized and PUBLIC** (121-63 done); main on bibliotec/herdr-verifier/idd-research is mechanically PR-only (ruleset, no bypass).
- Sandbox Tier-3 (E2B) DONE (121-62): microVM smoke test + K3 behavioral verification inside E2B proven; documented as an opt-in capability, not a mandate. `E2B_API_KEY` in the node env.

## Standing doctrine (short form; playbook is authoritative)
- Authority: the user overrules everything; otherwise IndyDevDan's repos are the rules; verified local experience fills gaps; labeled extrapolation last — gap-filler only.
- Quote decisions at their stated scope; never generalize. A user question is exploration, not a directive.
- Positive procedure only in bibliotec; history in lessons. Description verified where written; execution verified where run (fleet spans Mac/Windows/Linux; consuming agents port and verify locally).
- Workers: GPT models via Pi's `openai-codex` provider (direct codex kind retired). Name workers `<role>-<model>-<provider>`. Read the provider back after launch — patterns can resolve to surprise billers (an HF credit pool was burned learning this).
- Read results from artifact files and session JSONLs, never pane scrollback. Verify state transitions; never assume.
- No operational information may live only in an orchestrator's private memory — if you learn something operational, it goes in bibliotec.

## Known open ends
- The `verifier` (K3) and staff panes (`scribe`, `glm1`, `glm2`, `builder`, `artist`) may still be running from the prior session — check, reuse or release. Pre-convention names predate the naming rule.
- The user runs cross-device: Linear + the four repos must be sufficient to reconstruct everything on any node. If you find they aren't, that is a bug — report it.
