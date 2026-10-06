# Mechagotchi product checkpoint: design versus implementation

Date: 2026-10-05. Review baseline: `d4b4337d0dacbdfa816d990297c03a5da2d0cdca`,
branch `phase-l-gate`, resolved source `C:\Users\ryanf\github\_shelved\mechagotchi`.
Initial working tree: clean. Interpreter: the repository `.venv`, Python 3.13.9.

## Finding and scope

Mechagotchi has a working research engine and a substantial connected application.
W5 closed its registered reader/preparation defects; it did **not** close the
product vision. Several normal journeys still discard authored or lived state,
depend on the source checkout, or stop before an existing engine capability reaches
the user. The next work must integrate those journeys and address the deeper
mutation, experience and survival contracts, rather than keep polishing the same
reader screens or equate a test count with product completeness.

This is a source review and planning checkpoint, **not an implementation or
scientific adoption gate**. The current delegation requested assessment and a
new queue only. No proposed work below has been implemented. The previous queue
is preserved byte-for-byte at [Cycle 37 archive][old-queue]; the next queue is
[Cycle 38 / X1-X8][queue]. No new slice or RED run has started.

The owner committed the preceding work. All **51/51** source hashes in
`.development/w5-live-handoff.json` match this commit. W5's previously observed
full run remains `20261005T143932-8940eb33`: 2,707 tests / 24 suites, two documented
zlib skips, 2,302 valid JSON artifacts. These are inherited observations, not a
new run or evidence of CI on the present SHA. No unchanged suite was repeated.

## Authority and how it was applied

1. Current user instructions and [AGENTS.md][agents] govern this source tree,
   preservation, single-writer work and owner-only Git publication.
   [ONBOARDING.md][onboarding] sections 1-2 preserve the engine/game duality and
   explicitly reject declaring the project finished just because a queue ends.
2. The owner's [original design][owner-design], reached through the explicit
   reference in [DR0017][dr17], asks for a coherent mathematical creature engine,
   survival/ancestry-based evolution, many narrow intelligence threads, and a
   complete engine-SLIP-Workshop connection. It rejects fastest-to-market scope
   reduction. This review did not search unrelated personal archives.
3. The [governing research plan][research] defines the genome as more than pixels,
   SLIP as operative constraints, measurable adaptation and interaction influencing
   future generations (lines 169-193, 341-355, 750-878). The [validity analysis][validity]
   describes life/evaluation/lineage memory, meaningful variants and a complete
   authored-profile-to-engine workflow (155-167, 303-329, 719-763).
4. Accepted decisions constrain those ambitions. [DR0021][dr21] governs the Keeper
   loop; [DR0022][dr22] governs durable engine records; [DR0033][dr33] chooses the
   native pygame client. [DR0035][dr35] accepts local pack exchange while reserving
   hosting/registry/signing decisions to the owner. The [Workshop charter][workshop-design]
   requires complete creator tasks and faithful engine inputs, not a research UI.
5. Later explicit decisions and negative results survive. [DR0024][dr24] adopts
   engine-projected animation instead of stored hand-keyframed genomes.
   [DR0057][dr57] dispositions generator research arms; [DR0066][dr66] refuses
   Q-table default adoption. Historical proposals are not all mandatory features.

The testable implementation is the authority for what currently works. A design
sentence establishes intent, not proof that a feature ships. Conversely, a valid
schema or passing isolated API does not establish a complete user journey.

## Coverage and actual implemented capability

The preserved [inventory][inventory] enumerates 654 tracked implementation, test,
build and interface files with baseline hashes and line counts. It accompanies a
4,188-file tracked preservation snapshot in `.development/product-checkpoint-2026-10-05/`.
Inventory is not a claim that every fixture or every line was individually audited.
Four independent read-only reviews traced the following major boundaries; the
main reviewer reconciled them with current authority, source and targeted results.

| Subsystem | What genuinely exists | Remaining boundary |
| --- | --- | --- |
| Genome, validation, SLIP | Rich cells/organs/materials, profile validation, legacy formats and adopted cleanliness covenant. [Genome schema][genome-schema], [SLIP schema][slip-schema]. | Workshop projections do not preserve this complete contract; operator semantics are narrower than the authored mutation vocabulary. X2, X6. |
| Generation | Learned local-adjacency proposals, constrained stabilization, parent/ancestor IDs, optional WFC and real WFC explanation trace. [Generator][generate] 106-159, 220-327; [WFC][wfc]. | Most child structure is resampled; weights/locks and rate values need an explicit operational contract. X6. |
| Damage, repair and evolution | Actual damage, learned wound-site repair, lifecycle evaluation, archive selection, elite parents and next-era founders. [Live runtime][live] 99-170; [Evolution][evolve] 281-419; [Campaign][campaign] 551-589. | Current Keeper-life outcomes are not evolutionary inputs; harder survival remains primarily lab evidence. X7-X8. |
| Learning and thought | Micro-thread fleet, reward updates and confidence-gated computation; Q-table is explicitly opt-in and per-life. [Threads][threads] 932-977; [Switchboard][switchboard] 125-162; [Session][session] 347-386. | Product-compatible promotion evidence is missing; native thought traces are not perceptible. Incumbent is not wholly nonadaptive. X7. |
| Readability/archive | Learned readability orders parents and campaign selection; seven-axis niche occupancy and saved elite browsing work. [Evolution][evolve] 292-314; [Niche history][niches]. | Morphological descriptor labels are not observed individual personality; historical E5 cohorts cannot be conflated. X5, X7. |
| Care/death/succession | Real lifecycle, keeper-mediated feeding, actual generated children, in-session lineage, validated save/backup/recovery and retry. [Session][session] 319-545. | Adoption replaces that session history; campaign recovery/identity has uncovered discontinuities. X1. |
| Preparation/eras/progression | Staged genomes/weather, saved covenant changes, responsive cancellable computation, exactly-once completed-result journal, real admission/rejection and several earned caps. [Era plan][era-plan], [Campaign][campaign], [Covenant][covenant]. | Missing role/harder-weather consumers and an unproven live extinction journey. X8. |
| History/replay/provenance | Saved era reports, archive adoption, predecessor navigation, exact niche occurrences, original final-best recording and honest unavailable states. [Original recording][original], [DR0074][dr74]. | Founder payloads and full execution inputs are not self-contained; original footage is not equivalent to recomputation. X5. |
| Workshop | Grid/profile authoring, preview, projected animation, trait UI, carriers, release, inspection and browser lab sessions exist. [Workshop server][server], [Grid editor][grid-editor], [SLIP editor][slip-editor]. | Rich semantic loss, stale releases, fragile drafts and disconnected native Keeper context break complete tasks. X2-X3. |
| Native client | Care and engine animation/effects, covenant/preparation, hatching, imports, reports/replays/archive/niches and help are real consumers. [Application][app]. | Startup/recovery remains terminal-dependent; the complete player journey needs visible native actions and scalable legibility. X4. |
| CLI/examples/delivery | CLI launches lab, workshop, source game, build and development workflow; unsigned folder build and source CI exist. [CLI][cli], [Game workflow][game-cli], [Build][build], [CI][ci]. | Detached runtime content, pack creation, current-player routing and supported complete examples are incomplete. X3-X4. |
| Scientific operations | Preregistered contracts, lab cards/reports/metrics, historical ledgers, full local runner and separate publication gates. [Local cycle][local-cycle]. | These support product work; repeating a closed gate is not new product progress. Preserve all prior science throughout X1-X8. |

## End-to-end findings

### X1 — Keeper continuity and recoverable campaign identity (P0)

**User outcome:** caring through lives, adopting, changing the covenant and
restarting preserves one inspectable Keeper story and the intended campaign.

H/Enter and B/A adoption construct a fresh `CompanionSession` and replace the
current one ([app][app] 960-969, 1413-1422). The constructor initializes a one-row
lineage ([session][session] 210-211); L reads only that session (app 1335).
The [campaign probe][campaign-result] cared through two lives, adopted, and saved
one subsequent tick: both `companion.json` and `companion.bak.json` then held one
record and no earlier death. A separate `lineage.bak.json` may temporarily retain
older records; L cannot browse it, companion recovery does not restore it, and a
later lineage change can overwrite it. Genetic ancestor IDs do not preserve an
accessible, durable record of the actual cared-for lives.

Campaign recovery also has gaps beyond W5's malformed-JSON example. `_EraBench.ensure`
resumes only when both state and ledger exist (app 237-256). A valid imported-base
state with a missing ledger silently constructs the default campaign. A supported
format object missing required fields raises uncaught `KeyError('campaign_id')`
through `budget_lines` (app 273; campaign 872). Import explicitly sets a **new base**
([Covenant I/O][covenant-io] 93-96), but `successor()` uses original `self.inputs`
(campaign 714-727): the probe's `audit_new_base` became `slip_v2_cleanliness`.
Fixed demo metadata defaults (campaign 417) also require an identity contract.

This needs a durable care/adoption chronicle and coherent state/ledger/companion
recovery, grounded in DR0021's bloodline persistence and DR0022 succession. Do not
invent deaths for living replacements, merge genetic ancestry with adoption, or
claim to reconstruct already-lost history. Preserve available legacy records and
mark uncertainty. New factual per-life outcome summaries are a foundation for X7,
not evidence that any new evolutionary influence is valid.

### X2 — Lossless and recoverable authoring (P0)

**User outcome:** the creature/profile a creator edits is the same semantic object
they validate, preview, save, reopen, release and export.

The [actual API probe][workshop-result] demonstrates four failures: cell weight
`0.91` becomes `0.1` after unedited reopen/save; PNG sidecar export also drops it;
an authored antenna reloads as `N` then fails validation as an unknown token; and
the layer sidecar appears in creature catalogs without a creature identity.
Server load returns a matrix/palette projection (server 883-904), client load
clears overrides (grid editor 783-795), and export reconstructs the matrix without
them (server 1676-1698). The old `. B A E M` editor gate (server 211, 226-242)
cannot round-trip the engine's evolved vocabulary. Import similarly reduces
decoded data (server 1809); draft replacement can retain stale overrides
(grid editor 426). This is an authoring-model failure, not a missing button.

The SLIP editor builds a whitelist object (345-403, 745 onward), omitting
`mechanics` although [the shipped covenant][cleanliness] enables cleanliness.
Saving an edited profile can therefore remove an adopted mechanic. Its 64-cell
mass controls also lag the supported 16x16 surface (slip editor 163).

Release currently sends the saved filename (grid editor 725-739) even when the
canvas differs. Clear/load/resize have no undo or dirty-draft recovery; canvas
painting is pointer-only (383-412), validator lists do not locate implicated
cells (646), and responses carry no draft revision (626). These directly affect
the charter's complete, teaching, forgiving creator task. X2 should introduce one
faithful authoring document and revision model, accessible editing, recoverable
drafts and explicit save/release semantics together. Retain projected animation
as the authority; arbitrary frame authoring is not required by this finding.

### X3 — One selected Keeper, creation and file exchange (P1)

**User outcome:** author for the actual played Keeper, release into its next era,
inspect the resulting bloodline, and create a pack another Keeper can import.

Workshop uses `data/workshop/*` and the lab's `data/game_loop/keeper/keeper_session.json`
(server 198-210, 453-460, 765-793); native uses repository `keeper/` or
`~/.mechagotchi`, `campaign_state.json` and `campaign.sqlite3` (app 82-102, 516-549).
Workshop's active-budget panel can therefore refer to another campaign. The CLI
starts Workshop with only `--port` ([Workshop workflow][workshop-cli] 202-205).
Native X exports into its own save home, but the editor lists its curated/project
SLIPs; native R stages a genome, not an editable Workshop project. The Workshop
lineage view reads released/lab records (server 650), not that native ledger.

`build_pack` / `write_pack` exist ([Packs][packs] 30-69) with no operational
creation caller in game/CLI/Workshop. DR0035's export -> build -> hand over ->
import journey therefore stops at library functions. A selected local context,
faithful genome/profile handoff and a pack-composition consumer can complete it
without hosting, account integration or silent merging of distinct histories.
Dependent on X1-X2; coordinate explicit installed content paths with X4 and
lineage provenance with X5. Existing default directories must remain legible.

### X4 — A self-contained native product and executable entry journeys (P1)

**User outcome:** receive the application, launch it without a checkout, choose or
recover a save, learn care, prepare/run/review/adopt and quit/resume using visible
application actions. A creator or engine user has a supported runnable example.

The build includes only seeds, two SLIPs and readability content ([build][build]
26-34), while real/callback weather loaders require other files ([campaign][campaign]
132-180). Resource discovery walks ancestors ([Packets][packets] 44-74), so builds
under the checkout can hide missing packaged content. The [resolver probe][delivery-result]
used the real W5 `_internal` assets but hid ancestor-checkout discovery: defaults
resolved; both advertised weather sources failed with explicit missing-file
errors. This is a resolver-level observation, **not relocated native automation**.
The missing existing payloads are 45,622 and 5,769,937 bytes. Installed game
metadata declares no runtime data ([game package][game-package] 9-32), and retained
native artifacts lack discoverable LICENSE/NOTICE files. Metadata's parent-path
license pattern produces deprecation warnings, not a demonstrated build failure.

Fixture lookup occurs before loading a saved companion (app 512-540); invalid or
backup-only startup calls `parser.error` before pygame initialization (524-544,
578-580). The release omits its console (build 68-70). Recovery primitives are
sound, but double-click recovery is not complete. Fixed viewport/text size and
global key-driven modes (app 568-580, 1100 onward) need an application front door,
visible connected actions and scalable controls while preserving the LCD identity.
This does not imply a framework rewrite or a generic dashboard.

The CLI's actual status still reports only “9 promotion-ready of 10 candidates”
and “waiting on human ratings” (cli 50-84), although DR0017 makes manual calibration
fallback. Lab `session` and actual `game` remain distinct contexts. Package README
calls already-promoted modules deferred ([engine README][engine-readme] 30-47).
Evidence regeneration is not an ordinary engine example and can write historical
outputs. Complete executable player/creator/public-engine examples and context-aware
entry points belong to this implementation, not a separate prose cleanup.

Source CI ([ci][ci] 24-64) does not install/build/relocate product artifacts. Its
push trigger is `main`; this audit establishes no exact-SHA cloud result. Future
artifact acceptance must exercise declared supported targets and record both
source identity and bundled content identity.

### X5 — Self-contained era inputs and real founder provenance (P1)

**User outcome:** explain a recorded creature's origin and reproduce a newly
recorded era from its preserved inputs after installation content changes.

DR0022 promises replay-sufficient records and verbatim weather snapshots, but
playable eras store forecast plus snapshot IDs (campaign 628), reload external
weather/model sources, and pass `founders=None` to `record_era` (campaign 938).
The storage authority already supports full founder/admission records ([Store][store]
209 onward). A read-only query of the actual W5 demonstration ledger found
**2 eras, 23 elites, 2 replays, 0 founder rows**; era 1 names 14 admitted founders,
including `released_glow_lantern`, and two rejected releases. Verdicts exist,
but the promised full inputs/source records do not. The retained campaign probe
records this observation. Existing deterministic replay tests provide models,
seeds and configuration from their fixtures; they do not prove a self-contained save.

Repair caching keys use IDs/epochs/seed rather than source-content hashes
(campaign 379), so immutable input identity must also govern caching. Record exact
ordered founders, effective configuration, weather data, model/source digests,
generator/admission policy and archive geometry/calibration identity for future
eras. An immutable content-addressed reference is acceptable only when its bytes
remain available independently of the original mutable paths.

Preserve prior ledger blobs and all replay hashes. U1's actual original final-best
recording is an adopted product boundary, not an incomplete all-elites recorder.
Recomputed footage must never be called the original evaluation. Old unsupported
reproduction must list missing inputs. E5 morphology families, seven-axis niche
occurrence and actual ancestry stay separate; equal labels do not prove absent
calibration equality ([niches][niches] 169).

### X6 — Make mutation authorship operational (P1, scientific gate)

**User outcome:** authored mutation permissions have defined, measured effects on
descendants through preview, hatch and era generation.

The research plan calls `M` mutation permissions and describes controlled operators.
Current constrained generation samples a fixed 12 attempts (generate 253-255),
chooses an allowed palette independently (384-387), reconstructs cells with weight
`.1` and `locked=False` (396-417), then writes rate attributes within caps
(526-550). Workshop's cell weights have no consumer there.

The [engine diagnostic][engine-result] used a valid/aligned parent with 13 locked
cells, zero mutation rates/caps and two permitted palettes. All ten children
discarded locks, four changed palette and nine moved the anchor; current validators
accepted all ten. This **does not prove violation of a specified lock inheritance
rule**: the schema only types locks (178-180, 209-212). The existing
[generation contract][generation-contract] 92-100 enforces numeric maximums but
does not define observed operator frequencies. Resolve probabilities versus output
attributes, authoring locks versus germline locks, and zero-cap semantics first.

Implement and measure a named compatible arm rather than silently rewriting the
legacy generator and its history. Evidence must cover forbidden operations,
weight effects, validity, deterministic lineage/trace, accepted baselines and
legacy parity. Only a successful declared gate may connect new defaults. This is
deep engine/SLIP/Workshop work; adding explanations to inert controls is insufficient.

### X7 — Lived experience, justified adaptation and perceptible thought (P1, scientific gate)

**User outcome:** actual care history remains meaningful to the bloodline, and
the creature's adaptation and thinking can be observed through real behavior.

The promised user-history bridge is absent. `advance()` records action/reward/log
data, while `succeed()` takes only grid/model/profile/seed (session 347-407).
Lineage lacks bounded care summaries (427-437), and contributions stage only the
genome (app 1377; campaign 561-589). A controlled diagnostic with the same founder,
covenant and succession seed observed starvation at age 11 under neglect and
energy collapse at age 25 after 15 feeds; both produced the identical child hash
`d20a464415476b48dde00f458348212100bfbb5a55316c0c7c360adcc59488d4`.
This is evidence of the missing Keeper-history input, **not absence of ancestral
selection**: damage/repair/lifecycle fitness and elite ancestry already drive eras.

Individual behavior also needs an explicit disposition. Ten seed creatures under
one covenant and matched care yielded one 25-tick need trajectory in this narrow
diagnostic. Lifecycle initialization takes covenant priors plus mean stress/damage
([Lifecycle][lifecycle] 205-245), whereas `behavior_neediness` is a morphology
descriptor ([Metrics][metrics] 162-184). Do not relabel it as live personality or
claim this small sample refutes morphology's measured survival effects. Determine
which variation is species-level and whether individual variation has a justified
falsifiable mechanism before adding it.

Default sessions observe five kept threads but choose the frozen evaluator;
experimental sessions use the promoted decision path (session 347-357).
DR0066's 80% incompatible inherited corpus and default REFUSE remain authoritative.
A new product-compatible cohort and preregistered comparison are necessary, not
permission to announce learning gains or automatically promote Q-table.

Finally, four-tick thought records are present but absent from the native footer
and hints in the diagnostic (session 366, 379-380; app 428-502, 1430-1451).
Browser scrubbers already show thoughts; native replay captions show phase/tick
([Replay][replay] 217-232). Connect actual traces to visible native behavior without
invented confidence or arbitrary care delays. Couple this with the experience
contract and measured consumer rather than another display-only polish cycle.

### X8 — Earned stewardship choices and operational survival (P1, scientific gate)

**User outcome:** progress changes meaningful engine-backed choices, harder play
has demonstrated consequences, and genuine campaign failure leads to succession.

DR0021 names organ-role budgets, harsher forecasts and sheltered/hard survival
(68-86). The current covenant budget explicitly defers the first two (covenant 69);
weather names are all offered unconditionally (campaign 52; app 1398). Palette,
thinking, population/generation and readability effects do exist. Do not call the
whole progression system a stub or mistake an intentionally imported new base
for a budget bypass.

Promoted `evolve()` has no stress-regime argument (evolve 93-111). `tiny` is a
verification scale, not difficulty (app 173). [Historical hard-regime work][hard-regime]
is lab evidence, and [the session soak][soak] 275-305 records no observed extinction
at its stage-0 scale. Tests manually setting `status='extinct'` prove handling,
not a playable survival path. An archive retains incumbents within an era
([Archive store][archive-store] 86-142), but a fresh archive is created per era
(evolve 237): **extinction is not proved impossible**.

Preregister what live population/campaign failure means while preserving historical
elites. Promote only justified stress/difficulty and permission semantics, with
off-mode equivalence and unchanged failure thresholds. Demonstrate actual earned
inputs and a measured survival/failure protocol through the application. Do not
delete archive evidence or fabricate deaths to satisfy roguelite language.

## Dispositions: what this review does not invent

| Topic | Current disposition |
| --- | --- |
| Offline “simmering” | DR0021's original language is stronger than today's behavior, but the [2026-07-07 five-notices audit][five-notices] 56-64 explicitly interprets it as framing: eras run when requested, no background simulation should exist. The [2026-10-04 Keeper report][keeper-report] 178 preserves that disposition. Independent reviewers initially missed this record; main review corrected it. **No absence/catch-up implementation is queued.** Reopening requires an explicit product decision, not treating an old metaphor as new scope. |
| Hidden service or remote continuity | No unattended agent, scheduler, remote executor or credentials were installed. Parent owns supported remote setup and single-writer coordination. Local absence semantics and agent remote execution are separate matters. |
| New research methods | CPPN rejected / shape grammar watch and other historical generator decisions survive. Unbuilt NCA/Lenia/MRF/embedding/personality systems are not automatically product requirements. Learned linear repair is real; DR0041's withheld rich-regrowth adoption remains a legitimate refusal. |
| Default learning | R3/DR0066 REFUSE survives. No inherited trained Q-table for new lives; no weakened threshold or diagnostic-as-gain claim. |
| Animation and identity | Engine-projected clips are adopted. Mixed-species schema identity is a named future reopener, not a prerequisite for the present creator workflow. |
| Community and distribution | Usable local pack creation/exchange is incomplete and queued. Registry, hosted service, moderation, signing identity and public publication remain separate owner decisions. |
| Historical families | Preserve E5 definitions/cohorts, seven-axis niche-history limits and actual ancestry. No migration or invented family linkage is authorized. |
| Human and native evidence | HTTP timing is a proxy, not human usability. Native process launches, source pygame events and native keyboard interaction are different evidence. No native keyboard or fresh browser-interaction claim is made here. |

## Evidence, verification and next action

Retained [evidence manifest][manifest] hashes the exact diagnostic scripts and
outputs supplied by the reviewers. Workshop and campaign probes used temporary
fixtures; the engine probe used in-memory inputs; the packaging probe used read-only
resource resolution. They are deliberately labeled diagnostics, not new experiment
triads, acceptance tests or default-adoption evidence. Some probes encode local
paths or W5 fixture prerequisites; read them before rerunning and use only the
existing environment. No retained owner save was modified and no server was left
running. Initial temporary setup failures are not counted as product failures.

The checkpoint verifies Markdown/source references, structured evidence, the exact
queue archive, and the 4,188 baseline file identities, allowing only the intentional
documentation changes listed in its final preservation result. It does not alter
the prior runner's W5 closure or invent passing results for X1-X8. Each future
implementation needs its own registered contract, actual RED/GREEN evidence,
appropriate focused checks and the established full local closing gate.

Final preservation result: **4,184/4,188 existing tracked files are unchanged**;
the four intentional edits are ONBOARDING, the research index, local-cycle guidance
and the live TODO. The old queue archive matches exactly, 63 report source links
resolve, all nine manifest entries match their hashes, four retained diagnostic
scripts parse, structured outputs parse, and `git diff --check` passes.

**Remaining workflow gate:** the actual post-review `develop --status` returns
`slice=w5-integrated-finish`, `phase=polish`, `running=null`,
`full_current=false`, `local_complete=false`. The new retained diagnostic/evidence
files and the local-cycle Markdown pointer are in the runner's verified inventory.
Its incoming-registration exception permits only the new contract and registry;
it does not admit this additional evidence (`development.py:136-164`). Thus the
historical W5 pass is preserved, but cannot authorize a new slice on the changed
inventory. No full sweep was rerun during this review. Under the next implementation
delegation, refresh the retained slice through the supported full verification gate
before starting X1; do not edit runner state, remove evidence or broaden the
exception to force a pass. The exact command and inventories are in `resume.json`.
This is a runner freshness requirement, not an observed application regression.

**Next action after this review handoff:** reread actual Git state and
`.development/product-checkpoint-2026-10-05/resume.json`, then resolve the recorded runner freshness gate and take X1 into REVIEW.
Preregister its continuity/recovery contract and reproduction cases before RED.
The queue records integrated dependencies so this can continue autonomously under
the next implementation delegation. This turn stops at the requested review and
plan. Commits, synchronization and pushes remain the owner's actions.

[agents]: ../../AGENTS.md
[onboarding]: ../../ONBOARDING.md
[owner-design]: ../../.depreciated/v0.0.1/01-design.md
[research]: ../../docs/project-research/research.md
[validity]: ../../docs/project-research/validity-research.md
[workshop-design]: ../../docs/mecha-workshop/mecha-workshop-design.md
[dr17]: ../decision_records/0017-recalibration-engine-game-duality.md
[dr21]: ../decision_records/0021-game-loop.md
[dr22]: ../decision_records/0022-storage-module.md
[dr24]: ../decision_records/0024-grid-schema-animation-species-resolution.md
[dr33]: ../decision_records/0033-game-front-end-technology.md
[dr35]: ../decision_records/0035-pack-distribution-at-alpha.md
[dr57]: ../decision_records/0057-stage2-generator-arms-dispositioned.md
[dr66]: ../decision_records/0066-playable-qtable-opt-in.md
[dr74]: ../decision_records/0074-original-best-elite-recording.md
[genome-schema]: ../grid_genome/grid_genome.schema.json
[slip-schema]: ../slip/slip.schema.json
[generate]: ../../packages/mecha_engine/src/mecha_engine/generation/generate.py
[wfc]: ../../packages/mecha_engine/src/mecha_engine/generation/wfc.py
[live]: ../../packages/mecha_engine/src/mecha_engine/runtime/live.py
[evolve]: ../../packages/mecha_engine/src/mecha_engine/runtime/evolve.py
[threads]: ../../packages/mecha_engine/src/mecha_engine/learning/threads.py
[switchboard]: ../../packages/mecha_engine/src/mecha_engine/learning/_switchboard.py
[lifecycle]: ../../packages/mecha_engine/src/mecha_engine/lifecycle/simulate.py
[metrics]: ../../packages/mecha_engine/src/mecha_engine/archive/_metrics.py
[archive-store]: ../../packages/mecha_engine/src/mecha_engine/archive/store.py
[store]: ../../packages/mecha_engine/src/mecha_engine/storage/store.py
[session]: ../../game/src/mecha_game/session.py
[campaign]: ../../game/src/mecha_game/campaign.py
[covenant]: ../../game/src/mecha_game/covenant.py
[covenant-io]: ../../game/src/mecha_game/covenant_io.py
[app]: ../../game/src/mecha_game/app.py
[era-plan]: ../../game/src/mecha_game/era_plan.py
[niches]: ../../game/src/mecha_game/niche_history.py
[original]: ../../game/src/mecha_game/original_recording.py
[replay]: ../../game/src/mecha_game/replay.py
[packets]: ../../game/src/mecha_game/packets.py
[packs]: ../../game/src/mecha_game/packs.py
[server]: ../../workshop/server/workshop_server.py
[grid-editor]: ../../workshop/grid_editor/grid_editor.html
[slip-editor]: ../../workshop/slip_creator/slip_creator.html
[cleanliness]: ../../data/slips/valid/slip_v2_cleanliness.json
[cli]: ../../tools/mechas_cli/src/mechas_cli/app.py
[game-cli]: ../../tools/mechas_cli/src/mechas_cli/workflows/game.py
[workshop-cli]: ../../tools/mechas_cli/src/mechas_cli/workflows/workshop.py
[build]: ../../game/build_release.py
[game-package]: ../../game/pyproject.toml
[engine-readme]: ../../packages/mecha_engine/README.md
[ci]: ../../.github/workflows/ci.yml
[local-cycle]: ../../docs/development/local-cycle.md
[generation-contract]: ../package_specs/mecha_engine_generation_contract_gate.md
[hard-regime]: ../experiment_reports/2026-07-05-stress-regime-evolution.md
[soak]: ../../labs/game_loop/session_soak.py
[five-notices]: ../experiment_reports/2026-07-07-five-notices-audit.md
[keeper-report]: ../experiment_reports/2026-10-04-keeper-loop.md
[queue]: ../../sunsetted/TODO.md
[old-queue]: ../../sunsetted/complete/TODO/37/TODO.md
[inventory]: 2026-10-05-product-checkpoint/source-inventory.json
[manifest]: 2026-10-05-product-checkpoint/evidence-manifest.json
[workshop-result]: 2026-10-05-product-checkpoint/mecha-workshop-audit-result.json
[campaign-result]: 2026-10-05-product-checkpoint/mecha_campaign_audit_results.jsonl
[engine-result]: 2026-10-05-product-checkpoint/mechagotchi-current-engine-review.json
[delivery-result]: 2026-10-05-product-checkpoint/mechagotchi-detached-resolver-review-result.txt
