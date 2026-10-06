"""X6 public opt-in seam; probes import only the installed package surface."""
import json
import os
from pathlib import Path
import subprocess
import sys
import unittest

ROOT=Path(__file__).resolve().parents[3]
SRC=ROOT/'packages/mecha_engine/src'
PRELUDE=r'''
import copy,hashlib,json
from pathlib import Path
from mecha_engine.generation import generate_candidate,generate_batch,train_generation_model,explain_generation
from mecha_engine.genome import validate_grid
root=Path.cwd()
seeds=[json.loads(p.read_text()) for p in sorted((root/'data/seed_grids').glob('*.json'))]
profile=json.loads((root/'data/slips/valid/slip_lcd_seed.json').read_text())
model=train_generation_model(seeds)
'''

class OperativePackageContractTests(unittest.TestCase):
    def probe(self,script):
        result=subprocess.run([sys.executable,'-B','-c',PRELUDE+script],cwd=ROOT,env=dict(os.environ,PYTHONPATH=str(SRC)),text=True,capture_output=True,timeout=90)
        self.assertEqual(0,result.returncode,result.stderr)
        return json.loads(result.stdout)

    def test_zero_permissions_trace_and_multigeneration_public_api(self):
        result=self.probe(r'''
parent=copy.deepcopy(next(grid for grid in seeds if grid['palette']['palette_id']=='lcd_green'))
parent['mutation']=dict.fromkeys(parent['mutation'],0.0)
original=copy.deepcopy((parent,model,profile))
child=generate_candidate(parent,model,profile,rng_seed=7,mutation_arm='operative_permissions_v1')
explanation=explain_generation(child)
assert all(parent[key]==child[key] for key in ('cells','organs','palette','mutation'))
assert original==(parent,model,profile)
assert explanation['mutation_arm']=='operative_permissions_v1'
assert len(explanation['operator_events'])==36
assert explanation['operator_opportunities']==36
assert explanation['proposal_attempts']==explanation['rejected_proposals']==0
assert explanation['outcome_counts']=={'rate_disabled':36}
assert explanation['mutation_events']==[]
assert explanation['inherited_rates']==parent['mutation']
assert generate_candidate(parent,model,profile,rng_seed=7,mutation_arm='operative_permissions_v1')==child
batch=generate_batch([parent],5,profile,rng_seed=9,mutation_arm='operative_permissions_v1')
assert len({item['grid_id'] for item in batch})==5
assert all(validate_grid(item).ok for item in batch)
print(json.dumps({'passed':True}))
''')
        self.assertTrue(result['passed'])

    def test_legacy_omitted_explicit_and_prechange_pins(self):
        result=self.probe(r'''
rows=[]
for parent in seeds[:10]:
 for seed in (0,7,77):
  for temperature in (None,1.5):
   value=generate_candidate(parent,model,rng_seed=seed,resample_temperature=temperature)
   assert value==generate_candidate(parent,model,rng_seed=seed,resample_temperature=temperature,mutation_arm='legacy')
   rows.append(dict(parent=parent['grid_id'],seed=seed,temperature=temperature,sha256=hashlib.sha256(json.dumps(value,sort_keys=True).encode()).hexdigest(),explanation=explain_generation(value)))
for seed in (77,313):
 for slip in (None,profile):
  value=generate_batch(seeds,20,slip_profile=slip,rng_seed=seed)
  assert value==generate_batch(seeds,20,slip_profile=slip,rng_seed=seed,mutation_arm='legacy')
  rows.append(dict(batch=True,seed=seed,profile=slip is not None,sha256=hashlib.sha256(json.dumps(value,sort_keys=True).encode()).hexdigest()))
print(json.dumps({'digest':hashlib.sha256(json.dumps(rows,sort_keys=True).encode()).hexdigest()}))
''')
        self.assertEqual('17579288bd3d5c327fc2740c0df1dc35a1fc5a37cde8f6422c29cee7ac01b828',result['digest'])

    def test_invalid_arm_and_permission_types_are_explicit(self):
        result=self.probe(r'''
for arm in ('unknown',None,True,0):
 try: generate_candidate(seeds[0],model,rng_seed=2,mutation_arm=arm)
 except ValueError: pass
 else: raise AssertionError('arm was accepted')
parent=copy.deepcopy(seeds[0]); parent['cells'][0]['locked']='false'
try: generate_candidate(parent,model,rng_seed=2,mutation_arm='operative_permissions_v1')
except ValueError: pass
else: raise AssertionError('bad lock was accepted')
print(json.dumps({'passed':True}))
''')
        self.assertTrue(result['passed'])

if __name__=='__main__': unittest.main()
