---
name: implementing-tasks
description: Executes plan tasks using test-driven development workflow with validation and progress tracking. Use when the user runs /implement, needs to execute a plan, or wants to implement tasks step-by-step with TDD.
---

# Implementing Tasks Skill

Executes plan tasks using test-driven development workflow with validation and progress tracking.

---

## Pre-Implementation Setup

Before starting tasks, verify environment is ready. See [WORKTREE-SETUP.md](WORKTREE-SETUP.md) for:
- Git worktree detection
- Python virtual environment setup with `uv`
- Dependency installation
- Environment verification checklist

---

## Workflow

### 1. Identify Starting Point

**Parse plan to find current state:**

1. Read plan file completely
2. Parse task statuses from checkboxes:
   - ✅ Complete - Status shows "✅ Complete" AND all criteria checked
   - 🔄 In Progress - Status shows "🔄 In Progress" OR partially checked
   - ⬜ Not Started - Status shows "⬜ Not Started" AND no boxes checked
   - ⚠️ Blocked - Status shows "⚠️ Blocked"

3. Identify next task:
   - Follow "Execution Order" section
   - First incomplete task with complete dependencies = next task

4. Display summary:
   ```
   Plan: [PLAN-ID]
   Total Tasks: [N]
   Completed: [X] ✅
   In Progress: [Y] 🔄
   Not Started: [Z] ⬜

   Environment: [Worktree/Main] - [venv status]

   Next task: [TASK-ID] - [Task Title]
   Dependencies: [List or "None"]
   ```

### 2. Implement Task

**For each task:**

#### 2a. Start Task
1. Display: ID, title, dependencies
2. Show "What to do" steps
3. Show files to create/modify
4. Show acceptance criteria
5. Confirm: "Ready to start [TASK-ID]?"

#### 2b. Execute Implementation
1. Follow "What to do" steps sequentially
2. Create/modify files as specified
3. Write code following project conventions
4. Complete all implementation steps

#### 2c. Verify Acceptance Criteria

See [VALIDATION-REFERENCE.md](VALIDATION-REFERENCE.md) for validation patterns.

**For each criterion:**

1. Run validation command (use `uv run` for Python)
2. Display result with status
3. **If passes:** Mark checkbox ✅, continue (NO user interaction)
4. **If fails:** STOP, triage, attempt fix, escalate if needed

### 3. Update Plan File

**After task completion:**

1. Change status: `⬜ Not Started` → `✅ Complete`
2. Check all acceptance criteria boxes
3. Check all testing requirements boxes
4. Save updated plan file

### 4. Task Completion Flow

**When task is complete:**
1. Update plan file with ✅ status
2. Display: "[TASK-ID] completed successfully"
3. Show next task: "[NEXT-TASK-ID] is next"
4. Ask: "Continue with [NEXT-TASK-ID]?"

**If user wants to stop:**
- Save current progress
- Display: "Stopped at [TASK-ID]. Run /implement again to continue."

### 5. Final Verification

**When all tasks complete:**

1. Verify all tasks marked ✅
2. Verify all acceptance criteria checked
3. Populate post-implementation sections:
   - Lessons Learned
   - Key Decisions and Deviations
   - Validation Results
4. Display: "Plan [PLAN-ID] implementation complete!"

---

## Human Intervention Triggers

**Only prompt user when:**

1. Software installation required
2. Validation cannot execute (missing tools, environment issues)
3. Validation failure beyond agent capabilities
4. Technical blocker identified (architectural decision, scope change)
5. Environment setup fails

**Key Principle:** Human intervention is exception, not rule. Routine passing validations proceed automatically.

---

## Verification Checklist

**Before marking task complete:**
- [ ] All "What to do" steps completed
- [ ] All specified files created/modified
- [ ] All acceptance criteria pass
- [ ] All testing requirements met
- [ ] Code follows project conventions
- [ ] No linter errors
- [ ] Ad-hoc scripts removed

---

## Error Handling

| Error | Action |
|-------|--------|
| Plan not found | List available plans |
| Task implementation fails | Troubleshoot, ask user |
| Acceptance criteria can't verify | Document, ask user |
| Dependencies incomplete | List missing, ask preference |

For environment-specific errors, see [WORKTREE-SETUP.md](WORKTREE-SETUP.md).
