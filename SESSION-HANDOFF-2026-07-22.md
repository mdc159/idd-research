# Session Handoff — 2026-07-22 (Agentic Terminal Stack)

You are the incoming **orchestrator** (Fable) taking over from the previous session. Your job: orchestrate & verify; delegate all bulk work to cheaper herdr worker agents. Read this, confirm the state below, then continue.

## Read these to get fully briefed
- `MEMORY.md` auto-loads (13 memory notes — routing, launch conventions, philosophy). Trust it.
- Obsidian vault cluster: `~/Documents/Obsidian-Linux/Global/03-Resources/Agentic Terminal Stack/` — 12+ notes. Start at `Agentic Terminal Stack MOC.md`, then `Multi-Agent Orchestration Playbook.md` (the correct-first procedures) and `Friction Log.md` (the why).
- Analysis reports: `~/Projects/IDD/analysis/*.md` (5 repo analyses).

## What this is
Built a multi-agent stack: **herdr** (terminal multiplexer, v0.7.5) supervises agents; **Pi** (v0.81.1) is the multi-model runner; workers run on cheap subscriptions while Fable orchestrates.

## Model routing (policy)
- **Fable (me/you)** = orchestrate, plan, final review ONLY. Expensive, ~50% cap.
- **Codex models** = default heavy lean (per-node subscription).
- **Kimi K3** = top tier, hardest tasks + verification (1M ctx).
- **GLM-5.2** = high-mileage workhorse for bulk.

## Running fleet (herdr workspace w8) — check with `herdr agent list`
- `claude` w8:p1 = the orchestrator pane (the OLD one being retired; you'll be a NEW pane)
- `scribe` w8:p6 = Codex, docs→vault (auto-reads vault AGENTS.md)
- `builder` w8:pD = Codex, built the verifier
- `glm1` w8:p7 = GLM-5.2, warm with IndyDevDan repo analyses
- `glm2` w8:p8 = GLM-5.2, verifier guinea-pig
- `artist` w8:pC = Codex, vault visual research
- `verifier` w8:pG = Kimi K3, read-only verifier

## Canonical worker launch (correct-first — see playbook)
1. `herdr pane split ... --no-focus` (add `--env OPENAI_API_KEY=` for codex kinds)
2. `herdr pane wait-output <pane> --match <shell-prompt>` — never start into a cold pane
3. `herdr agent start <name> --kind <k> --pane <id> -- <flags>` (codex: `--dangerously-bypass-approvals-and-sandbox`; pi: `--model <provider/model>`)
4. First prompt via `herdr agent prompt <name> "..." --wait`; confirm status flipped to `working` before backgrounding.
Read results from artifact files or agent session JSONLs, NEVER pane scrollback (alternate-screen loss).

## DONE this session
- herdr skill installed; 6 agent integrations current (claude/codex/hermes/opencode/pi/kimi).
- Pi wired: zai/glm-5.2, kimi-coding/k3, openai-codex, xai, openrouter/HF — ~395 models.
- the-library installed local-first (`~/.claude/skills/library/`, git, no remote yet); planf3 installed.
- **herdr-verifier** (`~/Projects/herdr-verifier/`) — VALIDATED WITH CAVEAT: happy-path, honest-deviation, and infeasible-task cases proven LIVE (glm2 builder / K3 verifier, sound nuanced judgments). FAIL→FEEDBACK→escalation proven by UNIT TESTS only — GLM-5.2+K3 could not be sufficiently fooled by seeded-flaw tasks (positive result for the verifier, gap only for the live demo). 3 integration bugs found+fixed live + a continuous-logging fix. 15 tests green.

## OPEN THREADS (next work)
1. **Sandbox build** (see `Sandboxing Tiers.md`): Tier1 port damage-control YAML guardrails; Tier2 test Codex `--sandbox workspace-write`+network (demote full-bypass to exception); Tier3 E2B runner (`E2B_API_KEY` in env; reference impl cloned at `~/Projects/IDD/repos/agent-sandboxes`). Key insight: run verifiers/gates INSIDE sandboxes (isolation + verification are complementary halves).
2. **Fleet definitions**: per-agent `AGENT.md` (kind, model TIER not id, cwd convention) cataloged in the library so any device instantiates its own; thin `just` recipes consume them.
3. **Chain-runner**: watcher variant that hands worker→worker automatically, but only with a verifier in the middle (researcher→verifier→scribe).
4. **Library → private GitHub** publish (fleet goal: M6800 + newer Dell + Mac mini + VPSs all pull same playbook; sync is pull-on-use).
5. **Next plan → use plannotator** (user wants interactive review + before/after mermaid flows; user is visual).
6. **Visual upgrades**: artist recommends scoped CSS + one Excalidraw template, NOT a plugin stack.

## Standing rules
Slow is smooth, smooth is fast — correct-first over speed. Verify state transitions, never assume. Prefer lifecycle-authority (Pi-hosted) agents for automation. After `herdr update`: `herdr integration status --outdated-only`. Playbook = do this / Friction Log = why / memory = enforced.

## Your first action
Reply to the retiring orchestrator with: (a) a 4-5 line summary of current state proving you read this, (b) the model routing tiers, (c) what you'd pick as the next task. Once confirmed on the same page, the old pane (w8:p1) retires.
