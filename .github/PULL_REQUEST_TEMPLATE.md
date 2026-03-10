<!-- Pull Request template for Repository Base Template -->

## Summary
Short description of the change and why it is needed.

## Checklist for reviewers (education-first guidance)
These checklist items are guidance to help reviewers and authors apply the repository's principles. They are educational suggestions, not automated blockers.

Reviewers and authors can mark items as: checked (`- [x]`), unchecked (`- [ ]`), or `N/A` (not applicable). To mark an item N/A, include the checklist line and append `(N/A)` — e.g. `- [ ] The change preserves Airplane Mode requirements (N/A)`.

- [ ] I verified this change follows the _People-First & Simplicity_ principle (clear, maintainable code).
- [ ] The change follows _Screaming Architecture_ (feature/vertical-slice organization) where applicable.
- [ ] No new generic `utils/`, `helpers/`, or `services/` were added at the repository root without documented justification.
- [ ] Data/config was added under `src/data/` (or `data/` with justification) and exported as a single well-typed constant when applicable.
- [ ] The change preserves or documents _Airplane Mode_ requirements (local mocks, no runtime external deps for dev/tests).
- [ ] Any shared-library or cross-feature exception is documented in the repo README or exceptions file with rationale.
- [ ] The author included tests or a clear testing note, and the change leaves the repo in a releasable state (Last Day).
- [ ] Performance optimizations are documented and justified with benchmarks if they reduce readability.

## Notes for reviewers
- These items are educational guidance derived from the repository's base instructions: see `.github/copilot-instructions.md` for full details.
- If you believe an item should be enforced by CI, propose that as a separate PR explaining the rationale and migration path.

## Related
- Link any related issue, spec, or design note.
