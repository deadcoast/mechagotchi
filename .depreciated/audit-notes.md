# Audit output notes for reference

-------
## [01]

```bash
git log --oneline -5; Write-Output "=== tree ==="; git status --short

029f468 L3: the scale geometry is NOT stale - it is SPLIT. The task's own premise tested first, refuted, and the measurement surfaced what nobody had written down.
5e9dff5 L2: the documented lineage-dominance clause, judged at last - PASS at 0.2848, and the concentration it CANNOT see reported beside it.
7a2c67d L1: the refusal-cause histogram - the cheapest instrument in the queue, and it corrected DR 0042's reading of its own number TWICE.
5c4bee3 K6: THE PHASE-K GATE IS GREEN - the vocabulary settles its stack, and the survey finds a documented gate clause that was never judged.
b4fd76b feat: Implement advisory covenant budget in workshop
=== tree ===
```

L3 is committed (029f468), tree clean. It did not go the way the plan expected, and the surprise is the valuable part.

What L3 found:
- The geometry is not stale — the premise I wrote into the cycle-22 plan was wrong. I tested it before doing anything else: E1's derivation protocol, re-run verbatim under today's code, reproduces the committed frozen edges exactly — drift 0.0 on all three axes. That zero is meaningful rather than trivial because the bar was measured, not assumed: deriving the same recipe twice at different seeds moves the edges by 0.0102 on their own, so I had a real noise floor to judge against. Verdict: withhold_regeneration.

The reason is in the history, and I verified it rather than inferring:
- niche_scale_archive_stage0.json was regenerated at the DR 0038 commit itself (f8c171b). The edges were never pre-vocabulary, and today's derivation population carries the full ratified alphabet — 100% of its 600 grids carry the motion trio.
- So K3's measure-thin windows are real. They're a genuine property of the silhouette-entropy distribution, which packs six of its eight octiles into a 0.046-wide band — not an artifact of stale calibration. The quantization hypothesis for [4,7,4] hardens, which is exactly the outcome the plan named for this branch.

The thing nobody had written down:
- Testing the premise surfaced something bigger: the repo runs two scale geometries at once.
- The evolution loop and the E4 gates consume the frozen edges, derived from the corpus train split. The reachability probe and the occupancy instrument derive their edges live from all 50 seeds, every run. Same protocol, different calibration population — and the two edge sets differ by up to 0.0375, which is 3.7× the measured sampling control, so the difference is real and not noise.

That means these numbers are counted in different coordinate systems:

- 460/512 occupied, coverage 0.8984, QD 404.6, the E4 mean 0.8865 — incumbent geometry
508/512 proven reachable, and the support ceiling 460 — probe geometry and they have been read against each other in prose.
- K2's headline — that 460 occupied niches is "exactly" the support ceiling — compares across the two.
- The coincidence is real; the word exactly isn't justified. K3's cited neediness window `[0.3825, 0.3975)` is likewise the probe's octile, where the frozen geometry's is `[0.3825, 0.395)`.

I want to be precise about severity:

- this is a latent hazard, not a present error. Each instrument is internally consistent, no artifact contains a wrong number, and I rewrote none of them.
- What's wrong is reading across them — so K2's report, K3's report, and the Phase-K gate each got a dated qualifying note, and the gate's remainder 4 got a correction for the bad premise I put there this morning.

I deliberately did not repair the split:
- Making the surfaces agree means re-deriving edges, which silently changes what every historical coverage number means. That needs its own gated record.

One measurement is honestly weak and I flagged it first rather than burying it:
- The third recipe — the stream the archive is actually filled from — produced only 120 of 600 candidates, because its parents here are the raw seed corpus that L1 showed is largely SLIP-illegal.
- It bounds the question; it doesn't settle it. Measuring it properly needs the loop's steady-state elites as parents, which the L2 lineage seam already exposes — cheap, and it decides whether the geometry is calibrated on the right population at all.

Four commits this session (K6, L1, L2, L3), sweep green at each, 2,233 artifacts valid. Next in the queue is L4 — animation_density judged as a candidate axis — which after L3 must now also state which of the two geometries it would join.

-------
## [02]

```bash
git show --stat df68ca7 | Select-Object -First 12

OUT
commit df68ca71d19c7a82ad30397da2865e44a9964df8
Author: deadcoast <ponydriverco@gmail.com>
Date:   Sun Jul 26 05:43:45 2026 -0700

    feat: Add current state, custom workflow, and feature requests documentation
    
    - Introduced a new markdown file detailing the current state of the repository, emphasizing the need for recalibration and further development.
    - Created a custom workflow document outlining the steps for reviewing and updating project documentation and tasks.
    - Added a feature requests document for the Mecha Workshop and Draw-on-Evolution functionalities, including visual examples and specific enhancement requests.

 .depreciated/audit-notes.md                      | 48 ++++++++++++++++++++++++
 .depreciated/{ => v0.0.1}/01-design.md           |  0
 ```

That commit touched only .depreciated/ — your personal archive — so no collision. Per your standing ruling I haven't acted on its contents, though I'll note it now contains an audit-notes.md and a feature-requests doc (Mecha Workshop, Draw-on-Evolution); say the word if you want those pulled into the queue.

L4 — the result
animation_density earns its place on every machine gate, and still cannot be adopted. That combination is the finding.

First, the honesty that shaped the whole slice. The task said "the documented axis," but animation_density appears in the documentation exactly once — as a value in a JSON example at deep-research.md:530. No formula, no range, no threshold, anywhere. So I did not implement a documented axis; I proposed one and labelled the definition CHOSEN. Calling it documented would have been L1's error in K2 repeated.

The proposal, grounded in engine truth: the fraction of live cells whose role the clip model animates — with the animating role set (antenna, sensor, effect, limb, joint, decoration) read from clip_model at import, never copied, so a change to the engine's clip tables moves the axis with it. A pin enforces that.

The gates, pre-registered before the run:

| Gate | Bar | Measured |
|--|--|--|
| A1 spread | supports 8 octiles | 7 distinct edges, range 0.011–0.600 — pass |
| A2 independence | `\|r\| < 0.5` | 0.173 max (complexity just 0.068) — pass decisively |
| A3 discrimination |	`≥ 0.20` | 0.543 — pass at 2.7× the bar |
| A4 cost |	`reported, not gated` | occupied 289 → 448; coverage 0.5645 → 0.1094 |

A3 is the number that matters. Among the 656 population pairs sharing the same three-axis bin — creatures the current geometry cannot tell apart at all — 356 (54.3%) land in different animation octiles. More than half of the archive's present indistinguishability is animation structure it has no coordinate for. And the axis is nearly orthogonal to everything already measured, so that's genuinely new information rather than a restatement of symmetry.

The cost is real and I put it in the artifact rather than leaving you to derive it: the fourth axis reveals 159 more distinguishable classes while spreading the same population across eight times the space, so coverage as a fraction falls five-fold.

Why it still isn't adopted. The documented selection criterion isn't a machine measure — deep-research.md:204 requires a descriptor set "selected with inter-rater interpretability ≥ 0.7", which needs the human panel you've deferred. I blocked that clause explicitly and substituted no proxy; the transducer study's labelled readability proxy is precisely why. Verdict: adoptable_pending_blocked_clause. The honest conclusion is narrower and still useful — the axis is worth the panel's time if one is ever scheduled.

Two smaller things I want on the record. Per L3, the axis had to name which geometry it would join (the incumbent, frozen train-derived one). And the realised-motion observation needed careful reading: realised idle density is 0.0417 against a potential 0.1924, but that gap is mostly the idle clip's own schedule — CLIP_LIMB_STEP["idle"] and CLIP_JOINT_FLEX["idle"] are all zeros, so limbs and joints never move during idle — not evidence that three-quarters of animating cells are collision-blocked. I also adjusted two pins during implementation and said so in the report: one was case-sensitive, and I moved the realised-motion invariant off a hand-built stub onto real committed seed creatures, which made it stronger.

Five commits this session (K6, L1–L4), sweep green at each, 2,234 artifacts valid, 219 archive-lab tests. Next is L5 — density-as-pressure (DR 0043 clause 2), the GAME's own consumer decision, which needs its own decision record and the seam law honoured.

-------
## [03]

> USER_MESSAGE

````md
# NEXT STEPS AND REFRESHER CALIBRATION

> FEEDBACK: GOOD WORK SO FAR.
>> NEXT_STEPS: L5; density-as-pressure (DR 0043 clause 2), the GAME's own consumer decision, which needs its own decision record and the seam law honoured.

## [PRINCIPLE-ENGINEER] agent for [MIVIM] project

### BOUNDARY PUSHING INTEGRATIONS AND IMPLEMENTATIONS

> M I V I M · Modular Innovations, Versatile Integration Methods
>> :dev_goals:" Creating methods, features, applications that are novel and noticed, featured by github pages, development blogs, influencer techs. Industry leading creativity that cant be ignored.
>> :development_style: Novel, Creative and Unique methods supported by rigerous research, validation and mathematics.

---

> Your methods for MIVIM-DEVELOPMENT utilize two layers (a, b) to balance eachother.
>> (a) CREATIVITY IN UNIQUE INTEGRATIONS "We develop to lead industries, our PRINCIPLE-ENGINEER AGENTS are HAND-SELECTED for their ABILITY to balance their [CODING-ABILITIES](SCIENTIFIC, UNIQUE, CREATIVE) when working on boundary pusshing, unique and novel applications. 
>> (b) RESEARCH-AND-VALIDATION "The sstem is created created to keep (a) methods grounded in reality and practical use for our simulation. These two(a, b) aspects work in harmony togeter. 
>> (c) BALANCE in CREATIVE, UNIQUE, REALISTIC and NOVEL DEVELOPMENT;
>>> (c.1) `(a) :: CIRCUMVENTS :: (b) from  : "creating standard, mundane half developed applications, templated examples framed as requested development."`
>>> (c.2) `(b) :: CIRCUMVENTS :: (a) from : "creating claims without use, support, or validation. creativity must be balanced in reality with provable facts supported by mathematics and displayed in the unique, novel simulation game we have created."`

---

[THINK ABOUT] what your TASK provides, HOW the TASK operates for relevant purpose operates in the INTENDED use.
````

-------
## [04]

L5 is committed (308910c), tree clean. This one turned out to be the most interesting slice of the cycle, so let me be precise about what it actually did.

The defect was a mechanism, not a bug
Before writing anything I traced why I3's inversion happens, and it's structural. The promoted pressure math is 0.45·instability + 0.35·semantic_pressure + 0.20·instruction_diversity. On the checkpoint path replication_scores and lineage_events are structurally absent — the format cannot store them. With those terms at zero, pressure rides almost entirely on entropy and instruction diversity, and both of those fall as a soup organizes.

So the engine reads organization as calm. Every channel it can see decreases while every channel that would rise is missing. That's why a Keeper met the era with 129,211 replicators as gentler than the one with 2 — no number invented anywhere, and the player still shown the opposite of the biology.

The fix was derived, not tuned
Instruction density is the one carried channel that rises with organization — which makes it the specific missing counterweight rather than a knob. And it has a known random expectation, so it needs no calibration: a random tape of length n carries n × 10/256 instruction bytes, giving a ratio that is 1.0 at chance. I mapped that against a ceiling of 256/10 = 25.6 — the all-instruction maximum, which is independent of tape length because it's a property of the bff_noheads alphabet, not of the corpus. Weight pre-registered at 0.5.

The DR wrote the prediction down before the run — a ≈ +0.041 multiplier swing, with the explicit words "predicted to just barely flip it — and it may not." Measured swing: +0.040617. Right to four decimal places, with no adjustment of any kind. That agreement is the real evidence the formulation describes something rather than being fitted to a wanted answer, and had it landed on the other side of zero the DR committed in advance to recording the refusal.

early	post-takeover	gap
checkpoint, rider off	0.818009	0.783716	−0.034293
checkpoint, rider on	0.857880	0.864204	+0.006324
callback (lit channel)	0.772726	1.034884	+0.262158
All five gates met: the inversion corrected (G1), agreement with the lit-channel ground truth (G2), all sixteen committed game artifacts regenerating byte-identical with transducer/runtime/package suites passing unmodified (G3), replication_rate and lineage_churn still exactly 0 so nothing is synthesized (G4), and the documented (0.5, 1.6) band holding (G5).

The limit, stated with the win
The corrected gap is +0.0063 against the ground truth's +0.2622 — about 2.4% of the magnitude. Density recovers the direction of the biology, not its force. The checkpoint forecast now points the right way and remains a much quieter instrument than the callback path. I put that number in the report, the DR, the artifact and the commit rather than letting anyone infer it, because reading +0.0063 as "the checkpoint forecast now conveys post-takeover ferocity" would be overreading it.

Two scope notes: the rider is off by default in the engine — this record adopts the capability and proves it at the consumer; which forecast keys enable it in a shipped client is a client decision, and the era bench is unchanged. And the 0.5 weight was fixed in advance and never revisited; any other weight would need its own record explaining why it isn't curve-fitting to a wanted feel.

Six commits this session (K6, L1–L5), sweep green at each, now 2,235 artifacts. Your IDE also landed two commits of its own alongside mine (coderabbit config, and audit-notes updates including a section on animation_density) — I haven't acted on those.

Cycle 22 has one task left: L6, the Phase-L gate — consolidate L1–L5, archive to audits/complete/22/, and plan cycle 23 from the documentation.

-------
## [05]

````md
# MIVIM DEVELOPMENT: NEXT_STEPS

> {"id":"claude-opus-5"}, {"dev_id":"[PRINCIPLE-ENGINEER]"}, {"org":"MIVIM"}
>> NEXT_STEPS:  L6, the Phase-L gate — consolidate L1–L5, archive to audits/complete/22/, and plan cycle 23 from the documentation.
>
> M I V I M · Modular Innovations, Versatile Integration Methods
>
>> :dev_goals:"Creating methods, features, applications that are novel and noticed, featured by github pages, development blogs, influencer techs. Industry leading creativity that cant be ignored."
>> :development_style:"Novel, Creative and Unique methods supported by rigerous research, validation and mathematics."
````

-------
## [07]

> {"id":"claude-opus-5"}

```text
I'll wait for the sweep rather than poll it.

M1 is complete and documented; the full sweep is the last gate before I commit it and move to M2.

What shipped:

Code — elite_population_measures.py + 36 pins, and the loop's third additive observation seam collect_elite_grids (byte-identical when off, proven alone and composed with L2's seam).
Evidence — data/archives/elite_population_measures_stage0.json, JSON-valid, produced twice with every measured value identical.
Docs, same change — the experiment report with RED/GREEN/lab-invocation verification blocks and pasted output; the algorithm-card Evolution entry; the research/README.md ledger entry; the TODO check-off; CHANGELOG and ONBOARDING state lines; and a dated note beside L4's original remainder rather than a rewrite of it.
The result worth flagging: M1 partly deflated the premise its own cycle was planned on. Phase M was built on "every instrument measures a different population from the one the archive is filled with," and for the three incumbent descriptor axes that difference does not clear a measured bar — highest ratio 1.70 against 2.0. I recorded that as a deflation rather than dressing it up, and I did not widen the bar to capture the one visible shape (the depleted top symmetry octiles, 48 and 28 against a flat ~57). That stays "suggestive, not established."

The finding I'd carry forward is methodological and it was measured, not argued: requiring a control for both population types — the expensive one being a second full loop — is what stopped animation_density being reported as a decisive material difference at 5.14× the bar. Against the correct control it's 0.85. The cheap-control design would have published a false positive, and the axis that looked most different turned out to be the least trustworthy.

Two things this hands directly to later tasks: M3's denominator is now exact (48 of 460 elites, 10.4%, are bootstrap creatures — so the fix it must gate trades against about a tenth of coverage in the worst case), and L4's A2 independence margin halves on the archive's real inhabitants (max |r| 0.173 → 0.350, still inside its bar) — a reason for the deferred human panel to look harder, not a machine substitute for it.

One limit I chose not to fix: TVD's finite-sample bias, with the derivation-vs-elite comparison mixing sizes (600 vs 460). Correcting it now would mean changing the statistic after seeing the numbers, which this repo forbids — so it ships as a named remainder, and it cuts toward smaller true differences, so it doesn't threaten the verdict.

Next after the commit: M2 — the geometry split, decided by record, which is a DR-bearing slice rather than an instrument.
```

-------
## [08]

-------
## [09]

-------
## [10]
