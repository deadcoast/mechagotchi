# Completion Checklist

Before claiming a research continuation is complete:
- Run the focused tests for the changed lab.
- Run adjacent lab suites touched by the dependency surface.
- Validate new/changed JSON artifacts with `python -m json.tool`.
- Run relevant JS syntax checks if workshop browser data or app JS changed.
- Run a targeted stale-text search over `research`, `data`, and `labs` for old blocker wording.
- Run `Test-Path .\packages` when package absence matters.
- Run `git diff --check` and report any warnings honestly.

Final reporting should state exactly what was added/updated, which tests passed, and which blockers remain. Avoid saying a parent scope is complete unless every documented required surface is directly verified.