"""Fixed authored workload-v1 causal fixture, outside outcome holdouts.

The exact payload is the instrument owner's original authored constructor,
consolidated here before input freeze. Both operational fixture iterations and
all test logs remain preserved. No outcome tuning or seed search occurred.
Synthetic B/D bias models establish a causal contrast only; they are not trained
repair models or biological claims. Generation-model construction counts the
fixed two authored bodies for native adoption; no outcome is observed here.
"""
from copy import deepcopy
from dataclasses import asdict


def causal_fixture():
    """Explicit authored D->B / D->D fixture; no search, fitting, or outcome read."""
    from mecha_engine.repair._grids import grid_from_matrix
    from mecha_engine.repair._features import RICH_CLASS_TOKENS, RICH_LIVE_TOKENS, feature_count_for
    from mecha_engine.generation import train_generation_model
    matrix = [list('........') for _ in range(8)]
    for x, y, token in ((2,2,'A'), (3,2,'B'), (2,3,'B'), (3,3,'B'), (2,1,'E'), (4,3,'D')):
        matrix[y][x] = token
    def grid(value, identifier):
        return grid_from_matrix(grid_id=identifier, matrix=value,
            palette={'palette_id':'lcd_green'}, parent_grid_id=None,
            source='preregistered_workload_causal_fixture', mutation_events=[], generation_delta=0)
    low = grid(matrix, 'workload_fixture_low')
    high_matrix = deepcopy(matrix); high_matrix[3][4] = 'B'
    high = grid(high_matrix, 'workload_fixture_high')
    slip = {'slip_version':'0.1.0', 'profile_id':'workload_fixture', 'name':'Workload causal fixture',
        'grid':{'allowed_palettes':['lcd_green'], 'body_mass_min':4, 'body_mass_max':24,
                'required_organ_roles':['sensor']},
        'mutation':{'cell_mutation_rate_max':.15, 'organ_shift_rate_max':.05,
                    'palette_shift_rate_max':.05, 'symmetry_break_rate_max':.05},
        'behavior':{'curiosity':.6, 'neediness':.4, 'sleepiness':.5},
        'survival_weights':{'stability':.5, 'novelty':.25, 'bond':.25}}
    count = feature_count_for(8, 8, len(RICH_LIVE_TOKENS))
    models = {}
    for name, token in (('changed', 'B'), ('null', 'D')):
        weights = [[0.] * count for _ in RICH_CLASS_TOKENS]
        weights[RICH_CLASS_TOKENS.index(token)][-1] = 8.
        models[name] = dict(model_id='workload_synthetic_fixed_'+token,
            source_mode='engineered_constant_bias_causal_fixture', width=8, height=8,
            vocabulary='rich', class_tokens=list(RICH_CLASS_TOKENS), feature_count=count,
            weights=weights, target_template_used=False)
    return dict(grid=low, contrast_grid=high, covenant=slip,
        generation_model=asdict(train_generation_model([low, high])),
        damage_event={'removed_cells':[[4,3]]}, repair_models=models,
        play_actions=['play','sleep','feed']*3, no_play_actions=['idle','sleep','feed']*3,
        repair_ticks=9, rng_seed=20261101)

