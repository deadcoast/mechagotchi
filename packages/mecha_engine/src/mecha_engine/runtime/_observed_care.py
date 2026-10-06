"""Observed action-window selection; X7 pre-registered experimental mechanism.

Canonical research implementation mirrored byte-for-byte into the engine.
This evaluates fresh-life copies, not the source life's late-life state.
The morphology probe is an existing archive stress test, never inheritance.
"""
from __future__ import annotations

from collections import Counter
from copy import deepcopy
import hashlib
import json
import random

from mecha_engine.archive import lifecycle_probe_grid
from mecha_engine.generation import generate_candidate
from mecha_engine.genome import render_packet_v2
from mecha_engine.learning import observe_fleet
from mecha_engine.lifecycle import ACTIONS, advance_tick, choose_action_detailed, initial_state

CARE_POLICY = 'observed_care_selection_v1'
CARE_POLICY_V2 = 'observed_care_selection_v2'
CARE_POLICIES = (CARE_POLICY, CARE_POLICY_V2)
CARE_EVALUATORS = ('pristine', 'archive_morphology_probe_v1')
CARE_POOL_SIZE = 8
CARE_EVENT_LIMIT = 100
KEPT_THREADS = ('hunger_forecast', 'energy_forecast', 'interaction_timing',
                'animation_bandit', 'hidden_mood_hmm')
_CONTEXT_KEYS = frozenset(('format', 'keeper_id', 'life_id', 'grid_id', 'grid_sha256',
    'care_summary', 'events', 'events_omitted', 'last_age_ticks', 'last_session_tick', 'outcome'))
_EVENT_KEYS = frozenset(('tick', 'session_tick', 'actor', 'action', 'begging', 'alive', 'death_cause'))
_SUMMARY_KEYS = frozenset(('history', 'from_age_ticks', 'ticks_observed', 'keeper_actions',
                           'companion_actions', 'beg_requests'))


def _digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':'),
                                    allow_nan=False).encode('utf-8')).hexdigest()


def care_context_sha256(context: dict) -> str:
    return _digest(context)


def care_grid_sha256(grid: dict) -> str:
    return _digest(grid)


def care_structure_sha256(grid: dict) -> str:
    """Semantic body structure only: no IDs, lineage, palettes or rate labels."""
    cells = [{key: cell.get(key) for key in ('x', 'y', 'role', 'material', 'organ')}
             for cell in grid['cells']]
    cells.sort(key=lambda cell: (cell['y'], cell['x']))
    organs = {key: {field: value.get(field) for field in ('role', 'cells', 'required')}
              for key, value in grid['organs'].items()}
    return _digest({'grid_size': grid['grid_size'], 'cells': cells, 'organs': organs})


def validate_care_context(context: dict) -> dict:
    """Validate factual tape boundaries before any evaluation or persistence."""
    def refuse(reason):
        raise ValueError('invalid care context: ' + reason)
    def integer(value):
        return type(value) is int and value >= 0
    def identity(value):
        return isinstance(value, str) and bool(value.strip())
    keys = _CONTEXT_KEYS | {'body_response'} if isinstance(context, dict) and 'body_response' in context else _CONTEXT_KEYS
    if not isinstance(context, dict) or set(context) != keys:
        refuse('unsupported fields')
    if 'body_response' in context and context['body_response'] != 'workload-v1':
        refuse('unsupported body response')
    if context['format'] != 'keeper_care_context_v1':
        refuse('unsupported format')
    if any(not identity(context[key]) for key in ('keeper_id', 'life_id', 'grid_id')):
        refuse('missing source identity')
    prefix = context['keeper_id'] + ':life-'
    if not context['life_id'].startswith(prefix) or len(context['life_id']) == len(prefix):
        refuse('life belongs to another Keeper')
    digest = context['grid_sha256']
    if not isinstance(digest, str) or len(digest) != 64 or any(c not in '0123456789abcdef' for c in digest):
        refuse('source genome digest')
    for key in ('events_omitted', 'last_age_ticks', 'last_session_tick'):
        if not integer(context[key]): refuse('clock or omitted count')
    if context['last_session_tick'] < context['last_age_ticks']:
        refuse('session clock precedes life clock')
    if context['outcome'] not in ('alive', 'dead', 'replaced_alive', 'unknown'):
        refuse('outcome')
    summary = context['care_summary']
    if not isinstance(summary, dict) or set(summary) != _SUMMARY_KEYS:
        refuse('summary fields')
    if summary['history'] not in ('complete', 'partial', 'unavailable'):
        refuse('history availability')
    for key in ('from_age_ticks', 'ticks_observed', 'beg_requests'):
        if not integer(summary[key]): refuse('summary count')
    if (summary['from_age_ticks'] + summary['ticks_observed'] != context['last_age_ticks']
            or summary['beg_requests'] > summary['ticks_observed']
            or (summary['history'] == 'complete' and summary['from_age_ticks'] != 0)
            or (summary['history'] == 'unavailable' and summary['ticks_observed'] != 0)):
        refuse('summary observation boundary')
    total = 0
    actions = (*ACTIONS, 'clean')
    for key in ('keeper_actions', 'companion_actions'):
        counts = summary[key]
        if not isinstance(counts, dict) or any(a not in actions or not integer(n) or n == 0 for a, n in counts.items()):
            refuse('summary action counts')
        if key == 'companion_actions' and any(counts.get(a, 0) for a in ('feed', 'clean')):
            refuse('companion cannot execute keeper-only care')
        total += sum(counts.values())
    if total != summary['ticks_observed']: refuse('summary action total')
    events = context['events']
    if not isinstance(events, list) or len(events) > CARE_EVENT_LIMIT:
        refuse('bounded event tape')
    if len(events) + context['events_omitted'] != summary['ticks_observed']:
        refuse('retained and omitted counts')
    counts = {'keeper': Counter(), 'companion': Counter()}
    begs = 0
    for index, event in enumerate(events):
        if not isinstance(event, dict) or set(event) != _EVENT_KEYS:
            refuse('event fields')
        if (type(event['tick']) is not int or event['tick'] < 1
                or type(event['session_tick']) is not int or event['session_tick'] < event['tick']):
            refuse('event clock')
        if event['tick'] != context['last_age_ticks'] - len(events) + index + 1:
            refuse('noncontiguous age window')
        if event['session_tick'] != context['last_session_tick'] - len(events) + index + 1:
            refuse('noncontiguous session window')
        if (not isinstance(event['actor'], str) or not isinstance(event['action'], str)
                or event['actor'] not in counts or event['action'] not in actions):
            refuse('event actor or action')
        if event['actor'] == 'companion' and event['action'] in ('feed', 'clean'):
            refuse('companion cannot execute keeper-only care')
        if type(event['alive']) is not bool or type(event['begging']) is not bool:
            refuse('event boolean')
        if event['alive']:
            if event['death_cause'] is not None: refuse('living event death cause')
        elif (index != len(events) - 1 or not identity(event['death_cause'])
              or context['outcome'] != 'dead'):
            refuse('death event')
        counts[event['actor']][event['action']] += 1
        begs += int(event['begging'])
    if events and (not events[-1]['alive']) != (context['outcome'] == 'dead'):
        refuse('event outcome disagreement')
    for actor, observed in counts.items():
        if any(count > summary[actor + '_actions'].get(action, 0) for action, count in observed.items()):
            refuse('event counts exceed cumulative history')
    if begs > summary['beg_requests']: refuse('event begs exceed cumulative history')
    if context['events_omitted'] == 0 and begs != summary['beg_requests']:
        refuse('complete event window contradicts cumulative begs')
    try:
        _digest(context)
    except (ValueError, TypeError):
        refuse('non-finite or non-JSON data')
    return deepcopy(context)


def observed_care_episode(grid: dict, slip_profile: dict, context: dict, *,
                          rng_seed: int = 0, evaluator: str = 'archive_morphology_probe_v1',
                          policy: str = CARE_POLICY, body_response: str = "legacy") -> dict:
    """Fresh cold incumbent evaluation under exactly the observed keeper window."""
    context = validate_care_context(context)
    if body_response not in ('legacy', 'workload-v1') or context.get('body_response', 'legacy') != body_response:
        raise ValueError('care context body response differs from evaluation model')
    if policy not in CARE_POLICIES:
        raise ValueError('unsupported care episode policy: ' + str(policy))
    if evaluator not in CARE_EVALUATORS:
        raise ValueError('unsupported care evaluator: ' + str(evaluator))
    if not context['events']:
        raise ValueError('care evaluation requires an observed event window')
    evaluation_grid = lifecycle_probe_grid(grid) if evaluator == 'archive_morphology_probe_v1' else deepcopy(grid)
    state = initial_state(evaluation_grid, slip_profile,
        **({"body_response": body_response} if body_response != "legacy" else {}))
    if any(e['action'] == 'clean' for e in context['events']) and 'cleanliness' not in state:
        raise ValueError('observed clean action requires effective covenant cleanliness')
    state['learning_switches'] = {**(state.get('learning_switches') or {}),
        **{name: True for name in KEPT_THREADS}, 'qtable_policy': False, 'qtable_consumer': False}
    rng = random.Random(rng_seed)
    begs = 0
    keeper_actions = Counter()
    full_history = []
    trajectory = []
    detailed = policy == CARE_POLICY_V2 or body_response != "legacy"
    start_state = deepcopy(state) if detailed else None
    for event in context['events']:
        if not state['alive']: break
        state['last_animation'] = render_packet_v2(evaluation_grid, state, slip_profile=slip_profile)['animation']
        state['thread_states'] = observe_fleet(state)
        decision_state = deepcopy({key: value for key, value in state.items() if key != 'history'}) if detailed else None
        decision, thought = choose_action_detailed('switchboard', state, rng)
        recommended_thought = deepcopy(thought) if detailed else None
        begging = decision == 'feed'
        begs += int(begging)
        if event['actor'] == 'keeper':
            action, thought = event['action'], None
            keeper_actions[action] += 1
        else:
            action = 'idle' if begging else decision
        state = advance_tick(state, action, thought)
        full_history.append(deepcopy(state['history'][-1]))
        if detailed:
            trajectory.append({'evaluation_tick': state['age_ticks'],
                'source_actor': event['actor'], 'source_action': event['action'],
                'decision_state': decision_state, 'recommendation': decision,
                'recommended_thought': recommended_thought, 'begging': begging,
                'applied_action': action, 'applied_thought': deepcopy(thought),
                'result': deepcopy(full_history[-1])})
        state['history'] = state['history'][-32:]
    ticks = len(context['events'])
    episode = {'policy': policy, 'evaluator': evaluator, 'ticks_requested': ticks,
        'survival_ticks': state['age_ticks'], 'alive': state['alive'],
        'death_cause': state['death_cause'],
        'need_balance': round(sum(row['balance'] for row in full_history) / ticks, 6),
        'recovery_events': state['recovery_events'], 'action_counts': deepcopy(state['action_counts']),
        'keeper_actions': dict(keeper_actions), 'beg_requests': begs,
        'final_state': deepcopy(state), 'history': full_history}
    if policy == CARE_POLICY_V2:
        episode.update(terminal_survival=state['alive'] and state['age_ticks'] == ticks,
                       initial_state=start_state, trajectory=trajectory)
    if body_response != "legacy":
        episode.update(body_response=body_response, body_workload=deepcopy(state["body_workload"]),
                       initial_state=start_state, trajectory=trajectory)
    return episode


def select_care_successor(parent_grid: dict, model, slip_profile: dict, *, context: dict | None,
                          rng_seed: int, policy: str = 'off',
                          evaluator: str = 'archive_morphology_probe_v1',
                          body_response: str = 'legacy') -> tuple[dict, dict | None]:
    """Choose within one parent's fixed candidate pool; never alter newborn cells."""
    if policy not in ('off', *CARE_POLICIES):
        raise ValueError('care selection policy must be off or ' + ' or '.join(CARE_POLICIES))
    if evaluator not in CARE_EVALUATORS:
        raise ValueError('unsupported care evaluator: ' + str(evaluator))
    checked = validate_care_context(context) if context is not None else None
    if body_response not in ("legacy", "workload-v1"):
        raise ValueError("unsupported body response")
    if checked is not None and checked.get("body_response", "legacy") != body_response:
        raise ValueError("care context body response differs from selection model")
    if policy == 'off' or checked is None or not checked['events']:
        return generate_candidate(parent_grid, model, slip_profile, rng_seed=rng_seed), None
    candidates = []
    rows = []
    for index in range(CARE_POOL_SIZE):
        seed = rng_seed + index
        candidate = generate_candidate(parent_grid, model, slip_profile, rng_seed=seed)
        episode = observed_care_episode(candidate, slip_profile, checked, rng_seed=seed, evaluator=evaluator, policy=policy,
            **({"body_response": body_response} if body_response != "legacy" else {}))
        candidates.append(candidate)
        rows.append({'index': index, 'rng_seed': seed, 'grid_id': candidate['grid_id'],
            'grid_sha256': care_grid_sha256(candidate), 'structure_sha256': care_structure_sha256(candidate),
            **{key: episode[key] for key in ('need_balance', 'survival_ticks', 'alive', 'death_cause')}})
        if body_response != 'legacy':
            rows[-1].update(candidate_grid=deepcopy(candidate), episode=episode)
        if policy == CARE_POLICY_V2:
            rows[-1].update(terminal_survival=episode['terminal_survival'], episode=episode)
    def selection_key(index):
        row = rows[index]
        legacy_key = (row['need_balance'], row['survival_ticks'], -index)
        return (row['terminal_survival'], *legacy_key) if policy == CARE_POLICY_V2 else legacy_key
    selected = max(range(CARE_POOL_SIZE), key=selection_key)
    first, last = checked['events'][0], checked['events'][-1]
    receipt = {'policy': policy, 'evaluator': evaluator, 'context_sha256': care_context_sha256(checked),
        'observed_window': {'first_age_tick': first['tick'], 'last_age_tick': last['tick'],
            'first_session_tick': first['session_tick'], 'last_session_tick': last['session_tick'],
            'ticks': len(checked['events']), 'events_omitted': checked['events_omitted']},
        'pool_size': CARE_POOL_SIZE, 'selected_index': selected,
        'selected_grid_sha256': rows[selected]['grid_sha256'],
        'selected_structure_sha256': rows[selected]['structure_sha256'], 'candidates': rows}
    if policy == CARE_POLICY_V2:
        receipt.update(selection_order=['terminal_survival', 'need_balance', 'survival_ticks', 'earliest_index'],
                       source_identity={key: checked[key] for key in ('keeper_id', 'life_id', 'grid_id', 'grid_sha256')})
    if body_response != "legacy":
        receipt["body_response"] = body_response
    return candidates[selected], receipt
