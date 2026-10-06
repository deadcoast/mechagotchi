"""X6 experimental descendant permissions; pure, mirrored implementation.

Contract: docs/development/cycle-38-operative-mutation-permissions.md.
Twelve rounds offer cell, organ and palette proposals. Rates are inherited
Bernoulli permissions, never acceptance promises. Symmetry is an additional
permission on a structural decline. Protected payloads are checked against
the original parent on every proposal. No reconstruction or repair fallback.
"""
from __future__ import annotations

from copy import deepcopy
import math
import random

ARM = 'operative_permissions_v1'
RATES = ('cell_mutation_rate', 'organ_shift_rate', 'palette_shift_rate', 'symmetry_break_rate')
OPERATORS = (('cell_mutation', RATES[0]), ('organ_shift', RATES[1]), ('palette_shift', RATES[2]))
DIRECTIONS = ((0,-1),(-1,0),(1,0),(0,1))


def symmetry_score(grid: dict) -> float:
    """Existing formal bakeoff role-aware horizontal reflection fraction."""
    width=grid['grid_size'][0]
    occupied={(cell['x'],cell['y'],cell.get('role')) for cell in grid['cells']}
    return sum((width-1-x,y,role) in occupied for x,y,role in occupied)/len(occupied) if occupied else 0.0


def _strict_permissions(parent, profile):
    def probability(value,label):
        if type(value) not in (int,float) or not math.isfinite(value) or not 0<=value<=1:
            raise ValueError(f'{label} must be a finite number in 0..1')
    for cell in parent['cells']:
        if type(cell.get('locked')) is not bool:
            raise ValueError('operative cell locked must be a boolean')
        probability(cell.get('mutation_weight'),'operative cell mutation_weight')
    for organ in parent['organs'].values():
        if type(organ.get('mutation_locked',False)) is not bool:
            raise ValueError('operative organ mutation_locked must be a boolean')
    for rate in RATES:
        probability(parent['mutation'][rate],rate)
        if profile is not None:
            probability(profile['mutation'][rate+'_max'],rate+'_max')


def _cells(grid):
    return {(cell['x'],cell['y']):cell for cell in grid['cells']}


def _protected(parent):
    protected={point:cell for point,cell in _cells(parent).items() if cell['locked']}
    organs={name:organ for name,organ in parent['organs'].items() if organ.get('mutation_locked',False)}
    original=_cells(parent)
    for organ in organs.values():
        for point in organ['cells']:
            if tuple(point) in original: protected[tuple(point)]=original[tuple(point)]
    return protected,organs


def _protection_errors(candidate, protected_cells, protected_organs):
    cells=_cells(candidate)
    errors=[f'protected cell {point[0]},{point[1]} changed' for point,cell in protected_cells.items() if cells.get(point)!=cell]
    errors.extend(f'protected organ {name} changed' for name,organ in protected_organs.items() if candidate['organs'].get(name)!=organ)
    return errors


def _membership_errors(grid):
    """Do not exploit the legacy validator's partial reference checks."""
    cells=_cells(grid); errors=[]
    for name,organ in grid['organs'].items():
        members=[tuple(point) for point in organ['cells']]
        if not members or len(members)!=len(set(members)):
            errors.append(f'organ {name} requires nonempty unique membership')
        for point in members:
            if point not in cells or cells[point].get('organ') not in (name,None):
                errors.append(f'organ {name} has inconsistent membership')
    for point,cell in cells.items():
        name=cell.get('organ')
        if name is not None and (name not in grid['organs'] or list(point) not in grid['organs'][name]['cells']):
            errors.append(f'cell {point} missing organ membership')
    return errors


def _weighted(rows,rng):
    total=sum(weight for _,weight in rows)
    if total<=0: return None
    pick=rng.random()*total; cumulative=0.0
    for value,weight in rows:
        cumulative+=weight
        if pick<cumulative: return value
    return rows[-1][0]


def _token(cell, token_specs):
    if cell is None: return '.'
    if cell['role']=='anchor' or (cell['role']=='body' and cell['animation_anchor']): return 'A'
    return next((token for token,spec in token_specs.items() if token!='A' and spec[0]==cell['role']), '.')


def _allowed(cells, point, token, size, adjacency, specs):
    x,y=point; width,height=size
    neighbors=(('right',(x-1,y),True),('right',(x+1,y),False),('down',(x,y-1),True),('down',(x,y+1),False))
    for direction,(nx,ny),left in neighbors:
        if not (0<=nx<width and 0<=ny<height): continue
        neighbor=_token(cells.get((nx,ny)),specs)
        source,target=(neighbor,token) if left else (token,neighbor)
        if adjacency[direction].get(source,{}).get(target,0)<=0: return False
    return True


def _organ_name(grid,source,spec,organ_specs):
    canonical=spec[2]; role,required=organ_specs[canonical]
    old=source.get('organ')
    if old in grid['organs'] and grid['organs'][old]['role']==role: return old
    if canonical in grid['organs'] and grid['organs'][canonical]['role']!=role: return None
    return canonical


def _reindex_changed_organs(grid,before,organ_specs):
    """Preserve original membership order and payload when membership is unchanged."""
    cells=_cells(grid)
    for name in list(grid['organs']):
        organ=grid['organs'][name]
        old_points=[tuple(p) for p in organ['cells']]
        wanted={point for point,cell in cells.items() if cell.get('organ')==name}
        # Preserve valid unassigned cells explicitly listed in the authored organ.
        wanted.update(point for point in old_points if point in cells and cells[point].get('organ') is None)
        if wanted==set(old_points): continue
        if not wanted and not organ.get('required',False):
            del grid['organs'][name]; continue
        organ['cells']=[list(point) for point in old_points if point in wanted]
        organ['cells'].extend([list(point) for point in sorted(wanted-set(old_points),key=lambda p:(p[1],p[0]))])
    for cell in grid['cells']:
        name=cell.get('organ')
        if name is not None and name not in grid['organs']:
            role,required=organ_specs[name]
            grid['organs'][name]={'role':role,'cells':[[c['x'],c['y']] for c in grid['cells'] if c.get('organ')==name],'required':required}


def _cell_proposal(grid,event,rng,protected,token_counts,adjacency,specs,organ_specs):
    cells=_cells(grid)
    eligible=[(point,float(cell['mutation_weight'])) for point,cell in sorted(cells.items(),key=lambda row:(row[0][1],row[0][0])) if point not in protected and cell['mutation_weight']>0]
    event['eligible_weights']=[{'source':list(point),'weight':weight} for point,weight in eligible]
    selected=_weighted(eligible,rng)
    if selected is None: return None,'no_eligible_weight'
    event['selected_source']=list(selected); source=cells[selected]; width,height=grid['grid_size']
    targets=[selected]+[(selected[0]+dx,selected[1]+dy) for dx,dy in DIRECTIONS if 0<=selected[0]+dx<width and 0<=selected[1]+dy<height and (selected[0]+dx,selected[1]+dy) not in cells]
    choices=[]
    for point in targets:
        growth=point!=selected
        for token,count in sorted(token_counts.items()):
            if count<=0 or (token=='.' and growth): continue
            if token=='.':
                if not _allowed(cells,point,'.',grid['grid_size'],adjacency,specs): continue
                candidate=deepcopy(grid); candidate['cells']=[c for c in candidate['cells'] if (c['x'],c['y'])!=selected]
            else:
                if token not in specs: continue
                spec=specs[token]; organ=_organ_name(grid,source,spec,organ_specs)
                if organ is None: continue
                replacement=deepcopy(source)
                replacement.update(x=point[0],y=point[1],role=spec[0],material=spec[1],organ=organ,visual=grid['palette']['colors'][min(spec[3],len(grid['palette']['colors'])-1)])
                if growth: replacement.update(animation_anchor=False,stress=0,damage=0)
                if not growth and replacement==source: continue
                actual_token=_token(replacement,specs)
                if not _allowed(cells,point,actual_token,grid['grid_size'],adjacency,specs): continue
                candidate=deepcopy(grid)
                if growth: candidate['cells'].append(replacement)
                else: candidate['cells']=[replacement if (c['x'],c['y'])==selected else c for c in candidate['cells']]
            _reindex_changed_organs(candidate,grid,organ_specs)
            choices.append(({'candidate':candidate,'token':token,'target':list(point),'kind':'growth' if growth else 'delete' if token=='.' else 'replace'},float(count)))
    selected_proposal=_weighted(choices,rng)
    if selected_proposal is None: return None,'no_learned_proposal'
    event.update(selected_token=selected_proposal['token'],selected_target=selected_proposal['target'],cell_operation=selected_proposal['kind'])
    return selected_proposal['candidate'],None


def _organ_proposal(grid,event,rng,protected):
    cells=_cells(grid); eligible=[]
    for name,organ in sorted(grid['organs'].items()):
        points=[tuple(point) for point in organ['cells']]
        if organ.get('mutation_locked',False) or not points or any(point not in cells or point in protected or cells[point]['mutation_weight']<=0 for point in points): continue
        eligible.append((name,sum(float(cells[point]['mutation_weight']) for point in points)))
    event['eligible_weights']=[{'source':name,'weight':weight} for name,weight in eligible]
    selected=_weighted(eligible,rng)
    if selected is None: return None,'no_eligible_weight'
    event['selected_source']=selected; direction=rng.choice(DIRECTIONS); event['direction']=list(direction)
    points={tuple(point) for point in grid['organs'][selected]['cells']}; width,height=grid['grid_size']
    shifted={(x+direction[0],y+direction[1]) for x,y in points}
    if any(not (0<=x<width and 0<=y<height) for x,y in shifted): return None,'out_of_bounds'
    if shifted & (set(cells)-points): return None,'overlap'
    candidate=deepcopy(grid)
    for cell in candidate['cells']:
        if (cell['x'],cell['y']) in points: cell['x']+=direction[0]; cell['y']+=direction[1]
    # Any authored overlapping unassigned memberships travel consistently too.
    for organ in candidate['organs'].values():
        organ['cells']=[[x+direction[0],y+direction[1]] if (x,y) in points else [x,y] for x,y in organ['cells']]
    return candidate,None


def _palette_proposal(grid,event,rng,profile,palettes):
    allowed=sorted(profile['grid']['allowed_palettes'] if profile is not None else palettes)
    choices=[name for name in allowed if name!=grid['palette']['palette_id'] and name in palettes]
    event['eligible_palettes']=choices
    if not choices: return None,'no_alternative_palette'
    chosen=rng.choice(choices); event['selected_source']=chosen
    candidate=deepcopy(grid); before=grid['palette']['colors']; after=list(palettes[chosen])
    candidate['palette'].update(palette_id=chosen,colors=after)
    if candidate['palette'].get('background_index',0)>=len(after): return None,'background_index_unavailable'
    for cell in candidate['cells']:
        if cell['visual'] not in before: return None,'unmapped_cell_color'
        index=before.index(cell['visual'])
        if index>=len(after): return None,'palette_position_unavailable'
        cell['visual']=after[index]
    return candidate,None


def operative_descendant(parent: dict, *, grid_id: str, rng_seed: int, slip_profile: dict | None,
        token_counts: dict, adjacency: dict, token_specs: dict, organ_specs: dict, palettes: dict,
        validate, align, proposal_rounds: int = 12) -> dict:
    """Generate a permission-bearing child; callbacks only validate proposals."""
    if type(proposal_rounds) is not int or proposal_rounds<0: raise ValueError('proposal_rounds must be a nonnegative integer')
    validation=validate(parent)
    if not validation.ok: raise ValueError('operative parent invalid: '+'; '.join(validation.errors))
    _strict_permissions(parent,slip_profile)
    errors=_membership_errors(parent)
    if errors: raise ValueError('operative parent membership invalid: '+'; '.join(errors))
    if slip_profile is not None:
        alignment=align(parent,slip_profile)
        if not alignment.ok: raise ValueError('operative parent cannot satisfy SLIP constraints: '+'; '.join(alignment.errors))
    if not isinstance(parent.get('metadata',{}),dict) or not isinstance(parent.get('lineage',{}),dict):
        raise ValueError('operative parent metadata and lineage must be objects')
    current=deepcopy(parent); protected_cells,protected_organs=_protected(parent); events=[]; changes=[]
    for round_index in range(proposal_rounds):
        for operator,rate in OPERATORS:
            rng=random.Random(f'{rng_seed}:{grid_id}:{ARM}:{round_index}:{operator}')
            probability=parent['mutation'][rate]
            event={'round':round_index,'operator':operator,'rate':probability,'rate_draw':None,'selected_source':None,'eligible_weights':[]}
            events.append(event)
            if probability==0: event['outcome']='rate_disabled'; continue
            event['rate_draw']=rng.random()
            if event['rate_draw']>=probability: event['outcome']='rate_not_selected'; continue
            if operator=='cell_mutation': proposal,reason=_cell_proposal(current,event,rng,protected_cells,token_counts,adjacency,token_specs,organ_specs)
            elif operator=='organ_shift': proposal,reason=_organ_proposal(current,event,rng,protected_cells)
            else: proposal,reason=_palette_proposal(current,event,rng,slip_profile,palettes)
            if proposal is None: event['outcome']=reason; continue
            delta={key:{'before':deepcopy(current[key]),'after':deepcopy(proposal[key])} for key in ('cells','organs','palette') if proposal[key]!=current[key]}
            if not delta: event['outcome']='unchanged_proposal'; continue
            event['proposed_delta']=delta
            errors=_protection_errors(proposal,protected_cells,protected_organs)
            if errors: event.update(outcome='protected_payload',errors=errors); continue
            if operator!='palette_shift':
                before,after=symmetry_score(current),symmetry_score(proposal)
                event.update(symmetry_before=before,symmetry_after=after)
                if after<before:
                    symmetry_rate=parent['mutation']['symmetry_break_rate']; draw=rng.random() if symmetry_rate>0 else None
                    event.update(symmetry_rate=symmetry_rate,symmetry_draw=draw)
                    if draw is None or draw>=symmetry_rate: event['outcome']='symmetry_permission'; continue
            validation=validate(proposal); errors=list(validation.errors)+_membership_errors(proposal)
            if errors: event.update(outcome='invalid_proposal',errors=errors); continue
            if slip_profile is not None:
                alignment=align(proposal,slip_profile)
                if not alignment.ok: event.update(outcome='unaligned_proposal',errors=list(alignment.errors)); continue
            current=proposal; event.update(outcome='accepted',delta=deepcopy(delta)); changes.append(f'{operator}:round_{round_index}')
    parent_lineage=parent.get('lineage',{})
    current['grid_id']=grid_id; current['parent_grid_id']=parent['grid_id']
    current.setdefault('lineage',{}).update(generation=parent_lineage.get('generation',0)+1,ancestor_ids=[*parent_lineage.get('ancestor_ids',[]),parent['grid_id']],mutation_events=changes)
    validation=validate(current)
    if not validation.ok: raise ValueError('operative descendant invalid: '+'; '.join(validation.errors))
    alignment=align(current,slip_profile) if slip_profile is not None else None
    if alignment is not None and not alignment.ok: raise ValueError('operative descendant misaligned: '+'; '.join(alignment.errors))
    trace={'generator_strategy':ARM,'mutation_arm':ARM,'proposal_source':'permission_gated_local_adjacency','rng_seed':rng_seed,'parent_grid_id':parent['grid_id'],
        'operator_opportunities':len(events),'proposal_attempts':sum('proposed_delta' in e for e in events),'proposal_rounds':proposal_rounds,
        'accepted_proposals':len(changes),'rejected_proposals':sum('proposed_delta' in e and e['outcome']!='accepted' for e in events),
        'outcome_counts':{outcome:sum(e['outcome']==outcome for e in events) for outcome in sorted({e['outcome'] for e in events})},
        'inherited_rates':deepcopy(parent['mutation']),'operator_events':events,'validation':{'ok':True,'errors':[]},
        'slip_alignment':{'checked':slip_profile is not None,'profile_id':slip_profile.get('profile_id') if slip_profile else None,'ok':True if alignment is not None else None,'errors':[]}}
    current.setdefault('metadata',{})['rng_seed']=rng_seed; current['metadata']['generation_trace']=trace
    return current
