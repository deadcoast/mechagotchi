"""Synthetic guard checks; these do not establish actual population extinction."""
import copy
import unittest
from body_workload_native_successor import qualified_terminal_extinction

def report():
    return dict(living_population=dict(final_breeders=[],termination=dict(ended=True,reason='no_eligible_breeders',
        genuine_lifecycle_extinction=True,generation_index=1,lifecycle_deaths=1)),generations=[
        dict(generation=0,creatures=[]),dict(generation=1,creatures=[dict(cycles=[dict(episode=dict(alive=False,death_cause='energy_collapse'))],breeding=dict(final_episode=None))])])

class ConditionalNativeGuardTests(unittest.TestCase):
    def test_real_terminal_shape_is_required(self):
        value=report();self.assertTrue(qualified_terminal_extinction(value))
        for field,replacement in [('reason','all_structurally_invalid'),('genuine_lifecycle_extinction',False),('generation_index',0),('lifecycle_deaths',0)]:
            bad=copy.deepcopy(value);bad['living_population']['termination'][field]=replacement
            with self.subTest(field=field):self.assertFalse(qualified_terminal_extinction(bad))
    def test_prior_death_cannot_qualify_terminal_structural_wipeout(self):
        value=report();value['generations'][0]['creatures']=value['generations'][1]['creatures']
        value['generations'][1]['creatures']=[dict(cycles=[],breeding=dict(final_episode=None))]
        self.assertFalse(qualified_terminal_extinction(value))
    def test_breeders_or_missing_evidence_refuse(self):
        value=report();value['living_population']['final_breeders']=[{}]
        self.assertFalse(qualified_terminal_extinction(value))
        for value in (None,{},report()['generations']):self.assertFalse(qualified_terminal_extinction(value))
if __name__=='__main__':unittest.main()
