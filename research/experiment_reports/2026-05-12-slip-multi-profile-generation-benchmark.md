# Experiment Report: SLIP Multi-Profile Generation Benchmark

Date: 2026-05-12

Status: `research_slip_multi_profile_generation_no_package_code`

## Question

Can the current constrained generator produce valid, SLIP-aligned grids for all
current valid Stage 0 profiles, not only `slip_lcd_seed`?

## Plan Alignment

This continues the research plan's Stage 6 requirement that a user-created
`SLIP` can generate a valid creature, load into the engine-side validator, and
survive validation. It directly follows
`research/slip/profile_compatibility_tests.md`, which identified multi-profile
generation as the next missing proof.

No `packages/` implementation was created.

## Method

Added a lab benchmark module:

- `labs/grid_genome/slip_profile_benchmark.py`
- `labs/grid_genome/test_slip_profile_benchmark.py`

The benchmark reuses the existing constrained generator, grid validator, and
SLIP alignment validator. It loads each valid profile from `data/slips/valid`,
generates 50 candidates per profile with deterministic seed `214`, validates
each candidate, checks alignment against the active profile, and writes profile
corpora plus a compact JSON report.

## Results

| Profile | Candidates | Valid | Aligned | Invalid | Misaligned | Unique signatures |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `slip_lcd_seed` | 50 | 50 | 50 | 0 | 0 | 50 |
| `slip_gray_stable` | 50 | 50 | 50 | 0 | 0 | 49 |
| `slip_amber_social` | 50 | 50 | 50 | 0 | 0 | 50 |
| **Total** | **150** | **150** | **150** | **0** | **0** | - |

Artifact:

- `data/slips/multi_profile_generation_stage0/slip_multi_profile_generation_stage0.json`

Generated corpora:

- `data/slips/multi_profile_generation_stage0/slip_lcd_seed/*.json`
- `data/slips/multi_profile_generation_stage0/slip_gray_stable/*.json`
- `data/slips/multi_profile_generation_stage0/slip_amber_social/*.json`

## Interpretation

The previous matrix claim that only `slip_lcd_seed` had generation evidence is
now obsolete. The current generator can produce valid, profile-aligned corpora
for all three current valid Stage 0 profiles.

This does not prove full SLIP compatibility. The benchmark does not test
behavior preview, mutation preview UI, profile-weighted evolution, community
profile-pack import, version migration, or a final JSON Schema/Pydantic
contract.

## Verification

```powershell
python -B -m unittest discover -s labs\grid_genome -p "test_slip_profile_benchmark.py"
python -B labs\grid_genome\slip_profile_benchmark.py --profile data\slips\valid\slip_lcd_seed.json --profile data\slips\valid\slip_gray_stable.json --profile data\slips\valid\slip_amber_social.json --count-per-profile 50 --rng-seed 214 --output-dir data\slips\multi_profile_generation_stage0
python -m json.tool data\slips\multi_profile_generation_stage0\slip_multi_profile_generation_stage0.json
```

## Decision

Adopt `slip_multi_profile_generation_stage0` as the Stage 0 proof that the
current valid profile corpus can constrain generation across palette and
body-mass variants.

Next research should either author the versioned SLIP schema/failure corpus or
extend workshop round trips across the generated multi-profile corpora.
