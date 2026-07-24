# /ticket - Ticket Definition

Define a structured ticket before running `/design`, `/plan`, or `/implement`.

## Usage

```bash
/ticket [optional: short description or context]
```

## Skill Invocation

**IMPORTANT:** First invoke the **creating-tickets** skill and follow its workflow.

## When to Use

**Use to define:**
- New features or enhancements
- Bug reports with clear reproduction context
- Chores, refactors, or technical debt items
- Research spikes with a defined deliverable

**Skip when:**
- The ticket / task is already well-defined elsewhere
- You're jumping straight into `/design` with a fully scoped task

## Inputs

- Optional: short description or context provided inline
- Interactive: agent asks clarifying questions if context is incomplete

## Outputs

A ticket document at `artifacts/tickets/{TICKET-ID}/ticket.md` containing:
- Ticket metadata (ID, type, status)
- Description and goals
- Out-of-scope boundaries
- Acceptance criteria (verifiable, high-level)
- Open questions

## Next Steps

After ticket creation, run:
- `/design [TICKET-ID]` — create a technical design (LLD)
- `/plan [TICKET-ID]` — skip design and go straight to implementation plan (for simple tickets)

## Related

- `/design` - Technical design after ticket is defined
- `/plan` - Implementation plan from design or ticket
- `/implement` - Execute the plan
