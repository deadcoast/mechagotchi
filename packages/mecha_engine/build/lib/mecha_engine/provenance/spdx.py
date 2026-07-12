"""SPDX license-expression parsing for the mecha_engine package surface.

Contract sources:

- research/package_specs/mecha_engine_provenance_contract_gate.md
  ("SPDX Expression Acceptance")
- research/package_specs/mecha_engine_module_interfaces.md ("provenance")
- SPDX License Expressions v2.2.2:
  https://spdx.github.io/spdx-spec/v2.2.2/SPDX-license-expressions/

The grammar is a verbatim semantic port of the Stage 0 research parser
(the asset_pipeline lab): the same project-supported identifier subset,
``LicenseRef-*`` and ``DocumentRef-...:LicenseRef-*`` forms, ``AND`` /
``OR`` / ``WITH`` / ``+`` / parentheses handling, and the same
case-sensitive uppercase-operator policy. Lowercase SPDX 3.x operator
forms stay rejected until an explicit schema and test revision (contract
gate, "SPDX Expression Acceptance"): accepting them by parser drift is a
negative check. Parsing is deterministic, pure, and performs no I/O.
"""

from __future__ import annotations

import re

# Project-supported SPDX short identifiers (Stage 0 subset, not the full
# SPDX License List: full-list ingestion is an explicit non-goal).
KNOWN_SPDX_IDS: frozenset[str] = frozenset(
    {
        "Apache-2.0",
        "CC-BY-4.0",
        "CC-BY-SA-4.0",
        "CC0-1.0",
        "BSD-2-Clause",
        "BSD-3-Clause",
        "GPL-2.0-only",
        "GPL-2.0-or-later",
        "GPL-3.0-or-later",
        "LGPL-2.1-only",
        "LGPL-2.1-or-later",
        "MIT",
        "LicenseRef-Mechagotchi-Internal-Research",
        "LicenseRef-Reference-Only",
    }
)

KNOWN_SPDX_EXCEPTIONS: frozenset[str] = frozenset(
    {
        "Autoconf-exception-3.0",
        "Bison-exception-2.2",
    }
)

# Known copyleft / share-alike identifiers used for contains_copyleft and
# the decision-record gate.
COPYLEFT_OR_SHARE_ALIKE_IDS: frozenset[str] = frozenset(
    {
        "CC-BY-SA-4.0",
        "GPL-2.0-only",
        "GPL-2.0-or-later",
        "GPL-3.0-or-later",
    }
)

SPDX_TOKEN_RE = re.compile(
    r"DocumentRef-[A-Za-z0-9.-]+:LicenseRef-[A-Za-z0-9.-]+"
    r"|LicenseRef-[A-Za-z0-9.-]+"
    r"|[A-Za-z0-9.-]+\+?"
    r"|\(|\)"
)

_LICENSE_REF_RE = re.compile(
    r"(DocumentRef-[A-Za-z0-9.-]+:)?LicenseRef-[A-Za-z0-9.-]+"
)


def parse_spdx_expression(expression: str) -> dict:
    """Parse the project-supported SPDX expression subset.

    Returns a JSON-serializable dict with ``ok``, ``expression``, sorted
    ``license_ids`` / ``exception_ids`` / ``operators``,
    ``contains_copyleft``, and ``errors``.
    """
    parser = _SpdxExpressionParser(expression)
    return parser.parse()


class _SpdxExpressionParser:
    """Recursive-descent parser over the Stage 0 SPDX expression subset."""

    def __init__(self, expression: str):
        self.expression = expression
        self.tokens: list[str] = (
            SPDX_TOKEN_RE.findall(expression) if isinstance(expression, str) else []
        )
        self.index = 0
        self.errors: list[str] = []
        self.license_ids: set[str] = set()
        self.exception_ids: set[str] = set()
        self.operators: set[str] = set()

    def parse(self) -> dict:
        if not isinstance(self.expression, str) or not self.expression.strip():
            self.errors.append("SPDX expression is empty")
        elif "".join(self.tokens) != "".join(self.expression.split()):
            self.errors.append("SPDX expression contains invalid characters or spacing")
        else:
            self._parse_or()
            if self._peek() is not None:
                self.errors.append(f"unexpected token {self._peek()}")
        return {
            "ok": not self.errors,
            "expression": self.expression,
            "license_ids": sorted(self.license_ids),
            "exception_ids": sorted(self.exception_ids),
            "operators": sorted(self.operators),
            "contains_copyleft": bool(self.license_ids & COPYLEFT_OR_SHARE_ALIKE_IDS),
            "errors": self.errors,
        }

    def _parse_or(self) -> None:
        self._parse_and()
        while self._peek() == "OR":
            self._consume("OR")
            self.operators.add("OR")
            self._parse_and()

    def _parse_and(self) -> None:
        self._parse_with()
        while self._peek() == "AND":
            self._consume("AND")
            self.operators.add("AND")
            self._parse_with()

    def _parse_with(self) -> None:
        was_simple = self._parse_primary()
        if self._peek() == "WITH":
            self._consume("WITH")
            self.operators.add("WITH")
            if not was_simple:
                self.errors.append("WITH left operand must be a simple license expression")
            exception = self._consume_identifier()
            if exception is None:
                self.errors.append("WITH requires a license exception identifier")
            elif exception not in KNOWN_SPDX_EXCEPTIONS:
                self.errors.append(f"unknown SPDX exception identifier {exception}")
            else:
                self.exception_ids.add(exception)

    def _parse_primary(self) -> bool:
        token = self._peek()
        if token is None:
            self.errors.append("unexpected end of SPDX expression")
            return False
        if token == "(":
            self._consume("(")
            self._parse_or()
            if self._peek() == ")":
                self._consume(")")
            else:
                self.errors.append("missing closing parenthesis")
            return False
        if token in {"AND", "OR", "WITH", ")"}:
            self.errors.append(f"unexpected token {token}")
            self.index += 1
            return False
        identifier = self._consume_identifier()
        if identifier is None:
            return False
        normalized = identifier[:-1] if identifier.endswith("+") else identifier
        if _is_license_ref(normalized) or normalized in KNOWN_SPDX_IDS:
            self.license_ids.add(normalized)
        else:
            self.errors.append(f"unknown SPDX license identifier {normalized}")
        return True

    def _consume_identifier(self) -> str | None:
        token = self._peek()
        if token is None:
            return None
        if token in {"(", ")", "AND", "OR", "WITH"}:
            return None
        self.index += 1
        return token

    def _consume(self, expected: str) -> None:
        if self._peek() == expected:
            self.index += 1
        else:
            self.errors.append(f"expected {expected}, got {self._peek()}")

    def _peek(self) -> str | None:
        return self.tokens[self.index] if self.index < len(self.tokens) else None


def _is_license_ref(identifier: str) -> bool:
    return _LICENSE_REF_RE.fullmatch(identifier) is not None
