"""Conservative visible-state signals shared by output and explicit batches.

This is a detector of review needs, not a claim that arbitrary mod hazards are understood.
"""
import math
from .core import Error, digest, now, require_fields
from .observations import freshness


def pawn_change_severity(rows):
    """The upstream pawnDamage field also contains healing and new drug effects."""
    if not isinstance(rows, list) or not rows: return 'unknown'
    uncertain = False
    new_conditions = False
    for row in rows:
        if not isinstance(row, dict):
            uncertain = True
            continue
        before, after = row.get('hpBefore'), row.get('hpAfter')
        numeric = all(type(v) in (int,float) and math.isfinite(v) for v in (before,after))
        if numeric and after < before: return 'critical'
        if not numeric or set(row) - {'name','hpBefore','hpAfter','newInjuries'}:
            uncertain = True
        injuries = row.get('newInjuries', [])
        if not isinstance(injuries,list) or any(not isinstance(v,str) for v in injuries):
            uncertain = True
        new_conditions = new_conditions or bool(injuries)
    return 'unknown' if uncertain else 'review' if new_conditions else 'info'


def signals(obs):
    d = obs['data']; result = []
    def add(kind, value, severity='review'):
        if kind in ('rejected', 'failedCells') and type(value) in (int, float) and value == 0: return
        if value is None or value is False or value == [] or value == {} or value == '': return
        global_signal = kind in ('_threatWarning', '_dialogOpen', 'notification', 'alert')
        identity_scope = {'mapIndex': obs.get('map_index')} if global_signal else obs['scope']
        result.append({'id': digest({'tool': None if global_signal else obs['tool'], 'scope': identity_scope, 'kind': kind, 'value': value}),
                       'kind': kind, 'severity': severity, 'value': value, 'evidence': obs['id'],
                       'scope': obs['scope']})
    if obs['completeness'] != 'known':
        add('coverage_loss', {'state': obs['completeness'], 'missing': obs.get('missing'), 'malformed': obs.get('malformed')}, 'unknown')
    for key in ('error', 'warning', 'warnings', 'rejected', 'failedCells', '_threatWarning',
                '_dialogOpen', '_mcpAdditionalText', '_protocolNotifications'):
        add(key, d.get(key), 'unknown' if key in ('error', '_protocolNotifications') else 'review')
    for item in d.get('_notifications', []) if isinstance(d.get('_notifications'), list) else []:
        add('notification', item, 'info' if isinstance(item, dict) and item.get('kind') == 'learning' else 'review')
    if d.get('_notifications') and not isinstance(d['_notifications'], list):
        add('unmodeled_notifications', d['_notifications'], 'unknown')
    alerts = d.get('activeAlerts', [])
    if isinstance(alerts, list):
        for alert in alerts:
            priority = str(alert.get('priority', 'unknown')).lower() if isinstance(alert, dict) else 'unknown'
            # RimMolt serializes Alert.Priority as its enum name. High is
            # reviewable, not synonymous with Critical; unknown priorities
            # remain review needs rather than silently becoming benign.
            severity = ('critical' if priority == 'critical' else
                        'review' if priority in ('low', 'medium', 'high') else 'unknown')
            add('alert', alert, severity)
    if obs['tool'] == 'wait_for_event':
        if d.get('pausedAfter') is not True: add('pause_unconfirmed', {'pausedAfter': d.get('pausedAfter', 'missing')}, 'critical')
        if d.get('cause') not in ('timeout', 'gameHours', 'gameTicks', 'gameDays', 'budget', 'timeElapsed'):
            add('wait_event', {'cause': d.get('cause'), 'event': d.get('event')})
        add('crisis_cap', d.get('crisisCap'), 'info')
    if '_delta' in d:
        delta = d.get('_delta', {})
        if isinstance(delta, dict):
            for key, value in delta.items():
                if key not in ('newItems', 'removedItems', 'newBuildings', 'removedBuildings'):
                    severity = pawn_change_severity(value) if key == 'pawnDamage' else ('critical' if 'damage' in key.lower() else 'unknown')
                    add('delta:' + key, value, severity)
        elif delta: add('unmodeled_delta', delta, 'unknown')
    if obs['tool'] == 'list_colonists' and isinstance(d.get('colonists'), list):
        for pawn in d['colonists']:
            if not isinstance(pawn, dict): add('unmodeled_colonist', pawn, 'unknown'); continue
            if pawn.get('downed') or pawn.get('dead') or pawn.get('mentalState'):
                add('colonist_crisis', pawn, 'critical')
            if type(pawn.get('mood')) in (int, float) and pawn['mood'] <= 20:
                add('low_colonist_mood', {k: pawn[k] for k in ('id', 'name', 'mood', 'job') if k in pawn})
    if obs['tool'] == 'get_pawn':
        health = d.get('health', d) if isinstance(d.get('health', d), dict) else d
        if health.get('dead') or health.get('downed'):
            add('incapacitated', {k: health[k] for k in ('id', 'name', 'dead', 'downed') if k in health}, 'critical')
        if type(health.get('overallHealthPercent')) in (int, float) and health['overallHealthPercent'] < 100:
            add('health_impairment', {k: health[k] for k in ('id', 'overallHealthPercent', 'painPercent') if k in health})
        if health.get('hediffs'):
            add('health_conditions', {'pawn': health.get('id', obs['args'].get('id')),
                'count': len(health['hediffs']), 'conditions_digest': digest(health['hediffs']),
                'detail': 'Retrieve health evidence for condition values before medical decisions.'}, 'review')
        for key in ('bleedRatePerDay', 'bleedRate', 'totalBleedRate', 'bleedingRate', 'mentalState', 'mentalBreak'):
            if health.get(key): add(key, health[key], 'critical')
        needs = d.get('needs')
        if isinstance(needs, dict): needs = needs.get('needs')
        if isinstance(needs, list):
            for need in needs:
                if not isinstance(need, dict): add('unknown_need', need, 'unknown'); continue
                label = str(need.get('label', '')).lower()
                if label in ('food', 'sleep', 'rest', 'mood'):
                    percent = need.get('percent')
                    if type(percent) not in (int, float): add('unknown_need_units', need, 'unknown')
                    elif percent <= {'food': 15, 'sleep': 10, 'rest': 10, 'mood': 20}[label]:
                        add('low_need', need, 'critical' if percent <= 5 else 'review')
    if obs['tool'] in ('list_things', 'get_area'):
        things = d.get('things', [])
        if isinstance(things, list):
            for t in things:
                if not isinstance(t, dict): add('unmodeled_thing', t, 'unknown'); continue
                hostile = t.get('hostile') or t.get('hostileToPlayer') or t.get('faction') == 'Hostile'
                if hostile or t.get('burning') or t.get('onFire') or t.get('downed'):
                    add('visible_thing_risk', t, 'critical')
    if obs['tool'] == 'list_fires': add('fires', d.get('fires'), 'critical')
    return result






def assess(campaign, observations):
    risks = []
    for obs in observations:
        for risk in signals(obs):
            risks.append(risk)
    blockers = [r for r in risks if r['severity'] != 'info']
    return {'stop': bool(blockers), 'risks': risks, 'blockers': blockers,
            'coverage': 'Only the supplied observations; missing required queries are checked by the execution contract.'}


def deadlines(campaign, explicit=None):
    """Only typed hard deadlines stop time; a soft reminder remains a visible review task."""
    state = campaign.state(); tick = state['latest_tick']
    hard = [{'tick': explicit, 'source': 'caller'}] if explicit is not None else []
    reviews = []
    for issue in campaign.issue_reviews(state):
        deadline = issue.get('deadline')
        if deadline and deadline.get('kind') == 'hard':
            hard.append({'tick': deadline['tick'], 'source': issue['id'], 'reason': deadline['reason']})
        if issue.get('revisit_due') or issue.get('review_clock_unknown') or issue.get('recurring'): reviews.append(issue['id'])
    earliest = min((d['tick'] for d in hard), default=None)
    return {'earliest': earliest, 'hard': hard, 'due': earliest is not None and (tick is None or tick >= earliest),
            'soft_reviews': reviews}
