---
name: creating-plans
description: Converts designs or requirements into test-driven implementation plans with ordered tasks and acceptance criteria. Use when the user runs /plan, asks for an implementation plan, or needs to break down work into actionable tasks.
---

# Creating Plans Skill

Converts designs or requirements into test-driven implementation plans with ordered tasks and acceptance criteria.

---

## Workflow

### 1. Determine Input Source

**Ask user:**
- "Do you have a design file to create a plan from, or would you like me to create a plan based on your description?"

**If design file provided:** Parse the design (Step 2)
**If no design file:** Gather context through questions (Step 3)

### 2. Parse Design File

**Read and extract:**

1. **Metadata from frontmatter:**
   - `id` - Design ID (may be ticket ID or UUID)
   - `created`, `author`, `related_tickets`

2. **Key sections:**
   - Context / Purpose - Overall goal
   - Scope - What's included/excluded
   - Functional Behavior - What needs to be built
   - Technical Details - API endpoints, data models, components
   - Acceptance Criteria - With validation methods
   - Open Questions / Risks

3. **CRITICAL - Extract interface details:**
   - Code examples (classes, functions, APIs, models)
   - Configuration structures, defaults, validation rules
   - API endpoint specs (paths, methods, schemas)
   - Database model definitions

### 3. Gather Context Through Questions

**If no design file, ask systematically:**

| Question Set | Questions |
|--------------|-----------|
| Purpose & Goals | Primary goal? End user? Success criteria? |
| Scope & Boundaries | What's included? Out of scope? Dependencies? |
| Technical Requirements | Main components? Technologies? Integrations? |
| Functional Behavior | User flows? Inputs/outputs? Error cases? |
| Testing & Quality | Acceptance criteria? Test types? Performance? |
| Dependencies | What must be done first? What depends on this? |

**Summarize and confirm understanding before proceeding.**

### 4. Determine Plan ID

**If design file provided:**
- Plan ID MUST match design ID exactly
- Example: Design `id: PROJ-3` → Plan ID: `PROJ-3`

**If no design file:**
1. If user provides an ID, use it
2. Otherwise, use auto-increment `WORK-NNN` format

### 5. Interface Review (No Design File Only)

**CRITICAL: Before creating tasks, get approval on interfaces:**

Present for approval:
```
**INTERFACE REVIEW REQUIRED**: Before proceeding, I need approval on:

1. **[Interface Name]**: [Description]
   - Location: [Where created]
   - Key components: [List]
   - [Show complete definition]
```

**Wait for user confirmation before proceeding.**

### 6. Break Down into Tasks

**Task identification strategy:**

1. **Group by functional area:** Setup, Implementation (by feature), Testing, Documentation

2. **Task granularity:**
   - Too granular: "Create User model class"
   - Good: "Implement User model with validation and unit tests"
   - Too broad: "Build entire authentication system"

3. **Each task should:** Have clear single purpose, be independently testable, have explicit acceptance criteria

### 7. Order Tasks by Dependencies

**Common patterns:**
- Setup → Dependencies → Application startup
- Database models → Migrations → API endpoints
- Core functionality → Tests → Documentation

**Ensure:** No circular dependencies, related tasks grouped, execution order listed

### 8. Generate Plan Document

Use templates from:
- [PLAN-TEMPLATE.md](PLAN-TEMPLATE.md) - Full plan structure
- [TASK-TEMPLATE.md](TASK-TEMPLATE.md) - Individual task format

---

## Output Location

**Save plan to:**
- With ticket ID: `artifacts/tickets/{TICKET-ID}/plan.md`
- Without ticket ID: `artifacts/tickets/WORK-{NNN}-{description}/plan.md`

**Plan should be in same directory as design if design exists.**

---

## Validation Checklist

Before finalizing plan, verify:

- [ ] All acceptance criteria from design are covered
- [ ] All functional requirements have tasks
- [ ] All technical details are addressed
- [ ] Interface details included in Implementation Details
- [ ] Dependencies correctly mapped
- [ ] Test coverage is comprehensive
