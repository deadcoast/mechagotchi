"""X1: actual application transitions preserve factual Keeper continuity."""
import copy
import json
import os
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
for folder in ('game/src', 'packages/mecha_engine/src'):
    sys.path.insert(0, str(ROOT / folder))
import pygame
from mecha_game.app import run, _EraBench
from mecha_game.footer import FooterPager
from mecha_game.session import CompanionSession


def key(value):
    return pygame.event.Event(pygame.KEYDOWN, key=value, mod=0)


class KeeperContinuityApplicationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.fixture = tempfile.TemporaryDirectory()
        cls.addClassCleanup(cls.fixture.cleanup)
        cls.seed = Path(cls.fixture.name) / 'keeper'
        with patch.dict(os.environ, SDL_VIDEODRIVER='dummy', SDL_AUDIODRIVER='dummy'):
            assert run(['--keeper-dir', str(cls.seed), '--era-scale', 'tiny',
                        '--eras', '1', '--ticks', '1', '--tick-frames', '1',
                        '--fps', '0', '--scale', '1']) == 0

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.keeper = Path(self.temp.name) / 'keeper'
        shutil.copytree(self.seed, self.keeper)

    def bench(self):
        return _EraBench('tiny', cache_dir=self.keeper/'model_cache',
                         state_path=self.keeper/'campaign_state.json',
                         ledger_path=self.keeper/'campaign.sqlite3')

    def observe(self, batches, extra=()):
        sequence = iter(batches)
        pages = []
        original = FooterPager.layout
        def poll():
            batch = next(sequence, [pygame.event.Event(pygame.QUIT)])
            return batch() if callable(batch) else batch
        def capture(pager, lines, measure, width, rows):
            page = original(pager, lines, measure, width, rows)
            pages.append({'all':list(lines), 'visible':list(page.lines)})
            self.assertTrue(all(measure(line) <= width for line in page.lines))
            return page
        with patch.dict(os.environ, SDL_VIDEODRIVER='dummy', SDL_AUDIODRIVER='dummy'), \
                patch('pygame.event.get', side_effect=poll), patch.object(FooterPager, 'layout', capture):
            self.assertEqual(0, run(['--keeper-dir', str(self.keeper), '--era-scale', 'tiny',
                                    '--scale', '1', '--fps', '0', '--tick-frames', '1', *extra]))
        return pages

    def two_lives(self, policy='incumbent'):
        path = self.keeper/'companion.json'
        session = CompanionSession.load(path)
        if policy != session.learning_policy:
            session = CompanionSession(session.grid, session.slip_profile,
                                       model=session.model, learning_policy=policy)
        for _ in range(100):
            if not session.alive:
                break
            session.advance(player_action='idle')
        self.assertFalse(session.alive)
        session.succeed()
        self.assertEqual(2, len(session.lineage))
        session.save_checkpoint(path)
        session.sync_lineage_export(self.keeper/'lineage.json')
        return copy.deepcopy(session.lineage)

    def test_existing_state_without_ledger_never_constructs_default_campaign(self):
        state = self.keeper/'campaign_state.json'
        before = state.read_bytes()
        (self.keeper/'campaign.sqlite3').unlink()
        lines = self.bench().budget_lines()
        self.assertIn('Covenant unavailable', ' '.join(lines))
        self.assertEqual(before, state.read_bytes())
        self.assertFalse((self.keeper/'campaign.sqlite3').exists())

    def test_existing_ledger_without_state_never_constructs_default_campaign(self):
        ledger = self.keeper/'campaign.sqlite3'
        before = ledger.read_bytes()
        (self.keeper/'campaign_state.json').unlink()
        self.assertIn('Covenant unavailable', ' '.join(self.bench().budget_lines()))
        self.assertEqual(before, ledger.read_bytes())
        self.assertFalse((self.keeper/'campaign_state.json').exists())

    def test_supported_format_incomplete_state_is_readable_and_unchanged(self):
        path = self.keeper/'campaign_state.json'
        broken = b'{"state_format":"keeper_campaign_state_v1"}'
        path.write_bytes(broken)
        pages = self.observe([[key(pygame.K_c)], [key(pygame.K_F1)]])
        self.assertIn('Covenant unavailable', ' '.join(pages[0]['all']))
        self.assertEqual(broken, path.read_bytes())

    def test_care_death_child_hatch_archive_and_restart_keep_all_lives(self):
        for policy in ('incumbent', 'qtable'):
            with self.subTest(policy=policy):
                earlier = self.two_lives(policy)
                self.observe([[key(pygame.K_h)], [key(pygame.K_RETURN)],
                              [key(pygame.K_b)], [key(pygame.K_a)], [key(pygame.K_l)]])
                actual = CompanionSession.load(self.keeper/'companion.json')
                self.assertEqual(4, len(actual.lineage))
                self.assertEqual(earlier[0]['death_cause'], actual.lineage[0]['death_cause'])
                self.assertNotIn('death_cause', actual.lineage[1])
                self.assertNotIn('death_cause', actual.lineage[2])
                self.assertEqual(policy, actual.learning_policy)
                saved = (self.keeper/'companion.json').read_bytes()
                pages = self.observe([[key(pygame.K_l)], [key(pygame.K_COMMA)],
                                      [key(pygame.K_COMMA)], [key(pygame.K_COMMA)]])
                self.assertIn(earlier[0]['grid_id'], ' '.join(pages[-1]['all']))
                self.assertEqual(saved, (self.keeper/'companion.json').read_bytes())
                # Reset only this disposable fixture between the two policies.
                for name in ('companion.json', 'companion.bak.json', 'lineage.json', 'lineage.bak.json'):
                    source = self.seed/name
                    if source.exists():
                        shutil.copyfile(source, self.keeper/name)

    def test_explicit_new_companion_keeps_available_keeper_history(self):
        earlier = self.two_lives()
        self.observe([[key(pygame.K_F1)]], extra=('--new',))
        actual = CompanionSession.load(self.keeper/'companion.json')
        self.assertEqual(3, len(actual.lineage))
        self.assertEqual(earlier[0]['grid_id'], actual.lineage[0]['grid_id'])
        self.assertNotIn('death_cause', actual.lineage[1])


    def test_recovery_preview_pauses_care_blocks_changes_and_cancel_preserves_pair(self):
        state = self.keeper/'campaign_state.json'
        ledger = self.keeper/'campaign.sqlite3'
        state.write_bytes(b'broken primary')
        ledger_bytes = ledger.read_bytes()
        before = CompanionSession.load(self.keeper/'companion.json').snapshot()['age_ticks']
        pages = self.observe([[key(pygame.K_c), key(pygame.K_u), key(pygame.K_u)],
                              [key(pygame.K_f), key(pygame.K_1), key(pygame.K_h)],
                              [key(pygame.K_c), key(pygame.K_f)]])
        self.assertIn('RECOVERY', ' '.join(pages[0]['all']))
        self.assertEqual(b'broken primary', state.read_bytes())
        self.assertEqual(ledger_bytes, ledger.read_bytes())
        self.assertEqual(before, CompanionSession.load(self.keeper/'companion.json').snapshot()['age_ticks'])

    def test_later_recovery_confirmation_restores_pair_and_retains_corrupt_bytes(self):
        state = self.keeper/'campaign_state.json'
        expected = state.read_bytes()
        broken = b'broken primary requiring explicit restore'
        state.write_bytes(broken)
        self.observe([[key(pygame.K_c), key(pygame.K_u)], [key(pygame.K_u)],
                      [key(pygame.K_F1)]])
        self.assertEqual(json.loads(expected), json.loads(state.read_bytes()))
        self.assertTrue(any(p.is_file() and p.read_bytes() == broken
                            for p in self.keeper.rglob('*')))
        self.assertEqual(1, self.bench().ensure().era_offset)

    def test_changed_ledger_after_recovery_preview_refuses_restore(self):
        bench = self.bench()
        bench.inspect_recovery()
        ledger = self.keeper/'campaign.sqlite3'
        state_before = (self.keeper/'campaign_state.json').read_bytes()
        changed = ledger.read_bytes() + b'external change'
        ledger.write_bytes(changed)
        with self.assertRaisesRegex(ValueError, 'changed after inspection'):
            bench.restore_recovery()
        self.assertEqual(changed, ledger.read_bytes())
        self.assertEqual(state_before, (self.keeper/'campaign_state.json').read_bytes())

    def test_unrelated_pending_campaign_refuses_before_any_completion_write(self):
        from mecha_game.era_plan import state_digest
        bench = self.bench()
        campaign = bench.ensure(models=True)
        era = campaign.advance_era(bench.weather)
        bench.plan.begin(campaign, era, state_digest(bench.state_path))
        companion = CompanionSession.load(self.keeper/'companion.json')
        other = CompanionSession(companion.grid, companion.slip_profile, model=companion.model)
        other.bind_campaign('unrelated_keeper_campaign')
        bench.keeper_session = other
        paths = [bench.state_path, bench.ledger_path, bench.plan.path]
        before = [p.read_bytes() for p in paths]
        with self.assertRaisesRegex(ValueError, 'different recorded Keeper'):
            bench.run_era(bench.ledger_path)
        self.assertEqual(before, [p.read_bytes() for p in paths])


    def test_prior_checkpoint_is_selectable_and_restores_only_on_confirmation(self):
        bench = self.bench()
        original = json.loads(bench.state_path.read_text(encoding='utf-8'))
        bench.run_era(bench.ledger_path)
        pages = self.observe([[key(pygame.K_c), key(pygame.K_y)],
                              [key(pygame.K_u)], [key(pygame.K_F1)]])
        self.assertIn('RECOVERY (prior)', ' '.join(pages[0]['all']))
        self.assertEqual(original, json.loads(bench.state_path.read_text(encoding='utf-8')))


    def test_first_import_binding_changes_only_association_without_care(self):
        path = self.keeper/'companion.json'
        old = CompanionSession.load(path)
        unbound = CompanionSession(old.grid, old.slip_profile, model=old.model)
        unbound.save_checkpoint(path)
        before = json.loads(path.read_text(encoding='utf-8'))
        covenant_dir = self.keeper/'covenants'
        covenant_dir.mkdir(exist_ok=True)
        profile = json.loads((ROOT/'data/slips/valid/slip_lcd_seed.json').read_text(encoding='utf-8'))
        (covenant_dir/'chosen.json').write_text(json.dumps(profile), encoding='utf-8')
        self.observe([[key(pygame.K_i)], [key(pygame.K_RETURN)]])
        after = json.loads(path.read_text(encoding='utf-8'))
        prior_chronicle, current_chronicle = before.pop('chronicle'), after.pop('chronicle')
        self.assertEqual(before, after)
        self.assertIsNone(prior_chronicle['campaign_id'])
        self.assertEqual(json.loads((self.keeper/'campaign_state.json').read_text(encoding='utf-8'))['campaign_id'],
                         current_chronicle['campaign_id'])
        self.assertEqual(1, len(current_chronicle['campaign_links']))
        self.assertEqual(0, CompanionSession.load(path).state['age_ticks'])


if __name__ == '__main__':
    unittest.main()
