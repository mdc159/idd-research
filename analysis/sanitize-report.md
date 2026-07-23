# Sanitize Sweep Report — 2026-07-23

Scope: in-place edits to **tracked files only** (`git ls-files`) across four working trees.
No commits or pushes. All changes are unstaged in their respective working trees for
orchestrator diff review (`git diff`).

Repos:
- `~/.claude/skills/library`
- `~/Projects/herdr-verifier`
- `~/Projects/IDD`
- `/mnt/data/Documents/Obsidian-Linux/Global` (Obsidian vault)

## Headline result

- **7 replacements across 5 files in 4 repos** (all subscription/billing commentary → neutral tier language).
- **`/home/hammer`**, **`/mnt/data/Documents/Obsidian-Linux/Global`**, and the hostname
  **`hammer-Precision-M6800`** appear in **zero tracked files** across all four repos — no
  path/hostname edits were required. (Confirmed by `git grep`.)
- Load-bearing code (`watcher.py`, both `justfile`s) is already path-clean: `watcher.py` derives
  its root via `ROOT = Path(__file__).resolve().parent` and defaults `--runs-dir` to `ROOT/"runs"`;
  justfiles use relative paths only. No code edits needed; nothing flagged.
- 6 items **flagged** below for orchestrator decision (audit-quote integrity, hardware identifiers,
  provider-product docs).

---

## Repo 1 — `~/.claude/skills/library`

### Changed
| File | Replacements | Detail |
|---|---|---|
| `playbook/SKILL.md` | 1 | L23 `(flat-rate coding plan)` → `(per-node subscription)`; kept `zai/glm-5.2` routing key |

### Flagged
*(none)*

### Reviewed, left unedited
- `playbook/SKILL.md` L16/L21, `playbook/lessons.md` L7 — "Codex OAuth billing": this is the
  technical auth/billing **mechanism** (OAuth vs API-key), not an evaluative plan descriptor. Kept.
- `cookbook/bootstrap.md` L24, `playbook/SKILL.md` L12/L27 — generic neutral uses of "subscription(s)"
  ("whatever subscriptions this machine holds"). Kept.

---

## Repo 2 — `~/Projects/herdr-verifier`

### Changed
| File | Replacements | Detail |
|---|---|---|
| `specs/herdr-verifier-port.html` | 2 | L270 `(top-tier, flat-rate, 1M context …)` → `(top-tier, per-node subscription, 1M context …)`; L272 `acceptable on flat rate` → `acceptable on a per-node subscription` |

### Flagged
*(none in tracked files)*

### Reviewed, left unedited / noted
- **`runs/*.jsonl` (rule 4)** — inspected `runs/2026-07-22.jsonl` and `runs/2026-07-23.jsonl`.
  **No `/home/hammer` present** in any string; no fields changed. **Note:** `runs/` is **gitignored**
  (`.gitignore` L5 `runs/`); these files are **untracked**, so any future edits there will **not**
  appear in `git diff` for orchestrator review. Also untracked: `calibration/`,
  `specs/2026-07-22-verifier-calibration-spec.md`.
- `watcher.py`, `justfile` — path-clean (see Headline). No edits.

---

## Repo 3 — `~/Projects/IDD`

### Changed
| File | Replacements | Detail |
|---|---|---|
| `SESSION-HANDOFF-2026-07-22.md` | 1 | L15 `(most generous plan)` → `(per-node subscription)` |

### Flagged
| File | Location | Reason |
|---|---|---|
| `analysis/drift-audit-2026-07-22.md` | L26 (Claim), L30 (`<<<` old), L31 (`>>>` new) | The phrases `most generous plan` and `ChatGPT/Codex subscription` appear **exclusively inside the audit's verbatim quoted records** (a `Claim:` line and a `<<<`/`>>>` before/after patch). This file is an **evidentiary drift audit**: the `<<<` line documents the source note's *old* text and the `>>>` line is the *corrected* text that was applied to `Delegation Economics.md`. Rewriting these quotes would **falsify the before/after record** and decouple the audit from the source it references. **Left unedited.** Recommend orchestrator decide: (a) keep as-is (phrases are quoted evidence, not authorial commentary), (b) exclude this file from public release, or (c) explicitly accept rewriting the quotes. |
| `SESSION-HANDOFF-2026-07-22.md` | L45 | Fleet inventory names the current host by **model**: `M6800 + newer Dell + Mac mini + VPSs`. This is **not** the literal hostname `hammer-Precision-M6800` (rule 2), but `M6800` identifies the Precision M6800 = this machine. **Left unedited** (rule 6). Suggested neutralization if desired: replace `M6800` with `<host>`, e.g. `<host> + newer Dell + Mac mini + VPSs`. |

### Reviewed, left unedited
- `SESSION-HANDOFF-2026-07-22.md` L11 — "workers run on cheap subscriptions": generic structural
  characterization (cheap workers vs. expensive orchestrator), not a plan name/descriptor. Kept.

---

## Repo 4 — `/mnt/data/Documents/Obsidian-Linux/Global` (vault)

Rule 1 calls for **vault-relative** paths in the vault's own notes. `git grep` found **no**
`/home/hammer` or `/mnt/data/.../Global` self-references in any tracked vault note, so no path
rewrites were needed here. Only subscription commentary was edited.

### Changed
| File | Replacements | Detail |
|---|---|---|
| `03-Resources/Agentic Terminal Stack/Delegation Economics.md` | 2 | L20 "Bills to" cell `ChatGPT/Codex subscription` → `per-node subscription`; L22 `z.ai flat-rate coding plan` → `z.ai per-node subscription` |
| `03-Resources/Agentic Terminal Stack/Multi-Agent Orchestration Playbook.md` | 1 | L138 `(flat-rate coding plan)` → `(per-node subscription)` |

> Note on the `Delegation Economics.md` "Bills to" column: row L20 follows rule 3 literally
> (`ChatGPT/Codex subscription` is a listed whole-phrase → `per-node subscription`); row L22 keeps
> the `z.ai` biller prefix and neutralizes only the listed sub-phrase `flat-rate coding plan`
> (the `zai`/z.ai provider is not otherwise named in that row's Route cell, which reads `Pi → GLM-5.2`).
> Provider routing keys are preserved in every Route column.

### Flagged
| File | Location | Reason |
|---|---|---|
| `03-Resources/Agentic Terminal Stack/Agentic Terminal Stack MOC.md` | L31 | Mermaid node `W2["Workspace: m6800-freecad"]` — workspace name embeds the host **model** (`m6800` = Precision M6800 = this machine). Not the literal hostname (rule 2), so **left unedited** (rule 6). Suggested neutralization: `Workspace: <host>-freecad` or a generic label. |

### Reviewed, left unedited (provider-product documentation, not user billing commentary)
- `Pi - The Multi-Model Primitive.md` L40 `(z.ai coding plan)`, L41 `Kimi coding subscription`,
  L45 model surfaces (`kimi-for-coding (subscription)`, `kimi-k2.7-code (pay-per-token coding)`):
  these document the **providers' product surfaces/endpoints** (e.g. `api.z.ai/api/coding/paas/v4`,
  `api.kimi.com/coding`) and are tied to real product names in the endpoint URLs. Treated as
  **technical product documentation**, not the user's personal billing commentary. Kept. Flag for
  review if you want product-surface names neutralized too.
- `Agentic Terminal Stack MOC.md` L45 `GLM["z.ai GLM-5.2<br/>(coding plan)"]` — Mermaid node label,
  same "coding plan" product descriptor as above. Kept.
- `Delegation Economics.md` L19 `Claude subscription`, L21 `Moonshot/Kimi plan`: structurally
  parallel to the flagged `ChatGPT/Codex subscription` but **not** in rule 3's explicit list and
  carry no evaluative descriptor (`most generous` / `flat-rate`). **Left unedited for literal rule
  compliance.** If you want the whole "Bills to" column uniform, neutralize these two cells to
  `per-node subscription` as well.
- `Delegation Economics.md` L13 "50% of the subscription cap" — generic "subscription cap"; not a
  plan name. Kept.
- `Friction Log.md` L43, `Multi-Agent Orchestration Playbook.md` L29/L136 — "ChatGPT OAuth" /
  "API-key billing": technical auth mechanism. Kept.

---

## Cross-repo notes

- **Public identity preserved:** `github.com/mdc159` / `git@github.com:mdc159/...` repo URLs and the
  `mdc159/bibliotec` remote were **not touched** (per rule 5). They appear in
  `library`/`README.md`-adjacent context and in `IDD/analysis/drift-audit-2026-07-22.md` as verified
  facts.
- **`.git` dirs, git config:** untouched.
- **No code semantics changed.** The only files with executable meaning (`watcher.py`, `justfile` ×2,
  `pyproject.toml`, `uv.lock`, `tests/*`) were inspected and are path/hostname-clean; no edits.
- **Untracked working files** (not part of this sweep, FYI): herdr-verifier `calibration/`,
  `specs/2026-07-22-verifier-calibration-spec.md`, `runs/` (gitignored).

DONE: workhorse | sanitize sweep complete
