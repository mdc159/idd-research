# Analysis: `disler/agent-sandboxes`

Repo: `repos/agent-sandboxes` (origin `https://github.com/disler/agent-sandboxes.git`), same author family as the first four (IndyDevDan / "agenticengineer.com" footer, identical "Master Agentic Coding" CTA). `CLAUDE.md` is present but **empty (0 bytes)**; the real orientation lives in `README.md`, the big design spec `specs/sandbox-fork-cli-implementation.md`, and the per-app code under `apps/`. This report reads all of those and quotes them directly.

> **Headline for the E2B evaluation:** this repo is **entirely E2B** — it treats E2B as an opaque managed cloud service and contains **zero** local-container, Docker, Firecracker, KVM, Kata, or gVisor code or prose. A full-repo grep for `firecracker|docker|container|microvm|kvm|kata|gvisor|virtual` returns only a CSS `.container` class (`apps/sandbox_fundamentals/13_expose_simple_webserver.py:43`) and a `VIRTUAL_ENV` env-var pop (`apps/sandbox_mcp/server.py:51`). E2B's own public architecture is Firecracker-microVM-based, but **this codebase never says so** — it just calls the `e2b` Python SDK.

---

## 1. Purpose

A learning + tooling repo that explores running **Claude Code agents inside E2B cloud sandboxes** to get isolation, scale, and agency. From `README.md`:

> *"Agent Sandboxes unlock 3 key capabilities … **Isolation**: Each agent fork runs in a fully isolated, gated E2B sandbox … **Scale**: You can run as many agent forks as you want … **Agency**: Your agents have full control over the sandbox environment, they can install packages, modify files, run commands."*

It explicitly commits to one provider up front (`README.md` → "Agent Sandbox Tooling Choice"):

> *"Using **e2b** (General Sandbox SDK) for: Full control over sandbox environment; Shell command execution; File system operations; Running tools (Claude Code, git, npm, etc.)"*

So unlike the first four repos (which were planning/distribution/fusion/multiplexer layers), this one is the **execution-isolation layer**: it answers "where is it *safe* to let an agent run untrusted or high-blast-radius code?"

## 2. Architecture

The repo is a **ladder of five `apps/`**, each building on the one beneath it (`README.md` ordering):

```
sandbox_fundamentals/   raw E2B SDK patterns (13 PEP-723 uv scripts)
        │
sandbox_cli/             Typer CLI ("sbx") wrapping the E2B SDK
        │
sandbox_mcp/             FastMCP server wrapping sandbox_cli via subprocess  ← .mcp.json
        │
sandbox_workflows/       "obox": Typer CLI that runs N Claude agents in parallel forks
        │
cc_in_sandbox/ + sandbox_agent_working_dir/   minimal "claude in a box" + the agent's cwd
```

The dependency chain is concrete and layered:

- **`apps/sandbox_cli/src/modules/sandbox.py`** is the only place that talks to E2B directly — raw SDK calls, no abstraction:
  ```python
  from e2b import Sandbox
  def create_sandbox(...): return Sandbox.create(template=template, timeout=timeout, envs=envs, metadata=metadata)
  def kill_sandbox(sandbox_id): return Sandbox.kill(sandbox_id)
  def get_host(sandbox_id, port): ... return sbx.get_host(port)
  def pause_sandbox(sandbox_id): Sandbox.beta_pause(sandbox_id)
  ```
- **`apps/sandbox_mcp/server.py`** wraps that CLI by shelling out — every MCP tool is `run_sbx_cli(...)` doing `subprocess.run(["uv","run","sbx",*args], cwd=CLI_PATH, ...)` (lines ~28-56). It exposes ~18 tools (`init_sandbox`, `create_sandbox`, `connect_sandbox`, `kill_sandbox`, `execute_command`, `read_file`/`write_file`/`list_files`/`upload_file`/`download_file`/`make_directory`/`remove_file`/`rename_file`/`check_file_exists`/`get_file_info`, `get_host`, `list_sandboxes`, `pause_sandbox`). Crucially these are named `mcp__e2b-sandbox__*` (the MCP server key in `.mcp.json.sandbox` is `"e2b-sandbox"`).
- **`apps/sandbox_workflows/` ("obox")** is the payoff: a Typer command `sandbox-fork` that spins **N forks in N threads, each = one E2B sandbox + one Claude Code agent**. From `pyproject.toml`: `obox = "src.main:app"`, deps `typer`, `rich`, `claude-agent-sdk>=0.1.0`, `e2b>=2.6.4`. The flow (`src/commands/sandbox_fork.py`): validate repo URL/branch/forks/model → `forks.run_forks_parallel(...)` → each thread builds a `SandboxForkAgent` (`src/modules/agents.py`) → per-fork log file → open all logs in VSCode → summary table with cost/tokens/status.

### The "hybrid tool model" (the heart of the safety design)

Each fork agent runs **locally** (in `apps/sandbox_agent_working_dir/`, `cwd=str(WORKING_DIR)`) but is *steered* to do its real work **inside an E2B sandbox via MCP tools**. From `src/modules/agents.py`:

```python
self.options = ClaudeAgentOptions(
    system_prompt=self.system_prompt,
    mcp_servers=str(MCP_CONFIG_PATH),
    allowed_tools=ALLOWED_TOOLS,
    disallowed_tools=DISALLOWED_TOOLS,
    hooks=hooks_dict,
    permission_mode="acceptEdits",
    max_turns=self.max_turns,
    model=self.model,
    env=agent_env,                       # passes GITHUB_TOKEN through
    cwd=str(WORKING_DIR),
    setting_sources=["project"],         # enables the /plan /build /wf_plan_build commands
)
```

The system prompt (`src/prompts/sandbox_fork_agent_system_prompt.md`) makes the split explicit:

> *"You have two environments to work in: 1. **Agent Sandbox** - For repository operations (primary) 2. **Local directories** - For documentation and temporary files (restricted) … Use MCP sandbox tools (mcp__e2b-sandbox__*) for all repository operations."*

So the agent itself does **not** run inside the sandbox — it runs on the host, and the sandbox is a **remote, addressable workspace** it drives through MCP tools. (The alternative "ibox" pattern in `apps/cc_in_sandbox/run_claude_in_sandbox.py` instead boots `claude` *inside* the sandbox via `sbx.commands.run("echo '...' | claude -p --dangerously-skip-permissions")`.)

## 3. Tech stack

- **E2B** cloud sandbox SDK (`e2b>=2.6.4`) — the sole isolation provider. Used for: `Sandbox.create/connect/kill`, `commands.run` (with `background`/`cwd`/`user`/`root`/`shell`/`env_vars`/`timeout`), `files.read/write/list/upload/download`, `get_host(port)` (the `*.e2b.app` public URL), `beta_create(auto_pause=True)` / `beta_pause()` / `connect`-to-resume, and the `Template()` builder for custom images.
- **Claude Agent SDK** (`claude-agent-sdk`) — `ClaudeSDKClient`, `ClaudeAgentOptions`, and all six **hook** types (`PreToolUse`, `PostToolUse`, `UserPromptSubmit`, `Stop`, `SubagentStop`, `PreCompact`) via `HookMatcher`. This repo is **Claude-Code-centric, not pi-centric** (a shift from the first four repos); `pi` is not mentioned anywhere.
- **FastMCP** (`apps/sandbox_mcp/server.py`) for the MCP server; **Typer + Rich** for the two CLIs (`sbx`, `obox`).
- **uv + PEP-723 inline scripts** everywhere in `sandbox_fundamentals/` (`# /// script` blocks) — same toolchain thread as fusion-harness's `gate.py` and learning-cmux's `spawn_fast.py`.
- **`.mcp.json`** consumed by Claude Code (`/mcp`); `.claude/{commands,agents}/` conventions; `just`-style tasks replaced here by per-app `uv run` recipes. Optional **Firecrawl** MCP for the `docs-scraper` agent (`.claude/agents/docs-scraper.md`).
- Env (`.env.sample`): `E2B_API_KEY`, `ANTHROPIC_API_KEY`, `GITHUB_TOKEN`.

## 4. Sandbox providers / technologies covered

| Technology | Covered here? | Evidence |
|---|---|---|
| **E2B (cloud microVM service)** | ✅ **Only provider; pervasive** | `Sandbox.create(template=...)`, every fundamentals script, the CLI, the MCP server, the obox workflow |
| E2B **templates** | ✅ | `base`, `claude-code`, custom `agent-sandbox-dev-node22` built via `Template().from_base_image().run_cmd(...)` (`apps/sandbox_fundamentals/12_custom_template_build.py`) |
| E2B **public port exposure** | ✅ | `sbx.get_host(5173)` → `https://xxxxx.e2b.app` (`13_expose_vite_vue_webserver.py`, the `get_host` MCP tool) |
| E2B **pause/resume (beta)** | ✅ | `Sandbox.beta_create(auto_pause=True)`, `beta_pause()`, reconnect-resumes-state (`08_pause_resume.py`) |
| **Firecracker / microVM** | ❌ not mentioned | E2B is treated as a black box; the word never appears |
| **Docker / local containers** | ❌ not mentioned | — |
| **KVM / Kata / gVisor / namespaces / seccomp** | ❌ not mentioned | — |
| **Pluggable / abstracted backend** | ❌ | `sandbox_cli/src/modules/sandbox.py` calls `e2b.Sandbox.*` directly with no provider interface; the MCP server is a 1:1 wrapper. Porting to Docker/Firecracker-local would require rewriting this layer |

**Implication for the E2B evaluation:** the repo demonstrates the *full surface* of the E2B SDK (lifecycle, files, commands, templates, ports, pause/resume, metadata) and a clean MCP exposure of it, but it is **a single-vendor reference implementation, not a portable sandbox abstraction**. There is no local fallback and no "bring your own runtime."

## 5. Patterns it teaches for running agent code safely

1. **Remote sandbox as the blast-radius boundary.** Clone the untrusted repo *into* the E2B sandbox (`mcp__e2b-sandbox__execute_command(command="git clone ...")`), run all mutations there, and keep the host out of reach. The sandbox auto-times-out (default 300s; the obox system prompt sets `SANDBOX_LIFETIME_IN_SECONDS: 1800`) and is killed or left to expire.
2. **Hybrid tool model with an allow/deny matrix.** `constants.py` defines explicit `ALLOWED_TOOLS` (MCP `mcp__e2b-sandbox__*` + local `Read/Write/Edit/Bash` + utilities) and `DISALLOWED_TOOLS` (`NotebookEdit`). This is the same "scoped toolset per role" idea as fusion-harness's `READONLY_TOOLS`/`FULL_TOOLS`/`VALIDATOR_TOOLS`.
3. **Hook-based path confinement + full observability.** A `PreToolUse` hook (`src/modules/hooks.py`) resolves the `file_path` of `Read`/`Write`/`Edit` and **blocks** anything outside `ALLOWED_DIRECTORIES` (`temp/`, `specs/`, `ai_docs/`, `app_docs/`):
   ```python
   return {"hookSpecificOutput": {"hookEventName": "PreToolUse",
           "permissionDecision": "deny",
           "permissionDecisionReason": f"Path '{file_path_str}' is outside the allowed directories ..."}}
   ```
   All six hook types also stream a complete audit trail to a per-fork log (`logs/<branch>-fork-<n>-<ts>.log`).
4. **"ibox" vs "obox" — two ways to isolate an agent.** `ibox` (`cc_in_sandbox/`, `09_claude_code_agent.py`) runs the whole `claude` binary *inside* the sandbox with `--dangerously-skip-permissions` — acceptable *because* the microVM is the boundary. `obox` runs the agent on the host and drives the sandbox through MCP — acceptable *because* all repo-touching tools are the sandbox-scoped MCP ones.
5. **Plan → Build → Validate slash-command loop inside the sandbox.** The agent's project commands (`apps/sandbox_agent_working_dir/.claude/commands/{plan,build,wf_plan_build}.md`) implement the same spec-then-build-then-validate rhythm seen in planf3 and fusion-harness — and the system prompt reminds the agent these commands "always run against the sandbox, not the local filesystem."
6. **Per-fork logging + cost/token accounting.** Each fork gets its own logger; `ResultMessage.usage` is mined for `input_tokens`/`output_tokens`/`total_cost_usd` (`agents.py`).

## 6. Mapping to the three-tier sandbox model

| Tier | Concept | Present in this repo? | How |
|---|---|---|---|
| **Tier 1 — Local rule-based guardrails** | In-process policy: tool allow/deny, path allowlists, permission modes, prompt instructions | ✅ **Strong** | `ALLOWED_TOOLS`/`DISALLOWED_TOOLS`, `permission_mode="acceptEdits"`, the `PreToolUse` path-gating hook, and the "Allowed Directories" system-prompt contract. Pure software policy, no OS boundary. |
| **Tier 2 — OS-level workspace sandbox** | A real local isolation boundary for the agent's own working dir (chroot/namespaces/seccomp/Docker/Firecracker-local) | ⚠️ **Emulated, not real** | `apps/sandbox_agent_working_dir/` is an ordinary directory. Its "confinement" is *only* the Tier-1 hook checking `Path.relative_to(ALLOWED_DIRECTORIES)`. There is **no** local container/VM. |
| **Tier 3 — Cloud microVMs for untrusted code** | Fully isolated remote VM per fork | ✅ **The entire point** | E2B sandboxes — one per fork — where repos are cloned, packages installed, commands run, servers exposed. This is where untrusted/high-blast-radius work is dispatched. |

**The defining architectural choice:** the repo **offloads essentially all isolation to Tier 3 (E2B)** and uses Tier 1 (hooks) only for *steering and observability* on the host side. **Tier 2 is effectively skipped** — there is no defense-in-depth local sandbox between "the agent process" and "your laptop." Two concrete consequences:

- **`Bash` is a known escape hatch from the Tier-1 "allowed directories."** In `hooks.py`, `Bash` is in `ALLOWED_TOOLS` and the `PreToolUse` hook only **logs** it (`elif tool_name == "Bash": logger.log("INFO", ...)`) — it does **not** block or parse it. So an agent (or a prompt-injection payload inside a cloned repo) can run arbitrary local shell commands that touch the host filesystem outside `ALLOWED_DIRECTORIES`. The hook observes; it does not prevent. For an evaluator, this is the single most important gap to note: the "local workspace sandbox" is a tripwire, not a wall.
- **Correctness is not enforced by the sandbox.** Isolation answers "can it damage my machine?" (no). It does **not** answer "did it build the right thing?" — which is the job of the verifier/gate patterns (see next section).

## 7. Overlaps & conflicts with damage-control and verifier/gate patterns

*(For "damage control" I reason from the concept — limiting agent blast radius, least privilege, safe rollback/kill — since the `pi-vs-claude-code` repo is not in this workspace. The verifier/gate comparison is against the patterns I analyzed in `analysis/glm1-report.md`: fusion-harness `/auto-validate`, planf3 Build Plan, learning-cmux Flotion test worker.)*

### Overlaps (same ideas, same vocabulary)

1. **Hook path-gating = a rule-based guardrail (Tier 1 damage control).** The `PreToolUse` `permissionDecision: "deny"` for out-of-bounds paths is the same family as fusion-harness's clean-room children (`--no-skills --no-extensions --no-context-files`), its scoped tool matrices, and pi's `--no-tools`. All are "deny by policy before execution."
2. **Plan → Build → Validate loop.** `plan.md` → `build.md` → `wf_plan_build.md` is structurally identical to planf3's Create→Build workflows and fusion-harness's spec→/fusion→/auto-validate ladder. `build.md` even uses the same refrain as planf3's checklist loop:
   > *"If you have not run any validation commands throughout your implementation, DO NOT STOP until you have validated the work."* (`apps/sandbox_agent_working_dir/.claude/commands/build.md`)
3. **Fan-out / parallel forks = cloud-microVM equivalent of the fleet.** `obox sandbox-fork --forks N` is the E2B analogue of learning-cmux's 2×2 fleet and fusion-harness's `/opinion`/`/fusion` parallel workers — "scale compute by fanning out independent agents," just with each worker in its own VM instead of its own pane/subprocess.
4. **Artifact-grounded coordination.** Per-fork logs + the `specs/` plans + the roster-style working dir continue the "coordinate via files, not message buses" thread from the first four repos.
5. **uv PEP-723 single-file scripts** for deterministic tooling (fundamentals examples) — same as fusion-harness's `gate.py`.

### Conflicts / tensions (what an evaluator should flag)

1. **Gate is *optional and prompt-level* here; *mandatory and automated* in fusion-harness.** fusion-harness `/auto-validate` designs the gate **before** the build, requires a **red baseline**, runs `gate.py` (a real executable), feeds `FAIL: expected X, found Y, at PATH` lines back **verbatim**, and loops until green or halt — with gate-repair on `GATE DEFECT`. Here, `build.md` only *instructs* the agent to "run validation commands." There is **no `gate.py`, no red-baseline check, no automated fail→correction loop.** A fork can ship unvalidated work and the hooks will not catch it (hooks gate *paths*, not *correctness*). **Strong process isolation + weak output verification.**
2. **The two patterns are complementary, not competing — and this repo uses only one half.** Sandboxes = *where it's safe to run untrusted code*; gates = *whether the result is correct*. agent-sandboxes leans ~100% on the former; fusion-harness/planf3 lean on the latter. The natural synthesis (which neither repo fully implements) is **fusion-harness's gate loop running *inside* an E2B sandbox** — i.e., put `/auto-validate`'s `gate.py` into the obox system prompt so each fork must pass a real gate before it commits/pushes.
3. **`--dangerously-skip-permissions` inside the sandbox is a deliberate philosophy inversion vs damage-control "least privilege."** `cc_in_sandbox/run_claude_in_sandbox.py` and `09_claude_code_agent.py` run `claude -p --dangerously-skip-permissions` *inside* the E2B VM. That is defensible **because the microVM is the boundary** — but it directly contradicts the minimize-permissions instinct. Worth flagging: in this design, *more* permissions inside the sandbox is the point, because Tier-1 guardrails are made redundant by Tier-3 isolation. (obox does the opposite — keeps permissions and adds hooks on the host — so the two apps in the same repo embody two different trust philosophies.)
4. **Tier-2 absence conflicts with defense-in-depth damage control.** A damage-control posture wants overlapping controls: policy ∧ OS sandbox ∧ VM. Here it is policy ∧ VM, with a `Bash`-shaped hole in the policy (§6). If the evaluator's threat model includes a compromised/prompt-injected agent reaching the host via the orchestrator process, the lack of a real local workspace sandbox is the weak link.
5. **No rollback / no snapshot beyond E2B pause.** Damage control usually wants easy undo. The only snapshot-like primitive is E2B's beta `pause`/resume (`08_pause_resume.py`), which preserves filesystem state but is not wired into the obox workflow as a rollback path. fusion-harness's `/fh-reset` and the-library's git-pull-as-source-of-truth are closer to "undo" than anything here.
6. **Single-provider lock-in vs the first repos' portability.** the-library and planf3 are deliberately harness-agnostic (any tool reading `.claude/skills/`); learning-cmux treats agents as heterogeneous peers. agent-sandboxes is the opposite — hardcoded to E2B and Claude. That is fine for an E2B evaluation but it means the safety patterns here (MCP-over-E2B, the hook path-gate) do not port to a local-Docker or self-hosted-Firecracker tier without rewriting `sandbox_cli/src/modules/sandbox.py` and the MCP tool set.

## 8. Relation to the broader agentic stack (vs the first four repos)

This repo fills the **execution-isolation slot** the first four repos left empty:

| Earlier repo | Layer | What agent-sandboxes adds |
|---|---|---|
| planf3 | planning | A *safe place* for planf3's Build Plan to run its validation commands without touching prod |
| fusion-harness | in-process multi-model | Where to push `/auto-validate`'s builder when the task is genuinely untrusted (clone-unknown-repo, run-unknown-code) |
| learning-cmux (cmux≈herdr) | multi-pane fleet | The same fan-out thesis, but each fork is a **cloud microVM** instead of a local pane — cmux scales *terminals*, E2B scales *isolated machines* |
| the-library | distribution | The mechanism to ship *this* repo's MCP/skill across devices — and notably, the-library's `use` flow itself clones untrusted repos locally with no sandbox, which is exactly the risk agent-sandboxes exists to remove |

**Net assessment for the E2B evaluation:** agent-sandboxes is a clean, well-documented E2B reference implementation that shows the full SDK surface, a sensible MCP exposure, and a working parallel-fork workflow with hook-based host-side guardrails. Its limitations for a defense-in-depth evaluation are equally clear: (a) E2B-only, no local/container/Firecracker tier and no pluggable backend; (b) Tier-2 local sandboxing is emulated by hooks and bypassable via the allowed-but-unparsed `Bash` tool; (c) output *correctness* verification is left as a soft prompt instruction, not an automated gate — so it complements, but does not replace, the verifier/gate patterns from fusion-harness and planf3.
