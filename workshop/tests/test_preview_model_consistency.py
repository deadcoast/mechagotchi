"""Preview-model-consistency contract: real HTTP, fixed engine fixtures, no eras."""
from copy import deepcopy
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
for source in ('workshop/server', 'game/src', 'packages/mecha_engine/src'):
    sys.path.insert(0, str(ROOT/source))
import test_workshop_context as context_fixtures
from test_workshop_context import files
from mecha_game.session import CompanionSession
from mecha_game.campaign import KeeperCampaign
from mecha_game.replay import build_replay
from mecha_engine.runtime import live_cycle
from mecha_engine.repair import train_repair_model
import workshop_server
import authoring


class PreviewModelConsistencyTests(unittest.TestCase):
    """One preregistered beetle, covenant and seed; no outcome qualification."""
    setUp = context_fixtures.SelectedKeeperTests.setUp
    tearDown = context_fixtures.SelectedKeeperTests.tearDown
    request = context_fixtures.SelectedKeeperTests.request
    context = context_fixtures.SelectedKeeperTests.context
    pins = context_fixtures.SelectedKeeperTests.pins

    @classmethod
    def setUpClass(cls):
        context_fixtures.SelectedKeeperTests.setUpClass.__func__(cls)
        # Actual production repair training input, shared only to avoid repeating
        # training for every short-lived HTTP server; no engine outputs are mocked.
        cls.repair = train_repair_model(workshop_server.build_seed_grids_16()[:40])

    def keeper(self, name='one', body='workload-v1'):
        root = self.root/name
        root.mkdir()
        pet = CompanionSession(deepcopy(self.grid), deepcopy(self.profile), model=self.model, body_response=body)
        pet.bind_campaign(name)
        pet.save(root/'companion.json')
        campaign = KeeperCampaign({'slip_profile':deepcopy(self.profile)}, campaign_id=name,
            body_response=body, era_config={'population':3, 'generations':2})
        campaign.save(root/'campaign.sqlite3')
        campaign.save_state(root/'campaign_state.json')
        return root, pet, campaign

    def start(self, keeper=None, project=None):
        server = context_fixtures.SelectedKeeperTests.start(self, keeper, project)
        server._models_by_scale[16] = (self.model, self.repair)
        return server

    def payload(self, selected_context=None, **kwargs):
        return dict(document=deepcopy(self.document), draft_revision=7, cycles=1, ticks=48,
            rng_seed=20260512, **(self.pins(selected_context) if selected_context else {}), **kwargs)

    def expected(self, body, *, replay=False, **kwargs):
        operation = build_replay if replay else live_cycle
        return operation(self.grid, self.profile, self.repair, damage_cycles=1, ticks=48,
            rng_seed=20260512, body_response=body, **kwargs)

    def switch(self, root, pet, body=None):
        body = body or ('legacy' if pet.body_response=='workload-v1' else 'workload-v1')
        changed = pet.adopt(pet.grid, pet.slip_profile, body_response=body)
        changed.save(root/'companion.json')
        return changed

    def test_context_reports_current_version_and_standalone_legacy(self):
        for model in ('workload-v1', 'legacy'):
            root, _, _ = self.keeper(model, model)
            context = self.context(self.start(root))
            self.assertEqual(model, context.get('body_response'), context)
            self.assertEqual('current_keeper', context.get('body_response_source'))
        context = self.context(self.start())
        self.assertEqual('legacy', context.get('body_response'))
        self.assertEqual('standalone_legacy', context.get('body_response_source'))

    def test_actual_live_http_matches_both_engine_models_and_physiology_differs(self):
        balances = {}
        for model in ('workload-v1', 'legacy'):
            root, _, _ = self.keeper(model, model)
            server = self.start(root)
            context = self.context(server)
            before = files(root)
            code, result = self.request(server, '/api/preview/live', self.payload(context))
            self.assertEqual(200, code, result.get('error', sorted(result)))
            self.assertEqual(self.expected(model), result['report'])
            self.assertEqual(model, result.get('body_response'))
            balances[model] = result['report']['cycles'][0]['episode']['need_balance']
            self.assertEqual(before, files(root))
        self.assertNotEqual(balances['legacy'], balances['workload-v1'])

    def test_actual_replay_http_matches_engine_frames_and_live_episode(self):
        for model in ('workload-v1', 'legacy'):
            root, _, _ = self.keeper(model, model)
            server = self.start(root)
            context = self.context(server)
            before = files(root)
            code, result = self.request(server, '/api/preview/replay', self.payload(context))
            self.assertEqual(200, code, result.get('error', sorted(result)))
            self.assertEqual(self.expected(model, replay=True), result['replay'])
            self.assertEqual(model, result.get('body_response'))
            self.assertEqual(self.expected(model)['cycles'], result['replay']['live']['cycles'])
            recorded = live_cycle(self.grid, self.profile, self.repair, damage_cycles=1,
                ticks=48, rng_seed=20260512, body_response=model, record_frames=True)
            actual_ticks = [frame['entry'] for frame in result['replay']['frames'] if frame['phase']=='episode_tick']
            self.assertEqual(recorded['cycles'][0]['frames']['episode_history'], actual_ticks)
            self.assertTrue(actual_ticks)
            self.assertEqual(before, files(root))

    def test_native_living_previews_require_exact_context_pins(self):
        root, _, _ = self.keeper()
        server = self.start(root)
        context = self.context(server)
        before = files(root)
        for route in ('live', 'replay'):
            for pins in ({}, {'context_id':context['context_id']},
                    dict(context_id='another', expected_context_revision=context['context_revision']),
                    dict(context_id=context['context_id'], expected_context_revision=['malformed'])):
                with self.subTest(route=route, pins=pins):
                    code, result = self.request(server, '/api/preview/'+route, dict(self.payload(), **pins))
                    self.assertEqual(409, code, result.get('error', sorted(result)))
                    self.assertEqual('context_changed', result['error_code'])
                    self.assertNotIn('report', result)
                    self.assertNotIn('replay', result)
        self.assertEqual(before, files(root))

    def test_request_models_are_assertions_and_cannot_override_authority(self):
        root, _, _ = self.keeper()
        server = self.start(root)
        context = self.context(server)
        before = files(root)
        for route in ('live', 'replay'):
            for model in (None, False, 1, {}, [], 'future-v9'):
                with self.subTest(route=route, model=model):
                    code, result = self.request(server, '/api/preview/'+route, self.payload(context, body_response=model))
                    self.assertEqual(400, code, result.get('error', sorted(result)))
            code, result = self.request(server, '/api/preview/'+route, self.payload(context, body_response='legacy'))
            self.assertEqual(409, code, result.get('error', sorted(result)))
            self.assertEqual('body_response_changed', result['error_code'])
            code, result = self.request(server, '/api/preview/'+route, self.payload(context,
                body_response='workload-v1', context={'body_response':'legacy'}, preview_identity={'body_response':'legacy'}))
            self.assertEqual(200, code, result.get('error', sorted(result)))
            self.assertEqual('workload-v1', result['body_response'])
        self.assertEqual(before, files(root))

    def test_saved_malformed_model_refuses_without_legacy_fallback(self):
        root, _, _ = self.keeper()
        server = self.start(root)
        original = (root/'companion.json').read_bytes()
        for invalid in (False, None, {}, [], 'future-v9', 'legacy'):
            saved = json.loads(original)
            saved['body_response'] = invalid
            (root/'companion.json').write_text(json.dumps(saved))
            before = files(root)
            context = self.context(server)
            self.assertFalse(context['available'])
            for route in ('live', 'replay'):
                code, result = self.request(server, '/api/preview/'+route, self.payload(context))
                self.assertEqual(409, code, result.get('error', sorted(result)))
                self.assertEqual('context_unavailable', result['error_code'])
            self.assertEqual(before, files(root))

    def test_read_only_model_mismatch_uses_current_life_after_refresh(self):
        root, pet, _ = self.keeper(body='legacy')
        server = self.start(root)
        old = self.context(server)
        self.switch(root, pet)
        context = self.context(server)
        self.assertTrue(context['available'], context)
        self.assertFalse(context['capabilities']['authoring'])
        before = files(root)
        for route in ('live', 'replay'):
            code, result = self.request(server, '/api/preview/'+route, self.payload(old))
            self.assertEqual(409, code, result.get('error', sorted(result)))
            code, result = self.request(server, '/api/preview/'+route, self.payload(context))
            self.assertEqual(200, code, result.get('error', sorted(result)))
            self.assertEqual('workload-v1', result['body_response'])
        self.assertEqual(before, files(root))

    def test_model_or_life_change_during_actual_simulation_discards_result(self):
        for route in ('live', 'replay'):
            for body in ('legacy', 'workload-v1'):
                with self.subTest(route=route, replacement=body):
                    root, pet, _ = self.keeper(route+body)
                    server = self.start(root)
                    context = self.context(server)
                    operation_name = 'live_cycle' if route=='live' else 'build_replay'
                    operation = getattr(workshop_server, operation_name)
                    after = {}
                    def changed(*args, **kwargs):
                        result = operation(*args, **kwargs)
                        self.switch(root, pet, body)
                        after.update(files(root))
                        return result
                    with patch.object(workshop_server, operation_name, side_effect=changed):
                        code, result = self.request(server, '/api/preview/'+route, self.payload(context))
                    self.assertEqual(409, code, result.get('error', sorted(result)))
                    self.assertEqual('context_changed', result['error_code'])
                    self.assertNotIn('report', result)
                    self.assertNotIn('replay', result)
                    self.assertEqual(after, files(root))
                    fresh = self.context(server)
                    code, retry = self.request(server, '/api/preview/'+route, self.payload(fresh))
                    self.assertEqual(200, code, retry)
                    self.assertEqual(body, retry['body_response'])

    def test_repeated_results_and_full_inputs_have_model_and_context_bound_ids(self):
        root, pet, _ = self.keeper(body='legacy')
        server = self.start(root)
        context = self.context(server)
        identities = []
        for route in ('live', 'replay'):
            code, first = self.request(server, '/api/preview/'+route, self.payload(context))
            self.assertEqual(200, code, first)
            code, repeat = self.request(server, '/api/preview/'+route, self.payload(context))
            self.assertEqual(first, repeat)
            identity = first['preview_identity']
            self.assertEqual('mechagotchi_workshop_preview_v1', identity['format'])
            self.assertEqual('legacy', identity['body_response'])
            self.assertEqual(context['context_id'], identity['context_id'])
            self.assertEqual(context['context_revision'], identity['context_revision'])
            self.assertEqual(first['preview_id'], authoring.digest(identity))
            self.assertEqual(64, len(identity['inputs_sha256']))
            changed = self.payload(context)
            changed['document']['profile']['name'] += ' same ID changed content'
            code, other = self.request(server, '/api/preview/'+route, changed)
            self.assertEqual(200, code, other)
            self.assertNotEqual(first['preview_id'], other['preview_id'])
            changed = self.payload(context)
            changed['ticks'] = 49
            code, other = self.request(server, '/api/preview/'+route, changed)
            self.assertEqual(200, code, other)
            self.assertNotEqual(first['preview_id'], other['preview_id'])
            identities.append(first['preview_id'])
        self.assertNotEqual(*identities)
        self.switch(root, pet)
        fresh = self.context(server)
        for route, prior in zip(('live', 'replay'), identities):
            code, result = self.request(server, '/api/preview/'+route, self.payload(fresh))
            self.assertEqual(200, code, result.get('error', sorted(result)))
            self.assertNotEqual(prior, result['preview_id'])
            self.assertEqual('workload-v1', result['preview_identity']['body_response'])

    def test_standalone_defaults_stay_legacy_and_explicit_pins_are_honored(self):
        server = self.start()
        before = files(self.root)
        for route in ('live', 'replay'):
            code, result = self.request(server, '/api/preview/'+route, self.payload())
            self.assertEqual(200, code, result.get('error', sorted(result)))
            self.assertEqual('legacy', result.get('body_response'))
            expected = self.expected('legacy', replay=route=='replay')
            self.assertEqual(expected, result['replay' if route=='replay' else 'report'])
            code, result = self.request(server, '/api/preview/'+route, self.payload(body_response='workload-v1'))
            self.assertEqual(409, code, result.get('error', sorted(result)))
        for route in ('render', 'clip', 'offspring', 'live', 'replay'):
            code, result = self.request(server, '/api/preview/'+route,
                dict(self.payload(), context_id='another', expected_context_revision='stale'))
            self.assertEqual(409, code, result.get('error', sorted(result)))
        self.assertEqual(before, files(self.root))

    def test_unpinned_read_only_portrait_remains_available_but_pins_refuse_stale(self):
        root, pet, _ = self.keeper()
        server = self.start(root)
        old = self.context(server)
        self.switch(root, pet)
        before = files(root)
        for route in ('render', 'clip', 'offspring'):
            code, result = self.request(server, '/api/preview/'+route, self.payload(old))
            self.assertEqual(409, code, result.get('error', sorted(result)))
            code, result = self.request(server, '/api/preview/'+route, self.payload())
            self.assertEqual(200, code, result.get('error', sorted(result)))
        self.assertEqual(before, files(root))


if __name__ == '__main__':
    unittest.main()
