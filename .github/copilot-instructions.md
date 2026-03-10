Agent Instructions — Project Standard

Purpose
-------
Provide a concise, persistent set of rules and expectations for AI agents and contributors working in this repository. These instructions are derived from the project's "The Standard" principles and the current conversation context.

Scope
-----
Apply these rules to authoring code, components, architecture proposals, and agent-produced edits across the repository unless a file-level exception is explicitly documented.

Key Rules (enforced as guidance)
--------------------------------
- People-first & Simplicity: prioritize human understanding and maintainability over cleverness.
- Single-level inheritance: avoid inheritance deeper than one level except where frameworks require it.
- No horizontal/vertical entanglement: do NOT create global `utils/`, `helpers/`, `services/`, or local base-component chains that spread dependencies.
- Autonomous components: each feature/component must include its own validation, error handling, and utilities.
- Rewritability: design code so it can be rewritten easily; avoid hidden runtime injections and undocumented prerequisites.
- Mono-micro (modular monolith): organize by vertical feature slices; features should be extractable later.
- Level 0 (junior-friendly): prefer explicit, descriptive names and minimal unjustified abstractions.
- Open code & documentation: prefer shareable, documented patterns and public-ready documentation where possible.
- Airplane Mode: development must run offline (mock data, no external service runtime dependencies for dev and tests).
- No Toasters (no forced tooling): set linters/formatters but treat violations as conversational/code-review guidance, not hard CI blockers.
- Readability over optimization: avoid premature optimization; optimize only when measured and documented.
- Last Day (daily completeness): leave codebase in a releasable state at day's end; use feature flags or separate branches for incomplete work.
- Screaming Architecture: top-level folders must reflect business domains and features (vertical-slice architecture).
- Data Configuration Management: put configuration and static data in `src/data/` (or `data/` at repo root) as strongly-typed TypeScript modules that export a single constant.

How agents should apply these rules
----------------------------------
- When producing code, prefer explicit implementations over shortcuts; avoid creating new shared/global helper folders.
- When refactoring, ensure the change improves understandability and keeps features autonomous.
- Prefer small, self-contained diffs with tests and documentation. If adding a rule that affects CI, propose it in a PR description and include a rationale for reviewers.
- For typed projects, author data files as `.ts` modules exporting a single typed constant.
- Always include local mocks for external integrations and document how to run the system offline.

Examples (prompts to test the instruction)
-----------------------------------------
- "Create a vertical-slice `jobs` feature including UI, `src/data/jobs.ts` typed data file, unit tests, and local mock responses. Keep inheritance to one level and avoid adding any `utils/` at the root." 
- "Refactor the `auth` feature to remove cross-feature state sharing—make it self-contained and provide a migration note." 

Resolved Decisions
------------------
- Scope: These rules apply to all languages and every folder in repositories created from this Repository Base Template. This file is the canonical, centralized guidance for new repos; projects may add documented, repo-level exceptions when strictly necessary.
- Data file location: Prefer `src/data/` as the canonical location. For projects that do not use a `src/` layout, `data/` at the repo root is acceptable. Data should be provided as a single, well-documented module per data file; for typed projects export a single typed constant.
- Shared-library exceptions: Shared libraries (for example, framework base components or infra packages) are allowed only with explicit justification and documentation recorded in the repo's README or an exceptions file. Avoid creating generic `utils/`, `helpers/`, or `services/` at the root unless a documented, reviewed rationale exists.

Next steps (recommended)
------------------------
1. Review and answer the Ambiguities & Questions above.
2. If approved, add automated checklist items to PR templates that remind reviewers of the above principles (education-first, not auto-blocking enforcement).
3. Optionally: create small example feature (vertical-slice) that demonstrates compliance.

Maintainer note
---------------
These instructions are deliberately guidance-first. If the team wants stricter enforcement (CI gates), add that as a separate, documented policy and include migration guidance.

Repository Base Template usage
-----------------------------
This document is the single-source-of-truth for base rules. When scaffolding a new repo from this template, reference or copy this file into the new repository's `.github/` folder and update the "Shared-library exceptions" section for that repo only. Keep project-specific deviations documented and approved.

Example Prompts & Next Customizations
------------------------------------
Example prompts to see these rules in action:

- "Create a vertical-slice `jobs` feature with `src/data/jobs.ts`, local mocks, and unit tests following the Repository Base Template guidance."
- "Refactor `auth` to remove cross-feature shared state, document the migration, and add tests verifying isolation."
- "Add a small offline mock server and test harness for the `payments` feature that runs without network access."
- "Propose an exceptions file for a shared UI library and document the justification in the repo README."

Recommended next customizations (optional):

- Add an ISSUE_TEMPLATE and CONTRIBUTING.md that summarize these principles for contributors.
- Add a `docs/` snippet or badges that link to `.github/copilot-instructions.md` so reviewers see the guidance quickly.
- Add a small generator or repo-creation script that copies this file into new repositories automatically.
- Create a `docs/exceptions.md` template in the repo root for documenting allowed shared-library exceptions.
- Consider a non-blocking GitHub Action that comments a checklist on PRs (educational only) rather than failing the build.

Agent Instructions — Project Standard

Purpose
-------
Provide a concise, persistent set of rules and expectations for AI agents and contributors working in this repository. These instructions are derived from the project's "The Standard" principles and the current conversation context.

Scope
-----
Apply these rules to authoring code, components, architecture proposals, and agent-produced edits across the repository unless a file-level exception is explicitly documented.

Key Rules (enforced as guidance)
--------------------------------
- People-first & Simplicity: prioritize human understanding and maintainability over cleverness.
- Single-level inheritance: avoid inheritance deeper than one level except where frameworks require it.
- No horizontal/vertical entanglement: do NOT create global `utils/`, `helpers/`, `services/`, or local base-component chains that spread dependencies.
- Autonomous components: each feature/component must include its own validation, error handling, and utilities.
- Rewritability: design code so it can be rewritten easily; avoid hidden runtime injections and undocumented prerequisites.
- Mono-micro (modular monolith): organize by vertical feature slices; features should be extractable later.
- Level 0 (junior-friendly): prefer explicit, descriptive names and minimal unjustified abstractions.
- Open code & documentation: prefer shareable, documented patterns and public-ready documentation where possible.
- Airplane Mode: development must run offline (mock data, no external service runtime dependencies for dev and tests).
- No Toasters (no forced tooling): set linters/formatters but treat violations as conversational/code-review guidance, not hard CI blockers.
- Readability over optimization: avoid premature optimization; optimize only when measured and documented.
- Last Day (daily completeness): leave codebase in a releasable state at day's end; use feature flags or separate branches for incomplete work.
- Screaming Architecture: top-level folders must reflect business domains and features (vertical-slice architecture).
- Data Configuration Management: put configuration and static data in `src/data/` (or `data/` at repo root) as strongly-typed TypeScript modules that export a single constant.

How agents should apply these rules
----------------------------------
- When producing code, prefer explicit implementations over shortcuts; avoid creating new shared/global helper folders.
- When refactoring, ensure the change improves understandability and keeps features autonomous.
- Prefer small, self-contained diffs with tests and documentation. If adding a rule that affects CI, propose it in a PR description and include a rationale for reviewers.
- For typed projects, author data files as `.ts` modules exporting a single typed constant.
- Always include local mocks for external integrations and document how to run the system offline.

Examples (prompts to test the instruction)
-----------------------------------------
- "Create a vertical-slice `jobs` feature including UI, `src/data/jobs.ts` typed data file, unit tests, and local mock responses. Keep inheritance to one level and avoid adding any `utils/` at the root." 
- "Refactor the `auth` feature to remove cross-feature state sharing—make it self-contained and provide a migration note." 

Ambiguities & Questions (please advise)
---------------------------------------
- Does this apply to all languages and repo folders, or only frontend TypeScript code?
- Confirm the canonical path for data files: `src/data/` or `data/` at the repo root?
- Are there allowed exceptions for shared libraries (e.g., UI framework base components or infra packages)? If so, which packages?

Next steps (recommended)
------------------------
1. Review and answer the Ambiguities & Questions above.
2. If approved, add automated checklist items to PR templates that remind reviewers of the above principles (education-first, not auto-blocking enforcement).
3. Optionally: create small example feature (vertical-slice) that demonstrates compliance.

Maintainer note
---------------
These instructions are deliberately guidance-first. If the team wants stricter enforcement (CI gates), add that as a separate, documented policy and include migration guidance.
