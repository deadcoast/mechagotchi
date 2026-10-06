import copy, json, sys, tempfile, sqlite3
from pathlib import Path
ROOT=Path(r'C:\Users\ryanf\github\_shelved\mechagotchi')
sys.path[:0]=[str(ROOT/'game/src'), str(ROOT/'packages/mecha_engine/src')]
from mecha_game.campaign import KeeperCampaign, default_campaign_paths, load_campaign_inputs
from mecha_game.covenant_io import import_covenant
from mecha_game.app import _EraBench
from mecha_game.session import CompanionSession
from mecha_engine.generation import train_generation_model
paths=default_campaign_paths(ROOT)
inputs=load_campaign_inputs(paths['seed_dir'], paths['slip_path'], paths['adopted_model_path'], with_models=False)
with tempfile.TemporaryDirectory(prefix='mecha-read-audit-') as directory:
    folder=Path(directory)
    imported=copy.deepcopy(inputs['slip_profile'])
    imported['profile_id']='audit_new_base'
    profile_path=folder/'new-base.json'
    profile_path.write_text(json.dumps(imported),encoding='utf-8')
    campaign=KeeperCampaign(inputs)
    verdict=import_covenant(campaign,profile_path)
    campaign.campaign['status']='extinct'
    child=campaign.successor()
    print(json.dumps({'probe':'import_successor','import_ok':verdict['ok'],'active_base':campaign.base_profile['profile_id'],'successor_base':child.base_profile['profile_id'],'inherited_input_profile':child.inputs['slip_profile']['profile_id']}))
    campaign.campaign['status']='active'
    state_path=folder/'campaign_state.json'
    campaign.save_state(state_path)
    missing_ledger=folder/'missing.sqlite3'
    bench=_EraBench('tiny',state_path=state_path,ledger_path=missing_ledger)
    resumed=bench.ensure()
    print(json.dumps({'probe':'missing_ledger','existing_state_profile':imported['profile_id'],'loaded_profile':resumed.campaign['slip_profile']['profile_id'],'error':None,'state_preserved_before_mutation':json.loads(state_path.read_text())['base_profile']['profile_id']}))
    state_path.write_text(json.dumps({'state_format':KeeperCampaign.STATE_FORMAT}),encoding='utf-8')
    sqlite3.connect(missing_ledger).close()
    malformed=_EraBench('tiny',state_path=state_path,ledger_path=missing_ledger)
    try:
        malformed.budget_lines()
        error=None
    except Exception as exc:
        error=f'{type(exc).__name__}: {exc}'
    print(json.dumps({'probe':'supported_format_incomplete_campaign','budget_lines_error':error}))
    grid=inputs['seed_grids'][0]
    model=train_generation_model([grid])
    old=CompanionSession(grid,inputs['slip_profile'],model=model)
    while old.alive: old.advance()
    old.succeed()
    companion=folder/'companion.json'
    old.save_checkpoint(companion)
    new=CompanionSession(grid,inputs['slip_profile'],model=model,origin='era_elite')
    new.save_checkpoint(companion)
    new.advance('feed')
    new.save_checkpoint(companion)
    print(json.dumps({'probe':'adoption_chronicle','old_records':len(old.lineage),'active_records':len(json.loads(companion.read_text())['lineage']),'backup_records':len(json.loads(companion.with_suffix('.bak.json').read_text())['lineage']),'old_death_remaining':any('death_cause' in row for row in json.loads(companion.with_suffix('.bak.json').read_text())['lineage'])}))

fixture=ROOT/'.development/w5-release-demo/incumbent/campaign.sqlite3'
if fixture.exists():
    conn=sqlite3.connect(fixture.resolve().as_uri()+'?mode=ro',uri=True)
    counts={table:conn.execute(f'SELECT count(*) FROM {table}').fetchone()[0] for table in ['eras','elites','founders','replays']}
    row=conn.execute('SELECT weather_json, report_json FROM eras LIMIT 1').fetchone()
    admissions=[{'era_index':item[0], 'founders':json.loads(item[1]).get('founders')} for item in conn.execute('SELECT era_index,report_json FROM eras')]
    print(json.dumps({'probe':'existing_w5_ledger','fixture':fixture.relative_to(ROOT).as_posix(),'counts':counts,'weather_keys':list(json.loads(row[0])),'report_keys':list(json.loads(row[1])),'recorded_admissions':admissions}))
    conn.close()
