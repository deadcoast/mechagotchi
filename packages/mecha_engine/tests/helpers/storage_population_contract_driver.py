"""X8 passive storage acceptance; synthetic facts test integrity, never survival science."""
import base64
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import sqlite3
import tempfile
import unittest

import mecha_engine.storage as package_store
spec = importlib.util.spec_from_file_location('x8_care_fixture', Path(__file__).with_name('storage_care_contract_driver.py'))
care = importlib.util.module_from_spec(spec); spec.loader.exec_module(care)
legacy = care.legacy
POLICY = 'generation_survivors_v1'


def retain(bundle, value):
    data = json.dumps(value, separators=(',', ':'), allow_nan=False).encode()
    sha = hashlib.sha256(data).hexdigest()
    bundle['blobs'][sha] = dict(media_type='application/json', data_base64=base64.b64encode(data).decode())
    return sha


def population(bundle):
    return json.loads(base64.b64decode(bundle['blobs'][bundle['manifest']['inputs']['population_inputs_sha256']]['data_base64']))


def seal(era, bundle):
    m = bundle['manifest']
    if 'living_population' in era['report']:
        m['ordered_breeders_sha256'] = retain(bundle, era['report']['living_population']['final_breeders'])
    m['report_sha256'] = legacy.digest(era['report']); m['elites_sha256'] = legacy.digest(era['elites'])
    refs = {m['calibration_sha256'], *m['inputs']['founder_sha256']}
    refs.update(v for k,v in m['inputs'].items() if k.endswith('_sha256') and k != 'founder_sha256' and v is not None)
    refs.update(m[k] for k in ('ordered_elites_sha256','ordered_breeders_sha256') if k in m)
    refs.update(s['raw_sha256'] for s in m['sources'] if 'raw_sha256' in s)
    bundle['blobs'] = {key:value for key,value in bundle['blobs'].items() if key in refs}


def fixture(*, cared=False, empty=False):
    campaign, profile, era, bundle = care.fixture() if cared else legacy.fixture()
    m=bundle['manifest']; m['format']='mechagotchi_era_execution_v2'
    if not cared:
        m['sources'][0]['role']='documentary'
        for o in m['founder_occurrences']:
            m['sources'].append(dict(role='founder',founder_ordinal=o['ordinal'],source_kind=o['source_kind'],source_position=o['source_position']))
    options=dict(format='survival_population_inputs_v1',population_policy=POLICY,
        founder_start_mode='bootstrap',survival_regime='sheltered',cubff_density_pressure=False)
    m['inputs']['population_inputs_sha256']=retain(bundle,options)
    m['effective_config']=dict(generations=1,population=2,damage_cycles=1,ticks=3,dropout_rate=.2)
    ep=dict(survival_ticks=3,alive=True,death_cause=None,survival_ratio=1.0,need_balance=.7)
    report=era['report']; report.update(generations_requested=1,population=2,damage_cycles=1,ticks=3,dropout_rate=.2,seed_pool_size=2)
    contexts=care.payload(bundle)['founder_contexts'] if cared else []
    founder_grid=json.loads(base64.b64decode(bundle['blobs'][m['inputs']['founder_sha256'][0]]['data_base64']))
    parent=dict(kind='submitted_founder',submission_index=0,grid_id=founder_grid['grid_id'],grid_sha256=legacy.digest(founder_grid))
    breeders=[]; creatures=[]
    for index in range(2):
        grid={'grid_id':'same-offspring_c01','cells':[{'y':0,'x':index}]}
        ctx=contexts[0] if cared else None
        origin=dict(founder_submission_index=0,context_sha256=legacy.digest(ctx)) if cared else None
        breeder=dict(generation_index=0,candidate_index=index,grid_id=grid['grid_id'],grid=grid,
            grid_sha256=legacy.digest(grid),fitness=.5+index/10,learned_readability=.4,
            care_context=copy.deepcopy(ctx),care_context_origin=copy.deepcopy(origin))
        end=copy.deepcopy(ep)
        if empty: end.update(alive=False,death_cause='starvation')
        row=dict(parent_grid_id=parent['grid_id'],candidate_grid_id='same-offspring',stages=dict(candidate_valid=True,all_cycles_valid=True,all_cycles_aligned=True,scored=True),
            cycles=[dict(cycle=1,valid=True,aligned=True,episode=copy.deepcopy(ep))],
            score={'fitness':breeder['fitness']},archive_decision='kept_incumbent',
            breeding=dict(occurrence=dict(generation_index=0,candidate_index=index),
                parent_occurrence=copy.deepcopy(parent),candidate_grid_sha256=legacy.digest(grid),
                final_grid_sha256=legacy.digest(grid),cycles_requested=1,cycles_attempted=1,cycles_qualified=1,
                final_episode=end,eligible=not empty,
                stop=dict(stage='final_episode',cycle_index=None,reason='lifecycle_death') if empty else None))
        if origin is not None: row['care_context_origin']=copy.deepcopy(origin)
        creatures.append(row)
        if not empty: breeders.append(breeder)
    report['generations']=[dict(generation=0,creatures=creatures)]
    report['living_population']=dict(format=POLICY,population_policy=POLICY,founder_start_mode='bootstrap',
        survival_regime='sheltered',initial_parent_occurrences=[parent]+[dict(kind='seed_corpus',source_position=i,grid_id=g['grid_id'],grid_sha256=legacy.digest(g)) for i,g in enumerate(json.loads(base64.b64decode(bundle['blobs'][m['inputs']['seed_corpus_sha256']]['data_base64'])))],requested_candidate_slots=2,evaluated_candidates=2,
        unexecuted_candidate_slots=0,final_breeders=breeders,termination=dict(ended=empty,
            reason='no_eligible_breeders' if empty else 'requested_horizon_complete',generation_index=0,
            lifecycle_deaths=2 if empty else 0,structural_disqualifications=0,genuine_lifecycle_extinction=empty))
    era['went_extinct']=empty
    seal(era,bundle)
    return campaign,profile,era,bundle


def continuation(prior_era, prior_bundle, *, cared=False):
    _,_,era,bundle=fixture(cared=cared)
    m=bundle['manifest']; m['era_index']=era['era_index']=1
    options=population(bundle); options['founder_start_mode']='continue'
    m['inputs']['population_inputs_sha256']=retain(bundle,options)
    breeders=prior_era['report']['living_population']['final_breeders']
    sources=[row for row in m['sources'] if row['role']!='founder']
    occurrences=[]; refs=[]; contexts=[]
    for index,row in enumerate(breeders):
        sha=retain(bundle,row['grid']); refs.append(sha)
        source=dict(role='founder',founder_ordinal=index,source_kind='era_breeder',source_position=index,
            campaign_id=m['campaign_id'],era_index=0,generation_index=row['generation_index'],candidate_index=row['candidate_index'],
            grid_sha256=row['grid_sha256'])
        ctx=row['care_context']; contexts.append(copy.deepcopy(ctx))
        if ctx is not None: source.update(care_context=copy.deepcopy(ctx),care_context_origin=copy.deepcopy(row['care_context_origin']))
        sources.append(source)
        occurrence={k:copy.deepcopy(v) for k,v in source.items() if k not in ('role','founder_ordinal')}
        occurrence.update(ordinal=index,grid_id=row['grid_id'],grid_sha256=sha,admitted=True,rejection_errors=None)
        occurrences.append(occurrence)
    m['sources']=sources; m['founder_occurrences']=occurrences;m['inputs']['founder_sha256']=refs
    if cared:
        payload=care.payload(bundle);payload['founder_contexts']=contexts;care.rehash(bundle,payload)
        era['report']['care_selection']['founder_contexts']=copy.deepcopy(contexts)
    era['report']['founders']=dict(admitted_ids=[r['grid_id'] for r in breeders],rejected=[])
    era['report']['living_population']['founder_start_mode']='continue'
    initial=[dict(kind='submitted_founder',submission_index=i,grid_id=r['grid_id'],grid_sha256=r['grid_sha256']) for i,r in enumerate(breeders)]
    era['report']['living_population']['initial_parent_occurrences']=initial
    for creature in era['report']['generations'][0]['creatures']:
        if initial:
            creature['breeding']['parent_occurrence']=copy.deepcopy(initial[0]);creature['parent_grid_id']=initial[0]['grid_id']
    seal(era,bundle)
    return era,bundle


class StoragePopulationTests(unittest.TestCase):
    store=package_store
    def setUp(self):
        self.campaign,self.profile,self.era,self.bundle=fixture()
        self.conn=self.store.open_ledger(':memory:');self.addCleanup(self.conn.close)
        self.store.record_campaign(self.conn,self.campaign)
    def record(self,era=None,bundle=None):
        self.store.record_era(self.conn,self.campaign['campaign_id'],self.era if era is None else era,
            self.profile,execution=self.bundle if bundle is None else bundle)
    def test_roundtrip_breeders_separate_from_archive_and_nonmutating(self):
        before=copy.deepcopy(self.bundle);self.record()
        result=self.store.load_era_breeders(self.conn,self.campaign['campaign_id'],0)
        self.assertEqual(self.era['report']['living_population']['final_breeders'],result)
        self.assertEqual(before,self.bundle)
        self.assertEqual(2,len(result));self.assertEqual(result[0]['grid_id'],result[1]['grid_id'])
        self.assertEqual([e['grid'] for e in self.era['elites']],self.store.load_founder_pool(self.conn,self.campaign['campaign_id']))
        result.clear();self.assertEqual(2,len(self.store.load_era_breeders(self.conn,self.campaign['campaign_id'],0)))
    def test_legacy_absence_is_none(self):
        campaign,profile,era,bundle=legacy.fixture()
        self.store.record_era(self.conn,campaign['campaign_id'],era,profile,execution=bundle)
        self.assertIsNone(self.store.load_era_breeders(self.conn,campaign['campaign_id'],0))
        self.assertIsNone(self.store.load_era_breeders(self.conn,'missing',0))
    def test_verified_empty_keeps_historical_archive(self):
        _,_,era,bundle=fixture(empty=True);self.record(era,bundle)
        self.assertEqual([],self.store.load_era_breeders(self.conn,self.campaign['campaign_id'],0))
        self.assertEqual(era['elites'],self.store.load_era_elites(self.conn,self.campaign['campaign_id'],0))
    def test_missing_output_or_input_and_unknown_policy_refuse(self):
        changes=[lambda b:b['manifest'].pop('ordered_breeders_sha256'),
                 lambda b:b['manifest']['inputs'].pop('population_inputs_sha256'),
                 lambda b:b['manifest'].update(format='mechagotchi_era_execution_v1')]
        for change in changes:
            bad=copy.deepcopy(self.bundle);change(bad)
            with self.assertRaises(ValueError):self.store.validate_execution(bad)
        for key,value in [('population_policy','future'),('founder_start_mode',None),('cubff_density_pressure',1),('survival_regime','tiny')]:
            bad=copy.deepcopy(self.bundle);p=population(bad);p[key]=value
            bad['manifest']['inputs']['population_inputs_sha256']=retain(bad,p);seal(self.era,bad)
            with self.assertRaises(ValueError):self.store.validate_execution(bad)
    def test_terminal_endpoint_and_eligibility_corruption_refuse(self):
        changes=[lambda r:r['breeding']['final_episode'].update(alive=False,death_cause='starvation'),
            lambda r:r['breeding'].update(final_episode=None),lambda r:r['breeding'].update(stop=dict(stage='repair',cycle_index=1,reason='invalid_repair')),lambda r:r['breeding'].update(cycles_attempted=0),
            lambda r:r['breeding'].update(eligible=False),lambda r:r['breeding'].update(final_grid_sha256='a'*64),
            lambda r:r['cycles'][0]['episode'].update(alive=False,death_cause='starvation'),
            lambda r:r['cycles'][0]['episode'].update(survival_ticks=2),lambda r:r['cycles'][0].update(valid=False),
            lambda r:r['breeding']['final_episode'].update(alive=1),lambda r:r['stages'].update(candidate_valid=False)]
        for change in changes:
            era,bundle=copy.deepcopy(self.era),copy.deepcopy(self.bundle);change(era['report']['generations'][0]['creatures'][0]);seal(era,bundle)
            with self.assertRaises(ValueError):self.record(era,bundle)
            self.assertEqual(0,self.conn.execute('SELECT count(*) FROM eras').fetchone()[0])
    def test_rehashed_breeder_order_body_fitness_and_membership_refuse(self):
        for change in [lambda b:b.reverse(),lambda b:b[0]['grid']['cells'][0].update(x=99),
            lambda b:b[0].update(fitness=1),lambda b:b.pop(),lambda b:b[1].update(candidate_index=0),
            lambda b:b[0].update(care_context_origin={})]:
            era,bundle=copy.deepcopy(self.era),copy.deepcopy(self.bundle);change(era['report']['living_population']['final_breeders']);seal(era,bundle)
            with self.assertRaises(ValueError):self.record(era,bundle)
    def test_new_population_requires_immutable_execution(self):
        with self.assertRaises(ValueError):
            self.store.record_era(self.conn,self.campaign['campaign_id'],self.era,self.profile)
    def test_continuation_complete_prior_tail_even_without_care(self):
        self.record();era,bundle=continuation(self.era,self.bundle);self.record(era,bundle)
        self.assertEqual(bundle,self.store.load_era_execution(self.conn,self.campaign['campaign_id'],1))
        self.assertEqual(0,self.conn.execute('SELECT count(*) FROM founders').fetchone()[0])
    def test_omitted_duplicate_out_of_order_or_wrong_prior_tail_refuse(self):
        self.record()
        for change in [lambda s:s.update(source_position=1),lambda s:s.update(generation_index=1),
                       lambda s:s.update(era_index=1),lambda s:s.update(campaign_id='different'),
                       lambda s:s.update(grid_sha256='a'*64)]:
            era,bundle=continuation(self.era,self.bundle);source=bundle['manifest']['sources'][1];change(source)
            for key,value in source.items():
                if key not in ('role','founder_ordinal','grid_sha256'):bundle['manifest']['founder_occurrences'][0][key]=value
            seal(era,bundle)
            with self.assertRaises(ValueError):self.record(era,bundle)
        era,bundle=continuation(self.era,self.bundle)
        bundle['manifest']['sources'].pop();bundle['manifest']['founder_occurrences'].pop();bundle['manifest']['inputs']['founder_sha256'].pop()
        era['report']['founders']['admitted_ids'].pop();seal(era,bundle)
        with self.assertRaises(ValueError):self.record(era,bundle)
    def test_bootstrap_cannot_claim_breeder_ancestry(self):
        self.record();era,bundle=continuation(self.era,self.bundle)
        options=population(bundle);options['founder_start_mode']='bootstrap'
        bundle['manifest']['inputs']['population_inputs_sha256']=retain(bundle,options)
        era['report']['living_population']['founder_start_mode']='bootstrap';seal(era,bundle)
        with self.assertRaises(ValueError):self.record(era,bundle)
    def test_cared_breeder_continuation_checks_same_occurrence(self):
        _,_,era,bundle=fixture(cared=True);self.record(era,bundle)
        later,continuing=continuation(era,bundle,cared=True);self.record(later,continuing)
        self.assertEqual(continuing,self.store.load_era_execution(self.conn,self.campaign['campaign_id'],1))
    def test_corrupted_output_blob_and_missing_execution_refuse_on_read(self):
        self.record();sha=self.bundle['manifest']['ordered_breeders_sha256']
        self.conn.execute('UPDATE execution_blobs SET payload=? WHERE sha256=?',(b'[]',sha))
        with self.assertRaises(ValueError):self.store.load_era_breeders(self.conn,self.campaign['campaign_id'],0)
        self.conn.execute('DELETE FROM era_executions');self.conn.execute('DELETE FROM founder_occurrences')
        with self.assertRaises(ValueError):self.store.load_era_breeders(self.conn,self.campaign['campaign_id'],0)
    def test_legacy_extended_options_have_no_breeder_output(self):
        _,_,era,bundle=legacy.fixture();m=bundle['manifest'];m['format']='mechagotchi_era_execution_v2'
        m['inputs']['population_inputs_sha256']=retain(bundle,dict(format='survival_population_inputs_v1',population_policy='legacy_archive',
            founder_start_mode='bootstrap',survival_regime='stress_probe',cubff_density_pressure=False))
        era['report']['survival_regime']='stress_probe';seal(era,bundle)
        self.record(era,bundle);self.assertIsNone(self.store.load_era_breeders(self.conn,self.campaign['campaign_id'],0))
    def test_unique_release_projection_required_and_exact_on_read(self):
        era,bundle=copy.deepcopy(self.era),copy.deepcopy(self.bundle)
        m=bundle['manifest'];old=m['inputs']['founder_sha256'][1]
        grid=json.loads(base64.b64decode(bundle['blobs'][old]['data_base64']));grid['grid_id']='other-rejected'
        sha=retain(bundle,grid);m['inputs']['founder_sha256'][1]=sha
        m['founder_occurrences'][1].update(grid_id=grid['grid_id'],grid_sha256=sha)
        era['report']['founders']['rejected'][0]['grid_id']=grid['grid_id'];seal(era,bundle)
        with self.assertRaises(ValueError):self.record(era,bundle)
        founders=[dict(grid_id=o['grid_id'],source='workshop_release',admitted=o['admitted'],rejection_errors=o['rejection_errors'],
            grid=json.loads(base64.b64decode(bundle['blobs'][o['grid_sha256']]['data_base64']))) for o in m['founder_occurrences']]
        self.store.record_era(self.conn,self.campaign['campaign_id'],era,self.profile,founders=founders,execution=bundle)
        self.assertEqual(bundle,self.store.load_era_execution(self.conn,self.campaign['campaign_id'],0))
        self.conn.execute("UPDATE founders SET source='era_elite'")
        with self.assertRaises(ValueError):self.store.load_era_execution(self.conn,self.campaign['campaign_id'],0)

    def test_rehashed_initial_parent_identity_and_invented_seed_refuse(self):
        for change in [lambda p:p.clear(),lambda p:p[0].update(grid_sha256='a'*64),
                       lambda p:p[0].update(submission_index=1),lambda p:p.append(copy.deepcopy(p[0]))]:
            era,bundle=copy.deepcopy(self.era),copy.deepcopy(self.bundle)
            change(era['report']['living_population']['initial_parent_occurrences']);seal(era,bundle)
            with self.assertRaises(ValueError):self.record(era,bundle)

    def test_extinct_predecessor_cannot_be_reopened_with_new_era(self):
        _,_,era,bundle=fixture(empty=True);self.record(era,bundle)
        later,continued=continuation(era,bundle)
        with self.assertRaises(ValueError):self.record(later,continued)

    def test_bootstrap_is_only_valid_at_new_campaign_era_zero(self):
        era,bundle=copy.deepcopy(self.era),copy.deepcopy(self.bundle)
        era['era_index']=bundle['manifest']['era_index']=1
        with self.assertRaises(ValueError):self.record(era,bundle)

    def test_erased_generations_cannot_claim_no_initial_population(self):
        era,bundle=copy.deepcopy(self.era),copy.deepcopy(self.bundle)
        era['report']['generations']=[]
        living=era['report']['living_population'];living.update(final_breeders=[],evaluated_candidates=0,unexecuted_candidate_slots=2)
        living['termination']=dict(ended=True,reason='all_founders_rejected',generation_index=None,
            lifecycle_deaths=0,structural_disqualifications=0,genuine_lifecycle_extinction=False)
        era['went_extinct']=True;seal(era,bundle)
        with self.assertRaises(ValueError):self.record(era,bundle)

    def test_parent_display_identity_is_bound_to_source_occurrence(self):
        era,bundle=copy.deepcopy(self.era),copy.deepcopy(self.bundle)
        era['report']['generations'][0]['creatures'][0]['parent_grid_id']='forged-display';seal(era,bundle)
        with self.assertRaises(ValueError):self.record(era,bundle)

    def test_prior_parent_identity_cannot_be_relabelled_with_same_hash(self):
        era,bundle=copy.deepcopy(self.era),copy.deepcopy(self.bundle);report=era['report']
        second=copy.deepcopy(report['generations'][0]);second['generation']=1
        prior=report['living_population']['final_breeders'][0]
        for creature in second['creatures']:
            creature['breeding']['occurrence']['generation_index']=1
            creature['breeding']['parent_occurrence']=dict(kind='generation_breeder',generation_index=0,candidate_index=0,
                grid_id='forged-display',grid_sha256=prior['grid_sha256'])
            creature['parent_grid_id']='forged-display'
        report['generations'].append(second);report['generations_requested']=2;bundle['manifest']['effective_config']['generations']=2
        living=report['living_population'];living.update(requested_candidate_slots=4,evaluated_candidates=4)
        living['termination']['generation_index']=1
        for breeder in living['final_breeders']:breeder['generation_index']=1
        seal(era,bundle)
        with self.assertRaises(ValueError):self.record(era,bundle)

    def test_stopped_candidate_aggregate_cycle_flags_match_actual_cycles(self):
        for key in ('all_cycles_valid','all_cycles_aligned'):
            _,_,era,bundle=fixture(empty=True)
            era['report']['generations'][0]['creatures'][0]['stages'][key]=False;seal(era,bundle)
            with self.assertRaises(ValueError):self.record(era,bundle)

    def test_bootstrap_cannot_erase_seed_cohort_and_all_evaluations(self):
        era,bundle=copy.deepcopy(self.era),copy.deepcopy(self.bundle);m=bundle['manifest']
        m['inputs']['founder_sha256']=[];m['founder_occurrences']=[]
        m['sources']=[s for s in m['sources'] if s['role']!='founder']
        era['report']['founders']=dict(admitted_ids=[],rejected=[]);era['report']['generations']=[]
        living=era['report']['living_population'];living.update(initial_parent_occurrences=[],final_breeders=[],evaluated_candidates=0,unexecuted_candidate_slots=2)
        living['termination']=dict(ended=True,reason='empty_continuation',generation_index=None,
            lifecycle_deaths=0,structural_disqualifications=0,genuine_lifecycle_extinction=False)
        era['went_extinct']=True;seal(era,bundle)
        with self.assertRaises(ValueError):self.record(era,bundle)

    def test_readonly_breeder_loader_has_no_side_effects(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/'ledger.sqlite';conn=self.store.open_ledger(path)
            try:
                self.store.record_campaign(conn,self.campaign);self.store.record_era(conn,self.campaign['campaign_id'],self.era,self.profile,execution=self.bundle)
            finally:conn.close()
            before=path.read_bytes();conn=sqlite3.connect(path.as_uri()+'?mode=ro',uri=True)
            try:self.assertEqual(2,len(self.store.load_era_breeders(conn,self.campaign['campaign_id'],0)))
            finally:conn.close()
            self.assertEqual(before,path.read_bytes())

if __name__=='__main__':unittest.main()
