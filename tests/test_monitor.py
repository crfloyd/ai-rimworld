"""Finite progression/danger scenarios with injected server and guardian, never a live endpoint."""
import copy
import json
import unittest
from unittest.mock import patch
from test_system import ControlFixture, schema
from tools.rimworld.core import Error, atomic_json, read_json
from tools.rimworld.monitor import Monitor, create_plan, qualify, coverage, watchdog
from tools.rimworld.outcomes import contract
from tools.rimworld.observations import matches, normalize


class FakeGuardian:
    def __init__(self, control, plan): self.control = control; self.live = True
    def start(self): pass
    def healthy(self): return self.live
    def finish(self): pass


class ScenarioSetup(ControlFixture):
    def setUp(self):
        super().setUp()
        path = self.camp.path / 'raw/catalog.json'; catalog = read_json(path)
        for tool, props in {
            'set_speed': {'action': {'type': 'string', 'enum': ['pause', 'unpause']}},
            'get_alerts': {}, 'list_colonists': {}, 'list_fires': {'mapIndex': {'type': 'integer'}},
            'list_things': {'mapIndex': {'type': 'integer'}, 'category': {'type': 'string', 'enum': ['pawn']}, 'verbose': {'type': 'boolean'}},
        }.items(): catalog['tools'][tool] = {'name': tool, 'inputSchema': schema(props)}
        atomic_json(path, catalog)
        wait = self.camp.ingest('wait_for_event', {'maxSeconds': 5, 'maxGameHours': 0.1, 'pause': 'always'},
                               {'ok': True, 'ticksWaited': 0, 'cause': 'timeout', 'pausedAfter': True}, origin='live')
        pause = self.camp.ingest('set_speed', {'action': 'pause'}, {'ok': True, 'paused': True}, origin='live')
        qualify(self.control, self.token, wait['id'], pause['id'], 'Injected server only; finite/pause behavior reviewed')
        self.spec = {'purpose': 'Finish ordinary work', 'rationale': 'Stable supplies and safe pawns',
                     'expected_progress': 'Work continues', 'reconsider_when': 'Any new hazard or shortage',
                     'watch_pawns': ['p'], 'watch_maps': [0], 'max_cycles': 2, 'max_wall_seconds': 60, 'max_game_hours': 2,
                     'queries': [{'tool': 'get_status'}, {'tool': 'get_pawn', 'args': {'id': 'p', 'tab': 'health'}},
                                 {'tool': 'get_pawn', 'args': {'id': 'p', 'tab': 'needs'}},
                                 {'tool': 'list_fires', 'args': {'mapIndex': 0}},
                                 {'tool': 'list_things', 'args': {'mapIndex': 0, 'category': 'pawn', 'verbose': True}}]}
        # Fixture starts at day 5; avoid an intentionally due history stop for these independent scenarios.
        self.camp.event({'kind': 'checkpoint', 'day': 5, 'summary': 'Synthetic checkpoint only'})

    def safe_reads(self, tick=300000):
        return [{'loaded': True, 'colonyName': 'Fixture Colony', 'ticksGame': tick, 'maps': [{'mapIndex': 0}], 'paused': True,
                 'bundled': {'get_alerts': {'activeAlerts': []}, 'list_colonists': {'colonists': [{'id': 'p'}]}}},
                {'id': 'p', 'hediffs': [], 'overallHealthPercent': 100},
                {'id': 'p', 'needs': [{'label': 'Food', 'percent': 80}, {'label': 'Sleep', 'percent': 80}]},
                {'fires': []}, {'things': [{'id': 'p', 'hostile': False}]}]

    def execute(self, responses, guardian=FakeGuardian):
        self.responses.extend(responses)
        plan = create_plan(self.camp, copy.deepcopy(self.spec))
        result = Monitor(self.control, guardian).run(self.token, plan['id'])
        return plan, result


class Scenario(ScenarioSetup):
    def test_expected_progress_continues_without_model_roundtrip_then_pauses(self):
        wait = {'ok': True, 'cause': 'timeout', 'ticksWaited': 100, 'pausedAfter': True}
        plan, result = self.execute(self.safe_reads() + [wait] + self.safe_reads(300100) + [wait, {'paused': True}])
        self.assertEqual(result['cycles'], 2, result)
        self.assertTrue(result['pause']['confirmed'])
        self.assertEqual(sum(c['name'] == 'wait_for_event' for c in self.calls), 2)
        with self.assertRaises(Error): Monitor(self.control, FakeGuardian).run(self.token, plan['id'])

    def test_raid_damage_unknown_delta_and_lost_building_stop_before_second_wait(self):
        for change in ({'_threatWarning': 'Raid'}, {'_delta': {'pawnDamage': [{'id': 'p', 'hpAfter': 60}]}},
                       {'_delta': {'unrecognizedHazard': True}}, {'_delta': {'removedBuildings': [{'def': 'Wall', 'count': 1}]}}):
            wait = dict({'ok': True, 'cause': 'timeout', 'ticksWaited': 10, 'pausedAfter': True}, **change)
            _, result = self.execute(self.safe_reads(self.camp.state()['latest_tick']) + [wait, {'paused': True}])
            self.assertEqual(result['cycles'], 1); self.assertTrue(result['pause']['confirmed'])

    def test_critical_health_and_coverage_loss_prevent_any_wait(self):
        for index, replacement in [(1, {'id': 'p', 'hediffs': [], 'overallHealthPercent': 100, 'downed': True}),
                                   (1, {'id': 'p', 'error': 'Health unavailable'}),
                                   (2, {'id': 'p', 'needs': [{'label': 'Food', 'percent': 2}]}),
                                   (4, {'things': [{'id': 'p'}]})]:
            responses = self.safe_reads(); responses[index] = replacement
            _, result = self.execute(responses + [{'paused': True}])
            self.assertEqual(result['cycles'], 0, result)

    def test_guardian_loss_prevents_time_advance(self):
        class Dead(FakeGuardian):
            def healthy(self): return False
        _, result = self.execute([{'paused': True}], Dead)
        self.assertEqual(result['cycles'], 0); self.assertTrue(result['pause']['confirmed'])
        self.assertIn('guardian exited', str(result['details']))

    def test_risk_mode_and_unbounded_plans_refused(self):
        for field, value in [('risk', 'combat'), ('max_cycles', 999), ('max_wall_seconds', float('inf'))]:
            spec = dict(self.spec, **{field: value})
            with self.assertRaises(Error): create_plan(self.camp, spec)

    def test_stop_milestone_or_unknown_guard_pauses(self):
        self.spec['continue_checks'] = [{'tool': 'get_pawn', 'args': {'id': 'p'},
                                        'all': [{'path': 'missingSafetySignal', 'op': 'eq', 'value': True}]}]
        _, result = self.execute(self.safe_reads() + [{'paused': True}])
        self.assertEqual(result['cycles'], 0)

    def test_watchdog_worker_loss_uses_only_pause_and_preserves_pending(self):
        c = self.control
        atomic_json(c.path / 'monitor.json', {'id': 'plan-fixture', 'campaign_id': self.camp.meta['id'],
                    'status': 'running', 'pid': 99999999, 'expires_at': 1, 'monotonic_deadline': 1, 'heartbeat': 1})
        self.responses.append({'paused': True})
        before = len(self.calls)
        with patch('tools.rimworld.monitor.Control', return_value=c), patch('tools.rimworld.monitor.alive', return_value=False):
            watchdog(self.root, 'example', 'plan-fixture')
        self.assertEqual(len(self.calls), before+1)
        self.assertEqual(self.calls[-1]['name'], 'set_speed')
        self.assertEqual(read_json(c.path / 'monitor.json')['status'], 'stopped')


class OutcomeContracts(unittest.TestCase):
    def test_equipment_requires_worn_or_equipped_not_inventory(self):
        check = contract({'family': 'equipment', 'pawn': 'p', 'slot': 'equipment', 'item_label': 'Rifle'})['checks'][0]
        obs = normalize('get_pawn', {'id': 'p', 'tab': 'gear'}, {'equipment': [], 'apparel': [], 'inventory': [{'label': 'Rifle'}]}, 'c', 's')
        self.assertFalse(matches(obs, check))
        obs['data']['equipment'] = [{'label': 'Rifle'}]
        self.assertTrue(matches(obs, check))

    def test_treatment_requires_new_time_and_missing_time_is_unknown(self):
        check = contract({'family': 'treatment', 'pawn': 'p', 'condition': 'Infection', 'after_tick': 100,
                          'treatment_tick_field': 'tendTick', 'field_review': 'Fixture explicit timestamp'})['checks'][0]
        obs = normalize('get_pawn', {'id': 'p', 'tab': 'health'}, {'overallHealthPercent': 90,
                        'hediffs': [{'label': 'Infection', 'tendTick': 90}]}, 'c', 's')
        self.assertFalse(matches(obs, check)); obs['data']['hediffs'][0]['tendTick'] = 110
        self.assertTrue(matches(obs, check)); del obs['data']['hediffs'][0]['tendTick']
        self.assertIsNone(matches(obs, check))

    def test_rescue_refuses_position_only_contract(self):
        with self.assertRaises(Error): contract({'family': 'rescue', 'pawn': 'p', 'mapIndex': 0, 'x': 1, 'z': 2})

class MonitorRecovery(ScenarioSetup):
    def test_lost_worker_reconciliation_requires_terminal_request_and_current_pause(self):
        c = self.control
        atomic_json(c.path/'monitor.json',{'id':'plan-lost','status':'running','pid':9999999,'campaign_id':self.camp.meta['id']})
        self.assertTrue(c.stop_monitor(self.token,'Operator requested stop')['stop_requested'])
        pause = self.camp.ingest('set_speed',{'action':'pause'},{'paused':True},origin='live')
        atomic_json(c.path/'pending.json',{'request_id':'unresolved'})
        with patch('tools.rimworld.control.alive',return_value=False):
            with self.assertRaises(Error): c.reconcile_monitor(self.token,pause['id'],'Worker lost',True)
        (c.path/'pending.json').unlink()
        with patch('tools.rimworld.control.alive',return_value=True):
            with self.assertRaises(Error): c.reconcile_monitor(self.token,pause['id'],'Not actually lost',True)
        with patch('tools.rimworld.control.alive',return_value=False):
            self.assertTrue(c.reconcile_monitor(self.token,pause['id'],'Terminal fixture worker/server reviewed',True)['reconciled'])

    def test_unfinished_critical_issue_blocks_automatic_continuation(self):
        self.camp.issue({'title':'Critical dependency','rationale':'Safety uncertain','next_action':'Inspect',
                         'revisit':'Now','resolution':'Observed safe','critical':True})
        _, result=self.execute(self.safe_reads()+[{'paused':True}])
        self.assertEqual(result['cycles'],0)
        self.assertIn('critical work',result['reason'])
