"""Package-only operational X8 probes; no scientific cohort execution."""
from copy import deepcopy
import json
from pathlib import Path
from unittest.mock import patch
from mecha_engine.runtime import evolve,live_cycle
from mecha_engine.runtime import _survival_population as implementation
from mecha_engine.generation import train_generation_model
from mecha_engine.repair import train_repair_model
ROOT=Path(__file__).resolve().parents[4]
grid=json.loads((ROOT/'data/seed_grids/mg_seed_001.json').read_text())
slip=json.loads((ROOT/'data/slips/valid/slip_lcd_seed.json').read_text())
model=train_generation_model([grid]);repair=train_repair_model([grid],epochs=2,rng_seed=1)
args=dict(readability_scorer=lambda g:.5,generations=2,population=2,damage_cycles=1,ticks=2,dropout_rate=0)
before=deepcopy((grid,slip,model,repair));checks={}
baseline=evolve([grid],slip,model,repair,**args)
observed=[]
explicit=evolve([grid],slip,model,repair,**args,population_policy='legacy_archive',
    founder_start_mode='bootstrap',survival_regime='sheltered',cubff_density_pressure=False,
    evaluation_callback=observed.append)
checks['legacy_exact']=baseline==explicit
checks['actual_observer']=len(observed)==4 and all(x['final_episode']['alive'] for x in observed)
checks['damage_observer']=all(c['damage_seed']==x['run_seed']*10+c['cycle'] and
    len(c['frames']['removed_cells'])==c['removed_cell_count'] for x in observed for c in x['cycles'])
new=dict(population_policy='generation_survivors_v1',founder_start_mode='bootstrap')
archive,report=evolve([grid],slip,model,repair,**args,**new)
checks['survivor_api']=len(report['living_population']['final_breeders'])==2 and not report['living_population']['termination']['ended']
checks['full_endpoint_evidence']=all(c['breeding']['eligible'] and c['breeding']['cycles_qualified']==1
    and c['breeding']['final_episode']['alive'] for g in report['generations'] for c in g['creatures'])
checks['repeat_exact']=(archive,report)==evolve([grid],slip,model,repair,**args,**new)
empty=evolve([grid],slip,model,repair,**args,population_policy='generation_survivors_v1',founder_start_mode='continue',founder_grids=[])[1]
checks['empty_explicit']=empty['living_population']['final_breeders']==[] and empty['summary']['creature_count']==0
checks['empty_not_death']=empty['living_population']['termination']['reason']=='empty_continuation' and not empty['living_population']['termination']['genuine_lifecycle_extinction']
actual=implementation.run_episode
def dead(*a,**kw):
    result=actual(*a,**kw);result['alive']=False;result['death_cause']='STARVATION';return result
with patch.object(implementation,'run_episode',side_effect=dead):
    dead_archive,dead_report=evolve([grid],slip,model,repair,**args,**new)
checks['archive_is_history']=bool(dead_archive['elites']) and not dead_report['living_population']['final_breeders']
checks['terminal_death']=dead_report['living_population']['termination']['genuine_lifecycle_extinction'] and dead_report['summary']['generation_count']==1
checks['inputs_immutable']=before==(grid,slip,model,repair)
errors=0
for extra in [dict(population_policy='generation_survivors_v1'),dict(founder_start_mode='continue'),
              dict(cubff_density_pressure=True),dict(cubff_density_pressure=0),dict(survival_regime='tiny')]:
    try:evolve([grid],slip,model,repair,**args,**extra)
    except ValueError:errors+=1
checks['explicit_guards']=errors==5
print(json.dumps(checks))
