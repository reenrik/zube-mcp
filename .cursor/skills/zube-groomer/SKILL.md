<!-- markdownlint-disable MD032 MD040 MD060 -->

# Zube Groomer

Use this skill to groom work tasks from local planning documents into well-structured Zube cards. Default mode is preview; create cards only after explicit confirmation.

## Inputs

Identify these before producing output:

- Planning document path (for example: `reach-app/docs/planning/marketplace/MARKETPLACE-BE-GROOMING-CHECKLIST.md`)
- Epic number or URL to attach cards to
- Workspace name or ID (default: project's primary workspace)
- Mode: `preview` or `create` (default `preview`)

Always confirm mode with the user before creating anything.
If the planning document does not yet contain a task table with estimates/dependencies, use `zube-pre-groom-doc-writer` first.

## Card Body Standard

Use this exact structure for every card body:

```
## Scope
- <concrete deliverable or action>
- <concrete deliverable or action>
  - <sub-detail if needed>

## Out of Scope
- <item that might be assumed in scope but is excluded>
- <item deferred to a later task or epic>

## Acceptance Criteria
- [ ] <specific, verifiable criterion>
- [ ] <specific, verifiable criterion>

## Dependencies
- <task or condition that must be complete before this card starts>
- <Zube card link if the card already exists>

## Estimate
<N-Mh>
```

If there is truly nothing likely to be assumed in scope, `## Out of Scope` may be omitted.

## Points and Labels

Set points and labels at card creation time (not in body text).

### Points (Fibonacci mapping)

| Estimate | Points |
|----------|--------|
| 1-2h | 1 |
| 2-4h | 2 |
| 4-8h | 3 |
| 8-16h | 5 |
| 16-24h | 8 |
| 24-40h | 13 |
| 40h+ | 21 |

If an estimate spans bands (for example `8-12h`), round up to the higher band.

### Labels

Apply two labels per card:

1. Area: `Terraform`, `DAG`, `Schema`, `Infrastructure`, `Documentation`, `Research`
2. Category: `Feature`, `Spike`, `Chore`, `Bug`

If a needed label is missing, create it first with these colors:

| Label | Color |
|-------|-------|
| Terraform | `1D76DB` |
| DAG | `0075CA` |
| Schema | `006B75` |
| Infrastructure | `5319E7` |
| Documentation | `0052CC` |
| Research | `FBCA04` |
| Feature | `66BB6A` |
| Spike | `FFA726` |
| Chore | `ABB8C3` |
| Bug | `D73A4A` |

## Grooming Rules

- Scope is bullets only, each bullet is one concrete deliverable or action.
- Out of scope is explicit and references where deferred work belongs.
- Acceptance criteria are specific and independently verifiable, and use `- [ ]`.
- Dependencies describe required prerequisites, not people.
- Dependencies should use Zube `#number` card links when cards already exist.
- Estimate is always a range (`2-4h`, not `3h`; use `TBD` only when truly unknown).
- One card per task (do not bundle independent tasks).

## Workflow

### Preview mode (default)

Return each proposed card as a fenced block with `### Card: <title>` heading. Show all cards, then ask whether to proceed with creation.

Example:

```
### Card: Add endpoint-level validation for marketplace installs

## Scope
- Add request schema validation for the installs endpoint
- Add service-layer guardrails for unsupported install sources
- Add integration tests for valid and invalid payloads

## Out of Scope
- UI changes in `reach-app`
- Install analytics reporting updates

## Acceptance Criteria
- [ ] Invalid install payloads return deterministic 4xx errors with clear messages
- [ ] Supported payloads persist expected installation records
- [ ] Integration tests cover primary and negative paths

## Dependencies
- API contract for install payload approved

## Estimate
4-8h
```

### Create mode

For each task:
1. Check for existing card with same title in workspace (do not duplicate).
2. Create card with groomed body and attach to the target epic.
3. Report card number and URL.
4. For inter-card dependencies in the same batch, create card relations immediately after each card is created.
5. If creating more than 3 cards, pause after each batch of 3 for confirmation.

After creation, output:

```
| # | Title | Zube Card | Epic |
|---|-------|-----------|------|
| 1 | ... | #XXXX | #N |
```

Also update the planning doc task table with new links in the `Zube` column.

## Reach / Zube Context

- Account slug: `reach-reporting`
- Use `reach-app` planning and architecture docs as the reference source when grooming.
- Confirm project/workspace with `list_projects` and `list_workspaces` before create mode.
- Card URL: `https://zube.io/reach-reporting/<project-slug>/c/<number>`
- Epic URL: `https://zube.io/reach-reporting/<project-slug>/epics/<number>`
- Grooming standard: `reach-app/docs/planning/marketplace/MARKETPLACE-BE-GROOMING-CHECKLIST.md`

## Quality Gate Before Create

- [ ] Scope uses bullets, not prose
- [ ] Out-of-scope included (or explicitly omitted with reason)
- [ ] AC items are independently verifiable
- [ ] Estimate is a range
- [ ] Dependencies reference cards/conditions, not people
- [ ] Dependency links use Zube `#number` + URL where cards exist
- [ ] Points are set (never null)
- [ ] Two labels set (one Area, one Category)
- [ ] Card relations created for inter-card dependencies
