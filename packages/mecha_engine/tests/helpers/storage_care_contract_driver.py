"""X7 immutable care inputs: independent passive-ledger acceptance probes."""
import base64
import copy
import hashlib
import importlib.util
import json
import unittest
from pathlib import Path

import mecha_engine.storage as package_store

spec = importlib.util.spec_from_file_location('storage_execution_fixture',
    Path(__file__).with_name('storage_execution_contract_driver.py'))
legacy = importlib.util.module_from_spec(spec)
spec.loader.exec_module(legacy)


def retain(bundle, value):
    data = package_store.canonical_json(value).encode('utf-8')
    sha = hashlib.sha256(data).hexdigest()
    bundle['blobs'][sha] = dict(media_type='application/json',
        data_base64=base64.b64encode(data).decode('ascii'))
    return sha


def payload(bundle):
    sha = bundle['manifest']['inputs']['care_inputs_sha256']
    return json.loads(base64.b64decode(bundle['blobs'][sha]['data_base64']))


def rehash(bundle, value):
    old = bundle['manifest']['inputs']['care_inputs_sha256']
    new = retain(bundle, value)
    bundle['manifest']['inputs']['care_inputs_sha256'] = new
    if old != new:
        del bundle['blobs'][old]


def context(grid, ordinal):
    return dict(format='keeper_care_context_v1', keeper_id='keeper',
        life_id=f'keeper:life-{ordinal}', grid_id=grid['grid_id'],
        grid_sha256=legacy.digest(grid),
        care_summary=dict(history='complete', from_age_ticks=0, ticks_observed=1,
            keeper_actions={'feed': 1}, companion_actions={}, beg_requests=0),
        events=[dict(tick=1, session_tick=ordinal + 1, actor='keeper', action='feed',
            begging=False, alive=True, death_cause=None)], events_omitted=0,
        last_age_ticks=1, last_session_tick=ordinal + 1, outcome='alive')


def fixture():
    campaign, profile, era, bundle = legacy.fixture()
    contexts = []
    # Retain unrelated source bytes as a non-founder documentary source.
    bundle['manifest']['sources'][0]['role'] = 'documentary'
    for ordinal, occurrence in enumerate(bundle['manifest']['founder_occurrences']):
        grid = json.loads(base64.b64decode(bundle['blobs'][occurrence['grid_sha256']]['data_base64']))
        care = context(grid, ordinal)
        contexts.append(care)
        source = dict(role='founder', founder_ordinal=ordinal,
            source_kind='keeper_companion', source_position=ordinal,
            keeper_id=care['keeper_id'], life_id=care['life_id'], care_context=copy.deepcopy(care))
        bundle['manifest']['sources'].append(source)
        occurrence.update({key: copy.deepcopy(value) for key, value in source.items()
            if key not in ('role', 'founder_ordinal')})
    bundle['manifest']['inputs']['care_inputs_sha256'] = retain(bundle,
        dict(format='keeper_care_inputs_v1', policy='off', evaluator='pristine',
             founder_contexts=contexts))
    era['report']['care_selection'] = dict(policy='off', evaluator='pristine',
        founder_contexts=copy.deepcopy(contexts), elite_contexts=[copy.deepcopy(contexts[0])],
        elite_origins=[dict(founder_submission_index=0, context_sha256=legacy.digest(contexts[0]))])
    bundle['manifest']['report_sha256'] = legacy.digest(era['report'])
    return campaign, profile, era, bundle


class StorageCareTests(unittest.TestCase):
    store = package_store

    def setUp(self):
        self.campaign, self.profile, self.era, self.bundle = fixture()

    def test_round_trip_is_exact_and_nonmutating(self):
        before = copy.deepcopy(self.bundle)
        conn = self.store.open_ledger(':memory:')
        self.addCleanup(conn.close)
        self.store.record_campaign(conn, self.campaign)
        self.store.record_era(conn, self.campaign['campaign_id'], self.era,
                              self.profile, execution=self.bundle)
        self.assertEqual(before, self.bundle)
        self.assertEqual(before, self.store.load_era_execution(conn, self.campaign['campaign_id'], 0))

    def test_legacy_bundle_stays_valid_without_care_fields(self):
        self.store.validate_execution(legacy.fixture()[-1])

    def test_invalid_payload_schema_and_named_policy_refuse(self):
        changes = [lambda p: p.update(format='future'), lambda p: p.update(policy='default'),
            lambda p: p.update(evaluator='invented'), lambda p: p.update(extra=True),
            lambda p: p.update(founder_contexts=p['founder_contexts'][:1]),
            lambda p: p.update(founder_contexts={}), lambda p: p.pop('policy')]
        for change in changes:
            with self.subTest(change=change):
                bundle = copy.deepcopy(self.bundle); value = payload(bundle); change(value); rehash(bundle, value)
                with self.assertRaises(ValueError): self.store.validate_execution(bundle)

    def test_rehashed_context_metadata_swap_refuses(self):
        bundle = copy.deepcopy(self.bundle); value = payload(bundle)
        value['founder_contexts'].reverse(); rehash(bundle, value)
        with self.assertRaises(ValueError): self.store.validate_execution(bundle)

    def test_source_occurrence_context_disagreement_refuses(self):
        for section in ('sources', 'founder_occurrences'):
            with self.subTest(section=section):
                bundle = copy.deepcopy(self.bundle)
                row = bundle['manifest'][section][1 if section == 'sources' else 0]
                row['care_context']['life_id'] = 'another-life'
                with self.assertRaises(ValueError): self.store.validate_execution(bundle)

    def test_direct_context_body_hash_binding_is_canonical_not_blob_bytes(self):
        # Fixture founder blobs retain insertion order; their canonical digest differs.
        self.assertNotEqual(self.bundle['manifest']['inputs']['founder_sha256'][0],
            payload(self.bundle)['founder_contexts'][0]['grid_sha256'])
        self.store.validate_execution(self.bundle)

    def test_consistently_rehashed_false_direct_identity_refuses(self):
        for field, value in [('grid_sha256', '0' * 64), ('grid_id', 'wrong'),
                             ('keeper_id', 'wrong'), ('life_id', 'wrong')]:
            with self.subTest(field=field):
                bundle = copy.deepcopy(self.bundle); care = payload(bundle)
                care['founder_contexts'][0][field] = value
                bundle['manifest']['sources'][1]['care_context'][field] = value
                bundle['manifest']['founder_occurrences'][0]['care_context'][field] = value
                rehash(bundle, care)
                with self.assertRaises(ValueError): self.store.validate_execution(bundle)

    def test_duplicate_source_ordinal_refuses(self):
        bundle = copy.deepcopy(self.bundle)
        bundle['manifest']['sources'].append(copy.deepcopy(bundle['manifest']['sources'][1]))
        with self.assertRaises(ValueError): self.store.validate_execution(bundle)

    def test_context_on_nonfounder_source_refuses(self):
        bundle = copy.deepcopy(self.bundle)
        bundle['manifest']['sources'][0]['care_context'] = payload(bundle)['founder_contexts'][0]
        with self.assertRaises(ValueError): self.store.validate_execution(bundle)

    def test_missing_source_or_context_presence_refuses(self):
        for change in (lambda b: b['manifest']['sources'].pop(),
                       lambda b: b['manifest']['sources'][1].pop('care_context'),
                       lambda b: b['manifest']['founder_occurrences'][0].pop('care_context')):
            bundle = copy.deepcopy(self.bundle); change(bundle)
            with self.assertRaises(ValueError): self.store.validate_execution(bundle)

    def test_context_without_immutable_input_refuses(self):
        bundle = copy.deepcopy(self.bundle)
        sha = bundle['manifest']['inputs'].pop('care_inputs_sha256'); del bundle['blobs'][sha]
        with self.assertRaises(ValueError): self.store.validate_execution(bundle)

    def test_consistently_malformed_context_refuses(self):
        changes = [lambda c: c.update(format='future'), lambda c: c.update(grid_sha256='bad'),
            lambda c: c.update(events_omitted=True),
            lambda c: c.update(life_id='outside-keeper:life-0'),
            lambda c: c.update(life_id='keeper:life-'),
            lambda c: c['care_summary']['keeper_actions'].update(idle=0),
            lambda c: c['care_summary'].update(beg_requests=1), lambda c: c.update(last_age_ticks=9),
            lambda c: c.update(outcome='dead'), lambda c: c.update(thread_state={}),
            lambda c: c['events'][0].update(begging=True),
            lambda c: c['care_summary'].update(ticks_observed=2)]
        for change in changes:
            with self.subTest(change=change):
                bundle = copy.deepcopy(self.bundle); care = payload(bundle)
                change(care['founder_contexts'][0])
                for row in (bundle['manifest']['sources'][1], bundle['manifest']['founder_occurrences'][0]):
                    row['care_context'] = copy.deepcopy(care['founder_contexts'][0])
                    row['life_id'] = care['founder_contexts'][0]['life_id']
                rehash(bundle, care)
                with self.assertRaises(ValueError): self.store.validate_execution(bundle)

    def test_null_context_is_explicit_and_round_trips(self):
        bundle = copy.deepcopy(self.bundle); care = payload(bundle)
        care['founder_contexts'][0] = None; rehash(bundle, care)
        for row in (bundle['manifest']['sources'][1], bundle['manifest']['founder_occurrences'][0]):
            row['care_context'] = None
        self.store.validate_execution(bundle)

    def test_chain_context_retains_ancestor_body_and_requires_provenance(self):
        bundle = copy.deepcopy(self.bundle)
        for row in (bundle['manifest']['sources'][1], bundle['manifest']['founder_occurrences'][0]):
            row.update(source_kind='era_elite', campaign_id='prior', era_index=0, niche_key='n0')
        care = payload(bundle); care['founder_contexts'][0]['grid_sha256'] = 'a' * 64
        care['founder_contexts'][0]['grid_id'] = 'ancestor'
        for row in (bundle['manifest']['sources'][1], bundle['manifest']['founder_occurrences'][0]):
            row['care_context'] = copy.deepcopy(care['founder_contexts'][0])
            row['care_context_origin'] = dict(founder_submission_index=0, context_sha256=legacy.digest(row['care_context']))
        rehash(bundle, care)
        self.store.validate_execution(bundle)
        bundle['manifest']['sources'][1].pop('niche_key')
        with self.assertRaises(ValueError): self.store.validate_execution(bundle)


    def test_care_report_binding_refuses_rehashed_fabricated_origin(self):
        changes = [lambda c: c.update(policy='observed_care_selection_v1'),
            lambda c: c['elite_origins'][0].update(founder_submission_index=1),
            lambda c: c.update(elite_origins=[]),
            lambda c: c['elite_origins'][0].update(context_sha256='a' * 64),
            lambda c: c['elite_contexts'][0].update(life_id='made-up-life')]
        for change in changes:
            with self.subTest(change=change):
                conn = self.store.open_ledger(':memory:')
                try:
                    self.store.record_campaign(conn, self.campaign)
                    bundle, era = copy.deepcopy(self.bundle), copy.deepcopy(self.era)
                    change(era['report']['care_selection'])
                    bundle['manifest']['report_sha256'] = legacy.digest(era['report'])
                    with self.assertRaises(ValueError):
                        self.store.record_era(conn, self.campaign['campaign_id'], era, self.profile, execution=bundle)
                    self.assertEqual(0, conn.execute('SELECT count(*) FROM eras').fetchone()[0])
                finally:
                    conn.close()

    def test_continuation_binds_exact_recorded_ancestor_slot_on_write_and_read(self):
        conn = self.store.open_ledger(':memory:'); self.addCleanup(conn.close)
        self.store.record_campaign(conn, self.campaign)
        self.store.record_era(conn, self.campaign['campaign_id'], self.era, self.profile, execution=self.bundle)
        bundle, era = copy.deepcopy(self.bundle), copy.deepcopy(self.era)
        bundle['manifest']['era_index'] = era['era_index'] = 1
        for row in (bundle['manifest']['sources'][1], bundle['manifest']['founder_occurrences'][0]):
            row.update(source_kind='era_elite', campaign_id=self.campaign['campaign_id'], era_index=0,
                niche_key='n0', care_context_origin=copy.deepcopy(self.era['report']['care_selection']['elite_origins'][0]))
        self.store.record_era(conn, self.campaign['campaign_id'], era, self.profile, execution=bundle)
        self.assertEqual(bundle, self.store.load_era_execution(conn, self.campaign['campaign_id'], 1))
        for field, value in [('niche_key', 'different'), ('source_position', 1), ('era_index', 2), ('campaign_id', 'missing')]:
            with self.subTest(field=field):
                broken = copy.deepcopy(bundle); later = copy.deepcopy(era)
                broken['manifest']['era_index'] = later['era_index'] = 2
                for row in (broken['manifest']['sources'][1], broken['manifest']['founder_occurrences'][0]):
                    row[field] = value
                with self.assertRaises(ValueError):
                    self.store.record_era(conn, self.campaign['campaign_id'], later, self.profile, execution=broken)
        conn.execute("UPDATE eras SET report_json='{}' WHERE era_index=0")
        with self.assertRaises(ValueError):
            self.store.load_era_execution(conn, self.campaign['campaign_id'], 1)


if __name__ == '__main__':
    unittest.main()
