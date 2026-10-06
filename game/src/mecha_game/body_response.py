"""Native model identity/readout; arithmetic remains in the engine lifecycle."""
from mecha_engine.lifecycle import initial_state

BODY_RESPONSES = ('legacy', 'workload-v1')

def validate_body_response(value):
    if not isinstance(value, str) or value not in BODY_RESPONSES:
        raise ValueError('body response must be legacy or workload-v1')
    return value

def body_options(value):
    validate_body_response(value)
    return {'body_response': value} if value != 'legacy' else {}

def saved_body_response(document):
    if not isinstance(document, dict):
        raise ValueError('Body response evidence must be an object.')
    if 'body_response' in document and document['body_response'] != 'workload-v1':
        raise ValueError('Unsupported saved body response; legacy records omit the field.')
    return validate_body_response(document.get('body_response', 'legacy'))

def validate_saved_body(state, grid, profile, mechanics, model):
    validate_body_response(model)
    if saved_body_response(state) != model:
        raise ValueError('Saved lifecycle body response differs from this life.')
    if model == 'legacy':
        if 'body_workload' in state:
            raise ValueError('Legacy lifecycle cannot carry an active body workload.')
        return
    expected = initial_state(grid, profile, mechanics=mechanics, **body_options(model))['body_workload']
    from mecha_engine.storage import canonical_json
    if canonical_json(state.get('body_workload')) != canonical_json(expected):
        raise ValueError('Saved body workload differs from the actual body projection.')

def body_lines(document):
    if document.get('body_response', 'legacy') == 'legacy':
        return []
    value = document['body_workload']
    return ['Body response: workload-v1 (experimental).',
            f"Play energy: {value['play_energy_cost']:.6f}; functional capacity {value['functional_capacity']:.3f} / mass {value['occupied_mass']}.",
            'Play cost follows this body; behavior priors remain the species covenant.']
