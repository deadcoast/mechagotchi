# Code Style and Conventions

The repository uses dependency-light Python research labs with `unittest`, JSON fixtures, and explicit artifact writers. Existing Python files use standard-library modules heavily, simple functions, dictionaries/lists for research payloads, deterministic seeds, and CLI entrypoints guarded by `if __name__ == "__main__"`. Tests commonly add neighboring lab folders to `sys.path` because no package root exists yet.

Research conventions:
- Do not create or rely on `packages/` unless the user explicitly starts package implementation.
- Lab status strings and reports should distinguish research prototypes from package/runtime claims.
- Generated artifacts are mirrored as root JSON summaries and sometimes folder-local JSON/JS/README payloads under `data/`.
- Docs and JSON ledgers must retain blocked states for unproven surfaces; do not remove blockers unless new source/tests/artifacts directly prove them.
- Prefer deterministic seeds and exact counts in reports.

Editing conventions:
- Use ASCII unless a touched file already requires non-ASCII.
- Keep comments sparse and useful.
- Use `apply_patch` for manual edits.
- Do not revert unrelated dirty worktree changes.