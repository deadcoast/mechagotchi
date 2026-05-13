# CuBFF Upstream Snapshot Audit - 2026-05-12

## Scope

Audited the official `paradigms-of-intelligence/cubff` repository at commit
`f212e849027c98fcf4b242eccfb5fed435223e23`.

## Primary Sources

- https://github.com/paradigms-of-intelligence/cubff
- https://arxiv.org/abs/2406.19108
- https://github.com/paradigms-of-intelligence/cubff/blob/main/common.h
- https://github.com/paradigms-of-intelligence/cubff/blob/main/common_language.h
- https://github.com/paradigms-of-intelligence/cubff/blob/main/cubff_py.cc

## Findings

- The repo is the official CUDA-capable CuBFF implementation for many
  Computational Life experiments.
- `SimulationState` exposes soup, shuffle indices, epoch, Brotli metrics, byte
  frequencies, and self-replication scores.
- Checkpoints are written as three `size_t` header values followed by raw soup
  bytes.
- Each program is 64 bytes.
- The upstream tree includes 13 `testdata/*.txt` metrics logs.
- The upstream tree includes no committed `.dat` checkpoint, JSON state, or
  soup snapshot artifacts.

## Research Consequence

The synthetic CUBFF transducer baseline remains useful only as an interface
test. It cannot support adoption. Real CuBFF adoption review must wait until
the project has actual checkpoint or Python callback state exports to ingest.
