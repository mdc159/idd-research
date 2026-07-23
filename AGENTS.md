# AGENTS.md — the vault (idd-research)

## For PR reviewers: the vault rubric

End every review with `Score: N/5` — one point per criterion met, naming the criterion lost for any missing point:

1. **Traceable** — frontmatter is truthful and complete: real worker name, real date, mission/source filled when they exist (empty only when there genuinely is none).
2. **Placed** — the record sits in the directory matching its `type:`; filename is `YYYY-MM-DD-kebab-title.md`.
3. **Indexed** — `INDEX.md` gained a matching line whose one-sentence hook honestly summarizes the record and can be judged without opening it.
4. **Self-contained** — the record stands alone: claims cite their evidence (files, runs entries, sessions); a reader needs no session context to follow it.
5. **Records, not rules** — nothing prescriptive: no procedures, conventions, or doctrine (those belong in bibliotec); no mandate language; the words "canonical"/"canon" are banned.

The mechanical layer (frontmatter keys, filename pattern, placement, index line) is enforced by the `vault-gate` CI check — don't spend comments on what the gate already catches; spend them on honesty of the hook, quality of the citations, and rule-creep. Be terse and evidence-first.

## For all other agents

This repo is the fleet's vault: records land per `CONTRIBUTING.md`. Operating procedure lives in bibliotec (`playbook/SKILL.md`); the documentation contract is bibliotec `playbook/documentation.md`.
