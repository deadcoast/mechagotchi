# Experiment Report: The Mortal-Wound Signal (D2) — C6's Gradient Becomes a Felt Phenomenon

Date: 2026-07-07

## WHY

C6 measured a damage-scaled mortality gradient — creatures whose repair
left a shattered body core, marked `skipped_invalid` by the engine — and
named its own follow-up: "if gameplay wants the mortal wound surfaced,
`skipped_invalid` + this gradient are the source." D2 surfaces it. The
constraint is DR 0021's first law: no new engine number — the signal is
a READING of a report field the engine already produces.

## WHAT

`_mortal_wounds(report)` reads each era report's per-creature
`archive_decision` and tallies `skipped_invalid` (shattered-core mortal
wounds — C6's cause), `skipped_unaligned` (normal deaths — the creature
drifted out of its species), the creature count, and the rate. It rides
the era's derived metrics, the era digest, and — summed across eras —
the session report's `mortal_wound_toll` / `mortal_wounds_by_era`.

The signal is felt at every surface:
- **`mechas session --era`** prints "the toll" — "N creature(s) lost to
  shattered cores (mortal wounds)" (amber when non-zero, plain "no
  losses — the whole brood held" otherwise).
- **The Keeper page** era cards gain a "the toll" line (red when the
  bloodline took losses).
- The lab report carries the campaign toll and the per-era series.

## FINDING — the signal is honest at zero and fires under damage

The demo session (mild default parameters, dropout 0.2) reports a toll
of **0** — honest: C6's in-band rate is ~1.25%, rare over 36 creatures,
and the signal shows zero when no wounds occurred rather than inventing
drama. The test suite proves it FIRES: at a C6 boundary regime
(dropout 0.95, 4 cycles, seed 20260703) the tally goes non-zero, and in
every case — zero or not — it is pinned by an independent recomputation
of `skipped_invalid` from the report, so the number is always engine
truth, never decoration.

Also corrected here (stale-text discipline): the G2 session report's
`sqlite_ledger_pending_storage_module_promotion` blocked state was
removed — C3 promoted the storage module, so the claim was false.

## Verification

```powershell
PS> python -B -m unittest discover -s labs/game_loop -p "test_*.py"
Ran 60 tests in 5.367s
OK    # tally == recomputed skipped_invalid per era; toll == sum;
      # the signal fires non-zero under heavy damage and still matches

PS> python -B -m unittest discover -s workshop/tests -p "test_*.py"
OK
PS> python -B -m unittest discover -s tools/mechas_cli/tests -p "test_*.py"
OK
```

## Decision

Adopt — D2 developed to its description: C6's mortality gradient is now
a Keeper-visible event at every surface, sourced entirely from the
report's existing `archive_decision`. The living ecosystem shows one
more of its own truths (DR 0017's player-noticeable phenomena).

## Sources

- `research/experiment_reports/2026-07-07-repair-validity-boundary.md` (C6, the source)
- `research/decision_records/0021-game-loop.md` (the first law; player-noticeable phenomena)
- `labs/game_loop/session_runner.py` (+ `test_session_runner.py`)
- `tools/mechas_cli/src/mechas_cli/workflows/session.py`
- `workshop/session/session.html`
- `data/game_loop/session_runner_stage0.json` (the toll series)
