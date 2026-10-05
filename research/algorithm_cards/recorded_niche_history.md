# Recorded niche history

- **Name / Purpose:** V1 saved-record navigation: find occurrences of the
  selected exact seven-axis niche across recorded predecessor campaigns.
- **Mathematical basis:** equality of stored names/order/integer bin labels;
  no new scientific statistic, binning, projection or ancestry inference.
- **Inputs:** DR0022 campaign/era/elite blobs, recorded predecessor pointers,
  historical covenants and existing replay pointers.
- **Outputs:** campaign/era/body occurrences, explicit missing/incompatible
  notices, and links to the existing report/archive/replay/adoption views.
- **Strengths:** public storage reads only; no schema, simulation or engine
  change. Current-covenant adoption remains an explicit separate action.
- **Weaknesses:** old threshold provenance is absent; equal labels do not prove
  calibration equivalence. Only recorded campaign links are searched.
- **Failure modes:** missing/cyclic links and incompatible archive records are
  named; valid partial history remains accessible. No placeholder bodies.
- **Integration risk:** wrong campaign context on return/adoption, queued care
  while browsing, small-window outcome displacement; pinned by game tests.
- **License status:** same repository terms; no added external data/dependency.
- **Prototype result:** see the experiment report for actual RED/GREEN and
  source/native observations; full closure is reported separately.
- **Decision:** parent-authorized recorded-fact consumer; E5 projection deferred.
- **Go/No-Go gate:** exact read-only preservation, real connected navigation,
  explicit historical limits, full sweep and preservation review.

## Sources

- `game/src/mecha_game/niche_history.py`
- `game/tests/test_niche_history.py`
- `research/experiment_reports/2026-10-04-niche-history.md`
- `research/decision_records/0075-recorded-niche-history.md`
- `docs/development/cycle-32-niche-history.md`
