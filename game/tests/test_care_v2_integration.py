"""X7 v2 actual-life succession, terminal receipt and immutable-era integration."""
import copy
from contextlib import closing
import json
from pathlib import Path
import sqlite3
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
for folder in ('game/src', 'packages/mecha_engine/src'):
    sys.path.insert(0, str(ROOT / folder))
from mecha_engine.generation import generate_candidate
from mecha_engine.runtime.care import select_care_successor
from mecha_game.care_history import capture_care_context, validate_care_selection
from mecha_game.session import CompanionSession, load_session_inputs
from mecha_game import campaign as api
from mecha_game.contribute import companion_release_source
from mecha_game.era_plan import EraPlan
from mecha_game.execution import decode_execution_inputs, reproduce_era

POLICY = 'observed_care_selection_v2'


def pet(**kwargs):
    grid, profile, model = load_session_inputs(
        ROOT / 'data/seed_grids_16x16/mg_seed16_001_beetle.json',
        ROOT / 'data/slips/valid/slip_v2_cleanliness.json')
    return CompanionSession(grid, profile, model=model, **kwargs)


def neglect(session):
    for _ in range(400):
        if not session.alive:
            return
        session.advance()
    raise AssertionError('actual neglect must reach death')


class CareV2IntegrationTests(unittest.TestCase):
    def test_actual_death_successor_is_cold_and_saved_policy_and_receipt_survive(self):
        session = pet(care_selection_policy=POLICY, learning_policy='qtable')
        session.advance('feed')
        neglect(session)
        self.assertFalse(session.alive)
        context = capture_care_context(session)
        parent_id = session.lineage[-1]['life_id']
        session.succeed()
        selection = session.lineage[-1]['care_selection']
        self.assertEqual(context, selection['context'])
        self.assertEqual(parent_id, session.lineage[-1]['parent_life_id'])
        self.assertEqual(POLICY, selection['receipt']['policy'])
        self.assertEqual(0, session.state['age_ticks'])
        self.assertNotIn('thread_states', session.state)
        self.assertTrue(session.alive)
        with tempfile.TemporaryDirectory() as tmp:
            path = session.save(Path(tmp) / 'pet.json')
            loaded = CompanionSession.load(path)
            self.assertEqual(selection, loaded.lineage[-1]['care_selection'])
            self.assertEqual(POLICY, loaded.care_selection_policy)
            self.assertEqual(POLICY, loaded.adopt(loaded.grid, loaded.slip_profile).care_selection_policy)
            with self.assertRaises(ValueError):
                CompanionSession.load(path, care_selection_policy='off')

    def test_trajectory_terminal_and_source_tampering_refuse(self):
        session = pet(learning_policy='incumbent')
        session.advance('feed')
        neglect(session)
        child, receipt = select_care_successor(session.grid, session.model, session.slip_profile,
            context=capture_care_context(session), rng_seed=20261007, policy=POLICY)
        selection = dict(context=capture_care_context(session), receipt=receipt)
        validate_care_selection(selection, parent_record=session.lineage[-1], child_grid=child)
        mutations = [
            lambda r: r['source_identity'].update(life_id='forged'),
            lambda r: r['candidates'][0]['episode']['initial_state'].update(cleanliness=-1),
            lambda r: r['candidates'][0]['episode']['final_state'].pop('cleanliness'),
            lambda r: r['candidates'][0]['episode']['trajectory'][0]['decision_state'].update(cleanliness=False),
            lambda r: r['candidates'][0]['episode']['trajectory'][0]['decision_state'].update(cleanliness=.123),
            lambda r: r['candidates'][0]['episode']['initial_state'].update(learning_switches=[]),
            lambda r: r['candidates'][0]['episode']['history'][0].update(recoveries=[{}]),
            lambda r: r['candidates'][0]['episode']['trajectory'][0].update(decision_state=None),
            lambda r: r.update(selection_order=['need_balance']),
            lambda r: r['candidates'][0].update(terminal_survival=not r['candidates'][0]['alive']),
            lambda r: r['candidates'][0]['episode'].update(ticks_requested=1),
            lambda r: r['candidates'][0]['episode'].update(need_balance=.123),
            lambda r: r['candidates'][0]['episode']['final_state'].update(alive=not r['candidates'][0]['alive']),
            lambda r: r['candidates'][0]['episode']['trajectory'][0].update(evaluation_tick=2),
            lambda r: r['candidates'][0]['episode']['trajectory'][0].update(source_action='play'),
            lambda r: r['candidates'][0]['episode']['trajectory'][0].update(applied_action='play'),
            lambda r: r['candidates'][0]['episode']['trajectory'][0]['decision_state'].update(age_ticks=9),
            lambda r: r['candidates'][0]['episode']['trajectory'][0]['result'].update(alive=False),
            lambda r: r['candidates'][0]['episode']['history'].pop(),
            lambda r: r['candidates'][0]['episode']['initial_state'].update(age_ticks=3),
        ]
        for mutate in mutations:
            with self.subTest(mutate=mutate):
                bad = copy.deepcopy(selection)
                mutate(bad['receipt'])
                with self.assertRaises(ValueError):
                    validate_care_selection(bad, parent_record=session.lineage[-1], child_grid=child)

    def test_absent_empty_and_off_paths_preserve_exact_incumbent_candidate(self):
        session = pet(learning_policy='incumbent')
        empty = capture_care_context(session)
        session.advance('feed')
        observed = capture_care_context(session)
        expected = generate_candidate(session.grid, session.model, session.slip_profile, rng_seed=991)
        for policy, context in [(POLICY, None), (POLICY, empty), ('off', observed)]:
            with self.subTest(policy=policy, context=context):
                child, receipt = select_care_successor(session.grid, session.model, session.slip_profile,
                    context=context, rng_seed=991, policy=policy)
                self.assertEqual(expected, child)
                self.assertIsNone(receipt)

    def test_actual_founder_occurrences_persist_continue_and_reproduce(self):
        cold = api.load_campaign_inputs(**api.default_campaign_paths(ROOT), seed_limit=4, with_models=False)
        inputs = api.prepare_campaign_models(cold, repair_epochs=1)
        sessions = [CompanionSession(inputs['seed_grids'][0], inputs['slip_profile'],
                    model=inputs['generation_model'], learning_policy='incumbent') for _ in range(2)]
        sessions[0].advance('feed'); sessions[1].advance('sleep')
        sources = [companion_release_source(pet) for pet in sessions]
        before = copy.deepcopy(sources)
        campaign = api.KeeperCampaign(copy.deepcopy(inputs), campaign_id='care-v2-live',
            era_config=dict(generations=2, population=2, damage_cycles=1, ticks=3, dropout_rate=.2))
        era = campaign.advance_era('calm', released_grids=[pet.grid for pet in sessions],
            released_sources=sources, care_selection_policy=POLICY, care_evaluator='pristine')
        self.assertEqual(before, sources)
        contexts = decode_execution_inputs(era['execution'])['founder_care_contexts']
        self.assertEqual([s['care_context'] for s in sources], contexts)
        self.assertNotEqual(contexts[0]['life_id'], contexts[1]['life_id'])
        first = era['report']['generations'][0]['creatures']
        self.assertEqual([0, 1], [c['care_context_origin']['founder_submission_index'] for c in first])
        self.assertTrue(all(c['care_selection']['policy'] == POLICY for c in first))
        for generation in era['report']['generations']:
            for creature in generation['creatures']:
                origin = creature.get('care_context_origin')
                if origin:
                    self.assertEqual(contexts[origin['founder_submission_index']]['life_id'],
                        creature['care_selection']['source_identity']['life_id'])
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp); ledger = folder / 'campaign.sqlite3'; state = folder / 'state.json'
            plan = EraPlan(folder / 'plan.json'); plan.begin(campaign, era, None); plan.finish(ledger, state)
            loaded = api.KeeperCampaign.load_state(copy.deepcopy(inputs), state, ledger)
            uninterrupted = campaign.advance_era('calm', care_selection_policy=POLICY, care_evaluator='pristine')
            resumed = loaded.advance_era('calm', care_selection_policy=POLICY, care_evaluator='pristine')
            self.assertEqual(uninterrupted['report'], resumed['report'])
            self.assertEqual(uninterrupted['elites'], resumed['elites'])
            before_bytes = ledger.read_bytes()
            with closing(sqlite3.connect(ledger.as_uri() + '?mode=ro', uri=True)) as conn:
                result = reproduce_era(conn, 'care-v2-live', 0)
            self.assertEqual('matched', result['status'], result)
            self.assertEqual(before_bytes, ledger.read_bytes())


if __name__ == '__main__':
    unittest.main()
