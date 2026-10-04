# Q2: Covenant-authored cleanliness

Date: 2026-10-04. Cycle 27 Q2. Decision: DR 0063.

## Why

The adopted DR 0059 mechanic could be enabled only by a constructor keyword.
The covenant could not author it, and an explicit empty game override was
collapsed into None. Source review found another concrete gap: the session's
clean verb and readout had never been connected to the playable window.

## What

The Q2 contract was committed at `2cb9bd1` before implementation. SLIP v0.2
now admits the optional strict `mechanics.cleanliness` boolean. Absence, an
empty object or false is off; frozen v0.1, null, unknown keys and non-booleans
are refused. A supplied mechanics sequence overrides the validated profile;
an empty sequence disables. `run_episode` resolves that state before deciding
whether a clean stream is legal. Invalid profiles cannot be bypassed.

The game preserves inheritance and explicit disable through save/resume and
succession. An enabled player sees the engine value and presses **G** to queue
cleaning for the next tick. Off-mode controls and footer keep their shape.
No mechanic parameter, reward, autonomous action, danger threshold, default
covenant or Q-table promotion changed.

## Findings

The contract verdict is **adopt_authorship**, with all thirteen checks true.
The new artifact reports 32 adversarial profiles and 192 verdicts across the
authored schema, committed generated schema, Pydantic, package, grid lab and
standalone lab. Generated-schema parity with current generation is separately
pinned. Both strict boolean/version rules and input preservation hold.

The preimplementation baseline, captured from `2cb9bd1` before changing the
engine, contains all four incumbent valid profiles, including the default game
covenant and its actual 16x16 grid. Initial states, twelve 72-tick episodes
(idle, switchboard, random seed 123), game snapshots and save payloads reproduce
their recorded SHA256 values under canonical UTF-8 JSON. This is canonical
serialized identity, not a claim about OS newline encoding. Empty/false v0.2
blocks also produce identical states/episodes to absence.

The unchanged DR 0059 study reproduces its entire metrics and decision, including
switchboard need balance `0.789129` and committed/recomputed keeper floor
`0.0685`. In the new six-tend-action session probe, cleanliness goes from
`0.9256` to `1.0` after clean. This saturated response is an integration
observation; it does not replace DR 0059's unsaturated `+0.3076` measurement.
Resumed play matches uninterrupted play for both inherited opt-in and explicit
disable; each survives succession.

Five real pygame frames per variant were captured with SDL's dummy driver at
the actual default 384x668 window. Opt-in displayed `cleanliness 0.99  G clean`
fully within the footer after the scripted G event, with exactly one clean
recorded and final engine value `0.9876`. The off variant recorded zero cleans
and had no cleanliness field or footer. Actual pixels were inspected. The
existing long era-help line clips horizontally in both variants; Q2 preserves
that incumbent layout. This does not claim a human usability result or close
Q3's first-session assessment.

## Corpus preservation and instrument corrections

One valid and one malformed fixture are added, plus the required research
example mirror: **5 valid / 15 malformed / 5 examples**. Every earlier fixture
and historical observation remains unchanged. Only the named generated schema
is regenerated. The Pydantic roundtrip assertion had been outside its loop;
it now verifies each fixture instead of only the final one.

The first focused sweep exposed a missed 14/4 census assertion and the
documented requirement that research examples mirror valid fixtures. The
correction adds the missing example and updates exact counts; it keeps the
set-equality and all rejection assertions. No scientific criterion is weakened.
An earlier standalone-validator implementation reversed the required/allowed
sets for the optional object; the fixed call requires no keys and permits only
cleanliness. These were caught implementation mistakes, not new findings about
the mechanic.

The contract and public engine/session regressions began RED. The aggregate
report writer and its failure/missing-check/instrument-tamper controls were
added after those contracts went green; they are not described as pre-code RED.
Changing the committed instrument to a deliberately wrong floor produces
`withhold`, as does independently failing or deleting any required check.

## Verification

All commands ran in the actual repository
`C:/Users/ryanf/github/_shelved/mechagotchi`, on `phase-l-gate`, with native
CPython 3.14.3, zlib-ng 1.3.1, and the locked lab/CLI/game dependency groups.
The interpreter was the already provisioned workspace repair environment;
the repository's incumbent Python 3.13 environment was left untouched.

RED commands and captured outcomes before implementation:

```powershell
$python = 'C:/Users/ryanf/Documents/Codex/2026-10-03/task-3/repair/.venv/Scripts/python.exe'
& $python -B -m unittest discover -s labs/slip_validator -p test_mechanics_contract.py
# Ran 1 test; FAILED (failures=18): three legal v0.2 forms rejected by six authorities.
& $python -B -m unittest discover -s packages/mecha_engine/tests -p test_slip_mechanics.py
# Ran 7 tests; FAILED (failures=4): profile mechanics and override behavior absent.
& $python -B -m unittest discover -s game/tests -p test_slip_mechanics.py
# Ran 4 tests; FAILED (errors=3): profile mechanics is not allowed.
```

Before wiring the client, the expanded game command ran six tests and failed
the two added footer/event-loop cases: no cleanliness text, and G recorded
zero clean actions. The same command then passed all six.

Reproduction commands:

```powershell
& $python -B labs/lifecycle_sim/slip_mechanics_gate.py --output 'C:/Users/ryanf/Documents/Codex/2026-10-03/task-3/q2-edit/data/lifecycle/slip_mechanics_authorship_stage0.json'
# verdict: adopt_authorship; 32 cases / 192 votes; 13 checks true; no incumbent mismatches.
mechas develop --verify focused --python $python
mechas develop --verify full --python $python
```

The first focused run `20261004T080926-00e0a9b5` executed 903 tests and failed
the two corpus-integration assertions described above. Artifact parsing passed
and no inventoried source bytes changed during that run.

Closing results:

- Focused run `20261004T081945-be8f15f7`: **904 tests**, six suites,
  zero skips, 2265 JSON artifacts valid, no source mutations.
- Full run `20261004T082227-895410cd`: **2474 tests**, **24 suites**,
  **0 skips**, **2265 JSON artifacts valid**.
  Every suite passed; artifact parsing, source preservation and `git diff --check`
  passed. Complete per-suite stdout/stderr and JSON summaries are retained under
  `.development/runs/20261004T082227-895410cd/`.
- The Q2 starting inventory contained **4012 files**. All
  **2942 incumbent data files** and all
  **22 original SLIP fixture/example JSON files**
  remain byte-identical. Only the 41 explicit Q2 paths changed;
  no concurrent/unexpected owner changes were overwritten.
- The source fingerprint after this measured report update remains the full
  pass fingerprint. Report-only Markdown is reviewed separately per DR 0062.
  The local workflow is complete at POLISH; its publication gate remains unmet.

The preservation audit and actual window captures are retained locally in
`.development/q2-evidence/`. They are ignored runtime evidence; the portable
contract metrics, frozen baseline and research triad are committed source.

## Remaining work

Q3 must preregister the default-covenant ADOPT/REFUSE criteria and enumerate
the exact artifact cascade before measuring its player experience. Q4 surveys
the hidden axes; Q5 consolidates and plans the next cycle. None was started
inside this slice. Q1 eligibility does not promote the Q-table.

Publication remains blocked by the existing automatic approval rejection.
No remote retry or alternative route was attempted during Q2. Native Windows
and Ubuntu Actions must still pass on the exact published SHA before remote
CI is called green. The separate desktop turn-submission configuration error
is diagnosed in the ignored local diagnostics; no supported local fix was
established and no security/configuration bypass was made.

## Sources

- `docs/development/q2-mechanics-rung.md`, `docs/development/local-cycle.md`
- `research/decision_records/0012-slip-schema-extension-ladder.md`, `0013-port-slip-v2-and-packet-v2.md`, `0059-cleanliness-mechanic-opt-in.md`, `0063-covenant-mechanics-authorship.md`
- `research/algorithm_cards/slip_mechanics_authorship.md`
- `labs/slip_validator/mechanics_contract.py`, `labs/slip_validator/test_mechanics_contract.py`
- `labs/lifecycle_sim/slip_mechanics_gate.py`, `labs/lifecycle_sim/test_slip_mechanics_gate.py`
- `packages/mecha_engine/tests/test_slip_mechanics.py`, `game/tests/test_slip_mechanics.py`
- `data/lifecycle/slip_mechanics_authorship_stage0.json`, `slip_mechanics_incumbent_baseline.json`, `cleanliness_mechanic_gate_stage0.json`
- `data/slips/mechanics_cases_stage0.json`, `research/slip/slip_examples/slip_v2_cleanliness.json`
- `game/README.md`, `sunsetted/TODO.md`
