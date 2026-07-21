# Decision Record 0041: The 11-Class Regrowth Head — Repair Learns to Spell What It Preserves

Date: 2026-07-20

## Status

**Accepted and implemented — adoption WITHHELD by the pre-registered
rule** (cycle 21 · Phase K · K1). This is DR 0039's named future
record, chartered with pre-registered gates BEFORE any comparison run
(the DR 0040 discipline: the decision section is filled only from the
committed artifact; a draft carrying pre-run numbers is a process
violation). The head is implemented at both sites and G2–G5 passed;
**G1 refused at +0.0944 vs the ≥ +0.10 bar** — the rich head stays a
trainable, parity-pinned, opt-in vocabulary, and the coarsening stays
the recorded default everywhere. See "Measured verdict" below.

## Context

DR 0039 made repair vocabulary-PRESERVING: surviving rich cells keep
their ratified roles verbatim through every damage/repair cycle, and the
era lives. But the learned regrowth head stayed 5-class (`. B A E M`)
with a recorded perception coarsening (`PERCEPTION_LIVE`: body-family
S/J/L → B, sensory/light-family N/P/D/F → E) for feature encoding and
training labels alike — so **a wounded limb returns as body, a wounded
antenna as eye**. Restoration is honestly partial by construction. The
ecology now demands regrown limbs: since DR 0038/0039 the breeding
surface emits the motion trio at 0.512, the era's elites span the entire
ratified vocabulary, and the committed seed corpus itself carries the
trio at 0.48 — the creatures being wounded are rich, and the head that
regrows them is not.

## Decision

The head's **class vocabulary becomes a model-level property**, chosen
at training time by a keyword-only `vocabulary` parameter at both head
sites (the CA lab authority `ca_nca_growth_repair.py` and the promoted
`mecha_engine.repair` — mirrored verbatim, parity-pinned; the runtime's
`_grids` twin carries no head and is untouched):

1. **`vocabulary="legacy"` (the default)**: `LIVE_TOKENS = B A E M`,
   `CLASS_TOKENS = . B A E M`, `PERCEPTION_LIVE` coarsening — the
   historical head, byte-identical: identical inputs train identical
   weights, and the model dict gains NO new key (the rider pattern,
   DR 0038: the `vocabulary` key is recorded ONLY when non-legacy, so
   every committed model and artifact is unchanged).
2. **`vocabulary="rich"`**: the live classes are the ELEVEN ratified
   live tokens in declaration order (`B A S J L E M N P D F` — a
   12-way softmax with empty), perception is the IDENTITY (no
   coarsening: the head sees and predicts the full alphabet). The
   feature layout derives from the live-token count exactly as it
   derives from grid scale (DR 0029's precedent): 24 offsets × 11
   live one-hots + position + bias.
3. **Consumers read the vocabulary FROM THE MODEL**
   (`model.get("vocabulary", "legacy")` — pre-DR-0041 models carry no
   key and are legacy, the `_require_model_scale` compat precedent):
   the wound-site fill, the validity guard (strict pass AND the
   DR 0039 island drain — whose core set stays `{B, A}` in both
   vocabularies), and the blind benchmark arm all derive
   (live tokens, class tokens, perception) from the model they were
   handed, so one code path serves both heads and a model can never
   be decoded through the wrong alphabet.

## Pre-registered gates (the K1 study fills these from its artifact; a refused gate is a first-class finding)

The study (`labs/cellular_automata/regrowth_head11.py`) trains BOTH
heads on the committed 16×16 seed corpus — the ratified default scale
(DR 0029) and the measured rich corpus: probed before this design was
fixed, it carries ALL eleven live tokens with 49/50 grids rich (the
8×8 seed corpus projects to legacy tokens only, so it serves as G4's
byte-identity control, not a comparison arm) — using the benchmark's
split (training 40, held-out 10), wounds the held-out grids with
seeded stochastic damage at the boundary study's rates
(0.2, 0.4, 0.6), repairs through `repair_with_wound_sites` (guard
on), and measures at the wound sites. Run-once wall-clock bound
registered at ≤ 900 s stdlib (DR 0028 discipline; an overage is cited
with its cause, never silent).

- **G1 — exact-token restoration**: the rich head's wound-site
  exact-token restoration exceeds the legacy head's by ≥ +0.10
  absolute, pooled over the corpus (the legacy head cannot emit seven
  of the eleven tokens; its exact restoration on rich sites is
  expected near zero — but it is MEASURED, never assumed).
- **G2 — no family regression**: with BOTH arms' outputs judged after
  palette-family coarsening, the rich head's family-level restoration
  is ≥ the legacy head's − 0.02 (spelling the full alphabet may not
  cost the shape prior).
- **G3 — validity held**: the rich arm's post-repair
  validator-valid rate is ≥ the legacy arm's on the same wounds
  (guard substitutions recorded per arm, never hidden).
- **G4 — byte-identity where the head is not engaged**: training with
  the keyword unset reproduces the committed legacy weights and model
  dict byte-identically, and the committed repair/boundary artifacts
  regenerate with zero diffs when regenerated on the legacy path.
- **G5 — parity verbatim**: every existing lab↔package repair parity
  pin passes unmodified, plus new rich-head pins (rich-trained
  weights and rich wound repairs byte-identical across the two head
  sites).

**Adoption rule (pre-registered)**: if G1–G5 all pass, the era-loop
consumer (the game campaign's repair-model training) adopts
`vocabulary="rich"` and the perception coarsening is RETIRED from the
rich path — it remains only as the legacy vocabulary's recorded
perception, because legacy models are never retrained; the full game
suite (the era regression) must stay green for the adoption to stand,
and the boundary study re-measures under the adopted head with its
artifact regenerated. If ANY gate refuses, the adoption is withheld,
the coarsening stays the recorded default everywhere, and the refusal
is recorded with its numbers — reverted or narrowed, never fudged.

## Measured verdict (filled from `data/cellular_automata/regrowth_head11_stage0.json`, run 2026-07-21; 139–162 s across the two instrument passes vs the 900 s bound)

| Gate | Bar | Measured | Verdict |
| --- | --- | --- | --- |
| G1 exact-token gain | ≥ +0.10 | **+0.0944** (legacy 0.7414 → rich 0.8358) | **REFUSED** |
| G2 family held | ≥ −0.02 | **+0.0366** (0.8437 → 0.8802 — improved) | met |
| G3 validity held | ≥ 0.0 | 0.0 (1.0 → 1.0) | met |
| G4 legacy byte-identity | unchanged | no key, historical classes/id; artifacts regenerate zero-diff | met |
| G5 parity | byte-identical | legacy AND rich identical across both sites | met |

**Verdict: `withhold_adoption`** — the rule is the rule (the DR 0032
precedent: the advantage is real and measured, and the clause stays
refused honestly; nothing is re-scored after the fact). The era-loop
consumer keeps the legacy head; the coarsening stays the recorded
default.

**What the refusal's numbers name (recorded observations, not gates)**:
the rich head improved EVERY measured quality — exact restoration at
every dropout rate, family restoration, and guard work (substitutions
**131 → 5**: coarsened B-fills at rich sites break invariants the
guard must hill-climb away; native-vocabulary fills almost never do).
The pooled G1 metric is DILUTED: most wound sites hold body-family
tokens the legacy head already restores exactly, so the rich head's
advantage — concentrated at the seven tokens legacy cannot spell — is
averaged down by a denominator it was never about. The artifact's
site-breakdown observation measures this directly (rich-token sites
vs legacy-token sites, per arm). **A re-opener is NAMED, not
smuggled**: a future record may re-charter the gate on the undiluted
instrument (rich-site exact restoration), but this record's bar
stands refused as registered.

## Consequences

- Repair can REGROW the vocabulary it preserves: a wounded limb can
  return as a limb. Whether it does — and at what shape-prior cost —
  is the study's measurement, not this record's claim.
- The linear-softmax architecture is retained (stdlib, deterministic,
  convex). An NCA with hidden state remains out of scope; if the rich
  head's restoration gains stall at the architecture's ceiling, that
  ceiling becomes a named remainder with its own record.
- Legacy models, artifacts, and every consumer that never passes the
  keyword are byte-identical — the additivity law (DR 0038/0039)
  extends to the head.

## Sources

- `research/decision_records/0039-repair-vocabulary-preservation.md` (the named remainder this record charters)
- `research/decision_records/0038-vocabulary-complete-generation-alphabet.md` (the rider pattern; the additivity law), `0040-novelty-first-evolution-surface.md` (the pre-registration discipline), `0029-16x16-default-grid-scale.md` (the size-parametric layout precedent)
- `labs/cellular_automata/ca_nca_growth_repair.py` (the head authority) + `test_package_repair_parity.py` (the parity pins)
- `packages/mecha_engine/src/mecha_engine/repair/{_features,train,wound,blind}.py` (the mirror site)
- `labs/repair_boundary/repair_validity_boundary.py` (the boundary instrument), `labs/grid_genome/corpus_builder.py` (the rich seed corpus)
- `game/src/mecha_game/campaign.py` (the era-loop consumer named by the adoption rule)
- `research/experiment_reports/2026-07-20-role-emission.md` (the corpus richness measurements cited in context)
