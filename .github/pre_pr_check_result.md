<<<<<<< Updated upstream
# PR Checklist for: feat: add interactive pre-PR checklist script

- Introduced a new Python script (.github/scripts/pre_pr_interactive.py) that gathers changed files and guides the author through a checklist before creating a PR.
- The script detects the base branch, gathers changed files, and prompts for PR title and description.
- It checks for common issues and generates a checklist that is saved to .github/pre_pr_check_result.md and optionally copied to the clipboard.
- Added a GitHub Action workflow (.github/workflows/pr-checklist.yml) to run the checklist validator on PR events.
- Created VS Code tasks (.vscode/tasks.json) for running the pre-PR check easily.
- Updated README.md with usage instructions for the new features.
- Added OpenSpec skills for applying, archiving, exploring, and proposing changes, enhancing the workflow for managing changes.
- Configured OpenSpec with a new config file (openspec/config.yaml) to define project context and artifact rules.
- Created shell and PowerShell scripts (pre-pr-check and pre-pr-check.ps1) for cross-platform execution of the interactive checklist.
=======
# PR Checklist for: fix: update PR checklist title and correct Airplane Mode requirement status

update PR checklist title and correct Airplane Mode requirement status
>>>>>>> Stashed changes

- [x] I verified this change follows the People-First & Simplicity principle (clear, maintainable code).
- [x] The change follows Screaming Architecture (feature/vertical-slice organization) where applicable.
- [x] No new generic `utils/`, `helpers/`, or `services/` were added at the repository root without documented justification.
<<<<<<< Updated upstream
- [x] Data/config was added under `src/data/` (or `data/` with justification) and exported as a single well-typed constant when applicable.
- [x] The change preserves or documents Airplane Mode requirements (local mocks, no runtime external deps for dev/tests).
- [ ] Any shared-library or cross-feature exception is documented in the repo README or exceptions file with rationale.
- [ ] The author included tests or a clear testing note, and the change leaves the repo in a releasable state (Last Day).
- [ ] Performance optimizations are documented and justified with benchmarks if they reduce readability.
=======
- [ ] Data/config was added under `src/data/` (or `data/` with justification) and exported as a single well-typed constant when applicable. (N/A)
- [ ] The change preserves or documents Airplane Mode requirements (local mocks, no runtime external deps for dev/tests). (N/A)
- [ ] Any shared-library or cross-feature exception is documented in the repo README or exceptions file with rationale. (N/A)
- [ ] The author included tests or a clear testing note, and the change leaves the repo in a releasable state (Last Day). (N/A)
- [ ] Performance optimizations are documented and justified with benchmarks if they reduce readability. (N/A)
>>>>>>> Stashed changes
