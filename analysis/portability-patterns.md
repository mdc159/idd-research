# Portability Patterns Across disler's Repos

Focused study of how disler/IndyDevDan's repos make agent assets portable: how sources are referenced, how fleet/roster agents are defined and instantiated, and how a fresh machine is bootstrapped. Every claim cites a file under `~/Projects/IDD/repos/`.

---

## 1. the-library: how `library.yaml` references sources, and what `use`/`sync` do

### Does the repo vendor asset copies, or point outward?
**It points outward.** The repo is a pure catalog plus the skill that drives it. The full file tree of `repos/the-library-main/` is exactly:

```
cookbook/{add,install,list,push,remove,search,sync,use}.md
images/*.svg
library.yaml
justfile
LICENSE  README.md  SKILL.md
```

There is **no `skills/`, `agents/`, or `prompts/` directory** in the repo — nothing is vendored. And `library.yaml` ships **empty** (`repos/the-library-main/library.yaml`):

```yaml
default_dirs:
  skills:  [{default: .claude/skills/}, {global: ~/.claude/skills/}]
  agents:  [{default: .claude/agents/}, {global: ~/.claude/agents/}]
  prompts: [{default: .claude/commands/}, {global: ~/.claude/commands/}]
library:
  skills: []
  agents: []
  prompts: []
```

The design is stated explicitly in `SKILL.md`: *"The `library.yaml` is a catalog, not a manifest. Entries define what's available — not what gets installed. You pull specific items on demand with `/library use <name>`."* and *"Nothing is fetched until you ask for it."*

### How sources are referenced (three accepted formats)
The `source` field of a catalog entry is a **pointer to one specific file**, auto-detected into one of three formats (`SKILL.md` → "Source Format"):

| Format | Example |
|---|---|
| **Absolute local path** (starts with `/` or `~`) | `/Users/me/projects/tools/skills/my-skill/SKILL.md` |
| **GitHub browser URL** | `https://github.com/<org>/<repo>/blob/<branch>/<path>` |
| **GitHub raw URL** | `https://raw.githubusercontent.com/<org>/<repo>/<branch>/<path>` |

A populated entry looks like this (`SKILL.md` "Example Filled Library File"):

```yaml
library:
  skills:
    - name: diagram-kroki
      description: Generate diagrams via Kroki HTTP API
      source: https://github.com/myorg/private-skills/blob/main/skills/diagram-kroki/SKILL.md
      requires: [skill:firecrawl]   # typed dependency: skill: / agent: / prompt:
  agents:
    - name: code-reviewer
      source: https://github.com/myorg/agent-configs/blob/main/agents/code-reviewer/AGENT.md
  prompts:
    - name: commit-message
      source: https://github.com/myorg/team-prompts/blob/main/prompts/commit-message.md
```

Two things to note: (a) `source` points at **one file**, but the puller always grabs the **whole parent directory** (skills bundle scripts/refs/assets); (b) dependencies are **typed references** (`skill:name`, `agent:name`, `prompt:name`) resolved recursively before the item itself.

### What `use` does (`repos/the-library-main/cookbook/use.md`)
`use` is the on-demand fetch. The sequence:

1. **`cd <LIBRARY_SKILL_DIR> && git pull`** — refresh the catalog first.
2. Find the entry by name/description across `library.{skills,agents,prompts}`.
3. **Resolve dependencies** — for each `requires` entry, recursively run `use` on it first.
4. Pick the target dir from `default_dirs` (`default` unless the user said "global"/custom).
5. **Fetch by source type:**
   - **Local path** → `cp -R <parent_directory>/ <target_directory>/<name>/` (skills copy the whole parent dir; agents/prompts copy just the `.md`).
   - **GitHub URL** → parse `org/repo/branch/file_path`, `git clone --depth 1 --branch <branch> https://github.com/<org>/<repo>.git "$tmp_dir"` into a temp dir, `cp -R "$tmp_dir/<parent_path>/" <target>/<name>/`, `rm -rf "$tmp_dir"`. On failure (private repo) it falls back to SSH: `git clone ... git@github.com:<org>/<repo>.git`.
6. Verify the target exists, report.

### What `sync` does (`repos/the-library-main/cookbook/sync.md`)
`sync` is "make everything I've already installed match its source." Same mechanics as `use`, but bulk + lazy:

1. **`cd <LIBRARY_SKILL_DIR> && git pull`** — refresh catalog.
2. Read every entry in the catalog.
3. **Find only the *installed* items** (check `default` dir, `global` dir, and recurse for name matches). *"If nothing is installed, tell the user and exit."*
4. Re-pull each installed entry with the identical local-path / GitHub-clone logic as `use`.
5. Resolve dependencies for installed items that declare `requires`.
6. Report a status table (`refreshed` / `failed: <reason>`).

### What `push` does (`repos/the-library-main/cookbook/push.md`)
`push` is the reverse — local edits back to source. For GitHub sources it clones shallow into a temp dir, `rm -rf` the old skill dir, `cp -R` the local version in, stages **only** that path (`git add <skill_path>`), commits `library: updated <name> <...>`, pushes. For local-path sources it just overwrites the source dir with `cp -R`.

**Takeaway:** the-library is a **reference-based registry, not a vendor**. The repo body never contains the skills it manages; it stores only pointers (abs-path / GitHub URL) and a recipe (clone-or-copy) the agent executes at runtime. The catalog itself travels via the forked repo's git history.

---

## 2. learning-cmux-with-agents: fleet/roster agent definitions

Fleet definitions here are **not one file** — they live in three layers that work together:

### Layer A — role definitions: `.claude/agents/*.md` (the per-role brain + metadata)
Each of the five team members is a markdown file with YAML frontmatter. Example, `repos/learning-cmux-with-agents-main/.claude/agents/build-be.md`:

```yaml
---
name: build-be
description: Backend engineer for Flotion. Use to implement FastAPI + SQLite changes ...
color: orange
model: inherit        # ← takes whatever model the launcher passes on the pi line
---
# Flotion Backend Engineer
You are the **build-be** worker. You implement the **backend** of Flotion in
`apps/flotion/backend/` and nowhere else. ...
```

And `repos/learning-cmux-with-agents-main/.claude/agents/plan.md`:

```yaml
---
name: plan
description: Feature planner/architect for Flotion ...
color: yellow
model: inherit
---
```

Frontmatter fields observed across the five role files: `name`, `description`, `color` (UI pill), `model` (always `inherit` in this repo — the concrete model is supplied by the launcher, not the role file). The body is the role's system prompt (lane boundaries, workflow, the `FLOTION-DONE:` sentinel contract).

### Layer B — declarative layout: `cmux/fs-team.layout.json` (nested pane/surface tree)
This is the **machine-instantiable** form. The shape is `direction`/`split`/`children` recursion down to `pane.surfaces[]`, each surface being a terminal with a `name` and a full `command` (`repos/learning-cmux-with-agents-main/cmux/fs-team.layout.json`):

```jsonc
{
  "_comment": "Declarative cmux layout ... the fastcc/fastpi just recipes substitute __FEATURE__ and __REPO__ before passing this to `cmux workspace create --layout`.",
  "direction": "horizontal",
  "split": 0.5,
  "children": [
    { "pane": { "surfaces": [{ "type": "terminal", "name": "lead",
        "command": "pi --append-system-prompt __REPO__/.claude/agents/lead.md --model openrouter/z-ai/glm-5.2 --name lead-__FEATURE__ \"You are the LEAD of team __FEATURE__ ...\""
    }] } },
    { "direction": "vertical", "split": 0.5, "children": [
      { "direction": "horizontal", "split": 0.5, "children": [
        { "pane": { "surfaces": [{ "type": "terminal", "name": "plan",
            "command": "pi --append-system-prompt __REPO__/.claude/agents/plan.md --model openrouter/z-ai/glm-5.2 --name plan-__FEATURE__ \"...\""
        }] } },
        { "pane": { "surfaces": [{ "type": "terminal", "name": "build-be",
            "command": "pi --append-system-prompt __REPO__/.claude/agents/build-be.md --model openrouter/minimax/minimax-m3 --name build-be-__FEATURE__ \"...\""
        }] } }
      ]},
      { "direction": "horizontal", "split": 0.5, "children": [
        { "pane": { "surfaces": [{ "type": "terminal", "name": "build-fe",
            "command": "pi ... --model openrouter/minimax/minimax-m3 ..." }] } },
        { "pane": { "surfaces": [{ "type": "terminal", "name": "test",
            "command": "pi ... --model openrouter/minimax/minimax-m3 ..." }] } }
      ]}
    ]}
  ]
}
```

Field semantics:
- **`type: terminal`** (could also be `browser` per the README) — the surface kind.
- **`name`** — the role/tab label (lead, plan, build-be, build-fe, test).
- **`command`** — the **entire `pi` launch line**. This is where `model` actually gets bound: `--model openrouter/z-ai/glm-5.2` for the reasoning roles (lead, plan), `--model openrouter/minimax/minimax-m3` for build/test. `--append-system-prompt <role>.md` injects the Layer-A role file. `--name <role>-<team>` namespaces the session.
- **`cwd`** is **not** per-surface; it's set at the workspace level by the spawner (`cmux workspace create --cwd "$PWD"` in `spawn-fs-team.md`), so every pane inherits the repo root.
- **`__FEATURE__` / `__REPO__`** are template tokens the scripted fast path substitutes before applying the layout.

### Layer C — runtime roster: `.team/<team>.roster.json` (role → surface ref map)
Once a team is booted, the orchestrator writes a small JSON the lead reads to address its workers. Generated verbatim by `jq -n` in `repos/learning-cmux-with-agents-main/.claude/commands/spawn-fs-team.md` (step 7):

```bash
jq -n --arg t "$TEAM" --arg w "$WS" --arg f "$FEATURE" \
  --arg l "$LEAD" --arg p "$PLAN" --arg be "$BBE" --arg fe "$BFE" --arg te "$TEST" \
  '{team:$t,workspace:$w,feature:($f|select(.!="")),
    agents:{lead:{surface:$l},plan:{surface:$p},
            "build-be":{surface:$be},"build-fe":{surface:$fe},test:{surface:$te}}}' \
  > .team/$TEAM.roster.json
```

So the roster shape is `{team, workspace, feature, agents:{<role>:{surface:<ref>}}}` — names map to cmux `surface:N` handles captured at creation. Per `.team/README.md`, this file is gitignored runtime state, regenerated on every spawn.

### How a machine instantiates agents from these (two paths)
Both are wired through the repo `justfile` (`repos/learning-cmux-with-agents-main/justfile`):

1. **Agent-driven (natural language).** `just devcc` / `just devpi` launch a Claude Code / pi orchestrator with `/spawn-fs-team`. That command (`.claude/commands/spawn-fs-team.md`) drives cmux itself: `workspace create --env-file` → `new-split` ×4 → `rename-tab` + `set-color` for identity → type each agent's `pi …` line into its pane via `cmux send` + `send-key enter` → write `.team/<team>.roster.json`. Model blend is declared in the command's `Variables` (`LEAD_MODEL/PLAN_MODEL = openrouter/z-ai/glm-5.2`, `BE/FE/TEST_MODEL = openrouter/minimax/minimax-m3`).
2. **Scripted fast path (declarative).** `just fastcc <feature>` / `just fastpi <feature>` run `uv run --script scripts/spawn_fast.py cc|pi <feature> --orch-pi-model "openrouter/z-ai/glm-5.2"` (`repos/learning-cmux-with-agents-main/scripts/spawn_fast.py`). This substitutes `__FEATURE__`/`__REPO__` into `cmux/fs-team.layout.json` and calls `cmux workspace create --layout`, so **all five panes boot in one call**; the orchestrator then attaches via `/cmux-did-spawn`.

In both cases the actual instantiation primitive is the same: **`cmux send --surface <ref> "<pi launch line>"` + `cmux send-key <ref> enter`** — i.e., type the agent's start command into a real terminal surface and press Enter. Coordination after that is file + sentinel based (`.team/<role>.md` notes, `.team/backlog.md`, the `FLOTION-DONE: <role> | <summary>` line the lead greps via `cmux events`).

---

## 3. Bootstrap / setup procedures documented for a fresh machine

disler's repos consistently ship an **"Agentic Install"** — a slash command or justfile recipe that does prereq checks, key wiring, and project-specific setup, so a fresh machine is brought up by an agent rather than a README you follow by hand.

### the-library — `/library install` (`repos/the-library-main/cookbook/install.md`)
1. Check `git` and that `~/.claude/skills/` exists/creatable.
2. Ask "template repo or your fork?" If template, instruct a private GitHub fork and `git remote set-url origin <fork_url>`.
3. `mkdir -p <LIBRARY_SKILL_DIR> && cd <LIBRARY_SKILL_DIR> && git clone <fork_url> .` (default `LIBRARY_SKILL_DIR = ~/.claude/skills/library`).
4. Edit the `## Variables` block in `SKILL.md`: set `LIBRARY_REPO_URL` (fork URL); confirm `LIBRARY_YAML_PATH` (`~/.claude/skills/library/library.yaml`) and `LIBRARY_SKILL_DIR`.
5. Verify `SKILL.md` + `library.yaml` present, `/library list` works (empty catalog).
The README's manual equivalent: `gh repo fork disler/the-library --private --clone=false` → `gh repo clone <you>/the-library ~/.claude/skills/library` → edit variables.

### fusion-harness — `/install` (`repos/fusion-harness-main/.claude/commands/install.md`)
1. Install missing prereqs: `pi` via `npm install -g @earendil-works/pi-coding-agent`; `just jq uv` via `brew install just jq uv` (or pkg manager).
2. Verify `.env` at repo root has real `ANTHROPIC_API_KEY` + `OPENAI_API_KEY` (never invent/commit). Flagged gotcha: *"`just`'s dotenv-load does NOT override variables already exported in the shell, so a stale exported key silently wins over `.env`."*
3. Confirm the extension entry point + sibling `SYSTEM_PROMPT_*.md`/`USER_PROMPT_*.md` exist (extension throws at load if any prompt file is missing).
4. Launch `just fh-workhorse` (cheap test pair) and confirm the boot banner; `just fh-sota` is the frontier pair (costs money).
A companion `/prime` (`repos/fusion-harness-main/.claude/commands/prime.md`) orients an agent: `git ls-files | sort`, read README, skim `justfile`, glob `extensions/fusion-harness/*_PROMPT_*.md`.

### learning-cmux-with-agents (README "Install")
- **Agentic install:** `brew tap manaflow-ai/cmux && brew install --cask cmux` then `npx skills add manaflow-ai/cmux -g -y` (teach the agent the cmux verbs globally).
- **Manual install:** same brew tap/cask, `sudo ln -sf "/Applications/cmux.app/Contents/Resources/bin/cmux" /usr/local/bin/cmux`, `cp .env.example .env` (provider keys: `OPENROUTER_API_KEY`, `ANTHROPIC_API_KEY`, `OPENAI_API_KEY`, `GEMINI_API_KEY` — see `.env.example`), `open -a cmux`.
- **Gotcha to enable an outside orchestrator:** raise `automation.socketControlMode` in `~/.config/cmux/cmux.json` (default `cmuxOnly` → set `allowAll` or `password`) then `cmux reload-config`.
- `justfile` recipes: `just guide`, `just flotion`, `just devcc`/`devpi`, `just fastcc`/`fastpi`.

### planf3 (README "Install")
- **Agentic install** (prompt): "Read `.claude/skills/planf3/SKILL.md` and install this skill: copy it to `~/.claude/skills/planf3` so `/planf3` works everywhere, then copy `.env.sample` to `.env` and tell me which key to set."
- **Manual:** `cp -r .claude/skills/planf3 ~/.claude/skills/planf3` (global) ; `cp .env.sample .env` + add `OPENAI_API_KEY` (for `gpt-image-2`); run `/planf3 "<prompt>"`.
- Prereqs: `claude`/`pi`/Codex/opencode (any harness reading `.claude/skills/`), `uv`, an OpenAI key.

### agent-sandboxes (README "Quick Start")
- Root `.env` with `E2B_API_KEY`, `ANTHROPIC_API_KEY`, optional `GITHUB_TOKEN` (`repos/agent-sandboxes/.env.sample`).
- Install Claude Code.
- Walk apps bottom-up: `apps/sandbox_fundamentals/` (`uv sync`, run `01..13`), `apps/sandbox_cli/` (`uv sync`, `uv run sbx …`), `apps/sandbox_mcp/` (`cp .mcp.json.sandbox .mcp.json`, fill `E2B_API_KEY`, `/mcp` in Claude Code), `apps/sandbox_workflows/` (`uv sync`, `uv run obox …`).
- Each app also ships a prime command (`.claude/commands/prime*.md`) so an agent can self-orient.

### Common bootstrap thread (all five repos)
- **`.env` at repo root** for keys; `.env.sample`/`.env.example` templates committed, real file gitignored.
- **`uv` + `just`** as the recurring toolchain; **npm** for pi/Claude Code CLIs; **brew** on macOS.
- **An in-repo `/install` or `/prime` slash command** does the setup so the agent brings the machine up itself.
- **Global = `~/.claude/skills/` / `~/.claude/commands/`**; **project = `.claude/skills/` / `.claude/commands/` / `.claude/agents/`** — the same directory convention in every repo.
- **Deduplication across devices is git-based**: the-library syncs its fork; fusion-harness pins sessions under `/tmp`; nothing relies on a registry/marketplace.

---

## What we should copy

1. **Reference-catalog pattern (the-library).** Ship a repo that contains *only pointers* (abs-path / GitHub URL) plus a recipe the agent executes, never copies of the assets. A `library.yaml` of `{name, description, source, requires: [typed:refs]}` + a `use`/`sync`/`push` cookbook (clone-shallow-into-temp → `cp -R <parent>/` → cleanup) gives free private distribution and one-source-of-truth across devices. Keep it a **catalog, not a manifest** (available ≠ installed).
2. **Typed dependencies and "pull the parent dir, not the file."** `requires: [skill:x, agent:y, prompt:z]` resolved recursively, and copying the whole parent directory so scripts/refs/assets travel with a skill — both are worth adopting verbatim.
3. **Declarative fleet layout as a templateable JSON tree.** `cmux/fs-team.layout.json`'s `direction/split/children → pane.surfaces[]` shape, with each surface's `command` being the full launcher line and `__FEATURE__`/`__REPO__` tokens substituted at apply time, is a clean, reviewable, version-controllable way to define a team — far better than imperative split scripts.
4. **Role files = markdown + frontmatter, `model: inherit`.** `.claude/agents/<role>.md` with `name/description/color/model` frontmatter and a body that is the system prompt + lane rules + a completion sentinel. Binding the concrete model on the *launcher* line (`--model <provider/id>`), not in the role file, keeps roles model-agnostic and swappable.
5. **Runtime roster as a generated, gitignored JSON.** `.team/<team>.roster.json` mapping role → handle (`{team, workspace, feature, agents:{<role>:{surface}}}`), regenerated every spawn — separates the *declaration* (in git) from the *instance* (ephemeral).
6. **"Agentic Install" as a slash command.** Every repo's `/install` or `/prime` does prereq checks → key wiring → verify entry point → launch smoke test, with gotchas baked in (e.g., the `just` dotenv-vs-exported-var override trap). Standardizing this per repo makes fresh-machine bring-up a one-prompt operation.
7. **File + sentinel coordination over message buses.** `.team/<role>.md` notes, `.team/backlog.md`, and a `FLOTION-DONE: <role> | <summary>` line the lead greps from push events — cheap, debuggable, and harness-agnostic.
8. **Shared conventions to reuse wholesale:** `.env`/`.env.sample` for keys; `uv` + `just`; `.claude/{skills,commands,agents}/` directory layout; `~/.claude/*` for global vs `./.claude/*` for project; git as the cross-device sync (no marketplace, no central server).
