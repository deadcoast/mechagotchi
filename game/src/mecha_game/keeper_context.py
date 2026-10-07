"""Read-only selected native Keeper adapter; existing saves and ledger stay authoritative."""
from copy import deepcopy
import hashlib
import json
import os
import sqlite3
from pathlib import Path

from mecha_engine.storage import campaign_history, load_era_elites
from mecha_game.session import CompanionSession
from mecha_game.covenant import covenant_budget
from mecha_game.campaign_recovery import require_no_restore
from mecha_game.compatibility import require_campaign_compatibility

DOCUMENT_FORMAT = 'mecha_workshop_document_v1'


def digest(value):
    return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode('utf-8')).hexdigest()


def context_id(directory, kind='native_keeper'):
    return digest([kind, os.path.normcase(str(Path(directory).resolve()))])


def read_keeper(directory):
    """One coherent read snapshot, with honest unavailable results and no fallback."""
    from mecha_game.campaign_recovery import validated_campaign_snapshot, load_recorded_founders
    root = Path(directory).resolve()
    context = dict(kind='native_keeper',context_id=context_id(root),context_revision=None,
        available=False,reason=None,keeper_dir=str(root),keeper_id=None,campaign_id=None,
        identity_origin=None,covenant=None,budget=None,
        body_response=None,body_response_source='current_keeper',
        capabilities=dict(authoring=False,release=False,pack_import=False,lab_session=False))
    result = dict(context=context,creatures=[],lineage={'campaigns':[],'lives':[],
        'notice':'Genetic parent identifiers are recorded facts; missing source snapshots remain unavailable.'})
    raw = {}
    try:
        for name in ('companion.json','campaign_state.json','era_plan.json','campaign_restore.json','campaign_preparation.json'):
            path=root/name
            raw[name]=path.read_bytes() if path.exists() else None
        for name in ('companion.json','campaign_state.json'):
            if raw[name] is None: raise ValueError(f'Selected native Keeper is missing {name}; existing files preserved.')
        require_no_restore(root/'campaign_state.json')
        if raw['era_plan.json'] is not None:
            from mecha_game.era_plan import EraPlan
            preparation=json.loads(raw['era_plan.json'])
            EraPlan._validate(preparation)
            if preparation['pending'] is not None:
                raise ValueError('An actual completed era is pending persistence. Finish or recover it in the native Keeper before authoring writes.')
        pet = CompanionSession._from_payload(json.loads(raw['companion.json']))
        context.update(keeper_id=pet.keeper_id,identity_origin=pet.chronicle['identity_origin'],
            body_response=pet.body_response)
        state = json.loads(raw['campaign_state.json'])
        write_reason = None
        try:
            require_campaign_compatibility(state, keeper_session=pet, state_path=root/'campaign_state.json')
        except ValueError as error:
            # A coherent saved history remains inspectable after an intentional
            # new-life model switch. It cannot authorize campaign-related writes.
            write_reason = str(error)
        require_no_restore(root/'campaign_state.json')
        with validated_campaign_snapshot(state,root/'campaign.sqlite3') as (conn,history):
            if pet.campaign_id is not None and state['campaign_id'] != pet.campaign_id and state['predecessor_campaign_id'] != pet.campaign_id:
                raise ValueError('Campaign belongs to a different recorded Keeper history; files preserved.')
            campaigns = []
            current = history
            while current is not None:
                recorded = deepcopy(current)
                recorded.pop('resume_founders',None)
                for era in recorded['eras']:
                    era['elites'] = load_era_elites(conn,recorded['campaign_id'],era['era_index'])
                    era['founder_records'] = load_recorded_founders(conn,recorded['campaign_id'],era['era_index'])
                    verdict = era['report'].get('founders')
                    submitted = [] if verdict is None else [*verdict.get('admitted_ids',[]),*[row['grid_id'] for row in verdict.get('rejected',[])]]
                    covered = {row['grid_id'] for row in era['founder_records']}
                    era['founder_provenance'] = dict(available=bool(submitted) and all(identity in covered for identity in submitted),
                        unavailable_ids=sorted(set(submitted)-covered),
                        reason=None if submitted and all(identity in covered for identity in submitted) else 'Full submitted source snapshots were not recorded or their identities were ambiguous.')
                campaigns.append(recorded)
                predecessor=recorded['predecessor_campaign_id']
                current=campaign_history(conn,predecessor) if predecessor else None
            for name, original in raw.items():
                path=root/name
                if (path.read_bytes() if path.exists() else None) != original:
                    raise ValueError('Keeper files changed during inspection. Refresh the selected context.')
            context.update(available=True,reason=write_reason,campaign_id=state['campaign_id'],covenant=deepcopy(state['slip_profile']),
                budget=covenant_budget(state['base_profile'],state.get('base_parameters',state['era_config']),history['unlocks']),
                capabilities=dict(authoring=write_reason is None,release=write_reason is None,pack_import=write_reason is None,lab_session=False))
            context['context_revision']=digest({'files':{key:hashlib.sha256(value).hexdigest() if value is not None else None for key,value in raw.items()},'campaigns':campaigns})
        def add(ref,label,source,grid,profile,provenance):
            doc=dict(format=DOCUMENT_FORMAT,grid=deepcopy(grid))
            if profile is not None: doc['profile']=deepcopy(profile)
            result['creatures'].append(dict(ref=ref,label=label,source=source,grid_id=grid['grid_id'],
                document=doc,document_digest=digest(doc),provenance=provenance))
        life=pet.lineage[-1]
        add({'source':'companion','life_id':life['life_id']},pet.name,'companion',pet.grid,pet.slip_profile,
            dict(keeper_id=pet.keeper_id,life_id=life['life_id'],campaign_id=pet.campaign_id))
        for campaign in campaigns:
            for era in campaign['eras']:
                for elite in era['elites']:
                    ref=dict(source='era_elite',campaign_id=campaign['campaign_id'],era_index=era['era_index'],niche_key=elite['niche_key'])
                    add(ref,f"Era {era['era_index']}: {elite['grid_id']}",'era_elite',elite['grid'],era['slip_profile'],ref)
        # Release files are candidates, not admission records. Invalid files are
        # reported individually and never substitute a reconstructed creature.
        for file in sorted((root/'released').glob('*.json')):
            if file.name.endswith(('.bak.json','.layers.json','.authoring.json')): continue
            try:
                grid_bytes=file.read_bytes(); grid=json.loads(grid_bytes)
                if not isinstance(grid,dict) or not isinstance(grid.get('grid_id'),str):
                    raise ValueError('Release does not contain a complete grid.')
                sidecar=file.with_name(file.stem+'.authoring.json')
                sidecar_bytes=sidecar.read_bytes() if sidecar.exists() else None
                doc=dict(format=DOCUMENT_FORMAT,grid=deepcopy(grid))
                if sidecar_bytes is not None:
                    stored=json.loads(sidecar_bytes)
                    doc=stored.get('document') if isinstance(stored,dict) else None
                    if not isinstance(doc,dict) or doc.get('format')!=DOCUMENT_FORMAT or doc.get('grid')!=grid:
                        raise ValueError('Release authoring sidecar differs from its saved grid; both files preserved.')
                    if 'profile' in doc:
                        from mecha_engine.slip import validate_slip
                        verdict=validate_slip(doc['profile'])
                        if not verdict.ok: raise ValueError('Release authoring profile is invalid: '+'; '.join(verdict.errors))
                if file.read_bytes()!=grid_bytes or (sidecar.read_bytes() if sidecar.exists() else None)!=sidecar_bytes:
                    raise ValueError('Release changed during inspection; refresh before selecting it.')
                source_revision=digest([hashlib.sha256(grid_bytes).hexdigest(),
                    hashlib.sha256(sidecar_bytes).hexdigest() if sidecar_bytes is not None else None])
                result['creatures'].append(dict(ref=dict(source='released',name=file.stem,source_revision=source_revision),
                    label=file.stem,source='released',grid_id=grid['grid_id'],document=deepcopy(doc),document_digest=digest(doc),
                    provenance=dict(file=file.name,release=deepcopy(grid.get('metadata',{})),
                        profile_source='saved_authoring_document' if 'profile' in doc else 'not_recorded',
                        active_covenant_advisory=deepcopy(state['slip_profile']))))
            except (OSError,ValueError,TypeError,KeyError,AttributeError) as error:
                result.setdefault('release_errors',[]).append(dict(file=file.name,error=str(error)))
        result['lineage'].update(campaigns=campaigns,lives=deepcopy(pet.lineage),chronicle=deepcopy(pet.chronicle))
    except (OSError,ValueError,TypeError,KeyError,AttributeError,sqlite3.Error) as error:
        context.update(available=False,reason=str(error),covenant=None,budget=None,
            capabilities=dict(authoring=False,release=False,pack_import=False,lab_session=False))
        context['context_revision']=digest({'files':{key:hashlib.sha256(value).hexdigest() if value is not None else None for key,value in raw.items()},'unavailable':str(error)})
        result.update(creatures=[],lineage={'campaigns':[],'lives':[],'unavailable':str(error)})
    return result
