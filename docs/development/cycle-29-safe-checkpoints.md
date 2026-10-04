# Cycle 29 S2: durable play checkpoints and save-failure recovery

Preregistered 2026-10-04 after S1 full closure and before S2 RED. Use the
existing repo/.venv and workflow; no Git mutations or new process machinery.

Review observation `.development/s2-review.json`: real app runs with isolated
saves and injected replacement failures reproduced two defects. A failed
companion write left the export at two lineage records while the authoritative
save retained one. A failed lineage write raised before companion save and
lost current progress despite a writable companion path. The in-app browser
reads the companion's embedded lineage, not the standalone export.

Make companion.json the single authoritative checkpoint, including its embedded
lineage and unchanged learning policy/state. Write it before attempting the
derived lineage export; export failure must not prevent saving the pet. Repair
missing/stale exports from a validated loaded or explicitly recovered companion
before play, preserving replaced export bytes through existing backups. Keep
S1 backup validation, archives, byte preservation and refusal semantics.

Make saving usable during play: Ctrl+S checkpoints without invoking sleep.
Checkpoint critical death/adoption/succession boundaries. A primary save failure
must keep the current pet in memory, pause care, show the failure and permit
retry. Failed interactive quit stays open; Ctrl+S retries that quit, and Ctrl+Q
explicitly exits without saving. Bounded verification exits nonzero rather than
hanging or throwing a traceback. Export-only failures are visible warnings;
the saved pet remains usable. Reuse the current wrapped/paged casing and help.

RED pins: primary failure leaves old primary/export coherent; export failure
still commits the new primary and repairs on reload; repair is idempotent;
backup recovery derives the earlier lineage without changing learning; actual
interactive quit/retry/discard preserves care time and bytes; manual save is
not sleep; child adoption checkpoints are resumable; bounded failure is nonzero.

Observe source, CLI and native behavior with isolated fault fixtures; inspect
rendered save-failure/retry casing. Focused game/package/CLI verification is an
implemented checkpoint. Full sweep, artifact/preservation audit and diff review
remain required for local slice closure. No multi-file transaction claim,
new learning algorithm, default promotion or scientific threshold change.
