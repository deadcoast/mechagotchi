# Constrained hatch preview / saved origin consumer

Intent: explain a displayed founder before explicit adoption and inspect its
recorded origin after restart. This client adds no generation algorithm.

Inputs: engine-generated grid with trace metadata, active covenant snapshot,
or current saved companion grid and its own covenant. Outputs: unchanged engine
render packets, full explain_generation fields and the existing adopted session.
Copies isolate the view from caller mutations; clip selection uses the engine
packet vocabulary and existing client clip graph. No lifecycle steps occur in
the view. Complete JSON-valued fields wrap without truncation through FooterPager.

Adoption rechecks campaign state and covenant, constructs through initial_state,
and follows existing old/new checkpoint recovery. Invalid/unavailable provenance,
external changes and write failures remain visible. Incumbent stays the default;
qtable is experimental and retained only when already selected.

Evidence and limits: 2026-10-05-hatch-preview report and
data/game_client/hatch_preview_release_stage0.json. Source event injection proves
application behavior; native process launches do not prove keyboard usability.
Constrained trace is not WFC instrumentation. Seeds still reset per launch.

Full `20261005T130951-59a1cc56` passed **2,679 tests / 24 suites**, 2 documented DR0034 zlib skips; **2298 JSON artifacts valid**. No source mutations; local completion only.
48 application checks and exact fixed-seed candidate/trace parity passed.
