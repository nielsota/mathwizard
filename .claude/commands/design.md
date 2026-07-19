# /design - Ticket-Level Design Creation

Create a detailed ticket-level technical design (LLD) document.

## Usage

```bash
/design [TICKET-ID]
```

## Skill Invocation

**IMPORTANT:** First invoke the **creating-designs** skill and follow its workflow.

## When to Use

**Use for:**
- Complex tickets with multiple approaches
- Features requiring API contracts
- Unclear edge cases or error scenarios
- Work needing alignment before coding

**Skip for:**
- Simple bug fixes or typos
- Tickets with complete acceptance criteria
- Research or exploration tasks

## Inputs

- Ticket ID (from args or ticket.md)
- Ticket description & acceptance criteria
- Related codebase context

## Outputs

A design document at `artifacts/tickets/{TICKET-ID}/design.md` containing:
- Scope (in/out, assumptions)
- Functional requirements & user flows
- Edge cases & error handling
- Technical approach & patterns
- Acceptance criteria with validation methods
- Test scenarios

## Next Steps

After design creation, run `/plan` to create an implementation plan.

## Related

- `/pull-ticket` - Pull ticket before design
- `/plan` - Create implementation plan after design
- `/blueprint` - Project-level architecture (HLD)
