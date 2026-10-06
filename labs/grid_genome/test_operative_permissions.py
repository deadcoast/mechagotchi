"""X6 permission semantics, preregistered before the operative implementation."""
import copy
import json
import unittest
from pathlib import Path
from corpus_builder import build_seed_grids, build_seed_grids_16, PALETTES
from constrained_generator import train_constraints
from grid_helpers import RICH_TOKENS, RICH_ORGAN_ROLES
from validator import validate_grid
from slip import is_grid_aligned
from operative_permissions import operative_descendant, symmetry_score

ROOT = Path(__file__).resolve().parents[2]
RATES = ('cell_mutation_rate', 'organ_shift_rate', 'palette_shift_rate', 'symmetry_break_rate')

def phenotype(grid):
    return {key: copy.deepcopy(grid[key]) for key in ('schema_version','grid_size','cells','organs','palette','mutation')}

class OperativePermissionsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.seeds = build_seed_grids()
        cls.model = train_constraints(cls.seeds)
        cls.profile = json.loads((ROOT/'data/slips/valid/slip_lcd_seed.json').read_text())
        cls.profile['grid'].update(allowed_palettes=list(PALETTES),body_mass_max=64)
        cls.profile['mutation'] = {key+'_max':1.0 for key in RATES}

    def parent(self, **rates):
        parent = copy.deepcopy(self.seeds[0])
        parent['mutation'] = {key:rates.get(key, 1.0) for key in RATES}
        return parent

    def generate(self, parent, seed=7, model=None, profile=None, rounds=12):
        return operative_descendant(parent, grid_id='operative_test', rng_seed=seed,
            slip_profile=self.profile if profile is None else profile,
            token_counts=(model or self.model)['token_counts'], adjacency=(model or self.model)['adjacency'],
            token_specs=RICH_TOKENS, organ_specs=RICH_ORGAN_ROLES, palettes=PALETTES,
            validate=validate_grid, align=is_grid_aligned, proposal_rounds=rounds)

    def test_zero_rates_preserve_full_phenotype_and_permissions(self):
        parent=self.parent(**dict.fromkeys(RATES,0.0))
        parent['metadata']['author_note']={'kept':['verbatim']}
        child=self.generate(parent)
        self.assertEqual(phenotype(parent),phenotype(child))
        self.assertEqual(parent['metadata']['author_note'],child['metadata']['author_note'])
        self.assertEqual([],child['lineage']['mutation_events'])
        trace=child['metadata']['generation_trace']
        self.assertEqual(36,len(trace['operator_events']))
        self.assertEqual(0,trace['proposal_attempts'])
        self.assertEqual(0,trace['accepted_proposals'])
        self.assertEqual(0,trace['rejected_proposals'])
        self.assertEqual(36,trace['operator_opportunities'])

    def test_all_locked_and_locked_organ_survive_every_operator(self):
        parent=self.parent()
        for cell in parent['cells']: cell['locked']=True
        for seed in range(12): self.assertEqual(phenotype(parent),phenotype(self.generate(parent,seed)))
        parent=self.parent(); parent['organs']['core']['mutation_locked']=True
        core=copy.deepcopy(parent['organs']['core'])
        protected={tuple(p):next(c for c in parent['cells'] if [c['x'],c['y']]==p) for p in core['cells']}
        for seed in range(12):
            child=self.generate(parent,seed)
            self.assertEqual(core,child['organs']['core'])
            actual={(c['x'],c['y']):c for c in child['cells']}
            for point,cell in protected.items(): self.assertEqual(cell,actual[point])

    def test_zero_weights_are_not_uniform_fallback(self):
        parent=self.parent(palette_shift_rate=0.0)
        for cell in parent['cells']: cell['mutation_weight']=0.0
        child=self.generate(parent)
        self.assertEqual(phenotype(parent),phenotype(child))
        events=child['metadata']['generation_trace']['operator_events']
        self.assertFalse(any(e.get('selected_source') is not None for e in events))

    def test_each_rate_zero_forbids_its_operator(self):
        for rate,operator in zip(RATES[:3],('cell_mutation','organ_shift','palette_shift')):
            parent=self.parent(**{rate:0.0})
            events=self.generate(parent)['metadata']['generation_trace']['operator_events']
            self.assertTrue(all(e['outcome']=='rate_disabled' for e in events if e['operator']==operator))

    def test_zero_symmetry_permission_never_lowers_role_symmetry(self):
        parent=self.parent(symmetry_break_rate=0.0,palette_shift_rate=0.0)
        for seed in range(30):
            child=self.generate(parent,seed)
            self.assertGreaterEqual(symmetry_score(child),symmetry_score(parent))
            for event in child['metadata']['generation_trace']['operator_events']:
                if event['outcome']=='accepted' and event['operator']!='palette_shift':
                    self.assertGreaterEqual(event['symmetry_after'],event['symmetry_before'])

    def test_weighted_source_choice_precedes_validation_filtering(self):
        a=self.parent(organ_shift_rate=0.0,palette_shift_rate=0.0)
        for cell in a['cells']: cell['mutation_weight']=0.0
        a['cells'][0]['mutation_weight']=0.9; a['cells'][1]['mutation_weight']=0.1
        b=copy.deepcopy(a); b['cells'][0]['mutation_weight']=0.1; b['cells'][1]['mutation_weight']=0.9
        selected=[]
        for parent in (a,b):
            selected.append(sum(self.generate(parent,seed,rounds=1)['metadata']['generation_trace']['operator_events'][0]['selected_source']==[parent['cells'][0]['x'],parent['cells'][0]['y']] for seed in range(200)))
        self.assertGreater(selected[0],selected[1])
        self.assertGreater(selected[0],100); self.assertLess(selected[1],100)

    def test_accepted_trace_deltas_replay_actual_intermediate_changes(self):
        parent=self.parent(); accepted=0
        for seed in range(15):
            child=self.generate(parent,seed); current=copy.deepcopy(parent)
            trace=child['metadata']['generation_trace']; events=trace['operator_events']
            self.assertEqual(trace['proposal_attempts'],trace['accepted_proposals']+trace['rejected_proposals'])
            self.assertEqual(len(events),sum(trace['outcome_counts'].values()))
            for event in events:
                if event['outcome']!='accepted': continue
                accepted+=1; delta=event['delta']; self.assertTrue(delta)
                for key,change in delta.items():
                    self.assertEqual(current[key],change['before']); current[key]=copy.deepcopy(change['after'])
            self.assertEqual(phenotype(current),phenotype(child))
            self.assertEqual(sum(e['outcome']=='accepted' for e in events),len(child['lineage']['mutation_events']))
        self.assertGreater(accepted,0)

    def test_deterministic_immutable_and_valid_multigeneration(self):
        parent=self.parent(); snapshot=copy.deepcopy((parent,self.model,self.profile))
        self.assertEqual(self.generate(parent),self.generate(parent))
        self.assertEqual(snapshot,(parent,self.model,self.profile))
        rates=copy.deepcopy(parent['mutation'])
        for seed in range(15):
            previous=parent; parent=self.generate(parent,seed)
            self.assertTrue(validate_grid(parent).ok); self.assertTrue(is_grid_aligned(parent,self.profile).ok)
            self.assertEqual(rates,parent['mutation']); self.assertEqual(previous['grid_id'],parent['parent_grid_id'])
            self.assertEqual(previous['lineage']['generation']+1,parent['lineage']['generation'])

    def test_custom_organ_and_extra_payload_survive_zero_control(self):
        parent=self.parent(**dict.fromkeys(RATES,0.0)); parent['organs']['custom_sensors']=parent['organs'].pop('sensors')
        for cell in parent['cells']:
            if cell.get('organ')=='sensors': cell['organ']='custom_sensors'
            cell['extra_evidence']={'keep':True}
        self.assertEqual(phenotype(parent),phenotype(self.generate(parent)))

    def test_strict_permission_types_and_finite_values(self):
        for key,value in (('locked',1),('locked','false'),('mutation_weight',float('nan')),('mutation_weight',True)):
            parent=self.parent(); parent['cells'][0][key]=value
            with self.assertRaises(ValueError): self.generate(parent)
        parent=self.parent(); parent['organs']['core']['mutation_locked']='yes'
        with self.assertRaises(ValueError): self.generate(parent)
        parent=self.parent(); parent['mutation']['cell_mutation_rate']=float('nan')
        with self.assertRaises(ValueError): self.generate(parent)

    def test_rate_cap_refusal_and_bad_parent_are_not_clamped(self):
        parent=self.parent(); profile=copy.deepcopy(self.profile); profile['mutation']['cell_mutation_rate_max']=0.0
        with self.assertRaises(ValueError): self.generate(parent,profile=profile)
        parent['cells']=[]
        with self.assertRaises(ValueError): self.generate(parent)

    def test_rich_sixteen_outputs_remain_valid_aligned(self):
        seeds=build_seed_grids_16(); model=train_constraints(seeds); profile=copy.deepcopy(self.profile); profile['grid']['body_mass_max']=256
        for seed,parent in enumerate(seeds[:10]):
            parent=copy.deepcopy(parent); parent['mutation']=dict.fromkeys(RATES,1.0)
            child=self.generate(parent,seed,model,profile)
            self.assertTrue(validate_grid(child).ok,validate_grid(child).errors)
            self.assertTrue(is_grid_aligned(child,profile).ok)

if __name__=='__main__': unittest.main()
