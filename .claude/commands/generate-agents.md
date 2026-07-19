# Generate Agent Context File

## Description

Generates a customized `AGENTS.md` file from `AGENTS-template.md` by extracting parameter values and replacing all placeholders throughout the template.

## Instructions

This command should:

1. **Prompt user with instructions for filling out the template**
   - Display this informative message to the user:
     ```
     📝 Before generating AGENTS.md, please ensure the following parameters are filled in AGENTS-template.md:

     Critical Parameters that need to be filled in:
     - PROJECT_NAME: Your project name (e.g., "retail-data-demo")
     - TEAM_NAME: Your team name (e.g., "Engineering")
     - AUTHOR_NAME: Your name
     - PROJECT_DESCRIPTION: Brief description of your project
     - PROJECT_PURPOSE: The main purpose or business objective
     - REPO_URL: Your repository URL

     Instructions:
     1. Open AGENTS-template.md
     2. Find the PARAMETERS SECTION (between <!-- PARAMETERS SECTION and END PARAMETERS -->)
     3. Replace each placeholder value with your actual project information
     4. Save the file

     Example:
     Change: PROJECT_NAME: YOUR_PROJECT_NAME (ex : test-genx-workflow)
     To:     PROJECT_NAME: retail-data-demo

     Would you like help filling out the template? (Type "yes" for assistance, or "no" to proceed)
     ```
   - Wait for user response:
     - If user wants help ("yes"/"y"): Ask questions to gather values for each parameter, then offer to update `AGENTS-template.md` with the values
     - If user doesn't need help ("no"/"n") or after helping: Ask "Ready to proceed with generating AGENTS.md? (Type 'yes' to continue)"
     - If user says "yes" to proceed: Continue to step 2
     - If user says "no" or "cancel": Abort with message: "Generation cancelled. Please edit AGENTS-template.md when ready."

2. **Read the template file**
   - Read the `AGENTS-template.md` file
   - Verify the file exists and is readable

3. **Extract parameters**
   - Extract all parameter values from the PARAMETERS section (between `<!-- PARAMETERS SECTION` and `END PARAMETERS -->`)
   - Parse the parameters as key-value pairs (format: `KEY: value`)

4. **Replace placeholders**
   - Replace all placeholders in the template with actual values:
   - `[Project Name]` → `PROJECT_NAME` value
   - `[Your Project Name]` → `PROJECT_NAME` value
   - `[Brief description...]` → `PROJECT_DESCRIPTION` value
   - `[Your Team Name]` → `TEAM_NAME` value
   - `[Your Name]` → `AUTHOR_NAME` value
   - `[main/master/develop]` or `[main]` → `DEFAULT_BRANCH` value
   - `[FRONTEND_PORT]` → `FRONTEND_PORT` value
   - `[BACKEND_PORT]` → `BACKEND_PORT` value
   - And all other parameter placeholders throughout the document

5. **Remove PARAMETERS section**
   - Remove the entire PARAMETERS section from the output (from `<!-- PARAMETERS SECTION` through `END PARAMETERS -->`)

6. **Update metadata**
   - Update the "Last Updated" date at the bottom to today's date (YYYY-MM-DD format)

7. **Write output file**
   - Write the clean, customized content to `AGENTS.md`

## Processing Logic

### Parameter Extraction

Parse the PARAMETERS section and build a mapping of:
- `PROJECT_NAME` → actual value from template
- `PROJECT_DESCRIPTION` → actual value from template
- etc.

### Placeholder Replacement Strategy

For each parameter, replace ALL occurrences of related placeholders:

1. **PROJECT_NAME**: Replace `[Project Name]`, `[Your Project Name]`
2. **PROJECT_DESCRIPTION**: Replace `[Brief description of your project, its goals, and what problems it solves]`, `[Brief description...]`
3. **PROJECT_PURPOSE**: Replace `[The main purpose or business objective of this project]`
4. **TEAM_NAME**: Replace `[Your Team Name]`, `[Your Team]`
5. **INITIATIVE**: Replace `[Related initiative, program, or strategic objective]`
6. **ARCHITECTURE**: Replace `[High-level architecture overview - e.g., "React frontend ↔ Node.js/Express backend ↔ PostgreSQL database"]`
7. **BACKEND_TECH**: Replace `[e.g., Python/FastAPI, Node.js/Express, Java/Spring Boot, etc.]` in Backend line
8. **FRONTEND_TECH**: Replace `[e.g., React, Vue.js, Next.js, Angular, etc.]` in Frontend line
9. **DATABASE**: Replace `[e.g., PostgreSQL, MySQL, MongoDB, SQLite]`
10. **TESTING_FRAMEWORK**: Replace `[e.g., pytest, Jest, JUnit, etc.]`
11. **CODE_QUALITY_TOOLS**: Replace `[e.g., ESLint, Prettier, ruff, black, etc.]`
12. **VERSION_CONTROL**: Replace `[GitHub/GitLab/Bitbucket]`
13. **PROJECT_MGMT_TOOL**: Replace `[e.g., Linear, Azure DevOps, GitHub Issues, etc.]`
14. **FRONTEND_PORT**: Replace `[FRONTEND_PORT]`
15. **BACKEND_PORT**: Replace `[BACKEND_PORT]`
16. **DATABASE_PORT**: Replace `[DATABASE_PORT]` or remove if N/A
17. **PACKAGE_MANAGER**: Replace `[Key package managers or runtime dependencies - e.g., npm, pip, Maven, etc.]`, `[Specify your package manager - e.g., npm, pip, uv, yarn, Maven, Gradle]`
18. **AUTHOR_NAME**: Replace `[Your Name]`
19. **DEFAULT_BRANCH**: Replace `[main]`, `[main/master/develop]`
24. **TASK_RUNNER**: Replace `[e.g., \`make\`, npm scripts, Gradle tasks, custom scripts]`
25. **CODE_STYLE**: Replace `[e.g., PEP 8, Airbnb style guide, Google Java Style]`
26. **LINE_LENGTH**: Replace `[e.g., 80, 100, 120 characters]`
27. **COVERAGE_TARGET**: Replace `>[percentage]%` with `>${COVERAGE_TARGET}%`
28. **PRE_COMMIT_HOOKS**: Replace `[Enabled/Disabled - if enabled, describe setup]`
29. **PRE_COMMIT_INSTALL**: Replace `[install command]`, `[make install-hooks / pre-commit install]`
30. **TESTING_APPROACH**: Replace `[e.g., Test-Driven Development (TDD), Behavior-Driven Development (BDD)]`
31. **BACKEND_INSTALL_CMD**: Replace `[Install dependencies - e.g., npm install, pip install -r requirements.txt, uv sync]`
32. **BACKEND_START_CMD**: Replace `[Start server - e.g., npm start, uvicorn app:app --reload, ./gradlew bootRun]`
33. **FRONTEND_INSTALL_CMD**: Replace `[Install dependencies - e.g., npm install, yarn install]`
34. **FRONTEND_START_CMD**: Replace `[Start dev server - e.g., npm run dev, yarn start]`
35. **BACKEND_TEST_CMD**: Replace `[Command to run backend tests - e.g., \`npm test\`, \`pytest\`, \`./gradlew test\`]`
36. **FRONTEND_TEST_CMD**: Replace `[Command to run frontend tests - e.g., \`npm test\`, \`yarn test\`]`
37. **REPO_URL**: Replace `https://[github.com|gitlab.com|bitbucket.org]/[YOUR_ORG]/[your-repo]`

### Additional Replacements

Also handle these generic placeholders that appear in multiple contexts:
- `[e.g., ...]` patterns that match the parameter type
- `[Language runtime and version - e.g., Python 3.12+, Node.js 18+, Java 17+]` - construct from BACKEND_TECH/FRONTEND_TECH
- `[Date]` at the bottom → Today's date in YYYY-MM-DD format
- `[Active Development / Maintenance / Planning]` → "Active Development" (default)

### Smart Replacements

Apply intelligent handling for special cases:

1. **"N/A" values**: If a parameter is "N/A", replace appropriately:
   - Frontend technology: Use "N/A (API-only backend project)" or similar
   - Commands: Remove or simplify the section

2. **"tbd" or "TBD" values**: If a parameter is "to be determined":
   - TASK_RUNNER: Replace with "To be determined" and simplify commands section
   - CODE_STYLE: Replace with "Standard best practices" or "To be determined"

3. **Empty or blank values**: If a parameter is empty:
   - CODE_STYLE: Use "Standard best practices"
   - Other fields: Use "TBD" or leave as generic placeholder

4. **Duplicate FRONTEND_TECH/BACKEND_TECH**: If frontend and backend have the same value:
   - This likely means no separate frontend, so set Frontend to "N/A (API-only backend project)"

5. **COVERAGE_TARGET format**: Handle various formats:
   - "Y70" → ">70%"
   - "70" → ">70%"
   - "80" → ">80%"
   - Extract the number and format consistently

## Parameter Validation

Before generating, check for common issues and apply fixes:

1. **Duplicate Frontend/Backend**: If FRONTEND_TECH equals BACKEND_TECH exactly, assume no separate frontend
2. **Empty critical fields**: Warn if PROJECT_NAME or TEAM_NAME are still placeholder values
3. **Format issues**:
   - Clean up COVERAGE_TARGET (e.g., "Y70" → "70")
   - Normalize "tbd", "TBD", "to be determined" to consistent format

## Output

Create `AGENTS.md` with:
- No PARAMETERS section
- All placeholders replaced with actual values
- Smart replacements applied for edge cases
- Clean, production-ready agent context file
- Updated "Last Updated" date

## Success Message

After generation, inform the user:
```
✅ Successfully generated AGENTS.md from AGENTS-template.md
- Extracted [X] parameters
- Replaced [Y] placeholders
- Applied [Z] smart replacements for edge cases
- File ready to use: AGENTS.md
```

If any smart replacements were applied (duplicate frontend/backend, tbd values, etc.), mention them:
```
Note: Applied smart replacements:
- [List any automatic fixes made]
```

## Error Handling

If AGENTS-template.md is not found or PARAMETERS section is missing/malformed:
- Display clear error message
- Explain what's needed
- Do not create/overwrite AGENTS.md
