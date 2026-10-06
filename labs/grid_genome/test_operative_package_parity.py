"""X6 byte mirror and paired laboratory/package parity, separate from legacy pins."""
import copy
import hashlib
import json
from pathlib import Path
import sys
import unittest

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'packages/mecha_engine/src'))
from corpus_builder import build_seed_grids,build_seed_grids_16,PALETTES
from grid_helpers import RICH_TOKENS,RICH_ORGAN_ROLES
from operative_permissions import operative_descendant
from validator import validate_grid
from slip import is_grid_aligned
from mecha_engine.generation import generate_candidate,train_generation_model

class OperativeParityTests(unittest.TestCase):
    def test_private_implementation_is_verbatim(self):
        self.assertEqual((ROOT/'labs/grid_genome/operative_permissions.py').read_bytes(),(ROOT/'packages/mecha_engine/src/mecha_engine/generation/_operative_permissions.py').read_bytes())

    def test_paired_outputs_and_traces_for_eight_and_rich_sixteen(self):
        profile=json.loads((ROOT/'data/slips/valid/slip_lcd_seed.json').read_text())
        profile['grid'].update(allowed_palettes=list(PALETTES),body_mass_max=256)
        profile['mutation']=dict.fromkeys(profile['mutation'],1.0)
        for seeds in (build_seed_grids(),build_seed_grids_16()):
            model=train_generation_model(seeds)
            for index,parent in enumerate(seeds[:5]):
                parent=copy.deepcopy(parent); parent['mutation']=dict.fromkeys(parent['mutation'],1.0)
                if index==1:
                    for cell in parent['cells']: cell['locked']=True
                if index==2: parent['organs']['core']['mutation_locked']=True
                for seed in (7,41):
                    package=generate_candidate(parent,model,profile,rng_seed=seed,mutation_arm='operative_permissions_v1')
                    lab=operative_descendant(parent,grid_id=package['grid_id'],rng_seed=seed,slip_profile=profile,
                        token_counts=model.token_counts,adjacency=model.adjacency,token_specs=RICH_TOKENS,organ_specs=RICH_ORGAN_ROLES,
                        palettes=PALETTES,validate=validate_grid,align=is_grid_aligned)
                    model_trace=package['metadata']['generation_trace'].pop('model')
                    self.assertEqual(model.metadata['seed_count'],model_trace['seed_count'])
                    self.assertEqual(lab,package)
                    self.assertEqual(json.loads(json.dumps(lab)),lab)

if __name__=='__main__': unittest.main()
