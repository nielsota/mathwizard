# Task Template

Use this template for each task in an implementation plan.

```markdown
### Task [N]: [Task Title]

**ID**: [PLAN-ID]-T[N]
**Dependencies**: [List of task IDs or "None"]
**Status**: ⬜ Not Started

**What to do**:
1. [Step 1 - specific action]
2. [Step 2 - specific action]
3. [Step 3 - specific action]

**Implementation Details**:
[CRITICAL: Include interface specs when creating structures]

Example for a class:
```python
class Settings(BaseSettings):
    """Application settings."""
    environment: str = Field(default="dev")
    debug: bool = Field(default=False)
```

Example for an API endpoint:
```python
# Request schema
class UserCreate(BaseModel):
    email: str = Field(..., min_length=5)
    password: str = Field(..., min_length=8)

# Response schema
class UserResponse(BaseModel):
    id: int
    email: str
    created_at: datetime

# Endpoint
@router.post("/users", response_model=UserResponse)
async def create_user(data: UserCreate) -> UserResponse:
    ...
```

**Files to create/modify**:
- `path/to/file.py`: [What to implement]
- `path/to/test_file.py`: [What tests to add]

**Acceptance Criteria**:
- [ ] [Criterion 1]
  - **Validation Method**: [How to validate]
  - **Expected Result**: [Expected outcome]
- [ ] [Criterion 2]
  - **Validation Method**: [How to validate]
  - **Expected Result**: [Expected outcome]

**Validation Checklist**:
- [ ] [Validation type 1]
- [ ] [Validation type 2]

**Testing Requirements**:
- [ ] Unit tests written and passing
- [ ] Integration tests (if applicable)
- [ ] All acceptance criteria validated

**Notes**:
[Additional context or gotchas]
```

## Status Indicators

| Status | Indicator | Meaning |
|--------|-----------|---------|
| Complete | ✅ | All criteria pass |
| In Progress | 🔄 | Currently working |
| Not Started | ⬜ | Waiting or not begun |
| Blocked | ⚠️ | Cannot proceed |
