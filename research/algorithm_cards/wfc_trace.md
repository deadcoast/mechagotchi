# Observational WFC trace and inspector

Purpose: make the existing WFC generator's actual decisions/retries inspectable,
without changing its science. The trace is not a new generation algorithm.

Input: the unchanged trained WFC model, grid ID, seed and restart budget, plus
an optional append-only caller list. Output: the unchanged generated grid or
original exception, and detached JSON-native events when requested. Events are
recorded at real decision boundaries; no extra random draws occur. A contradiction
contains an empty proposed filter that was never applied. Finishing events
record normalization, retained/dropped core, ratified floor and actual anchor.

Client: reconstruct diagnostic wave choices only from recorded wave/choice/
propagation/matrix events; identify them as diagnostics. Final-body animation
uses the unchanged engine packet. Capturing is foreground-owned and joined on
every exit. Cancellation leaves the generator call unchanged and discards the
new view. Failed events remain inspectable; no saves/preparation changes occur.
The constrained hatch candidate remains separate and unchanged.

Limits: trace lists scale with attempts/cells; this UI uses the existing bounded
corpus/default retry budget. Session-only captures are not saved history. WFC
does not gain covenant conditioning or adoption. Constrained is still the
DR0042 evolution default. Native keyboard and maximal scales remain unobserved.

Evidence: 68 pre-edit output/error/RNG fixtures, exact lab/package event parity,
JSON round trips, source interaction and native smoke in the W4 report.

Full `20261005T135504-94a410b6` passed **2,694 tests / 24 suites**, 2 documented DR0034 zlib skips and **2300 JSON artifacts valid**, with no source mutations.
Exact fixed-seed/RNG/failure and lab/package event parity passed.
