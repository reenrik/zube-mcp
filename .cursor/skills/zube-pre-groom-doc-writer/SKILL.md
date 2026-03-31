<!-- markdownlint-disable MD060 -->

# Zube Pre-Groom Doc Writer

Use this skill to create or update a pre-groom planning document before Zube card grooming. The goal is a clean task list with estimates, dependencies, and verifiable acceptance criteria.

## Inputs

- Initiative or epic name
- Source docs (PRD, ADR, architecture notes, existing planning docs)
- Output doc path
- Environment/stage context if needed (`Dev`, `Staging`, `Production`)
- Known dependencies or constraints

Ask brief clarifying questions if these are incomplete.

## Style Rules

Use this style by default:

1. Title + short initiative context paragraph.
2. `## Task Table` with one independently deliverable task per row.
3. `## Task Scope and Acceptance Criteria` with a matching section for every row.
4. Scope and Out of Scope are separate bullet lists.
5. Acceptance criteria are checkbox items and independently verifiable.
6. Dependencies are explicit (`[1]`, `[2], [3]`, and concrete external links if needed).

## Output Document Shape

Include:

1. Title and context
2. `## Task Table`
3. `## Task Scope and Acceptance Criteria`
4. Related references

### Task Table Template

| # | Zube | Task | Category | Estimate | Depends On | Status |
|---|------|------|----------|----------|------------|--------|
| 1 | — | task title | category | 2-4h | — | Todo |

Rules:

- One independent deliverable per row.
- Estimate uses range (`1-2h`, `4-8h`, `16-24h`) or `TBD` only when unknown.
- `Depends On` uses row refs (`[1]`, `[2], [3]`) and epic/doc links where useful.
- `Zube` is `—` until card numbers exist.
- `Status` values: `Todo`, `Blocked`, `In Progress`, `Done`.
- Optional columns by domain:
  - FE/UI work: `Stage`, `Figma Link?`
  - Grooming progress: `Scope + AC in Zube?`, `Groomed`

### Per-Task Detail Template

```markdown
### Task N -- <task title>

**Scope**
- <concrete deliverable>

**Out of Scope**
- <explicitly excluded item>

**Acceptance Criteria**
- [ ] <specific, testable criterion>

**Dependencies**
- <task refs or prerequisite conditions>
```

## Quality Bar

- Task table and detail sections must stay in sync.
- Acceptance criteria must be observable and testable.
- Dependencies describe sequencing, not people.
- Split tasks that are too large (for example > `24-40h`).

## Reference Conventions

- Use this skill's style by default.
- If source docs provide stronger local conventions, keep this structure but adopt local naming.
- Do not hard-code project IDs/slugs unless explicitly provided.

## Done Condition

Close with a short readiness checklist:

- [ ] Task list approved
- [ ] Estimates approved
- [ ] Dependencies approved
- [ ] Ready for card grooming (`zube-groomer`)
