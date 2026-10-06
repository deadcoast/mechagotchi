"""Read-only preparation wording, derived from campaign authority and saved choices."""
from mecha_game.campaign import UNLOCK_THRESHOLDS
from mecha_game.covenant import ORGAN_ROLE_UNLOCK_ORDER


def role_progress_lines(campaign):
    active=campaign.campaign['slip_profile']['grid'].get('allowed_organ_roles')
    budget=campaign.budget()['allowed_organ_roles']
    if active is None:
        return ['Roles: unrestricted by this base covenant; no role spend is needed.']
    lines=['Roles: '+', '.join(active)]
    next_role=next((role for role in ORGAN_ROLE_UNLOCK_ORDER if role not in active),None)
    if next_role is None:
        return [*lines,'All supported roles are already available in this covenant.']
    tier=ORGAN_ROLE_UNLOCK_ORDER.index(next_role)+1
    threshold=UNLOCK_THRESHOLDS['niche_mastery']['tiers'][tier-1]
    ready=budget is None or next_role in budget
    lines.append(f"Next role: {next_role} {'ready to spend [5]' if ready else 'locked'}; "
                 f'niche mastery tier {tier}, {threshold} niches.')
    return lines


def next_era_line(weather, staged_count, *, population_policy, survival_regime, density, body_response="legacy"):
    policy={'legacy_archive':'archive continuity','generation_survivors_v1':'living generations'}.get(
        population_policy,'population unavailable')
    regime={'sheltered':'sheltered','stress_probe':'stress probe'}.get(survival_regime,str(survival_regime))
    return (f'NEXT ERA [{weather}]: {staged_count} staged; {policy}; {regime}; '
            f"density {'on' if density else 'off'}"
            + ("; body workload-v1" if body_response == "workload-v1" else ""))


def covenant_change_summary(before,after):
    old=before['slip_profile'];new=after['slip_profile'];changes=[]
    for field,label in (('allowed_organ_roles','role'),('allowed_palettes','palette')):
        previous=old['grid'].get(field);current=new['grid'].get(field)
        if previous is not None and current is not None:
            added=[item for item in current if item not in previous]
            removed=[item for item in previous if item not in current]
            if added: changes.append(f"{label} {', '.join(added)} added")
            if removed: changes.append(f"{label} {', '.join(removed)} removed")
    old_depth=old.get('deliberation',{}).get('max_ticks',0)
    new_depth=new.get('deliberation',{}).get('max_ticks',0)
    if old_depth != new_depth: changes.append(f'thinking depth {new_depth}')
    for key in ('population','generations'):
        if before['era_config'][key] != after['era_config'][key]:
            changes.append(f"{key} {after['era_config'][key]}")
    if not changes:
        if before == after: return 'Covenant unchanged.'
        return 'Covenant selection saved.'
    return 'Covenant saved: '+'; '.join(changes)+'.'


def preparation_notice(commit):
    if commit is None: return None
    if commit.error:
        return 'Preparation recovery required: '+str(commit.error)+' C/U inspects a paired checkpoint.'
    if commit.pending is not None:
        summary=commit.pending.get('summary') or 'Captured preparation'
        if summary.startswith('Covenant saved: '):
            summary='Covenant change: '+summary[len('Covenant saved: '):]
        elif summary == 'Covenant selection saved.':
            summary='Covenant selection'
        return f'PREPARATION awaiting finish: {summary} C then E finishes the saved choice; no era runs.'
    return None
