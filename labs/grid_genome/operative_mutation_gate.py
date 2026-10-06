"""X6 preregistered operative mutation qualification, 2026-10-06.

G0 reproduces the formal 30/10/10 split, 100 outputs per arm, and 1,000
bootstrap resamples. Only generation_seconds is excluded from equality.
G1 requires independent operator/parity review; no test-only quality claim.
G2 requires ALL requested outputs valid/aligned, with exceptions retained.
G3: ordinary and all-open cohorts; fixed blocks 20260706 and 20260707;
100 outputs per arm/block. EACH ordinary operative block's readability
loss versus its matched legacy block must be <= abs(legacy A - legacy B).
EACH open operative block must meet the worse legacy novelty, corpus
silhouette entropy bits (B2 _entropy_bits over _signature), and parent-copy
fraction. Zero spread means zero allowance; pooling cannot rescue failure.
Clone must fail open variation; existing ungated random must fail reliability.
Per-grid silhouette entropy is observational only. Any G0-G3 failure REFUSES
consumer promotion: no evolutionary rescue study or threshold retuning.

Phenotype excludes identity, lineage, metadata, mutation rates, cell weights,
locks, stress/damage; includes all other cell payload, palette, grid size and
all organ attributes except mutation_locked, with sorted cell/membership order.

Source contract: docs/development/cycle-38-operative-mutation-permissions.md.
This module was rule-registered, then RED-tested, before implementation/run.
"""
from __future__ import annotations

import argparse
from collections import Counter
from copy import deepcopy
from dataclasses import asdict
import hashlib
import gzip
import json
from pathlib import Path
from statistics import mean
import sys
import time

ROOT = Path(__file__).resolve().parents[2]
for relative in ('labs/grid_genome', 'labs/readability_benchmark', 'labs/wfc_grid',
                 'packages/mecha_engine/src'):
    location = str(ROOT / relative)
    if location not in sys.path:
        sys.path.insert(0, location)

from generation_bakeoff_formal import (build_generation_bakeoff_report, corpus_split,
                                      _cell_set, _novelty, _symmetry)
from generation_bakeoff16 import _entropy_bits, _signature as silhouette_signature
from random_mutation import mutate_grid
from mecha_engine.generation import generate_candidate, train_generation_model
from mecha_engine.genome import validate_grid
from mecha_engine.slip import is_grid_aligned
from mecha_engine.runtime import learned_readability_score
from mecha_engine.runtime._readability import extract_readability_features

ARTIFACT_ID = 'operative_mutation_stage0'
ARM = 'operative_permissions_v1'
BLOCKS = (20260706, 20260707)
COUNT = 100
FORMAL_PATH = 'data/generated_grids/generation_bakeoff_formal_stage0.json'
PROFILE_PATH = 'data/slips/valid/slip_lcd_seed.json'
READABILITY_PATH = 'data/readability_benchmark/adopted_readability_model.json'
CONTRACT_PATH = 'docs/development/cycle-38-operative-mutation-permissions.md'
RATE_KEYS = ('cell_mutation_rate', 'organ_shift_rate', 'palette_shift_rate', 'symmetry_break_rate')
G1_REVIEW_SOURCES = (
    'labs/grid_genome/operative_permissions.py',
    'labs/grid_genome/test_operative_permissions.py',
    'labs/grid_genome/test_operative_package_parity.py',
    'packages/mecha_engine/src/mecha_engine/generation/_operative_permissions.py',
    'packages/mecha_engine/src/mecha_engine/generation/generate.py',
    'packages/mecha_engine/src/mecha_engine/generation/explain.py',
    'packages/mecha_engine/tests/test_operative_permissions_contract.py',
)
SOURCE_PATHS = (CONTRACT_PATH, FORMAL_PATH, PROFILE_PATH, READABILITY_PATH,
    'labs/grid_genome/operative_mutation_gate.py', 'labs/grid_genome/generation_bakeoff_formal.py',
    'labs/grid_genome/corpus_builder.py', 'labs/grid_genome/grid_helpers.py',
    'labs/grid_genome/random_mutation.py', 'labs/wfc_grid/generation_bakeoff16.py',
    'packages/mecha_engine/src/mecha_engine/generation/generate.py',
    'packages/mecha_engine/src/mecha_engine/generation/model.py',
    'packages/mecha_engine/src/mecha_engine/runtime/_readability.py')


def encoded(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()


def digest(value):
    return hashlib.sha256(encoded(value)).hexdigest()


def file_hash(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def source_hashes():
    paths = list(SOURCE_PATHS) + list(G1_REVIEW_SOURCES)
    # The operator owner owns these implementation names. Capture every matching
    # operative source without guessing which is the authoritative private copy.
    for directory in ('labs/grid_genome', 'packages/mecha_engine/src/mecha_engine/generation'):
        paths.extend(path.relative_to(ROOT).as_posix() for path in (ROOT/directory).glob('*operative*.py'))
    return {path: file_hash(ROOT/path) for path in sorted(set(paths)) if (ROOT/path).is_file()}


def read_inputs():
    split = corpus_split()
    profile = json.loads((ROOT/PROFILE_PATH).read_text(encoding='utf-8'))
    lcd = [grid for grid in split['holdout']
           if grid['palette']['palette_id'] in profile['grid']['allowed_palettes']] or split['holdout']
    # Verbatim formal package_hybrid holdout parent schedule (10 parents x 10).
    parents = [lcd[index % len(lcd)] for index in range(len(split['holdout']))]
    return dict(split=split, parents=parents, profile=profile,
                model=train_generation_model(split['train']),
                readability=json.loads((ROOT/READABILITY_PATH).read_text(encoding='utf-8')),
                holdout_sets=[_cell_set(grid) for grid in split['holdout']])


def block_overlap(inputs):
    pairs = {seed: {(digest(inputs['parents'][index//10]), seed+index) for index in range(COUNT)}
             for seed in BLOCKS}
    shared = len(pairs[BLOCKS[0]] & pairs[BLOCKS[1]])
    return dict(pair_key='parent JSON SHA256 and effective candidate rng_seed',
                unique_pairs_per_block={seed: len(rows) for seed, rows in pairs.items()},
                shared_parent_seed_pairs=shared, fraction_of_each_block=shared/COUNT,
                interpretation='fixed shifted-block sensitivity control, not independent noise or confidence evidence',
                preregistered_seeds_and_thresholds_unchanged=True)


def all_open_inputs(parent, profile):
    child, covenant = deepcopy(parent), deepcopy(profile)
    for name in RATE_KEYS:
        child['mutation'][name] = 1
        covenant['mutation'][name + '_max'] = 1
    for cell in child['cells']:
        cell['locked'] = False
        if cell['mutation_weight'] > 0:
            cell['mutation_weight'] = 1
    for organ in child['organs'].values():
        organ['mutation_locked'] = False
    return child, covenant


def phenotype_signature(grid):
    cells = [{key: value for key, value in cell.items()
              if key not in ('mutation_weight', 'locked', 'stress', 'damage')}
             for cell in grid['cells']]
    cells.sort(key=lambda cell: (cell['y'], cell['x'], encoded(cell)))
    organs = deepcopy(grid['organs'])
    for organ in organs.values():
        organ.pop('mutation_locked', None)
        organ['cells'] = sorted(organ['cells'])
    return digest(dict(grid_size=grid['grid_size'], palette=grid['palette'], cells=cells, organs=organs))


def compare_formal(expected, actual):
    left = {key: value for key, value in expected.items() if key != 'generation_seconds'}
    right = {key: value for key, value in actual.items() if key != 'generation_seconds'}
    missing = object()
    different = sorted(key for key in left.keys() | right.keys()
                       if left.get(key, missing) != right.get(key, missing))
    return dict(passed=not different, different_metrics=different,
                expected=left, actual=right,
                generation_seconds_observed=actual.get('generation_seconds'))


def reproduce_formal():
    before = file_hash(ROOT/FORMAL_PATH)
    committed = json.loads((ROOT/FORMAL_PATH).read_text(encoding='utf-8'))
    actual = build_generation_bakeoff_report(outputs_per_seed=10, bootstrap_resamples=1000)
    expected_row = next(row for row in committed['arms'] if row['arm'] == 'package_hybrid')
    actual_row = next(row for row in actual['arms'] if row['arm'] == 'package_hybrid')
    result = compare_formal(expected_row, actual_row)
    result.update(source=FORMAL_PATH, source_sha256_before=before,
                  source_sha256_after=file_hash(ROOT/FORMAL_PATH), protocol=actual['protocol'],
                  observed_other_arms=[row for row in actual['arms'] if row['arm'] != 'package_hybrid'])
    result['passed'] = (result['passed'] and actual['protocol'] == committed['protocol']
                        and result['source_sha256_before'] == result['source_sha256_after'])
    return result


def evaluate_candidate(parent, profile, inputs, *, arm, seed, index, generator=None):
    before = digest(dict(parent=parent, profile=profile, model=asdict(inputs['model'])))
    row = dict(index=index, parent_grid_id=parent['grid_id'], parent_sha256=digest(parent),
               profile_sha256=digest(profile), rng_seed=seed, arm=arm, status='exception',
               valid=False, aligned=False, trace=None, trace_counts={}, lineage_events=[],
               novelty=None, readability=None, silhouette_signature=None,
               silhouette_entropy_feature=None, symmetry=None, parent_copy=None)
    try:
        if generator is not None:
            child = generator(parent, inputs['model'], profile, rng_seed=seed)
        elif arm == 'clone':
            child = deepcopy(parent)
        elif arm == 'random_ungated':
            child = mutate_grid(parent, index, seed)
        else:
            child = generate_candidate(parent, inputs['model'], profile, rng_seed=seed,
                                       mutation_arm='legacy' if arm == 'legacy' else ARM)
        row.update(status='returned', child_grid_id=child.get('grid_id'), child_sha256=digest(child), grid=deepcopy(child))
        valid = validate_grid(child)
        aligned = is_grid_aligned(child, profile)
        trace = deepcopy(child.get('metadata', {}).get('generation_trace'))
        counts = Counter()
        for event in (trace or {}).get('operator_events', []):
            counts[event.get('operator', 'unknown') + ':' + event.get('outcome', 'unknown')] += 1
        row.update(valid=valid.ok, aligned=aligned.ok,
                   validation_errors=list(valid.errors), alignment_errors=list(aligned.errors),
                   trace=trace, trace_counts=dict(sorted(counts.items())),
                   lineage_events=deepcopy(child.get('lineage', {}).get('mutation_events', [])),
                   phenotype_sha256=phenotype_signature(child),
                   parent_copy=phenotype_signature(child) == phenotype_signature(parent),
                   novelty=_novelty(child, inputs['holdout_sets']), symmetry=_symmetry(child),
                   readability=learned_readability_score(child, inputs['readability']),
                   silhouette_signature=silhouette_signature(child),
                   silhouette_entropy_feature=extract_readability_features(child)['silhouette_entropy'])
    except Exception as error:
        # Exceptions are observations, never dropped/retried. A returned but
        # unmeasurable grid is a measurement_error, not a successful row.
        row.update(status='measurement_error' if row['status'] == 'returned' else 'exception',
                   exception_type=type(error).__name__, error=str(error))
    row['inputs_unchanged'] = before == digest(dict(parent=parent, profile=profile, model=asdict(inputs['model'])))
    return row


def summarize_candidates(rows, *, requested_count):
    returned = [row for row in rows if row['status'] == 'returned']
    complete = len(returned) == requested_count and len(rows) == requested_count
    counts = Counter()
    for row in rows:
        counts.update(row['trace_counts'])
    def average(key):
        return mean(row[key] for row in returned) if complete else None
    return dict(requested_count=requested_count, attempted_count=len(rows),
                candidate_count=len(returned), candidate_failures=len(rows)-len(returned),
                valid_count=sum(row['valid'] for row in returned),
                aligned_count=sum(row['aligned'] for row in returned),
                inputs_unchanged=all(row['inputs_unchanged'] for row in rows),
                mean_readability=average('readability'), mean_novelty=average('novelty'),
                mean_symmetry=average('symmetry'),
                corpus_silhouette_entropy_bits=_entropy_bits([row['silhouette_signature'] for row in returned]) if complete else None,
                mean_silhouette_entropy_feature=average('silhouette_entropy_feature'),
                parent_copy_fraction=average('parent_copy'), trace_counts=dict(sorted(counts.items())),
                trace_opportunities=sum(sum(row['trace_counts'].values()) for row in rows),
                traced_accepted_proposals=sum((row['trace'] or {}).get('accepted_proposals', 0) for row in returned),
                traced_rejected_proposals=sum((row['trace'] or {}).get('rejected_proposals', 0) for row in returned),
                traced_proposal_attempts=sum((row['trace'] or {}).get('proposal_attempts', 0) for row in returned),
                traced_operator_opportunities=sum((row['trace'] or {}).get('operator_opportunities', 0) for row in returned),
                lineage_event_count=sum(len(row['lineage_events']) for row in returned),
                actual_accepted_delta_events=sum(1 for row in returned for event in (row['trace'] or {}).get('operator_events', [])
                    if event.get('outcome') == 'accepted' and event.get('delta')))


def reliable(summary):
    return (summary['requested_count'] == COUNT and summary['candidate_count'] == COUNT
            and summary['candidate_failures'] == 0 and summary['valid_count'] == COUNT
            and summary['aligned_count'] == COUNT and summary.get('inputs_unchanged', True))


def judge_quality(cohorts):
    ordinary, opened = cohorts['ordinary'], cohorts['all_open']
    legacy_readability = [ordinary[seed]['legacy']['mean_readability'] for seed in BLOCKS]
    spread = abs(legacy_readability[0]-legacy_readability[1]) if None not in legacy_readability else None
    thresholds = {}
    for metric in ('mean_novelty', 'corpus_silhouette_entropy_bits', 'parent_copy_fraction'):
        values = [opened[seed]['legacy'][metric] for seed in BLOCKS]
        thresholds[metric] = ((max(values) if metric == 'parent_copy_fraction' else min(values))
                              if None not in values else None)
    def variation(summary):
        return all(summary[key] is not None and threshold is not None and
                   (summary[key] <= threshold if key == 'parent_copy_fraction' else summary[key] >= threshold)
                   for key, threshold in thresholds.items())
    per_block = {}
    for seed in BLOCKS:
        before = ordinary[seed]['legacy']['mean_readability']
        after = ordinary[seed][ARM]['mean_readability']
        loss = max(0, before-after) if before is not None and after is not None else None
        per_block[seed] = dict(readability_loss=loss,
            ordinary_readability=loss is not None and spread is not None and loss <= spread,
            all_open_variation=variation(opened[seed][ARM]),
            variation_by_metric={key: (opened[seed][ARM][key] is not None and threshold is not None and
                (opened[seed][ARM][key] <= threshold if key == 'parent_copy_fraction'
                 else opened[seed][ARM][key] >= threshold)) for key, threshold in thresholds.items()},
            clone_challenges_variation=not variation(opened[seed]['clone']),
            random_challenges_reliability=not reliable(opened[seed]['random_ungated']))
    checks = dict(complete_valid_aligned=all(reliable(cohorts[name][seed][arm])
                  for name in ('ordinary', 'all_open') for seed in BLOCKS for arm in ('legacy', ARM)))
    for key in ('ordinary_readability', 'all_open_variation', 'clone_challenges_variation',
                'random_challenges_reliability'):
        checks[key] = all(row[key] for row in per_block.values())
    return dict(checks=checks, between_seed_readability_spread=spread,
                all_open_thresholds=thresholds, per_block=per_block)


def measure_block(inputs, cohort, seed, arm):
    rows = []
    started = time.perf_counter()
    for index in range(COUNT):
        parent = deepcopy(inputs['parents'][index//10])
        profile = deepcopy(inputs['profile'])
        if cohort == 'all_open':
            parent, profile = all_open_inputs(parent, profile)
        rows.append(evaluate_candidate(parent, profile, inputs, arm=arm, seed=seed+index, index=index))
    return dict(summary=summarize_candidates(rows, requested_count=COUNT), rows=rows,
                generation_seconds=time.perf_counter()-started)


def intentional_controls(inputs):
    results = {}
    for name in ('zero_rates', 'all_locked'):
        rows = []
        for index, original in enumerate(inputs['parents']):
            parent = deepcopy(original)
            if name == 'zero_rates':
                parent['mutation'] = {key: 0 for key in RATE_KEYS}
            else:
                for cell in parent['cells']:
                    cell['locked'] = True
                for organ in parent['organs'].values():
                    organ['mutation_locked'] = True
            rows.append(evaluate_candidate(parent, inputs['profile'], inputs,
                arm=ARM, seed=BLOCKS[0]+index, index=index))
        results[name] = dict(summary=summarize_candidates(rows, requested_count=len(rows)), rows=rows)
    return results


def write_report(path, report):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2, allow_nan=False)+'\n', encoding='utf-8')


def write_measurement_report(path, report, appendix_path):
    """Keep every raw candidate/trace; committed metric rows reference a hash."""
    result = deepcopy(report)
    raw_rows = []
    def retain(rows, identity):
        for row in rows:
            ordinal = len(raw_rows)
            raw_rows.append(dict(identity=identity, row=deepcopy(row)))
            trace = row.pop('trace', None)
            row.pop('grid', None)
            row['trace_sha256'] = digest(trace) if trace is not None else None
            row['raw_evidence_ordinal'] = ordinal
    for cohort, blocks in result['metrics']['measurements'].items():
        for seed, arms in blocks.items():
            for arm, measured in arms.items():
                retain(measured['rows'], dict(cohort=cohort, seed_block=seed, arm=arm))
    for name, measured in result['metrics']['intentional_controls'].items():
        retain(measured['rows'], dict(intentional_control=name, arm=ARM))
    raw = b''.join(encoded(row)+b'\n' for row in raw_rows)
    appendix_path.parent.mkdir(parents=True, exist_ok=True)
    appendix_path.write_bytes(gzip.compress(raw, mtime=0))
    try:
        appendix_label = appendix_path.resolve().relative_to(ROOT).as_posix()
    except ValueError:  # unit-test temporary output, not a source artifact
        appendix_label = appendix_path.name
    result['raw_candidate_evidence'] = dict(format='jsonl+gzip', path=appendix_label,
        rows=len(raw_rows), sha256=file_hash(appendix_path), uncompressed_sha256=hashlib.sha256(raw).hexdigest(),
        uncompressed_bytes=len(raw), compressed_bytes=appendix_path.stat().st_size,
        includes='every actual candidate grid, complete trace, errors and metrics; zero-based raw_evidence_ordinal')
    write_report(path, result)
    return result


def validate_contract_review(receipt, measured_sources, current_sources):
    """A passed label cannot qualify stale, unbound or incomplete source review."""
    errors = []
    reviewed = receipt.get('source_sha256', {})
    if receipt.get('independent_review_passed') is not True:
        errors.append('independent_review_not_passed')
    if not isinstance(reviewed, dict) or set(reviewed) != set(G1_REVIEW_SOURCES):
        errors.append('review_source_inventory_incomplete_or_unknown')
        reviewed = reviewed if isinstance(reviewed, dict) else {}
    for name, expected in reviewed.items():
        if current_sources.get(name) != expected:
            errors.append('current_source_mismatch:' + name)
        if name in measured_sources and measured_sources[name] != expected:
            errors.append('measured_source_mismatch:' + name)
    # Direct operator computations must have been pinned in the actual run.
    for name in ('labs/grid_genome/operative_permissions.py',
                 'packages/mecha_engine/src/mecha_engine/generation/_operative_permissions.py',
                 'packages/mecha_engine/src/mecha_engine/generation/generate.py'):
        if name not in measured_sources:
            errors.append('operator_source_absent_from_measurement:' + name)
    return dict(passed=not errors, errors=errors,
                measurement_bound_review_sources=sorted(set(reviewed) & set(measured_sources)),
                supplemental_current_review_bindings=sorted(set(reviewed) - set(measured_sources)),
                current_sha256={name: current_sources.get(name) for name in reviewed})


def finalize_contract_review(report, receipt, *, receipt_path, original_path):
    """Assemble later review evidence; never rerun, rescore or relabel a sample."""
    result = deepcopy(report)
    current = {name: file_hash(ROOT/name) for name in G1_REVIEW_SOURCES if (ROOT/name).is_file()}
    binding = validate_contract_review(receipt, result['source_sha256_after'], current)
    if result['source_sha256_before'] != result['source_sha256_after']:
        binding['passed'] = False
        binding['errors'].append('measurement_sources_changed_during_run')
    result['metrics']['g1'] = dict(evidence=deepcopy(receipt), binding=binding,
        independent_review_passed=binding['passed'], source=receipt_path.resolve().relative_to(ROOT).as_posix(),
        source_sha256=file_hash(receipt_path))
    checks = result['metrics']['checks']
    checks['G1_independent_contract_review'] = binding['passed']
    failed = sorted(key for key, value in checks.items() if value is False)
    pending = sorted(key for key, value in checks.items() if value is None)
    result['closed_states'] = [key for key, value in checks.items() if value is True]
    old_gates = set(report['metrics']['checks'])
    result['blocked_states'] = failed + pending + [name for name in report['blocked_states'] if name not in old_gates]
    result['decision'].update(verdict='REFUSE' if failed else ('INCOMPLETE' if pending else 'STAGED_PASS'),
                              failed_checks=failed, pending_checks=pending)
    result['next_research_step'] = ('Retain REFUSE and address exact failed gates in separately preregistered work.'
        if failed else 'Obtain integration authorization for the registered damage/repair and evolution gates; no product promotion.')
    result['review_finalization'] = dict(original_measurement=original_path.resolve().relative_to(ROOT).as_posix(),
        original_measurement_sha256=file_hash(original_path),
        measured_harness_sha256=report['source_sha256_after']['labs/grid_genome/operative_mutation_gate.py'],
        finalizer_harness_sha256=file_hash(Path(__file__)),
        change='Added strict source-bound G1 finalizer and prospective review source inventory after the measurement; candidate and metric code/definitions unchanged.',
        new_measurement=False, numeric_samples_or_thresholds_changed=False)
    return result


def build_report(*, g0, g1_evidence=None):
    inputs = read_inputs()
    before = source_hashes()
    measurements, summaries = {}, {}
    for cohort in ('ordinary', 'all_open'):
        measurements[cohort], summaries[cohort] = {}, {}
        for seed in BLOCKS:
            measurements[cohort][seed], summaries[cohort][seed] = {}, {}
            arms = ('legacy', ARM) if cohort == 'ordinary' else ('legacy', ARM, 'clone', 'random_ungated')
            for arm in arms:
                measured = measure_block(inputs, cohort, seed, arm)
                measurements[cohort][seed][arm] = measured
                summaries[cohort][seed][arm] = measured['summary']
    controls = intentional_controls(inputs)
    quality = judge_quality(summaries)
    after = source_hashes()
    g1 = deepcopy(g1_evidence) if g1_evidence is not None else dict(status='pending_independent_review')
    if g1_evidence is not None:
        review = g1.get('evidence', g1)
        binding = validate_contract_review(review, before, after)
        g1['binding'] = binding
        g1['independent_review_passed'] = binding['passed']
    checks = dict(G0_formal_instrument=g0['passed'], G1_independent_contract_review=g1.get('independent_review_passed'),
                  G2_reliability=quality['checks']['complete_valid_aligned'],
                  G3_quality_and_controls=all(value for key, value in quality['checks'].items() if key != 'complete_valid_aligned'),
                  measured_sources_unchanged=before == after,
                  intentional_controls=all(row['summary']['candidate_failures'] == 0 and
                    row['summary']['valid_count'] == 10 and row['summary']['aligned_count'] == 10 and
                    row['summary']['parent_copy_fraction'] == 1 for row in controls.values()))
    failed = sorted(key for key, value in checks.items() if value is False)
    pending = sorted(key for key, value in checks.items() if value is None)
    return dict(artifact_id=ARTIFACT_ID, date='2026-10-06', status='measured',
        purpose='Qualify explicit descendant permissions without rewriting the legacy generator or historical evidence.',
        source_artifacts=sorted(before), source_sha256_before=before, source_sha256_after=after,
        parameters=dict(seed_blocks=list(BLOCKS), outputs_per_arm_block=COUNT, block_dependence=block_overlap(inputs),
            parent_schedule='formal package_hybrid LCD-filtered holdout schedule, index//10',
            split_ids={key:[grid['grid_id'] for grid in grids] for key, grids in inputs['split'].items()},
            split_sha256={key:digest(grids) for key, grids in inputs['split'].items()},
            generation_model_sha256=digest(asdict(inputs['model'])),
            effective_parent_ids=[grid['grid_id'] for grid in inputs['parents']],
            effective_parent_sha256=[digest(grid) for grid in inputs['parents']],
            ordinary_profile_sha256=digest(inputs['profile']), readability_model_sha256=digest(inputs['readability']),
            silhouette_metric='generation_bakeoff16._entropy_bits over generation_bakeoff16._signature',
            parent_copy_metric='phenotype_signature; semantic/rendered equality excluding permission/state/evidence fields',
            promotion_scope='named opt-in only; legacy remains default'),
        metrics=dict(g0=g0, g1=g1, measurements=measurements, summaries=summaries,
                     quality=quality, intentional_controls=controls, checks=checks),
        closed_states=[key for key,value in checks.items() if value],
        blocked_states=failed+pending+['product_consumers_unqualified','damage_repair_permission_carrier_unqualified',
                              'evolution_comparison_not_run','native_product_promotion_not_permitted'],
        decision=dict(verdict='REFUSE' if failed else ('INCOMPLETE' if pending else 'STAGED_PASS'), failed_checks=failed, pending_checks=pending,
                      consumer_promotion=False, legacy_default_unchanged=True),
        next_research_step=('Retain measured refusal; reopen only through separately preregistered evidence addressing these exact failed gates.'
                            if failed else ('Complete independent G1 evidence review before qualifying later consumer studies.' if pending
                                           else 'Obtain integration authorization for the registered damage/repair and evolution gates.')))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--g0-only', action='store_true')
    parser.add_argument('--finalize-existing', type=Path)
    parser.add_argument('--g0', type=Path, default=ROOT/'.development/x6/science/g0.json')
    parser.add_argument('--g1-evidence', type=Path)
    parser.add_argument('--output', type=Path, default=ROOT/'data/grid_genome/operative_mutation_stage0.json')
    parser.add_argument('--appendix', type=Path, default=ROOT/'.development/x6/science/candidates.jsonl.gz')
    args = parser.parse_args()
    if args.finalize_existing is not None:
        if args.g1_evidence is None:
            raise ValueError('Finalization requires an explicit independent source review receipt.')
        report = json.loads(args.finalize_existing.read_text(encoding='utf-8'))
        receipt = json.loads(args.g1_evidence.read_text(encoding='utf-8'))
        final = finalize_contract_review(report, receipt, receipt_path=args.g1_evidence,
                                         original_path=args.finalize_existing)
        write_report(args.output, final)
        print(json.dumps(dict(decision=final['decision'], binding=final['metrics']['g1']['binding'],
                              finalization=final['review_finalization']), indent=2))
        return 0 if final['metrics']['g1']['binding']['passed'] else 1
    if args.g0_only:
        result = reproduce_formal()
        write_report(args.g0, result)
        print(json.dumps(result, indent=2))
        return 0 if result['passed'] else 1
    if not args.g0.is_file():
        raise ValueError('Run --g0-only first; the formal instrument must be recorded before G2/G3.')
    g0 = json.loads(args.g0.read_text(encoding='utf-8'))
    if not g0['passed'] or g0['source_sha256_after'] != file_hash(ROOT/FORMAL_PATH):
        raise ValueError('G0 failed or the committed instrument changed; later measurement is refused.')
    evidence = None
    if args.g1_evidence is not None:
        evidence = json.loads(args.g1_evidence.read_text(encoding='utf-8'))
        evidence = dict(evidence=evidence, source=args.g1_evidence.resolve().relative_to(ROOT).as_posix(),
                        source_sha256=file_hash(args.g1_evidence),
                        independent_review_passed=evidence.get('independent_review_passed'))
    report = build_report(g0=g0, g1_evidence=evidence)
    report = write_measurement_report(args.output, report, args.appendix)
    print(json.dumps(dict(decision=report['decision'], quality=report['metrics']['quality'],
                         summaries=report['metrics']['summaries']), indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())




