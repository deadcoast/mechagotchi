# Experiment Report: The 11-Class Regrowth Head — A Narrow, Honest Refusal That Measures Its Own Dilution (Cycle 21 · SHARED · K1)

Date: 2026-07-21

## WHY

DR 0039's named remainder: repair PRESERVES the ratified vocabulary but
regrows through a 5-class head behind a recorded palette-family
coarsening — a wounded limb returns as body, a wounded antenna as eye.
Since DR 0038/0039 the ecology is rich (the era's elites span the full
alphabet; the committed 16×16 seed corpus carries all eleven live
tokens, 49/50 grids rich — probed before the design was fixed), so K1
charters DR 0041: the head's class vocabulary becomes a model-level
property, and the retrain is judged by gates PRE-REGISTERED before any
run (the DR 0040 discipline).

## WHAT

**The implementation (both head sites, mirrored verbatim)**:
`train_neighborhood_repair_model` / `train_repair_model` gain
keyword-only `vocabulary="legacy"|"rich"` — legacy is the historical
5-class head with the DR 0039 coarsening, byte-identical (the model
dict gains NO new key, the DR 0038 rider pattern); rich trains a
12-way softmax over the full ratified live alphabet with IDENTITY
perception, its feature layout derived from the live-token count
exactly as it derives from grid scale (DR 0029's precedent). Every
consumer (wound-site fill, the validity guard including the DR 0039
island drain, the blind benchmark arm) derives the class alphabet FROM
THE MODEL (`model.get("vocabulary", "legacy")`; a model whose recorded
`class_tokens` contradict its vocabulary is refused loudly). The
repair interface spec and contract pin record the signature evolution.

**The study** (`labs/cellular_automata/regrowth_head11.py`): both
heads trained on the committed 16×16 seed corpus (training 40,
held-out 10), 90 seeded wound events at dropout 0.2/0.4/0.6, wound-site
repair guard-on, 2,680 wound sites measured per arm; 139–162 s vs the
registered 900 s bound.

## THE PRE-REGISTERED VERDICT: `withhold_adoption`

| Gate | Bar | Measured | Verdict |
| --- | --- | --- | --- |
| G1 exact-token gain | ≥ +0.10 | **+0.0944** (0.7414 → 0.8358) | **REFUSED** |
| G2 family held | ≥ −0.02 | +0.0366 (improved) | met |
| G3 validity held | ≥ 0.0 | 0.0 (1.0 → 1.0) | met |
| G4 legacy byte-identity | unchanged | no key; HEAD-vs-K1 regen hash-equal | met |
| G5 parity | byte-identical | legacy AND rich, both sites | met |

The rule is the rule (the DR 0032 precedent): adoption is withheld,
the era loop keeps the legacy head, the coarsening stays the recorded
default. Nothing was re-scored after the fact.

**And the refusal carries its own mechanism, measured**: the artifact's
site-breakdown observation (an instrument extension, not a gate — the
gates re-verified identical under it) splits the 2,680 sites:

- **480 rich-token sites**: legacy exact restoration **0.0** — the
  5-class head literally cannot spell them (measured, as the DR
  demanded, never assumed); the rich head restores **0.525**.
- **2,200 legacy-token sites**: 0.9032 vs 0.9036 — statistically
  identical; spelling the full alphabet costs the shape prior nothing.
- **Guard substitutions 131 → 5**: coarsened B-fills at rich sites
  break invariants the guard must hill-climb away; native-vocabulary
  fills almost never do — regrowth quality was hiding inside guard
  work.

The pooled G1 gain is therefore pure arithmetic of the denominator:
0.525 × 480/2680 ≈ 0.094 — the entire advantage lives at the sites
legacy cannot spell, averaged down by the sites it already restores.
**The re-opener is NAMED, not smuggled**: a future record may
re-charter the gate on the undiluted instrument (rich-site exact
restoration); this record's bar stands refused as registered.

## G4, proven not inferred

Regenerating `ca_nca_trained_repair_stage0.json` surfaced a 2-line
diff (`width`/`height` added). Diagnosed from history, then PROVEN:
the committed artifact predates DR 0029's model-scale keys (last
regenerated 2026-07-04; DR 0029 landed 2026-07-08), and a pristine
HEAD-code regeneration in a scratch worktree hashes **byte-identical**
to the K1-code regeneration (`A743C773…` both) — the drift is
DR 0029's, not K1's. The refreshed artifact is committed with this
cause named; the boundary artifact regenerated with zero diffs.

## Verification

```powershell
PS> python -B -m unittest test_regrowth_head11   # (from labs/cellular_automata)
ImportError: cannot import name 'RICH_CLASS_TOKENS' from 'ca_nca_growth_repair'   # RED
# after the implementation + study module:
Ran 12 tests ... OK
PS> python -B -m unittest test_ca_nca_growth_repair test_package_repair_parity test_repair_vocabulary_preservation test_repair_scale16
Ran 37 tests ... OK                    # legacy byte-identity via the unmodified parity pins
PS> python -B -m unittest discover -s packages/mecha_engine/tests -p "test_*.py"
Ran 295 tests ... OK                   # after the contract pin records the signature evolution
PS> python -B labs/cellular_automata/regrowth_head11.py
verdict: withhold_adoption             # 2,680 sites/arm; 139-162 s vs the 900 s bound
```

## HONEST REMAINDER

1. **The rich head is implemented but unadopted** — trainable,
   parity-pinned, opt-in at both sites; the era loop keeps the legacy
   head until a record re-charters the gate on the undiluted
   instrument (rich-site exact restoration, baseline 0.525 vs 0.0).
2. **The 0.525 ceiling at rich sites is unexplained** — architecture
   (linear softmax), training budget, or corpus statistics; naming the
   binding constraint is the re-opener's first measurement.
3. **The mechanism finding (guard substitutions 131 → 5)** suggests
   guard work as a cheap regrowth-quality instrument on any future
   head comparison.

## Sources

- `audits/TODO.md` (cycle 21 K1) · `research/decision_records/0041-eleven-class-regrowth-head.md` (the charter + measured verdict) · `0039-repair-vocabulary-preservation.md` (the named remainder)
- `labs/cellular_automata/ca_nca_growth_repair.py` + `regrowth_head11.py` (+ `test_regrowth_head11.py`, 12 pins)
- `packages/mecha_engine/src/mecha_engine/repair/{_features,train,wound,blind}.py` (the mirror) + `packages/mecha_engine/tests/test_repair_contract.py` + `research/package_specs/mecha_engine_repair_interface_spec.md` (the recorded signature evolution)
- `data/cellular_automata/regrowth_head11_stage0.json` (the artifact) + `ca_nca_trained_repair_stage0.json` (the DR 0029 refresh, cause proven)
- `research/algorithm_cards/ca_nca_growth_repair.md` (the card's vocabulary-evolution block)
