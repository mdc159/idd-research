# Analysis: Four Extracted Repos

Analyzed in `repos/`: `fusion-harness-main`, `learning-cmux-with-agents-main`, `planf3-main`, `the-library-main`. All four are authored by the same source (IndyDevDan / "agenticengineer.com"), are MIT-licensed, and ship a near-identical closing footer ("Master Agentic Coding… Stay Focused and Keep Building"). Despite overlapping marketing, they occupy distinct layers of the same agentic-coding stack. This report reads the READMEs plus the actual source/skill/config files and quotes them directly.

---

## 1. `fusion-harness-main` — a Pi extension that *fuses* two frontier models

### Purpose
A **standalone Pi coding-agent extension** (`pi -e ...`) that implements the "architect/editor" or "fusion" pattern: instead of picking one frontier model, it runs two hard-labeled roles in parallel — an **ARCHITECT** (plans/fuses/validates) and a **BUILDER** (builds) — and merges their outputs with attribution. From `README.md`: *"Fuse frontier models instead of racing them. AND, not OR."*

### Architecture
The entire harness is **one TypeScript file** — `extensions/fusion-harness/fusion-harness.ts` (2,506 lines) — that registers three slash commands:

- `/opinion <prompt>` — both models answer independently; a two-column A/B panel compares model · latency · tokens · cost.
- `/fusion "<prompt>" "<fusion-prompt>"` — ARCHITECT + BUILDER answer in parallel, then a third FUSION agent (architect model, fresh session) merges them with `[ARCHITECT]`/`[BUILDER]` provenance.
- `/auto-validate <prompt>` — a VALIDATOR writes an acceptance **gate** *before* the BUILDER builds; the gate runs, FAIL lines feed back to the builder, looping until green or a halt cap (`--max-validations`, default 5).

The core plumbing is that **every agent is a spawned `pi` subprocess**. From the file header (`fusion-harness.ts:39-45`):

> *"Plumbing: every agent is a spawned `pi --mode json -p` subprocess with a fully-qualified `provider/id` model and a throwaway --session-dir under a per-run /tmp/fusion-harness-* artifacts dir. Nothing is written to the repo."*

The `runChild()` implementation confirms children are deliberately **clean-room** (`fusion-harness.ts:460-485`):

```ts
const args: string[] = ["--mode","json","-p","--session-dir",opts.sessionDir,
  "--no-skills","--no-extensions","--no-context-files","--thinking",opts.thinking,"--model",run.model];
```

So children never load skills/extensions/context files — *"their entire contract comes from the harness's prompt files"* — which makes runs deterministic across machines regardless of installed skills.

The host itself runs on the **BUILDER** model; the ARCHITECT is a separate persistent session keyed per-project *and per-model* under `/tmp/fusion-harness-sessions/`. Raw chat is therefore "vanilla Pi on the builder"; a slash command **forks the host session** so builder children inherit conversation history.

### Tech stack
- **TypeScript** against `@earendil-works/pi-coding-agent` + `@earendil-works/pi-tui` (Box/Container/Markdown/Text).
- **pi** (badlogic/pi-mono), `just`, `jq`, `uv`.
- `uv` PEP-723 Python scripts are used as the *executable acceptance gate* (`SYSTEM_PROMPT_VALIDATOR.md`: *"Your deliverable is an Astral `uv` single-file Python script (PEP 723) that exits 0 IF AND ONLY IF the user's REQUEST is genuinely, verifiably complete"*).
- Anthropic + OpenAI keys. Default models: `anthropic/claude-fable-5` (architect) / `openai/gpt-5.6-sol` (builder); workhorse tier `claude-sonnet-5` / `gpt-5.6-terra` (`justfile`).

### Key files
- `extensions/fusion-harness/fusion-harness.ts` — the harness.
- `extensions/fusion-harness/{SYSTEM,USER}_PROMPT_*.md` — every default prompt, `{{VAR}}` interpolated ("tune the harness by editing files, not code").
- `justfile` — `fh-workhorse` / `fh-sota` recipes; flags append (e.g. `--architect-thinking max`).
- `live_final_generation/` — on-camera SOTA artifacts (fused bench, gate rounds, manifest).

### Relation to terminal AI agents / harnesses
This is **in-process, single-terminal multi-model orchestration**. It does *not* use panes or a multiplexer — instead it splits one pi TUI into two columns it fully controls (ARCHITECT left, BUILDER right) via `@earendil-works/pi-tui`. It sits *inside* one pi session and spawns *more* pi sessions as subprocesses. It is the canonical example here of a **harness extension**: it extends the agent runtime rather than replacing it. It directly references Aider's architect/editor, Devin's "fusion," and OpenRouter's "model fusion" as prior art.

---

## 2. `learning-cmux-with-agents-main` — driving a fleet through a terminal multiplexer

### Purpose
A hands-on **showcase + skills package** proving a single thesis: a primary agent (Claude Code, pi, Codex, Gemini) can stand up, prompt, observe, and tear down a whole **fleet** of other agents *inside* **cmux**, entirely through cmux's CLI and socket. From `README.md`: *"Most 'multi-agent' tooling hides the agents behind an SDK. cmux does the opposite: every agent is a real terminal surface you can see, and every surface is addressable (`surface:3`) and scriptable."* It ships **31 natural-language prompts** (Tiers 1–5 + customization 26–31), each validated against cmux `0.64.17`.

### Architecture
cmux (a native macOS terminal built on **Ghostty**) nests in one hierarchy — **Window → Workspace → Pane → Surface → Panel** — and orchestration collapses to four verbs (`README.md`):

```bash
cmux send        --surface surface:3 "claude"   # type into a terminal
cmux send-key    --surface surface:3 enter       # press a key
cmux read-screen --surface surface:3             # read what it printed
cmux close-surface --surface surface:3           # shut it down
```

The capstone demo is a **5-agent Flotion team** (lead + plan/build-be/build-fe/test) that ships a feature of a small Notion clone. Roles are markdown system prompts booted as `pi --append-system-prompt <role>.md`, e.g. `cmux/fs-team.layout.json`:

```jsonc
{ "type":"terminal", "name":"lead",
  "command":"pi --append-system-prompt __REPO__/.claude/agents/lead.md --model openrouter/z-ai/glm-5.2 --name lead-__FEATURE__ \"You are the LEAD …\"" }
```

Coordination is **file + sentinel based**, not message-passing. From `.team/README.md` and `.claude/agents/lead.md`: the orchestrator writes `.team/<team>.roster.json` mapping roles→`surface:N` refs; the lead dispatches tasks with one single-line `send` + `send-key enter` (newlines submit separate broken prompts); each worker ends with a sentinel `FLOTION-DONE: <role> | <summary>`, and the lead **waits on cmux push notifications** rather than busy-polling (`cmux events --category notification`).

A declarative layout can boot the whole team at once (`cmux workspace create --layout`), and two spawn paths exist: agent-driven (`just devcc`/`devpi` run `/spawn-fs-team`) and a scripted fast path (`just fastcc`/`fastpi` → `uv run scripts/spawn_fast.py`).

### Tech stack
- **cmux** (Ghostty-based macOS terminal), driven by **any agent CLI** (`claude`, `pi`, `codex`, `gemini`) — heterogeneous by design.
- Demo app **Flotion**: FastAPI + SQLite backend (`apps/flotion/backend/main.py`) + Vue 3 + TypeScript/Vite frontend.
- `just`, `uv` (single-file `scripts/spawn_fast.py`), `jq`, `npx skills` to install the vendored cmux skills.
- Default orchestrator/lead/plan model is `openrouter/z-ai/glm-5.2`; build/test workers use `openrouter/minimax/minimax-m3` (`spawn-fs-team.md:24-28`, `justfile:30`).

### Key files
- `prompts/01–31*.md` + `prompts/PATTERNS-read-and-notify.md` — the 31 prompts, each with plain-English prompt + answer-key verbs + success criteria.
- `.claude/agents/{lead,plan,build-be,build-fe,test}.md` — the 5 role system prompts.
- `.claude/commands/{spawn-fs-team,prime,cmux-fresh,cmux-did-spawn}.md` + `.claude/skills/cmux/SKILL.md`.
- `cmux/fs-team.layout.json`, `scripts/spawn_fast.py`, `apps/flotion/`.
- `ai_docs/cmux-skills/` — all 19 vendored cmux skills (9 agent-facing + 10 contributor).

### Relation to terminal AI agents / harnesses
This is the **multi-pane / multi-process orchestration layer**. cmux is a direct analogue of **herdr** (pi's own "terminal multiplexer for coding agents") — the README explicitly benchmarks cmux against tmux and Warp. Where fusion-harness keeps models inside *one* TUI as subprocesses, learning-cmux keeps each agent in its *own* real terminal surface, driven by another agent over a socket. The `cmux` skill (`.claude/skills/cmux/SKILL.md`) teaches the driving agent the verbs so plain English compiles to `cmux` calls. pi appears here in three roles: as orchestrator (`just devpi`), as a worker in a pane, and as the skill target.

---

## 3. `planf3-main` — "Plans For Fable Five": a planning meta-skill

### Purpose
A **Claude Code Agent Skill** (runs in pi, Codex, opencode — "any harness that reads `.claude/skills/`") that is itself a **meta-skill**: it doesn't build features, it *writes, updates, and builds plans*. It targets "Mythos-class" models (Fable 5) and deliberately spends tokens/images/structure to extract their planning ceiling. From `README.md`: *"you template your engineering once … and every plan the agent writes mirrors it, forever."* API is one line: `/planf3 "<prompt>" [questionable]`.

### Architecture
The skill is `SKILL.md` (240 lines) containing an **HTML Plan Template** plus a workflow router. The template uses `{{PLACEHOLDER}}` interpolation and `<!-- repeat -->` blocks (mirroring fusion-harness's prompt-file convention). Every plan is a single self-contained `.html` written to `specs/`, carrying: updatable append-only metadata (`created`, `modified[]`, `commits[]`, `agent[]`, `session[]`, back/forward refs), Purpose/Problem/Solution, Relevant Files (existing-tagged vs new), Implementation Phases with **per-task checklists**, a **Validation loop**, freeform Notes, and Amendments.

Status markers live inline in the plan — `[]` idle · `[wip]` in progress · `[x]` complete · `[f]` failed — so the build agent tracks its own progress *inside* the artifact. One prompt routes to one of **five workflows** (`SKILL.md`):

| Workflow | Trigger |
|---|---|
| Create Plan | plan/spec/design new work |
| Update Plan | revise an existing plan (surgical edit + amendment) |
| Update References | refresh metadata / wire back-forward refs |
| Build Plan | implement the plan, updating markers as it goes |
| Image Generation | subworkflow — fills `gpt-image-2` diagram slots |

The **Build Plan** workflow (`workflows/build-plan.md`) is the payoff — an agentic execution loop: read the full plan (+ images + back refs), execute phases top-to-bottom, *"loop on failure until they pass,"* mark `[x]`/`[f]`, then run global Validation Commands, then append metadata. A real output ships in-repo: `specs/pi-iroh-coms-net.html` (a serverless P2P agent-mesh plan with 8 synced diagrams).

### Tech stack
- **Pure markdown** skill (`SKILL.md` + `workflows/*.md`).
- `uv` PEP-723 Python scripts for image generation: `scripts/generate_gpt_image.py`, `scripts/edit_gpt_image.py`.
- `OPENAI_API_KEY` for `gpt-image-2`; `code`/`chrome` as IDE/browser defaults.
- Design axis stated in `RAW.md`: *"Performance > Speed >= Cost"* — spend tokens to win.

### Key files
- `.claude/skills/planf3/SKILL.md` — API, instructions, HTML Plan Template.
- `.claude/skills/planf3/workflows/{create,update,update-references,build,image-generation}.md`.
- `.claude/skills/planf3/scripts/*.py`, `specs/pi-iroh-coms-net.html` (+ synced images).
- `RAW.md` (raw think-aloud spec), `legacy_v1_meta_plan.md` (the V1 markdown plan it evolved from), `prompts/pi-iroh-coms.md` (demo prompt).

### Relation to terminal AI agents / harnesses
planf3 is a **consumable capability** that feeds the other layers. It explicitly serves the **"agent trifecta"** (you, your team, AI agents) — the plan is the shared artifact a human reviews, a team reads, and a build agent executes. It attacks the **"planning"** constraint of agentic engineering (paired with "reviewing"), and its Build Plan workflow is itself a self-validating agent loop structurally similar to fusion-harness's gate loop, except the gate is embedded checklist+test commands inside an HTML artifact rather than a generated `gate.py`.

---

## 4. `the-library-main` — a distribution meta-skill ("package.json for agentics")

### Purpose
A **meta-skill whose only job is to manage other skills**: a private-first catalog of references (local paths + GitHub URLs) pointing to where your skills, agents, and prompts live. From `README.md`: *"Think of it as a `package.json` for agent capabilities — but instead of packages, you're managing skills, agents, and prompts."* Crucially it is a **pure agent application**: *"There are no scripts, no CLIs, no dependencies, no build tools. The entire application is encoded in `SKILL.md` … The agent IS the runtime."*

### Architecture
Three pieces: `SKILL.md` (the brain + command table), `library.yaml` (the **catalog of pointers, not copies** — entries define what's *available*, pulled on demand), and `cookbook/*.md` (one step-by-step guide per command: install/add/use/push/remove/list/sync/search). Commands resolve typed dependencies recursively — `requires: [skill:base-utils, agent:reviewer, prompt:task-router]` — and pull **whole parent directories** (skills bundle scripts/refs/assets, not just `SKILL.md`). `library.yaml` ships empty:

```yaml
default_dirs:
  skills:  [{default: .claude/skills/}, {global: ~/.claude/skills/}]
  agents:  [{default: .claude/agents/}, {global: ~/.claude/agents/}]
  prompts: [{default: .claude/commands/}, {global: ~/.claude/commands/}]
library: {skills: [], agents: [], prompts: []}
```

The `use` flow (`cookbook/use.md`) is concrete: `git pull` the library repo → find entry → resolve deps → clone source `--depth 1` into a temp dir → `cp -R <parent>/ <target>/<name>/` → verify. `push` clones, overwrites the skill dir, stages only that path, commits `library: updated <name> …`, pushes. Source URLs are auto-parsed (`github.com/<o>/<r>/blob/<b>/<p>` or `raw.githubusercontent.com/...`), with SSH/`GITHUB_TOKEN` fallback for private repos. The `justfile` shells every command through `claude --dangerously-skip-permissions --model opus "/library <cmd>"`, and installation is "fork → clone into `~/.claude/skills/library` → set `LIBRARY_REPO_URL`."

### Tech stack
- **Pure markdown** (`SKILL.md`, `library.yaml`, `cookbook/*.md`) — no runtime code.
- `git`, `gh` (GitHub CLI), SSH keys / `GITHUB_TOKEN`, `just`.
- Targets `.claude/skills/` conventions; works in Claude Code and "any compatible agent harness that reads `.claude/skills/` — e.g., Pi."

### Key files
- `SKILL.md` (command table, source-parsing rules, GitHub workflow, dependency model), `library.yaml`, `cookbook/{install,add,use,push,remove,list,sync,search}.md`, `justfile`, `README.md`.

### Relation to terminal AI agents / harnesses
the-library is the **distribution/sync layer** of the agentic stack. It is the mechanism you'd use to push fusion-harness's extension, planf3's skill, or the cmux skill set to another device, a remote server, or a teammate — privately, without a public marketplace. It rejects global `~/.claude/*` (which "exposes everything to every agent") and monorepos (which "don't reflect reality") in favor of reference-based, pull-on-demand distribution. Its README even lays out a "Agentic Stack": Skills (capabilities) → Agents (scale/specialization) → Prompts (orchestration) → Justfile (terminal access) → **The Library** (distribution).

---

## Common Threads

The four repos are **complementary layers of one agentic-coding stack**, all from the same author and sharing vocabulary, toolchain, and design philosophy.

### 1. Same agent ecosystem, with `pi` as the recurring runtime
Every repo targets the **pi** / **Claude Code** ecosystem and the `.claude/{skills,commands,agents}/` conventions. pi appears as: the harness fusion-harness extends (fusion-harness), both orchestrator and pane-worker (learning-cmux), a supported runtime (planf3, the-library). The installed `herdr` skill in this environment is pi's *own* terminal multiplexer — a direct counterpart to cmux, which learning-cmux benchmarks against tmux/Warp.

| Repo | Layer | Multi-model / multi-agent mechanism |
|---|---|---|
| **fusion-harness** | In-process model orchestration | Two roles as spawned `pi` subprocesses in one TUI (columns, not panes) |
| **learning-cmux** | Multi-pane process orchestration | Each agent in its own real terminal surface, driven over a socket |
| **planf3** | Planning capability | One skill producing HTML plans a build agent later executes |
| **the-library** | Distribution capability | Reference catalog + pull/push/sync of skills across devices |

### 2. Shared design philosophy: "meta" artifacts and config-as-markdown
Three are explicitly **meta** (a skill that produces/manages other artifacts): planf3 ("a skill that writes… every plan"), the-library ("a skill whose only job is to manage other skills"), and fusion-harness (a harness that spawns more agents and ships default prompts as files). All lean on **markdown/JSON as code**: prompt files with `{{VAR}}` interpolation (fusion-harness `USER_PROMPT_*.md`, planf3 template), role files (`learning-cmux .claude/agents/*.md`), layouts (`fs-team.layout.json`), cookbook steps (the-library). Behavior is changed by editing files, not code.

### 3. Identical shared toolchain
- `just` + a `justfile` in **all four** (task runner, dotenv-loaded).
- `uv` PEP-723 single-file Python for deterministic, dependency-declared scripts: the gate runner (fusion-harness), `scripts/spawn_fast.py` (learning-cmux), image generation (planf3). (the-library is the lone exception — it is *pure agent* by design.)
- `jq` for machine-readable refs; `.env`/`--env-file` for key injection; `npx skills` for skill installation.
- Common install pattern: an **"Agentic Install"** that delegates to an in-repo slash command (`.claude/commands/install.md` / `prime.md` / `spawn-fs-team.md`).

### 4. Shared vocabulary and framing
- The **two constraints of "Agentic Engineering": planning + reviewing** (planf3 `RAW.md`, fusion-harness README's "deeper problem is review").
- The **"agent trifecta": you, your team, AI agents** (planf3, the-library).
- The **"software factory"** zoom-out: fusion-harness calls itself "one node in your software factory"; learning-cmux prompt 25 is literally "The Software Factory"; the-library's stack diagram puts agents in a factory pipeline.
- Identical closing footer + YouTube/agenticengineer.com CTAs across all four.

### 5. Multi-agent coordination via files/artifacts, not message buses
None of these use an SDK message-passing layer; they coordinate through **grounded artifacts**:
- fusion-harness grounds downstream agents in a `/tmp/fusion-harness-*/` run dir (named `architect.md`/`builder.md`/`gate.py`).
- learning-cmux uses `.team/<team>.roster.json` + `.team/<role>.md` notes + the `FLOTION-DONE:` sentinel + cmux's event/notification stream.
- planf3 grounds the build agent in the plan `.html` itself (status markers + checklists live inside it).
- the-library grounds pulls in `library.yaml` and uses git as the source of truth.

### 6. Fan-out / fan-in and validation loops are everywhere
- fusion-harness `/fusion` = parallel workers + merge agent; `/auto-validate` = gate-first loop with escalation/triage and gate-repair.
- learning-cmux prompt 12 ("Fan-Out / Fan-In"), prompt 25 (plan → fan out → test → browser-verify → notify → collect diffs), and the Flotion lead→workers→test loop with PASS/FAIL routing.
- planf3 Build Plan = per-phase testing loop *"do not exit until every box is checked."*
All treat **review as a built-in, automated step** (a gate, a test worker, a checklist) rather than a human afterthought.

### 7. Determinism / clean-room children
Each repo fights "drift" by isolating agent inputs: fusion-harness spawns with `--no-skills --no-extensions --no-context-files`; planf3 warns *"stray context bleeds in… keep the output directory clean"*; the-library keeps a **catalog vs. manifest** distinction (available ≠ installed) and scopes pulls to specific dirs; learning-cmux sandboxes Tier-1 prompts in `mktemp -d /tmp/…`. The recurring lesson: an agent's contract should come from *what you hand it*, not from ambient global state.

### 8. The "agentic stack" they collectively form
Read together they describe a complete pipeline an engineer could actually assemble:
1. **planf3** turns a prompt into a structured, validated plan.
2. **fusion-harness** executes a plan-fusion step (architect plans, builder builds, gate verifies) inside one pi session.
3. **learning-cmux / cmux (≈ herdr)** scales that to a *fleet* of specialized agents across panes/windows, with browser verification and push notifications.
4. **the-library** distributes every skill/agent/prompt above to other devices and teammates, privately.

In short: **fusion-harness is the multi-model brain, cmux/herdr is the multi-terminal body, planf3 is the planning discipline, and the-library is the supply chain** — all four written as markdown/config/extension code that any pi- or Claude-Code-class agent can load and run.
