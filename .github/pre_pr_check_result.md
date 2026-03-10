# PR Checklist for: feat: add interactive pre-PR checklist script

Initial Set up for Base Repo using Open Spec

- [x] I verified this change follows the People-First & Simplicity principle (clear, maintainable code).
- [x] The change follows Screaming Architecture (feature/vertical-slice organization) where applicable.
- [x] No new generic `utils/`, `helpers/`, or `services/` were added at the repository root without documented justification.
- [x] Data/config was added under `src/data/` (or `data/` with justification) and exported as a single well-typed constant when applicable.
- [x] The change preserves or documents Airplane Mode requirements (local mocks, no runtime external deps for dev/tests).
- [ ] Any shared-library or cross-feature exception is documented in the repo README or exceptions file with rationale.
- [ ] The author included tests or a clear testing note, and the change leaves the repo in a releasable state (Last Day).
- [ ] Performance optimizations are documented and justified with benchmarks if they reduce readability.