# Experiment Report: Species Class + Visual Grammar Gain Their Authoring Faces (Cycle 20 · SHARED · J5)

Date: 2026-07-20

## WHY

The Phase-H gate named it, H4's honest remainder queued it, and the
Phase-I gate carried it standing: **`visual_grammar` and
`species_class` were the last un-authored SLIP ladder fields** — ratified
by DR 0012 (rung T3.5), judged by the promoted authority since DR 0027,
worn by every zoo profile, and yet authorable nowhere. Cycle 20 is the
generative-range cycle: J2 (DR 0038/0039) taught the breeding and repair
surfaces to spell the full ratified vocabulary — so the workshop's
constraint surface must be able to author over that same range, or the
authored range and the generated range stay strangers. J5 is that face,
under the H-phase pattern: authored visually, validated live by the
engine's authority, refusals verbatim in the page.

## WHAT

**The slip creator gains the species & visual grammar panel**: a
`species_class` text input (blank = the field stays off; the honest hint
names the lowercase-identifier shape), an **allowed-materials** toggle
group over the schema's seven-value material vocabulary (none selected =
unrestricted; naming any narrows the species to exactly those), and an
**animation-vocabulary** toggle group over the engine's five clip states
with the idle-mandatory constraint stated in the hint. Selections emit in
the schema's canonical vocabulary order; setting any of the three writes
`slip_version 0.2.0` (the ladder rule); `buildProfile`, load-restore, and
New-reset all carry the fields; every change flows through the existing
live `/api/slip/validate` loop, so the authority's refusals — e.g.
`species_class must be a non-empty lowercase identifier`,
`visual_grammar animation_vocab must include idle`,
`visual_grammar allowed material not in vocabulary: chrome` — reach the
page verbatim, as pinned.

**No server change was needed** — `validate_slip` (the promoted
`mecha_engine.slip` authority) has judged both fields since DR 0027, and
`_slip_validate`/`_slip_save` pass profiles through verbatim. The new
tests pin that truth end to end: a species-grammar profile validates,
saves, and round-trips exactly; the three refusals are verbatim; the
0.2.0 version gate holds for both fields.

**The authored range meeting the generated range, pinned**: the
grid-compat pin saves a real creature (the committed seed
`mg_seed_001`, whose cells carry `soft`/`glass`/`hard`) into the
workshop and authors a grammar allowing only `soft` and `glass` — the
compatibility verdict refuses it with the authority's own words,
`material not allowed by SLIP visual grammar: hard`, on the page's
compatibility chips. The constraint surface the game's alignment check
enforces (`is_grid_aligned`) is now the same surface a player can
author.

## Verification

```powershell
PS> python -B -m unittest discover -s workshop/tests -p "test_workshop_server.py" -k SpeciesGrammarAuthoringTests
.F...
FAIL: test_serves_the_species_grammar_controls
AssertionError: 'species-class' not found in '<!doctype html>…'
Ran 5 tests ... FAILED (failures=1)   # RED: the page serves no species/grammar controls;
                                      # the four authority pins were already green and say so
# after the panel:
Ran 5 tests ... OK
PS> python -B -m unittest discover -s workshop/tests -p "test_*.py"
Ran 88 tests in 151.017s ... OK
PS> node --check <extracted slip creator script>
JS SYNTAX OK                          # 488 lines
```

## HONEST REMAINDER

1. **The panel is server-verified, not click-tested** — the human
   first-session pass stays prepared-not-blocking (H5's standing gate),
   as with H2/H3/H4.
2. **The animation vocabulary is the engine's five** (`idle`, `blink`,
   `sleep`, `beg`, `ill`); per-clip choreography beyond the recorded
   tables remains an engine DR when a consumer asks (the Phase-H/I
   standing remainder, unchanged).
3. **`allowed_materials` constrains cells the creature has** — a grammar
   cannot demand a material be present, only refuse ones that appear;
   a "required materials" rung would be a new schema ladder decision
   (DR 0012's process), not workshop drift.

## Sources

- `audits/TODO.md` (cycle 20 J5), `research/experiment_reports/2026-07-19-phase-h-gate.md` + `2026-07-20-phase-i-gate.md` (the named remainder), `2026-07-19-behavior-editor.md` (the H4 pattern this mirrors)
- `workshop/slip_creator/slip_creator.html` (the species & visual grammar panel) + `workshop/tests/test_workshop_server.py` (SpeciesGrammarAuthoringTests)
- `research/slip/slip.schema.json` (the T3.5 fragments), `research/decision_records/0012-slip-schema-extension-ladder.md` (the rung), `0027-slip-module-disposition.md` (the authority)
- `packages/mecha_engine/src/mecha_engine/slip/authority.py` (`_validate_visual_grammar`, the species_class check, `is_grid_aligned`'s material grammar)
- `data/seed_grids/mg_seed_001.json` (the compat pin's subject), `data/slips/zoo/` (the fields worn by the committed zoo)
- `research/experiment_reports/2026-07-20-vocabulary-alphabet.md` (DR 0038/0039 — the generated range this authoring face meets)
