# Code style

- No module-level docstrings at the top of files
- Do not use `from __future__ import annotations`

# Architecture patterns

- Keep business and workflow logic in service classes, following the existing `QuestionService` and `AuthService` pattern.
- FastAPI routes should depend on services, not database clients or app-state database handles.
- Use module-level functions only for small pure helpers or compatibility wrappers. If a module owns stateful workflow behavior, make it a service class instead of growing more module-level functions.
