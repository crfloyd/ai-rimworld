"""Run-local decisions and one replaceable evidence-bound transfer checkpoint. No game access."""
from pathlib import Path
from . import __version__
from .core import Error, atomic_json, atomic_text, canonical, digest, identifier, journal, lock, now, read_json, require_fields, slug
from .observations import freshness
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


def _handoff_packet(campaign, state):
    """Bounded transfer context; journals and the fact index already hold full history."""
    from .facts import entries
    from .safety import signals, deadlines
    risks, seen, missing = [], set(), []
    retired = campaign._retired()
    for entry in entries(state, risks=True):
        obs = entry['latest']
        if obs['id'] in retired or (obs['origin'] != 'live' and campaign.meta.get('session_id')):
            continue
        for risk in signals(obs):
            if risk['id'] in seen: continue
            seen.add(risk['id'])
            if len(risks) < 24:
                risks.append({k:risk[k] for k in ('id','kind','severity','evidence','scope') if k in risk})
        if obs['completeness'] != 'known' and len(missing) < 16:
            missing.append({'id':obs['id'],'tool':obs['tool'],'missing':obs.get('missing'),
                            'prior_evidence':(entry.get('last_known') or {}).get('id')})
    actions = [a for a in campaign._actions(open_only=True).values() if a['status'] in OPEN]
    issues = campaign.issue_reviews(state)
    return {'campaign_id':campaign.meta['id'], 'name':campaign.meta['name'],
            'objective':campaign.meta['objective'], 'tick':state['latest_tick'],
            'time_basis':state.get('tick_basis'), 'clock_warning':state.get('clock_warning'),
            'live_checked':False, 'active_risks':risks,
            'active_risk_records_total':len(seen), 'missing_coverage':missing,
            'pending_actions':[{k:a[k] for k in ('id','intent','family','status') if k in a} for a in actions],
            'issues':[{k:i[k] for k in ('id','title','next_action','restore_when','critical') if i.get(k) is not None} for i in issues],
            'deadlines':deadlines(campaign), 'checkpoint':campaign.checkpoints(state),
            'strategy':{'path':str(campaign.path/'STRATEGY.md'),
                        'digest':digest((campaign.path/'STRATEGY.md').read_text())},
            'evidence_index':str(campaign.path/'STATE.md'), 'control':runtime_snapshot(campaign)}


def _current_snapshot(campaign, reason, next_action, uncertainties, state=None):
    state = state or campaign._load()
    strategy = (campaign.path/'STRATEGY.md').read_text()
    packet_ = _handoff_packet(campaign, state)
    consequence_ids = [e['id'] for e in journal(campaign.path/'events.jsonl')[0]
                       if e.get('kind') in ('decision','outcome','incident','milestone','checkpoint')][-20:]
    return {'schema_version':2, 'id':identifier('handoff-'), 'campaign_id':campaign.meta['id'],
            'at':now(), 'tooling_version':__version__, 'reason':reason, 'next_action':next_action,
            'uncertainties':uncertainties,
            'rules':campaign.meta,
            'strategy':strategy, 'packet':packet_,
            'open_action_ids':[a['id'] for a in campaign._actions(open_only=True).values() if a['status'] in OPEN],
            'open_issue_ids':[i['id'] for i in campaign.issue_reviews(state)],
            'journal_offsets':{name:(campaign.path/name).stat().st_size for name in
                               ('observations.jsonl','actions.jsonl','issues.jsonl','events.jsonl')},
            'local_learning_digest':digest({str(p.relative_to(campaign.path)):p.read_text()
                                            for p in sorted((campaign.path/'knowledge').rglob('*.json'))}),
            'recent_consequence_ids':consequence_ids,
            'history':'Full observations, actions, issues, events and learning remain in their indexed campaign stores.'}


def handoff(campaign, reason, next_action, uncertainties):
    if not reason or not next_action or not uncertainties:
        raise Error('Record handoff reason, concrete next action and remaining uncertainties (including live freshness).')
    # One current transfer checkpoint replaces its predecessor. Journals retain history.
    with lock(campaign.path / '.handoff.lock'), lock(campaign.path / '.memory.lock'):
        campaign.meta['presentation_reset_at'] = now()
        atomic_json(campaign.path / 'campaign.json', campaign.meta)
        snapshot = _current_snapshot(campaign, reason, next_action, uncertainties, campaign._load())
        path = campaign.path/'handoffs/current.json'
        atomic_json(path, snapshot)
        atomic_text(campaign.path/'handoffs/current.md',
                    '# Current transfer checkpoint\n\n'+reason+'\n\nNext: '+next_action+
                    '\n\nUncertainties: '+uncertainties+'\n\nStructured checkpoint: [current.json](current.json)\n')
        atomic_json(campaign.path/'handoffs/latest.json', {'id':snapshot['id'],'path':'current.json','sha256':digest(snapshot)})
        return {'id': snapshot['id'], 'path': str(path),
                'next_action': next_action, 'live_checked': False}


def compact_handoffs(campaign, review):
    """Replace legacy snapshot copies with one current checkpoint, then remove the copies."""
    if not review: raise Error('Explain the authorized handoff cleanup.')
    base = campaign.path/'handoffs'
    with lock(campaign.path/'.handoff.lock'), lock(campaign.path/'.memory.lock'):
        legacy = sorted([*base.glob('handoff-*.json'), *base.glob('handoff-*.md')])
        before = sum(p.stat().st_size for p in legacy if p.is_file())
        latest = read_json(base/'latest.json') if (base/'latest.json').exists() else {}
        old_path = _checkpoint_path(base, latest) if latest else None
        old = read_json(old_path) if old_path and old_path.exists() else {}
        snapshot = _current_snapshot(campaign, old.get('reason','Memory cleanup'),
                                     old.get('next_action','Read current strategy and issues, then revalidate live state.'),
                                     old.get('uncertainties','Stored state is not live proof.'), campaign._load())
        snapshot['maintenance_review'] = review
        atomic_json(base/'current.json', snapshot)
        atomic_text(base/'current.md', '# Current transfer checkpoint\n\n'+snapshot['reason']+
                    '\n\nNext: '+snapshot['next_action']+'\n\nUncertainties: '+snapshot['uncertainties']+
                    '\n\nStructured checkpoint: [current.json](current.json)\n')
        atomic_json(base/'latest.json', {'id':snapshot['id'],'path':'current.json','sha256':digest(snapshot)})
        removed = 0
        for path in legacy:
            if path.parent != base or not path.name.startswith('handoff-'): raise Error('Unexpected handoff cleanup target.')
            path.unlink(); removed += 1
        after = sum(p.stat().st_size for p in (base/'current.json',base/'current.md',base/'latest.json'))
        return {'legacy_files_removed':removed,'bytes_removed':max(0,before-after),
                'current_checkpoint':str(base/'current.json'),'history_preserved_in':'campaign journals and indexed evidence'}


def _checkpoint_path(base, pointer):
    name = pointer.get('path') or (pointer.get('id','')+'.json')
    if Path(name).name != name or not (name == 'current.json' or (name.startswith('handoff-') and name.endswith('.json'))):
        raise Error('Invalid transfer-checkpoint path.')
    return base/name


def resume_snapshot(campaign, *, full=False):
    latest = campaign.path / 'handoffs/latest.json'
    if not latest.exists():
        return {'snapshot': None, 'warning': 'No transfer checkpoint yet. Reconstruct from current strategy/issues and indexed evidence; do not assume missing work was completed.'}
    pointer = read_json(latest); slug(pointer['id'])
    path = _checkpoint_path(campaign.path/'handoffs', pointer)
    snapshot = read_json(path)
    if snapshot.get('campaign_id') != campaign.meta['id'] or digest(snapshot) != pointer['sha256']:
        raise Error('Handoff identity or integrity mismatch.')
    changes = {name: (campaign.path / name).stat().st_size != size for name, size in snapshot['journal_offsets'].items()}
    changes['strategy'] = (campaign.path / 'STRATEGY.md').read_text() != snapshot['strategy']
    changes['rules_or_session'] = campaign.meta != snapshot['rules']
    changes['local_learning'] = snapshot.get('local_learning_digest') != digest({str(p.relative_to(campaign.path)): p.read_text() for p in sorted((campaign.path / 'knowledge').rglob('*.json'))})
    current_files={'rules':str(campaign.path/'CAMPAIGN.md'),'strategy':str(campaign.path/'STRATEGY.md'),
                   'issues':str(campaign.path/'ISSUES.md'),
                   'strategy_digest_at_handoff':digest(snapshot['strategy'])}
    return {'snapshot': {'id': snapshot['id'], 'path': str(path), 'at': snapshot['at'],
                         'next_action': snapshot['next_action'], 'uncertainties': snapshot['uncertainties'],
                         'current_files':current_files,
                         **({'rules':snapshot['rules'],'strategy':snapshot['strategy'],'packet':snapshot['packet']} if full else {'packet_index':{
                             'path':str(path), 'field':'packet',
                             'fields':list(snapshot['packet']),
                             'active_risk_records':len(snapshot['packet'].get('active_risks',[])),
                             'missing_coverage_records':len(snapshot['packet'].get('missing_coverage',[])),
                             'pending_action_records':len(snapshot['packet'].get('pending_actions',[])),
                             'detail_required':'Current files are authoritative. Load this compact checkpoint body only when its transfer pointers are needed; counts do not resolve risks or work.'}})},
            'changed_since_handoff': changes,
            'next': 'Use the returned handoff and changed-file flags; retrieve full historical detail only where the decision needs it. Live status, control and mutable facts require revalidation.'}
