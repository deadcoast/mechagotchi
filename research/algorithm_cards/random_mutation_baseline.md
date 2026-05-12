# Algorithm Card: Random Mutation Baseline

## Purpose

Provide the simplest comparator for all future grid generators.

## Mathematical Basis

Uniform random selection over naive mutation operators. This is not intended as
an adoption candidate; it is the baseline that Markov, WFC, and hybrid methods
must beat.

## Inputs

- Valid seed grid corpus
- RNG seed
- Mutations per seed

## Outputs

- Generated child grid genomes
- Validity count
- Invalidity count
- Error profile

## Strengths

- Simple
- Reproducible
- Reveals validator sensitivity
- Establishes the minimum generator quality bar

## Weaknesses

- No learned structure
- No SLIP awareness
- No repair pass
- Frequently breaks organ references and animation anchors

## Failure Modes

- Missing animation anchor
- Missing organ references
- Duplicate coordinates
- Invalid mutation rates
- Semantic organ mismatch

## Integration Risk

Low.

## License Status

Internal lab code.

## Prototype Result

Completed on 2026-05-12.

```txt
candidate_count: 100
valid_count: 42
invalid_count: 58
validity_rate: 0.42
```

## Decision

Adopt as baseline only. Do not use as the real generator.

## Go/No-Go Gate

Future generators must beat this baseline on valid grid rate while preserving
novelty and ancestor resemblance.

