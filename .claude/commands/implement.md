# /implement - Plan Implementation Workflow

Execute implementation plan tasks with TDD workflow and automated validation.

## Usage

```bash
/implement [TICKET-ID|PLAN-PATH]
```

## Skill Invocation

**IMPORTANT:** First invoke the **implementing-tasks** skill and follow its workflow.

For coding standards during implementation, also invoke relevant skills:
- Python code: `y100-type-hints`, `y200-code-organization`, `y600-error-handling`, `y700-testing`
- Review code: `z100-coupling-issues`, `z200-type-safety-violations`

## Inputs

**Plan file location** (in priority order):
1. Explicit path provided by user
2. `artifacts/tickets/{TICKET-ID}/plan.md` from ticket ID
3. Ask user if plan location unclear

**Accepted formats:**
- Ticket ID: `PROJ-3` → `artifacts/tickets/PROJ-3/plan.md`
- Relative: `PROJ-3/plan.md`
- Full path: `artifacts/tickets/PROJ-3/plan.md`

## Outputs

- Implemented code and tests
- Updated plan with completion status (checkboxes marked)
- Git commit and push
- Pull request (if GitHub CLI available)

## Workflow Summary

1. **Verify environment** - Check worktree, Python venv
2. **Parse plan** - Identify completed/pending tasks
3. **Execute tasks** - Follow TDD workflow per task
4. **Validate** - Run acceptance criteria checks
5. **Update plan** - Mark tasks complete
6. **Finalize** - Commit, push, create PR

## Next Steps

After implementation complete:
- Review the created PR
- Merge when approved

## Related

- `/pull-ticket` - Pull ticket before implementation
- `/design` - Create design before plan
- `/plan` - Create plan from design
