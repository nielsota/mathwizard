# Agent Skills Index

This index provides metadata for all available skills. Skills are loaded on-demand to optimize context consumption through progressive disclosure.

## How Skills Work

1. **Metadata Only**: This index loads first, providing brief descriptions
2. **On-Demand Loading**: Full skill instructions load only when activated
3. **Progressive Disclosure**: Resources and templates load during execution

---

## Workflow Skills

### creating-designs

**Purpose**: Create ticket-level technical designs (LLD) for implementation tasks
**Used By**: `/design`
**Triggers**: User runs /design, asks for a design document, needs implementation details for a ticket, wants to plan technical approach before coding

**Capabilities**:
- Gather context from ticket.md or user input
- Review codebase for related patterns and code
- Generate design document with scope, requirements, edge cases
- Save design to `artifacts/tickets/{ID}/design.md`

**Reference Files**:
- `DESIGN-TEMPLATE.md` - Full design document template

---

### creating-plans

**Purpose**: Convert designs or requirements into implementation plans
**Used By**: `/plan`
**Triggers**: User runs /plan, asks for an implementation plan, needs to break down work into actionable tasks

**Capabilities**:
- Parse design documents for requirements
- Gather context through structured questions
- Break down work into tasks with acceptance criteria
- Generate plan with task dependencies and execution order
- Save plan to `artifacts/tickets/{ID}/plan.md`

**Reference Files**:
- `PLAN-TEMPLATE.md` - Full plan document structure
- `TASK-TEMPLATE.md` - Individual task format

---

### implementing-tasks

**Purpose**: Execute plan tasks with TDD workflow
**Used By**: `/implement`
**Triggers**: User runs /implement, needs to execute a plan, wants to implement tasks step-by-step with TDD

**Capabilities**:
- Identify starting point from plan checkboxes
- Setup Python environment in worktrees
- Implement tasks following TDD principles
- Verify acceptance criteria with automated validation
- Update plan with completion status
- Generate post-implementation documentation

**Reference Files**:
- `WORKTREE-SETUP.md` - Git worktree and Python environment setup
- `VALIDATION-REFERENCE.md` - Validation patterns and troubleshooting

---

### managing-git

**Purpose**: Git operations for feature development
**Used By**: `/pull-ticket`, `/pull-single-ticket`, `/implement`
**Triggers**: User needs to create branches, commit changes, push to remote, or create PRs

**Capabilities**:
- Create feature branches from base branch
- Sanitize ticket names for branch naming
- Commit with conventional commit format
- Push to remote (with upstream setup)
- Create pull requests via GitHub CLI

---

### generate-pr-note

**Purpose**: Generate a concise, shareable PR note (for Slack/Teams)
**Used By**: `/generate-pr-note`
**Triggers**: User runs /generate-pr-note, asks for a PR note or summary to share

**Capabilities**:
- Reads current branch's PR and commits from GitHub
- Produces a formatted `[Project] Title / [#N] type: keywords / paragraph` note
- Outputs as a fenced code block for easy copy-paste

---

### clementing

**Purpose**: Multi-agent refactor review — runs 8 specialized reviewer subagents in parallel (paired y/z lenses) and synthesizes a prioritized improvement list
**Used By**: `/clementing`
**Triggers**: User runs /clementing, asks for a refactor review, wants prioritized code-improvement recommendations

**Capabilities**:
- Asks the user for review scope (branch diff / specific path / whole repo)
- Spawns parallel reviewer subagents, one per lens domain
- Dedupes overlapping findings and ranks by impact × effort
- Outputs a tiered markdown report (Top Priorities / Worth Doing / Nice to Have)

**Reference Files**:
- `REVIEWER-PROMPT.md` - Template prompt for each reviewer subagent

---

## Python Coding Skills

### y100-type-hints

**Purpose**: Python type hints and type safety guidelines (Y100-Y127)
**Triggers**: Writing typed Python code, creating protocols, using generics, defining type aliases, reviewing type annotations

---

### y200-code-organization

**Purpose**: Python code organization and modularity guidelines (Y200-Y224)
**Triggers**: Structuring modules, organizing imports, applying dependency injection, designing package architecture

---

### y300-design-patterns

**Purpose**: Python design patterns guidelines (Y300-Y334)
**Triggers**: Implementing factory, strategy, observer, decorator, or other design patterns

---

### y400-functional-programming

**Purpose**: Python functional programming guidelines (Y400-Y424)
**Triggers**: Writing immutable data structures, pure functions, generators, comprehensions, functools/itertools patterns

---

### y500-documentation

**Purpose**: Python documentation and readability guidelines (Y500-Y524)
**Triggers**: Writing docstrings, choosing variable names, formatting code, adding comments

---

### y600-error-handling

**Purpose**: Python error handling guidelines (Y600-Y614)
**Triggers**: Implementing exception handling, creating custom exceptions, using context managers, designing error flows

---

### y700-testing

**Purpose**: Python testing guidelines (Y700-Y714)
**Triggers**: Writing tests, creating fixtures, using pytest parametrize, mocking dependencies, applying TDD

---

### y800-performance

**Purpose**: Python performance and optimization guidelines (Y800-Y814)
**Triggers**: Optimizing code, profiling bottlenecks, choosing generators vs lists, applying caching

---

## Python Custom Lens Skills (User-Defined)

### x100-simplicity

**Purpose**: User-defined simplicity guidelines (X100-X109) — dead code, defensive cruft, speculative generality
**Triggers**: Reviewing code for unused symbols, unreachable branches, try/except for impossible cases, re-validation of validated inputs, backwards-compat shims with no consumers, or abstractions with one implementation

---

## Python Anti-Pattern Skills

### z100-coupling-issues

**Purpose**: Python coupling anti-patterns (Z100-Z114)
**Triggers**: Reviewing code for tight coupling, circular dependencies, god objects, feature envy

---

### z200-type-safety-violations

**Purpose**: Python type safety anti-patterns (Z200-Z215)
**Triggers**: Reviewing code for overuse of Any, missing type hints, type ignore comments

---

### z300-mutability-problems

**Purpose**: Python mutability anti-patterns (Z300-Z314)
**Triggers**: Reviewing code for argument mutation, global state, mutable class attributes

---

### z400-poor-abstractions

**Purpose**: Python abstraction anti-patterns (Z400-Z409)
**Triggers**: Reviewing code for leaky abstractions, wrong abstraction levels, long parameter lists, boolean flags

---

### z500-testing-antipatterns

**Purpose**: Python testing anti-patterns (Z500-Z509)
**Triggers**: Reviewing test code for implementation coupling, brittle tests, over-mocking, missing edge cases

---

### z600-miscellaneous

**Purpose**: Miscellaneous Python anti-patterns (Z600-Z604)
**Triggers**: Reviewing code for magic numbers, deep nesting, long functions, inconsistent naming, commented-out code

---

## Skill Invocation Pattern

Commands invoke skills using this pattern:

```markdown
Invoke the **creating-designs** skill and follow the workflow.

Invoke the **managing-git** skill and apply "Create Feature Branch" to generate branch name.

Invoke the **y100-type-hints** skill and apply type safety guidelines to the implementation.
```

**Key points:**
- Use "Invoke the **{skill-name}** skill" to load and activate the skill
- Use "and apply" or "and follow" to specify the action
- Skills with reference files will load them on-demand
