# Mechagotchi interface context

Cycle 38, 2026-10-05. Preserve the existing LCD companion and restrained creator
workbench. Native care is a living simulation; reading, inspection and destructive
decisions pause it. Facts come from engine state or recorded evidence. Never
present recomputation as original footage, genotype ancestry as all cared lives,
or historical E5 families as seven-axis niche history.

The Workshop pages own the existing light/dark tokens: ground, panel, ink,
ink-soft, line, accent, accent-ink, bezel, amber and danger. Light ground/panel
are #e8e6dd/#f2f1ea and dark #1a1d18/#22261f; green marks affirmative actions,
amber focus/attention and rust red errors. Keep system-ui/Segoe UI body text
(15px, 1.5 line height) and the existing Cascadia/Consolas monospace labels.
No new font service or component framework is needed for these interfaces.

Canonical behavior owners:

- workshop/shared/authoring.js owns complete document history, bounded undo/redo,
  local recovery, revision arbitration, keyboard dialogs and focus return.
- workshop/shared/authoring.css owns common authoring states, focus, small-screen
  containment, reduced motion and forced-color support; it consumes page tokens.
- Grid Editor owns the spatial canvas, tools and error-cell navigation. SLIP
  Creator patches its complete loaded profile; untouched valid fields survive.
- workshop/server/authoring.py and workshop_server.py own validation, document
  digests, disk conflicts and exact selected release. The browser never substitutes
  cached filenames for selected drafts or calls late feedback current.
- game/src/mecha_game/footer.py owns wrapping/paging. app.py owns mutually
  consistent read/close/help behavior and the explicit recovery decision.
- chronicle.py/session.py own recorded life facts; campaign_recovery.py owns
  paired snapshot identity. UI wording follows those authorities.

Draft, validation, saved file and released creature are separate visible states.
Failures preserve the draft and offer retry or download. Recovery requires an
explicit Restore/New choice. Overwrite and release identify their selected work
and disk conflict; stale replies never label a newer draft saved. Crop states its
effect and can be undone. Canvas arrows select, Space/Enter applies a tool, and
normal text entry retains its shortcuts. Controls, dialogs, errors and narrow
layouts must remain reachable by keyboard, with visible focus and truthful text.

The behavioral acceptance contract is
docs/development/cycle-38-keeper-and-authoring.md, alongside the existing Workshop
charter. Actual browser screenshots/flows and native process/source interaction
evidence are separate; neither establishes human usability or native keyboard QA.

Native select and range inputs retain platform-owned popup and keyboard behavior;
no custom popup geometry is claimed. Shared authoring.css owns global scrollbar
colors/states with forced-color fallback.


X3 extends these canonical owners without changing the LCD palette or typography.
Shared authoring.js owns the explicit native_keeper/browser_lab context ribbon,
selected-context request pins, bounded complete server draft history, browser
fallback and explicit Restore/New/conflict/previous-copy decisions. Server drafts
are namespaced by stable context identity and survive an origin/port change;
startup templates cannot replace recoverable work. Shared authoring.css owns
common context facts, containment and interaction states. Server/context adapters
remain the authority for current identity, active covenant, earned caps and disk
comparison revisions; the UI never infers a native Keeper from a browser history.

Grid edits patch the full existing layer objects and preserve accepted siblings,
ordering and untouched default/optional fields. Unrecognized layer semantics
remain present and disable destructive spatial transforms. Preview requests use
the full selected document and invalidate results when selection changes. The
inspector uses text nodes for file labels/provenance and separates stored genetic
declarations, verbatim era admission reports and actual cared-life records.
Missing facts remain unavailable. Preview offspring are possibilities, and new
preview footage is labeled separately from original saved observations.

workshop/packs/packs.html owns named composition, explicit complete creature and
covenant selection, validated local download, chosen-file review and per-item
staging outcomes. Native context and target path stay visible. Item format status,
active-covenant compatibility advisory and eventual engine admission are distinct.
Retry never assumes an interrupted write succeeded; conflicts retain existing
files and expose explicit outcomes. Native selects/file inputs retain platform
behavior. These source/browser journeys do not claim detached X4 packaging,
native OS keyboard validation, signing, registry publication or human usability.


X4 native entry and navigation keep the same pygame LCD casing: ground
(16,18,16), green-white text (200,230,200), muted green borders and amber keyboard
focus. No font service or GUI dependency is added. native_ui.py owns button
geometry, paging, focus, read-only entry rendering and the editable save path;
startup.py owns inspection/revision checks and explicit save choices; app.py owns
mode transitions, engine actions, worker lifetime and care pause. FooterPager
continues to own wrapping and long-text paging. These owners do not duplicate
care, campaign or recovery mechanics.

Startup exists before a valid companion. It shows independent primary/backup
facts and the selected directory, presents only authority-provided choices, and
keeps failures actionable through Retry/Choose directory/Quit. Backup inspection
and New open a Cancel-first confirmation pinned to the captured revision. A view
must be drawn before it accepts activation; held Enter/Space and same-batch
click-through cannot confirm. Path text is changed locally, supports selection,
Unicode input and explicit paste, and is inspected only after Apply. Escape
returns without changing the selected home. UI inspection/cancellation has no
filesystem or session authority.

ActionStrip routes opaque action IDs to app.py. F6 enters visible navigation;
Tab is configurable where a mode already owns it. Arrow/Tab navigation skips
unavailable controls, Enter/Space activates, and Escape leaves focus. Main pauses
care while keyboard navigation is active; mouse hover/click does not acquire a
persistent navigation pause. Overflow uses visible More/Back pages and keyboard
focus follows its action ID through resize. A newly revealed page must be drawn
before activation. fit_native_layout reserves integer LCD pixels, separate
legible footer rows and paged actions; it never shrinks the body font or alters
the creature compositor. Main enforces supported minimum/display bounds.

Source-injected pygame events, rendered screenshots, native process launch and
actual OS keyboard observation remain separate evidence categories. Helper tests
alone do not establish the connected application journey or detached delivery.


The integrated native app routes each selected button through the existing key
handler. It reconciles contextual controls before every retrieved event: a raw
shortcut changing modes disarms the old drawn buttons until the new controls are
painted. It pauses care on any navigation-consumed frame, including the frame
that leaves focus, while retaining intentional raw shortcut sequences. Era/WFC
workers expose Cancel/Help in the same layout and forward key releases to the
parent navigation guard. Resize changes only integer raster size/placement and
resets ghost pixels only when their raster dimensions change. Diagnostic receipts
record the actual SDL driver, window size and resizable flag separately from any
claim of operating-system input observation.


X5 preserves the same report/archive layout and first-page outcome metrics.
execution_readout.py owns compact immutable-input availability, ordered release
admission/source facts and explicit comparison notices. EraReview keeps these
summaries outside ordinary history records. Source links require supported
recorded evaluation parent events and unambiguous input occurrences; authored
ancestor declarations do not establish release origin. Missing old inputs and
ambiguous IDs remain explicit.

Reproduce [D] is an explicit report/archive action using app.py's existing joined
EraWork foreground loop. It pauses care, provides real progress, Help and Cancel,
and returns its comparison notice to the selected reading view. Its read-only
ledger connection belongs to that worker. Inspection never starts comparison;
comparison never saves a Keeper or replaces the original report, archive or
footage. Saved recording remains a separate action with its existing provenance.
The standalone command writes complete recomputed results only to a new directory
outside the Keeper home. Source-injected SDL tests remain distinct from native
OS keyboard and human usability evidence.

| Capability | Canonical owner | Source of truth | Allowed variants | Verification |
|---|---|---|---|---|
| Native action navigation | native_ui.ActionStrip | X4 entry contract and existing mode handlers | report/archive Reproduce action | test_native_actions.py; test_execution_client.py |
| Native foreground progress | app.wait_for_era and EraWork | X5 immutable-input contract | era execution; read-only reproduction | cancellation, join and care-pause controls |
| Recorded evidence feedback | execution_readout and FooterPager | verified storage and recorded report events | available, matched, mismatch, unavailable, ambiguous | read-only history and complete paged text controls |
