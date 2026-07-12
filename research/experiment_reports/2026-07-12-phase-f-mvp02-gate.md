# Experiment Report: The MVP 0.2 Gate — the Creator Loop Closes (Cycle 15 · GAME · F12)

Date: 2026-07-12

## WHY

Cycle 15 climbed the ladder's second rung. MVP 0.2's own sentence
(validity §1.23): *"Add Markov grid generation. Add micro-learning
threads. Add profile-weighted mutation. Add visual editor. Add
preview simulation."* The cycle also owed the MVP 0.1 gate's named
product remainders: covenant spending, the Contribute bridge, the
Review replays, and hardening.

## THE GATE — MVP 0.2's checklist, judged honestly

| The documented element (§1.23) | Delivered | Where |
| --- | --- | --- |
| Markov grid generation | **In the product** (F8): the hatchery's candidates carry the engine's own trace — `proposal_source: markov_local_adjacency_proposals` finished by the constrained stabilizer, validator-gated, covenant-filtered | `hatchery_stage0` |
| Micro-learning threads | Delivered in cycle 14 F3b (the D6-kept five streaming into begs-soon / clip choice / felt mood) | `fleet_consumers_stage0` |
| Profile-weighted mutation | The covenant weights every generation path: succession (`generate_candidate` under the active covenant, F2/F7) and the hatchery (parent-pool filtering + alignment, F8) — the SLIP's mutation profile is the engine's own input | `hatchery_stage0`, `covenant_spending_stage0` |
| Visual editor | **On the workshop surface, by design** (the docs' own split: `mecha_workshop` is the authoring layer) — the GAME consumes it through the F9 Contribute bridge; authoring depth (layers/onion-skin/timeline) remains the workshop track's measured gap, unchanged | `contribute_bridge_stage0` |
| Preview simulation | The workshop's preview page stands; the GAME's product-side answer is the Review — a real recorded life replayed (F10) | `review_replay_stage0` |

The cycle's tasks, each gated green with its stage-0 artifact:

| Task | Result |
| --- | --- |
| **F7 · covenant spending** | the budget/spend rule (session-lab semantics, SLIP-authority-validated); one calm era earned 8 facts, palette+thinking+population(64) spent, the spent-covenant era filled 93 niches — DR 0021's exponential axis observed |
| **F8 · the hatchery** | founders generated under the covenant with verbatim generation traces; released founders lead the pool |
| **F9 · the Contribute bridge** | file-bridge inboxes; the engine's admission verdict shown never smoothed (the committed 8×8 releases reject verbatim on size; an aligned 16×16 release admits and leads) |
| **F10 · the Review replays** | the era's best elite lives one RECORDED life at the era's own seed; scrubber invariant at every frame; the G2 truncation boundary pinned |
| **F11 · hardening** | model cache byte-equal-pinned; `--windowed` build; `mechas game` live-verified |
| **F12 · this gate** | 19 lab suites + package 295 + workshop 60 + CLI 23 + **game 117** — all green |

The creator loop the cycle names is playable end to end: **spend your
earned covenant → hatch a founder under it (origin legible) → raise
it → release it into an era → watch the era's recorded life → adopt
the elite.** Every number in that sentence is an engine output.

## HONEST REMAINDER (what Phase F still owes)

1. **The 0.3 rung** (validity §1.24) decomposes into cycle 16 FROM
   THE GAP ANALYSIS: the archive/niches surfaced as a browsable
   repertoire, SLIP import/export in the product, the lineage
   browser, community profile packs.
2. **Named product remainders carried forward**: replay persistence
   (the ledger's `record_replay` surface awaits its consumer);
   campaign resume re-earns spends from persisted facts (the ACTIVE
   spent covenant is process-state); the committed workshop releases
   are 8×8-era pieces (16×16 authoring is the workshop track's gap);
   the model cache keys on grid ids (a content hash the day
   generated corpora feed the trainer); the windowed bundle not
   separately launch-verified.
3. **Standing engine remainders unchanged** (the cycle-15 standing
   note's list), and **Phase G stays late-stage** (real-CuBFF ingest
   REQUIRED; CI/packaging matrices; community; the M7 public alpha).

## VERDICT

**The Phase-F MVP 0.2 gate is GREEN.** Phase F CONTINUES at the 0.3
rung; cycle 15 archives to `audits/complete/15/`; cycle 16 opens from
the gap analysis.

## Verification

```powershell
PS> # the closing sweep (2026-07-12)
# 19 lab suites (system python -B): all OK
# package 295 OK · workshop 60 OK · CLI 23 OK · game 117 OK
PS> uv run python -B game/evidence.py
# ten artifacts under data/game_client/, every status "complete"
PS> mechas game --play   # the product, playable
```

## Sources

- `audits/TODO.md` (cycle 15, all six tasks checked) → `audits/complete/15/`
- `docs/project-research/validity-research.md` (§1.23 — the judged sentence; §1.24 — the next rung)
- `docs/gap-analysis.md` (Phase F), the five task reports of 2026-07-12 (`covenant-spending`, `hatchery`, `contribute-bridge`, `review-replay`, `product-hardening`)
- `data/game_client/` (the ten stage-0 artifacts)
