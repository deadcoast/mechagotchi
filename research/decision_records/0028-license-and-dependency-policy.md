# 0028 — License: Apache-2.0; third-party dependencies permitted

- Status: accepted (owner decision, 2026-07-07)
- Deciders: owner
- Supersedes: the "deliberately blocked" package dependency policy and
  the "license pending" state (decision record 0005's package-side
  deferral; the scaffold gate's Metadata Acceptance deferral)

## Decision

1. **The repository and the `mecha-engine` package are licensed
   Apache-2.0.** Root `LICENSE` carries the verbatim text;
   `packages/mecha_engine/pyproject.toml` declares `license` /
   `license-files`.
2. **Third-party dependencies are PERMITTED wherever a capability
   genuinely needs one.** The owner's words: "we can't make
   everything." The stdlib-only rule is no longer a package boundary —
   it was a Stage 0 research discipline, and treating it as a product
   virtue misjudged the project's scope. Each dependency added to
   `[project.dependencies]` is justified in the decision record of the
   feature that needs it; labs keep the existing `lab` group mechanics
   (DR 0005).

## Context

Recorded together with the owner's broader course correction: the
repository's ~300k words of documentation define the scope; the
current implementation is an early fraction of it. Engineering
recommendations must serve the documented vision's scale — real
simulation scale, real ML, the full application — not minimize toward
what is already built.

## Consequences

- The scaffold gate's "Metadata Acceptance" deferral is closed; its
  text is updated to cite this record.
- Future capabilities may pull in real libraries (e.g. numerical,
  imaging, serving) when they earn their place; "could we hand-roll
  it?" is no longer a blocking question, only an engineering trade-off.
- CuBFF real-export ingest remains a REQUIRED late-stage feature (the
  owner, same correction) — the seam ships; the feature is queued for
  the stage that needs it, not "closed".

## Sources

- owner decision, 2026-07-07 (this session)
- `LICENSE` (Apache-2.0, verbatim)
- `packages/mecha_engine/pyproject.toml`
- `research/decision_records/0005-lab-dependency-group.md`
