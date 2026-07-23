- Agentic Terminal Stack MOC.md:60 — Repo locations, names, visibility, remotes
  Claim: | The Library | installed locally, 2 commits, catalog seeded; no remote yet |
  Actual: `~/.claude/skills/library` has remote `origin → git@github.com:mdc159/bibliotec.git` (private) and 11 commits on HEAD; it is already pushed. `gh repo view mdc159/bibliotec` confirms a private, non-fork repo.
  Verified via: `git -C ~/.claude/skills/library remote -v`; `git -C ~/.claude/skills/library rev-list --count HEAD` (= 11); `gh repo view mdc159/bibliotec`
  Patch:
    <<< | The Library | installed locally, 2 commits, catalog seeded; no remote yet |
    >>> | The Library | installed locally, remote `mdc159/bibliotec` (private), catalog seeded |

- The Library - Local Setup.md:11 — Repo locations, names, visibility, remotes
  Claim: IndyDevDan's skill-distribution meta-skill is installed at `~/.claude/skills/library/` as a local git repository. It has **2 commits** and no remote yet; publishing it to GitHub is a future step.
  Actual: The checkout has a remote (`git@github.com:mdc159/bibliotec.git`) and 11 commits; publishing already happened. `mdc159/bibliotec` is the private operational repo (per `playbook/lessons.md` and `Bibliotec.md`).
  Verified via: `git -C ~/.claude/skills/library remote -v`; `git -C ~/.claude/skills/library rev-list --count HEAD` (= 11); `gh repo view mdc159/bibliotec`
  Patch:
    <<< IndyDevDan's skill-distribution meta-skill is installed at `~/.claude/skills/library/` as a local git repository. It has **2 commits** and no remote yet; publishing it to GitHub is a future step.
    >>> IndyDevDan's skill-distribution meta-skill is installed at `~/.claude/skills/library/` as a local git repository. Its remote is `mdc159/bibliotec` (private) and it has been pushed; keep it in sync as the catalog grows.

- The Library - Local Setup.md:37 — Repo locations, names, visibility, remotes
  Claim: Add a remote and push the two-commit Library repository to GitHub when the local catalog is ready to become the shared source of truth.
  Actual: The remote (`mdc159/bibliotec`) already exists and the repo is pushed (11 commits); the "next step" is no longer adding a remote.
  Verified via: `git -C ~/.claude/skills/library remote -v`; `git -C ~/.claude/skills/library rev-list --count HEAD`
  Patch:
    <<< Add a remote and push the two-commit Library repository to GitHub when the local catalog is ready to become the shared source of truth.
    >>> The Library repository already has its `mdc159/bibliotec` remote and is pushed; run `library sync` (or `git pull` in the skill dir) to keep each device's catalog current as it grows.

- Delegation Economics.md:20 — Operational conventions (launch, routing, roles)
  Claim: | Default heavy lean | Codex models | Default workers for substantial implementation; this is the most generous plan | ChatGPT/Codex subscription |
  Actual: Per `playbook/SKILL.md`, default substantial implementation routes through Pi → `openai-codex/...` (GPT models on Codex OAuth billing); `playbook/lessons.md` (2026-07-22) records that direct `--kind codex` launches were retired. Presenting "Codex models" as the default worker route contradicts current procedure.
  Verified via: `~/.claude/skills/library/playbook/SKILL.md` ("Roles and model routing"); `~/.claude/skills/library/playbook/lessons.md` (2026-07-22 GPT-via-Pi retirement)
  Patch:
    <<< | Default heavy lean | Codex models | Default workers for substantial implementation; this is the most generous plan | ChatGPT/Codex subscription |
    >>> | Default heavy lean | Pi → `openai-codex/...` | Default workers for substantial implementation; GPT models on Codex OAuth billing | ChatGPT/Codex subscription |

- Delegation Economics.md:32 — Operational conventions (launch, routing, roles)
  Claim: R --> C["Codex agent"]
  Actual: Default-implementation GPT workers are no longer launched as a standalone "Codex agent"; they run as Pi-hosted agents (`Pi → openai-codex/...`). The sibling nodes already use the `Pi → ...` form, so this node is the stale exception.
  Verified via: `~/.claude/skills/library/playbook/SKILL.md` (Model routing table); `~/.claude/skills/library/playbook/lessons.md` (direct Codex launch retired)
  Patch:
    <<<     R --> C["Codex agent"]
    >>>     R --> C["Pi → openai-codex"]

- Friction Log.md:91 — Operational conventions (launch, routing, roles)
  Claim: **Fix / rule →** Open question: eventually host Codex models through Pi — `--kind pi --model openai-codex/gpt-5.6-sol` — for a uniformly drivable fleet.
  Actual: This is no longer an open question or future step. `playbook/SKILL.md` canonizes exactly this — GPT models run through Pi's `openai-codex` provider (`--kind pi --model openai-codex/...`) — and `playbook/lessons.md` records the decision (2026-07-22). Presenting it as "eventually" contradicts current procedure.
  Verified via: `~/.claude/skills/library/playbook/SKILL.md` ("Roles and model routing" + "GPT models run through Pi's openai-codex provider"); `~/.claude/skills/library/playbook/lessons.md`
  Patch:
    <<< **Fix / rule →** Open question: eventually host Codex models through Pi — `--kind pi --model openai-codex/gpt-5.6-sol` — for a uniformly drivable fleet.
    >>> **Fix / rule →** Resolved — GPT models now host through Pi (`--kind pi --model openai-codex/...`) per the playbook, which sidesteps the Codex-TUI friction in items 1–5 for automated fleets.

- Herdr Verifier - Status.md:19 — Verifier status and evidence
  Claim: | Infeasible task | Live | Verifier correctly reasoned about SHA256 infeasibility |
  Actual: `~/Projects/herdr-verifier/runs/*.jsonl` contain 4 entries total (2026-07-22: 1; 2026-07-23: 3) — all `builder=glm2`, all `status=verified`, slices spanning lines 1–30 of a repo-survey artifact, zero with `feedback` or `escalated`. None is an infeasible/SHA256 task. The SHA256-preimage infeasibility determination this session was made by the orchestrator (Claude), not by the verifier, so it is not verifier evidence.
  Verified via: `~/Projects/herdr-verifier/runs/2026-07-22.jsonl`; `~/Projects/herdr-verifier/runs/2026-07-23.jsonl`
  Patch:
    <<< | Infeasible task | Live | Verifier correctly reasoned about SHA256 infeasibility |
    >>> | Infeasible task | Orchestrator-side (not a verifier run) | Orchestrator correctly reasoned SHA256 preimage infeasibility; no corresponding entry exists in `runs/*.jsonl` |

DONE: workhorse | 7 findings
