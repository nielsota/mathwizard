---
name: creating-tickets
description: Defines a structured ticket by gathering requirements from the user and producing a ticket.md document. Use when the user runs /ticket, wants to define a new task, bug report, or feature request before running /design, /plan, or /implement.
---

# Creating Tickets Skill

Produces a structured `ticket.md` document by gathering requirements from the user. The output feeds directly into the `/design` → `/plan` → `/implement` workflow.

---

## Workflow

### 1. Gather Initial Context

Ask the user to describe what they want to build or fix. Use the AskQuestion tool to collect structured inputs:

- **Type**: feature, bug, chore, refactor, docs, test
- **Title**: short, action-oriented (e.g., "Add financial expert node to account planner")
- **Description**: what problem does this solve, what should be built?
- **Acceptance criteria**: how do we know it's done? (high-level, not implementation-level)

If the user already provided some context in their message, extract it rather than asking again.

### 2. Explore the Codebase (if relevant)

For features or refactors, briefly explore related files:
- Find similar patterns or modules that will be affected
- Identify integration points
- Note any constraints (data models, interfaces, config schemas)

Keep this lightweight — the goal is context awareness, not a full technical analysis (that's `/design`'s job).

### 3. Determine Ticket ID

**Priority order:**
1. User provides an ID → use it as-is (e.g., `PROJ-42`)
2. Check `artifacts/tickets/` for the highest `WORK-NNN-*` folder → increment
3. If no `artifacts/tickets/` directory or no `WORK-NNN` folders → start at `WORK-001`

### 4. Determine Output Location

- Directory: `artifacts/tickets/{TICKET-ID}/`
- Filename: `ticket.md`
- Example: `artifacts/tickets/WORK-003-add-financial-expert/ticket.md`

Create the directory if it does not exist.

### 5. Generate the Ticket Document

Use the template below. Fill in all sections — mark unknowns as `TBD` rather than omitting.

```markdown
---
created: YYYY-MM-DD
ticket_id: [TICKET-ID]
title: [Short action-oriented title]
type: [feature | bug | chore | refactor | docs | test]
status: open
---

# [TICKET-ID]: [Title]

## Description

[1–3 sentences explaining the problem or goal. Why does this work need to happen?]

## Goals

- [Goal 1]
- [Goal 2]

## Out of Scope

- [What this ticket explicitly does NOT cover]

## Acceptance Criteria

- [ ] [Criterion 1 — observable, verifiable outcome]
- [ ] [Criterion 2]
- [ ] [Criterion 3]

## Open Questions

- [Any ambiguities or decisions to resolve before/during implementation]

## Related

- Blueprint: [reference if applicable]
- Epic: [reference if applicable]
- Related tickets: [IDs if applicable]
```

### 6. Confirm and Suggest Next Step

After writing the file, tell the user:
- The path where the ticket was saved
- That they can now run `/design [TICKET-ID]` to create a technical design

---

## Best Practices

- **Acceptance criteria must be verifiable** — avoid vague language like "works correctly"
- **Keep scope tight** — one ticket, one concern; push extras to related tickets
- **Describe the "why" in Description** — the "what" comes out in `/design`
- **Don't over-engineer** — this is a ticket, not a spec; technical details go in `design.md`
