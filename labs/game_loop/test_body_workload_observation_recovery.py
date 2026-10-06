"""Synthetic observation/receipt checks; no held-out era or lifecycle replay."""
from copy import deepcopy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import body_workload_observation_recovery as recovery


def synthetic(active=True):
    recovery.imports()
    from body_workload_fixtures import causal_fixture
    from mecha_engine.lifecycle import initial_state
    from mecha_engine.runtime._survival_live import _episode_digest, evaluation_grid
    from mecha_engine.runtime.care import care_grid_sha256
    fixture = causal_fixture(); grid = fixture['grid']; slip = fixture['covenant']
    evaluated, _ = evaluation_grid(grid, 'stress_probe')
    state = dict(hunger=.2, energy=.5, stress=.1, bond=.8, grid_stability=.9)
    history = [dict(tick=1, action='play', balance=.8, alive=True, death_cause=None, state=state)]
    episode = dict(survival_ticks=1, alive=True, death_cause=None, need_balance=.8,
                   history=history, final_state=deepcopy(state))
    if active:
        projection = initial_state(evaluated, slip, body_response='workload-v1')['body_workload']
        episode.update(body_response='workload-v1', body_workload=projection)
        history[0].update(body_response='workload-v1', play_energy_cost=projection['play_energy_cost'],
                          action_energy_effect=-projection['play_energy_cost'])
    digest = _episode_digest(episode, 1, evaluated_grid=evaluated)
    cycle = dict(cycle=1, removed_cell_count=0, episode=deepcopy(digest))
    creature = dict(candidate_grid_id=grid['grid_id'], parent_grid_id=grid['grid_id'], cycles=[deepcopy(cycle)],
        breeding=dict(candidate_grid_sha256=care_grid_sha256(grid), final_grid_sha256=care_grid_sha256(grid),
                      final_episode=deepcopy(digest)))
    cycle.update(damage_seed=71, frames=dict(removed_cells=[], repaired_grid=deepcopy(grid), episode_history=deepcopy(history)))
    row = dict(generation_index=0, candidate_index=0, creature=deepcopy(creature), run_seed=7,
               candidate_grid=deepcopy(grid), parent_grid=deepcopy(grid), final_grid=deepcopy(grid),
               cycles=[cycle], final_episode=episode)
    report = dict(rng_seed=7, ticks=1, survival_regime='stress_probe', generations=[dict(generation=0, creatures=[creature])])
    if active: report['body_response']='workload-v1'
    return dict(report=report, evaluations=[row]), slip


def retained_tree(root):
    """Tiny synthetic failed receipt tree; never reads the recorded production era."""
    out=root/recovery.ORIGINAL_OUTPUT; control=root/recovery.ORIGINAL_CONTROL
    for path in (root/recovery.ATTEMPT/'source-manifest.json',root/recovery.ATTEMPT/'budget.json',
                 root/recovery.ATTEMPT/'study/setup/output/inputs.json',root/recovery.ATTEMPT/'prerequisites.json'):
        recovery.write(path,{'synthetic':True})
    common=dict(source_manifest_sha256=recovery.OLD_SOURCE_SHA,inputs_sha256=recovery.OLD_INPUT_SHA)
    start={**common,'spec':dict(stage='production',index=1,seconds=120),
           'prerequisites_sha256':recovery.OLD_PREREQUISITE_SHA}
    recovery.write(out/'started.json',start)
    recovery.write(out/'result.json',dict(era_index=1,rng_seed=20261130,body_response='workload-v1',
        checks=dict(input_immutable=True,observations_bound=False,body_response_bound=True)))
    recovery.write(out/'failure.json',{'error':'synthetic original failure'})
    recovery.write(out/'save/campaign.sqlite3',{'synthetic_saved_bytes':True})
    outputs={p.relative_to(out).as_posix():recovery.file_digest(p) for p in out.rglob('*')
             if p.is_file() and p.name!='started.json'}
    terminal={**start,'status':'error','error':{'message':'production input or observation integrity failed'},
              'started_sha256':recovery.file_digest(out/'started.json'),'elapsed_seconds':1,'outputs':outputs}
    recovery.write(out/'terminal.json',terminal)
    request={'synthetic_request':True};control_start={**common,'request':request}
    recovery.write(control/'started.json',control_start)
    recovery.write(control/'stdout.log',{'synthetic':'log'})
    control_outputs={'worker/'+p.relative_to(out).as_posix():recovery.file_digest(p) for p in out.rglob('*') if p.is_file()}
    control_outputs['parent/stdout.log']=recovery.file_digest(control/'stdout.log')
    recovery.write(control/'terminal.json',{**common,'request':request,'status':'error','cleanup_confirmed':True,
        'returncode':1,'elapsed_seconds':2,'started_sha256':recovery.file_digest(control/'started.json'),'outputs':control_outputs})
    return {name:recovery.file_digest(root/name) for name in recovery.PINNED_FILES}


class ObservationRecoveryTests(unittest.TestCase):
    def test_active_body_binding_passes_without_replay(self):
        result, slip = synthetic()
        from survival_population_gate import observations_bound as old
        self.assertFalse(old(result))
        with patch('mecha_engine.lifecycle.run_episode', side_effect=AssertionError('no replay')), \
                patch('mecha_engine.runtime.evolve', side_effect=AssertionError('no evolution')):
            self.assertTrue(recovery.observations_bound(result, slip))

    def test_legacy_parity_retains_original_predicates(self):
        result, slip = synthetic(False)
        from survival_population_gate import observations_bound as old
        self.assertTrue(old(result))
        self.assertTrue(recovery.observations_bound(result, slip))
        for target in ('run_seed', 'candidate_index'):
            forged = deepcopy(result); forged['evaluations'][0][target] += 1
            self.assertEqual(recovery.observations_bound(forged, slip), old(forged))
            self.assertFalse(old(forged))

    def test_changed_evaluated_body_refuses_even_with_duplicate_report_forged(self):
        result, slip = synthetic(); row=result['evaluations'][0]
        row['creature']['breeding']['final_episode']['evaluated_grid']['grid_id']='forged'
        result['report']['generations'][0]['creatures'][0]=deepcopy(row['creature'])
        self.assertFalse(recovery.observations_bound(result, slip))

    def test_changed_final_body_refuses_even_with_updated_hash(self):
        result, slip = synthetic(); row=result['evaluations'][0]
        from mecha_engine.runtime.care import care_grid_sha256
        row['final_grid']['grid_id']='forged'
        row['creature']['breeding']['final_grid_sha256']=care_grid_sha256(row['final_grid'])
        result['report']['generations'][0]['creatures'][0]=deepcopy(row['creature'])
        self.assertFalse(recovery.observations_bound(result, slip))

    def test_changed_cycle_body_refuses(self):
        result, slip=synthetic()
        result['evaluations'][0]['cycles'][0]['frames']['repaired_grid']['grid_id']='forged'
        self.assertFalse(recovery.observations_bound(result, slip))

    def test_forged_projection_and_cost_refuse(self):
        for location in ('body_workload', 'history_cost', 'history_effect', 'model'):
            result, slip=synthetic(); episode=result['evaluations'][0]['final_episode']
            if location=='body_workload': episode['body_workload']['functional_capacity']+=1
            elif location=='history_cost': episode['history'][0]['play_energy_cost']+=.01
            elif location=='history_effect': episode['history'][0]['action_energy_effect']=0
            else: episode['body_response']='future-v99'
            with self.subTest(location=location): self.assertFalse(recovery.observations_bound(result, slip))

    def test_nonplay_applied_cost_is_checked(self):
        result, slip=synthetic(); row=result['evaluations'][0]['final_episode']['history'][0]
        row.update(action='sleep', action_energy_effect=0)
        self.assertFalse(recovery.observations_bound(result, slip))

    def test_malformed_observation_refuses(self):
        result, slip=synthetic(); del result['evaluations'][0]['cycles'][0]['frames']
        self.assertFalse(recovery.observations_bound(result, slip))

    def test_recovery_attestation_hash_and_payload_must_match(self):
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'recovery.json'; payload={'source_manifest_sha256':'a'*64,'source_manifest':'source.json'}
            recovery.write(path,payload)
            with patch.object(recovery,'_build_attestation',return_value=(payload,{'retained':True})):
                self.assertEqual(recovery.validate_recovery(path,recovery.file_digest(path),'a'*64),{'retained':True})
                with self.assertRaises(ValueError):recovery.validate_recovery(path,'b'*64,'a'*64)
                with self.assertRaises(ValueError):recovery.validate_recovery(path,recovery.file_digest(path),'b'*64)
                payload['changed']=True
                with self.assertRaises(ValueError):recovery.validate_recovery(path,recovery.file_digest(path),'a'*64)

    def test_old_runtime_source_change_refuses(self):
        self.assertEqual(recovery.ALLOWED_ORIGINAL_INSTRUMENT_CHANGES,{
            'labs/game_loop/body_workload_coordinator.py','labs/game_loop/test_body_workload_coordinator.py',
            'labs/game_loop/verify_body_workload_delivery.py','labs/game_loop/test_verify_body_workload_delivery.py'})
        old={'files':{'game/src/mecha_game/session.py':'a'*64,
                     **{name:'b'*64 for name in recovery.ALLOWED_ORIGINAL_INSTRUMENT_CHANGES}}}
        current=deepcopy(old)
        for name in recovery.ALLOWED_ORIGINAL_INSTRUMENT_CHANGES:current['files'][name]='c'*64
        self.assertTrue(recovery.unchanged_original_source(old,current))
        current['files']['game/src/mecha_game/session.py']='d'*64
        self.assertFalse(recovery.unchanged_original_source(old,current))

    def test_original_saved_output_drift_refuses(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);pins=retained_tree(root)
            with patch.object(recovery,'ROOT',root),patch.object(recovery,'PINNED_FILES',pins):
                bound,result=recovery._original_evidence()
                self.assertFalse(result['checks']['observations_bound'])
                self.assertIn(recovery.ORIGINAL_OUTPUT+'/save/campaign.sqlite3',bound)
                (root/recovery.ORIGINAL_OUTPUT/'save/campaign.sqlite3').write_text('tampered')
                with self.assertRaisesRegex(ValueError,'output changed'):recovery._original_evidence()

    def test_unbound_new_saved_file_refuses(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);pins=retained_tree(root)
            recovery.write(root/recovery.ORIGINAL_OUTPUT/'save/extra.json',{})
            with patch.object(recovery,'ROOT',root),patch.object(recovery,'PINNED_FILES',pins), \
                    self.assertRaisesRegex(ValueError,'inventory'):recovery._original_evidence()

    def test_original_error_terminal_is_immutable(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);pins=retained_tree(root)
            terminal=root/recovery.ORIGINAL_OUTPUT/'terminal.json'
            value=recovery.read(terminal);value['status']='completed';terminal.write_bytes(recovery.encode(value))
            with patch.object(recovery,'ROOT',root),patch.object(recovery,'PINNED_FILES',pins), \
                    self.assertRaisesRegex(ValueError,'retained evidence'):recovery._original_evidence()


if __name__=='__main__':unittest.main()
