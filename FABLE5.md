# FABLE5.md — Onboarding for the next Fable 5 instance

Written 2026-07-08 by the outgoing Fable 5 session, at the owner's
direction, so you can pick up EXACTLY where it left off. Read this
whole file before touching anything. Re-verify state claims against
`git log` and the gate artifacts — but the FRAME in §1 and the
corrections in §2 are owner rulings, not stale state; they do not
expire.

---

## 1. THE FRAME — we are building TWO things

The owner has had to repeat this to the point of exhaustion. Do not
make them say it again.

1. **THE ENGINE** — the Mechagotchi Computational Life Engine,
   inspired by CuBFF (arXiv:2406.19108, local copy in `assets/pdf/`).
   Genome grids, generation, validation, lifecycle, repair, evolution
   archives, micro-learning threads, SLIP interpretation, the render
   bridge. Lives in `packages/mecha_engine` and is proven through
   `labs/` + `research/` + `data/`.
2. **THE GAME** — a SEPARATE build that showcases the engine, with its
   own **playable user front end**: a client a player launches and
   plays. It does NOT exist yet. The Keeper/era design (decision
   record 0021) is its *design document*, not its implementation. The
   dev-served workshop HTML pages are NOT the game's front end — a
   prior session repeatedly made that mistake.

They sell each other, so both must be high quality and creative or
neither matters. **The engine is built before the game.** The workshop
(authoring layer) and the `mechas` CLI are supporting surfaces —
never the application.

**The anti-periscope rule:** the prior session's chronic failure was
periscoping into whatever module was under its cursor, treating it as
the entire application, overdeveloping it, and losing the big picture.
Every cycle plan names its build track (ENGINE or GAME) and its phase.
Before deepening any feature ask: does the bigger picture need MORE of
this, or am I periscoping?

## 2. Owner rulings that are LAW (do not re-litigate, do not undo)

- **Never declare the project "complete," "finished," or the queue
  "empty."** The prior session did this twice, measuring against its
  own invented cycle queues instead of the documentation. The ~300k
  words of documentation define the scope; the implementation is an
  early fraction of it. `docs/gap-analysis.md` is the measured gap and
  governs all cycle planning until its Phase G alpha gate is green.
- **License: Apache-2.0** (DR 0028; root `LICENSE`; pyproject
  declares it; a test pins the declaration).
- **Third-party dependencies are PERMITTED** when a capability needs
  one (DR 0028). "We can't make everything." The old stdlib-only
  policy is retired; never present minimalism as a virtue that shrinks
  the documented scope. NumPy etc. enter where scale demands —
  justified in the feature's decision record.
- **CuBFF real-export ingest is REQUIRED, late-stage** (Phase G) — an
  additional feature, not an open question. Never resurface it as a
  decision. Synthetic weather remains the interim in-game source.
  Never fabricate "real" data.
- **Manual readability calibration** (the browser survey via
  `mechas rate --creatures`, 0/63 rows) is deferred by owner choice;
  the LEARNED readability model is primary (currently the F3
  real-mutation-augmented artifact `data/readability_benchmark/
  adopted_readability_model.json`), the rating pipeline is its
  fallback/calibration check. Never treat calibration as a blocker.
- **`.depreciated/` is the owner's personal archive** — ignore unless
  explicitly linked.
- **Never push without being asked.** Commit per completed task with
  the co-author line `Co-Authored-By: Claude Fable 5
  <noreply@anthropic.com>`.

## 3. Where we are RIGHT NOW

- **Active queue:** `audits/TODO.md` = **Cycle 09 · ENGINE track ·
  Phase A — the 16×16 foundation.** Nothing in it is started. The
  next concrete work is **A1** (see §5).
- **Governing roadmap:** `docs/gap-analysis.md` — read it in full
  before planning anything. §0 is the two-builds frame; §3 is the
  measured gap table (documented spec vs implementation); §4 is the
  phase ladder: ENGINE A–E → GAME F → shared G. Cycles decompose
  phases; when the TODO is exhausted AND confirmed complete (full
  sweep green), archive it to `audits/complete/NN/` and plan the next
  cycle FROM THE GAP ANALYSIS, never from your own momentum.
- **What exists and is genuinely good** (the owner affirms this): a
  robust `research/` evidence ledger; a comprehensive `data/` evidence
  directory (each folder = one lab's measured `*_stage0.json` outputs
  + fixture corpora; the two SCHEMAS live in `research/grid_genome/`
  and `research/slip/`); robust `labs/` python wired to
  `packages/mecha_engine` by lab-side parity pins (drift fails the
  suite — keep it that way). Ten promoted engine modules (genome,
  generation, lifecycle, archive, provenance, repair, runtime,
  learning, storage, slip; `render` dispositioned by DR 0026 with a
  named re-opener). ~1,225 tests, all green at handoff.
- **The honest limitation:** everything is proven at **8×8 grids with
  ~13-cell bodies** — below the documentation's own 16×16 primary
  target. The evolution scale (population 4, 3 generations) is ~3
  orders of magnitude under the documented regime. There is no WFC
  generation layer, no animation system (clips/frames/transitions),
  ~2 of the ~11 documented micro-learner threads, one canvas consumer
  of a partial render-bridge contract, no CI, no packaging, no
  playable game client. That is WHY Phase A exists.
- **Archived history:** cycles 01–08 under `audits/complete/`. The
  consolidated research reports live in `research/reports/` (newest:
  v1.0 — read its manifest). `docs/agent-standards.md` is an older
  onboarding doc; where it conflicts with this file or the gap
  analysis, THIS file and the gap analysis win.

## 4. The documents that define the application (read before building)

1. `docs/gap-analysis.md` — the roadmap (start here).
2. `docs/project-research/validity-research.md` — the founding vision
   + MVP ladder (§1.34 names the first implementation target: the
   16×16 creature that "proves the entire thesis").
3. `docs/project-research/deep-research/01/deep-research.md` — the
   research dossier: scale figures, thresholds, stages M0–M7 (two
   concatenated reports; both matter).
4. `docs/project-research/research.md` — the research plan (layers,
   stages, evaluation framework).
5. `research/decision_records/` 0001–0028 — ADRs; 0017 (engine+game
   duality), 0021 (the game design), 0026–0028 recent dispositions.
6. `docs/mecha-workshop/*` and `docs/cli/*` — the supporting-surface
   charters (the CLI roadmap has unshipped items: gates, test, regen,
   doctor, reviewer prefill, shell completion).
7. `research/README.md` — the master traceability ledger.

## 5. WHAT TO DO NEXT — Cycle 09, task A1

`audits/TODO.md` holds the full task text. The sequence:

- **A1 · 16×16 invariants and schema ratification.** Re-derive the
  hard/soft invariants at 16×16 EMPIRICALLY (body-mass bounds,
  connectivity, organ expectations, symmetry — the 8×8 numbers do not
  scale linearly; measure, don't assume). Ratify in
  `research/grid_genome/grid_invariants.md` + the schema (it already
  permits 8–64). Record scaling decisions in a decision record. 8×8
  stays valid input; 16×16 becomes the proven default.
- **A2** · the 16×16 seed corpus (≥50 creatures, real morphological
  variety across the DR 0015 role vocabulary — limbs, antennae,
  shells — NOT upscaled blobs) + invalid corpus + editor canvas.
- **A3** · generator/validator/repair/lifecycle re-proven at 16×16
  (size-parametric — do not break the 8×8 pins; NumPy where justified).
- **A4** · evolution + game-design surfaces at 16×16 defaults with a
  meaningfully raised session config (measure wall-clock; record it).
- **A5** · the Phase-A gate report (one consolidated experiment
  report; honest list of anything still 8×8-only and why).

Then Phase B (WFC + the real bake-off) per the gap analysis.

## 6. HOW to work here (the standing discipline)

- **Triad convention** for every finding: dated experiment report in
  `research/experiment_reports/YYYY-MM-DD-kebab-slug.md` + algorithm
  card + lab code with tests + `data/<lab>/<slug>_stage0.json` —
  ledgered in `research/README.md`, `## Sources` footers everywhere,
  RED/GREEN verification blocks with pasted output.
- **Engine truth** (DR 0021 first law): everything any surface shows
  is a report field, an artifact, or a recorded replay — no invented
  numbers. Uncalibrated things are shown as uncalibrated.
- **Verbatim parity:** package ports keep lab semantics exactly
  (error strings included), pinned by lab-side tests over full
  corpora. New engine seams are additive keywords, byte-identical when
  off. RED-first for engine changes.
- **Determinism:** no wall clock, no unseeded randomness in labs or
  engine; repo-relative POSIX path strings in artifacts.
- **Honesty norms:** negative results and refuted hypotheses are
  first-class findings; gates derive from evidence, never constants;
  reconstruct the engine's exact statistic before comparing outcomes
  (survivorship bias caught a prior analysis); a faithful replay
  reproduces INPUTS exactly (`founder_grids=None` ≠ `[]`).
- **Commands** (PowerShell, always `python -B`):
  ```powershell
  python -B -m unittest discover -s labs/<lab> -p "test_*.py"
  python -B -m unittest discover -s packages/mecha_engine/tests -p "test_*.py"
  python -B -m unittest discover -s workshop/tests -p "test_*.py"
  python -B labs/package_promotion/package_promotion_gate.py
  python -m json.tool data/<path>.json
  ```
  Full sweep (16 labs + package + workshop + CLI) before claiming a
  cycle complete. Ambient `FORCE_COLOR` breaks CLI test assertions —
  the harness pins it; keep that.
- **Traps:** 64-char `grid_id` cap (reassign per cycle, never
  accumulate suffixes — bitten twice); lifecycle bistability (stress
  ≥0.95 collapses ~tick 12–14; idle starves ~tick 11);
  `deliberation.max_ticks` authority floor is 2; ports are
  OS-reserved in shifting ranges (servers use port 0); complex
  one-liners fail PowerShell parsing — write script files to the job
  tmp dir.

## 7. How to talk to the owner

Plain language. They are reconnecting with a codebase that grew fast —
explain what things ARE, not just what changed. Lead with outcomes.
Never over-promise: describing 10% as if it were the vision destroyed
trust once already. When they correct you, the correction goes into
memory AND into the repo's planning documents in the same turn. They
are in a state of disconnect until the source code develops further
into coherence — your job is steady, honest, documented progress
through `docs/gap-analysis.md`, cycle by cycle, engine first, then the
game.

## Sources

- `docs/gap-analysis.md` (the roadmap this file serves)
- `audits/TODO.md` (cycle 09 · ENGINE · Phase A)
- `research/decision_records/0017`, `0021`, `0026`–`0028`
- owner corrections of 2026-07-07 (recorded in session memory:
  two-builds frame; scope-is-the-documentation; rating-fallback;
  `.depreciated/` scope)
- `docs/project-research/` (the vision documents, §4 above)
