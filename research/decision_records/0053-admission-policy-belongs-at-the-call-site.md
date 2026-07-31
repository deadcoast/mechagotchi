# Decision Record 0053: A Study's Admission Policy Belongs at Its Call Site — and a Study That Measures a Defect Is Never Migrated Onto the Fix

Date: 2026-07-28

## Status

**ACCEPTED** — executed in cycle 24 N7 while carrying out DR 0052's
scheduled migration.

The `slip_admission` default is now `insertion` (DR 0052). All eight
historical callers name `slip_admission="none"` explicitly. **No
committed number moved**, and this record states the two rules that made
that the correct outcome rather than a hedge.

## Context

DR 0052 adopted `insertion` and scheduled the migration as N7, whose
charter said: *"Do not start it by flipping the constant — start it by
listing every artifact and test that moves."*

The inventory found **eight** production modules calling the loop
implicitly (DR 0052 estimated "at least six"; it missed
`generation_arm_evolution` and `novelty_evolution`), writing **eight**
committed artifacts, across **63** implicit call sites in 7 test files.

Flipping the default then broke **DR 0047's pinned byte-identity
contract** — `implicit == explicit("none")` — which turned out to be the
*weak* form ONBOARDING §9 warns about: it states a fact about the
default, not about off-mode identity.

## The decision

### Rule 1 — a study's admission policy is part of what it measured, so it is named at the call site

Every one of the eight historical callers now passes
`slip_admission="none"` explicitly, each with a comment saying why *that
study* is pinned. A default that can move underneath a committed
artifact is a silent contradiction waiting to happen; a named argument
is evidence a reader can check.

This is the same discipline N2 (DR 0050) applied to the probe geometry's
`edges_source`, and it generalises: **any setting that changes what an
artifact means is recorded at the call site that produced it, never
inherited from a default.**

### Rule 2 — a study that measures a defect is never migrated onto the fix

The obvious reading of "flip the default" is *regenerate the eight
artifacts and explain the deltas*. That reading is **wrong**, and wrong
in a way that destroys evidence. The clearest case:

> `generation_refusal_causes` (L1) **is the measurement of the
> 4,435-refusal tax.** Under `insertion` that tax is zero. Regenerating
> it on the new default would not *update* the finding — it would erase
> the evidence the finding is made of.

Three more measure the incumbent's population directly —
`elite_population_measures` (M1's *"48 of 460 elites are bootstrap"*),
`lineage_dominance` (L2, whose two largest founder lines are
bootstrap-founded), `family_ancestry` (M4) — and two are **bake-offs**
(`generation_arm_evolution` for DR 0031/0042, `novelty_evolution` for
DR 0040), which are only readable if every arm shares every other
setting with the run that decided them.

**A measurement does not improve. It is reproduced, or it is superseded
by a new measurement answering a new question.** If any of these are
ever re-run under the adopted default, they ship as **new artifacts
answering a new question** — never as regenerations of these.

### Rule 3 — the two genuine migration candidates need their own record

`evaluation_loop_scale` (E3, the source of **DR 0042's headline coverage
0.8984**) and `coverage_qd_gates` (the E4 gates) are the only two whose
migration is a real question. Migrating either restates a number quoted
across decision records, gate reports and ONBOARDING, with a delta
explained at every site. **That is a documented decision with its own
record — not a side effect of a default change**, which is exactly why
N7 refused to make it one.

## Consequences

**The change is prospective, and that is stated rather than dressed up.**

- Every existing study measures what it measured; every artifact keeps
  its meaning; **no committed number moves.** Proven by regenerating
  L1's artifact — the study whose subject would vanish if the pinning
  were wrong — and diffing: **every measured field reproduces exactly**,
  including `generation_attempts_total`, the reason-class histogram and
  the `k2_self_verification` block. The file is *not* bit-identical, and
  the claim is stated as measured rather than rounded up: the sole
  differing field is `metrics.wall_clock_s`, a machine-dependent
  stopwatch this repo's own convention keeps out of the deterministic
  report body. Had the pinning been wrong, the refusal histogram would
  have collapsed to zero — the failure the check exists to catch.
- Every **new** consumer gets zero refusal tax and a covenant-legal
  archive by default — pinned by
  `test_the_loop_default_is_the_ADOPTED_arm`, which is what makes the
  fix propagate instead of sitting in a record.
- The "what the loop achieves under the adopted default" numbers are not
  missing: N4 measured them and they are committed in
  `data/archives/slip_admission_default_stage0.json` (coverage 0.847005,
  QD 394.0508, 0 refusals, 0 illegal elites, three seeds).

**DR 0047's byte-identity pin is re-expressed, not deleted.** Its literal
guarantee — `slip_admission="none"` reproduces the pre-seam loop — is
still true and now carried by the frozen-key-set pin, which is the
stronger form. What changed is that the *implicit* call no longer means
`"none"`.

## Sources

- `research/experiment_reports/2026-07-28-slip-admission-migration.md` (this record's study)
- `research/decision_records/0052-slip-admission-default-insertion.md` (the adoption this executes), `0047-slip-admission-arms.md` (whose pin this re-expresses), `0050-probe-geometry-frozen.md` (the call-site discipline this generalises), `0042-generation-layer-loop-revisit.md`, `0040-novelty-first-evolution-surface.md`
- `labs/map_elites_archive/evaluation_loop_scale.py` (the flipped default) and the eight pinned callers
- `labs/map_elites_archive/test_slip_admission_arms.py`, `test_evaluation_loop_scale.py` (the re-expressed pins)
- `audits/TODO.md` (cycle 24 N7)
