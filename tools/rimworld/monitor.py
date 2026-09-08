"""Finite routine continuation with a separate pause-only process guardian.

No tactical decisions, no mutation replay, no unbounded play, no hidden game access.
A disconnected or hung server can defeat any client-side pause: preserve that uncertainty.
"""
import argparse
import contextlib
import os
from pathlib import Path
import subprocess
import sys
import time

from .core import Error, alive, atomic_json, digest, identifier, lock, now, read_json, require_fields, slug
from .control import Control, effect
from .mcp import validate
from .observations import freshness, matches, pause_confirmed
from .safety import assess, deadlines


def qualify(control, token, wait_id, pause_id, review):
    control._owner(token); control._no_pending()
    if not review: raise Error('Review current catalog, finite waits, pause behavior and client-loss limitations.')
    campaign = control.campaign
    wait, pause = (campaign.observation(i) for i in (wait_id, pause_id))
    for obs in (wait, pause):
        if obs['origin'] != 'live' or obs['session_id'] != campaign.meta.get('session_id') or obs['completeness'] != 'known':
            raise Error('Qualification requires complete live evidence from this session.')
    if wait['tool'] != 'wait_for_event' or wait['data'].get('pausedAfter') is not True or wait['args'].get('pause') != 'always':
        raise Error('Verify a bounded wait with pause=always actually paused.')
    if pause['tool'] != 'set_speed' or pause['args'] != {'action': 'pause'} or not pause_confirmed(pause):
        raise Error('Verify the ordinary set_speed pause action actually paused.')
    if freshness(pause, campaign.state(), campaign.meta)['revalidate']: raise Error('Pause qualification evidence is stale.')
    catalog = read_json(campaign.path / 'raw/catalog.json')
    for tool, args in [('set_speed', {'action': 'pause'}), ('wait_for_event', {'maxSeconds': 5, 'maxGameHours': 0.1, 'pause': 'always'})]:
        if tool not in catalog['tools']: raise Error('Required finite-wait/pause capability missing.')
        validate(catalog['tools'][tool]['inputSchema'], args)
    profile = {'session_id': campaign.meta['session_id'], 'catalog_digest': catalog['schema_digest'],
               'evidence': [wait_id, pause_id], 'review': review, 'at': now(),
               'limitations': 'Empirical session qualification, not a proof of all mod/server failure behavior. Requalify after reconnect or schema/settings change.'}
    atomic_json(campaign.path / 'reference/monitor-qualification.json', profile)
    return profile


def create_plan(campaign, spec):
    require_fields(spec, ('purpose', 'rationale', 'expected_progress', 'reconsider_when', 'queries',
                         'watch_pawns', 'watch_maps', 'max_cycles', 'max_wall_seconds', 'max_game_hours'))
    if spec.get('risk', 'routine') != 'routine': raise Error('Automatic continuation is routine-only; combat/unstable medicine remain supervised.')
    for key, lo, hi in [('max_cycles', 1, 20), ('max_wall_seconds', 10, 600), ('max_game_hours', 0.01, 6),
                        ('wait_seconds', 5, 40), ('wait_hours', 0.01, 1)]:
        value = spec.get(key, 20 if key == 'wait_seconds' else (1 if key == 'wait_hours' else None))
        import math
        if type(value) not in (int, float) or not math.isfinite(value) or not lo <= value <= hi:
            raise Error(f'{key} must be finite within {lo}–{hi}.')
        if key in ('max_cycles', 'wait_seconds') and type(value) is not int: raise Error(key + ' must be an integer.')
    if not isinstance(spec.get('watch_patients',[]),list) or not all(isinstance(p,str) and p for p in spec.get('watch_patients',[])): raise Error('watch_patients must contain explicit additional pawn IDs.')
    if not isinstance(spec['queries'], list) or not 1 <= len(spec['queries']) <= 32: raise Error('Plan needs 1–32 bounded read queries.')
    if not all(isinstance(i, str) for i in spec['watch_pawns']) or not all(type(i) is int for i in spec['watch_maps']):
        raise Error('Record explicit pawn IDs and map indices reviewed for this run.')
    if not campaign.meta.get('binding') or campaign.meta['binding']['expected'].get('loaded') is not True:
        raise Error('Bind the loaded authorized game before planning continuation.')
    catalog = read_json(campaign.path / 'raw/catalog.json')
    for q in spec['queries']:
        require_fields(q, ('tool',))
        every=q.get('every_cycles',1)
        if type(every) is not int or not 1<=every<=20:raise Error('Query cadence must be 1–20 cycles.')
        if every!=1 and q['tool'] in ('get_status','get_alerts','list_colonists','get_pawn','list_fires','list_things'):
            raise Error('Safety coverage must be refreshed every cycle; stagger supplementary queries only.')
        if q.get('reviewed_evidence'):
            reviewed=campaign.observation(q['reviewed_evidence'])
            if reviewed['tool']!=q['tool'] or reviewed['args']!=q.get('args',{}) or reviewed['origin']!='live' or reviewed['session_id']!=campaign.meta['session_id']:
                raise Error('Query shape review must match this session and exact query.')
        if q['tool'] not in catalog['tools'] or not effect(q['tool'], q.get('args', {})).startswith('inspection'):
            raise Error('Continuation queries must be classified ordinary reads; actions belong in act/batch before the plan.')
        validate(catalog['tools'][q['tool']]['inputSchema'], q.get('args', {}))
    if not any(q['tool'] == 'get_status' and not q.get('args') for q in spec['queries']):
        raise Error('Continuation must inspect get_status every cycle; default bundles can supply alerts/roster.')
    from .outcomes import validate_check
    for check in spec.get('continue_checks', []) + spec.get('stop_checks', []): validate_check(check)
    plan = dict(spec, id=identifier('plan-'), campaign_id=campaign.meta['id'], session_id=campaign.meta['session_id'],
                catalog_digest=catalog['schema_digest'], created_at=now(), risk='routine')
    atomic_json(campaign.path / 'plans' / (plan['id'] + '.json'), plan)
    campaign.event({'kind': 'continuation_plan', 'summary': spec['purpose'], 'plan': plan['id'], 'rationale': spec['rationale']})
    return plan


def coverage(campaign, observations, plan):
    """All watched pawns/maps must still exist and have fresh, complete danger/medical reads."""
    missing = []
    state = campaign.state()
    def find(tool, args=None):
        candidates = [o for o in observations if o['tool'] == tool and all(o['args'].get(k) == v for k,v in (args or {}).items())]
        valid = [o for o in candidates if not freshness(o, state, campaign.meta)['revalidate']]
        if not valid: missing.append({'tool': tool, 'args': args or {}, 'reason': 'Missing, stale or incomplete required coverage'})
        return valid[-1]['data'] if valid else None
    status = find('get_status'); find('get_alerts'); roster = find('list_colonists')
    if status and (status.get('loaded') is not True or {m.get('mapIndex') for m in status['maps']} != set(plan['watch_maps'])):
        missing.append({'reason': 'Loaded game/map roster changed; reason about new context.'})
    if roster and {p.get('id') for p in roster.get('colonists', [])} != set(plan['watch_pawns']):
        missing.append({'reason': 'Colonist roster changed or IDs missing; recruitment/death/transfer needs review.'})
    for pawn in dict.fromkeys(plan['watch_pawns']+plan.get('watch_patients',[])):
        find('get_pawn', {'id': pawn, 'tab': 'health'})
        find('get_pawn', {'id': pawn, 'tab': 'needs'})
    for m in plan['watch_maps']:
        find('list_fires', {'mapIndex': m})
        danger = find('list_things', {'mapIndex': m, 'category': 'pawn'})
        query = next((o for o in observations if o['tool']=='list_things' and o['args'].get('mapIndex')==m and o['args'].get('category')=='pawn'), None)
        if query and any(k in query['args'] for k in ('defName', 'nearId', 'nearX', 'nearZ', 'radius', 'faction')):
            missing.append({'reason': 'Threat coverage must include all visible pawns on the map, without spatial/faction filters.', 'mapIndex': m})
        if danger is not None and not isinstance(danger.get('things'), list):
            missing.append({'reason': 'Threat query did not return an actual list of visible pawns.', 'mapIndex': m})
        if danger:
            for thing in danger.get('things', []):
                if not isinstance(thing, dict) or 'hostile' not in thing:
                    missing.append({'reason': 'Pawn hostility is not observable in this response shape.', 'mapIndex': m}); break
    return missing


def checks_match(check, observations):
    checks = check.get('checks', [check])
    results = []
    for c in checks:
        values = [matches(o, c) for o in observations]
        results.append(True if True in values else (False if False in values else None))
    return True if all(v is True for v in results) else (False if False in results else None)


def unexpected_progress(obs, plan):
    delta = obs['data'].get('_delta', {})
    allowed = plan.get('expected_changes', {})
    unexpected = []
    for key in ('newItems', 'removedItems', 'newBuildings', 'removedBuildings'):
        rows = delta.get(key, []) if isinstance(delta, dict) else []
        if not isinstance(rows, list): unexpected.append({'kind': key, 'reason': 'Unknown change shape'}); continue
        for row in rows:
            rule = allowed.get(key, {}).get(row.get('def')) if isinstance(row, dict) else None
            if not isinstance(rule, dict) or type(row.get('count')) not in (int, float) or abs(row['count']) > rule.get('max_count_per_wait', 0):
                unexpected.append({'kind': key, 'change': row})
    if obs['data'].get('weatherChanged'): unexpected.append({'weatherChanged': obs['data']['weatherChanged']})
    return unexpected


class Guardian:
    def __init__(self, control, plan_id): self.control, self.plan_id, self.process = control, plan_id, None
    def start(self):
        root = self.control.campaign.root
        log = self.control.path / ('guardian-' + self.plan_id + '.log')
        with log.open('ab') as stream:
            self.process = subprocess.Popen([sys.executable, '-B', '-m', 'tools.rimworld.monitor', '--watchdog',
                '--root', str(root), '--run', self.control.campaign.meta['name'], '--id', self.plan_id],
                cwd=root, stdin=subprocess.DEVNULL, stdout=stream, stderr=stream, start_new_session=True)
        ready = self.control.path / ('guardian-' + self.plan_id + '.json')
        deadline = time.monotonic() + 5
        while time.monotonic() < deadline and self.process.poll() is None:
            if ready.exists() and read_json(ready).get('pid') == self.process.pid: return
            time.sleep(0.02)
        raise Error('Independent pause guardian did not start; no time may advance.')
    def healthy(self): return self.process is not None and self.process.poll() is None
    def finish(self):
        if self.process:
            try: self.process.wait(timeout=2)
            except subprocess.TimeoutExpired:
                # Do not kill a guardian potentially performing emergency pause.
                pass


class Monitor:
    def __init__(self, control, guardian_factory=Guardian):
        self.control = control; self.campaign = control.campaign; self.guardian_factory = guardian_factory

    def run(self, token, plan_id):
        c = self.control; campaign = self.campaign
        plan = read_json(campaign.path / 'plans' / (slug(plan_id) + '.json'))
        qualification = read_json(campaign.path / 'reference/monitor-qualification.json')
        catalog = read_json(campaign.path / 'raw/catalog.json')
        for doc in (plan, qualification):
            if doc.get('session_id') != campaign.meta.get('session_id') or doc.get('catalog_digest') != catalog['schema_digest']:
                raise Error('Session/schema changed; requalify and review a fresh plan.')
        if plan.get('campaign_id') != campaign.meta['id']: raise Error('Plan belongs to another run.')
        lease_path = c.path / 'monitor.json'
        with lock(c.path / 'monitor.lock'):
            c._owner(token); c._no_pending()
            execution_path = campaign.path / 'plans' / (plan_id + '.execution.json')
            if execution_path.exists(): raise Error('This finite plan was already started. Review results and create a new plan; do not replay it.')
            if lease_path.exists() and read_json(lease_path).get('status') == 'running': raise Error('A monitor is already recorded; inspect its real handle first.')
            record = {'id': plan_id, 'campaign_id': campaign.meta['id'], 'pid': os.getpid(), 'status': 'running',
                      'started_at': now(), 'heartbeat': time.time(), 'expires_at': time.time()+plan['max_wall_seconds'],
                      'monotonic_deadline': time.monotonic()+plan['max_wall_seconds'], 'phase': 'starting', 'cycles': 0}
            atomic_json(lease_path, record)
            atomic_json(execution_path, record)
            guardian = self.guardian_factory(c, plan_id)
            stopped = 'finite budget'; details = []; last_pause = None
            start_tick = campaign.state()['latest_tick']; observations = []
            def heartbeat(phase):
                current = read_json(lease_path)
                if current.get('status') != 'running' or current.get('id') != plan_id: raise Error('Guardian stopped or replaced this monitor.')
                if (c.path / (plan_id + '.stop.json')).exists(): raise Error('Explicit monitor stop requested.')
                if not guardian.healthy(): raise Error('Pause guardian exited; stop continuation.')
                if time.monotonic() >= record['monotonic_deadline']: raise Error('Finite monitor wall budget expired.')
                record.update(heartbeat=time.time(), phase=phase)
                atomic_json(lease_path, record)
            try:
                guardian.start()
                while record['cycles'] < plan['max_cycles']:
                    observations = []
                    notices=[]
                    for query in plan['queries']:
                        if record['cycles'] % query.get('every_cycles',1): continue
                        heartbeat('inspection')
                        result = c.call(token, query['tool'], query.get('args', {}))
                        if result.get('structure_changes'):notices.append({'tool':query['tool'],'evidence':result['id'],'novelty':result['structure_changes']})
                        if campaign.observation(result['id']).get('coverage',{}).get('model')=='unmodeled' and not query.get('reviewed_evidence'):
                            notices.append({'tool':query['tool'],'evidence':result['id'],'reason':'Unmodeled query needs agent shape review'})
                        if query.get('reviewed_evidence'):
                            from .observations import structure
                            baseline=campaign.observation(query['reviewed_evidence'])
                            current=campaign.observation(result['id'])
                            added=sorted(structure(current['data'])-structure(baseline['data']))
                            if added:notices.append({'tool':query['tool'],'evidence':result['id'],'new_paths':added})
                        if result.get('identity_mismatch'): raise Error('Live identity changed.')
                        observations += [campaign.observation(result['id'])] + [campaign.observation(b['id']) for b in result.get('bundle', [])]
                    if notices:
                        stopped='new or unreviewed response structure';details={'notices':notices};break
                    gaps = coverage(campaign, observations, plan)
                    safety = assess(campaign, observations, permit_acknowledged=True)
                    blockers = [r for r in safety['risks'] if r['severity'] != 'info' and (not r['acknowledged'] or r['severity'] in ('critical', 'unknown'))]
                    urgent_issues = [i for i in campaign.issue_reviews() if i.get("critical")]
                    urgent_actions = [a["id"] for a in campaign._actions(open_only=True).values() if
                                      a["status"] in ("unknown", "blocked", "interrupted", "requested") or
                                      a["family"] in ("treatment", "rescue", "combat")]
                    if urgent_issues or urgent_actions:
                        stopped = 'unfinished critical work requires reasoning'
                        details = {'issues': urgent_issues, 'actions': urgent_actions, 'coverage': gaps, 'risks': blockers}; break
                    if gaps or blockers:
                        stopped = 'danger or coverage needs review'; details = {'coverage': gaps, 'risks': blockers}; break
                    if any(checks_match(check, observations) is not True for check in plan.get('continue_checks', [])):
                        stopped = 'continuation condition false or unknown'; break
                    stop_values = [checks_match(check, observations) for check in plan.get('stop_checks', [])]
                    if any(v is not False for v in stop_values):
                        stopped = 'milestone reached or its evidence unknown'; break
                    due = deadlines(campaign)
                    if due['due'] or due['soft_reviews'] or campaign.checkpoints()['due']:
                        stopped = 'deadline, review or history checkpoint due'; details = due; break
                    tick = campaign.state()['latest_tick']
                    if tick is None or start_tick is None: raise Error('Unknown game clock; cannot bound progress.')
                    remaining = plan['max_game_hours'] - (tick-start_tick)/(campaign.meta['ticks_per_day']/24)
                    if remaining <= 0: break
                    wall_left = record['monotonic_deadline'] - time.monotonic()
                    if wall_left < 7: break
                    hours = min(plan.get('wait_hours', 1), remaining)
                    if due['earliest'] is not None:
                        hours = min(hours, (due['earliest']-tick)/(campaign.meta['ticks_per_day']/24))
                    heartbeat('monitored_wait')
                    wait = c.call(token, 'wait_for_event', {'maxSeconds': min(plan.get('wait_seconds', 20), int(wall_left)-2),
                                  'maxGameHours': hours, 'pause': 'always'}, intent=plan['purpose'])
                    record['cycles'] += 1
                    obs = campaign.observation(wait['id'])
                    last_pause = {'confirmed': obs['data'].get('pausedAfter') is True, 'evidence': obs['id']}
                    safety = assess(campaign, [obs])  # New wait events are never inherited acknowledgements.
                    unexpected = unexpected_progress(obs, plan)
                    campaign.event({'kind': 'monitor_cycle', 'summary': 'Bounded routine wait returned', 'plan': plan_id,
                                    'cycle': record['cycles'], 'wait': obs['id'], 'ticks': obs['data'].get('ticksWaited'),
                                    'stop': safety['stop'] or bool(unexpected), 'unexpected_progress': unexpected})
                    if safety['stop'] or unexpected or obs['data'].get('ticksWaited', 0) <= 0:
                        stopped = 'event, unexpected progress or stalled time'; details = {'safety': safety, 'changes': unexpected}; break
            except Exception as exc:
                stopped = 'controller uncertainty'; details = {'error': str(exc)}
            finally:
                # Independent of agent/model response latency. No unmonitored handback is called safe.
                try: last_pause = c.ensure_paused(token, emergency=True)
                except Exception as exc: last_pause = {'confirmed': False, 'urgent': str(exc)}
                record.update(status='stopped', stopped_at=now(), reason=stopped, details=details, pause=last_pause)
                atomic_json(lease_path, record)
                atomic_json(execution_path, record)
                guardian.finish()
            campaign.event({'kind': 'monitor_stop', 'summary': stopped, 'plan': plan_id,
                            'cycles': record['cycles'], 'pause': last_pause, 'details': details})
            from .continuity import packet
            campaign.meta['presentation_reset_at'] = now()
            atomic_json(campaign.path / 'campaign.json', campaign.meta)
            packet_path = campaign.path / 'plans' / (plan_id + '.packet.json')
            atomic_json(packet_path, packet(campaign))
            return {'stopped': True, 'reason': stopped, 'cycles': record['cycles'], 'pause': last_pause,
                    'details': details, 'packet_path': str(packet_path),
                    'limitation': 'Client-side guards cannot guarantee a pause when the server/OS is unreachable. Pending requests remain unresolved and are never replayed.'}


def watchdog(root, name, plan_id):
    from .memory import Campaign
    campaign = Campaign(root, name); c = Control(campaign)
    lease_path = c.path / 'monitor.json'
    record = read_json(lease_path)
    if record['id'] != plan_id or record['campaign_id'] != campaign.meta['id']: raise Error('Guardian lease mismatch.')
    token = read_json(c.path / 'owner.json')['token']
    atomic_json(c.path / ('guardian-' + plan_id + '.json'), {'pid': os.getpid(), 'at': now(), 'plan': plan_id})
    while True:
        record = read_json(lease_path)
        if record.get('id') != plan_id or record.get('status') != 'running': return
        failed = ((c.path / (plan_id + '.stop.json')).exists() or alive(record['pid']) is not True or time.time() >= record['expires_at'] or
                  time.monotonic() >= record['monotonic_deadline'] or time.time()-record['heartbeat'] > 65)
        if failed:
            # A live in-flight RPC still holds the operation lock. Do not interleave another request.
            try:
                pause = c.ensure_paused(token, emergency=True)
                current = read_json(lease_path)
                if current.get('id') == plan_id and current.get('status') == 'running':
                    atomic_json(lease_path, dict(current, status='stopped', reason='guardian expiry or worker loss', pause=pause, stopped_at=now()))
                return
            except Error:
                atomic_json(c.path / ('guardian-' + plan_id + '.json'), {'pid': os.getpid(), 'at': now(),
                    'urgent': 'Pause guardian is waiting for the serialized RPC lock; server operation may still be running.'})
        time.sleep(0.25)


if __name__ == '__main__':
    p = argparse.ArgumentParser(); p.add_argument('--watchdog', action='store_true', required=True)
    p.add_argument('--root', type=Path, required=True); p.add_argument('--run', required=True); p.add_argument('--id', required=True)
    a = p.parse_args(); watchdog(a.root, a.run, a.id)
