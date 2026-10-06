"""Capture first, then record an actual bounded result without a second era.

Only the measurement coordinator authorizes outcome execution. This helper has
no evolve call: it persists the existing report and offers explicit reproduction.
"""
from copy import deepcopy
import json
from pathlib import Path
import sqlite3

from mecha_game.execution import (capture_execution, decode_execution_inputs,
    finalize_execution, result_digest, reproduce_era, ordered_json_bytes)

CONFIG = dict(generations=6, population=16, damage_cycles=2, ticks=16, dropout_rate=.2)


def prepare_record(home, inputs, spec):
    home = Path(home)
    if home.exists() and any(home.iterdir()):
        raise ValueError('Body recording home must be new and empty.')
    home.mkdir(parents=True, exist_ok=True)
    model = spec['body_response']
    if model not in ('legacy', 'workload-v1'):
        raise ValueError('Unsupported body recording model.')
    campaign_id = 'body-workload-' + str(spec['rng_seed']) + '-' + model
    effective = dict(seed_grids=deepcopy(inputs['seed_grids']), slip_profile=deepcopy(inputs['slip_profile']),
        generation_model=deepcopy(inputs['generation_model']), repair_model=deepcopy(inputs['repair_model']),
        legibility_model=deepcopy(inputs['legibility_model']), readability_selection=deepcopy(inputs['readability_selection']),
        cubff_pressure_source=deepcopy(inputs['weather_sources']['storm']), founder_grids=[],
        rng_seed=spec['rng_seed'], effective_config=deepcopy(spec.get('config', CONFIG)),
        population_policy='generation_survivors_v1', founder_start_mode='bootstrap',
        survival_regime='stress_probe', cubff_density_pressure=False, body_response=model)
    sources = deepcopy(inputs.get('input_sources', []))
    sources += deepcopy(inputs.get('weather_input_sources', {}).get('storm', []))
    bundle = capture_execution(campaign_id, 0, effective, sources)
    # Persist the precise captured inputs before the caller runs its only era.
    (home/'prepared-inputs.json').write_bytes(ordered_json_bytes(bundle))
    return bundle, decode_execution_inputs(bundle)


def record_result(home, bundle, archive, report, admissions=()):
    home = Path(home)
    if (home/'campaign.sqlite3').exists():
        raise ValueError('Body recording ledger already exists; no retry or overwrite.')
    prepared = json.loads((home/'prepared-inputs.json').read_text(encoding='utf-8'))
    if result_digest(prepared) != result_digest(bundle):
        raise ValueError('Body recording differs from the pre-execution capture.')
    elites = [{'niche_key': niche, **deepcopy(archive['elites'][niche])} for niche in sorted(archive['elites'])]
    execution = finalize_execution(bundle, list(admissions), report, elites)
    ended = report['living_population']['termination']['ended']
    campaign_id = execution['manifest']['campaign_id']
    from mecha_game.campaign import KeeperCampaign, evaluate_unlocks
    from mecha_engine.runtime import learned_readability_score
    from mecha_game.campaign_recovery import save_campaign_checkpoint
    data = decode_execution_inputs(bundle)
    campaign = KeeperCampaign(data, campaign_id=campaign_id,
        keeper_label='Registered body workload observation', created_date='2026-10-06',
        base_seed=execution['manifest']['rng_seed'], era_config=data['effective_config'],
        population_policy='generation_survivors_v1', body_response=report.get('body_response', 'legacy'))
    multipliers = [row['dropout_multiplier'] for row in report.get('cubff_pressure', {}).get('by_generation', [])]
    legibility = (round(sum(learned_readability_score(elite['grid'], data['legibility_model'])
                            for elite in elites) / len(elites), 6) if elites else None)
    # These are the campaign's ordinary derived observations over the original
    # report. No unlock, death, breeder or additional generation is fabricated.
    era = dict(era_index=0, rng_seed=execution['manifest']['rng_seed'],
        weather=dict(forecast='storm', snapshot_ids=[row['snapshot_id']
            for row in report.get('cubff_pressure', {}).get('by_generation', [])]),
        founders_submitted=[], founder_records=[], report=deepcopy(report), elites=elites,
        derived=dict(went_extinct=ended, generations_ran=len(report['generations']),
            max_dropout_multiplier_survived=max(multipliers) if multipliers and not ended else None,
            elite_mean_learned_readability=legibility), execution=execution)
    campaign.campaign['eras'].append(era)
    campaign._population_continuation = dict(founder_start_mode='continue', era_index=0,
        ordered_breeders_sha256=execution['manifest']['ordered_breeders_sha256'])
    campaign.campaign['unlocks'].extend(evaluate_unlocks(era, []))
    if ended:
        campaign.campaign['status'] = 'extinct'
    campaign.save(home/'campaign.sqlite3')
    campaign.save_state(home/'campaign_state.json')
    save_campaign_checkpoint(home/'campaign_state.json', home/'campaign.sqlite3')
    receipt = dict(campaign_id=campaign_id, era_index=0, report_sha256=result_digest(report),
        elites_sha256=result_digest(elites), execution_manifest_sha256=result_digest(execution['manifest']),
        body_response=report.get('body_response','legacy'))
    (home/'record.json').write_bytes(ordered_json_bytes(receipt))
    return receipt


def reproduce_record(home):
    home = Path(home)
    receipt = json.loads((home/'record.json').read_text(encoding='utf-8'))
    conn = sqlite3.connect((home/'campaign.sqlite3').resolve().as_uri()+'?mode=ro', uri=True)
    try:
        return reproduce_era(conn, receipt['campaign_id'], receipt['era_index'])
    finally:
        conn.close()
