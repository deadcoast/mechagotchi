# Preview model consistency

## Name / Purpose
Keep recomputed preview physiology, identity and visible context consistent.

## Mathematical basis
No new simulation mathematics. SHA-256 binds canonical simulation inputs; exact
context revision equality gates asynchronous result acceptance.

## Inputs / Outputs
Validated current model, selected document and effective simulation options yield
new model-bound previews. Stored recordings retain their original bytes/provenance.

## Strengths / Weaknesses
Fresh authority checks prevent known stale-context races. A displayed result is
an explicitly labeled snapshot; it does not continuously observe later disk edits.

## Failure modes / Integration risk
Invalid context or model refuses; interrupted publication cannot overwrite prior
footage. Shared historical recording formatter must remain unchanged.

## License status
Apache-2.0, repository-native integration.

## Prototype result / Decision
Confirmed omitted dispatch in both HTTP routes. Software repair locally qualified by recorded closing gates.
Full 3682 tests / 24 suites; browser15 and additive Windows delivery.
No scientific promotion.

## Go-No-Go gate
All preregistered functional, browser, native, aggregate and preservation checks
must pass. Refuse closure on stale model display, historical rewrite or mixed IDs.

## Sources

- docs/development/cycle-38-preview-consistency.md
- game/src/mecha_game/keeper_context.py
- workshop/server/workshop_server.py
- workshop/shared/authoring.js
- workshop/preview/preview.html
- game/src/mecha_game/replay.py
- game/src/mecha_game/campaign.py
- .development/preview-consistency/registration.json
- .development/preview-consistency/entry.json
- .development/body-compatibility/next-preview-boundary.json
