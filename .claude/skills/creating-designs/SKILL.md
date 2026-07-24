---
name: creating-designs
description: Creates ticket-level technical designs (LLD) for implementation tasks. Use when the user runs /design, asks for a design document, needs implementation details for a ticket, or wants to plan technical approach before coding.
---

# Creating Designs Skill

Creates ticket-level technical designs (Low-Level Designs) for implementation tasks.

## Design vs Blueprint

- **Blueprint (HLD)**: Project-level architecture covering multiple epics (via `/blueprint`)
- **Design (LLD)**: Ticket-level implementation details for a single task (via `/design`)

## When to Create a Design

**Create when:**
- Ticket is complex or has ambiguities
- Multiple edge cases need to be defined
- API contracts need to be specified
- Implementation approach needs agreement

**Skip for:**
- Trivial tickets (simple bug fixes, typos)
- Tickets with complete acceptance criteria already
- Exploratory or research tickets

---

## Workflow

### 1. Gather Ticket Context

**If ticket.md exists:**
- Read `ticket.md` in the current directory
- Extract ticket ID, title, description, acceptance criteria
- Use ticket ID as design ID

**If no ticket.md:**
- Ask user for ticket ID and basic context
- Gather additional requirements through questions

### 2. Review Existing Context

**Search codebase for:**
- Related code files that will be modified
- Similar implementations or patterns
- Existing models/schemas related to this ticket
- Related API endpoints or components
- Test files for similar features

**Review:**
- Current implementation state
- Existing patterns and conventions
- Integration points
- Data models that will be affected
- Error handling patterns
- Validation tools (CI, linters, pre-commit hooks)

### 3. Ask for Additional Context

**Present findings and ask:**
- "I found [list of relevant files/context]. Is there anything else I should consider?"
- "Are there specific edge cases or error scenarios you want me to cover?"
- "Do you have design docs, mockups, or other references?"
- "Are there performance or security requirements specific to this ticket?"
- "What testing approach should be taken?"

### 4. Determine Design ID

**Priority order:**
1. **ticket.md** - If contains a ticket/work ID → use it (e.g., `PROJ-4`)
2. **User-provided** - If user provides a work ID → use it
3. **Generate WORK-NNN** - Check `artifacts/tickets/` for highest `WORK-NNN-*`, increment

### 5. Determine Output Location

**With ticket ID (e.g., `PROJ-3`):**
- Directory: `artifacts/tickets/PROJ-3/`
- Filename: `design.md`

**Without ticket ID:**
- Directory: `artifacts/tickets/WORK-NNN-{short-description}/`
- Filename: `design.md`
- Short description: kebab-case, 2-4 words (e.g., `auth-refactor`, `docker-setup`)

### 6. Generate Design Document

Use template from [DESIGN-TEMPLATE.md](DESIGN-TEMPLATE.md).

---

## Best Practices

1. **Be Specific**: Focus on this one ticket, not general architecture
2. **Testable Criteria**: Every acceptance criterion should be verifiable
3. **Complete Edge Cases**: Think through all scenarios
4. **Clear Errors**: Define exact error messages and handling
5. **Reference Existing Code**: Point to patterns and examples in codebase
6. **Security First**: Consider security implications early

---

## Template Reference

See [DESIGN-TEMPLATE.md](DESIGN-TEMPLATE.md) for the full design document template with all sections.
