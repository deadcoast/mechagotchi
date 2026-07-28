# ONBOARDING.md — start here, next session

Written **2026-07-21** by the outgoing session, completed
**2026-07-26** at the owner's direction, and its §3/§4 state sections
refreshed at the **Phase-M gate (2026-07-27)**. Read this file
completely before touching anything.

`CHANGELOG.md` in the root is the cycle-by-cycle summary of what
shipped; it is derived from the gate reports, and where they disagree
the gate report wins.

**How to trust this file:** §1 (the frame), §2 (owner rulings), §6 (the
format), and §7 (honesty norms) are *durable* — they are owner rulings
and established discipline; they do not expire. §3 (state) and §4
(what's next) are a **snapshot** — re-verify them against `git log`,
`audits/TODO.md`, and the gate artifacts before relying on them.

**The orienting files at the repo root**, and what each is for:

| file | what it is |
| --- | --- |
| `ONBOARDING.md` | **this file** — start here |
| `README.md` | what the project *is*, and the anti-drift identity constraint |
| `CLAUDE.md` | the agent operating brief (commands, architecture, conventions) |
| `CHANGELOG.md` | cycle-by-cycle summary, derived from the gate reports |
| `_MOC_.md` | map of contents across the documentation |
| `TOOLS.md` | the tooling notes |
| `audits/TODO.md` | **the live cycle queue** — the actual work list |

*Corrected 2026-07-27*: earlier versions of this file pointed at
`FABLE5.md` and `AGENTS.md` as live references. **Both now live under
`.depreciated/`** (`v0.0.1/FABLE5.md`, `AGENTS.md`) — the owner's
personal archive, which §2 says to ignore unless explicitly linked. Do
not go looking for them at the root. `docs/agent-standards.md` still
exists and is an older orientation doc, largely superseded.

Where anything conflicts: **this file and the decision records win.**

---

## 1. THE FRAME — we are building TWO things

The owner has had to repeat this to the point of exhaustion. Do not
make them say it again.

1. **THE ENGINE** — the *Mechagotchi Computational Life Engine*.
   Grid genomes, generation, validation, lifecycle, repair, evolution
   archives, micro-learning threads, SLIP interpretation, the render
   bridge. Lives in `packages/mecha_engine` (ten promoted modules) and
   is proven through `labs/` + `research/` + `data/`. Inspired by the
   CuBFF study behind *Computational Life: How Well-formed,
   Self-replicating Programs Emerge from Simple Interaction*
   (arXiv:2406.19108; local copy `assets/pdf/2406.19108v2.pdf`).
2. **THE GAME** — *"Eras of the Soup"* (DR 0021): a Keeper stewards a
   bloodline through eras of a computational-life soup. It is a
   **separate build with its own playable front end** — a client a
   player launches and plays. It lives at `game/` (pygame-ce, DR 0033)
   and its MVP ladder 0.1 → 0.2 → 0.3 is built and gated.

They sell each other, so both must be high quality and creative or
neither matters. **The engine is built before the game.** The
`workshop/` (authoring layer) and the `mechas` CLI (`tools/`) are
**supporting surfaces — never the application.**

### Why we build it this way

The defining property of this repo: **the documentation is the
deliverable AND the governance.** Roughly 300k words of research
documents define the scope; the code is the part of it that has been
proven so far. Nothing is claimed without executable evidence; nothing
is promoted without passing a documented gate. This exists because the
project's one real failure mode is *drift* — a session working from
memory or momentum instead of the repo's own documents, overdeveloping
whatever is under its cursor, and calling a fraction "the application."

**The anti-periscope rule:** before deepening any feature, ask — does
the bigger picture need MORE of this, or am I periscoping? Every cycle
plan names its build track (ENGINE / GAME / SHARED) and its phase.

**The engine-truth law (DR 0021, first law):** everything any surface
shows a player is engine truth — a report field, an artifact, or a
recorded replay. No invented numbers. Uncalibrated things are shown as
uncalibrated.

**The North Star (DR 0017):** the ENGINE+GAME duality — deep
integrations over breadth. The manual rating system is a FALLBACK,
never a blocker.

---

## 2. Owner rulings that are LAW (do not re-litigate, do not undo)

- **Never declare the project "complete," "finished," or the queue
  "empty."** A prior session did this twice, measuring against its own
  invented queues instead of the documentation. The documentation
  defines the scope; the implementation is a fraction of it.
- **When a queue exhausts, THE DEVELOPER plans the next cycle** from
  the still-unmet documentation and keeps developing. **Never stop to
  ask "which direction?"** — a prior session did and was forcefully
  corrected. Asking for direction is a failure.
- **License: Apache-2.0** (DR 0028; root `LICENSE`; pyproject declares
  it; a test pins the declaration).
- **Third-party dependencies are PERMITTED** when a capability needs
  one (DR 0028), declared in the pyproject and justified in the
  feature's decision record. The old stdlib-only policy is retired —
  never present minimalism as a virtue that shrinks the documented
  scope. In practice stdlib has kept holding at every measured scale
  gate so far; that is a *measurement*, not a policy.
- **CuBFF real-export ingest was REQUIRED and is DONE** (cycle 17 G2 —
  real upstream data, built in WSL2 at the audited commit). Never
  fabricate "real" data; never resurface ingest as an open question.
- **Manual readability calibration** (browser survey via `mechas rate
  --creatures`, 0/63 rows) is deferred by owner choice. The LEARNED
  model is primary (DR 0019;
  `data/readability_benchmark/adopted_readability_model.json`); the
  rating pipeline is its fallback. **Never treat calibration as a
  blocker.**
- **`.depreciated/` is the owner's personal archive** — ignore unless
  explicitly linked.
- **Ask before publishing NEW work** (a PR nobody requested, a branch
  the owner has not seen). **Never ask to unify finished work** — at
  gate close, merge into `main` and push. Standing authorization,
  2026-07-27. Never force-push or rewrite history.
- Commit per completed task. The owner's IDE commits mid-session —
  check `git log` before committing and stage by explicit path.
  `.depreciated/audit-notes.md` is the owner's; never stage it.
- **Community infrastructure, a pack registry, and hosted
  distribution are OWNER decisions** (DR 0035), not tasks.
- Talk to the owner in **plain language**: explain what things ARE,
  not just what changed; lead with outcomes; never over-promise
  (describing 10% as if it were the vision destroyed trust once).

---

## 3. WHERE WE ARE RIGHT NOW (2026-07-27 — verify against `git log`)

### The headline

**Every documented phase A–G is COMPLETE and GATED.**
`docs/gap-analysis.md` — the roadmap that governed cycles 09–17 — is
**RETIRED per its own charter** (the Phase-G alpha gate went green
2026-07-12). It remains as the measured history of the gap and how it
closed. Since then, cycles plan from the **still-unmet documentation**
and from the named remainders each cycle's own records leave behind.

### Branch and merge state

Working branch **`phase-l-gate`** — historical name, not being renamed
(phases are already sequential, I→N). It carries cycles 22–24.

**Unified as of 2026-07-27**: `main`, `origin/main`, the branch and its
remote are all on one commit. Cycles 22 (PR #1) and 23 (PR #2) are
merged. Check with `git log --oneline origin/main..HEAD` — it should be
empty.

### The cycle ladder so far

| Cycle | Phase | What it delivered |
| --- | --- | --- |
| 01–07 | pre-phase | ontology, schemas, validators, labs, the module program (no cycle 08) |
| 09 | A | the 16×16 foundation (DR 0029/0030) |
| 10 | B | WFC generation + the real bake-off (WFC ships, DR 0031; hybrid REFUTED) |
| 11 | C | the animation system (clips, transitions 0.9877, `animstate_950`, packet contract) |
| 12 | D | the intelligence threads (fleet 11/11; ablation gates: 5 kept / 6 dropped) |
| 13 | E | evolution at documented scale (20,480 evals/run; coverage/QD/family gates) |
| 14–16 | F | the GAME client: MVP 0.1 → 0.2 → 0.3 (pygame-ce, DR 0033) |
| 17 | G | the late-stage requireds → **the public-alpha gate GREEN**; REAL CuBFF corpus ingested |
| 18 | H | workshop authoring depth |
| 19 | I | the post-takeover science |
| 20 | J | the generative range (vocabulary blindness found and cured) |
| 21 | K | the vocabulary settles its stack (gate green 2026-07-26) |
| 22 | L | the descriptor space settles its geometry — and the cycle audits its own ledger (gate green 2026-07-26) |
| 23 | M | the archive meets its own inhabitants — and the cycle audits its own **prose** (gate green 2026-07-27) |
| **24** | **N** | **the descriptor space earns its edges ← WE ARE HERE** |

Archived queues live in `audits/complete/NN/TODO.md` (01–07, 09–23).

### Cycle 21 · Phase K — CLOSED, gate green 2026-07-26

Gate report `research/experiment_reports/2026-07-26-phase-k-gate.md`;
queue archived at `audits/complete/21/TODO.md`. The vocabulary Phase J
taught the engine to spell was settled through its whole stack:
**DR 0041** implemented the 11-class regrowth head and **WITHHELD its
adoption** by its own bar (+0.0944 vs +0.10); **DR 0042** adopted the
constrained generation layer at its consumer (coverage 0.7852 →
**0.8984**); the reachability probe proved **508/512** bins with the
residue bounded by measured gaps; **DR 0043** adopted forecast key 5
(the first lit harshness channels) and dispositioned `lineage_churn`
**BLOCKED-UPSTREAM**; **DR 0044** gave the covenant's earned budget an
advisory-never-authority face in the workshop. Three of five slices
ended in a verb that was not "ship it". Full detail: the gate report
and `CHANGELOG.md`.

### Cycle 22 · Phase L — CLOSED, gate green 2026-07-26

All six tasks DONE; gate report
`research/experiment_reports/2026-07-26-phase-l-gate.md`; queue archived
at `audits/complete/22/TODO.md`. What it settled, in one line each:
**L1** corrected DR 0042 twice (the rate is 7.2% not ~22%; the refusals
are SLIP-rejected *parents*, not invalid candidates, and 100% of them
bootstrap creatures). **L2** judged the documented lineage-dominance
clause for the first time in the project's history — PASS at 0.2848,
with *four founder lines holding half the archive* reported beside the
verdict and the bar not widened to capture it. **L3** proved the
geometry is not stale and found the repo runs **two** of them, differing
by 3.7× the sampling control. **L4** let `animation_density` earn every
machine gate and still refused adoption, because the documented
criterion needs the deferred human panel. **L5** (DR 0045) corrected the
checkpoint forecast's inverted biology, with the DR's pre-run prediction
matching the measurement to four decimal places.

**The cycle's character, and the reason to trust it**: three of the five
slices corrected something the ledger already said — and **nothing was
rewritten**. Every correction is a dated note beside the original.

### Cycle 23 · Phase M — CLOSED, gate green 2026-07-27

All six tasks DONE; gate report
`research/experiment_reports/2026-07-27-phase-m-gate.md`; queue archived
at `audits/complete/23/TODO.md`. **M1** measured the archive on its own
inhabitants — `within_sampling_noise`, partly deflating the cycle's own
premise, with its lasting result methodological: measuring a control for
**both** population types caught a false positive that the cheap control
alone would have published at 5.14×. **M2** decided L3's geometry split
by measuring it in *addresses* rather than edge distance, and **refused
convergence on the measurement**: the probe recipe disagrees with itself
at another seed on 31% of the population, so the two geometries are two
draws from a noisy process, not two coordinate systems (**DR 0046**).
**M3** measured all three unbreedable-bootstrap fixes, found every one
drives the 4,435-refusal tax to zero inside the noise floor, and **still
withheld the default change** because the arms separate on quality and
archive legality in the opposite order (**DR 0047**). **M4** answered
Evolution Q3 — `common_descent`, but with the convergence half reported
beside it. **M5** was chartered to build a player-facing feature and
**built nothing**, because two of the five "missing" axes were already
on screen (**DR 0048**).

**The cycle's character, and the reason to trust it**: three of the five
slices found a claim in the repo's own **prose** was wrong — and each
was found by *reading the engine instead of the document*. Phase L
audited its own numbers; **Phase M audited its own sentences.** Every
correction is a dated note beside the original.

### Cycle 24 · Phase N — the descriptor space earns its edges

`audits/TODO.md` is the live queue: **N1 DONE, N2–N6 open.** The spine
is Phase M's deepest finding: **the octile edges are not determined by a
600-creature derivation.** `visual_complexity` re-addresses **26% of the
population** when the derivation is merely resampled, and its seven
interior edges sit inside a band about **0.046 wide** — a defect
*underneath every coverage number in the ledger*, and a question about
E1's derivation protocol rather than about which population feeds it.

*Corrected 2026-07-27 by N1 / DR 0049*: the premise is **half right, in
the half that matters least**, and "a defect underneath every coverage
number" is **overstated**. Measured as a function of derivation size,
the protocol is **`sampling_limited`, not structurally indeterminate**
(slope −0.4186 against sampling theory's −0.5, inside a measured band):
600 does not determine the *addresses* and neither does 4,800, but the
edges are under-sampled rather than unknowable. Meanwhile the
**occupied-niche count every coverage figure is counted in was already
at its measured floor at 600** — it moves exactly the floor there while
31.7% of individual creatures re-address, and at 4,800 re-addressing has
improved 2.5× while the ceiling movement is *higher*. **`derivation_count`
stays at 600**, because what raising it would fix is not what was broken.
The 26% and the 0.046 band both stand — and the band is now measured
**constant across a 64× size range**, so the measure-thinness is
structural and permanent while only the edge placement inside it is
sampled.

N1/N2 sit under everything; N4 and N5 pay debts DR 0047 and DR 0048
explicitly asked for; **N3 is deliberately non-archive** — the
micro-learner ablation conditions E/F/G, documented and unmet since
cycle 12 — because cycles 22 and 23 were both archive-heavy and the
anti-periscope rule applies to the developer too. N5 is the GAME-track
slice. See `audits/TODO.md` for each task's pre-registered shape.

### What exists and is genuinely good

- **`packages/mecha_engine`** — ten promoted modules: `genome`,
  `generation`, `lifecycle`, `archive`, `provenance`, `repair`,
  `runtime`, `learning`, `storage`, `slip`. (`render` is
  DISPOSITIONED, not promoted — DR 0026, rejected-until-consumer.)
  Each backed by contract tests and lab-side parity pins.
- **`game/`** — the playable client (pygame-ce). Companion loop, era
  bench, covenant spending, hatchery, Contribute bridge, replays,
  repertoire/lineage browsers, SLIP import/export, community packs,
  save/resume, a PyInstaller bundle. **183 tests.**
- **`workshop/`** — grid editor, SLIP creator, preview/scrubber,
  inspector, Keeper session page. **92 tests.**
- **`labs/`** — 19 research labs; every algorithm is proven here first.
  (The two that grew most in cycle 23: `map_elites_archive` 219 → **319**,
  `architecture` 14 → **27**.)
- **`research/`** — the evidence ledger: **261 experiment reports**,
  **77 algorithm cards**, **48 decision records** (through DR 0048),
  package specs.
- **`data/`** — **2,240 JSON evidence artifacts**, all valid.

**Verified at the Phase-M gate (2026-07-27):**
`python -B tools/ci/run_sweep.py` → **SWEEP GREEN** — 19 lab suites +
package 295 + workshop 92 + game 183 + CLI 23;
`data artifacts OK — 2240 JSON artifacts valid`.
(Slowest at this gate: workshop 228.8 s, runtime_integration 102.5 s,
map_elites_archive 90.3 s, cellular_automata 47.0 s.)
- Real CuBFF data is ingested; 16×16 is the proven grid scale;
  novelty-first evolution and the constrained generation layer are
  adopted; the vocabulary is ratified end to end; the checkpoint
  forecast's harshness now tracks the direction of its own biology
  (DR 0045).

### Standing named remainders (not tasks until a record charters them)

Phase M's own — the five that became cycle 24 (N1–N5) are in the queue,
not here. What stays from Phase M: the **scored candidate stream**, which
would answer L4's A3/A4 on the population the archive is filled *from*
(M1); a **size-matched TVD control** (M1); a **game-side snapshot pin**
for age and mood (M5); the documented **HIDDEN axes**, still never
surveyed per-axis; **`cleanliness`**, which needs a MECHANIC, and
**`happiness`**, which needs a DEFINITION — neither is a display gap
(M5).

Phase L's own, still standing: `animation_density`'s adoption, which
waits on the human panel (L4) — and whose **A2 independence halves on
the elites** (M1: max |r| 0.173 → 0.350), a reason for that panel to
look harder and never a machine substitute for it; the **576-vs-512
repertoire divergence**, declared by L2 and unresolved; **which forecast
keys enable the DR 0045 density rider in a shipped client** — a client
decision L5 did not make; and the honest limit that density recovers
direction, not magnitude (~2.4% of the callback path's gap).

Phase K's own, still standing: the undiluted rich-site regrowth
instrument and the unexplained 0.525 ceiling (DR 0041's re-opener); an
analytical emptiness argument for the quantization bin; richer callback
export states (a WSL run); SLIP-shaped caps only in the workshop budget
strip.
*(The ~22% generation-failure cause, the frozen derivation edges, and
density-as-pressure were promoted OUT of this list into cycle 22 as
L1/L3/L5 — all three are now closed.)*

From the documentation: **THREE of the eight documented VISIBLE
companion state axes have no engine source** (`validity-research.md`
§1.17 — `happiness`, `cleanliness`, `health`). *Corrected 2026-07-27 by
M5 / DR 0048*: the Phase-K/L survey said **five**, but `age` is a
lifecycle field (`age_ticks`) and `mood` is a derived engine value
(`select_animation_state`) — both engine truth, both already displayed
by the game. The survey had counted lifecycle *homeostasis fields*. The
three real gaps are three different kinds — no definition, no mechanic,
and a definition that would have to be CHOSEN from documented-hidden
axes — and DR 0048 built none of them. Also standing: Stage 2's
undispositioned generator arms (**shape grammar**, **CPPN**) and the
unbuilt method tracks (MRF-lite, Lenia, reaction–diffusion, the MDP
sandbox, the QDax shadow port, z3/SMT at DR 0011's WATCH); the
micro-learner ablation conditions **E/F/G** (Q-table, tiny decision
tree, Bayesian counter), never instantiated in the Phase-D fleet; the
24×24 scale-up (DR 0014's re-opener) and the unpromoted
scale-geometry seam.

Standing: the ≤45-min HUMAN first-session pass and the whole
owner-deferred human-study block (prepared-not-blocking — and the
transducer study's "preference" number is a labeled PROXY, never
human preference); per-clip choreography (an engine DR when a consumer
asks); DR 0032's re-openers (untriggered, refutation deepening); the
first green CLOUD CI run, which awaits a push never made unasked.

---

## 4. WHAT TO DO NEXT

**Work `audits/TODO.md` task by task** — RED first, triad docs in the
same change, one commit per task naming the task ID. Cycle 24's queue in
order (cycle 23's closed ladder is in §3 and its gate report):

1. **N1 · do 600 creatures determine the octile edges?** — **DONE
   2026-07-27 (DR 0049).** `sampling_limited`, not structurally
   indeterminate (slope −0.4186 vs theory's −0.5 inside a measured
   band): 600 does not determine the addresses and neither does 4,800,
   but the edges are under-sampled rather than unknowable. **The
   occupied-niche count the ledger quotes was already at its measured
   floor at 600**, so `derivation_count` stays. Measure-thinness proved
   **structural** (the band is constant across 64×) while only the edge
   placement inside it is sampled. DR 0046's two controls corrected as
   understated single draws — which **strengthens** `freeze_split`
   (ratio 1.16 → 0.969).
2. **N2 · freeze the probe's edges** — **DONE 2026-07-28 (DR 0050).**
   Frozen at 600 with recorded provenance; all four gates passed. Both
   committed headlines recomputed from scratch and came back **exact**
   (support ceiling 460 → 460, reached-by-generators 495 → 495);
   determinism **measured** rather than inherited from DR 0046's
   assertion; separation held at 0.037500 so the refusal to converge is
   intact. The recipe now lives in one place instead of three private
   copies, every probe-side artifact records `edges_source`, and a
   **parity pin makes drift fail the suite**. *Corrected*: the charter
   said "a draw no artifact records" — `reachability_probe` **does**
   record its edges; `occupancy_saturation` and
   `reachability_escalation` do not, which is worse. Honest limit:
   **freezing the edges does not freeze the numbers** — the support
   ceiling spans 447–462 across evaluation resamples.
3. **N3 · the micro-learner ablation conditions E/F/G** ← **THE NEXT
   TASK.** Documented and unmet since **cycle 12**, and deliberately
   this cycle's
   **non-archive** ENGINE slice after two archive-heavy cycles (the
   anti-periscope rule applies to the developer too). Build Q-table,
   tiny decision tree and Bayesian counter; run the D6 ablation gates
   **verbatim**; let the measured rule keep or drop each. Dropping all
   three is first-class; a drop that changes the kept-five roster would
   be a real result.
4. **N4 · the `slip_admission` default, decided** — DR 0047's named
   decider. All three arms already drive the refusal tax to zero inside
   the noise floor, so the question is *which*, not *whether*. Re-run
   with **quality and archive legality pre-registered alongside
   coverage**, multi-seed. DR 0047 records that the likely winner is
   **`insertion`**, not the tie-break's `parents` — which is exactly
   why the gate must be written first and allowed to refuse all three.
5. **N5 · `health` — the CHOSEN definition, gated** *(GAME track)* —
   DR 0048's named next record, and the one absent visible axis with a
   real engine source. `grid_stability` and per-cell `damage` are both
   documented **HIDDEN**, so any definition is CHOSEN and must say so
   first. Gate it on more than arithmetic: whether a player-facing
   "health" that is really grid-stability is **honest labelling or a
   euphemism** is part of the decision. **Refusal is first-class.**
6. **N6 · the Phase-N gate** — then archive to `audits/complete/24/`
   and plan cycle 25 from the documentation. **Do not ask which
   direction.**

## 5. The map — what each directory IS

```text
packages/mecha_engine/   THE ENGINE (src layout, promoted modules)
game/                    THE GAME (pygame-ce client, src layout)
workshop/                authoring layer (server + HTML pages)  — support
tools/mechas_cli/        the `mechas` CLI                        — support
tools/ci/run_sweep.py    the ONE verification sweep runner
labs/                    19 research labs — algorithms proven here FIRST
research/                the evidence ledger (the deliverable)
  ├─ experiment_reports/ dated findings (YYYY-MM-DD-kebab-slug.md)
  ├─ algorithm_cards/    fixed-template cards (snake_case, same stem)
  ├─ decision_records/   ADRs, NNNN-slug.md (through 0048)
  ├─ package_specs/      contracts + the traceability matrix
  └─ README.md           THE MASTER TRACEABILITY LEDGER
data/                    JSON evidence artifacts + fixture corpora
docs/                    the vision + roadmap documents
audits/TODO.md           THE ACTIVE CYCLE QUEUE
audits/complete/NN/      archived cycles (01–07, 09–23)
CHANGELOG.md             cycle-by-cycle summary (derived from the gates)
keeper/, game/dist/      live play state / builds — GITIGNORED, not evidence
```

**Boundary law (enforced by a scan):** no `sys.path` text anywhere in
`packages/` or `game/src/`. Package and game code import
`mecha_engine`, **never** `labs`. Labs *may* import the package — that
is exactly how parity pins work. The workshop may import both. Private
files are **mirrored verbatim, never imported across boundaries**, and
a lab-side parity test pins the mirror so drift fails the suite.

### The working vocabulary (you will meet these constantly)

`research/glossary.md` defines the companion-domain terms. These are
the *working* terms the reports, commit messages, and artifacts use —
they are not written down elsewhere:

- **SLIP** — Synthetic Learning Intelligence Profile: the user-authored
  constraint profile (palettes, mass bounds, organ roles, mutation
  caps, behavior weights, visual grammar) that governs generation and
  behavior. The *covenant* is the game's name for the player's SLIP.
- **The covenant / unlock facts / spending** — the game earns
  falsifiable "unlock facts" from eras and *spends* them to widen the
  covenant (thinking depth, palette, population). `apply_covenant_change`
  is the only spender.
- **Era / the Keeper** — one era = one `evolve` run under a weather
  forecast; the Keeper is the player, stewarding a bloodline across
  eras.
- **Niches / elites / coverage / QD** — MAP-Elites vocabulary. The
  descriptor space is binned (the 8×8×8 = 512-bin octile geometry);
  an *elite* is the best creature in a bin; *coverage* is the fraction
  of bins occupied; *QD* is quality-diversity (summed elite fitness).
- **Seam** — an additive extension point. The law: a new seam is
  **byte-identical when off**, proven by test, never a rewrite.
- **Parity pin** — a lab-side test asserting the promoted package
  reproduces lab semantics *verbatim* (error strings included). Private
  files are **mirrored, never imported** across boundaries; the pin is
  what makes drift fail the suite.
- **stage0 artifact** — a `data/<lab>/<slug>_stage0.json` evidence
  file. "Stage 0" is the evidence maturity level, not a version.
- **Gate / pre-registered gate / `withhold_adoption`** — a decision
  rule written down *before* the run, with adopt / withhold / refuse
  all first-class outcomes.
- **The fleet / threads** — the 11 micro-learner threads (cycle 12);
  five were kept by the D6 ablation, six dropped.
- **The soup / takeover / post-takeover** — CuBFF terms: the soup is
  the population of interacting programs; *takeover* is the moment
  self-replicators dominate. Early-phase soup behaves very differently
  from post-takeover soup, and reports are careful about which they
  measured.
- **Weather / harshness / forecast keys** — the game's environmental
  pressure, sourced from real CuBFF records; forecast keys 1–5 select
  the source in the client.
- **The triad** — report + card + code + artifact for one finding.
- **Engine truth** — DR 0021's first law (see §1).

### The documents that define the application

1. `docs/project-research/validity-research.md` — the founding vision
   and the MVP ladder (§1.34 names the first target).
2. `docs/project-research/deep-research/01/deep-research.md` — the
   research dossier: scale figures, thresholds, stages, the method
   matrices, the ablation protocols. (Two concatenated reports; both
   matter.)
3. `docs/project-research/research.md` — the research plan.
4. `docs/gap-analysis.md` — RETIRED but the measured history.
5. `research/decision_records/` — 0017 (North Star), 0021 (the game),
   0028 (license/deps), 0029 (size-parametric), 0031/0042 (generation),
   0032, 0033 (pygame-ce), 0035 (community = owner), 0038–0048
   (recent; 0046 the geometry split + its comparability rule, 0047 the
   SLIP-admission arms, 0048 the visible companion axes — cycle 23's
   three new records).
6. `research/README.md` — the traceability ledger.
7. `docs/alpha.md` — the public-alpha packet.
8. `CHANGELOG.md` — the cycle-by-cycle summary, derived from the gates.

---

## 6. THE FORMAT we develop in (non-negotiable)

### The triad convention

Every finding exists as linked files sharing one slug:

```text
research/experiment_reports/2026-07-21-covenant-budget-face.md   ← dated report
research/algorithm_cards/<same_stem>.md                          ← card (when an algorithm)
labs/<lab>/<module>.py  (+ test_<module>.py)                     ← code
data/<lab>/<slug>_stage0.json                                    ← evidence
```

…all registered in `research/README.md`. **Every code or data change
updates its documents in the SAME change.** Every research document
ends with a `## Sources` footer of relative repo paths.

### Experiment reports

WHY / WHAT / FINDINGS / **Verification** / Sources. The verification
block contains the exact PowerShell commands with **pasted real
output** — the RED run that failed, the GREEN run that passed, and the
lab invocation that produced the artifact.

### Artifacts

Every `*_stage0.json` carries `artifact_id`, `status`, `date`,
`purpose`, `source_artifacts`, metrics, `closed_states`,
`blocked_states`, `decision`, `next_research_step`. **Keep blocked
states explicit — never silently drop an unproven surface.** Paths in
artifacts are repo-relative POSIX strings, never absolute.

### The lab module pattern

`foo.py` + sibling `test_foo.py`, flat imports, `ROOT =
Path(__file__).resolve().parents[2]`, a `build_*_report()` returning
the report dict, a `write_*_artifacts(output_dir, report)`, and an
`if __name__ == "__main__":` main with argparse defaults into `data/`.
Modern union syntax, frozen dataclasses, explicit annotations,
deterministic tests using `tempfile.TemporaryDirectory`.

### The gate discipline (the strongest recent norm)

**PRE-REGISTER the decision rule in the module BEFORE the run.** Write
the gates, the bars, and the adopt/withhold verbs *first*; then run;
then record whatever the numbers say. Nothing is re-scored after the
fact. K1 refused its own adoption at +0.0944 vs a +0.10 bar and that
refusal shipped as the finding. **A gate that cannot fail is a bug.**

New engine seams are **additive and byte-identical when off** —
proven, not asserted. Adoption never deletes the incumbent: it stays
runnable and parity-pinned.

### The cycle rule

Work `audits/TODO.md` task by task; one commit per completed task
naming the task ID, the evidence, and the doc updates. A cycle ends
only when the queue is exhausted AND a full sweep is green — then
archive to `audits/complete/NN/` and plan the next cycle from the
documentation and the recorded remainders.

### The branch and merge rule

**At gate close: merge into `main`, push, bring the branch level with
`main`.** Do not ask. Do not continue on a branch while its PR is open —
the merge takes a snapshot and everything after it is stranded again.

`git log --oneline origin/main..HEAD` must be empty when you stop.

### External code review runs on every PR

Five bots review PRs here (CodeRabbit, Copilot, qodo, Codex, Sourcery;
`.coderabbit.yaml` configures the first). **Triage their findings, do
not implement them on sight** — treat this exactly like the
receiving-review discipline in §7:

- **Verify before complying.** Cycle 23's review produced seven
  findings: four real (a genuine byte-identity contract break, stale
  composition metadata, a non-portable subprocess probe, an abbreviated
  sweep block), one worth recording, and **three that were simply
  wrong** — each disproved in a single command (`parents[1]` and
  `parents[2]` resolve to the *same path*; 219 of 219 artifacts use
  underscore slugs; 0 of 545 test methods carry `-> None`).
- **Repo convention beats a generic rule.** A "fix" that would make your
  files the only inconsistent ones in the tree is not a fix.
- **When review catches a wrong claim in a shipped report, add a dated
  note** — the same law as any other correction. Do not silently edit
  the sentence into being true.

---

## 7. Honesty norms (learned the hard way; enforced)

- **Negative results and refuted hypotheses are first-class
  findings.** The refuted record is a real, valued part of this repo.
  A refusal that carries its own measured mechanism is worth more than
  a pass.
- **Gates derive from evidence, never constants.**
- **Record process deviations, don't hide them.** K3 recorded that it
  ran implementation-first, inverting RED-first. K2 recorded that a
  draft briefly carried invented numbers, caught and stripped before
  the artifact existed. Do this.
- **Never fabricate data**, and never present a proxy as the real
  thing. When a channel is silent upstream, pin the silence honestly
  (`lineage_events: []`) and name the re-openers.
- **Beware the statistic, not just the data** — reconstruct the
  engine's exact statistic before comparing outcomes (a survivorship
  bias once ranked the switchboard dead last).
- **A faithful replay reproduces the INPUTS exactly**
  (`founder_grids=None` ≠ `[]` — a real DR 0016 distinction).
- **Never pin environment observations in tests**; assert the policy,
  record availability as a per-run observation.
- **Regenerate artifacts you invalidate** and explain every delta.
  Never let a live surface overwrite committed evidence.

---

## 8. Commands and environment

```powershell
# The FULL sweep — every lab, package, workshop, CLI, game + JSON validation
python -B tools/ci/run_sweep.py            # --quick skips the ~2-min workshop suite

# Individual suites
python -B -m unittest discover -s labs/<lab> -p "test_*.py"
python -B -m unittest discover -s packages/mecha_engine/tests -p "test_*.py"
python -B -m unittest discover -s workshop/tests -p "test_*.py"
uv run python -B -m unittest discover -s game/tests -p "test_*.py"

# Gates and validation
python -B labs/package_promotion/package_promotion_gate.py
python -m json.tool data/<path>.json

# Play surfaces
uv run python -B game/run_game.py [--ticks N]
mechas session --open
```

- **Always `python -B`** (tree hygiene — tracked bytecode was a real
  past hazard).
- **Run labs with the system `python -B`, not `uv run`** —
  `workshop_editor`'s foreign-fixture byte pins are zlib-BUILD
  sensitive (system 3.14 uses zlib-ng; uv's 3.13 uses classic zlib and
  fails 10 of them; DR 0034 made those pins conditional). The uv venv
  is for the dependency-group suites: `uv sync --group lab --group cli
  --group game` (syncing one group alone EVICTS the others).
- Git: LF→CRLF warnings are normal noise. Commit messages end with the
  co-author line.

---

## 9. Traps that have bitten before

- **The 64-char `grid_id` cap** — reassign ids per cycle; never
  accumulate suffixes. This has bitten TWICE (once a study harness
  measured its own bug as biology).
- **Lifecycle bistability** — stress ≤0.94 stabilizes, ≥0.95 collapses
  around tick 12–14; idle creatures starve by ~tick 11. Mind
  survivorship bias in any per-tick aggregate.
- **`deliberation.max_ticks` has an authority floor of 2.**
- **Rung-conditional keys exist only when their feature ran** —
  `None` ≠ `[]` ≠ absent.
- **"Byte-identical when off" means identical to what the surface
  returned BEFORE the seam existed** — not merely identical between two
  calls to the new code. A test comparing new-to-new cannot catch a key
  both calls gained; **pin the off-mode key set against a frozen list**.
  Cycle 23's M3 shipped this bug and external review caught it.
- **A verdict must agree with the number it publishes.** At a gate
  boundary, `(0.5 - 0.4) / 0.05` evaluates to `1.9999999999999996` but
  *reports* as `2.0` — judge on the **rounded** value, or the artifact
  says "z = 2.0, refused". That is float representation, not science.
- **Subprocess probes: inherit the environment, never replace it.**
  Follow `mecha_engine_scaffold_verification_gate._import_probe_env` —
  copy `os.environ`, *extend* `PYTHONPATH`, and set a timeout. A
  hand-built two-key env drops `PATH`/virtualenv vars and hard-codes a
  platform.
- **`ROOT` may be written two equivalent ways.** `Path(__file__).
  resolve().parents[2]` and `LAB_DIR.parents[1]` (where `LAB_DIR` is the
  module's own directory) resolve to the **same** repo root; the archive
  lab uses the second throughout. Reviewers have flagged the second as a
  violation — it is not. Verify before "fixing".
- **Complex one-liners fail PowerShell parsing** — write a script file
  to the scratchpad instead. The Bash tool's `cd` persists between
  calls; prefer absolute paths.
- **Servers must bind port 0** (OS-reserved ranges shift).
- Two `data/slips` pydantic-version observation artifacts get rewritten
  by `slip_validator` sweeps — `git checkout` them, never commit.

---

## 10. First moves for a fresh session

1. `git log --oneline -10` and `git status --short` — what happened, and
   is anything uncommitted? **The owner's IDE commits mid-session**, so
   never assume the tree is yours; check before committing and stage by
   explicit path. Expect `.depreciated/audit-notes.md` to be dirty; that
   is the owner's file — **never stage it**.
2. `git log --oneline origin/main..HEAD` — **is anything stranded off
   `main`?** If that list is longer than the cycle you are about to
   work, a previous cycle was never merged back (see §6, the branch and
   merge rule). Fix that before adding to the pile.
3. Read `audits/TODO.md` — the live queue and its standing note.
4. `python -B tools/ci/run_sweep.py --quick` — confirm the tree is
   green before changing anything. **~5 min**; the full sweep is ~9 min
   and is required before any commit that closes a task.
5. Read the most recent experiment reports in
   `research/experiment_reports/` (`2026-07-27-*`) for the immediate
   context, starting with `2026-07-27-phase-m-gate.md`. `CHANGELOG.md`
   is the faster orientation if you only need the shape.
6. Then work the queue — task by task, RED first, triad docs in the
   same change, one commit per task. When the queue exhausts, plan the
   next cycle yourself from the documentation.

### What a task actually looks like, start to finish

Every cycle-23 slice ran this loop; copy it:

1. **Read the charter** — the task's own bullet in `audits/TODO.md`, and
   the reports it names. They tell you what is already measured.
2. **Write the pins FIRST** (`test_<module>.py`) and run them — you want
   `ModuleNotFoundError`. That is the RED, and it goes in the report.
3. **Pre-register the rule IN the module docstring** — the statistic,
   the bar (derived from measured evidence, never a constant), and the
   adopt/withhold/refuse verbs. *Then* run. A gate that cannot fail is
   a bug.
4. **Implement**, get the pins green, run the whole lab suite.
5. **Run the study**, at documented budget. Long runs go in the
   background; derive the wall-clock bound from the incumbent's
   (DR 0028) rather than picking one.
6. **Write the triad in the same change** — experiment report (WHY /
   WHAT / FINDINGS / Verification with pasted output / Sources),
   algorithm-card entry, `research/README.md` ledger entry, and a DR if
   anything was adopted, withheld or refused.
7. **Report what the numbers say**, including against your own
   expectations. Three cycle-23 slices contradicted their own charter,
   and that was the value.
8. **Full sweep**, `git checkout` the two `data/slips` observation
   artifacts, stage by explicit path, one commit naming the task ID.

## Sources

- `audits/TODO.md` (cycle 24 · Phase N), `audits/complete/*/TODO.md`
- `CHANGELOG.md` (the cycle-by-cycle summary)
- `CLAUDE.md`, `README.md`, `_MOC_.md`, `docs/agent-standards.md`  
  (`FABLE5.md` and `AGENTS.md` are now under `.depreciated/` — archived)
- `docs/gap-analysis.md` (retired; the measured history)
- `docs/project-research/` (the vision documents)
- `research/README.md` (the master ledger)
- `research/decision_records/0017`, `0021`, `0026`–`0048`
- `research/experiment_reports/2026-07-12-phase-g-gate.md`,
  `2026-07-20-phase-j-gate.md`, `2026-07-26-phase-k-gate.md`,
  `2026-07-26-phase-l-gate.md`,
  `2026-07-27-phase-m-gate.md` (the gate that refreshed §3/§4),
  `2026-07-27-*.md` (the M1–M5 science)
- `tools/ci/run_sweep.py`
