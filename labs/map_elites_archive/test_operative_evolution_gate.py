import copy
import unittest

from operative_evolution_gate import (ARM, SEEDS, PROTOCOL, judge_evolution,
                                     reproduce_headline, summarize_run)


SOURCES={'labs/example.py':'abc', 'data/example.json':'def'}


def row(arm, seed, coverage=.8, qd=400):
    return dict(arm=arm, rng_seed=seed, status='returned', configuration=copy.deepcopy(PROTOCOL),
                evaluations_total=20480, coverage=coverage, qd_score=qd,
                occupied_niches=410, candidate_failures=0, refusals=0, slip_illegal_elites=0,
                invalid_elites=0, elapsed_seconds=1, sources_unchanged=True,
                operator_counters_qualified=True, source_sha256_before=copy.deepcopy(SOURCES),
                source_sha256_after=copy.deepcopy(SOURCES))


def runs():
    return [row(arm, seed) for arm in ('legacy', ARM) for seed in SEEDS]


class EvolutionGateTests(unittest.TestCase):
    def test_all_declared_conditions_can_pass(self):
        self.assertEqual('STAGED_PASS', judge_evolution(runs(), instrument={'passed':True},current_sources=SOURCES)['verdict'])

    def test_each_stable_run_must_share_complete_source_and_input_snapshot(self):
        for change in ('changed', 'added', 'removed'):
            data=runs()
            for field in ('source_sha256_before','source_sha256_after'):
                if change=='changed': data[-1][field]['labs/example.py']='different'
                elif change=='added': data[-1][field]['labs/lazy.py']='extra'
                else: data[-1][field].pop('data/example.json')
            result=judge_evolution(data,instrument={'passed':True},current_sources=SOURCES)
            self.assertFalse(result['checks']['source_stable'],change)
            self.assertEqual('REFUSE',result['verdict'])

    def test_shared_snapshot_must_match_complete_current_inventory(self):
        for current in ({}, {**SOURCES,'labs/lazy.py':'new'}, {**SOURCES,'data/example.json':'new'}):
            result=judge_evolution(runs(),instrument={'passed':True},current_sources=current)
            self.assertFalse(result['checks']['source_stable'])

    def test_zero_spread_is_zero_allowance(self):
        for metric in ('coverage','qd_score'):
            data=runs()
            for item in data:
                if item['arm']==ARM: item[metric]-=.000001
            self.assertEqual('REFUSE',judge_evolution(data,instrument={'passed':True},current_sources=SOURCES)['verdict'])

    def test_one_seed_millionth_cost_cannot_round_away_at_zero_spread(self):
        data=runs();data[-1]['coverage']-=.000001
        result=judge_evolution(data,instrument={'passed':True},current_sources=SOURCES)
        self.assertEqual(0,result['controls']['coverage_cost'])  # display only
        self.assertFalse(result['checks']['coverage_preserved'])
        self.assertEqual('REFUSE',result['verdict'])

    def test_published_rounding_boundary_is_judged_as_published(self):
        data=runs()
        values=[398.1,399.1,400.1]
        for index,item in enumerate(data[:3]): item['qd_score']=values[index]
        reference=399.1
        for item in data[3:]: item['qd_score']=reference-2
        result=judge_evolution(data,instrument={'passed':True},current_sources=SOURCES)
        self.assertEqual(2,result['controls']['quality_cost'])
        self.assertEqual(2,result['controls']['quality_spread'])
        self.assertTrue(result['checks']['quality_preserved'])

    def test_one_failed_dirty_illegal_or_slow_seed_cannot_hide_in_mean(self):
        for field,value in (('candidate_failures',1),('refusals',1),('slip_illegal_elites',1),
                             ('invalid_elites',1),('elapsed_seconds',1200.001),
                             ('sources_unchanged',False),('operator_counters_qualified',False)):
            data=runs();data[-1][field]=value
            self.assertEqual('REFUSE',judge_evolution(data,instrument={'passed':True},current_sources=SOURCES)['verdict'],field)

    def test_incomplete_and_unequal_scoring_budgets_refuse(self):
        for count in (256,20479,20481):
            data=runs();data[-1]['evaluations_total']=count
            self.assertFalse(judge_evolution(data,instrument={'passed':True},current_sources=SOURCES)['checks']['complete_budget'])

    def test_declared_seed_set_and_exact_protocol_are_required(self):
        for change in ('missing','duplicate','wrong_population'):
            data=runs()
            if change=='missing': data.pop()
            elif change=='duplicate': data[-1]['rng_seed']=data[-2]['rng_seed']
            else: data[-1]['configuration']['population']=512
            self.assertEqual('REFUSE',judge_evolution(data,instrument={'passed':True},current_sources=SOURCES)['verdict'],change)

    def test_first_instrument_failure_blocks_even_high_quality_arm(self):
        self.assertFalse(judge_evolution(runs(),instrument={'passed':False},current_sources=SOURCES)['checks']['instrument_reproduced'])

    def test_exception_cannot_qualify_an_empty_result(self):
        data=runs();data[-1].update(status='exception',coverage=None,qd_score=None)
        self.assertEqual('REFUSE',judge_evolution(data,instrument={'passed':True},current_sources=SOURCES)['verdict'])

    def test_exact_headline_ignores_runtime_but_no_scientific_field(self):
        expected=dict(rng_seed=20260709,adopted_occupied=451,adopted_coverage=.880859,
                      adopted_qd=411.738214,adopted_refusals=0,adopted_illegal_elites=0)
        actual=row('legacy',20260709,.880859,411.738214);actual['occupied_niches']=451
        self.assertTrue(reproduce_headline(actual,expected)['passed'])
        actual['qd_score']+=.000001
        self.assertFalse(reproduce_headline(actual,expected)['passed'])

    def test_gains_are_not_penalized_with_zero_spread(self):
        data=runs()
        for item in data[3:]: item.update(coverage=.9,qd_score=450)
        result=judge_evolution(data,instrument={'passed':True},current_sources=SOURCES)
        self.assertEqual(0,result['controls']['coverage_cost'])
        self.assertEqual(0,result['controls']['quality_cost'])
        self.assertEqual('STAGED_PASS',result['verdict'])


if __name__=='__main__': unittest.main()

