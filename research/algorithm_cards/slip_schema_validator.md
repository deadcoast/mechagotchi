# Algorithm Card: SLIP Schema and Validator

## Purpose

Turn authored profile intent into safe, testable constraints and priors for
generation, behavior, mutation, and survival.

## Mathematical Basis

Typed schema validation, constraint checking, bounded weights, and compatibility
scoring.

## Inputs

- SLIP profile file
- Grid genome schema
- Engine version
- Generator capabilities
- Mutation operator registry

## Outputs

- Validation result
- Normalized constraints
- Behavior priors
- Mutation permissions
- Compatibility score
- Human-readable error report

## Strengths

- Makes modular authoring real
- Protects the engine from invalid user profiles
- Gives the workshop a stable contract
- Can generate JSON Schema from Pydantic research models

## Weaknesses

- Overly strict rules can kill novelty.
- Under-specified rules can permit malformed companions.
- Profile versioning must be handled from the first draft.

## Failure Modes

- Profile validates but cannot generate a viable creature
- Profile weights exceed useful ranges
- Required animation anchors or organs are missing
- Mutation permissions conflict with hard grid invariants

## Integration Risk

Low to medium.

## License Status

No external code selected. Pydantic is a candidate validation dependency for
Python prototypes, with JSON Schema as the interchange contract.

## Prototype Result

First minimal profile validator completed on 2026-05-12.

```txt
valid profiles accepted: 3/3
invalid profiles rejected: 2/2
SLIP-constrained generated grids: 50
SLIP-aligned generated grids: 50
```

## Decision

Keep as active prototype. Expand into a versioned JSON Schema or Pydantic-backed
contract before workshop authoring begins.

## Go/No-Go Gate

A user-authored SLIP must generate a valid creature, preview behavior, preview
mutation, export, reload, pass validation, and influence evolution.
