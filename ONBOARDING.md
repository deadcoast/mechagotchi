<!-- Current operational snapshot: section 4 and the Phase-Q gate, 2026-10-04.
Earlier dated science and owner rulings are retained; latest direct session
instructions govern authorized Git actions. -->
# ONBOARDING.md — start here, next session

## Current W5 integrated finish (2026-10-05)

Full `20261005T143932-8940eb33` passed **2,707 tests / 24 suites**, 2 documented DR0034 zlib skips and **2302 JSON artifacts valid**, with no source mutations.
84 application checks / 17 source flows / 239 frames / four native launches passed.

Readers preserve care on their closing frame, help restores the reading page,
and inboxes remember their selected filename within a session. Contextual help
matches covenant spending keys; malformed campaign loads remain readable.
Lineage exposes all recorded fields; archive/history Back and Help are visible.
Measured report: `research/experiment_reports/2026-10-05-integrated-finish.md`.
Release candidate: `game/dist/w5-integrated-finish-release/Mechagotchi/Mechagotchi.exe`
with adjacent `_internal`. Read `.development/w5-live-handoff.json` and actual
runner state for closure. Native keyboard/remote/published-SHA CI remain unobserved.
Earlier dated evidence below is retained; this is the current application entry.


Written **2026-07-21** by the outgoing session, completed
**2026-07-26** at the owner's direction, and its §3/§4 state sections
refreshed **2026-08-09 at the Phase-P gate (cycle 27 planned)**. Read
this file completely before touching anything.

The changelog (`sunsetted/complete/CHANGELOG/01/CHANGELOG.md`) is the
cycle-by-cycle summary of what shipped; it is derived from the gate
reports, and where they disagree the gate report wins.

**How to trust this file:** §1 (the frame), §2 (owner rulings), §6 (the
format), and §7 (honesty norms) are *durable* — they are owner rulings
and established discipline; they do not expire. §3 (state) and §4
(what's next) are a **snapshot** — re-verify them against `git log`,
`sunsetted/TODO.md`, and the gate artifacts before relying on them.

**The orienting files at the repo root**, and what each is for:

| file | what it is |
| --- | --- |
| `ONBOARDING.md` | **this file** — start here |
| `README.md` | what the project *is*, and the anti-drift identity constraint |
| `CLAUDE.md` | the agent operating brief (commands, architecture, conventions) |
| `sunsetted/complete/CHANGELOG/01/CHANGELOG.md` | cycle-by-cycle summary, derived from the gate reports |
| `_MOC_.md` | map of contents across the documentation |
| `TOOLS.md` | the tooling notes |
| `sunsetted/TODO.md` | **the live cycle queue** — the actual work list |

*Corrected 2026-07-27*: earlier versions of this file pointed at
`FABLE5.md` and `AGENTS.md` as live references. **Both now live under
`.depreciated/`** (`v0.0.1/FABLE5.md`, `AGENTS.md`) — the owner's
personal archive, which §2 says to ignore unless explicitly linked. Do
not go looking for them at the root. `docs/agent-standards.md` still
exists and is an older orientation doc, largely superseded.

*Relocated 2026-08-08 by the owner*: the `audits/` tree and the root
`CHANGELOG.md` now live under `sunsetted/` — the live queue at
`sunsetted/TODO.md`, archived cycles at `sunsetted/complete/TODO/NN/`,
the changelog at `sunsetted/complete/CHANGELOG/01/CHANGELOG.md`. Dated
records that cite `audits/...` paths cite where the files lived when
they were written; per the correction law they are not rewritten.

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

## 3. WHERE WE ARE RIGHT NOW (2026-07-28 — verify against `git log`)

### The headline

**Every documented phase A–G is COMPLETE and GATED.**
`docs/gap-analysis.md` — the roadmap that governed cycles 09–17 — is
**RETIRED per its own charter** (the Phase-G alpha gate went green
2026-07-12). It remains as the measured history of the gap and how it
closed. Since then, cycles plan from the **still-unmet documentation**
and from the named remainders each cycle's own records leave behind.

### Branch and merge state

Working branch **`phase-l-gate`** — historical name, not being renamed
(phases are already sequential, I→O). It carries cycles 22–25.

**Unified as of 2026-07-28**: `main`, `origin/main`, the branch and its
remote are all on one commit. Every cycle-24 and cycle-25 task was
merged and pushed at its own commit, per §6's branch rule. Check with
`git log --oneline origin/main..HEAD` — it should be empty.

> **A trap this cycle actually hit** (recorded in §9 too): **do not write
> a RED test into a lab directory until the previous task is
> committed.** O3's closing sweep failed on O4's deliberately-failing
> test, and the owner's IDE then committed that RED — briefly making
> HEAD red on unstarted work. Design and reading may overlap tasks; a
> failing test may not.

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
| 24 | N | the descriptor space earns its edges — and the cycle audits its own **instruments** (gate green 2026-07-28) |
| 25 | O | the adopted definitions reach the player — landed without a committed number drifting (gate green 2026-08-08) |
| 26 | P | the missing axes earn their sources — the visible-axis program complete (gate green 2026-08-09) |
| **27** | **Q** | **the engine's own advice reaches its decisions ← WE ARE HERE** |

Archived queues live in `sunsetted/complete/TODO/NN/TODO.md` (01–07, 09–26).

### Cycle 21 · Phase K — CLOSED, gate green 2026-07-26

Gate report `research/experiment_reports/2026-07-26-phase-k-gate.md`;
queue archived at `sunsetted/complete/TODO/21/TODO.md`. The vocabulary Phase J
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
at `sunsetted/complete/TODO/22/TODO.md`. What it settled, in one line each:
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
at `sunsetted/complete/TODO/23/TODO.md`. **M1** measured the archive on its own
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

### Cycle 24 · Phase N — CLOSED, gate green 2026-07-28

All six tasks DONE (N1–N5 plus **N7**, which DR 0052 added mid-cycle
rather than letting a default change happen as a side effect); gate
report `research/experiment_reports/2026-07-28-phase-n-gate.md`; queue
archived at `sunsetted/complete/TODO/24/TODO.md`. Six decision records,
**0049–0054**.

**The cycle's character, and the reason to trust it**: **Phase L audited
its own numbers, Phase M its own sentences, and Phase N its own
INSTRUMENTS.** Every one of its six slices found a defect in the
measuring apparatus rather than in the thing measured — and **three were
errors the session made and caught before they shipped as findings**
(N3's observer scored a learner on an event it cannot observe; N4's
population parameter was invented and **flipped the verdict**; N5's own
candidate name overclaimed). Each is a recorded process deviation.

**Every gate that could have rubber-stamped, did not**: N3 dropped two of
three, N5 refused DR 0048's *named* candidate and adopted one the record
never proposed, N4's rule could have refused all three arms, and **N1's
own prediction was refuted by its own measurement.**

**Phase N's specific debt, and it is this cycle's plan: it adopted three
things and put NONE of them in front of a player.** `insertion` is the
loop's default but every historical study is pinned to the incumbent;
`danger_margin` is the adopted definition of `health` but is blocked
off-screen by one package constant. Correct in each case, deliberate in
each case — and exactly the debt that quietly becomes permanent.

### Cycle 25 · Phase O — CLOSED, gate green 2026-08-08

All five tasks DONE; gate report
`research/experiment_reports/2026-08-08-phase-o-gate.md`; queue archived
at `sunsetted/complete/TODO/25/TODO.md`. Three decision records,
**0055–0057** (O1 deliberately wrote none — executing DR 0054's decision
is not a decision). The spine was Phase N's own debt — **it adopted
three things and put none of them in front of a player** — and the
cycle's character is that it **paid that debt without a single
committed number drifting**: landings additive, headlines restated
never overwritten, challengers judged in their documented roles, and
the one mid-cycle process failure (a RED committed early by the owner's
IDE) recorded as a trap with its rule.

### Cycle 26 · Phase P — CLOSED, gate green 2026-08-09

All six tasks DONE; gate report
`research/experiment_reports/2026-08-09-phase-p-gate.md`; queue archived
at `sunsetted/complete/TODO/26/TODO.md`. Two decision records,
**0058–0059** (three slices deliberately wrote none). **The
visible-axis program is COMPLETE**: seven of §1.17's eight visible
axes on the player's screen, one an honest opt-in, zero without an
engine source — and the split instrument moved with every surface
change, expecting exactly three DR-explained differences and raising
on a fourth. One prediction was REFUTED (P4 — the cycle's sharpest
finding: the Q-table beats the incumbent rule itself); three process
deviations were caught and recorded; five instruments were verified
against committed evidence before any new number was trusted.

### Cycle 27 · Phase Q — the engine's own advice reaches its decisions — OPEN

`sunsetted/TODO.md` is the live queue: **Q1 DONE; Q2–Q5 open.** The
remaining spine: the two authorship rungs cycle 26 named (the SLIP
mechanics rung, DR 0059's default-flip record), the oldest un-surveyed
half of §1.17 (M5's remainder 4), and the gate. Task detail and
sources are in the queue itself.

**Q1 — DONE 2026-08-09 (DR 0060).** **The prediction was REFUTED in
the strong direction — the Q-table's consumer CLEARS the documented 5%
bar, the learning track's strongest positive result to date.** The
opt-in seam (follows the thread at its own full-confidence semantics;
byte-identical off, pinned against the committed scenarios artifact)
fired on 59.4% of ticks and changed ~1 decision in 6: welfare
**0.187712 → 0.201518 (+7.355%)** — the first D6-style clearance the
decision seam has ever produced. **D6's saturation lesson is refuted
at the follower — the saturation was additive dilution, not the
seam.** The gain belongs to the good keeper (attentive
0.7276 → 0.7966; non-responders unchanged to the sixth decimal — the
consumer amplifies good keeping and cannot rescue neglect); begs
+236 / answered feeds +243, recorded not gated. **Eligibility only**:
the default-fleet promotion is DR 0060's named next record.
micro_threads 140 → **160**.

**P5 — DONE 2026-08-09 (no DR; DR 0050's own named remainder
executed).** **The last two probe artifacts that could not prove their
draw now carry their own edges — and both restatements come back
IDENTICAL to the number.** Each study re-ran through its own committed
builder at its documented defaults, written as a NEW `*_edged_stage0`
artifact beside the untouched original with a full-body deep
comparison: **zero differing paths over the entire bodies**; the only
additions are DR 0050's two provenance keys; the time-bounded concern
did not materialize (escalation 85.3 s vs its 900 s bound). The
committed originals still carry no edges — deliberately, and pinned.
map_elites_archive 449 → **464**.

**P4 — DONE 2026-08-09 (no DR; dated notes beside DR 0051).** **The
prediction was REFUTED, and the refutation is the headline: the
Q-table BEATS the incumbent frozen reactive rule itself, by
44.685%.** The collector reproduced ALL of N3's committed statistics
exactly first; the frozen rule's per-tick choices turned out to carry
empirical regret 0.027851 — 81% of uniform random's — so the harder
opponent was barely harder (D6's welfare-optimality is about survival;
per-tick selection leaves real regret on the table). **F's drop holds
like-for-like** (−1.776% → −0.744% against the online stump — the
asymmetry was ~58% of the gap, the sign never flips). **No roster
change in any branch, pre-registered.** micro_threads 123 → **140**.

**P1 — DONE 2026-08-08 (no DR; the decisions cited are 0048/0054/0055).**
**The §1.17 split measured AS SHIPPED, and the founding text now
carries its dated correction.** A live client session, the on-screen
half read from `snapshot()` under a pre-registered operationalization:
**6 of 8 visible axes on screen, 2 absent upstream of display, 2
hidden axes surfaced honestly** ("stress", "body stability"); no axis
without an engine source is shown (DR 0021's first law, pinned
per-axis). The instrument reproduced the committed M5 survey **7/8**
with `health`'s difference explained by DR 0054 — any other mismatch
raises. **M5's remainder 2 is closed in the game's own suite**
(snapshot carries age and mood, measured). Prediction confirmed. Game
200 → **216**.

**P2 — DONE 2026-08-08 (DR 0058).** **`happiness` is `social_warmth` —
the engine's own recent-interaction window — and the readout landed
the same day.** The N5 → O2 pattern end to end in one slice: three
CHOSEN candidates reading only what the engine records; five
pre-registered gates (N5's four + **G5 distinct-from-shown**, whose
`refuse_as_duplicate` outranks the euphemism verdict); both instrument
gates held first. `bond_rename` **refused as a duplicate** (its series
IS the shown bond readout's, tick for tick); `need_balance` — the
engine's own statistic — **withheld under the measured floor** with
its corpse reading 0.65 recorded (a mean hides the killer axis);
`social_warmth` adopted with **the neglected corpse reading 0.0**.
Prediction confirmed, including its named uncertainty. **Live in the
client: `play` raises happiness while it lowers health** — two bars,
different questions, both true. The P1 instrument moved with the
surface deliberately (regenerated: **7 of 8 visible on screen, 1
upstream gap, 2 hidden surfaced**); §1.17 carries a dated addendum.
Game 216 → **228**.

**P3 — DONE 2026-08-09 (DR 0059).** **`cleanliness` earns its MECHANIC
— the engine's first OPT-IN lifecycle seam — and dirt hurts only the
neglected.** The one §1.17 gap no display work could close: the seam
supplies the need, the decay, the keeper `clean` verb and a bounded
dirt→stress consequence, **byte-identical when off** (proven against
the committed Stage 0 comparator's own numbers and a frozen key list)
with **every parameter derived from the incumbent engine**. Five
pre-registered gates, the charter's refusals first-class
(`blocked_on_mechanic`, `refuse_as_lethal_cosmetic`): **ADOPT** —
clean responds +0.3076, the neglect stream shows the exact
deterministic consequence (+0.00682 stress, the starvation unmoved),
switchboard welfare impact 1.6e-05 vs the 5% D6 bar — and **an
attentive keeper's care absorbs the dirt pressure entirely** (care
delta 0.0), predicted and confirmed. Landed same slice for opted-in
covenants; the **default-covenant flip is a named future record** with
its regeneration cascade priced. The split instrument regenerated:
**7 on screen / 0 absent upstream — no documented visible axis lacks
an engine source any longer.** Package 299 → **316**; game
228 → **239**; lifecycle_sim 24 → **43**.

**O1 — DONE (no DR; DR 0054 already made the decision).** The lifecycle
public surface widens **six names → seven** (`DANGER_THRESHOLDS`),
following the W1 precedent: the exact `__all__` equality probe fails
until spec and code agree, and **that failing run is the RED**. The
promotion is deliberately narrow **and the narrowness is pinned** — a
test asserts neither `danger_margin` nor `health` is on the surface, so
whether the margin formula belongs in the engine stays a separate
decision. The constant is pinned **by value**, not by presence. Package
**295 → 299**.

**O2 — DONE (DR 0055).** *(GAME track.)* **`health` is on the player's
screen, and the play-drop is explained rather than hidden.** `play`
lowers the number (play costs energy), and two of the three ways to
handle that — smoothing, hiding — are forbidden by DR 0021's first law.
The answer: **show the BINDING AXIS beside the number.** `health 0.62
(tired)` costs no new number (argmin of margins already computed) and
turns an unexplained fall into a sentence. **The measured case, from the
live client**: a keeper who never sleeps sees `tired` from tick 2, 0.000
by tick 7, and dies of `energy_collapse` at tick 10 — **the readout
named the death cause eight ticks early.** Game **188 → 200**. Honest
limit recorded, not fixed: the bar bottoms out at **danger, not death**,
so it reads 0.000 on a living companion.

**O3 — DONE (DR 0056).** **The headline studies restated under the
adopted default — and coverage buys quality.** DR 0053's rule 2 shaped
it: a measurement does not improve, so this is a **new artifact** and
both committed incumbent artifacts are untouched. At DR 0042's own seed:
coverage **0.898438 → 0.880859** (−0.017579) but **QD 404.618236 →
411.738214 (+7.119978)**, **refusals 4,435 → 0**, **illegal elites
35 → 0**. L1 declined to patch the refusal tax because *"the fix trades
against coverage"* — this prices the other side. The documented E4 gates
were re-judged **verbatim** over ten paired seeds: **`NO_REGRESSION`**
(`ga_advantage_gate_met` was **already** failing and is explicitly not
attributed to the adoption). **DR 0042 is not retracted**; DR 0056 adds
a **quoting rule** — any *"the loop achieves X"* must name which arm.
Only the adopted arm was re-run (ten runs, not forty), because the GA
control takes no `slip_admission` and cannot move.

**O4 — DONE (DR 0057).** **Stage 2's last undispositioned generator
arms judged — each in its DOCUMENTED role, and the charter's own
framing corrected first.** CPPN (stance: *"late exploratory
generator"*) was bake-offed on B2's own terms and **REJECTED** at
validity **0.12** vs the 0.85 dossier bar — with the mechanism measured
(79 of 88 invalid bodies are *connected* cores under the DR 0029 mass
floor; only 9 disconnect) and the method's documented strengths
recorded beside the verdict (symmetry 0.475 above the WFC family;
100/100 unique; none of it offsets validity, pre-registered). Shape
grammar (stance: *"validator or post-generator stabilizer"* — a role
**already shipped** as `wfc_grid._finish`) was judged at the sharper
question *does it beat the incumbent?* — it repairs the raw collapse
0.01 → **1.00** validity at retention 1.0, then **TIES** the incumbent
at 1.00/1.0 under two-seed measured noise 0.0: **WATCH**, because a tie
is not a reason to replace a shipped incumbent. The instrument
reproduced the committed wfc row exactly before any new number was
trusted. Nothing adopted; no incumbent moved; prediction confirmed.
Lab 36 → **61**.

### What exists and is genuinely good

- **`packages/mecha_engine`** — ten promoted modules: `genome`,
  `generation`, `lifecycle`, `archive`, `provenance`, `repair`,
  `runtime`, `learning`, `storage`, `slip`. (`render` is
  DISPOSITIONED, not promoted — DR 0026, rejected-until-consumer.)
  Each backed by contract tests and lab-side parity pins.
- **`game/`** — the playable client (pygame-ce). Companion loop, era
  bench, covenant spending, hatchery, Contribute bridge, replays,
  repertoire/lineage browsers, SLIP import/export, community packs,
  save/resume, a PyInstaller bundle. **200 tests** (O2 added 12 with the
  `health` readout).
- **`workshop/`** — grid editor, SLIP creator, preview/scrubber,
  inspector, Keeper session page. **92 tests.**
- **`labs/`** — 19 research labs; every algorithm is proven here first.
  (`map_elites_archive` is the largest at **464**; `micro_threads`
  **140**; `architecture` **76**; `wfc_grid` **61**; `lifecycle_sim`
  **43** — all grown through cycles 25–26.)
- **`research/`** — the evidence ledger: **280 experiment reports**,
  **79 algorithm cards**, **59 decision records** (through DR 0059),
  package specs.
- **`data/`** — **2,253 JSON evidence artifacts**, all valid.

**Verified 2026-08-09, at the Phase-P gate:**
`python -B tools/ci/run_sweep.py` → **SWEEP GREEN** — 19 lab suites +
package **316** + workshop 92 + game **239** + CLI 23;
`data artifacts OK — 2253 JSON artifacts valid`.
(Slowest: workshop ~187 s, runtime_integration ~85 s,
map_elites_archive ~50 s, cellular_automata ~40 s.)
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
axes — and DR 0048 built none of them.

*Corrected 2026-07-28 by N5 / DR 0054 and O2 / DR 0055*: **`health` is
no longer one of the three.** It was the "CHOSEN definition" kind, and
the choice has now been made and gated — `health` **is** `danger_margin`
(the minimum normalised safety margin across the engine's own
`DANGER_THRESHOLDS`), the candidate DR 0048 *named* was **refused as a
euphemism** (it would have read 93% on a starved corpse), and the
readout is **on the player's screen with its binding axis beside it**.
~~**Two real gaps remain**~~ *Corrected 2026-08-08/09 by P2 / DR 0058
and P3 / DR 0059*: **no §1.17 visible axis lacks an engine source any
longer.** `happiness` has its CHOSEN definition (`social_warmth`) and
is on screen; `cleanliness` has its OPT-IN mechanic (not enabled by
the default covenant — a named future record). ~~§1.17
itself is also **measurably stale against the shipped client**~~
*Corrected 2026-08-08 by P1*: the split is now **measured as shipped**
(`data/game_client/companion_axis_split_stage0.json` — 6/8 visible on
screen, 2 hidden axes surfaced honestly) and §1.17 carries a dated
correction note quoting the artifact.

Also standing: ~~Stage 2's
undispositioned generator arms (**shape grammar**, **CPPN**)~~
**CLOSED 2026-08-08 by O4 / DR 0057** — each judged in its documented
role (CPPN rejected on validity 0.12 with the mass-floor mechanism
measured; shape grammar watch, tying the incumbent `_finish` at
1.00/1.0 under measured noise 0.0; nothing adopted, prediction
confirmed); the unbuilt method tracks remain (MRF-lite, Lenia,
reaction–diffusion, the MDP
sandbox, the QDax shadow port, z3/SMT at DR 0011's WATCH); the
~~the micro-learner ablation conditions **E/F/G** (Q-table, tiny
decision tree, Bayesian counter), never instantiated in the Phase-D
fleet~~ **CLOSED 2026-07-28 by N3 / DR 0051** — all three built and
judged through the D6 gates verbatim (E KEPT, F and G DROPPED, kept-five
roster unchanged, D6 regenerated byte-identical, nothing promoted); the
24×24 scale-up (DR 0014's re-opener) and the unpromoted
scale-geometry seam.

Standing: the ≤45-min HUMAN first-session pass and the whole
owner-deferred human-study block (prepared-not-blocking — and the
transducer study's "preference" number is a labeled PROXY, never
human preference); per-clip choreography (an engine DR when a consumer
asks); DR 0032's re-openers (untriggered, refutation deepening); the
first green CLOUD CI run, which awaits a push never made unasked.

---

## 4. WHAT TO DO NEXT (2026-10-04 Q5 snapshot)

Q1–Q4 are locally complete; Q5's consolidated gate is
`research/experiment_reports/2026-10-04-phase-q-gate.md`. Cycle 27's original
charter is archived at `sunsetted/complete/TODO/27/TODO.md`.
The live queue is cycle 28 / Phase R, PLANNED and NOT STARTED. Its complete
contract is `docs/development/cycle-28-learning-consumer.md`: promote the
missing bounded Q-table producer and consumer with defaults off, deliver an
explicit playable choice and save semantics, then gate ADOPT/REFUSE against
actual game arms with begging priced explicitly. Review completed Q5 first.

Use this repository's existing `.venv/Scripts/python.exe` (Python 3.13.9).
Preserve user/external work. Follow pombi development direction. The direct user
recovery delegation of 2026-10-04 reserves commit/sync/push to the user; it
supersedes earlier agent publishing authorization for this recovery.
No history rewrite, new source checkout/environment or automatic next-cycle
start is authorized here. Earlier dated state notes remain historical snapshots.

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
  ├─ decision_records/   ADRs, NNNN-slug.md (through 0056)
  ├─ package_specs/      contracts + the traceability matrix
  └─ README.md           THE MASTER TRACEABILITY LEDGER
data/                    JSON evidence artifacts + fixture corpora
docs/                    the vision + roadmap documents
sunsetted/TODO.md           THE ACTIVE CYCLE QUEUE
sunsetted/complete/TODO/NN/      archived cycles (01–07, 09–24)
sunsetted/complete/CHANGELOG/01/CHANGELOG.md   the cycle-by-cycle summary
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
8. `sunsetted/complete/CHANGELOG/01/CHANGELOG.md` — the cycle-by-cycle
   summary, derived from the gates.

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

Work `sunsetted/TODO.md` task by task; one commit per completed task
naming the task ID, the evidence, and the doc updates. A cycle ends
only when the queue is exhausted AND a full sweep is green — then
archive to `sunsetted/complete/TODO/NN/` and plan the next cycle from the
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

### CI repair addendum, 2026-10-04 (DR 0061)

Provision all three groups from the lock with the intended interpreter:
`uv sync --locked --python <interpreter> --group lab --group cli --group game`.
Then `uv run --no-sync python -B tools/ci/run_sweep.py` retains per-suite logs
and `summary.json` under `.ci-logs/`. The sweep includes its own CI instrument
tests. A local green result is not a native Ubuntu result; inspect both GitHub
jobs on the exact published SHA before closing a CI repair.

SLIP writer tests now target temporary paths and preserve committed observations.
The older instruction below to restore those artifacts after a sweep is
historical; never use blanket checkout/reset as test cleanup. Report unexpected
changes and preserve any owner work.

Original provenance artifacts are preserved under
`data/asset_provenance/baselines/stage0-windows/`. Their mixed Windows bytes and
native path ordering were not portable. The dated current restatement pins LF
checkout bytes and relative POSIX-string ordering; hashing never normalizes
input bytes.

### Earlier lessons (retained)

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
- **A RED test in a lab directory turns the CLOSING SWEEP red for the
  task you are trying to finish.** Cycle 25 hit this: O4's RED was
  written while O3 was still open, O3's verification sweep failed on it,
  and the owner's IDE then committed the failing file. **Do not write a
  RED into a lab directory until the previous task is committed** —
  design work and reading may overlap tasks, a deliberately-failing test
  may not.
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
3. Read `sunsetted/TODO.md` — the live queue and its standing note.
4. `python -B tools/ci/run_sweep.py --quick` — confirm the tree is
   green before changing anything. **~5 min**; the full sweep is ~9 min
   and is required before any commit that closes a task.
5. Read the most recent experiment reports in
   `research/experiment_reports/` for the immediate context, starting
   with `2026-08-09-phase-p-gate.md` (the last closed gate) and then
   cycle 26's own — `2026-08-08-companion-axis-split.md`,
   `-happiness-definition-gate.md`,
   `2026-08-09-cleanliness-mechanic-gate.md`,
   `-harder-skill-baselines.md`, `-probe-artifact-restatement.md`.
   The changelog is the faster orientation if you only need the shape.
6. Then work the queue — task by task, RED first, triad docs in the
   same change, one commit per task. When the queue exhausts, plan the
   next cycle yourself from the documentation.

### What a task actually looks like, start to finish

Every cycle-23 slice ran this loop; copy it:

1. **Read the charter** — the task's own bullet in `sunsetted/TODO.md`, and
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

- `sunsetted/TODO.md` (cycle 25 · Phase O — the LIVE queue), `sunsetted/complete/TODO/*/TODO.md`
- `sunsetted/complete/CHANGELOG/01/CHANGELOG.md` (the cycle-by-cycle summary)
- `CLAUDE.md`, `README.md`, `_MOC_.md`, `docs/agent-standards.md`  
  (`FABLE5.md` and `AGENTS.md` are now under `.depreciated/` — archived)
- `docs/gap-analysis.md` (retired; the measured history)
- `docs/project-research/` (the vision documents)
- `research/README.md` (the master ledger)
- `research/decision_records/0017`, `0021`, `0026`–`0059`
- `research/experiment_reports/2026-07-12-phase-g-gate.md`,
  `2026-07-20-phase-j-gate.md`, `2026-07-26-phase-k-gate.md`,
  `2026-07-26-phase-l-gate.md`, `2026-07-27-phase-m-gate.md`,
  `2026-07-28-phase-n-gate.md`, `2026-08-08-phase-o-gate.md`,
  `2026-08-09-phase-p-gate.md` (the last CLOSED gate),
  `2026-08-08-companion-axis-split.md`,
  `-happiness-definition-gate.md`,
  `2026-08-09-cleanliness-mechanic-gate.md`,
  `-harder-skill-baselines.md`, `-probe-artifact-restatement.md`
  (cycle 26's P1–P5)
- `tools/ci/run_sweep.py`


## 2026-10-04: Local development cycle (DR 0062)

A new root `AGENTS.md` is the operating entry point for the local cycle; it
is not the historical file in the owner archive. The original archived-file
notes above retain their historical meaning. Use `mechas develop --status`
(or the source invocation in `docs/development/local-cycle.md`) to inspect
the actual root/branch/HEAD and resume state. Specifications and suite scopes
are under `docs/development/`; runtime logs are in ignored `.development/`.

REVIEW -> REPAIR -> ENHANCE -> POLISH is operated by the active agent. No
hidden agent, scheduler, new credentials or automatic publishing is installed.
Q2 is the next preregistered product slice; Q3 defaults and Q1 promotion remain
separate decisions. A local full pass cannot satisfy native Windows/Ubuntu CI
on a published SHA. A blocked publication gate does not stop independent
authorized local work.

## 2026-10-04: Q2 completed locally (DR 0063)

Q2 now authors cleanliness through strict SLIP v0.2 mechanics. The keyword
still overrides (empty disables); save/resume/succession preserve that choice;
the window has conditional G clean and an engine-value footer. Incumbent
canonical outputs and the original DR 0059 metrics reproduce. The dated report
`research/experiment_reports/2026-10-04-slip-mechanics-authorship.md` records
the completed verification and preservation evidence.

Q1/Q2 are complete; **Q3-Q5 remain planned**. Next, preregister Q3's default
experience criteria and exact artifact cascade before any measurement. Q-table
eligibility remains separate from promotion. The default covenant is unchanged.
This local milestone does not close remote CI; no alternative push route is
authorized by a blocked publication attempt.

The old instruction to restore SLIP observation artifacts after tests is
superseded by DR 0061's isolated writers and DR 0062's preservation audit.
Tests must not change source artifacts. If they do, inspect the failure;
do not reset owner files to hide it.

## Sources for this update

- `research/decision_records/0061-portable-provenance-and-ci-evidence.md`
- `research/decision_records/0062-local-development-cycle.md`
- `research/decision_records/0063-covenant-mechanics-authorship.md`
- `sunsetted/TODO.md`, `docs/development/local-cycle.md`

## 2026-10-04: Q3 adopted for new lives (DR 0064)

The measured Q3 gate adopts cleanliness for new default companions and new
campaigns. Existing saves keep their covenants. A new campaign now starts under
the companion's selected covenant; the launcher exposes --slip and --keeper-dir.
Both covenants are bundled and the actual Windows executable was verified for
new/resumed lives and campaigns. Historical experiment inputs remain explicitly
frozen; no old artifact was regenerated. See the Q3 report for exact evidence.

Q1-Q3 are complete locally; Q4's hidden-axis survey and Q5's consolidation are
next. Native remote CI remains unmet and publication must not be retried or
bypassed. The earlier dated default notes describe their historical states.

## Sources for this update

- `research/decision_records/0064-default-covenant-cleanliness.md`
- `research/experiment_reports/2026-10-04-default-covenant-gate.md`
- `sunsetted/TODO.md`

## Earlier local resume snapshot (2026-10-04, Q4; retained history)

Q4 is in progress at 97db227c with actual-repository Python 3.13.9. Writes now
work after direct approval. Follow pombi local development direction; owner
retains commits/sync/push. No source mirrors or environment replacement.
Preregistration: `docs/development/q4-hidden-axes-controls.md`; findings:
`research/experiment_reports/2026-10-04-hidden-axis-sources-and-readable-controls.md`.

Q4 closing gate passed: 2493 tests / 24 suites, two named DR 0034 zlib skips,
2269 JSON artifacts. Owner-side commit e1bcf9f landed during the run without
source byte changes. Completion notes remain uncommitted; Q5 is next.

## Current local resume (2026-10-04, playable learning)

Use C:/Users/ryanf/github/_shelved/mechagotchi and its existing Python 3.13.9.
Q5 was reviewed. R1/R2 implemented the bounded producer/follower and persistent
playable option; full run `20261004T155004-f33ec4a2` passed 2,509 tests in 24
suites, two named DR 0034 skips and 2,271 JSON artifacts with no source mutations.
External owner commits 03ec951 and d1ebd03 are preserved; the agent performs no
commit/sync/push. The user explicitly waived commit-before-next-RED sequencing
for this recovery after being told the conflict. Do not reintroduce that stop.

R3 REFUSES default adoption: the current covenant rejects forty of the inherited
fifty corpus members; admitted-subset gains do not repair that comparability
failure. The experimental option remains usable and the incumbent stays default.
R4 fixes frozen save-home selection, preserves legacy saves without migration,
and has 26 real process launches / 23 checks on the final Windows bundle at
`game/dist/r4-learning/Mechagotchi/Mechagotchi.exe` (keep `_internal` adjacent).

Resume with the exact read-only source command in `docs/development/local-cycle.md`.
Cycle 28 passed full run `20261004T162036-b03ceece`: 2,516 tests, two named
skips, no source mutations. It is reviewed and archived. S1 (`s1-safe-resume`) covered validated model reload, explicit backup recovery,
atomic file replacement and actual policy status. Its source/CLI/native harness
passed 48 launch checks for both saved policies; the new native bundle is
`game/dist/s1-safe-resume/Mechagotchi/Mechagotchi.exe` (keep `_internal` adjacent).
Read `research/experiment_reports/2026-10-04-safe-resume.md` and the runner's
current full-gate status before claiming local closure or repeating tests.
S1 closed with `20261004T170013-413498d4`: 2,528 tests / 24 suites, two
documented skips, 2,275 valid JSON files, no source mutations.
Remote exact-SHA CI, signing and human usability remain separate unmet gates.
Scoped runtime escalation works; no security settings, source checkout,
environment, background service or scheduler were installed.

S2 closed in full run `20261004T173915-19f22122`: 2,537 tests / 24 suites,
two documented skips, 2,276 valid JSON artifacts, no source mutations. It is
reviewed and archived in `sunsetted/complete/TODO/29/TODO.md`. Its authoritative
companion checkpoints, derived-export reconciliation and save retry/discard
remain intact; read `research/experiment_reports/2026-10-04-safe-checkpoints.md`.

Cycle 30 T1 closed at `20261004T181855-269f5dbc`: 2,548 tests / 24 suites,
two documented skips, 2,279 valid JSON artifacts and no source mutations.
Repeated navigation, 24 real eras, restart, empty histories and 384-pixel windows
passed additional observations. Read `research/experiment_reports/2026-10-04-era-review.md`.

T2 locally closed the explicit F13/F17 remainder
in repertoire.py. B browses stored creatures after restart, or the selected era
from T. Historical packets use the recorded covenant; A adopts only through the
current covenant's existing gate and keeps the learning-policy choice. Viewing
pauses care, ignores care inputs and does not train, evolve or write the keeper.
T opens the selected report; B/Escape returns to the entry report or care.
C's budget/spending controls now precede care status without changing its timing.

Read `research/experiment_reports/2026-10-04-saved-archive.md`, the live queue and
runner state for actual verification and the exact next action. Candidate:
`game/dist/t2-saved-archive/Mechagotchi/Mechagotchi.exe`, keep adjacent `_internal`.
T2 full `20261004T185738-2f3b4168` passed 2,563 tests / 24 suites, two
documented skips and 2,282 JSON artifacts with no mutations. Native
keyboard remains unavailable because node_repl/@oai/sky is not exposed here;
packaged subprocess and source pygame interaction evidence are distinguished.
No Git mutations, security changes, new environment or background service.

T3 `t3-saved-replays` is locally complete: V reopens indexed recordings after
restart or from the selected T era, with paused care and honest post-era labels.
The existing producer records only a current-run era with matching inputs;
missing/corrupt old history is explicit and is never reconstructed. Read
`research/experiment_reports/2026-10-04-saved-replays.md` and runner status for
exact verification and closure. Full `20261004T192757-866fdf0f` passed
2,576 tests / 24 suites, two documented skips and 2,283 valid JSON artifacts
with no source mutations. Native build: `game/dist/t3-saved-replays/Mechagotchi/Mechagotchi.exe`, retain
`_internal`. No engine/default-policy changes or Git mutations.

Locally closed T4 joins the existing DR 0021 loop: next-era weather and
R/W contribution copies persist immediately; successful covenant changes persist
without waiting for an era. E journals the real completed result before ledger/
state writes, allowing foreground retry/restart to finish it without re-evolution.
Recorded outcomes show actual admitted IDs; archive/adoption/replay semantics
remain. Backspace unstages copies, and T supports paused preparation. Engine
rules/default policy remain unchanged. Read the precise code/queue handoff and
verification in `research/experiment_reports/2026-10-04-keeper-loop.md` and
`develop --status`. Full `20261004T202052-aaa63dd1` passed 2,590 tests / 24
suites, two documented skips and 2,286 JSON artifacts without mutations. Then-current
locally closed build: `game/dist/t4-keeper-loop/Mechagotchi/Mechagotchi.exe`,
with adjacent `_internal`. All four contracted Cycle 30 tasks are locally closed.
Legacy saves without budget-base metadata retain their prior interpretation;
no historical values are inferred. Native keyboard remains unavailable.

T5 is the directly delegated responsiveness investigation after T4's closure.
Normal/larger source eras demonstrated 9-12 seconds of event starvation; the
repair uses one joined foreground-owned worker, real candidate progress and an
atomic cancellation/save boundary. Headless runs retain their prior contract.
Read `research/experiment_reports/2026-10-04-era-responsiveness.md`, DR 0073 and
`develop --status` for actual closing gates. No new environment, service,
scheduler or Git mutation; original scientific results/defaults remain intact.

T5 is locally closed: full `20261004T214405-8fe7b9f8` passed 2,606 tests /
24 suites, two documented DR 0034 skips and 2,288 JSON artifacts with no
mutations. Then-current locally verified build:
`game/dist/t5-responsive-eras/Mechagotchi/Mechagotchi.exe`, adjacent `_internal`
required. No active worker. Read the responsiveness report for the consolidated
product checkpoint, measured scale limits and established recording/family/hosting
remainder; `.development/t5-live-handoff.json` holds the exact restart context.
The next action is read-only `develop --status`, not another unchanged gate.

Cycle 31 U1 is locally closed. New E eras retain their actual final-best
evaluation with exact candidate seed, generation, weather and original/final
identity. V from care/T or the matching B selection reads saved frames; other
elites and missing originals explicitly say not recorded. Legacy labels remain.
Versioned completed-result journals preserve footage across failed saves; no
re-simulation or default-policy change. Full `20261004T224746-6ccc82b0` passed
2,624 tests / 24 suites, two documented zlib skips and 2,290 JSON artifacts
without mutations. Then-current locally verified build:
`game/dist/u1-original-recordings/Mechagotchi/Mechagotchi.exe`, with `_internal`.
Read `research/experiment_reports/2026-10-04-original-era-recordings.md` and
`.development/u1-live-handoff.json` for evidence, limits and exact restart.
The original-recording remainder above is now closed; morphological families
and hosted sharing remain separate. Next: read-only `develop --status`; no
active worker or next RED. Git actions remain reserved to the user.

Cycle 32 V1 is locally closed: exact saved seven-axis niche history (N in B),
recorded predecessor-campaign navigation (Ctrl+[ / Ctrl+] in T), and connected
report/archive/original recording/current-covenant adoption. L links to campaign
story and pauses care. Missing/incompatible records are explicit; equal labels
are not calibration or biological-family evidence. Both E5 cohorts survive.
Full `20261004T234803-5750f659` passed 2,636 tests / 24 suites, two documented
zlib skips and 2,292 valid JSON artifacts without mutations. Current local build:
`game/dist/v1-niche-history/Mechagotchi/Mechagotchi.exe`, with adjacent `_internal`.
Read `research/experiment_reports/2026-10-04-niche-history.md` and
`.development/v1-live-handoff.json`. Next: read-only `develop --status` and review
the completed result; no active worker or next RED. E5 projection, new role/weather
mechanics and hosting remain deferred. Native keyboard, maximum-history behavior
and exact-published-SHA CI remain unverified. Git actions belong to the user.

Cycle 33 W1 is locally closed (2026-10-05): I/K browse named covenant/pack
files in the chosen save home's inboxes; explicit Enter imports, F5 refreshes,
and context-specific help and refusal details remain paused and pageable.
The committed starter pack now connects to named covenant choice and the next
era without renaming. Stale previews and conflicting existing files refuse;
equal staged JSON preserves its bytes. Current companion, both policy fixtures,
predecessor history and every prior scientific artifact remain intact.
Full `20261005T115738-611ddb0c`: 2,656 tests / 24 suites, two documented zlib
skips and 2,294 valid JSON artifacts without mutations. Application evidence:
28 checks, four native launches, twelve source flows / 75 rendered frames.
Current local build: `game/dist/w1-import-inboxes-final/Mechagotchi/Mechagotchi.exe`,
with adjacent `_internal`. Read `research/experiment_reports/2026-10-05-import-inboxes.md`
and `.development/w1-live-handoff.json`; the active runner slice is
`w1-import-inboxes`. Next: read-only source `develop --status` and W1 review,
then source-backed investigation before another preregistered slice. No active
worker or next RED. Native keyboard, maximum inbox scale and cold covenant
model-load responsiveness remain unmeasured. Publication and remote setup are
separate; commits, synchronization and pushes remain reserved to the user.

Cycle 34 W2 is locally closed (2026-10-05). Cold covenant preparation now reads
the existing corpus without training evolution models; E requests those models
in its established responsive worker. Bounded cold imports fell from 4.2-4.4s
to 23-38ms, including invalid/stale refusals. Both-policy retry, repeated import,
conflict and cold-load cancel/close flows preserve existing files and companion
state. Tiny/normal pre-change hashes and genuinely earned larger era/recording
parity match. No scientific, cache-input, covenant or default-policy change.
Full `20261005T123344-a9435c5a`: 2,666 tests / 24 suites, two documented skips,
2,297 valid JSON artifacts, no mutations. Application: 76 checks, four native
launches, 14 source flows / 560 frames. Current local build:
`game/dist/w2-responsive-preparation/Mechagotchi/Mechagotchi.exe`, with `_internal`.
Read `research/experiment_reports/2026-10-05-responsive-preparation.md` and
`.development/w2-live-handoff.json`; run read-only source `develop --status`.
No active worker or next RED. Review the existing hatch explanation/preview
boundary before a further contract: F8 constrained traces are distinct from
WFC's missing trace seam. Native keyboard/maximum scale and published-SHA CI
remain unverified. No remote executor; Git actions remain the user's.


## Cycle 35 W3 - constrained hatch preview (2026-10-05)

W3 implements paused H preview, explicit Enter adoption and O saved-origin
inspection. Engine animation and complete recorded trace remain distinct from
WFC collapse/restart events, which the current engine does not expose.
Read `research/experiment_reports/2026-10-05-hatch-preview.md`, its DR0078/card,
and `.development/w3-live-handoff.json` for actual closure and exact restart.
Active contract: `docs/development/cycle-35-hatch-preview.md`. No Git mutations;
native keyboard, remote executor and published-SHA CI remain unclaimed.


W3 locally closed: Full `20261005T130951-59a1cc56` passed **2,679 tests / 24 suites**, 2 documented DR0034 zlib skips; **2298 JSON artifacts valid**. No source mutations; local completion only.
48 application checks / 10 source flows / 208 rendered frames / four native
load/resume launches passed. Current candidate:
`game/dist/w3-hatch-preview-final/Mechagotchi/Mechagotchi.exe` with `_internal`.
Exact restart: `.development/w3-live-handoff.json`. WFC collapse/restart tracing
is a separate unregistered seam; native keyboard, remote executor and
published-SHA CI remain unclaimed. Do not repeat unchanged verification.


## Cycle 36 W4 - distinct WFC inspection (2026-10-05)

Tab in H preview captures and inspects the optional WFC arm. Space plays its
real events; comma/period steps, brackets move attempts, Home/End select
endpoints. V shows the actual final body/animation when available. Tab/Escape
returns to the unchanged constrained hatch candidate; N captures another WFC.
The inspector is read-only and session-only: it does not adopt a creature,
write saves or claim the active covenant constrains WFC. Help and paging pause
playback. Failed/cancelled captures retain honest outcomes; cancellation waits
for the current bounded call and joins its worker before returning.

Current science correction: DR0042 superseded DR0031's evolution-default clause.
Constrained remains the default; WFC remains a distinct additive arm. Earlier
F8/W3 wording about WFC as current production/default is stale and is retained
as dated evidence, not current authority. No generator decisions or defaults
changed in W4. Read `research/experiment_reports/2026-10-05-wfc-trace.md`, DR0079,
the W4 metric/baseline artifacts and `.development/w4-live-handoff.json` for
measured closure and exact restart. No Git mutations or remote executor claim.


W4 locally closed: Full `20261005T135504-94a410b6` passed **2,694 tests / 24 suites**, 2 documented DR0034 zlib skips and **2300 JSON artifacts valid**, with no source mutations.
The 68 pre-edit RNG/output/error cases and exact lab/package traces pass;
80 application checks / 12 source flows / 162 frames / four native smoke
launches pass. Current candidate:
`game/dist/w4-wfc-trace-release/Mechagotchi/Mechagotchi.exe` with `_internal`.
Exact restart: `.development/w4-live-handoff.json`. No next scope is registered;
no active worker or Git mutation. Native WFC keyboard, maximal-scale observations,
remote executor and exact-published-SHA CI remain unclaimed.
