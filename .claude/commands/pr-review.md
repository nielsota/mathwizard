# PR Review Workflow

This workflow reviews a Pull Request using GitHub CLI (`gh`) and provides a comprehensive code review against project standards.

## Default Variables

The following variables should be retrieved from `AGENTS.md` (see "Default Variables" section):

- **Default Git Branch**: Target branch for PR comparison (e.g., `main`). Used to verify PR is targeting the correct branch.
- **Default Author Name**: For filtering PRs when listing (e.g., `poupon`).

---

## Prerequisites

### GitHub CLI Installation and Authentication

**GitHub CLI (`gh`) must be installed and authenticated:**

```bash
# Check if gh is installed
gh --version

# Check authentication status
gh auth status
```

**If not authenticated:**
```bash
gh auth login
```

### Important: Sandbox and Permission Requirements

**All `gh` commands MUST run with `required_permissions: ["all"]`**

Why this is required:
- GitHub CLI needs network access to communicate with GitHub API
- `gh` reads authentication tokens from system keyring (outside sandbox scope)
- Git commands need access to `.git` directory
- File operations need unrestricted filesystem access

**Agent Implementation Rule**: Every `run_terminal_cmd` that executes a `gh` command MUST include:
```python
required_permissions: ["all"]
```

**Alternative: Using GH_TOKEN Environment Variable**

If keyring authentication has issues, users can set `GH_TOKEN` environment variable:
```bash
export GH_TOKEN=ghp_yourpersonalaccesstoken
```

This allows `gh` to authenticate without interactive prompts. Generate a token at: https://github.com/settings/tokens

Required token scopes:
- `repo` - Full control of private repositories
- `read:org` - Read org and team membership
- `workflow` - Update GitHub Action workflows

---

## Step 0: Pre-Flight Authentication Check

**Action**: Verify GitHub CLI authentication before proceeding with PR review.

**Important**: This step MUST run with `required_permissions: ["all"]` to access keyring and network.

### Check Authentication Status

```bash
gh auth status
```

**Expected output** (if authenticated):
```
github.com
  ✓ Logged in to github.com account [username]
  - Active account: true
  - Git operations protocol: https
  - Token: ghp_****
  - Token scopes: 'repo', 'workflow', 'read:org'
```

### Error Handling

**If authentication fails:**

```
❌ GitHub Authentication Required

GitHub CLI is not authenticated or token has expired.

To fix:
1. Run: gh auth login
2. Follow the prompts to authenticate
3. Ensure token has required scopes: repo, workflow, read:org

Alternative: Set GH_TOKEN environment variable
  export GH_TOKEN=your_personal_access_token

Generate a token at: https://github.com/settings/tokens

Review cannot proceed without GitHub CLI authentication.
```

**Action**: Stop workflow execution. Do not proceed to Step 1 until authentication succeeds.

**If authentication succeeds**: Display confirmation and proceed to Step 1:
```
✅ GitHub CLI authenticated successfully
- Account: [username]
- Scopes: [list of scopes]

Proceeding with PR review...
```

---

## Step 1: Identify PR to Review

**Action**: Determine which PR to review.

**Options:**

### Option A: PR Number Provided
If user provides a PR number (e.g., `/pr-review 42`):
- Use the provided PR number directly
- Proceed to Step 2

### Option B: Auto-detect from Current Branch
If no PR number provided:
1. Get current branch name:
   ```bash
   git branch --show-current
   ```
2. Find PR for current branch:
   ```bash
   gh pr view --json number,title,state,baseRefName,headRefName
   ```
3. If PR found: Use that PR number
4. If no PR found: List open PRs and ask user to select

### Option C: List Open PRs
If auto-detect fails or user wants to choose:
```bash
gh pr list --state open --json number,title,author,headRefName,createdAt --limit 20
```

**Display format:**
```
Open Pull Requests:

#  | Title                              | Author    | Branch                | Created
---|------------------------------------|-----------|-----------------------|------------
42 | feat: Add user authentication      | poupon    | feature/GENXTEST-1... | 2025-12-01
38 | fix: Database connection timeout   | developer | fix/GENXTEST-5-db...  | 2025-11-30
...

Which PR would you like to review? (Enter number)
```

**Error Handling:**
- If `gh` is not installed: Display "GitHub CLI (`gh`) is not installed. Please install it: https://cli.github.com/"
- If not authenticated: Display "GitHub CLI is not authenticated. Run: `gh auth login`"
- If no open PRs: Display "No open pull requests found."

---

## Step 2: Fetch PR Details

**Action**: Retrieve comprehensive PR information using GitHub CLI.

**Commands:**

```bash
# Get PR metadata
gh pr view [PR_NUMBER] --json number,title,body,state,author,baseRefName,headRefName,additions,deletions,changedFiles,files,commits,reviewDecision,labels,milestone,createdAt,updatedAt

# Get PR diff
gh pr diff [PR_NUMBER]

# Get PR checks status
gh pr checks [PR_NUMBER]
```

**Extract and store:**
- PR number and title
- Author information
- Base branch (should match Default Git Branch from AGENTS.md)
- Head branch (feature branch)
- Files changed (list with additions/deletions per file)
- Total additions/deletions
- Commit count
- CI/CD check status
- Labels and milestone (if any)
- PR description/body

**Display PR Overview:**
```
═══════════════════════════════════════════════════════════════
📋 PR REVIEW: #[NUMBER] - [TITLE]
═══════════════════════════════════════════════════════════════

Author: [author]
Branch: [head] → [base]
State: [state]
Created: [date]
Updated: [date]

Changes: +[additions] -[deletions] across [N] files
Commits: [N]

CI Status: [✅ All checks passed / ⚠️ Checks pending / ❌ Checks failed]

Labels: [labels or "None"]
Milestone: [milestone or "None"]

───────────────────────────────────────────────────────────────
```

**Verification:**
- [ ] PR exists and is accessible
- [ ] Base branch matches expected default branch (warn if different)
- [ ] PR state is "open" (warn if merged/closed)

---

## Step 3: Review Criteria Checklist

**Action**: Apply the following review checklist to each changed file. This checklist is based on project standards defined in `AGENTS.md`. check code to confirm compliance of each item in this checklist.

### Review Categories

#### 1. Architecture & Project Structure
- [ ] Files are in correct directories per project structure
- [ ] New files follow naming conventions
- [ ] No business logic in wrong layers (e.g., UI logic in backend)
- [ ] Dependencies flow in correct direction

#### 2. Code Quality
- [ ] Code follows project style guide (ESLint+Prettier for frontend, Black+Ruff for backend)
- [ ] Functions have appropriate type hints/annotations
- [ ] Public functions have docstrings (Google-style for Python)
- [ ] No hardcoded values that should be configuration
- [ ] No commented-out code blocks
- [ ] No debug statements (console.log, print, debugger)
- [ ] Line length ≤ 120 characters

#### 3. Testing
- [ ] New functionality has corresponding tests
- [ ] Tests are in correct location (`tests/` or `__tests__/`)
- [ ] Tests follow project testing conventions (pytest, Jest)
- [ ] Test coverage appears adequate for changes
- [ ] No skipped tests without justification

#### 4. Security
- [ ] No secrets, API keys, or credentials in code
- [ ] User input is validated/sanitized
- [ ] No SQL injection vulnerabilities
- [ ] No XSS vulnerabilities (frontend)
- [ ] Proper authentication/authorization checks

#### 5. Error Handling
- [ ] Appropriate error handling for external calls
- [ ] Errors are logged appropriately
- [ ] User-facing errors are clear and helpful
- [ ] No swallowed exceptions

#### 6. Documentation
- [ ] README updated if needed
- [ ] API documentation updated if endpoints changed
- [ ] Complex logic has explanatory comments
- [ ] No typos in user-facing strings or documentation

#### 7. Git & Commits
- [ ] Commit messages follow Conventional Commits format
- [ ] Commits are logically organized
- [ ] No merge commits in feature branch (should be rebased)
- [ ] Branch name follows convention (`feature/`, `fix/`, etc.)

#### 8. Performance (if applicable)
- [ ] No obvious N+1 query issues
- [ ] Large data sets are paginated
- [ ] Expensive operations are optimized or cached
- [ ] No unnecessary re-renders (React)

---

## Step 5: File-by-File Review

**Action**: Review each changed file against the checklist from Step 4, including ticket completeness verification.

### 5.1 Get Changed Files List

```bash
gh pr view [PR_NUMBER] --json files --jq '.files[].path'
```

### 5.2 Review Process

**For each file:**

1. **Read the file diff:**
   ```bash
   gh pr diff [PR_NUMBER] -- [FILE_PATH]
   ```

2. **Read the full file** (for context):
   - Use `read_file` tool to see complete file

3. **Apply relevant checklist items** based on file type:
   - `.py` files: Python/FastAPI standards
   - `.ts/.tsx/.js/.jsx` files: React/TypeScript standards
   - `.md` files: Documentation standards
   - Config files: Security and correctness

4. **Document findings** with:
   - File path
   - Line number (if applicable)
   - Issue description
   - Severity level
   - Suggested fix

### 5.3 Severity Levels

**🔴 Critical** - Must fix before merge:
- Security vulnerabilities
- Breaking changes
- Data loss risks
- Build/test failures

**🟡 Major** - Should fix before merge:
- Architecture violations
- Missing error handling
- Missing tests for new functionality
- Type safety issues

**🟢 Minor** - Can address later:
- Code style inconsistencies
- Missing documentation
- Optimization opportunities
- Nitpicks

### 5.4 Review Output Format (Per File)

**If file passes (no issues):**
```
✅ [file-path] - Pass
```

**If file has issues:**
```
⚠️ [file-path] - [N] issue(s)

  🔴 Critical:
  - Line [N]: [Description]
    Suggestion: [How to fix]

  🟡 Major:
  - Line [N]: [Description]
    Suggestion: [How to fix]

  🟢 Minor:
  - Line [N]: [Description]
    Suggestion: [How to fix]
```

### 5.5 Collect Structured Findings for Inline Comments

**Action**: As you review each file, collect findings in a structured format for posting as inline GitHub comments.

**Structure each finding as:**
```
findings = [
  {
    "id": 1,
    "path": "backend/src/services/auth.py",
    "line": 42,
    "side": "RIGHT",
    "severity": "critical",
    "body": "🔴 **Critical**: SQL injection vulnerability\n\nUser input is directly interpolated into SQL query.\n\n**Suggestion**: Use parameterized queries instead.",
    "in_diff": true
  },
  {
    "id": 2,
    "path": "frontend/src/Login.tsx",
    "line": 87,
    "side": "RIGHT",
    "severity": "major",
    "body": "🟡 **Major**: Missing error handling for API call\n\n**Suggestion**: Wrap in try/catch and display user-friendly error.",
    "in_diff": true
  },
  ...
]
```

**Field definitions:**
- `id`: Sequential number for user reference during exclusion selection
- `path`: Full file path relative to repository root
- `line`: Line number in the file where the issue occurs
- `side`: `"RIGHT"` for additions/new code, `"LEFT"` for deletions
- `severity`: One of `"critical"`, `"major"`, or `"minor"`
- `body`: Markdown-formatted comment text including severity emoji, description, and suggestion
- `in_diff`: `true` if the line appears in the PR diff, `false` otherwise

**Important**: Only lines that appear in the PR diff can receive inline comments. For issues on unchanged lines, set `in_diff: false` - these will be included in the summary comment only.

**To verify if a line is in the diff:**
```bash
gh pr diff [PR_NUMBER] -- [FILE_PATH] | grep -n "^[+-]" | head -50
```

---

## Step 6: Generate Review Summary

**Action**: Compile all findings into a comprehensive review summary, including ticket completeness assessment.

### 6.1 Summary Format

```markdown
═══════════════════════════════════════════════════════════════
📊 PR REVIEW SUMMARY: #[NUMBER] - [TITLE]
═══════════════════════════════════════════════════════════════

## Overview

**PR**: #[number] - [title]
**Author**: [author]
**Branch**: [head] → [base]
**Files Changed**: [N]
**Changes**: +[additions] -[deletions]

## CI/CD Status

[✅ All checks passed / ⚠️ Checks pending / ❌ Checks failed]
[List any failed checks]

## Code Review Results

### Files Summary
- ✅ Files passed: [N]
- ⚠️ Files with issues: [N]

### Issues by Severity
- 🔴 Critical: [N]
- 🟡 Major: [N]
- 🟢 Minor: [N]

───────────────────────────────────────────────────────────────

## Detailed Findings

### 🔴 Critical Issues (Must Fix)

[List all critical issues with file paths and line numbers]

### 🟡 Major Issues (Should Fix)

[List all major issues with file paths and line numbers]

### 🟢 Minor Issues (Optional)

[List all minor issues with file paths and line numbers]

───────────────────────────────────────────────────────────────

## Files Reviewed

1. ✅ [file-path] - Pass
2. ⚠️ [file-path] - [N] issues (X Critical, Y Major, Z Minor)
3. ✅ [file-path] - Pass
...

───────────────────────────────────────────────────────────────

## Verdict

[Choose one based on findings:]

✅ **APPROVED** - All acceptance criteria met. No code issues. Ready to merge.

⚠️ **CHANGES REQUESTED** - [N] issue(s) should be addressed before merge.
   - [N] Critical issues, [N] Major issues

❌ **BLOCKED** - Critical issues must be resolved.
   - Critical code issues: [list]

───────────────────────────────────────────────────────────────

## Recommendations

1. [Specific recommendation based on code findings]
...

═══════════════════════════════════════════════════════════════
```

### 6.2 Confirm Inline Comments to Post

> ⚠️ **MANDATORY STEP**: You MUST present this confirmation prompt to the user and wait for their response BEFORE posting anything to GitHub. Do NOT skip this step.

**Action**: Present all findings to the user and allow them to exclude specific comments. Wait for the user's response before proceeding to Step 6.3.

**Display format:**
```
───────────────────────────────────────────────────────────────
📝 INLINE COMMENTS TO POST
───────────────────────────────────────────────────────────────

The following [N] comments will be posted as inline comments on GitHub:

  1. 🔴 backend/src/auth.py:42 - SQL injection vulnerability
  2. 🟡 backend/src/auth.py:87 - Missing error handling
  3. 🟡 frontend/src/Login.tsx:23 - Unused import
  4. 🟢 frontend/src/Login.tsx:45 - Consider using optional chaining
  5. 🟢 README.md:12 - Typo in documentation

⚠️  Comments not in diff (will appear in summary only):
  6. 🟡 backend/src/utils.py:15 - Missing type hint (line not in diff)

───────────────────────────────────────────────────────────────

Enter numbers to EXCLUDE (e.g., "3,5") or:
  - Press Enter to post all
  - Type "none" to post summary only (no inline comments)
  - Type "cancel" to abort posting to GitHub

Your choice:
```

**User input handling:**

| Input | Action |
|-------|--------|
| `Enter` (empty) | Post all comments that are `in_diff: true` |
| `3,5` or `3, 5` | Exclude comments #3 and #5 from inline posting |
| `1-3,5` | Exclude comments #1, #2, #3, and #5 |
| `none` | Post summary comment only, no inline comments |
| `cancel` | Abort - do not post anything to GitHub |

**After exclusion:**
```
✅ Posting review with [N] inline comments...

Excluded from inline posting:
  - #3: frontend/src/Login.tsx:23 - Unused import
  - #5: README.md:12 - Typo in documentation

(These will still appear in the summary comment)
```

**Note**: All findings (including excluded ones) will always be listed in the summary comment body. Exclusion only affects whether a comment appears as an inline annotation on the specific line in the PR diff.

### 6.3 Post Inline Comments to GitHub

**Action**: Use the GitHub API via `gh api` to post a review with inline comments at specific file/line positions.

**Important**: All `gh` commands MUST run with `required_permissions: ["all"]`.

**Step 1: Get repository owner and name**
```bash
gh repo view --json owner,name --jq '"\(.owner.login)/\(.name)"'
```

**Step 2: Get the HEAD commit SHA**

This is REQUIRED for inline comments to work properly:
```bash
gh pr view [PR_NUMBER] --json headRefOid --jq '.headRefOid'
```

Store this as `HEAD_COMMIT_SHA` variable.

**Step 3: Prepare comments JSON file**

Create a temporary JSON file with the comments array to avoid shell escaping issues:

```bash
# Create /tmp/pr-review-comments.json with structure:
[
  {
    "path": "backend/src/auth.py",
    "line": 42,
    "side": "RIGHT",
    "body": "🔴 **Critical**: SQL injection vulnerability\n\nUser input is directly interpolated into SQL query.\n\n**Suggestion**: Use parameterized queries."
  },
  {
    "path": "backend/src/auth.py",
    "line": 87,
    "side": "RIGHT",
    "body": "🟡 **Major**: Missing error handling\n\n**Suggestion**: Wrap in try/catch."
  }
]
```

**Step 4: Create the review payload**

Create `/tmp/pr-review-payload.json`:
```json
{
  "event": "REQUEST_CHANGES",
  "body": "[SUMMARY_COMMENT_BODY]",
  "commit_id": "[HEAD_COMMIT_SHA]",
  "comments": [
    {
      "path": "[file path]",
      "line": [line number],
      "side": "RIGHT",
      "body": "[comment body]"
    }
  ]
}
```

**Step 5: Post review with inline comments**

```bash
gh api repos/{owner}/{repo}/pulls/{PR_NUMBER}/reviews \
  --method POST \
  --input /tmp/pr-review-payload.json
```

**Step 6: Handle response and cleanup**

If successful:
```
✅ Review posted successfully!

Posted:
- 1 summary comment with full review
- [N] inline comments at specific lines

View on GitHub: https://github.com/{owner}/{repo}/pull/{PR_NUMBER}#pullrequestreview-{REVIEW_ID}
```

If failed, apply automatic fallback (see Error Handling section below).

**Step 7: Clean up temporary files**

Always clean up temporary files after posting (success or failure):
```bash
rm -f /tmp/pr-review-payload.json /tmp/pr-review-comments.json
```

**Important reminders:**
- All `gh` commands require `required_permissions: ["all"]`
- Always include `commit_id` in the payload for inline comments to work
- Implement automatic fallback to summary-only if inline comments fail
- Clean up temporary files after posting

**Event types based on verdict:**

| Verdict | Event | Description |
|---------|-------|-------------|
| ✅ APPROVED | `APPROVE` | All criteria met, no issues |
| ⚠️ CHANGES REQUESTED | `REQUEST_CHANGES` | Has critical/major issues or missing criteria |
| 📝 COMMENT | `COMMENT` | Only minor suggestions |

**Building the API call:**

1. **Get HEAD commit SHA**: `gh pr view [PR_NUMBER] --json headRefOid --jq '.headRefOid'`
2. **Filter findings**: Remove excluded IDs and findings where `in_diff: false`
3. **Build comments array**: For each remaining finding:
   ```json
   {
     "path": "[finding.path]",
     "line": [finding.line],
     "side": "[finding.side]",
     "body": "[finding.body]"
   }
   ```
4. **Build payload JSON file**: Create `/tmp/pr-review-payload.json` with:
   ```json
   {
     "event": "[APPROVE|REQUEST_CHANGES|COMMENT]",
     "body": "[full review summary with all findings]",
     "commit_id": "[HEAD_COMMIT_SHA]",
     "comments": [...]
   }
   ```
5. **Execute API call**: Post the review using `--input` flag

**Example complete workflow:**
```bash
# Step 1: Get HEAD commit SHA
COMMIT_SHA=$(gh pr view 42 --json headRefOid --jq '.headRefOid')

# Step 2: Create payload file
cat > /tmp/pr-review-payload.json << 'EOF'
{
  "event": "REQUEST_CHANGES",
  "commit_id": "abc123def456",
  "body": "⚠️ **Changes Requested**\n\n## Summary\n- Files reviewed: 5\n- Issues found: 3 (1 Critical, 2 Major)\n- Ticket: GENXTEST-42\n\n## All Findings\n\n### 🔴 Critical\n1. backend/src/auth.py:42 - SQL injection vulnerability\n\n### 🟡 Major\n2. backend/src/auth.py:87 - Missing error handling\n3. frontend/src/Login.tsx:23 - Unused import\n\nPlease address these issues before merging.",
  "comments": [
    {
      "path": "backend/src/auth.py",
      "line": 42,
      "side": "RIGHT",
      "body": "🔴 **Critical**: SQL injection vulnerability\n\nUser input is directly interpolated into SQL query.\n\n**Suggestion**: Use parameterized queries."
    },
    {
      "path": "backend/src/auth.py",
      "line": 87,
      "side": "RIGHT",
      "body": "🟡 **Major**: Missing error handling\n\n**Suggestion**: Wrap in try/catch."
    }
  ]
}
EOF

# Step 3: Post the review
gh api repos/myorg/myrepo/pulls/42/reviews \
  --method POST \
  --input /tmp/pr-review-payload.json

# Step 4: Clean up
rm /tmp/pr-review-payload.json
```

**Success output:**
```
✅ Review posted successfully!

Posted:
- 1 summary comment with full review
- [N] inline comments at specific lines

View on GitHub: https://github.com/{owner}/{repo}/pull/{PR_NUMBER}#pullrequestreview-{REVIEW_ID}
```

**If fallback was used:**
```
⚠️ Review posted as summary comment (inline comments unavailable)

Reason: [ERROR_REASON]

Posted:
- 1 comprehensive summary comment with all [N] findings
- Includes file paths, line numbers, and detailed feedback

View on GitHub: https://github.com/{owner}/{repo}/pull/{PR_NUMBER}#issuecomment-{COMMENT_ID}
```

### 6.4 Edge Cases and Limitations

**Action**: Handle special cases when posting inline comments.

#### Lines Not in Diff

GitHub only accepts inline comments on lines that appear in the PR diff (additions, deletions, or context lines). For issues found on unchanged lines:

1. **Mark as `in_diff: false`** in the findings structure
2. **Display separately** in the comment selection prompt (see 6.2)
3. **Include in summary only** - these findings will appear in the review body but not as inline comments

**Detection:**
```bash
# Get line numbers that appear in the diff for a file
gh pr diff [PR_NUMBER] -- [FILE_PATH] | grep -E "^@@" | \
  sed -E 's/.*\+([0-9]+)(,[0-9]+)?.*/\1/'
```

#### Deleted Lines (Side: LEFT)

For comments on deleted code (lines removed in the PR):
- Set `"side": "LEFT"` in the comment object
- The line number refers to the old file version

```json
{
  "path": "backend/src/old_file.py",
  "line": 50,
  "side": "LEFT",
  "body": "🟡 **Major**: This deletion removes important validation..."
}
```

#### Large Reviews (GitHub Limits)

GitHub has a soft limit of approximately 50 comments per review. For reviews with many findings:

**If more than 50 inline comments:**
```
⚠️ GitHub Comment Limit

You have [N] inline comments, but GitHub limits reviews to ~50 comments.

Options:
1. Post first 50 comments now, remaining in summary only
2. Split into multiple reviews
3. Post summary only with all findings listed

Your choice (1/2/3):
```

**Option 1 - Truncate:**
- Post first 50 comments as inline
- Add note to summary: "Note: [N] additional findings listed below could not be posted as inline comments due to GitHub limits."

**Option 2 - Split reviews:**
- Post multiple reviews, each with up to 50 comments
- First review includes summary, subsequent reviews are `COMMENT` type

#### Multi-line Comments

For issues spanning multiple lines, use `start_line` and `line` together:

```json
{
  "path": "backend/src/auth.py",
  "start_line": 42,
  "line": 48,
  "side": "RIGHT",
  "body": "🟡 **Major**: This entire block lacks error handling..."
}
```

**Note**: Both start and end lines must be in the diff for multi-line comments.

---

## Error Handling

### GitHub CLI Not Available

```
❌ GitHub CLI Error

GitHub CLI (`gh`) is not installed or not authenticated.

To install:
- macOS: brew install gh
- Windows: winget install GitHub.cli
- Linux: See https://cli.github.com/

To authenticate:
gh auth login

Review cannot proceed without GitHub CLI.
```

### PR Not Found

```
❌ PR Not Found

PR #[NUMBER] was not found or you don't have access to it.

Possible reasons:
- PR number is incorrect
- PR is in a different repository
- You don't have permission to view this PR

To list available PRs:
gh pr list --state open
```

### No Changes to Review

```
ℹ️ No Changes to Review

PR #[NUMBER] has no file changes to review.

This might be:
- An empty PR
- A PR with only merge commits
- A draft PR with no commits yet
```

### CI Checks Failed

```
⚠️ CI Checks Status

PR #[NUMBER] has failing CI checks:

❌ [check-name]: [status]
❌ [check-name]: [status]
✅ [check-name]: passed

Recommendation: Review CI failures before code review. Fix failing checks first.

Continue with code review anyway? (y/n)
```


### GitHub API Review Post Failed

```
❌ Failed to Post Review with Inline Comments

Could not post review to GitHub via API.

Error: [ERROR_MESSAGE]
```

**Automatic Diagnosis and Fallback:**

**1. Missing commit_id Error**
```
Error: "Pull request review thread line must be part of the diff"
```
**Cause**: Missing `commit_id` in API request or commit SHA is incorrect.
**Fix**: Verify HEAD commit SHA retrieval:
```bash
gh pr view [PR_NUMBER] --json headRefOid --jq '.headRefOid'
```
**Fallback**: Post summary comment only (see fallback strategy below)

**2. Invalid Line Position**
```
Error: "line must be part of the diff" or "diff hunk can't be blank"
```
**Cause**: Line numbers don't exist in the PR diff (common with new files if position is wrong).
**Fix**: Remove problematic comments from the payload and retry.
**Fallback**: Post summary with all findings as regular comment (not review)

**3. Authentication Issues**
```
Error: "Resource not accessible by personal access token" or "401 Unauthorized"
```
**Cause**: Token expired or missing required scopes.
**Fix**: Re-authenticate:
```bash
gh auth login
# Or refresh token
gh auth refresh
```
**Required scopes**: `repo`, `workflow`, `read:org`

**4. Rate Limiting**
```
Error: "API rate limit exceeded" or "403 Forbidden"
```
**Cause**: Too many API requests in short time.
**Fix**: Check rate limit status:
```bash
gh api rate_limit
```
**Fallback**: Wait until rate limit resets or post summary only

**5. Insufficient Permissions**
```
Error: "Resource not accessible" or "Must have write access"
```
**Cause**: User doesn't have write permission to repository.
**Fix**: Request write access from repository owner.
**Fallback**: Display review in chat only for user to copy/paste manually

---

**Automatic Fallback Strategy**

If inline comments fail for any reason, automatically fallback to posting a comprehensive summary comment:

```bash
# Fallback: Post summary as regular comment (not a review)
gh pr comment [PR_NUMBER] --body "[FULL_REVIEW_SUMMARY_WITH_ALL_FINDINGS]"
```

This ensures the review feedback is always delivered, even if inline positioning fails.

**Fallback workflow:**
1. Attempt to post review with inline comments
2. If error occurs, diagnose the issue
3. Remove problematic inline comments
4. Retry once with fixed payload
5. If still fails, post comprehensive summary as regular comment
6. Inform user: "✅ Review posted as summary comment (inline comments unavailable due to: [REASON])"
7. Clean up temporary files

**User notification after fallback:**
```
⚠️ Inline Comments Unavailable

Inline comments could not be posted due to: [SPECIFIC_ERROR]

Fallback applied: Posted comprehensive review as summary comment instead.

All [N] findings are included in the summary with:
- File paths and line numbers
- Severity levels
- Detailed descriptions
- Suggested fixes

View comment: [GITHUB_URL]
```

### Invalid Line Position (Specific Handling)

When specific lines are not in the diff but others are valid:

```
⚠️ Some Inline Comments Skipped

The following comments could not be posted inline (line not in diff):
- backend/src/utils.py:15 - Missing type hint
- frontend/src/App.tsx:200 - Consider refactoring

Action taken:
✅ Posted [N] valid inline comments successfully
✅ Included skipped findings in summary comment with full details

All findings are documented. Reviewers can see full details in the summary.
```

**Automatic handling:**
1. Detect which specific comments have invalid line positions
2. Remove only those comments from the inline array
3. Include all findings (including skipped ones) in the summary body
4. Post review with remaining valid inline comments
5. Notify user which comments were skipped but included in summary

### GitHub API Rate Limit

```
⚠️ GitHub API Rate Limit

You have exceeded the GitHub API rate limit.

Rate limit: [LIMIT]
Remaining: 0
Resets at: [RESET_TIME]

Options:
1. Wait until [RESET_TIME] and retry
2. Post summary only (uses fewer API calls)
3. Cancel

Your choice:
```

### Insufficient Permissions

```
❌ Insufficient Permissions

You don't have permission to post reviews on this PR.

Required permission: Write access to the repository

To resolve:
- Request write access from repository owner
- Or ask a maintainer to post the review

The review summary has been displayed above. You can copy and post it manually.
```

### Malformed Comment Body

```
⚠️ Comment Formatting Error

One or more comments contain invalid characters or formatting:

- Comment #[N]: Contains invalid JSON characters

Attempting to sanitize and retry...

[If retry fails:]
These comments have been moved to the summary comment.
```

---

## Quick Reference

### Commands

```bash
# Review current branch's PR
/pr-review

# Review specific PR by number
/pr-review 42

# List open PRs
gh pr list --state open
```

### Workflow Steps

1. **Identify PR** - Get PR number (provided, auto-detect, or list)
2. **Fetch PR Details** - Get metadata, diff, CI status via `gh` CLI
3. **Load Review Criteria** - Embedded checklist from `AGENTS.md`
4. **File-by-File Review** - Check each file, collect structured findings
5. **Generate Summary** - Compile findings and verdict
6. **Confirm Comments** - Present findings list, user selects which to exclude (MANDATORY)
7. **Post to GitHub** - Post inline comments + summary via `gh api`

### Severity Quick Guide

| Severity | Description | Action |
|----------|-------------|--------|
| 🔴 Critical | Security, breaking changes, data loss, missing acceptance criteria | Must fix |
| 🟡 Major | Architecture, missing tests/error handling, partial criteria | Should fix |
| 🟢 Minor | Style, docs, optimizations | Can defer |

### Review Verdicts

| Verdict | Condition |
|---------|-----------|
| ✅ APPROVED | No code issues found |
| ⚠️ CHANGES REQUESTED | Has critical or major issues |
| ❌ BLOCKED | Critical issues that must be resolved before merge |
| 📝 COMMENT | Only minor suggestions |

---

## Notes

- This workflow uses GitHub CLI (`gh`) for all GitHub interactions
- Review criteria are based on project standards in `AGENTS.md`
- The review is displayed directly in chat (no file generation)
- Optionally post review to GitHub after summary
- Focus on actionable feedback with specific line numbers
- Respect the author's approach while ensuring quality standards

### Inline Comments Feature

- Comments are posted at specific file/line positions in the PR diff
- Uses GitHub's review API via `gh api` for inline comment positioning
- User can exclude specific comments before posting (exclusion-based selection)
- Findings on lines not in the diff appear in summary only
- All findings are always listed in the summary comment regardless of inline posting
- GitHub limits ~50 inline comments per review; workflow handles overflow gracefully
