"""Mock/pure X8 native instrument controls; no model training or simulation."""
import base64
import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import Mock, patch

SPEC=importlib.util.spec_from_file_location('native_survival',Path(__file__).with_name('verify_survival_population.py'))
native=importlib.util.module_from_spec(SPEC);SPEC.loader.exec_module(native)


class NativeSurvivalInstrumentTests(unittest.TestCase):
    def judgment(self):
        return dict(cohort_verdict='ADOPT',checks={'fixed':True},genuine_extinct_seeds=[20260704,20260701],
                    lowest_extinct_seed=20260701,counts=[dict(seed=20260701,arm='D',termination={'genuine_lifecycle_extinction':True})])

    def inputs(self):
        seeds=[{'grid_id':str(i)} for i in range(50)]
        return dict(format='surviving_population_inputs_v1',seed_grids=seeds,
            training_options=dict(repair_training_count=40,**native.TRAINING),legibility_model={'weights':{}},
            readability_selection={'weights':{},'blend':.7},weather_sources={'storm':[{}]*6},repair_model={'weights':[.5]},
            input_sources=[dict(role='seed_corpus',source_position=i,data_base64=base64.b64encode(json.dumps(g).encode()).decode()) for i,g in enumerate(seeds)])

    def before(self,**changes):
        state=dict(campaign_id='parent',base_seed=20260701,era_count=1,status='extinct',population_policy=native.POLICY,
                   era_config=native.CONFIG,unlocks=[],inherited_unlocks=[],predecessor_campaign_id=None)
        state.update(changes)
        return dict(state=state,files={'campaign_state.json':'sha'})

    def previous(self,home,action='direct-era'):
        return dict(format=native.FORMAT,status='completed',action=action,selected_seed=20260701,save_home=str(home.resolve()),after=self.before())

    def test_only_lowest_registered_qualified_extinction_is_selectable(self):
        self.assertEqual(20260701,native.select_qualified_seed(self.judgment()))
        for changes in ({'cohort_verdict':'REFUSE'},{'checks':{'fixed':False}},{'genuine_extinct_seeds':[]},
                        {'lowest_extinct_seed':20260704},{'genuine_extinct_seeds':[999]}):
            value={**self.judgment(),**changes}
            with self.subTest(changes=changes),self.assertRaises(ValueError):native.select_qualified_seed(value)

    def test_cache_uses_frozen_bytes_and_original_material_without_training(self):
        inputs=self.inputs();before=copy.deepcopy(inputs)
        name,envelope=native.cache_envelope(inputs,{'available':True,'version':'frozen'})
        self.assertTrue(name.startswith('repair_model_v2_'))
        self.assertEqual(native.TRAINING,envelope['key_material']['trainer_options'])
        self.assertEqual(40,len(envelope['key_material']['source_identities']))
        raw=base64.b64decode(envelope['model_data_base64'])
        self.assertEqual(inputs['repair_model'],json.loads(raw))
        self.assertEqual(native.digest(raw),envelope['model_sha256'])
        self.assertEqual(before,inputs)

    def test_frozen_options_do_not_accept_tiny_or_retrained_cohort(self):
        for change in ('seed_count','epochs','blend','weather'):
            inputs=self.inputs()
            if change=='seed_count':inputs['seed_grids'].pop()
            elif change=='epochs':inputs['training_options']['epochs']=6
            elif change=='blend':inputs['readability_selection']['blend']=.8
            else:inputs['weather_sources']['storm'].pop()
            with self.subTest(change=change),self.assertRaises(ValueError):native.validate_frozen_inputs(inputs)

    def test_each_cli_stage_runs_at_most_one_era(self):
        with tempfile.TemporaryDirectory() as tmp:
            home=Path(tmp)/'home';out=Path(tmp)/'out'
            for action in native.ACTIONS:
                args=native.launch_arguments(action,home,out,20260701,self.before(),source=False)
                if '--eras' in args:self.assertEqual('1',args[args.index('--eras')+1])
                self.assertNotIn('tiny',args)
                self.assertNotIn('--auto-succeed',args)
                self.assertNotIn('--ticks',args)

    def test_source_actions_use_visible_key_seam_not_headless_era(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            for action in (*native.ERA_ACTIONS,'create-successor'):
                args=native.launch_arguments(action,root/'home',root/'out',20260701,self.before(),source=True)
                self.assertNotIn('--eras',args)
                self.assertNotIn('--create-successor',args)

    def test_fallback_requires_actual_empty_facts_and_separate_home(self):
        with tempfile.TemporaryDirectory() as tmp:
            home=Path(tmp)/'fallback';direct=self.previous(Path(tmp)/'direct')
            empty=dict(state=None,files={})
            native.validate_stage('fallback-sheltered-era',empty,20260701,direct=direct,home=home)
            for invalid in (None,{**direct,'selected_seed':20260702},{**direct,'save_home':str(home.resolve())},
                            {**direct,'after':self.before(unlocks=[{'earned':True}])}):
                with self.subTest(invalid=invalid),self.assertRaises(ValueError):
                    native.validate_stage('fallback-sheltered-era',empty,20260701,direct=invalid,home=home)

    def test_second_fallback_era_refuses_grind_or_reordered_stage(self):
        with tempfile.TemporaryDirectory() as tmp:
            home=Path(tmp);before=self.before(status='active');prior=self.previous(home,'fallback-sheltered-era');prior['after']=before
            native.validate_stage('fallback-stress-era',before,20260701,previous=prior,home=home)
            for era in (0,2):
                changed=self.before(status='active',era_count=era)
                with self.assertRaises(ValueError):native.validate_stage('fallback-stress-era',changed,20260701,previous=prior,home=home)

    def test_pending_finish_cannot_accidentally_launch_a_fresh_era(self):
        with tempfile.TemporaryDirectory() as tmp:
            home=Path(tmp);before=self.before();prior=self.previous(home)
            with self.assertRaisesRegex(ValueError,'No completed journal'):
                native.validate_stage('finish-pending',before,20260701,previous=prior,home=home)

    def test_prior_receipt_reuse_requires_completed_checksum_bound_outputs(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);native.write(root/'result.json',{'actual':True})
            native.write(root/'terminal.json',{'status':'completed','checks':{'ok':True},'outputs':{'result.json':native.file_digest(root/'result.json')}})
            native.verified_receipt(root)
            (root/'result.json').write_text('{}')
            with self.assertRaises(ValueError):native.verified_receipt(root)

    def test_child_watchdog_reserves_cleanup_and_kills_on_timeout(self):
        child=Mock();child.wait.side_effect=[subprocess.TimeoutExpired('child',110),0];child.poll.return_value=None
        with tempfile.TemporaryDirectory() as tmp,patch.object(native.subprocess,'Popen',return_value=child):
            with self.assertRaises(subprocess.TimeoutExpired):native.supervise(['child'],Path(tmp),{},120)
        self.assertEqual(110,child.wait.call_args_list[0].kwargs['timeout'])
        child.kill.assert_called_once()

    def test_child_cleanup_also_runs_on_interruption(self):
        child=Mock();child.wait.side_effect=[KeyboardInterrupt(),0];child.poll.return_value=None
        with tempfile.TemporaryDirectory() as tmp,patch.object(native.subprocess,'Popen',return_value=child):
            with self.assertRaises(KeyboardInterrupt):native.supervise(['child'],Path(tmp),{},120)
        child.kill.assert_called_once()

    def test_no_child_starts_without_cleanup_reservation(self):
        with tempfile.TemporaryDirectory() as tmp,patch.object(native.subprocess,'Popen') as process:
            with self.assertRaises(TimeoutError):native.supervise(['child'],Path(tmp),{},10)
        process.assert_not_called()

    def test_cleanup_failure_holds_wrapper_until_outer_tree_cleanup(self):
        for failure in ('kill','wait'):
            child=Mock();child.pid=42;child.poll.return_value=None
            child.wait.side_effect=[subprocess.TimeoutExpired('child',110),OSError('cannot reap')]
            if failure=='kill':child.kill.side_effect=OSError('cannot kill')
            with self.subTest(failure=failure),tempfile.TemporaryDirectory() as tmp, \
                    patch.object(native.subprocess,'Popen',return_value=child), \
                    patch.object(native,'hold_for_outer_cleanup',create=True) as hold:
                with self.assertRaises(subprocess.TimeoutExpired):native.supervise(['child'],Path(tmp),{},120)
                hold.assert_called_once()

    def test_each_effective_action_binds_seed_regime_start_blend_and_care(self):
        for action in native.ERA_ACTIONS:
            before=self.before(era_count=1 if action=='fallback-stress-era' else 0,
                inherited_unlocks=[{'axis':'legibility','tier':1}] if action=='successor-era' else [])
            fresh=action in ('direct-era','fallback-sheltered-era')
            if fresh:before={'state':None}
            seed=20260701+(1_000_000 if action=='fallback-stress-era' else 50_000_000 if action=='successor-era' else 0)
            value=dict(rng_seed=seed,population_policy=native.POLICY,
                founder_start_mode='continue' if action=='fallback-stress-era' else 'bootstrap',
                survival_regime='stress_probe' if action in ('direct-era','fallback-stress-era') else 'sheltered',
                cubff_density_pressure=False,founder_grids=[{'prior':'breeder'}] if action=='fallback-stress-era' else [],
                readability_selection={'weights':{},'blend':.75 if action=='successor-era' else .7})
            inputs=self.inputs()
            self.assertTrue(all(native.effective_action_checks(value,action,20260701,before,inputs).values()))
            for key,replacement in [('rng_seed',999),('population_policy','archive_legacy'),
                    ('founder_start_mode','wrong'),('survival_regime','wrong'),('cubff_density_pressure',True),
                    ('readability_selection',{'blend':.2}),('care_selection_policy','observed_care_selection_v2'),
                    ('care_evaluator','archive_morphology_probe_v1'),('founder_care_contexts',[{'care':True}])]:
                bad={**value,key:replacement}
                with self.subTest(action=action,key=key):
                    self.assertFalse(all(native.effective_action_checks(bad,action,20260701,before,inputs).values()))
            if action!='fallback-stress-era':
                self.assertFalse(all(native.effective_action_checks({**value,'founder_grids':None},action,20260701,before,inputs).values()))

    def test_unconfirmed_cleanup_receipt_survives_until_positive_reap(self):
        child=Mock();child.pid=42
        child.wait.side_effect=[OSError('reap unavailable'),KeyboardInterrupt(),0]
        with tempfile.TemporaryDirectory() as tmp,patch.object(native.time,'sleep') as pause:
            root=Path(tmp);native.hold_for_outer_cleanup(child,root,OSError('kill denied'))
            self.assertEqual(42,native.read(root/'cleanup-unconfirmed.json')['child_pid'])
        self.assertEqual(3,child.wait.call_count)
        self.assertEqual(2,pause.call_count)


if __name__=='__main__':unittest.main()
