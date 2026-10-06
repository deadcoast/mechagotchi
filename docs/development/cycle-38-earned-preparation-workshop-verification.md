# Cycle 38 closing-gate workshop ownership correction

2026-10-06. Prospective repair boundary after the retained aggregate failure and
before fixture edits. This is verification infrastructure, not a new experiment
or amendment to the closed earned-preparation study.

## Retained observation

Full run `20261006T103255-3894d524` executed 3,460 tests in 24 suites. Twenty-three
suites passed. Workshop executed all 134 tests in 237.797 seconds with one native
HTTP rejection request reporting Windows connection abort 10053; its process
then lingered until the existing 900-second suite timeout. All 2,320 JSON
artifacts were valid and the runner recorded no inventoried source mutation.
This run is FAILED, not a local completion gate.

The unchanged failing test passed alone in 0.729 seconds, leaving no threads.
Read-only independent source review found that `SemanticLayerTests.setUpClass`
starts another `serve_forever` loop after `start_workshop_server` already starts
the owned foreground loop. Its teardown shuts the shared server down once,
joins only the extra daemon loop, and omits server close. The standard library's
shared shutdown flag and readability/accept assumptions require one loop per
server. The ongoing unchanged-suite diagnostic records per-test thread ownership
and final stacks. Retain both observations whether or not the race repeats.

The native 403 route returns before reading a POST body. That is a plausible
independent early-close race on Windows, but the retained error does not prove
it. This correction must not claim that the HTTP abort was fixed.

## Authorized narrow correction and checks

- Preserve the original test file bytes in the operational repair evidence.
- Remove only the duplicate fixture-owned loop and its now-unused import.
- Close the server through its existing owned lifetime method; require its
  recorded foreground thread to be stopped before fixture cleanup.
- Keep every response, selected-context, isolation, semantic-layer and mutation
  assertion unchanged. No skip, timeout extension, retry decorator, weakened
  threshold, production daemonization or HTTP behavior change is permitted here.
- Run the complete workshop suite once against the corrected fixture, then the
  full registered sweep. A renewed transport failure remains a failure requiring
  diagnosis; do not selectively discard it or call the correction an HTTP fix.
- Recheck the 699 frozen scientific source identities and all 241 bundled runtime
  source identities. No scientific stage or native study journey is repeated.

The owned server API already exists in production. This is a correction to the
test's use of that API. Food access, lifecycle arithmetic, engine contracts,
native preparation code and the Windows bundle remain unchanged. The failed
aggregate run and original fixture are preserved alongside the eventual gate.
