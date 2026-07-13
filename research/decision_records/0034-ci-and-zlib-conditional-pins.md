# Decision Record 0034: CI Reproducibility and the zlib-Conditional Byte Pins

Date: 2026-07-12

## Status

**Accepted** (cycle 17 · Phase G, task G1). Authorizes the checked-in
CI workflow and the ONE test-scope change it requires: making the
foreign-fixture byte-identity pins conditional on the interpreter's
zlib build, as a documented environment observation.

## Context

The full sweep is the repo's standing verification (19 lab suites +
package + workshop + CLI + game). Phase G's charter requires it as
CI. One measured environment sensitivity stands in the way, recorded
in the F1 report (2026-07-12): `labs/workshop_editor/
test_foreign_fixture_conformance.py`'s committed-corpus BYTE pins
compare the independent spec-writer's CURRENT output against committed
fixture bytes. Deflate output is **zlib-BUILD-specific**: the
committed corpus was generated under a zlib-ng CPython build (the
Windows CPython 3.14 family reports `1.3.1.zlib-ng`), and a
classic-zlib interpreter (e.g. uv's python-build-standalone 3.13, or
Linux CPython against system zlib) produces different — equally
spec-valid — compressed bytes, failing 10 subtests that assert
nothing about correctness under that build.

What the byte pins actually protect: regression of the writer's exact
output UNDER THE GENERATING BUILD. What protects correctness under
EVERY build, and keeps running unconditionally:

- `test_manifest_hashes_match_committed_files` — the committed files'
  integrity against their recorded sha256s (build-insensitive);
- the decode-conformance suites — every fixture × decoder expectation
  over FRESHLY BUILT fixtures (a decoder must decode any spec-valid
  stream, whichever zlib compressed it).

## Decision

1. **The two byte-identity pins become build-conditional**: they run
   when `zlib.ZLIB_RUNTIME_VERSION` reports the fixture-generating
   build family (`zlib-ng`) and SKIP with a named reason citing this
   record otherwise. This is an environment OBSERVATION in the H-01
   sense — the tests record what the interpreter provides; they never
   pin the environment itself. The content-level gates stay
   unconditional.
2. **CI runs the sweep on two runners**: `windows-latest` with
   CPython 3.14 (the fixture-generating build family — the byte pins
   RUN there) and `ubuntu-latest` (classic zlib — the byte pins skip
   with the named reason, everything else runs; the skip path is
   thereby exercised on every push). The venv is built FROM the
   runner's set-up interpreter (`UV_PYTHON`), never uv's managed
   python-build-standalone, so the zlib provenance is explicit.
3. **The sweep is a checked-in script** (`tools/ci/run_sweep.py`,
   stdlib-only): lab discovery, the package/workshop/CLI/game suites,
   and JSON validation over every `data/**/*.json` artifact — the
   same runner locally and in CI, verified locally in this cycle.
   pygame suites run headless (`SDL_VIDEODRIVER=dummy`, the suites'
   own convention).
4. **Regenerating the fixture corpus remains a deliberate act** on a
   zlib-ng interpreter (the corpus README documents the build
   provenance); CI never regenerates committed fixtures.

## Consequences

- The sweep becomes reproducible off this machine with the known
  sensitivity handled honestly instead of hidden or deleted.
- The first green CLOUD run awaits a push (commits are never pushed
  unasked); the workflow and the sweep script are verified locally.
- If a future fixture regeneration lands under a different build,
  `FIXTURE_ZLIB_BUILD` in the test module is the single declared
  constant to update — with the corpus, in the same change.

## Sources

- `research/experiment_reports/2026-07-12-front-end-client-skeleton.md` (the recorded observation)
- `labs/workshop_editor/test_foreign_fixture_conformance.py`, `data/foreign_fixtures/`
- `docs/gap-analysis.md` (Phase G: CI + reproducibility)
- review finding H-01 (environment observations are recorded, never pinned)
