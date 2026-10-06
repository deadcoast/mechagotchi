import json, sys, tempfile, urllib.request, urllib.error
from pathlib import Path
root=Path(r'C:\Users\ryanf\github\_shelved\mechagotchi')
sys.path.insert(0,str(root/'workshop'/'server'))
from workshop_server import start_workshop_server, import_png_with_embedded_sidecar
matrix=[list(r) for r in ['.E..E...','..BB....','.BABB...','..BB.M..','...BB...','........','........','........']]
def request(base,path,data=None):
    req=urllib.request.Request(base+path,data=None if data is None else json.dumps(data).encode(),headers={'Content-Type':'application/json'})
    with urllib.request.urlopen(req) as res:return json.loads(res.read())
with tempfile.TemporaryDirectory(prefix='mecha-workshop-review-') as temp:
    p=Path(temp)
    server=start_workshop_server(port=0,grids_dir=p/'grids',slips_dir=p/'slips',released_dir=p/'released',metrics_dir=p/'metrics',session_dir=p/'session')
    base=f'http://127.0.0.1:{server.server_address[1]}'
    try:
        initial=request(base,'/api/save',{'name':'trait-probe','matrix':matrix,'palette_id':'lcd_green','cell_overrides':{'2,1':{'material':'hard','mutation_weight':0.91}}})
        before=json.loads((p/'grids'/initial['file']).read_text(encoding='utf-8'))
        export_payload={'name':'trait-probe','matrix':matrix,'palette_id':'lcd_green','profile_id':'slip_lcd_seed','cell_overrides':{'2,1':{'material':'hard','mutation_weight':0.91}}}
        export_request=urllib.request.Request(base+'/api/export/png',data=json.dumps(export_payload).encode(),headers={'Content-Type':'application/json'})
        with urllib.request.urlopen(export_request) as response: png_bytes=response.read()
        exported_grid=import_png_with_embedded_sidecar(png_bytes)['restored_grid']
        loaded=request(base,'/api/grids/trait-probe')
        second=request(base,'/api/save',{'name':'trait-probe','matrix':loaded['matrix'],'palette_id':loaded['palette_id'],'cell_overrides':{}})
        after=json.loads((p/'grids'/second['file']).read_text(encoding='utf-8'))
        cell=lambda g: next(c for c in g['cells'] if (c['x'],c['y'])==(2,1))
        result={'source_head':'d4b4337d0dacbdfa816d990297c03a5da2d0cdca','save':initial,'load_keys':sorted(loaded),'before':cell(before),'after_unedited_reload_save':cell(after),'exported_png_sidecar_cell':cell(exported_grid),'unchanged':before==after}
        role_saved=request(base,'/api/save',{'name':'role_probe','matrix':matrix,'palette_id':'lcd_green','cell_overrides':{'1,0':{'role':'antenna','material':'signal'}}})
        role_loaded=request(base,'/api/grids/role_probe')
        try:
            role_validation=request(base,'/api/validate',{'matrix':role_loaded['matrix'],'palette_id':role_loaded['palette_id'],'cell_overrides':{}})
        except urllib.error.HTTPError as error:
            role_validation={'http_status':error.code,**json.loads(error.read())}
        result['rich_role_reload']={'saved':role_saved,'token_at_1_0':role_loaded['matrix'][0][1],'validation_after_load':role_validation}
        layers=[{'name':name,'matrix':matrix if name=='body' else [['.']*8 for _ in range(8)],'visible':True} for name in ('body','organs','decoration','effects')]
        request(base,'/api/save',{'name':'layered','matrix':matrix,'palette_id':'lcd_green','layers':layers})
        result['layered_catalog']={'grids':request(base,'/api/grids')['grids'],'preview_workshop_creatures':[entry for entry in request(base,'/api/preview/creatures')['creatures'] if entry['source']=='workshop']}
        output=json.dumps(result,indent=2)
        Path(r'C:\Users\ryanf\AppData\Local\Temp\mecha-workshop-audit-result.json').write_text(output,encoding='utf-8')
        print(output)
    finally:server.shutdown();server.server_close()
