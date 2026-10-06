"""X8 native preparation guards; fixtures are not survival qualification."""
import copy,json,sys,tempfile,unittest
from pathlib import Path
from unittest.mock import patch,Mock
ROOT=Path(__file__).resolve().parents[2]
for rel in ('game/src','packages/mecha_engine/src'):sys.path.insert(0,str(ROOT/rel))
from mecha_game.app import _EraBench,build_parser
from mecha_game.covenant import STARTER_ORGAN_ROLES
from mecha_game.campaign import ERA_CONFIG

class SurvivalPreparationTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.home=Path(self.tmp.name)
        self.bench=_EraBench('session',state_path=self.home/'campaign_state.json',ledger_path=self.home/'campaign.sqlite3',
            initial_profile=json.loads((ROOT/'data/slips/valid/slip_v2_cleanliness.json').read_text()))
    def inventory(self):return {str(p.relative_to(self.home)):p.read_bytes() for p in self.home.rglob('*') if p.is_file()}
    def test_cli_options_are_explicit_and_omitted_defaults_preserve_saved_choices(self):
        args=build_parser().parse_args([])
        self.assertIsNone(args.population_policy);self.assertIsNone(args.prepare_survival_regime)
        self.assertIsNone(args.prepare_density_pressure);self.assertFalse(args.starter_roles)
        values=build_parser().parse_args(['--population-policy','generation_survivors_v1','--campaign-seed','20260700','--prepare-survival-regime','stress_probe','--prepare-density-pressure','on','--starter-roles'])
        self.assertEqual(20260700,values.campaign_seed);self.assertEqual('on',values.prepare_density_pressure)
    def test_explicit_new_population_persists_and_restarts(self):
        self.bench.choose_new_campaign('generation_survivors_v1',base_seed=20260700)
        self.assertEqual('generation_survivors_v1',self.bench.ensure().population_policy)
        self.assertEqual(ERA_CONFIG,self.bench.ensure().era_config)
        self.assertEqual(20260700,self.bench.ensure().campaign['base_seed'])
        again=_EraBench('session',state_path=self.bench.state_path,ledger_path=self.bench.ledger_path)
        self.assertEqual('generation_survivors_v1',again.ensure().population_policy)
    def test_existing_campaign_cannot_be_reinterpreted(self):
        self.bench.choose_new_campaign('legacy_archive');before=self.inventory()
        with self.assertRaises(ValueError):self.bench.choose_new_campaign('generation_survivors_v1')
        self.assertEqual(before,self.inventory())
    def test_optional_role_starter_is_campaign_base_only(self):
        self.bench.choose_new_campaign('generation_survivors_v1',starter_roles=True)
        c=self.bench.ensure()
        self.assertEqual(list(STARTER_ORGAN_ROLES),c.base_profile['grid']['allowed_organ_roles'])
        self.assertEqual(c.base_profile,c.campaign['slip_profile'])
        self.assertEqual('designed_covenant',c.base_covenant_source['source_kind'])
    def test_harder_setting_persists_without_running_an_era(self):
        self.bench.choose_survival_regime('stress_probe')
        again=_EraBench('session',state_path=self.bench.state_path,ledger_path=self.bench.ledger_path)
        self.assertEqual('stress_probe',again.plan.survival_regime)
        self.assertFalse(self.bench.ledger_path.exists())
    def test_density_refusal_preserves_preparation_without_earned_fact(self):
        self.bench.choose_weather(3);before=self.inventory()
        with self.assertRaises(ValueError):self.bench.choose_density_pressure(True)
        self.assertEqual(before,self.inventory())
    def test_density_needs_a_weather_source_even_with_fact(self):
        current=self.bench.ensure();before=self.inventory()
        with patch.object(current,'budget',return_value={'cubff_density_pressure_allowed':True}):
            with self.assertRaises(ValueError):self.bench.choose_density_pressure(True)
        self.assertEqual(before,self.inventory())
    def test_versioned_campaign_history_opens_without_writes(self):
        from mecha_game.era_review import EraReview
        self.bench.choose_new_campaign('generation_survivors_v1')
        before=self.inventory()
        review=EraReview.load(self.home)
        self.assertIsNone(review.current)
        self.assertEqual(before,self.inventory())
    def test_review_distinguishes_empty_population_from_historical_archive(self):
        from mecha_game.era_review import EraReview
        era=dict(era_index=0,went_extinct=True,weather={'forecast':'storm'},report={
            'summary':{'generation_count':2,'archive':{'filled_niches':4}},'generations_requested':2,
            'living_population':{'format':'generation_survivors_v1','survival_regime':'stress_probe',
              'final_breeders':[],'evaluated_candidates':12,'requested_candidate_slots':12,'unexecuted_candidate_slots':0,
              'termination':{'ended':True,'reason':'no_eligible_breeders','lifecycle_deaths':6,'structural_disqualifications':0}}})
        lines='\n'.join(EraReview({'campaign_id':'guard','eras':[era],'unlocks':[]}).lines())
        self.assertIn('Living breeders: 0',lines)
        self.assertIn('Historical archive: 4',lines)
        self.assertIn('Create successor',lines)
    def test_occurrence_origin_survives_nonwinning_parent_and_duplicate_ids(self):
        from mecha_game.execution_readout import descendant_lines
        from mecha_engine.runtime.care import care_grid_sha256
        grid=json.loads((ROOT/'data/seed_grids_16x16/mg_seed16_001_beetle.json').read_text())
        parent=copy.deepcopy(grid);parent['grid_id']='parent_occurrence'
        child=copy.deepcopy(grid);child['grid_id']='child_occurrence'
        report={'living_population':{'format':'generation_survivors_v1'},'generations':[
          {'creatures':[{'archive_decision':'rejected','breeding':{'occurrence':{'generation_index':0,'candidate_index':0},
           'final_grid_sha256':care_grid_sha256(parent),'eligible':True,'parent_occurrence':{'kind':'submitted_founder','submission_index':0}}}]},
          {'creatures':[{'archive_decision':'inserted','breeding':{'occurrence':{'generation_index':1,'candidate_index':0},
           'final_grid_sha256':care_grid_sha256(child),'eligible':True,'parent_occurrence':{'kind':'generation_breeder','generation_index':0,'candidate_index':0}}}]}]}
        evidence={'status':'available','founder_occurrences':[
          {'ordinal':0,'grid_id':'same_id','admitted':True,'source_kind':'era_breeder'},
          {'ordinal':1,'grid_id':'same_id','admitted':True,'source_kind':'keeper_companion'}]}
        lines='\n'.join(descendant_lines(evidence,report,{'grid_id':child['grid_id'],'grid':child}))
        self.assertIn('occurrence 0',lines);self.assertIn('2 recorded evaluation parent',lines)
        self.assertNotIn('ambiguous',lines)
    def test_new_extinct_campaign_requires_explicit_successor_action(self):
        campaign=Mock(population_policy='generation_survivors_v1',status='extinct')
        campaign.successor.side_effect=AssertionError('Automatic successor invoked without explicit action')
        with patch.object(self.bench,'ensure',return_value=campaign),patch.object(self.bench,'check_current_state'):
            with self.assertRaisesRegex(ValueError,'successor'):
                self.bench.run_era(self.bench.ledger_path)
        campaign.successor.assert_not_called();campaign.advance_era.assert_not_called()

if __name__=='__main__':unittest.main()
