"""The care gate can refuse; source tapes and missing results stay honest."""
from copy import deepcopy
import unittest

from observed_care_gate import judge, prefix, altered_metadata, PAIR_COUNT, CARE_EVALUATORS, REQUIRED_CHECKS, SEEDS
from test_observed_care_selection import context
from observed_care_selection import validate_care_context

class CareGateTests(unittest.TestCase):
    def rows(self,different=True):
        return [{'checks':dict.fromkeys(REQUIRED_CHECKS,True),'elapsed_seconds':1.0,
                 'pair_index':index,'founder_index':index%10,'rng_seed':SEEDS[index//10],
                 'evaluators':{name:{'selected_structures_differ':different}
                 for name in CARE_EVALUATORS}} for index in range(PAIR_COUNT)]
    def test_null_complete_cohort_refuses(self):
        for result in judge(self.rows(False),True,True).values():
            self.assertEqual(result['verdict'],'REFUSE')
            self.assertEqual(result['failed_checks'],['structural_descendant_effect'])
    def test_missing_pair_does_not_pass(self):
        self.assertTrue(all(r['verdict']=='REFUSE' for r in judge(self.rows()[:-1],True,True).values()))
    def test_hard_invariant_and_source_change_refuse(self):
        rows=self.rows();rows[0]['checks']['off_exact']=False
        self.assertTrue(all(r['verdict']=='REFUSE' for r in judge(rows,True,True).values()))
        self.assertTrue(all(r['verdict']=='REFUSE' for r in judge(self.rows(),True,False).values()))
    def test_complete_positive_gate_is_falsifiable(self):
        self.assertTrue(all(r['verdict']=='ADOPT' for r in judge(self.rows(),True,True).values()))
    def test_every_required_check_is_explicit_true(self):
        for key in REQUIRED_CHECKS:
            for value in (None,False,1):
                rows=self.rows();rows[0]['checks'][key]=value
                with self.subTest(key=key,value=value):
                    self.assertTrue(all(r['verdict']=='REFUSE' for r in judge(rows,True,True).values()))
            rows=self.rows();rows[0]['checks'].pop(key)
            self.assertTrue(all(r['verdict']=='REFUSE' for r in judge(rows,True,True).values()))
        rows=self.rows();rows[0]['checks']={}
        self.assertTrue(all(r['verdict']=='REFUSE' for r in judge(rows,True,True).values()))
    def test_duplicate_missing_and_misordered_pair_identity_refuse(self):
        for key,value in (('pair_index',1),('founder_index',1),('rng_seed',0)):
            rows=self.rows();rows[0][key]=value
            self.assertTrue(all(r['verdict']=='REFUSE' for r in judge(rows,True,True).values()))
        rows=self.rows();rows[1]=deepcopy(rows[0])
        self.assertTrue(all(r['verdict']=='REFUSE' for r in judge(rows,True,True).values()))
    def test_measured_total_and_pair_runtime_refuse(self):
        rows=self.rows()
        total=judge(rows,True,True,elapsed_seconds=300.001)
        self.assertTrue(all(r['verdict']=='REFUSE' and 'registered_runtime' in r['failed_checks'] for r in total.values()))
        rows[0]['elapsed_seconds']=30.001
        pair=judge(rows,True,True,elapsed_seconds=299)
        self.assertTrue(all(r['verdict']=='REFUSE' and 'registered_runtime' in r['failed_checks'] for r in pair.values()))
    def test_operational_failure_precludes_adoption_even_complete(self):
        results=judge(self.rows(),True,True,elapsed_seconds=10,failure={'kind':'worker_error'})
        self.assertTrue(all(r['verdict']=='REFUSE' for r in results.values()))
    def test_prefix_uses_only_actual_events_and_clock(self):
        source=context(12);original=deepcopy(source)
        used=prefix(source,7)
        self.assertEqual(used['events'],source['events'][:7])
        self.assertEqual(used['last_age_ticks'],7)
        self.assertEqual(used['care_summary']['ticks_observed'],7)
        self.assertEqual(source,original)
        with self.assertRaises(ValueError):prefix(source,13)
    def test_metadata_control_changes_no_observed_actions(self):
        source=context();other=altered_metadata(source)
        self.assertEqual([(e['actor'],e['action']) for e in source['events']],
                         [(e['actor'],e['action']) for e in other['events']])
        self.assertNotEqual(source['care_summary'],other['care_summary'])
    def test_untrusted_unhashable_actor_refuses_cleanly(self):
        source=context();source['events'][0]['actor']=[]
        with self.assertRaises(ValueError):validate_care_context(source)
