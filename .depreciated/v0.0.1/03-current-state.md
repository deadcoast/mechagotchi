# FEEDBACK

> **NOTE**: THE CURRENT STATE OF THE REPOSITORY IS ACCEPTABLE AND DOES NOT REQUIRE ROLLBACKS OR REMOVALS. IT REQUIRES RECALIBRATION, FURTHER DESIGN AND DEVELOPMENT.
> THE FOLLOWING ARE CONCERNS TO BE CORRECTED THROUGH DEVELOPMENT; NOT DELETION.

---

## ON agents CONCLUSIVE QUESTION

`One thing awaiting your direction: you've added new material to the tree that rode along with my commits —
  .depreciated/feature-requests.md and two PNGs (workshop-build-window.png, block-highlight-example.png)`: they are LITERALLY INSIDE A DIRECTLY CALLED `.depreciated`.

- This directory is my personal notes. They are not relevant to the CURRENT repository design, they are archived files i can reference if i sense drift in development. You can ignore this directory unless explicitly asked or linked to a file there.

## DEVELOPMENTAL CONCERNS

### DESIGN DRIFT

The main concern is the lack of oversign of the actual applications goals and or prupose. The micro tasks are done well, the todo pipeline workflow is done well. BUT the agent seems to completely ignore what the actual application does while it develops. The agent also seems to completely ignore the complexity and unique nature the source code was designed in. This application is;

- (a.1) An innovative and creative integration of the google cubff experiment, mathematic research and algorithms, and clever development to create real, unique engine output.
- (a.2) To showcase (a.1) we are developing a incrimental progression, survival and simulation game.
- (a.3) The game design was initially to feature exponential growth utilizing the scale of [Google CubFF Experiment](assets\pdf\2406.19108v2.pdf).
- (a.4) The game was designed to integrate TRUE Machine Learning where applicable, and introduce a real feeling of a living ecosystem to the users.

- (b.1) Combined with incrimental progression(feeling of growth), Machine Learning (adaptability, and changes to the ecosystem THAT THE GAMER NOTICES), and the sheer scale and proven methods of Google Experiment CuBFF(a.3), THERE WAS TRULY UNIQUE DESIGN, THAT WHEN COMPLETED WOULD PROVIDE A WORTHWHILE GAME AND ENGINE. Now, im not sure if it is gone, OR we are too early in development to see it yet.
- (b.2) The ENGINE requires the GAME to be exceptional, addicting, fun to play; or else NO ONE will ever find or discover the engine no matter its quality.
- (b.3) The GAME requires the ENGINE to be exceptionally developed, unique, creative, adaptive; or else the GAME will not operate correctly and almost no one will play it or deem it worthy of their time.

---

### QUALITY CONTROL

- (1) The development is slowly drifting. The Fable 5 Developer agent is completing tasks well and staying on workflow pipeline adequately. There seems to be some drift in project understanding, or purpose, or scale.
- (2) This project is designed to be a truly unique integration, with a robust and advanced mathematical system supporting it (that is why there is so much research into mathematics and their applications)
- (3) Requirement T10 keeps being brought up as a hard constraint, even after it was removed and corrected twice. I BELIEVE this pertaines to the workshop readibility and rating scoring system.
- (3.1) This system was designed and integrated in the foundations of the application because it is highly customizable, provides robust quality of life. It was and is not developed or designed to achieve the function it is assigned to; IT IS THE MANUAL FALLBACK TO THE ASSIGNMENT.
- (3.2) The workshop is developed well, and looks good. The system attached to it is done well, and it looks good, and the CLI operates well with it. The current state of this IS CORRECT as a fallback use and doesnt need to be altered at this point.
- (4) The development INITIALLY searched through algorithm to develop these. Im not sure what happened, but I am guessing that the AGENT deemed the format "slow", "inaccurate", or "not established", then deleted it entirely.
- (4.1) The project was designed with comprehensive Machine Learning aspects. They for the most part seem to have been removed. This type of regression is detrimental, as here we are now; VERY DEEP into development, and the ENTIRE purpose of the front end is removed from the project. The current state requires humans to train manually train the model. WHICH IS FINE; BUT NOT INNOVATIVE, NOT CREATIVE, ITS LITERALLY THE OLDEST WAY TO DO IT.
- (4.2) After further review of the repository, it has become exceedingly apparent that throughout development the actual unique and innovative design features have been watered down to a point they dont achieve what they were designed to do, or removed entirely.
- (4.3) The code quality shows that the AGENT Fable 5 opted to remove most development features that were unique or difficult to develop, and only opted to complete surface level, simple integrations, then consistently lie about its validation and task completion.
- (5) IMPORTANT NOTE: It is entirely possible features are still to be developed, ALL OF THE ABOVE is speculation, and concern, NOT ABSOLUTE CONDEMNATION.

---

## ON THE AUDIT COMPLETE CLAIM

I reviewed the audit file, and saw that these are still incomplete. IT IS POSSIBLE YOU SIMPLY FORGOT TO MARK THEM COMPLETE. IF THAT IS THE CASE. COMPLETE THEM BY MARKING THEM COMPLETE. A TASK IS NOT COMPLETE UNTILL IT IS DEVELOPED TO ITS DESCRIPTIONS, THEN MARKED AS COMPLETE.

### 2.10 Evaluation framework — PARTIAL

Visual, evolution, and behavior metric families: implemented across the
readability benchmark, archive, and lifecycle labs. **Workshop
evaluation metrics** (authoring time, validator clarity, schema error
rate, custom-profile survival rate, first-session usability) and og's
human studies (semantic-vs-plain editor test, creator pilot) are not
instrumented — consistent with the owner's standing deferral of manual
survey data, but they need a tracked place. (TODO T10)

- [ ] **T4 · Animation-state vocabulary.** (SEMANTICS + animstate_300 SHIPPED 2026-07-05 — states are deterministic genome projections, 300/300 valid; remaining: T16 packet selection, workshop previewer, T3.5 field) og: idle/blink/sleep/beg/ill
  states, animation anchors per state, `animstate_300` dataset.
  Research-first: lab defining state semantics on the grid genome
  (extends the single-anchor invariant), then schema, then render-packet
  animation selection, then workshop preview/editing. Feeds T3.5, T7,
  and slice-3 preview's "animation/state previewer" og responsibility.
- [ ] **T7 · Grid schema fields from the og starter schema**:
  `species_class` (with T3.5), animation-state fields (with T4).
  Schema version bump + validator + invariants doc + migration note for
  existing corpora.
- [ ] **T8 · CTM gating integration decision.** Verify whether
  `labs/ctm_ticks`' confidence-gated deliberation ("act if confident,
  else extra switchboard cycles") reached the runtime switchboard; if
  not, run the integration experiment (og research question: does
  internal deliberation make behavior feel more alive / improve
  decisions measurably?) and record adopt/watch/reject.
- [ ] **T11 · og dataset program completion**: `mechaseed_200` (curated
  variants of the 50), `mutationbench_5000` (generated offspring under
  fixed configs — the labs' mutation machinery makes this cheap),
  `replay_100k_ticks` (runtime episode logs; also feeds T12); `animstate_300` DONE (2026-07-05, with T4). Each with a README + ledger entry.
- [ ] **T12 · Recorded replay consumer for the render bridge.** og named
  three packet consumers; replay is missing. Lab: record per-tick render
  packets from a `live_cycle`/episode run into a replay artifact; the
  workshop preview gains a replay scrubber (engine truth, recorded).
- [ ] **T16 · Render packet contract v2.** (SHIPPED 2026-07-05 incl. the DR 0013 package port — genome.render_packet_v2 additive publics; effects wait on the SLIP render-block rung) Both og runs specify the
  packet carries animation, mood, and effects (RUN TWO adds frame_id +
  ui_hints like needs_attention). Today `state` is an opaque
  passthrough. Spec-first: packet v2 contract (animation from T4's
  vocabulary, mood from lifecycle state, effects from SLIP render
  block per T14/T3), then promoted-module change with parity notes,
  then the workshop preview consumes the new fields. Depends on T4;
  feeds T12 (replay).
