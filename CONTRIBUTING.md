# The Vault — how records land here

This repo is the fleet's vault: the interim home for narrative records until the vault moves to its VPS host (when it does, only the resolution line in bibliotec's `playbook/documentation.md` changes). It holds records, not rules — prescriptive content (procedures, conventions, doctrine) belongs in [bibliotec](https://github.com/mdc159/bibliotec).

The toll for a record is deliberately small: a frontmatter block and an index line. That's the whole contract — low enough to never hinder a contribution, enough that every record is traceable and findable.

## Structure

| Directory | Holds | `type:` |
|---|---|---|
| `reports/` | Mission outputs — audits, sweeps, worker reports | `report` |
| `research/` | Studies, repo analyses, investigations | `research` |
| `handoffs/` | Orchestrator session handoffs | `handoff` |
| `certifications/` | Full Check-out Gauntlet exam records with evidence | `certification` |
| `artifacts/` | Non-record files (demo outputs, specimens) — not gated | — |

Filenames: `YYYY-MM-DD-kebab-title.md`, date first so listings sort themselves.

## The frontmatter block

Every record opens with:

```yaml
---
date: 2026-07-23
worker: ver-gpt56-codex   # role-model-provider per the fleet naming convention; or orchestrator, or user
type: report              # report | research | handoff | certification — must match the directory
mission: ""               # Linear ID or brief path, when one exists
source: ""                # repo, PR, or session that produced this, when one exists
---
```

## The index

`INDEX.md` is the register — one line per record: date, type, worker, a one-sentence hook, and the link. A record isn't in the vault until its index line is. Write the hook so it can be judged without opening the record; the index is what a future retrieval layer ingests.

## How writes land

Branch + PR to `main` (locked by ruleset). The `vault-gate` CI check validates exactly the toll — frontmatter present and typed correctly, filename pattern, directory placement, index line added — and nothing more. Red gate, no merge. Reviewer guidance lives in `AGENTS.md`.
