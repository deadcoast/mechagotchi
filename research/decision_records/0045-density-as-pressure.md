# Decision Record 0045: Density as Pressure — the Counterweight the Checkpoint Format Can Carry

Date: 2026-07-26

## Status

**Accepted and ADOPTED on the measured verdict** (cycle 22 · Phase L ·
L5). The gates below were pre-registered BEFORE the run; the "Measured
verdict" section was filled only from the committed artifact
(`data/game_client/density_pressure_stage0.json`).
This is DR 0043 clause 2's named future record: *"whether density
should FEED the pressure math — giving the checkpoint forecast
measured-biology harshness without the callback path — is the named
future record."* Refusal is first-class; a rider that fails its gates
is reverted and recorded, never tuned until it passes.

## Context

### The defect, and its exact mechanism

I3 measured, through the untouched checkpoint seam, that **real
post-takeover soup produces MILDER weather than early-phase soup**
(mean multiplier 0.784 vs 0.818). That is backwards from the biology:
the same runs measure 2 replicating programs of 131,072 early against
**129,211 (98.6%) post-takeover**. The soup the player meets as
"mature, teeming, replicator-dominated" arrives as the *gentler* era.

The mechanism is not a mystery and is not a bug in anyone's arithmetic.
The promoted pressure math is:

```text
mutation_pressure = 0.45·instability + 0.35·semantic_pressure
                    + 0.20·instruction_diversity

instability       = 0.45·entropy + 0.30·lineage_churn
                    + 0.25·(1 − replication_dominance)
semantic_pressure = 0.50·replication_rate + 0.25·motif_repetition
                    + 0.25·lineage_churn
```

On the **checkpoint** path `replication_scores` and `lineage_events`
are structurally absent — the format cannot carry them (I3; DR 0043
clause 3 dispositioned `lineage_churn` BLOCKED-UPSTREAM). With those
terms at zero, pressure is driven almost entirely by **entropy** and
**instruction diversity** — and *both of those FALL as a soup
organizes*. So the engine reads organization as calm. Every channel it
can see decreases while every channel that would rise is missing.

This is an engine-truth problem of the sharpest kind: no number is
invented, and the player is still shown the opposite of the biology.

### Why instruction density is the right counterweight

J4 built, and K4 landed on the game's own forecasts, a brotli-free
instruction-density instrument over the ten `bff_noheads` instruction
bytes. Measured on the committed corpora:

| Source | Phase | Mean density | vs chance |
| --- | --- | --- | --- |
| checkpoint (`real`) | early | 6.92 | 2.8× |
| checkpoint (`real`) | post-takeover | 11.5 | 4.6× |

**Density is the one channel the checkpoint format carries that RISES
as the soup organizes.** It is therefore not a tuning knob bolted onto
the formula; it is the specific missing counterweight to the entropy
terms, and it is available on exactly the path whose harshness channels
are silent.

It also has a **known random expectation**, which makes it dimensionless
without any calibration: a uniformly random tape of length *n* contains
`n × 10/256` instruction bytes. So

```text
organization_ratio = instruction_density / (n × 10/256)
```

is 1.0 for random soup, 2.8 for early, 4.6 for post-takeover — a
measured *departure from randomness*, which is an ALife quantity, not a
game-balance constant.

## Decision

Add an **additive, off-by-default density rider** to the CuBFF pressure
math at BOTH parity sites (the `cubff_transducer` lab authority and its
`runtime/_cubff.py` package mirror), following the DR 0038 rider
pattern exactly: keyword-only, byte-identical when off, mirrored
verbatim, parity-pinned.

1. `extract_cubff_features(snapshot, *, include_density=False)` gains
   `instruction_density`, `density_expectation`, `organization_ratio`
   and `organization_signal` **only when asked**. Off, the returned
   feature dict is unchanged.
2. `features_to_traits(features, *, density_weight=0.0)` computes
   `mutation_pressure = clamp(base + density_weight ×
   organization_signal)`. At weight 0.0 it is the incumbent formula
   exactly.
3. `evolve(..., cubff_density_pressure=False)` threads the rider. The
   game's forecast keys are unchanged; nothing about which records a
   forecast serves moves.

### The signal, derived rather than tuned

```text
organization_signal = clamp( (organization_ratio − 1) / (CEILING − 1) )
CEILING = 256 / 10 = 25.6
```

`CEILING` is the **theoretical maximum**: a tape whose every byte is an
instruction has density *n*, hence ratio `n / (n × 10/256) = 256/10`.
Note this is **independent of tape length** — the ceiling is a property
of the language's alphabet, not of the corpus. It is therefore derived
from `bff_noheads` itself and is **not calibrated on the outcome**,
which is what keeps this gate honest.

`CUBFF_DENSITY_WEIGHT = 0.5` is pre-registered: density may contribute
at most 0.5 to a pressure in [0,1] — enough to matter, never enough to
dominate the three incumbent terms.

### The prediction this makes, stated before the run

On the committed corpora the signal is `(2.768−1)/24.6 = 0.0719` early
and `(4.6−1)/24.6 = 0.1463` post-takeover; at weight 0.5 that is a
pressure difference of ≈ 0.037, or ≈ 0.041 in multiplier terms after
the 1.1 gain. I3's inversion is 0.034 in the wrong direction. **The
rider is therefore predicted to just barely flip it — and it may not.**
That is a genuinely uncertain, falsifiable prediction, and no weight
will be adjusted to rescue it.

## Pre-registered gates

- **G1 — the inversion is corrected.** Under the rider, the committed
  checkpoint corpus's post-takeover records must produce a **strictly
  higher** mean dropout multiplier than its early records. This is the
  whole point; failing it refuses the rider.
- **G2 — agreement with the ground truth.** The callback path (key 5)
  lit the real replication channel and is the closest thing to truth
  the project has. The density-fed checkpoint ordering must **agree in
  direction** with the callback path's measured ordering.
- **G3 — the seam law.** Off, everything is byte-identical: the
  incumbent feature dict, the incumbent multipliers on every existing
  forecast, the parity pins, and all sixteen committed game evidence
  artifacts.
- **G4 — no smuggling.** Density enters as its **own named channel**.
  It must NOT be used to synthesize `replication_rate` or
  `lineage_churn`; those stay honestly zero on the checkpoint path, and
  DR 0043 clause 3's disposition is untouched.
- **G5 — bounded.** The documented multiplier band `(0.5, 1.6)` still
  clamps every result; the rider cannot push pressure outside the
  engine's recorded range.

Any refused gate is a first-class finding: the rider is reverted or
narrowed, and the measurement stands as the record.

## Measured verdict: ADOPT

| | early | post-takeover | gap |
| --- | --- | --- | --- |
| checkpoint, rider OFF | 0.818009 | 0.783716 | **−0.034293** |
| checkpoint, rider ON | 0.857880 | 0.864204 | **+0.006324** |
| callback (lit channel) | 0.772726 | 1.034884 | +0.262158 |

- **G1 MET** — the inversion is corrected: −0.034293 → **+0.006324**.
- **G2 MET** — the callback ground truth reads `post_takeover_harsher`;
  the density-fed checkpoint ordering now agrees.
- **G3 MET** — all sixteen committed game evidence artifacts regenerate
  **byte-identical**; the transducer, runtime and package suites pass
  unmodified with the rider off.
- **G4 MET** — `replication_rate` and `lineage_churn` stay 0 on every
  checkpoint record with the rider ON (pinned at both sites).
- **G5 MET** — every multiplier stays inside `(0.5, 1.6)`.

**The pre-registered prediction was right to four decimal places.** The
Decision section predicted a ≈ +0.041 multiplier swing before any run;
the measured swing is −0.034293 → +0.006324 = **+0.040617**. The
derivation — a ceiling from the language's alphabet, a weight fixed at
0.5 — produced the observed magnitude without a single adjustment.

**And the honest limit, stated with the win**: the corrected gap is
**+0.0063 against the ground truth's +0.2622 — about 2.4% of the
magnitude**. Density recovers the DIRECTION of the biology, not its
force. The checkpoint forecast now points the right way; it is still a
much quieter instrument than the lit-channel callback path, and the
margin is thin enough that it is a correction, not a dramatization.

## Consequences

If the gates pass, the checkpoint forecast — the one a player actually
has, with no WSL export path — carries harshness that tracks measured
biology, and the era a Keeper meets as "teeming" finally arrives as the
harsher one. The callback path stays the richer truth where it is
available.

If they fail, the honest result is that **density carries the right
direction but not the magnitude** to overcome the format's blindness,
and the checkpoint forecast's mildness stands as a recorded property of
what a checkpoint can carry — which is itself a finding about the
upstream format, not about the game.

Either way the incumbent stays runnable and byte-identical, and nothing
is tuned after the fact.

## Sources

- `research/decision_records/0043-callback-forecast-adoption.md` (clause 2 — the named record this charters), `0020-cubff-pressure-runtime-promotion.md` (the promoted pressure math), `0021-game-loop.md` (the seam law), `0038-vocabulary-complete-generation-alphabet.md` (the rider pattern)
- `research/experiment_reports/2026-07-20-real-weather-harshness.md` (I3 — the inversion and the callback ground truth), `2026-07-20-structured-decoder.md` (J4 — the density instrument), `2026-07-21-callback-forecast.md` (K4 — density on the game's own forecasts)
- `labs/cubff_transducer/cubff_transducer.py` (the authority) + `packages/mecha_engine/src/mecha_engine/runtime/_cubff.py` (the mirror) + `labs/cubff_transducer/test_package_cubff_parity.py` (the drift guard)
- `labs/cubff_transducer/structured_decoder.py` (`INSTRUCTION_TOKENS` — the ten bytes, mirrored verbatim never imported across the boundary)
- `data/game_client/real_weather_harshness_stage0.json`, `data/game_client/forecast_density_stage0.json`
