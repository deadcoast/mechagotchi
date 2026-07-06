# Decision Record 0015: Dormant Grid-Schema Vocabulary — Cover, Not Trim

Date: 2026-07-05

## Status

**Accepted** (audit task T15; owner: "Next action: T15 --go").

## Verdicts, per dormant item

| Item | Verdict | Action |
| --- | --- | --- |
| Cell roles shell/joint/limb/antenna/decoration/effect/sensor | **COVER** | Exemplar corpus (`data/vocabulary_exemplars/`, this record) exercises every role today; DR 0011 ratified the vocabulary and T3.5 (`limb_growth`) plus T9 (trait editor) depend on it. |
| Materials light/signal | **COVER** | Exercised by the exemplar (antenna/effect = signal, decoration = light). |
| Organ roles locomotion/ornament/effect | **COVER** | Exemplar organs joints/limbs (locomotion), trim (ornament), aura (effect); the validator accepted the open organ map first try — genuinely vocabulary-generic. |
| Grid sizes 8–64 | **Already decided** | DR 0014: schema stays 8–64; sizes re-open via T17. |
| Workshop authoring affordances for the new roles | **DEFERRED to T9** | The trait editor is the chartered surface; the exemplar corpus is its test material. |
| Animation semantics for the new roles | **WATCH** | T4's projections deliberately key off eye/mouth/body only; per-role animation (antenna twitch, effect pulse) is a future T4 increment, recorded not improvised. |

## The drift guard

`labs/grid_genome/test_vocabulary_exemplars.py` pins that the combined
corpus (exemplars + seeds) exercises EVERY schema cell role (minus
`empty`), every material (minus `void`), and every organ role — the
vocabulary can never silently go dormant again. The exemplar also passes
the promoted validator, renders through the packet contract, and
survives all five animation projections (pinned).

## Sources

- `audits/audit-devspec.md` (addendum A1), `audits/TODO.md` (T15)
- `research/decision_records/0011-run-one-run-two-reconciliation.md`, `0014-grid-size-commitment.md`
- `labs/grid_genome/vocabulary_exemplars.py`, `labs/grid_genome/test_vocabulary_exemplars.py`
- `data/vocabulary_exemplars/`
