"""Prospective X8 earned-role and density permission controls.

Synthetic unlock facts here test authority guards only, never play qualification.
"""
import copy
import json
import sys
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
for rel in ('labs/game_loop','game/src','packages/mecha_engine/src'):
    sys.path.insert(0,str(ROOT/rel))
import session_runner as lab
from mecha_game import covenant as product

STARTER=['body_core','sensor','expression','locomotion']
BASE=json.loads((ROOT/'data/slips/valid/slip_v2_cleanliness.json').read_text())
PARAMS={'population':16,'generations':6}
def fact(axis,tier):
    return dict(axis=axis,tier=tier,earned_era_index=0,metric_path='unit_guard_only',metric_value=99,threshold=1)
def profile(restricted=True):
    p=copy.deepcopy(BASE)
    if restricted:p['grid']['allowed_organ_roles']=STARTER[:]
    return p
def state(facts=()):
    p=profile()
    return dict(active_campaign_id='guard',base_profile=copy.deepcopy(p),base_engine_parameters=PARAMS.copy(),engine_parameters=PARAMS.copy(),
      campaigns=[dict(campaign_id='guard',predecessor_campaign_id=None,slip_profile=p,unlocks=list(facts))])

class ProgressionControls:
    module=None
    def test_roles_follow_exact_niche_tiers(self):
        for tier,extras in ((0,[]),(1,['ornament']),(2,['ornament','effect']),(3,['ornament','effect'])):
            b=self.module.covenant_budget(profile(),PARAMS,[fact('niche_mastery',tier)] if tier else [])
            self.assertEqual(STARTER+extras,b['allowed_organ_roles'])
    def test_unrestricted_base_remains_unrestricted(self):
        self.assertIsNone(self.module.covenant_budget(profile(False),PARAMS,[])['allowed_organ_roles'])
    def test_imported_base_roles_are_not_removed_or_counted_twice(self):
        p=profile();p['grid']['allowed_organ_roles']+=['effect']
        b=self.module.covenant_budget(p,PARAMS,[fact('niche_mastery',2)])
        self.assertEqual(STARTER+['effect','ornament'],b['allowed_organ_roles'])
    def test_density_requires_storm_record(self):
        for facts,allowed in (([],False),([fact('niche_mastery',3)],False),([fact('storm_record',1)],True),([fact('storm_record',2)],True)):
            self.assertEqual(allowed,self.module.covenant_budget(profile(),PARAMS,facts)['cubff_density_pressure_allowed'])
    def test_budget_never_mutates_inputs(self):
        args=(profile(),PARAMS.copy(),[fact('niche_mastery',1)])
        original=copy.deepcopy(args);self.module.covenant_budget(*args)
        self.assertEqual(original,args)

class LabEarnedPreparationTests(ProgressionControls,unittest.TestCase):
    module=lab
    def test_unearned_role_and_mixed_spend_are_atomic_refusal(self):
        s=state();before=copy.deepcopy(s)
        v=lab.apply_covenant_change(s,allowed_organ_roles=STARTER+['effect'],population=1)
        self.assertFalse(v['ok']);self.assertEqual(before,s)
    def test_earned_role_changes_actual_covenant_and_keeps_base(self):
        s=state([fact('niche_mastery',1)]);base=copy.deepcopy(s['base_profile'])
        v=lab.apply_covenant_change(s,allowed_organ_roles=STARTER+['ornament'])
        self.assertTrue(v['ok'],v);self.assertEqual(STARTER+['ornament'],s['campaigns'][0]['slip_profile']['grid']['allowed_organ_roles'])
        self.assertEqual(base,s['base_profile'])
    def test_empty_duplicate_unknown_and_required_role_removal_refuse(self):
        for roles in ([],STARTER+['locomotion'],STARTER+['nonsense'],['locomotion']):
            s=state([fact('niche_mastery',2)]);before=copy.deepcopy(s)
            v=lab.apply_covenant_change(s,allowed_organ_roles=roles)
            self.assertFalse(v['ok'],roles);self.assertEqual(before,s)

class ProductEarnedPreparationTests(ProgressionControls,unittest.TestCase):
    module=product
    def test_budget_is_exact_lab_parity(self):
        for restricted in (True,False):
            for tier in range(4):
                args=(profile(restricted),PARAMS,[fact('niche_mastery',tier),fact('storm_record',min(tier,2))])
                self.assertEqual(lab.covenant_budget(*args),product.covenant_budget(*args))
    def test_explicit_starter_is_fresh_copy_and_preserves_species_mechanics(self):
        p=profile(False);before=copy.deepcopy(p)
        actual=product.starter_role_covenant(p)
        self.assertEqual(STARTER,actual['grid']['allowed_organ_roles'])
        actual.pop('grid');expected=copy.deepcopy(p);expected.pop('grid')
        self.assertEqual(expected,actual);self.assertEqual(before,p)

if __name__=='__main__':unittest.main()
