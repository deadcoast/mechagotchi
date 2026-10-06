"""Bounded X3 browser fixture: two real native save homes and an isolated lab."""
from copy import deepcopy
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[2]
for source in ('workshop/server','game/src','packages/mecha_engine/src'):
    sys.path.insert(0,str(ROOT/source))
from workshop_server import start_workshop_server
from mecha_game.session import CompanionSession,load_session_inputs
from mecha_game.campaign import KeeperCampaign
from authoring import project_grid
scratch=Path(sys.argv[1]).resolve(); scratch.mkdir(parents=True,exist_ok=True)
grid,profile,model=load_session_inputs(ROOT/'data/seed_grids_16x16/mg_seed16_001_beetle.json',ROOT/'data/slips/valid/slip_v2_cleanliness.json')
keepers=[];pets=[];servers=[]
for name in ('first','second'):
    home=scratch/name;home.mkdir();pet=CompanionSession(deepcopy(grid),deepcopy(profile),model=model);pet.bind_campaign('browser_'+name);pet.save(home/'companion.json')
    campaign=KeeperCampaign({'slip_profile':deepcopy(profile)},campaign_id='browser_'+name,era_config={'population':3,'generations':2})
    campaign.save(home/'campaign.sqlite3');campaign.save_state(home/'campaign_state.json');keepers.append(home);pets.append(pet)
rich=deepcopy(grid);rich['cells'][0]['mutation_weight']=0.91;rich.setdefault('metadata',{})['source']='<img src=x onerror="window.fixtureInjection=true"> literal provenance'
layers=[{'name':name,'matrix':project_grid(rich) if name=='body' else [['.']*16 for _ in range(16)],'visible':True,'custom':{'author':'preserved '+name,'opacity':0.731}} for name in ('body','organs','decoration','effects')]
document={'format':'mecha_workshop_document_v1','grid':rich,'profile':profile,'layers':layers}
folder=keepers[0]/'workshop/grids';folder.mkdir(parents=True);(folder/'rich.json').write_text(json.dumps(rich),encoding='utf-8');(folder/'rich.layers.json').write_text(json.dumps({'document':document,'layers':layers}),encoding='utf-8')
foreign=deepcopy(rich);foreign['grid_id']='x3_foreign_palette';foreign['palette']['palette_id']='gameboy_gray';foreign['palette']['colors']=['#0f180f','#849478','#dae3c9'];(folder/'foreign_palette.json').write_text(json.dumps(foreign),encoding='utf-8')
def start(home):return start_workshop_server(port=0,keeper_dir=home)
servers=[start(home) for home in keepers]
lab=scratch/'lab';servers.append(start_workshop_server(port=0,grids_dir=lab/'grids',slips_dir=lab/'slips',released_dir=lab/'released',metrics_dir=lab/'metrics',session_dir=lab/'session'))
def status(event='ready'):print(json.dumps({'port':servers[0].server_address[1],'second_port':servers[1].server_address[1],'lab_port':servers[2].server_address[1],'scratch':str(scratch),'keepers':[str(p) for p in keepers],'event':event}),flush=True)
status()
try:
    for line in sys.stdin:
        command=line.strip()
        if command=='stop':break
        if command=='restart':
            servers[0].shutdown();servers[0].server_close();servers[0]=start(keepers[0]);status('restarted')
        elif command=='advance':
            pets[0].advance();pets[0].save(keepers[0]/'companion.json');status('advanced')
finally:
    for server in servers:server.shutdown();server.server_close()
