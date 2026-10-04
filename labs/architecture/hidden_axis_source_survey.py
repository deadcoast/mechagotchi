"""Q4 / DR 0065: bounded source survey; no hidden display or adoption.

Preregistered in docs/development/q4-hidden-axes-controls.md. Probe budgets
are diagnostic only: two generations/two candidates, one damage cycle,
three ticks, two repair epochs, default runtime seed and dropout. No quality
or survival claim is inferred from this small call-surface census.
"""
import argparse
from functools import lru_cache
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[2]
HIDDEN_AXES=('mutation pressure','lineage fitness','novelty decay','attachment score','user response confidence','profile alignment')
VISIBLE=('hunger','happiness','energy','cleanliness','mood','age','health','bond')
PROBE_TIMEOUT_S=120

PROBE=r"""
import copy,json,sys
from pathlib import Path
from mecha_engine.lifecycle import initial_state,advance_tick
from mecha_engine.learning import fleet_signals,observe_fleet,decide
from mecha_engine.generation import train_generation_model
from mecha_engine.repair import train_repair_model
from mecha_engine.runtime import evolve,learned_readability_score
from mecha_engine.slip import is_grid_aligned
root=Path(sys.argv[1])
def read(path): return json.loads((root/path).read_text(encoding='utf-8'))
grid=read('data/seed_grids_16x16/mg_seed16_001_beetle.json')
slip=read('data/slips/valid/slip_lcd_seed.json')
readability=read('data/readability_benchmark/adopted_readability_model.json')
original=json.dumps([grid,slip],sort_keys=True)
base=initial_state(grid,slip)
off=fleet_signals(base)
def signals(actions):
    state=initial_state(grid,slip)
    state['learning_switches']={'boredom_novelty':True,'attention_forecast':True}
    cold={t['name']:t for t in fleet_signals(state)}
    for action in actions:
        state=advance_tick(state,action)
        state['thread_states']=observe_fleet(state)
    return cold,{t['name']:t for t in fleet_signals(state)},state
cold,repeated,repeated_state=signals(['idle']*6)
_,varied,varied_state=signals(['play','feed','sleep']*2)
model=train_generation_model([grid])
repair=train_repair_model([grid],epochs=2)
def scorer(candidate): return learned_readability_score(candidate,readability)
kwargs=dict(readability_scorer=scorer,generations=2,population=2,damage_cycles=1,ticks=3)
archive,off_report=evolve([grid],slip,model,repair,**kwargs)
records=read('data/cubff_real_ingest/callback_states/callback_states_compact.json')['records']
_,on_report=evolve([grid],slip,model,repair,cubff_pressure_source=[records[0],records[-1]],**kwargs)
invalid=copy.deepcopy(grid); invalid['palette']['palette_id']='not_in_this_covenant'
aligned=is_grid_aligned(grid,slip); misaligned=is_grid_aligned(invalid,slip)
assert original==json.dumps([grid,slip],sort_keys=True),'Probe mutated source inputs.'
print(json.dumps({'state_keys':sorted(base),'bond':base['bond'],
    'fleet_off':off,'novelty_cold':cold['boredom_novelty'],
    'novelty_repeat':repeated['boredom_novelty'],'novelty_varied':varied['boredom_novelty'],
    'attention_cold':cold['attention_forecast'],'attention_warm':varied['attention_forecast'],
    'recent_interaction_thread':next(t for t in decide(varied_state)['threads'] if t['name']=='recent_interaction_ewma'),
    'pressure_off_keys':sorted(off_report),'pressure_on':on_report['cubff_pressure']['by_generation'],
    'candidate_fitness':[c['score']['fitness'] for g in off_report['generations'] for c in g['creatures']],
    'generation_mean_fitness':off_report['summary']['mean_fitness_by_generation'],
    'archive_elite_keys':sorted(next(iter(archive['elites'].values()))) if archive['elites'] else [],
    'alignment_valid':{'ok':aligned.ok,'errors':aligned.errors},
    'alignment_invalid':{'ok':misaligned.ok,'errors':misaligned.errors},
    'source_inputs_unchanged':True}))
"""

def check_visible_instrument(observed,committed):
    if observed!=committed:
        raise ValueError('Committed visible-axis instrument mismatch; refuse the hidden survey.')
    return True

@lru_cache(maxsize=1)
def _observations():
    sys.path.insert(0,str(ROOT/'game'))
    sys.path.insert(0,str(ROOT/'game/src'))
    sys.path.insert(0,str(ROOT/'packages/mecha_engine/src'))
    from evidence import build_companion_axis_split_report
    observed=build_companion_axis_split_report()['metrics']['axes']
    committed=json.loads((ROOT/'data/game_client/companion_axis_split_stage0.json').read_text(encoding='utf-8'))['metrics']['axes']
    visible_observed={k:observed[k] for k in VISIBLE}
    visible_committed={k:committed[k] for k in VISIBLE}
    check_visible_instrument(visible_observed,visible_committed)
    env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',PYTHONIOENCODING='utf-8')
    # A child with only the package source on PYTHONPATH cannot consume a lab mirror.
    env['PYTHONPATH']=str(ROOT/'packages/mecha_engine/src')
    result=subprocess.run([sys.executable,'-B','-c',PROBE,str(ROOT)],cwd=ROOT,env=env,
                          capture_output=True,text=True,encoding='utf-8',timeout=PROBE_TIMEOUT_S)
    if result.returncode:
        raise RuntimeError(f'Package source probe failed; no findings recorded:\n{result.stderr}')
    return visible_observed,visible_committed,json.loads(result.stdout)

def build_report():
    observed,committed,probe=_observations()
    def derived(source,value,cause,scope):
        return {'disposition':'derived_engine_value','source':source,'value':value,'cause':cause,'scope':scope}
    def absent(cause,related):
        return {'disposition':'absent','source':None,'value':None,'cause':cause,'scope':'Reviewed promoted surfaces and observed records; not a proof about future implementations.','related_observation':related}
    axes={
      'mutation pressure':derived('mecha_engine.runtime.evolve -> report.cubff_pressure.by_generation[*].mutation_pressure',
          [r['mutation_pressure'] for r in probe['pressure_on']],
          'The runtime derives pressure from supplied CuBFF snapshots and reports it only when that seam is active.',
          'Generation/environment signal; absent from the off report and companion lifecycle state.'),
      'lineage fitness':absent('Candidate fitness and generation mean fitness exist, but neither is a dedicated lineage-aggregated fitness definition. No lineage fitness is manufactured from ancestry or candidate scores.',
          {'candidate_fitness':probe['candidate_fitness'],'generation_mean_fitness':probe['generation_mean_fitness'],'elite_record_keys':probe['archive_elite_keys']}),
      'novelty decay':derived('mecha_engine.learning.fleet_signals -> boredom_novelty.output.boredom',
          {'repeat':probe['novelty_repeat']['output'],'varied':probe['novelty_varied']['output']},
          'The existing thread explicitly describes novelty decay over the action stream and derives boredom from distinct actions in its bounded window. Its repeat learner uses decayed counts.',
          'Opt-in thread, cold start has no boredom value; this is its existing signal, not a new scalar called novelty_decay or a default-roster promotion.'),
      'attachment score':absent('The lifecycle carries bond, already a separate documented visible axis. No independent attachment definition or attachment score is exported; renaming bond would assert an unchosen synonym.',
          {'bond':probe['bond']}),
      'user response confidence':derived('mecha_engine.learning.fleet_signals -> attention_forecast.confidence',
          {'confidence':probe['attention_warm']['confidence'],'output':probe['attention_warm']['output']},
          'The existing attention-hazard thread returns confidence beside predicted interaction probability; these are distinct values. The reactive attention thread has a separate history-count confidence.',
          'An opt-in prediction-specific source candidate, not calibrated human confidence and not an adopted canonical definition for the prose axis.'),
      'profile alignment':derived('mecha_engine.slip.is_grid_aligned(grid, slip_profile)',
          {'valid':probe['alignment_valid'],'invalid':probe['alignment_invalid']},
          'The promoted authority computes a constraint verdict and reasons. Archive scoring also records alignment; a Boolean covenant verdict is not a continuous similarity score.',
          'Explicit grid/covenant pair; no new companion state field.')}
    return {'artifact_id':'hidden_axis_source_survey_stage0','status':'measured','date':'2026-10-04',
      'purpose':'Survey six unsurfaced hidden-axis source candidates through promoted APIs without inventing definitions or displays.',
      'source_artifacts':['docs/development/q4-hidden-axes-controls.md','docs/project-research/validity-research.md','data/game_client/companion_axis_split_stage0.json',
        'data/seed_grids_16x16/mg_seed16_001_beetle.json','data/slips/valid/slip_lcd_seed.json','data/cubff_real_ingest/callback_states/callback_states_compact.json',
        'packages/mecha_engine/src/mecha_engine/runtime/evolve.py','packages/mecha_engine/src/mecha_engine/learning/threads.py','packages/mecha_engine/src/mecha_engine/archive/scoring.py','packages/mecha_engine/src/mecha_engine/slip/authority.py'],
      'parameters':{'generations':2,'population':2,'damage_cycles':1,'ticks':3,'repair_epochs':2,'runtime_seed':20260512,'runtime_dropout':0.2,'action_probe_ticks':6,'measurement':'Bounded source/availability census; no quality or survival inference.'},
      'instrument':{'observed_visible_axes':observed,'committed_visible_axes':committed},
      'metrics':{'visible_instrument_reproduced':True,'axes':axes,'probe':probe},
      'closed_states':['six_hidden_source_dispositions','historical_visible_instrument_reproduced','off_cold_warm_and_negative_alignment_observed'],
      'blocked_states':['dedicated_lineage_fitness_definition_absent','independent_attachment_definition_absent','attention_axis_canonical_definition_not_adopted','human_calibration_unmeasured','hidden_axes_not_displayed','native_remote_ci_unverified'],
      'decision':{'verdict':'survey_only_no_adoption','counts':{'field':0,'derived_engine_value':4,'absent':2},'scope':'Four existing source candidates with explicit bounds; two absent dedicated definitions. No engine or UI number is created.'},
      'next_research_step':'Q5 consolidate Phase Q; future definitions require their own gates, never silent aliases.'}

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,default=ROOT/'data/architecture/hidden_axis_source_survey_stage0.json')
    args=parser.parse_args()
    report=build_report()
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps(report['decision'],indent=2))
