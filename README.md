# Repository Base Template — JobHunter07

Purpose
-------
This repository is a reusable "base template" for JobHunter07 organization projects. It centralizes the engineering principles, contributor guidance, and lightweight automation so new repositories can inherit a consistent rule set without copy/paste.

What this provides (CLI-first)
-------------------
- `.github/copilot-instructions.md` — canonical rules and guidance (The Standard) applied to all languages and project types.
- `.github/PULL_REQUEST_TEMPLATE.md` — educational PR checklist for reviewers.
- `.github/prompts/pre_pr_check.prompt.md` — Copilot Chat prompt to run an interactive pre-PR checklist with an author.
- `.github/copilot-instructions.md` — canonical rules and guidance (The Standard) applied to all languages and project types.
- `.github/PULL_REQUEST_TEMPLATE.md` — educational PR checklist for reviewers.
- `.github/prompts/pre_pr_check.prompt.md` — Copilot Chat prompt to run an interactive pre-PR checklist with an author.
- `.github/scripts/pre_pr_interactive.py` — interactive local CLI script that gathers changed files and walks the author through the checklist.
- `pre-pr-check` / `pre-pr-check.ps1` — cross-platform wrappers and a VS Code task to run the interactive checklist quickly.

Quick usage
-----------

Interactive (recommended before opening a PR)
 Use the Copilot Chat prompt at `.github/prompts/pre_pr_check.prompt.md` to walk an author through the checklist in the editor.

Local automated interactive checklist (no pasting required)
- Run the local helper to auto-gather changed files and run the interactive checklist:

```bash
python .github/scripts/pre_pr_interactive.py
```

The script detects changed files against the repository default branch, extracts a suggested PR title/description from the latest commit, and interactively asks confirmations for subjective checklist items. It saves the final checklist to `.github/pre_pr_check_result.md` and attempts to copy it to the clipboard on Windows.

Optional: create the PR automatically
- If you have the GitHub CLI (`gh`) installed and authenticated, the interactive script will offer to create the PR for you using the generated checklist as the body. Confirm when prompted to create the PR.

Run with one command
- Cross-platform wrappers are provided at the repository root so you can run the interactive checklist with a single command:

Windows PowerShell:

```powershell
./pre-pr-check.ps1
```

Unix / macOS:

```bash
./pre-pr-check
```

VS Code Task
- You can run the `pre-pr-check` task from the Command Palette (`Tasks: Run Task`) or bind it to a keyboard shortcut. The task runs the appropriate wrapper for your OS.

Behavior
- The interactive script detects changed files against your repository base branch, suggests a PR title/description from the latest commit, prompts to confirm subjective checklist items, saves the checklist to `.github/pre_pr_check_result.md`, copies it to the clipboard on Windows when possible, and can optionally create the PR using the `gh` CLI.


Customizing this template
-------------------------
- To change the rules, edit `.github/copilot-instructions.md` (this file is the canonical source for the template).
- To add or relax exceptions, document them in the repo README and update the "Shared-library exceptions" section in `.github/copilot-instructions.md`.

How to use this when creating a new repo from the template
---------------------------------------------------------
1. Copy or reference `.github/copilot-instructions.md` into the new repo's `.github/` folder.
2. Keep the PR template and workflow in the new repo (or adapt them) so reviewers see the checklist and the automated checks run.

Contributing
------------
Suggestions and improvements to this template are welcome. Please open an issue or PR that explains the rationale and migration path for changes to the base rules.
