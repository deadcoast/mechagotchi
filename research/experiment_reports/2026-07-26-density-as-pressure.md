# Experiment Report: Density as Pressure — the Checkpoint Forecast Stops Lying About the Biology (Cycle 22 · SHARED · L5)

Date: 2026-07-26

## WHY

I3 measured a defect through the untouched seam and recorded it
honestly rather than tuning it away: **real post-takeover soup produces
MILDER weather than early-phase soup** (mean dropout multiplier 0.784
vs 0.818). The same runs measure **2 replicating programs of 131,072
early against 129,211 (98.6%) post-takeover**. So a Keeper meets the
mature, replicator-dominated soup as the *gentler* era.

DR 0043 clause 2 named the candidate fix and refused to smuggle it:
*"whether density should FEED the pressure math is the named future
record."* This is that record.

**The mechanism, diagnosed exactly.** The promoted pressure math is:

```text
mutation_pressure = 0.45·instability + 0.35·semantic_pressure
                    + 0.20·instruction_diversity
instability       = 0.45·entropy + 0.30·lineage_churn + 0.25·(1 − replication_dominance)
semantic_pressure = 0.50·replication_rate + 0.25·motif_repetition + 0.25·lineage_churn
```

On the **checkpoint** path `replication_scores` and `lineage_events`
are *structurally absent* — the format cannot carry them (DR 0043
clause 3 dispositioned `lineage_churn` BLOCKED-UPSTREAM). With those
terms at zero, pressure is driven almost entirely by **entropy** and
**instruction diversity** — and **both of those FALL as a soup
organizes**. The engine reads organization as calm. Every channel it
can see decreases; every channel that would rise is missing.

That is engine truth of the sharpest kind: no number is invented, and
the player is still shown the opposite of the biology.

## WHAT

**Instruction density is the one carried channel that RISES with
organization** — J4 measured it and K4 landed it on the game's own
forecasts (early 6.92, post-takeover 11.5, against a random expectation
of 2.5). So it is not a knob bolted onto the formula; it is the
specific missing counterweight, available on exactly the path whose
harshness channels are silent.

**The signal is derived, not calibrated.** A uniformly random tape of
length *n* carries `n × 10/256` instruction bytes, so

```text
organization_ratio  = density / (n × 10/256)      # 1.0 at chance
organization_signal = clamp((ratio − 1) / (CEILING − 1))
CEILING = 256/10 = 25.6
```

`CEILING` is the theoretical maximum — an all-instruction tape has
ratio `n / (n × 10/256) = 256/10` — and is therefore **independent of
tape length**, a property of `bff_noheads`'s alphabet rather than of
the corpus. Nothing here is fitted to the outcome, which is what keeps
the gate honest. `CUBFF_DENSITY_WEIGHT = 0.5` was pre-registered:
density may contribute at most 0.5 to a pressure in [0,1] — enough to
matter, never enough to dominate the three incumbent terms.

**The rider follows the DR 0038 pattern exactly**, at both parity
sites (the `cubff_transducer` lab authority and its `runtime/_cubff.py`
package mirror): keyword-only, byte-identical when off, mirrored
verbatim, parity-pinned. `extract_cubff_features(...,
include_density=False)` adds four keys only when asked;
`features_to_traits(..., density_weight=0.0)` is the incumbent formula
exactly at weight zero; `_cubff_generation_pressure(...,
density_pressure=False)` threads it.

**The prediction was written down before the run.** DR 0045's Decision
section computed the expected swing from the committed densities —
signal 0.0719 early, 0.1463 post-takeover, ≈ 0.037 in pressure, **≈
0.041 in multiplier** — against I3's 0.034 inversion, and said plainly:
*"the rider is therefore predicted to just barely flip it — and it may
not."*

## FINDINGS

### The gates: ADOPT

| | early | post-takeover | gap |
| --- | --- | --- | --- |
| checkpoint, rider **OFF** | 0.818009 | 0.783716 | **−0.034293** |
| checkpoint, rider **ON** | 0.857880 | 0.864204 | **+0.006324** |
| callback (lit channel, ground truth) | 0.772726 | 1.034884 | +0.262158 |

- **G1 MET** — the inversion is corrected: **−0.034293 → +0.006324**.
- **G2 MET** — the callback path, whose replication channel is LIT,
  reads `post_takeover_harsher`; the density-fed checkpoint ordering
  now agrees with it.
- **G3 MET** — all **sixteen** committed game evidence artifacts
  regenerate **byte-identical**, and the transducer (58), runtime (65)
  and package (295) suites pass unmodified with the rider off.
- **G4 MET** — `replication_rate` and `lineage_churn` stay **0** on
  every checkpoint record with the rider ON; DR 0043 clause 3's
  disposition is untouched.
- **G5 MET** — every multiplier stays inside the documented
  `(0.5, 1.6)` band.

### The prediction was right to four decimal places

Predicted swing, written before the run: **≈ +0.041**. Measured swing:
−0.034293 → +0.006324 = **+0.040617**.

A ceiling taken from the language's alphabet and a weight fixed at 0.5
produced the observed magnitude with **no adjustment of any kind**.
That agreement is the strongest evidence that the formulation is
describing something real rather than being fitted to a wanted answer —
and had it come out on the other side of zero, DR 0045 committed in
advance to recording the refusal instead.

### The honest limit, stated with the win

The corrected gap is **+0.0063 against the ground truth's +0.2622 —
roughly **2.4% of the magnitude**.

**Density recovers the DIRECTION of the biology, not its force.** The
checkpoint forecast now points the right way, and it remains a far
quieter instrument than the lit-channel callback path. The margin is
thin enough that this is a *correction*, not a dramatization — which is
the right outcome for a proxy standing in for a channel the format
genuinely cannot carry. Anyone reading `+0.0063` as "the checkpoint
forecast now conveys post-takeover ferocity" would be overreading it,
so the number is stated here rather than left to be inferred.

## Verification

```powershell
PS> python -B -m unittest test_density_pressure   # (from labs/cubff_transducer)
ModuleNotFoundError: No module named 'cubff_transducer'... CUBFF_DENSITY_WEIGHT   # RED
# after the rider at both parity sites:
Ran 15 tests ... OK
PS> python -B -m unittest discover -s labs/cubff_transducer -p "test_*.py"
Ran 58 tests ... OK            # the DR 0020 parity pins unmodified
PS> python -B -m unittest discover -s labs/runtime_integration -p "test_*.py"
Ran 65 tests ... OK
PS> python -B -m unittest discover -s packages/mecha_engine/tests -p "test_*.py"
Ran 295 tests ... OK           # the seam is byte-identical when off
PS> uv run python -B -m unittest discover -s game/tests -p "test_*.py"
Ran 183 tests ... OK           # 174 + the 9 L5 consumer pins
PS> uv run python -B game/evidence.py
PS> git status --short data/game_client/
?? data/game_client/density_pressure_stage0.json
# G3: all SIXTEEN prior artifacts byte-identical; the new one joins as the seventeenth
```

## HONEST REMAINDER

1. **Direction, not magnitude.** 2.4% of the ground truth's gap. The
   callback path stays the richer weather wherever it is available; the
   checkpoint rider is the correction available to a player who has no
   WSL export path.
2. **The rider is OFF by default in the engine.** This record adopts
   the *capability* and proves it at the consumer; which forecast keys
   turn it on in a shipped client is a client decision, and the game's
   era bench is unchanged by this slice.
3. **Three callback states from one run** remains the ground truth's
   honest scale (the I3 remainder, unchanged). G2 is a direction
   agreement on a small corpus, not a distributional claim.
4. **The weight is pre-registered, not optimised.** 0.5 was fixed in
   advance and never revisited. Whether some other weight serves the
   game better is a question that would need its own record — and would
   have to explain why it is not curve-fitting to a wanted feel.
5. **`lineage_churn` stays BLOCKED-UPSTREAM.** Density is its own named
   channel and synthesizes nothing; DR 0043 clause 3 is untouched.

## Sources

- `audits/TODO.md` (cycle 22 L5) · `research/decision_records/0045-density-as-pressure.md` (the charter + measured verdict) · `0043-callback-forecast-adoption.md` (clause 2 — the record this closes), `0020-cubff-pressure-runtime-promotion.md` (the promoted pressure math), `0021-game-loop.md` (the seam law), `0038-vocabulary-complete-generation-alphabet.md` (the rider pattern)
- `research/experiment_reports/2026-07-20-real-weather-harshness.md` (I3 — the inversion and the callback ground truth), `2026-07-20-structured-decoder.md` (J4 — the density instrument), `2026-07-21-callback-forecast.md` (K4 — density on the game's own forecasts)
- `labs/cubff_transducer/cubff_transducer.py` (the authority) + `packages/mecha_engine/src/mecha_engine/runtime/_cubff.py` (the mirror) + `evolve.py` (`_cubff_generation_pressure`) + `labs/cubff_transducer/test_density_pressure.py` (15 pins) + `test_package_cubff_parity.py` (the drift guard)
- `labs/cubff_transducer/structured_decoder.py` (`INSTRUCTION_TOKENS` — the ten bytes, mirrored verbatim, never imported across the boundary)
- `game/evidence.py` (`build_density_pressure_report`) + `game/tests/test_density_pressure.py` (9 pins) + `data/game_client/density_pressure_stage0.json`
