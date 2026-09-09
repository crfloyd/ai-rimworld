"""Run-local decision/outcome links and immutable, evidence-bound handoffs. No game access."""
from pathlib import Path
from . import __version__
from .core import Error, atomic_json, atomic_text, canonical, digest, identifier, journal, lock, now, read_json, require_fields, slug
from .observations import compact, freshness
from .memory import OPEN


def event_index(campaign):
    return {e['id']: e for e in journal(campaign.path / 'events.jsonl')[0]}


def evidence_exists(campaign, values):
    events = event_index(campaign)
    if not isinstance(values, list) or not values: raise Error('Supply evidence IDs from this run.')
    for value in values:
        if value not in events and not campaign.has_observation(value): raise Error('Unknown run evidence: ' + str(value))


def decide(campaign, value):
    require_fields(value, ('summary', 'rationale', 'expected_result', 'risks', 'alternatives', 'reconsider_when', 'evidence'))
    evidence_exists(campaign, value['evidence'])
    for dependency in value.get('requires_completed', []):
        if dependency not in campaign._actions(): raise Error('Decision references an unknown action dependency.')
    return campaign.event(dict(value, kind='decision'))


def outcome(campaign, value):
    require_fields(value, ('decision', 'summary', 'result', 'observed', 'evidence', 'review'))
    decision = event_index(campaign).get(value['decision'])
    if not decision or decision.get('kind') != 'decision': raise Error('Outcome must refer to a decision in this run.')
    if value['result'] not in ('expected', 'unexpected', 'failure', 'inconclusive'):
        raise Error('Result must be expected, unexpected, failure or inconclusive.')
    evidence_exists(campaign, value['evidence'])
    result = campaign.event(dict(value, kind='outcome', expected_result=decision['expected_result']))
    if value['result'] != 'expected' or value.get('review_lesson'):
        candidate = {'id': result['id'], 'status': 'needs_review', 'decision': decision['id'],
                     'outcome': result['id'], 'expected': decision['expected_result'],
                     'observed': value['observed'], 'evidence': value['evidence'],
                     'topics': decision.get('topics', []), 'campaign_id': campaign.meta['id'],
                     'next': 'Investigate cause and counterexamples; save a scoped run lesson or dismiss with evidence.'}
        atomic_json(campaign.path / 'knowledge' / 'candidates' / (result['id'] + '.json'), candidate)
    return result


def review_candidate(campaign, candidate_id, status, review, lesson_id=None):
    slug(candidate_id)
    if status not in ('learned', 'dismissed', 'needs_evidence') or not review:
        raise Error('Review as learned, dismissed or needs_evidence with a reason.')
    path = campaign.path / 'knowledge' / 'candidates' / (candidate_id + '.json')
    value = read_json(path)
    if value.get('campaign_id') != campaign.meta['id']: raise Error('Candidate belongs to another run.')
    if status == 'learned':
        lesson = read_json(campaign.path / 'knowledge' / 'lessons' / (slug(lesson_id) + '.json'))
        if lesson.get('campaign_id') != campaign.meta['id']: raise Error('Use a run-local lesson.')
        if not any(e.get('outcome') == value['outcome'] for e in lesson['evidence']):
            raise Error('The lesson must cite this outcome before closing its review candidate.')
    event = campaign.event({'kind': 'lesson_candidate_review', 'summary': review, 'candidate': candidate_id,
                            'status': status, 'lesson': lesson_id})
    atomic_json(path, dict(value, status=status, review=review, review_event=event['id'], lesson=lesson_id))
    return event


def incident(campaign, value):
    require_fields(value, ('key', 'episode', 'summary', 'evidence'))
    evidence_exists(campaign, value['evidence'])
    events = event_index(campaign)
    existing = next((e for e in events.values() if e.get('kind') == 'incident' and
                     e.get('key') == value['key'] and e.get('episode') == value['episode']), None)
    if existing: return dict(existing, already_recorded=True)
    return campaign.event(dict(value, kind='incident'))


def learning_packet(campaign, topic=None):
    events = event_index(campaign)
    outcomes = {}
    for e in events.values():
        if e.get('kind') == 'outcome': outcomes[e['decision']] = e
    decisions = []
    for e in events.values():
        if e.get('kind') != 'decision': continue
        if topic and e.get('topics') and topic not in e['topics']: continue
        if e['id'] not in outcomes:
            decisions.append({k: e[k] for k in ('id', 'summary', 'rationale', 'expected_result', 'reconsider_when', 'requires_completed') if k in e})
    candidates = []
    for p in sorted((campaign.path / 'knowledge' / 'candidates').glob('*.json')):
        c = read_json(p)
        if c['status'] in ('learned', 'dismissed'): continue
        if topic and c.get('topics') and topic not in c['topics']: continue
        candidates.append(dict(c, path=str(p)))
    return {'decisions_awaiting_outcome': decisions, 'lesson_reviews': candidates}


def runtime_snapshot(campaign):
    from .mcp import endpoint_key
    endpoint = campaign.meta.get('endpoint', 'http://localhost:8787/mcp')
    base = campaign.root / '.runtime' / digest(endpoint_key(endpoint))
    result = {'endpoint': endpoint, 'live_checked': False}
    for name in ('owner', 'pending', 'composition', 'session', 'pause-uncertain'):
        path = base / (name + '.json')
        if path.exists():
            data = read_json(path)
            if name == 'owner': data = {k: v for k, v in data.items() if k != 'token'}
            result[name] = data
    for name in ('pending','composition'):
        pending = result.get(name, {})
        if pending.get('request_id'):
            path = base / (pending['request_id'] + '.handle.json')
            if path.exists():
                handle=read_json(path)
                pending['orchestrator_handle']=handle
                if name=='pending':result['handle']=handle
    return result


def packet(campaign, topic=None, entity=None):
    from .knowledge import context
    state = campaign.state()
    actions = [a for a in campaign._actions(open_only=True).values() if a['status'] in OPEN]
    issues = campaign.issue_reviews(state)
    risks, missing = [], []
    from .safety import signals, deadlines
    from .facts import entries
    retired = campaign._retired()
    for entry in entries(state, risks=True):
        obs = entry['latest']
        if obs['id'] in retired: continue
        if obs['origin'] != 'live' and campaign.meta.get('session_id'): continue
        flags = signals(obs)
        if flags: risks.extend(dict(flag, freshness=freshness(obs, state, campaign.meta)) for flag in flags)
        if obs['completeness'] != 'known':
            if entry.get('last_known'):
                old = entry['last_known']
                risks.extend(dict(flag, freshness={'revalidate': True, 'reasons': ['Latest scoped read failed; prior risk unresolved']})
                             for flag in signals(old))
            missing.append({'id': obs['id'], 'missing': obs['missing'], 'prior_evidence': (entry.get('last_known') or {}).get('id')})
    result = {'campaign_id': campaign.meta['id'], 'name': campaign.meta['name'],
              'objective': campaign.meta['objective'], 'tick': state['latest_tick'],
              'time_basis': state.get('tick_basis'), 'clock_warning': state.get('clock_warning'),
              'live_checked': False, 'active_risks': risks, 'missing_coverage': missing,
              'pending_actions': [{k: a[k] for k in ('id', 'intent', 'family', 'status', 'check', 'evidence', 'reason', 'requires_completed') if k in a} for a in actions],
              'issues': [{k: i[k] for k in ('id', 'title', 'rationale', 'next_action', 'blocker', 'alternative', 'deadline', 'revisit_due', 'recurring', 'restore_when') if k in i} for i in issues],
              'deadlines': deadlines(campaign), 'checkpoint': campaign.checkpoints(state),
              'strategy': {'path': str(campaign.path / 'STRATEGY.md'), 'digest': digest((campaign.path / 'STRATEGY.md').read_text())},
              'learning': learning_packet(campaign, topic), 'control': runtime_snapshot(campaign)}
    if topic: result['decision_context'] = context(campaign, topic, entity)
    if not state['facts']: result['missing_coverage'].append({'reason': 'No observations; all live state unknown.'})
    return result


def handoff(campaign, reason, next_action, uncertainties):
    if not reason or not next_action or not uncertainties:
        raise Error('Record handoff reason, concrete next action and remaining uncertainties (including live freshness).')
    # Serialize all local writers while capturing the exact journal boundaries and strategy version.
    with lock(campaign.path / '.handoff.lock'), lock(campaign.path / '.memory.lock'):
        campaign.meta['presentation_reset_at'] = now()
        atomic_json(campaign.path / 'campaign.json', campaign.meta)
        snapshot_id = identifier('handoff-')
        current = packet(campaign)
        with lock(campaign.path / '.memory.lock'):
            state = campaign._load()
            snapshot = {'id': snapshot_id, 'campaign_id': campaign.meta['id'], 'at': now(),
                        'tooling_version': __version__, 'reason': reason, 'next_action': next_action,
                        'uncertainties': uncertainties, 'rules': campaign.meta,
                        'strategy': (campaign.path / 'STRATEGY.md').read_text(), 'packet': current,
                        'open_actions': [a for a in campaign._actions(open_only=True).values() if a['status'] in OPEN],
                        'open_issues': campaign.issue_reviews(state),
                        'facts': [{ 'view': compact(e['latest']),
                                    'freshness': freshness(e['latest'], state, campaign.meta),
                                    'last_known': (e.get('last_known') or {}).get('id') } for e in state['facts'].values()],
                        'journal_offsets': {name: (campaign.path / name).stat().st_size for name in
                                            ('observations.jsonl', 'actions.jsonl', 'issues.jsonl', 'events.jsonl')}}
            # Keep the selected lesson revisions available as of handoff, including unresolved cautions.
            from .knowledge import TOPICS, run_knowledge
            snapshot['knowledge'] = {topic: run_knowledge(campaign, topic, full=True) for topic in TOPICS}
            snapshot['local_learning_digest'] = digest({str(p.relative_to(campaign.path)): p.read_text() for p in sorted((campaign.path / 'knowledge').rglob('*.json'))})
            snapshot['recent_consequences'] = [e for e in journal(campaign.path / 'events.jsonl')[0]
                                                if e.get('kind') in ('decision', 'outcome', 'incident', 'milestone', 'checkpoint')][-20:]
            snapshot['historical_tail_note'] = 'Twenty recent consequences are orientation only. All unresolved decisions/issues/actions are included without a count cap; full history remains in events.jsonl.'
            atomic_json(campaign.path / 'handoffs' / (snapshot_id + '.json'), snapshot)
            atomic_text(campaign.path / 'handoffs' / (snapshot_id + '.md'),
                        '# Run handoff\n\n' + reason + '\n\nNext: ' + next_action + '\n\nUncertainties: ' + uncertainties +
                        '\n\nFull immutable snapshot: [' + snapshot_id + '.json](' + snapshot_id + '.json)\n')
            atomic_json(campaign.path / 'handoffs/latest.json', {'id': snapshot_id, 'sha256': digest(snapshot)})
        return {'id': snapshot_id, 'path': str(campaign.path / 'handoffs' / (snapshot_id + '.json')),
                'next_action': next_action, 'live_checked': False}


def resume_snapshot(campaign, *, full=False):
    latest = campaign.path / 'handoffs/latest.json'
    if not latest.exists():
        return {'snapshot': None, 'warning': 'No immutable handoff yet. Reconstruct from current packet and original rules/strategy; do not assume missing work was completed.'}
    pointer = read_json(latest); slug(pointer['id'])
    path = campaign.path / 'handoffs' / (pointer['id'] + '.json')
    snapshot = read_json(path)
    if snapshot.get('campaign_id') != campaign.meta['id'] or digest(snapshot) != pointer['sha256']:
        raise Error('Handoff identity or integrity mismatch.')
    changes = {name: (campaign.path / name).stat().st_size != size for name, size in snapshot['journal_offsets'].items()}
    changes['strategy'] = (campaign.path / 'STRATEGY.md').read_text() != snapshot['strategy']
    changes['rules_or_session'] = campaign.meta != snapshot['rules']
    changes['local_learning'] = snapshot.get('local_learning_digest') != digest({str(p.relative_to(campaign.path)): p.read_text() for p in sorted((campaign.path / 'knowledge').rglob('*.json'))})
    return {'snapshot': {'id': snapshot['id'], 'path': str(path), 'at': snapshot['at'],
                         'next_action': snapshot['next_action'], 'uncertainties': snapshot['uncertainties'],
                         'rules': snapshot['rules'], 'strategy': snapshot['strategy'],
                         **({'packet':snapshot['packet']} if full else {'packet_index':{
                             'path':str(path), 'field':'packet',
                             'fields':list(snapshot['packet']),
                             'active_risk_records':len(snapshot['packet'].get('active_risks',[])),
                             'missing_coverage_records':len(snapshot['packet'].get('missing_coverage',[])),
                             'pending_action_records':len(snapshot['packet'].get('pending_actions',[])),
                             'detail_required':'Read current strategy/issues and retrieve relevant original evidence when needed; full STATE/packets are optional indexes, and counts do not resolve risks or work.'}})},
            'changed_since_handoff': changes,
            'next': 'Use the returned handoff and changed-file flags; retrieve full historical detail only where the decision needs it. Live status, control and mutable facts require revalidation.'}
