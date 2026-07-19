# /plan - Implementation Plan Creation

Convert a design document or requirements into a test-driven implementation plan.

## Usage

```bash
/plan [TICKET-ID|DESIGN-PATH]
```

## Skill Invocation

**IMPORTANT:** First invoke the **creating-plans** skill and follow its workflow.

## Inputs

**Design file** (preferred):
- `artifacts/tickets/{TICKET-ID}/design.md`

**Or:** User-provided requirements and context

**Accepted formats:**
- Ticket ID: `PROJ-3` → `artifacts/tickets/PROJ-3/design.md`
- Directory: `artifacts/tickets/PROJ-3/`
- Full path: `artifacts/tickets/PROJ-3/design.md`

## Outputs

- Plan document at `artifacts/tickets/{TICKET-ID}/plan.md`
- If no ticket ID: `artifacts/tickets/WORK-{NNN}-{description}/plan.md`

**Plan contains:**
- Overview and success criteria
- Ordered task breakdown with dependencies
- Acceptance criteria with validation methods
- Testing strategy
- Execution order

## Workflow Summary

1. **Determine input** - Design file or gather context through questions
2. **Parse requirements** - Extract scope, interfaces, acceptance criteria
3. **Interface review** - Get approval on proposed interfaces (if no design)
4. **Break down tasks** - Group by functional area, ensure proper granularity
5. **Order by dependencies** - Create execution order
6. **Generate plan** - Create plan document with task templates
7. **Validate** - Ensure all requirements are covered

## Error Handling

| Error | Action |
|-------|--------|
| Design file not found | List available designs, ask to select |
| Design malformed | List missing sections, ask to fix |
| No acceptance criteria | Warn, ask to proceed or fix |
| Dependencies unresolvable | List unclear deps, ask to clarify |

## Next Steps

After plan creation, run `/implement` to start implementing tasks.

## Related

- `/design` - Create design before plan
- `/implement` - Execute plan step-by-step
- `/pull-ticket` - Pull ticket before design
