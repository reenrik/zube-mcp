---
name: zube-pre-groom-doc-writer
description: Creates a pre-groom planning document with a prioritized task table, estimates, dependencies, and per-task Scope/Out of Scope/Acceptance Criteria sections before Zube card grooming.
allowed-tools: Read, Grep, Glob, Edit, Write
---

<!-- markdownlint-disable MD060 -->

# Zube Pre-Groom Doc Writer

Use this skill to create or update a planning document before card grooming. The output should turn raw initiative context into a task list with estimates and dependencies that is ready for card-by-card grooming.

## Inputs

Collect these inputs first:

- Initiative or epic name
- Source material paths (PRDs, ADRs, architecture docs, existing planning docs)
- Target repository and output path
- Environment/stage context if relevant (`Dev`, `Staging`, `Production`)
- Any known dependency constraints

If key inputs are missing, ask concise clarifying questions before writing.

## Style Rules

Use this style by default for pre-groom docs:

1. Start with context: title, epic/initiative link (if available), and a one-paragraph scope statement.
2. Add a `## Task Table` with one row per independently deliverable task.
3. Add `## Task Scope and Acceptance Criteria` with a matching section for every task row.
4. Keep task language implementation-specific; avoid vague planning prose.
5. Keep dependencies explicit and machine-readable (`[1]`, `[2], [3]`, or concrete external links).

Do not include project IDs/slugs/links unless provided by the user or source docs.

## Required Output Structure

Write the planning doc with this skeleton:

1. Title + initiative context
2. Story/goal coverage summary (optional but recommended for larger efforts)
3. `## Task Table`
4. `## Task Scope and Acceptance Criteria`
5. Related docs / references

### Task Table Standard

Use this default table:

| # | Zube | Task | Category | Estimate | Depends On | Status |
|---|------|------|----------|----------|------------|--------|
| 1 | — | task title | category | 2-4h | — | Todo |

Rules:

- Keep one independent deliverable per row.
- Estimates are ranges (`1-2h`, `4-8h`, `16-24h`) or `TBD` only when truly unknown.
- `Depends On` uses task row references (`[1]`, `[2], [3]`) and/or epic links when needed.
- `Zube` is `—` in pre-groom docs unless card numbers already exist.
- `Status` defaults to `Todo`; allowed values: `Todo`, `Blocked`, `In Progress`, `Done`.
- Add optional columns only when needed by domain:
  - FE/UI work: `Stage`, `Figma Link?`
  - Grooming progress tracking: `Scope + AC in Zube?`, `Groomed`

### Task Detail Standard

For every task row, include a matching section:

```markdown
### Task N -- <task title>

**Scope**
- <concrete deliverable>
- <concrete deliverable>

**Out of Scope**
- <explicitly excluded item>

**Acceptance Criteria**
- [ ] <specific, independently verifiable criterion>
- [ ] <specific, independently verifiable criterion>

**Dependencies**
- <task refs, epic refs, or concrete prerequisite conditions>
```

## Estimation Guidance

Use pragmatic ranges for first-pass planning:

- `1-2h` very small change
- `2-4h` small scoped task
- `4-8h` moderate implementation
- `8-16h` substantial cross-module work
- `16-24h` large effort
- `24-40h` major multi-system effort
- `40h+` split recommended

If a task looks larger than `24-40h`, split it into smaller tasks where possible.

## Quality Gate

Before finalizing, verify:

- Table and detailed sections are consistent (same task count and numbering).
- No bundled mega-tasks; each row is actionable.
- Acceptance criteria are observable/testable, not vague.
- Dependencies reflect sequencing, not people ownership.
- Terminology matches target repo conventions.
- Scope and Out of Scope are separate bullet lists (never mixed).
- Every task in the table has a corresponding detailed section.

## Hand-off to Grooming

End with a short "Ready for grooming" checklist:

- [ ] Task list approved
- [ ] Estimates approved
- [ ] Dependencies approved
- [ ] Scope boundaries approved

Once approved, use `zube-groomer` to convert tasks into card bodies and create cards.
