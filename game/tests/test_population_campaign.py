"""X8 registered operational controls; these are not survival qualification."""
import copy
from contextlib import closing
import json
from pathlib import Path
import sqlite3
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
for folder in ('game/src', 'packages/mecha_engine/src'):
    sys.path.insert(0, str(ROOT/folder))
from mecha_game import campaign as api
from mecha_game import execution
from mecha_game.era_plan import EraPlan, state_digest

POLICY = 'generation_survivors_v1'


class PopulationCampaignTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.inputs = api.load_campaign_inputs(**api.default_campaign_paths(ROOT), seed_limit=4, repair_epochs=1)
        cls.config = dict(generations=1, population=2, damage_cycles=1, ticks=3, dropout_rate=0.2)

    def campaign(self, policy=POLICY):
        return api.KeeperCampaign(copy.deepcopy(self.inputs), campaign_id='x8-operational',
                                  era_config=self.config, population_policy=policy)

    def effective(self, **settings):
        return dict(**copy.deepcopy(self.inputs), founder_grids=[], cubff_pressure_source=None,
                    readability_selection={**self.inputs['legibility_model'], 'blend': 0.7},
                    rng_seed=20260707, effective_config=self.config, **settings)

    def test_legacy_capture_shape_is_unchanged(self):
        omitted = execution.capture_execution('control', 0, self.effective(), [])
        explicit = execution.capture_execution('control', 0, self.effective(population_policy='legacy_archive',
                founder_start_mode=None, survival_regime='sheltered', cubff_density_pressure=False), [])
        self.assertEqual(omitted, explicit)
        self.assertEqual('mechagotchi_era_execution_v1', omitted['manifest']['format'])
        self.assertNotIn('population_inputs_sha256', omitted['manifest']['inputs'])

    def test_capture_all_extended_inputs_and_empty_list_exactly(self):
        for settings in (
                dict(population_policy=POLICY, founder_start_mode='continue', survival_regime='stress_probe', cubff_density_pressure=True),
                dict(population_policy='legacy_archive', founder_start_mode=None, survival_regime='stress_probe', cubff_density_pressure=False),
                dict(population_policy='legacy_archive', founder_start_mode='bootstrap', survival_regime='sheltered', cubff_density_pressure=False)):
            with self.subTest(settings=settings):
                bundle = execution.capture_execution('control', 0, self.effective(**settings), [])
                self.assertEqual('mechagotchi_era_execution_v2', bundle['manifest']['format'])
                options = execution.blob_json(bundle, bundle['manifest']['inputs']['population_inputs_sha256'])
                self.assertEqual({'format': 'survival_population_inputs_v1', **settings}, options)
                decoded = execution.decode_execution_inputs(json.loads(json.dumps(bundle, sort_keys=True)))
                self.assertEqual([], decoded['founder_grids'])
                self.assertEqual(settings, execution.population_arguments(bundle))
                self.assertEqual(settings, {key: decoded[key] for key in settings})

    def test_capture_rejects_ambiguous_or_invalid_population_settings(self):
        for settings in (dict(population_policy=POLICY), dict(population_policy='legacy_archive', founder_start_mode='continue'),
                         dict(population_policy='invented'), dict(survival_regime='tiny'), dict(cubff_density_pressure=1)):
            with self.subTest(settings=settings), self.assertRaises(ValueError):
                execution.capture_execution('control', 0, self.effective(**settings), [])

    def test_new_mode_state_has_explicit_bootstrap_and_legacy_stays_v1(self):
        campaign = self.campaign()
        state = campaign.state_payload()
        self.assertEqual('keeper_campaign_state_v2', state['state_format'])
        self.assertEqual(POLICY, state['population_policy'])
        self.assertEqual(dict(founder_start_mode='bootstrap', era_index=None, ordered_breeders_sha256=None), state['population_continuation'])
        api.KeeperCampaign.validate_state_payload(state)
        self.assertEqual('keeper_campaign_state_v1', self.campaign('legacy_archive').state_payload()['state_format'])
        with self.assertRaises(AttributeError): campaign.population_policy = 'legacy_archive'

    def test_new_state_never_guesses_missing_mode_or_output_identity(self):
        state = self.campaign().state_payload()
        for key in ('population_policy', 'population_continuation'):
            bad = copy.deepcopy(state); bad.pop(key)
            with self.subTest(key=key), self.assertRaises(ValueError): api.KeeperCampaign.validate_state_payload(bad)
        state['era_count'] = 1
        with self.assertRaises(ValueError): api.KeeperCampaign.validate_state_payload(state)

    def test_plan_v4_preserves_preparation_through_staging_and_restart(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp)/'era_plan.json'; plan = EraPlan(path)
            self.assertEqual('sheltered', plan.survival_regime)
            self.assertFalse(plan.cubff_density_pressure)
            plan.select_survival_regime('stress_probe'); plan.select_density_pressure(True)
            plan.stage([self.inputs['seed_grids'][0]]); plan.unstage_all(); plan.select_weather('storm')
            reopened = EraPlan(path)
            self.assertIsNone(reopened.error)
            self.assertEqual('mechagotchi_era_plan_v4', reopened.document['format'])
            self.assertEqual('stress_probe', reopened.survival_regime)
            self.assertTrue(reopened.cubff_density_pressure)
            before = path.read_bytes()
            for call in (lambda: reopened.select_survival_regime('tiny'), lambda: reopened.select_density_pressure(1)):
                with self.assertRaises(ValueError): call()
                self.assertEqual(before, path.read_bytes())

    def test_density_denial_precedes_capture_and_mutation(self):
        campaign = self.campaign(); before = copy.deepcopy(campaign.state_payload())
        with patch.object(campaign, 'budget', return_value={'cubff_density_pressure_allowed': False}), \
             patch.object(execution, 'capture_execution', side_effect=AssertionError('captured refused input')):
            with self.assertRaisesRegex(ValueError, 'density|Density'):
                campaign.advance_era('real', cubff_density_pressure=True)
        self.assertEqual(before, campaign.state_payload())
        with patch.object(campaign, 'budget', return_value={'cubff_density_pressure_allowed': True}), \
             patch.object(execution, 'capture_execution', side_effect=AssertionError('captured absent source')):
            with self.assertRaisesRegex(ValueError, 'density|Density'):
                campaign.advance_era('calm', cubff_density_pressure=True)
        self.assertEqual(before, campaign.state_payload())

    def test_population_end_uses_living_outcome_even_with_archive(self):
        from mecha_game.execution import population_ended
        report = dict(generations_requested=1, generations=[{}], living_population=dict(
            format=POLICY, population_policy=POLICY, final_breeders=[],
            termination=dict(ended=True, reason='no_eligible_breeders', generation_index=0,
                             lifecycle_deaths=1, structural_disqualifications=0, genuine_lifecycle_extinction=True)))
        self.assertTrue(population_ended(report, [{'historical': True}], POLICY))
        self.assertFalse(population_ended(dict(generations_requested=1, generations=[{}]), [{'historical': True}], 'legacy_archive'))
        report['living_population']['termination']['ended'] = False
        with self.assertRaises(ValueError): population_ended(report, [{'historical': True}], POLICY)

    def test_source_breeder_tail_rejects_omission_duplicate_and_changed_body(self):
        from mecha_game.execution import validate_breeder_continuation, breeder_sources
        grid = copy.deepcopy(self.inputs['seed_grids'][0])
        breeder = dict(generation_index=0,candidate_index=0,grid_id=grid['grid_id'],grid=grid,
                       grid_sha256=execution.result_digest(grid),fitness=1.0,learned_readability=None,
                       care_context=None,care_context_origin=None)
        report = dict(living_population=dict(final_breeders=[breeder]))
        sources = breeder_sources(report, 'keeper', 0)
        validate_breeder_continuation([grid], sources, [breeder], 'keeper', 1, 'continue')
        for genomes, rows in (([], []), ([grid,grid],sources+sources), ([{**grid,'grid_id':'changed'}],sources)):
            with self.subTest(genomes=genomes), self.assertRaises(ValueError):
                validate_breeder_continuation(genomes, rows, [breeder], 'keeper', 1, 'continue')
        validate_breeder_continuation([], [], [], 'keeper', 1, 'continue')
        with self.assertRaises(ValueError): validate_breeder_continuation([grid],sources, [],'keeper',0,'bootstrap')

    def test_successor_retains_policy_identity_and_facts_but_bootstraps(self):
        campaign = self.campaign(); campaign.campaign['status'] = 'extinct'
        facts = [dict(axis='storm_record',tier=1,earned_era_index=0,metric_path='derived.max_dropout_multiplier_survived',metric_value=1.2,threshold=1.1)]
        campaign.campaign['unlocks'] = copy.deepcopy(facts)
        child = campaign.successor()
        self.assertEqual(POLICY, child.population_policy)
        self.assertNotEqual(campaign.campaign['campaign_id'], child.campaign['campaign_id'])
        self.assertEqual(campaign.campaign['base_seed']+api.SUCCESSOR_SEED_OFFSET, child.campaign['base_seed'])
        self.assertEqual(facts, child.inherited_unlocks)
        self.assertEqual(campaign.base_profile, child.base_profile)
        self.assertEqual('bootstrap', child.state_payload()['population_continuation']['founder_start_mode'])

    def test_real_small_era_restart_reproduction_and_exact_continuation(self):
        from mecha_engine.storage import load_era_breeders
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); state=root/'campaign_state.json'; ledger=root/'campaign.sqlite3'
            campaign = self.campaign(); first = campaign.advance_era('calm')
            breeders = first['report']['living_population']['final_breeders']
            self.assertTrue(breeders, 'operational sheltered fixture has no continuation')
            self.assertEqual(POLICY, execution.population_arguments(first['execution'])['population_policy'])
            self.assertEqual('bootstrap', execution.population_arguments(first['execution'])['founder_start_mode'])
            campaign.save(ledger); campaign.save_state(state)
            with closing(sqlite3.connect(ledger)) as conn:
                self.assertEqual(breeders, load_era_breeders(conn,'x8-operational',0))
                self.assertEqual('matched', execution.reproduce_era(conn,'x8-operational',0)['status'])
            resumed = api.KeeperCampaign.load_state(copy.deepcopy(self.inputs),state,ledger)
            self.assertEqual(campaign.state_payload(), resumed.state_payload())
            continued = resumed.advance_era('calm'); uninterrupted = campaign.advance_era('calm')
            self.assertEqual(uninterrupted, continued)
            rows=continued['execution']['manifest']['founder_occurrences']
            self.assertEqual(len(breeders),len(rows))
            self.assertEqual(list(range(len(rows))),[row['source_position'] for row in rows])
            self.assertTrue(all(row['source_kind']=='era_breeder' for row in rows))
            self.assertEqual([],continued['founder_records'])
            resumed.save(ledger); resumed.save_state(state)
            self.assertEqual(resumed.state_payload(),api.KeeperCampaign.load_state(copy.deepcopy(self.inputs),state,ledger).state_payload())

    def test_completed_journal_preserves_mode_preparation_and_output(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); state=root/'campaign_state.json'; ledger=root/'campaign.sqlite3'
            campaign=self.campaign(); plan=EraPlan(root/'era_plan.json'); plan.select_survival_regime('sheltered')
            era=campaign.advance_era('calm'); plan.begin(campaign,era,None)
            recovered=EraPlan(plan.path); self.assertIsNone(recovered.error)
            recovered.finish(ledger,state)
            self.assertEqual('mechagotchi_era_plan_v4',recovered.document['format'])
            loaded=api.KeeperCampaign.load_state(copy.deepcopy(self.inputs),state,ledger)
            self.assertEqual(campaign.state_payload(),loaded.state_payload())
            self.assertIsNone(recovered.pending)
            self.assertEqual('continue',loaded.state_payload()['population_continuation']['founder_start_mode'])

    def test_changed_or_missing_breeder_authority_refuses_without_writes(self):
        for fault in ('state_digest', 'legacy_relabel', 'missing_blob', 'corrupt_blob'):
            with self.subTest(fault=fault), tempfile.TemporaryDirectory() as tmp:
                root=Path(tmp); state=root/'campaign_state.json'; ledger=root/'campaign.sqlite3'
                campaign=self.campaign(); era=campaign.advance_era('calm'); campaign.save(ledger); campaign.save_state(state)
                digest=era['execution']['manifest']['ordered_breeders_sha256']
                if fault in ('state_digest','legacy_relabel'):
                    value=json.loads(state.read_bytes())
                    if fault=='state_digest': value['population_continuation']['ordered_breeders_sha256']='0'*64
                    else:
                        value['state_format']='keeper_campaign_state_v1'
                        value.pop('population_policy'); value.pop('population_continuation')
                    state.write_text(json.dumps(value))
                else:
                    with closing(sqlite3.connect(ledger)) as conn, conn:
                        if fault=='missing_blob': conn.execute('DELETE FROM execution_blobs WHERE sha256=?',(digest,))
                        else: conn.execute('UPDATE execution_blobs SET payload=? WHERE sha256=?',(b'[]',digest))
                before={p.name:p.read_bytes() for p in root.iterdir() if p.is_file()}
                with self.assertRaises(ValueError): api.KeeperCampaign.load_state(copy.deepcopy(self.inputs),state,ledger)
                self.assertEqual(before,{p.name:p.read_bytes() for p in root.iterdir() if p.is_file()})

    def test_interrupted_v4_completion_finishes_once_without_resimulation(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); state=root/'campaign_state.json'; ledger=root/'campaign.sqlite3'
            campaign=self.campaign(); first=campaign.advance_era('calm'); campaign.save(ledger); campaign.save_state(state)
            plan=EraPlan(root/'era_plan.json'); plan.select_survival_regime('sheltered')
            era=campaign.advance_era('calm'); plan.begin(campaign,era,state_digest(state))
            with patch('mecha_game.era_plan.save_campaign_checkpoint',side_effect=PermissionError('checkpoint locked')):
                with self.assertRaises(PermissionError): plan.finish(ledger,state)
            self.assertIsNotNone(EraPlan(plan.path).pending)
            with patch.object(api,'evolve',side_effect=AssertionError('resimulation')):
                recovered=EraPlan(plan.path); recovered.finish(ledger,state)
            self.assertIsNone(recovered.pending)
            self.assertEqual(campaign.state_payload(),api.KeeperCampaign.load_state(copy.deepcopy(self.inputs),state,ledger).state_payload())
            with closing(sqlite3.connect(ledger)) as conn:
                self.assertEqual(2,conn.execute('SELECT count(*) FROM eras').fetchone()[0])
                self.assertEqual(sum(len(x['elites']) for x in campaign.eras),conn.execute('SELECT count(*) FROM elites').fetchone()[0])

    def test_duplicate_release_ids_stay_occurrence_bound_and_projection_truthful(self):
        valid=copy.deepcopy(self.inputs['seed_grids'][0]); refused=copy.deepcopy(valid)
        refused['cells'][0]['mutation_weight']=-1
        campaign=self.campaign()
        era=campaign.advance_era('calm',released_grids=[valid,refused])
        occurrences=era['execution']['manifest']['founder_occurrences']
        self.assertEqual([True,False],[row['admitted'] for row in occurrences])
        self.assertNotEqual(occurrences[0]['grid_sha256'],occurrences[1]['grid_sha256'])
        self.assertEqual([],era['founder_records'])
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); campaign.save(root/'campaign.sqlite3'); campaign.save_state(root/'campaign_state.json')
            api.KeeperCampaign.load_state(copy.deepcopy(self.inputs),root/'campaign_state.json',root/'campaign.sqlite3')

    def test_ended_campaign_refuses_release_before_capture(self):
        campaign=self.campaign(); campaign.campaign['status']='extinct'
        before=copy.deepcopy(campaign.state_payload())
        with patch.object(execution,'capture_execution',side_effect=AssertionError('resurrection')):
            with self.assertRaisesRegex(ValueError,'ended bloodline'):
                campaign.advance_era('calm',released_grids=[self.inputs['seed_grids'][0]])
        self.assertEqual(before,campaign.state_payload())

    def test_zero_era_initialization_is_versioned_and_recoverable(self):
        from mecha_game.campaign_recovery import initialize_campaign_checkpoint, inspect_campaign_backup
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); state=root/'campaign_state.json'; ledger=root/'campaign.sqlite3'
            campaign=self.campaign(); initialize_campaign_checkpoint(campaign,state,ledger)
            preview=inspect_campaign_backup(state,ledger)
            self.assertEqual(campaign.state_payload(),preview['state'])
            restored=api.KeeperCampaign.load_state(copy.deepcopy(self.inputs),state,ledger)
            self.assertEqual(POLICY,restored.population_policy)
            self.assertEqual([],restored.resume_breeders)
            self.assertEqual('bootstrap',restored.state_payload()['population_continuation']['founder_start_mode'])

    def test_legacy_extended_inputs_save_and_reproduce_without_mode_migration(self):
        for regime,density in (('stress_probe',False),('sheltered',True)):
            with self.subTest(regime=regime,density=density), tempfile.TemporaryDirectory() as tmp:
                root=Path(tmp); state=root/'campaign_state.json'; ledger=root/'campaign.sqlite3'
                campaign=self.campaign('legacy_archive')
                # A guard-only fixture, not evidence of play-earned progression.
                with patch.object(campaign,'budget',return_value={'cubff_density_pressure_allowed':True}):
                    era=campaign.advance_era('storm',survival_regime=regime,cubff_density_pressure=density)
                self.assertNotIn('living_population',era['report'])
                self.assertNotIn('ordered_breeders_sha256',era['execution']['manifest'])
                self.assertEqual('mechagotchi_era_execution_v2',era['execution']['manifest']['format'])
                self.assertEqual(regime,era['report'].get('survival_regime','sheltered'))
                self.assertEqual(density,era['report']['cubff_pressure'].get('density_pressure',False))
                campaign.save(ledger); campaign.save_state(state)
                self.assertEqual('keeper_campaign_state_v1',json.loads(state.read_bytes())['state_format'])
                self.assertEqual('legacy_archive',api.KeeperCampaign.load_state(copy.deepcopy(self.inputs),state,ledger).population_policy)
                with closing(sqlite3.connect(ledger)) as conn:
                    self.assertEqual('matched',execution.reproduce_era(conn,'x8-operational',0)['status'])

    def test_injected_terminal_observation_empty_output_journal_and_successor(self):
        # Persistence control only: an injected final endpoint is not scientific
        # extinction evidence. The attempted real stress fixture survived and its
        # false test assumption is retained in campaign/green-03.log.
        import importlib
        from mecha_engine.storage import load_era_breeders
        population_api=importlib.import_module('mecha_engine.runtime._survival_population')
        actual_episode=population_api.run_episode
        def dead_endpoint(*args,**kwargs):
            episode=actual_episode(*args,**kwargs)
            episode['alive']=False; episode['death_cause']='STARVATION'
            return episode
        actual_evolve=api.evolve
        def injected_ending(*args,**kwargs):
            # Capture genuine source identity first; inject only the operational
            # observation. Reproduction below must honestly detect the mismatch.
            with patch.object(population_api,'run_episode',side_effect=dead_endpoint):
                return actual_evolve(*args,**kwargs)
        campaign=self.campaign()
        with patch.object(api,'evolve',side_effect=injected_ending):
            era=campaign.advance_era('calm')
        population=era['report']['living_population']
        self.assertTrue(population['termination']['ended'])
        self.assertTrue(population['termination']['genuine_lifecycle_extinction'])
        self.assertEqual([],population['final_breeders'])
        self.assertTrue(era['elites'])
        self.assertEqual('extinct',campaign.status)
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); state=root/'campaign_state.json'; ledger=root/'campaign.sqlite3'
            plan=EraPlan(root/'era_plan.json')
            plan.begin(campaign,era,None); EraPlan(plan.path).finish(ledger,state)
            restored=api.KeeperCampaign.load_state(copy.deepcopy(self.inputs),state,ledger)
            self.assertEqual('extinct',restored.status)
            self.assertEqual([],restored.resume_breeders)
            self.assertEqual(campaign.state_payload(),restored.state_payload())
            with closing(sqlite3.connect(ledger)) as conn:
                self.assertEqual([],load_era_breeders(conn,'x8-operational',0))
                self.assertEqual(len(era['elites']),conn.execute('SELECT count(*) FROM elites').fetchone()[0])
                self.assertEqual('mismatch',execution.reproduce_era(conn,'x8-operational',0)['status'])
            child=restored.successor()
            self.assertEqual('bootstrap',child.state_payload()['population_continuation']['founder_start_mode'])
            self.assertEqual(POLICY,child.population_policy)
            child_era=child.advance_era('calm')
            self.assertEqual('bootstrap',execution.population_arguments(child_era['execution'])['founder_start_mode'])
            self.assertEqual([],execution.decode_execution_inputs(child_era['execution'])['founder_grids'])
            child_plan=EraPlan(plan.path); child_plan.begin(child,child_era,state_digest(state)); child_plan.finish(ledger,state)
            self.assertEqual(child.state_payload(),api.KeeperCampaign.load_state(copy.deepcopy(self.inputs),state,ledger).state_payload())
            with closing(sqlite3.connect(ledger)) as conn:
                self.assertEqual(2,conn.execute('SELECT count(*) FROM campaigns').fetchone()[0])
                self.assertEqual(len(era['elites']),conn.execute('SELECT count(*) FROM elites WHERE campaign_id=?',('x8-operational',)).fetchone()[0])

    def test_cared_duplicate_founders_keep_exact_origins_through_breeder_restart(self):
        from mecha_game.session import CompanionSession
        from mecha_game.contribute import companion_release_source
        lives=[CompanionSession(copy.deepcopy(self.inputs['seed_grids'][0]),self.inputs['slip_profile'],
                                model=self.inputs['generation_model']) for _ in range(2)]
        lives[0].advance('feed'); lives[1].advance('sleep')
        sources=[companion_release_source(life) for life in lives]
        campaign=self.campaign()
        era=campaign.advance_era('calm',released_grids=[life.grid for life in lives],released_sources=sources)
        breeders=era['report']['living_population']['final_breeders']
        self.assertEqual({0,1},{row['care_context_origin']['founder_submission_index'] for row in breeders})
        for row in breeders:
            self.assertEqual(sources[row['care_context_origin']['founder_submission_index']]['care_context'],row['care_context'])
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); state=root/'campaign_state.json'; ledger=root/'campaign.sqlite3'
            campaign.save(ledger); campaign.save_state(state)
            restored=api.KeeperCampaign.load_state(copy.deepcopy(self.inputs),state,ledger)
            resumed=restored.advance_era('calm'); direct=campaign.advance_era('calm')
            self.assertEqual(direct,resumed)
            restored.save(ledger); restored.save_state(state)
            with closing(sqlite3.connect(ledger)) as conn:
                self.assertEqual('matched',execution.reproduce_era(conn,'x8-operational',1)['status'])


if __name__ == '__main__': unittest.main()
