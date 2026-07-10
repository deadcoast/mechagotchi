# Development TODO — Cycle 14: GAME track · Phase F — the playable game (MVP 0.1)

**Build track: THE GAME** (of the two builds — engine and game — per
`docs/gap-analysis.md` §0). The ENGINE track (Phases A–E) is COMPLETE
with green gates. This cycle begins the build the engine exists to
showcase: a REAL user front end — a client a player launches and plays.
The dev-served workshop HTML pages are NOT this front end (standing
identity constraint). The Keeper/era design (DR 0021) and the companion
loop are DESIGN INPUTS, not implementations.

Source: `docs/gap-analysis.md` (Phase F), opened by the Phase-E gate
(`research/experiment_reports/2026-07-09-phase-e-gate.md`, cycle 13).
The MVP ladder (validity-research §1.21–1.34) is climbed as PRODUCT
releases; MVP 0.1 is this cycle's rung: *"A 16×16 monochrome grid
creature that is generated from a genome, has hunger/energy/mood/age,
changes expression by state, logs interactions, mutates after death,
produces a child using parent traits, saves a lineage file. This
proves the entire thesis."* Named engine seams this cycle finally
consumes: the render-packet animation/effects/ui_hints contract
(Phase C), the kept fleet's game-side value — beg timing, ui_hints,
clip choice, mood display (Phase D), and the evolution repertoire —
species memory surfacing to the player (Phase E).

- [ ] **F1 · The front-end technology decision record + the client
  skeleton.** Evaluate the documented bridge targets (web / Godot /
  terminal / Pygame / desktop; TS+React is the documented workshop
  scale-path) against the engine's REAL contract (JSON render packets,
  retro effects, deterministic replays, installable releases with save
  files); choose by decision record with justification; deliver a
  LAUNCHABLE hello-creature client rendering a real engine packet
  end-to-end. RED-first where testable; triad on the game side too.
- [ ] **F2 · The companion loop as a product (MVP 0.1).** The
  launchable client runs the documented loop: a 16×16 creature
  generated from a genome; hunger/energy/mood/age VISIBLE; expression
  changes by state; interactions logged; death → mutation → child
  carrying parent traits; a lineage file saved. Engine-truth law
  (DR 0021 first law): every displayed number is a report field, an
  artifact, or a recorded replay — uncalibrated things shown as
  uncalibrated.
- [ ] **F3 · The render bridge consumed in full.** Live clip DRIVING
  through the animation graph (the named Phase-C remainder); the retro
  effects pipeline (scanline, lcd_ghosting, crt_bloom, glitch);
  ui_hints (need icons, attention ping). The kept fleet cashes out
  here: beg timing, clip choice, mood display through the D6-kept
  threads' confidences.
- [ ] **F4 · The Keeper/era loop.** DR 0021's design as input: save
  files, sessions, era progression; the evolution repertoire surfaces
  to the player (species memory — E5's recurrent families are the
  proven substrate). The engine archive's scale-geometry seam promotes
  HERE if this consumer demands it (the named Phase-E remainder, its
  own gated package change).
- [ ] **F5 · The installable release.** MVP 0.1 as a product: a player
  can install, launch, play, quit, and resume from a save file.
  Packaging tech justified in F1's decision record (full CI/
  reproducibility stays Phase G).
- [ ] **F6 · The Phase-F MVP 0.1 gate.** One consolidated gate report
  with the honest remainder list (including what of Phase F remains
  beyond MVP 0.1 — the ladder's 0.2/0.3 rungs decompose into the next
  cycle FROM THE GAP ANALYSIS if the phase continues); cycle 14
  archived; the gap analysis governs what opens next.

## Standing note

`docs/gap-analysis.md` governs cycle planning until retired (Phase G
alpha). The engine-truth law (DR 0021), the identity constraint, and
the triad discipline are unchanged and apply to GAME-side work. CuBFF
real ingest is REQUIRED late-stage (Phase G). Apache-2.0; dependencies
permitted with justification (DR 0028) — a game front end will need
them; justify in F1's decision record. Named remainders standing from
the engine track: DR 0032's re-openers (GA-advantage direction,
family collapse); occupancy saturation ~55% under the pure WFC parent
path (novelty pressure is a candidate with its own evidence);
behavior_neediness recalibration at 16×16; the unpromoted archive
scale-geometry seam (F4 may be its consumer); evolve's inner loop on
WFC (E2's evidence recorded; the package change waits for its
consumer); SLIP alignment in the scale harnesses; the hybrid
re-opener; limb/joint per-role motion; clip-frame exports; dropped
threads stay out of default profiles (D6).

## Sources

- `docs/gap-analysis.md` (Phase F; §0 the two builds)
- `research/experiment_reports/2026-07-09-phase-e-gate.md` (the opener)
- `research/decision_records/0021-game-loop.md` (the Keeper/era design input)
- `docs/project-research/validity-research.md` (§1.21–1.34, the MVP ladder)
- `research/decision_records/0026`, `0031`, `0032` (named re-openers)
- `data/micro_threads/ablation_gates_stage0.json` (the kept fleet)
