import copy
import gzip
import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from operative_mutation_gate import (
    all_open_inputs, compare_formal, evaluate_candidate, judge_quality,
    phenotype_signature, read_inputs, summarize_candidates, _entropy_bits, silhouette_signature, write_measurement_report, block_overlap, validate_contract_review, G1_REVIEW_SOURCES,
)


def arm(readability=.5, novelty=.3, entropy=.8, copies=.1):
    return dict(requested_count=100, candidate_count=100, candidate_failures=0,
                valid_count=100, aligned_count=100, mean_readability=readability,
                mean_novelty=novelty, corpus_silhouette_entropy_bits=entropy,
                parent_copy_fraction=copies)


def cohorts():
    return {name: {seed: {'legacy': arm(), 'operative_permissions_v1': arm(),
                        'clone': arm(novelty=0, copies=1),
                        'random_ungated': {**arm(), 'valid_count': 30, 'aligned_count': 10}}
                   for seed in (20260706, 20260707)} for name in ('ordinary', 'all_open')}


class QualificationGateTests(unittest.TestCase):
    def test_exact_formal_comparison_excludes_only_time(self):
        prior = dict(arm='package_hybrid', candidate_count=100, validity_rate=1,
                     mean_novelty=.151401, generation_seconds=.1)
        current = {**prior, 'generation_seconds': 10}
        self.assertTrue(compare_formal(prior, current)['passed'])
        current['mean_novelty'] += .000001
        self.assertFalse(compare_formal(prior, current)['passed'])
        current.pop('candidate_count')
        self.assertIn('candidate_count', compare_formal(prior, current)['different_metrics'])

    def test_gate_can_pass_when_controls_challenge_it(self):
        result = judge_quality(cohorts())
        self.assertTrue(all(result['checks'].values()), result)

    def test_zero_spread_does_not_invent_readability_tolerance(self):
        data = cohorts()
        data['ordinary'][20260706]['operative_permissions_v1']['mean_readability'] -= .000001
        self.assertFalse(judge_quality(data)['checks']['ordinary_readability'])

    def test_each_block_must_pass_without_pooling_rescue(self):
        data = cohorts()
        data['all_open'][20260706]['operative_permissions_v1']['mean_novelty'] = .29
        data['all_open'][20260707]['operative_permissions_v1']['mean_novelty'] = .99
        self.assertFalse(judge_quality(data)['checks']['all_open_variation'])

    def test_entropy_and_parent_copy_are_independent_gates(self):
        for field, value in (('corpus_silhouette_entropy_bits', .79), ('parent_copy_fraction', .11)):
            data = cohorts()
            data['all_open'][20260706]['operative_permissions_v1'][field] = value
            self.assertFalse(judge_quality(data)['checks']['all_open_variation'], field)

    def test_missing_failed_invalid_unaligned_candidates_refuse(self):
        for field, value in (('candidate_count', 99), ('candidate_failures', 1),
                             ('valid_count', 99), ('aligned_count', 99)):
            data = cohorts()
            data['ordinary'][20260706]['operative_permissions_v1'][field] = value
            self.assertFalse(judge_quality(data)['checks']['complete_valid_aligned'], field)

    def test_controls_cannot_silently_pass(self):
        data = cohorts()
        for seed in data['all_open']:
            data['all_open'][seed]['clone'] = arm()
            data['all_open'][seed]['random_ungated'] = arm()
        checks = judge_quality(data)['checks']
        self.assertFalse(checks['clone_challenges_variation'])
        self.assertFalse(checks['random_challenges_reliability'])

    def test_missing_quality_does_not_qualify_a_failed_candidate_subset(self):
        data = cohorts()
        data['ordinary'][20260706]['operative_permissions_v1']['mean_readability'] = None
        self.assertFalse(judge_quality(data)['checks']['ordinary_readability'])


class ReviewBindingTests(unittest.TestCase):
    def setUp(self):
        self.sources = {name: 'a'*64 for name in G1_REVIEW_SOURCES}
        self.receipt = dict(independent_review_passed=True, source_sha256=self.sources)

    def test_complete_current_receipt_passes(self):
        self.assertTrue(validate_contract_review(self.receipt, self.sources, self.sources)['passed'])

    def test_stale_current_or_measured_hash_cannot_pass(self):
        name = next(iter(self.sources))
        stale = {**self.sources, name: 'b'*64}
        self.assertFalse(validate_contract_review(self.receipt, self.sources, stale)['passed'])
        self.assertFalse(validate_contract_review(self.receipt, stale, self.sources)['passed'])

    def test_incomplete_false_or_hashless_review_is_not_qualification(self):
        for receipt in ({'independent_review_passed': True},
                        {**self.receipt, 'independent_review_passed': False},
                        {**self.receipt, 'source_sha256': {}}):
            self.assertFalse(validate_contract_review(receipt, self.sources, self.sources)['passed'])

    def test_supplemental_review_files_are_explicitly_not_run_bound(self):
        name = 'packages/mecha_engine/src/mecha_engine/generation/explain.py'
        measured = {key: value for key, value in self.sources.items() if key != name}
        result = validate_contract_review(self.receipt, measured, self.sources)
        self.assertTrue(result['passed'])
        self.assertEqual([name], result['supplemental_current_review_bindings'])
        self.assertNotIn(name, result['measurement_bound_review_sources'])


class MeasurementTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.inputs = read_inputs()

    def test_corpus_entropy_counts_repeated_and_distinct_role_signatures(self):
        parent = self.inputs['parents'][0]
        other = copy.deepcopy(parent)
        other['cells'][0]['role'] = 'different'
        a, b = silhouette_signature(parent), silhouette_signature(other)
        self.assertNotEqual(a, b)
        self.assertEqual(0, _entropy_bits([a, a, a, a]))
        self.assertEqual(1, _entropy_bits([a, a, b, b]))
        self.assertEqual(2, _entropy_bits(['a', 'b', 'c', 'd']))
        rows = [evaluate_candidate(parent, self.inputs['profile'], self.inputs,
                                   arm='clone', seed=20260706+i, index=i) for i in range(4)]
        summary = summarize_candidates(rows, requested_count=4)
        self.assertEqual(0, summary['corpus_silhouette_entropy_bits'])
        self.assertGreater(summary['mean_silhouette_entropy_feature'], 0)

    def test_appendix_preserves_every_grid_trace_failure_and_hash(self):
        rows = [dict(index=0, status='returned', grid={'cells': [1]}, trace={'events': [2]}),
                dict(index=1, status='exception', trace=None, error='real refusal')]
        report = dict(metrics=dict(measurements={'ordinary': {20260706: {'test': {'rows': rows}}}},
                                   intentional_controls={}))
        before = copy.deepcopy(report)
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)
            lean = write_measurement_report(path/'metric.json', report, path/'raw.jsonl.gz')
            raw = (path/'raw.jsonl.gz').read_bytes()
            self.assertEqual(hashlib.sha256(raw).hexdigest(), lean['raw_candidate_evidence']['sha256'])
            unpacked = [json.loads(line) for line in gzip.decompress(raw).splitlines()]
            self.assertEqual(rows, [row['row'] for row in unpacked])
            self.assertEqual(2, lean['raw_candidate_evidence']['rows'])
            saved_rows = lean['metrics']['measurements']['ordinary'][20260706]['test']['rows']
            self.assertEqual('real refusal', saved_rows[1]['error'])
            self.assertNotIn('trace', saved_rows[0])
            self.assertNotIn('grid', saved_rows[0])
            self.assertEqual(1, saved_rows[1]['raw_evidence_ordinal'])
            self.assertEqual(before, report)

    def test_adjacent_fixed_blocks_are_honestly_not_independent(self):
        overlap = block_overlap(self.inputs)
        self.assertEqual(90, overlap['shared_parent_seed_pairs'])
        self.assertEqual(.9, overlap['fraction_of_each_block'])
        self.assertIn('not independent', overlap['interpretation'])

    def test_open_transform_changes_only_declared_permissions(self):
        parent, profile = self.inputs['parents'][0], self.inputs['profile']
        original = copy.deepcopy((parent, profile))
        opened, covenant = all_open_inputs(parent, profile)
        self.assertEqual(original, (parent, profile))
        self.assertEqual(phenotype_signature(parent), phenotype_signature(opened))
        self.assertTrue(all(value == 1 for value in opened['mutation'].values()))
        self.assertTrue(all(value == 1 for value in covenant['mutation'].values()))
        self.assertTrue(all(not cell['locked'] and cell['mutation_weight'] == 1 for cell in opened['cells']))
        self.assertTrue(all(not organ.get('mutation_locked', False) for organ in opened['organs'].values()))

    def test_phenotype_excludes_identity_permissions_and_list_order(self):
        parent = self.inputs['parents'][0]
        child = copy.deepcopy(parent)
        child['grid_id'] = 'different'
        child['cells'].reverse()
        child['cells'][0]['mutation_weight'] = .9
        child['cells'][0]['locked'] = True
        self.assertEqual(phenotype_signature(parent), phenotype_signature(child))
        child['cells'][0]['material'] = 'changed'
        self.assertNotEqual(phenotype_signature(parent), phenotype_signature(child))

    def test_exception_is_retained_and_not_counted_as_a_candidate(self):
        def fail(*args, **kwargs):
            raise ValueError('instrumented actual refusal')
        row = evaluate_candidate(self.inputs['parents'][0], self.inputs['profile'],
                                 self.inputs, arm='operative_permissions_v1',
                                 seed=20260706, index=0, generator=fail)
        self.assertEqual('exception', row['status'])
        self.assertEqual('ValueError', row['exception_type'])
        self.assertIn('instrumented actual refusal', row['error'])
        summary = summarize_candidates([row], requested_count=1)
        self.assertEqual(0, summary['candidate_count'])
        self.assertEqual(1, summary['candidate_failures'])
        self.assertIsNone(summary['mean_readability'])

    def test_clone_and_random_controls_are_measured_not_labelled(self):
        rows = [evaluate_candidate(self.inputs['parents'][i % len(self.inputs['parents'])],
                                   self.inputs['profile'], self.inputs, arm='random_ungated',
                                   seed=20260706 + i, index=i) for i in range(20)]
        self.assertTrue(any(not row['valid'] or not row['aligned'] for row in rows))
        clone = evaluate_candidate(self.inputs['parents'][0], self.inputs['profile'],
                                   self.inputs, arm='clone', seed=20260706, index=0)
        self.assertTrue(clone['parent_copy'])
        self.assertEqual(0, clone['novelty'])


if __name__ == '__main__':
    unittest.main()





