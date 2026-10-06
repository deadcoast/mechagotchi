"""Run a reproducible toy ecosystem through promoted APIs, with no corpus lookup.

python -m mecha_engine.runtime.examples.seeded --output NEW_DIRECTORY
The authored fixture and small training budget teach the API, not performance.
Readability is an explicitly uncalibrated constant; no default is promoted.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path

from mecha_engine.archive import archive_summary
from mecha_engine.generation import train_generation_model
from mecha_engine.genome import validate_grid
from mecha_engine.repair import train_repair_model
from mecha_engine.runtime import evolve
from mecha_engine.slip import is_grid_aligned, validate_slip


def toy_inputs() -> tuple[dict, dict]:
    """A fresh authored, connected 8x8 fixture and its explicit covenant."""
    groups = {
        'core': ('body_core', 'body', 'hard', '#5dbb63',
                 [[x,y] for y in range(2,5) for x in range(2,6)]),
        'sensors': ('sensor', 'eye', 'glass', '#d8ffd6', [[2,1],[5,1]]),
        'expression': ('expression', 'mouth', 'soft', '#d8ffd6', [[3,5],[4,5]]),
    }
    cells=[]; organs={}
    for name,(organ_role,role,material,color,positions) in groups.items():
        organs[name]={'role':organ_role,'cells':positions,'required':True}
        for x,y in positions:
            cells.append(dict(x=x,y=y,visual=color,role=role,material=material,
                mutation_weight=0.1,animation_anchor=(x,y)==(3,3),organ=name,
                stress=0,damage=0,locked=False))
    grid=dict(grid_id='example_toy_seed',schema_version='0.1.0',parent_grid_id=None,
        grid_size=[8,8],cells=sorted(cells,key=lambda cell:(cell['y'],cell['x'])),
        organs=organs,palette={'palette_id':'lcd_green',
            'colors':['#07140d','#5dbb63','#d8ffd6'],'background_index':0},
        mutation={'cell_mutation_rate':0.05,'organ_shift_rate':0.02,
            'palette_shift_rate':0.01,'symmetry_break_rate':0.01},
        lineage={'generation':0,'ancestor_ids':[],'mutation_events':[]},
        metadata={'source':'public_example_authored_toy'})
    profile={'slip_version':'0.1.0','profile_id':'example_toy_covenant',
        'name':'Toy example covenant',
        'grid':{'allowed_palettes':['lcd_green'],'body_mass_min':4,
            'body_mass_max':24,'required_organ_roles':['sensor','expression']},
        'mutation':{'cell_mutation_rate_max':0.15,'organ_shift_rate_max':0.05,
            'palette_shift_rate_max':0.05,'symmetry_break_rate_max':0.05},
        'behavior':{'curiosity':0.6,'neediness':0.4,'sleepiness':0.5},
        'survival_weights':{'stability':0.5,'novelty':0.25,'bond':0.25}}
    return grid,profile


def run_example(output: Path, rng_seed: int=20261006) -> dict:
    output=Path(output)
    if type(rng_seed) is not int:
        raise ValueError('rng_seed must be an integer')
    try:
        output.mkdir(parents=True,exist_ok=False)
    except FileExistsError as error:
        raise ValueError(f'Output already exists; choose a new directory: {output}') from error
    grid,profile=toy_inputs()
    checks={'seed_valid':validate_grid(grid).ok,'profile_valid':validate_slip(profile).ok,
            'seed_aligned':is_grid_aligned(grid,profile).ok}
    if not all(checks.values()):
        raise ValueError('Authored example inputs did not pass the promoted validators.')
    training={'dropout_rates':(0.1,0.2),'damage_instances':1,'epochs':20,
              'learning_rate':1.5,'live_class_weight':3.0,'rng_seed':rng_seed,
              'vocabulary':'legacy'}
    configuration={'generations':2,'population':3,'damage_cycles':1,
                   'ticks':8,'dropout_rate':0.1,'rng_seed':rng_seed}
    generation_model=train_generation_model([grid])
    repair_model=train_repair_model([grid],**training)
    archive,engine_report=evolve([grid],profile,generation_model,repair_model,
        readability_scorer=lambda candidate:0.5,**configuration)
    elites=[{'niche_key':niche,**record} for niche,record in sorted(archive['elites'].items())]
    checks['elites_valid']=all(validate_grid(item['grid']).ok for item in elites)
    checks['no_target_template']=repair_model['target_template_used'] is False
    report={'format':'mecha_engine_seeded_example_v1','ok':all(checks.values()),
        'scientific_evidence':False,
        'assumptions':['One authored toy seed; no measured corpus coverage claim.',
                       'Small explicit training/evolution budgets are teaching settings.',
                       'An empty archive or extinction is an engine outcome, not fabricated success.'],
        'readability':{'kind':'constant_uncalibrated','value':0.5,'manual_ratings_used':False},
        'training':training,'configuration':configuration,'checks':checks,
        'archive_summary':archive_summary(archive),'engine_report':engine_report}
    for name,value in [('seed.json',grid),('covenant.json',profile),
                       ('elites.json',elites),('report.json',report)]:
        with (output/name).open('x',encoding='utf-8',newline='\n') as stream:
            stream.write(json.dumps(value,indent=2,sort_keys=True,allow_nan=False)+'\n')
    return report


def main(argv=None) -> int:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True,help='New directory; existing paths are never overwritten.')
    parser.add_argument('--rng-seed',type=int,default=20261006)
    args=parser.parse_args(argv)
    try:
        report=run_example(args.output,args.rng_seed)
    except (OSError,ValueError) as error:
        parser.exit(2,str(error)+'\n')
    print(f"Toy example {'completed' if report['ok'] else 'failed'}: {args.output/'report.json'}")
    return 0 if report['ok'] else 1

if __name__=='__main__': raise SystemExit(main())
