"""Asset/code provenance contract surface for mecha_engine.

Promoted fifth (and last of the initial modules), in the contract
traceability matrix's fixed order
(research/package_specs/mecha_engine_contract_traceability_matrix.md).
Public surface per
research/package_specs/mecha_engine_provenance_contract_gate.md:

- ``parse_spdx_expression(expression) -> dict``
- ``validate_ledger(ledger, repo_root) -> dict``
- ``build_ci_report(ledger, repo_root) -> dict``
- ``generate_attribution_manifest(ledger) -> dict``
- ``hash_included_path(path) -> dict``

Provenance is a deterministic policy gate: ledger + repo_root ->
required-field validation -> SPDX expression parsing (Stage 0 subset,
case-sensitive uppercase operators) -> included sha256 / sha256-tree
hash verification -> review and decision-record policy -> CI report and
attribution manifest. ``build_ci_report`` intentionally hides the
lab-only name ``build_provenance_ci_report``; package callers do not
inherit lab file names.

The implementation is a verbatim semantic port of the Stage 0 research
lab (asset_pipeline), self-contained package code: stdlib only, no
research lab imports, no other mecha_engine module dependencies (the
interface spec scopes provenance inputs to ledgers, paths, SPDX
expressions, and decision-record references), no artifact writes on
import or call, and no input mutation. This gate is research and
package-promotion policy — it is not legal review, not repository-wide
REUSE compliance, and not a release-compliance claim (contract gate,
"Compliance Model"); release license metadata stays blocked until an
explicit license decision record exists.
"""

from .hashing import hash_included_path
from .ledger import validate_ledger
from .report import build_ci_report, generate_attribution_manifest
from .spdx import parse_spdx_expression

__all__ = [
    "build_ci_report",
    "generate_attribution_manifest",
    "hash_included_path",
    "parse_spdx_expression",
    "validate_ledger",
]
