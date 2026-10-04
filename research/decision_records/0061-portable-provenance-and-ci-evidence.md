# Decision Record 0061: Portable provenance and retained CI evidence

Date: 2026-10-04

## Status

Accepted for the integrated CI repair. Acceptance is the full local sweep
and both native GitHub runners on the published commit, not a simulated
Linux checkout or the historical local-green claim.

## Evidence and decision

The original ledger was generated from a Windows working tree with CRLF
JSON and an LF seed README. These included text files are LF in Git. Fresh Windows checkout
converts that README, while Ubuntu leaves all three included assets LF.
The tree algorithm additionally sorts native Path objects, whose case folding
differs by OS. Local replays reproduce the cloud's 4/6 asset failures and
9/10 package failures. Architecture and runtime fail downstream provenance
checks. Nothing in this evidence implicates the zlib-conditioned foreign
fixtures or Q1's engine decision seam.

1. The three included asset locations now have explicit LF checkout attributes.
   File hashes remain raw SHA-256; directory hashes retain the NUL-delimited
   relative-name/content-digest formula, with ordering explicitly defined as
   case-sensitive lexical ordering of relative POSIX strings. Hashing never
   normalizes input bytes. This repairs the unspecified platform behavior;
   it deliberately changes recorded digests, rather than claiming byte parity.
2. `hash_policy: raw-bytes-posix-lexical-v1` and the 2026-10-04 generation date
   identify the current ledger restatement. Exact prior Git blobs are retained
   under `data/asset_provenance/baselines/stage0-windows/`. The new restatement
   artifact enumerates all three old/new digests. Historical experiment claims
   remain intact with dated correction notes. Original artifacts are evidence
   of the earlier instrument, not validators of the corrected checkout.
3. The lab and package stay mirrored. A literal mixed-case/nested fixture
   supplies an independent byte-stream oracle. Changing only LF to CRLF in an
   input must still change the digest; stale and altered assets still fail.
4. CLI help tests compare decoded ANSI text. NO_COLOR removes colors, not all
   styles; GitHub's terminal forcing separates characters in otherwise valid
   option names. Fresh subprocess tests exercise both dumb and styled terminals.
5. Every sweep suite retains stdout/stderr, counts, skips, duration and exit
   status. Failed traces are visible; timeouts preserve partial output; empty
   discovery fails. The 900-second per-suite bound exceeds twice the measured
   slowest #32 suite. CI uploads diagnostics even on failure and rejects tracked
   evidence changes. Three SLIP writers accept explicit output locations so
   their tests exercise real writes without replacing committed observations.

## Consequences

Old tree digests cannot be assumed portable; consumers must use the identified
baseline. This correction is intentionally limited to the provenance contract,
test assertions and the verification instrument. No learning threshold, covenant
default, dependency lock, corpus semantics or scientific verdict changes.

The full sweep adds a small CI-instrument suite. DR 0034's two zlib byte pins
remain conditional; semantic fixture checks remain unconditional. Missing
dependencies are recorded, and CI provisions every declared dependency group.

## Sources

- `docs/development/ci-reproducibility.md`
- `research/experiment_reports/2026-10-04-ci-portability-repair.md`
- `data/asset_provenance/portability_restatement_stage0.json`
- `labs/asset_pipeline/test_provenance_portability.py`
- `tools/ci/run_sweep.py`, `tools/ci/tests/test_run_sweep.py`
- `research/decision_records/0034-ci-and-zlib-conditional-pins.md`
- https://docs.python.org/3/library/pathlib.html#general-properties
- https://git-scm.com/docs/gitattributes
- https://rich.readthedocs.io/en/latest/console.html#environment-variables
