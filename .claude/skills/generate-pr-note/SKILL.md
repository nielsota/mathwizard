---
name: generate-pr-note
description: Generate a concise PR note for sharing (e.g. in Slack/Teams). Reads the current branch's PR and commits to produce a formatted summary. Use when the user runs /generate-pr-note or asks for a PR note/summary to share.
user_invocable: true
---

# Generate PR Note

Generate a short, shareable PR note in the following exact format:

```
[Project name] Short title

[#PR_NUMBER] type: comma-separated feature keywords

One paragraph narrative. Written in plain language, describing what the PR does and why, highlighting the key changes. No bullet points — a single flowing paragraph.
```

## Process

1. **Identify the PR.** Run `gh pr view --json number,title,body,baseRefName,headRefName` on the current branch. If no PR exists, ask the user for context.

2. **Read the diff.** Run `git log --oneline <base>..HEAD` and `git diff <base>...HEAD --stat` to understand the scope.

3. **Determine the project name.** Use the repo name or a human-friendly project label if one is known (check CLAUDE.md or memory). Capitalise naturally (e.g. "DAL", "Conversational prototype").

4. **Write the note.** Follow the format exactly:
   - **Line 1:** `[Project name] Short human-readable title` — not the branch name, a real title.
   - **Line 3:** `[#NUMBER] type: keyword, keyword, keyword` — conventional commit type + a few comma-separated keywords summarising the scope.
   - **Line 5:** A single narrative paragraph. Start with context if the PR builds on another (`Builds on #N.`). Describe what the change does, not how the code is structured. Write for a teammate skimming Slack, not for a code reviewer.

5. **Output the note as a fenced code block** so the user can copy-paste it.

## Rules

- No bullet points in the paragraph — one flowing block of text.
- No Claude/AI attribution anywhere.
- Keep it concise: the paragraph should be 2–4 sentences.
- Use the PR number from GitHub, not a guess.
