"""Read-only product/source audit probes; no repository writes or source copies."""
import copy
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(r'C:\Users\ryanf\github\_shelved\mechagotchi')
sys.path[:0] = [str(ROOT/'packages/mecha_engine/src'), str(ROOT/'game/src')]
from mecha_engine.generation import train_generation_model, generate_candidate
from mecha_engine.genome import validate_grid
from mecha_engine.slip import is_grid_aligned
from mecha_game.session import CompanionSession
from mecha_game.app import _footer_lines

def digest(value):
    return hashlib.sha256(json.dumps(value,sort_keys=True).encode()).hexdigest()

p=json.loads((ROOT/'data/slips/valid/slip_v2_cleanliness.json').read_text(encoding='utf-8'))
gs=[json.loads(f.read_text(encoding='utf-8')) for f in sorted((ROOT/'data/seed_grids').glob('mg_seed_*.json'))]
gs=[g for g in gs if is_grid_aligned(g,p).ok]
report={'format':'checkpoint_source_review_diagnostic_v1','head':'d4b4337d0dacbdfa816d990297c03a5da2d0cdca',
        'python':sys.version,'profile_id':p['profile_id'],'profile_sha256':digest(p),
        'evidence_limits':['Read-only in-memory probes, not preregistered science/adoption gates.',
                           'No default, artifact, source, save or scientific claim changed.',
                           'Lock semantics are not fully defined by the schema; measured behavior is factual, normative gap needs a decision record.',
                           'Matched lifecycle trajectories do not refute measured morphology/survival archive selection.']}
trajectories=[]
for g in gs:
    s=CompanionSession(g,p,model=train_generation_model([g]))
    rows=[]
    for i in range(25):
        if not s.alive: break
        st=s.advance('feed' if s.state['hunger']>.6 else 'play' if i%9==0 else None)
        rows.append({k:st[k] for k in ('age_ticks','hunger','energy','stress','bond','grid_stability','alive')})
    trajectories.append({'grid_id':g['grid_id'],'input_sha256':digest(g),
                         'trajectory_sha256':digest(rows),'rows':rows})
report['same_covenant_trajectories']={'aligned_seed_count':len(gs),'distinct_need_trajectories':len({x['trajectory_sha256'] for x in trajectories}),
                                    'keeper_rule':'feed if hunger>.6 else play when index%9==0 else autonomous; at most25 ticks','results':trajectories}
g=copy.deepcopy(gs[0]); q=copy.deepcopy(p)
q['grid']['allowed_palettes']=['lcd_green','gameboy_gray']
for k in g['mutation']: g['mutation'][k]=0.0
for k in q['mutation']: q['mutation'][k]=0.0
for c in g['cells']: c['locked']=True
model=train_generation_model([g]); observations=[]
for seed in range(10):
    child=generate_candidate(g,model,q,rng_seed=seed)
    observations.append({'seed':seed,'output_sha256':digest(child),'output_valid':validate_grid(child).ok,
        'output_aligned':is_grid_aligned(child,q).ok,'palette_changed':child['palette']['palette_id']!=g['palette']['palette_id'],
        'locked_cells_retained':sum(x['locked'] for x in child['cells']),'parent_locked_cells':len(g['cells']),
        'mutation':child['mutation'],'anchor_changed':[(x['x'],x['y']) for x in child['cells'] if x['animation_anchor']] != [(x['x'],x['y']) for x in g['cells'] if x['animation_anchor']],
        'generation_trace':child['metadata']['generation_trace']})
report['zero_caps_locked_parent']={'parent_id':g['grid_id'],'parent_sha256':digest(g),'parent':g,'profile':q,
    'parent_valid':validate_grid(g).ok,'parent_aligned':is_grid_aligned(g,q).ok,'results':observations}
outcomes=[]
for treatment in ('neglect','feed_first_15'):
    s=CompanionSession(gs[0],p,model=train_generation_model([gs[0]]))
    for i in range(500):
        if not s.alive: break
        s.advance('feed' if treatment=='feed_first_15' and i<15 else 'idle')
    parent_summary={'age':s.state['age_ticks'],'death_cause':s.death_cause,'action_counts':s.state['action_counts'],'lineage':copy.deepcopy(s.lineage)}
    if s.alive: raise RuntimeError('probe unexpectedly did not die')
    s.succeed()
    outcomes.append({'treatment':treatment,'parent_outcome':parent_summary,'child_sha256':digest(s.grid),'child_id':s.grid['grid_id']})
report['care_to_succession']={'results':outcomes,'identical_child':outcomes[0]['child_sha256']==outcomes[1]['child_sha256']}
tp=copy.deepcopy(p);tp['deliberation']={'max_ticks':4,'confidence_threshold':.95}
s=CompanionSession(gs[0],tp,model=train_generation_model([gs[0]]))
thoughts=[]
for i in range(20):
    if not s.alive:break
    s.advance('feed' if s.state['hunger']>.65 else None)
    thought=s.log[-1].get('thought')
    if thought:
        snap=s.snapshot()
        thoughts.append({'tick':s.state['age_ticks'],'thought':thought,'footer':_footer_lines(snap,None),'ui_hints':snap['ui_hints']})
report['ctm_trace_vs_footer']={'profile':tp,'records':thoughts}
print(json.dumps(report,indent=2))
