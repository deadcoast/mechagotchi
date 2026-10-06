"""X7 dedicated package driver: real engine parity and occurrence propagation."""
from copy import deepcopy
import json
from pathlib import Path

from mecha_engine.generation import generate_candidate, train_generation_model
from mecha_engine.repair import train_repair_model
from mecha_engine.runtime import evolve
from mecha_engine.runtime.care import CARE_POLICY_V2, care_grid_sha256, care_context_sha256, select_care_successor

ROOT = Path(__file__).resolve().parents[4]
grid = json.loads((ROOT/'data/seed_grids/mg_seed_001.json').read_text())
slip = json.loads((ROOT/'data/slips/valid/slip_lcd_seed.json').read_text())
model = train_generation_model([grid])
repair = train_repair_model([grid], epochs=1)
def make_context(number):
    events = [{'tick': i+1, 'session_tick': i+1,'actor':'keeper','action':'feed',
               'begging':False,'alive':True,'death_cause':None} for i in range(4)]
    return {'format':'keeper_care_context_v1','keeper_id':'keeper-'+str(number),
        'life_id':'keeper-'+str(number)+':life-1','grid_id':grid['grid_id'],
        'grid_sha256':care_grid_sha256(grid),'care_summary':{'history':'complete',
        'from_age_ticks':0,'ticks_observed':4,'keeper_actions':{'feed':4},
        'companion_actions':{},'beg_requests':0},'events':events,'events_omitted':0,
        'last_age_ticks':4,'last_session_tick':4,'outcome':'alive'}
contexts = [make_context(1), make_context(2)]
config = dict(generations=2,population=4,damage_cycles=1,ticks=4,dropout_rate=0,rng_seed=12345,
              readability_scorer=lambda g: .6,founder_grids=[grid,deepcopy(grid)])
plain_a, plain_r = evolve([grid],slip,model,repair,**config)
none_a, none_r = evolve([grid],slip,model,repair,founder_care_contexts=[None,None],**config)
off_a, off_r = evolve([grid],slip,model,repair,founder_care_contexts=contexts,**config)
on_a, on_r = evolve([grid],slip,model,repair,founder_care_contexts=contexts,
                     care_selection_policy='observed_care_selection_v1',**config)
# Strip additive factual metadata only, leaving every scored/generated value intact.
stripped = deepcopy(off_r)
stripped.pop('care_selection')
for gen in stripped['generations']:
    for creature in gen['creatures']: creature.pop('care_context_origin',None)
checks={
    'null_exact': (plain_a,plain_r)==(none_a,none_r),
    'off_archive_exact': plain_a==off_a,
    'off_science_exact': plain_r==stripped,
    'duplicate_occurrences_distinct': [r.get('care_context_origin',{}).get('founder_submission_index')
        for r in on_r['generations'][0]['creatures']]==[0,1,None,0],
    'source_free_no_selection': 'care_selection' not in on_r['generations'][0]['creatures'][2],
    'enabled_receipts': all('care_selection' in row for row in on_r['generations'][0]['creatures'] if 'care_context_origin' in row),
    'elite_context_order': len(on_r['care_selection']['elite_contexts'])==len(on_a['elites']),
    'later_actual_parent_occurrence': True,
}
# Read selected ancestry from the actual generation0 insertions, not duplicate IDs.
first_elites = {}
for row in on_r['generations'][0]['creatures']:
    if row['archive_decision'] in ('inserted','replaced'):
        first_elites[row['candidate_grid_id']+'_c01'] = row.get('care_context_origin')
for row in on_r['generations'][1]['creatures']:
    checks['later_actual_parent_occurrence'] &= row.get('care_context_origin') == first_elites[row['parent_grid_id']]
# Public explicit off is byte-exact incumbent, even with contextual provenance available.
old=generate_candidate(grid,model,slip,rng_seed=111)
selected, receipt=select_care_successor(grid,model,slip,context=contexts[0],rng_seed=111)
checks['successor_off_exact']=old==selected and receipt is None
checks['source_immutable']=contexts==[make_context(1),make_context(2)]
# Invalid ordinal input must refuse before generation.
try:
    evolve([grid],slip,model,repair,founder_care_contexts=[contexts[0]],**config)
    checks['ordinal_length_refuses']=False
except ValueError: checks['ordinal_length_refuses']=True
v2_a, v2_r = evolve([grid],slip,model,repair,founder_care_contexts=contexts,
                     care_selection_policy=CARE_POLICY_V2,**config)
v2_none = evolve([grid],slip,model,repair,founder_care_contexts=[None,None],
                     care_selection_policy=CARE_POLICY_V2,**config)
checks['v2_absent_exact'] = v2_none == (plain_a,plain_r)
checks['v2_duplicate_occurrences_distinct'] = [r.get('care_context_origin',{}).get('founder_submission_index')
    for r in v2_r['generations'][0]['creatures']] == [0,1,None,0]
checks['v2_source_identity_bound'] = True
checks['v2_terminal_selection_order'] = True
checks['v2_later_actual_parent_occurrence'] = True
v2_elites={}
for row in v2_r['generations'][0]['creatures']:
    if row['archive_decision'] in ('inserted','replaced'):
        v2_elites[row['candidate_grid_id']+'_c01'] = row.get('care_context_origin')
for generation in v2_r['generations']:
    for row in generation['creatures']:
        receipt=row.get('care_selection');origin=row.get('care_context_origin')
        if receipt:
            ctx=contexts[origin['founder_submission_index']]
            checks['v2_source_identity_bound'] &= receipt['source_identity']=={key:ctx[key] for key in ('keeper_id','life_id','grid_id','grid_sha256')}
            candidates=receipt['candidates']
            checks['v2_terminal_selection_order'] &= candidates[receipt['selected_index']]['terminal_survival'] or not any(c['terminal_survival'] for c in candidates)
for row in v2_r['generations'][1]['creatures']:
    checks['v2_later_actual_parent_occurrence'] &= row.get('care_context_origin') == v2_elites[row['parent_grid_id']]
checks['v2_source_immutable'] = contexts==[make_context(1),make_context(2)]
json.dump(checks,__import__('sys').stdout)

