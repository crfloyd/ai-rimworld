"""Deidentified reproductions of the 0.2 audit. No network/game access."""
import copy
import json
import unittest
from pathlib import Path
from unittest.mock import patch
from test_system import Workspace, ControlFixture, fixture
from tools.rimworld.core import Error, atomic_json
from tools.rimworld.memory import Campaign, init_campaign
from tools.rimworld.observations import normalize, compact, freshness
from tools.rimworld.knowledge import context, save_lesson, run_knowledge, adopt_shared
from tools.rimworld.cli import parser, run


def lesson(name='local-lesson'):
    return {'id': name, 'title': 'An observed interruption', 'topics': ['medicine'],
            'applicability': {'required_dlc': []}, 'observed': 'Treatment interrupted',
            'explanation': 'Hypothesis: conflicting work', 'recommendation': 'Verify treatment',
            'exceptions': 'Review against current conditions', 'verify': 'Current health detail',
            'evidence': [{'source': 'fixture:an-incident'}], 'status': 'provisional'}


class Isolation(Workspace):
    def test_cli_run_lesson_is_not_shared(self):
        init_campaign(self.root, 'beta', copy.deepcopy(self.meta))
        path = self.root / 'lesson.json'; atomic_json(path, lesson())
        run(parser().parse_args(['--root', str(self.root), '--run', 'example', 'lesson',
                                 '--file', str(path), '--review', 'Review this incident']))
        self.assertEqual(run_knowledge(self.camp, 'medicine')['lessons'][0]['id'], 'local-lesson')
        self.assertFalse(run_knowledge(Campaign(self.root, 'beta'), 'medicine')['lessons'])
        self.assertFalse((self.root / 'knowledge/lessons/local-lesson.json').exists())

    def test_shared_changes_require_adoption(self):
        save_lesson(self.root, lesson('shared'), 'Shared editorial review', shared=True)
        self.assertFalse(run_knowledge(self.camp, 'medicine')['lessons'])
        adopt_shared(self.camp, 'Read and adopt this baseline')
        before = run_knowledge(self.camp, 'medicine')['lessons']
        updated = lesson('shared'); updated['recommendation'] = 'Changed advice'
        save_lesson(self.root, updated, 'Changed reviewed advice', shared=True)
        self.assertEqual(run_knowledge(self.camp, 'medicine')['lessons'], before)
        adopt_shared(self.camp, 'Adopt updated advice')
        self.assertEqual(run_knowledge(self.camp, 'medicine')['lessons'][0]['recommendation'], 'Changed advice')

    def test_direct_shared_write_must_be_explicit(self):
        with self.assertRaises(Error): save_lesson(self.root, lesson(), 'Unscoped')

    def test_campaign_constructor_refuses_symlink_and_identity_mismatch(self):
        (self.root / 'campaigns/alias').symlink_to(self.camp.path, target_is_directory=True)
        with self.assertRaises(Error): Campaign(self.root, 'alias')
        self.camp.meta['name'] = 'wrong'; atomic_json(self.camp.path / 'campaign.json', self.camp.meta)
        with self.assertRaises(Error): Campaign(self.root, 'example')


class ObservationRegression(Workspace):
    def test_full_health_conditions_remain_retrievable_from_bounded_state_index(self):
        result = self.ingest('get_pawn', {'id': 'patient', 'tab': 'health'},
                             {'id': 'patient', 'overallHealthPercent': 100, 'downed': False, 'dead': False,
                              'hediffs': [{'label': 'Heatstroke (initial)', 'severity': 0.05}], 'capacities': {'moving': 95}})
        brief = Campaign(self.root, 'example').refresh()
        self.assertNotIn('Heatstroke', brief)
        full = Campaign(self.root, 'example').observation(result['id'])['data']
        self.assertEqual(full['hediffs'][0]['severity'], 0.05)
        self.assertEqual(full['capacities']['moving'], 95)

    def test_filters_do_not_collide(self):
        keys = set()
        for args in ({'defName': 'WoodLog'}, {'defName': 'MedicineIndustrial'},
                     {'nearX': 2, 'radius': 3}, {'nearX': 3, 'radius': 3}, {'nearX': 2, 'radius': 4}):
            keys.add(normalize('list_things', dict(args, mapIndex=0), {'things': []}, 'c', 's')['key'])
        self.assertEqual(len(keys), 5)

    def test_actual_tool_tab_shapes_are_valid(self):
        for tool, args, data in [('get_map', {}, {'colonists': 3}),
                                 ('get_pawn', {'tab': 'all'}, {'id': 'p', 'needs': {'needs': []}}),
                                 ('get_pawn', {'tab': 'needs'}, {'id': 'animal', 'needs': []})]:
            self.assertEqual(normalize(tool, args, data, 'c', 's')['completeness'], 'known')

    def test_partial_keeps_usable_subset(self):
        result = compact(normalize('get_pawn', {'tab': 'health'}, {'overallHealthPercent': 80}, 'c', 's'))
        self.assertEqual(result['completeness'], 'partial')
        self.assertEqual(result['known_subset']['overallHealthPercent'], 80)
        self.assertIn('hediffs', result['missing'])

    def test_clock_advance_invalidates_health_without_wait_record(self):
        self.camp.meta['session_id'] = 's'
        self.camp.ingest('get_status', {}, {'loaded': False, 'ticksGame': 100}, origin='live')
        self.camp.ingest('get_pawn', {'id': 'p', 'tab': 'health'}, {'hediffs': [], 'overallHealthPercent': 100}, origin='live')
        self.camp.ingest('get_status', {}, {'loaded': False, 'ticksGame': 6100}, origin='live')
        health = next(e['latest'] for e in self.camp.state()['facts'].values() if e['latest']['tool'] == 'get_pawn')
        self.assertTrue(freshness(health, self.camp.state(), self.camp.meta)['revalidate'])
        self.assertTrue(next(f for f in context(self.camp, 'medicine')['facts'] if f['tool'] == 'get_pawn')['revalidate'])

    def test_recorded_data_does_not_overwrite_live_clock_or_fact(self):
        self.camp.meta['session_id'] = 'live'
        self.camp.ingest('get_status', {}, {'loaded': False, 'ticksGame': 100}, origin='live')
        self.camp.ingest('get_status', {}, {'loaded': False, 'ticksGame': 90000}, origin='recorded')
        state = self.camp.state()
        self.assertEqual(state['latest_tick'], 100); self.assertEqual(len(state['facts']), 2)
        recorded = next(e['latest'] for e in state['facts'].values() if e['latest']['origin'] == 'recorded')
        self.assertIsNone(recorded['source_captured_at'])

    def test_session_change_requires_revalidation_in_context(self):
        self.camp.meta['session_id'] = 'before'
        self.camp.ingest('get_pawn', {'id': 'p', 'tab': 'health'}, {'hediffs': [], 'overallHealthPercent': 100}, origin='live')
        self.camp.meta['session_id'] = 'after'
        self.assertTrue(context(self.camp, 'medicine')['facts'][0]['revalidate'])


class EvidenceRegression(ControlFixture):
    def test_import_cannot_complete_or_manually_certify_live_order(self):
        a = self.camp.action('order_pawn', {'id': 'p'}, 'Move', 'movement', {
            'tool': 'get_pawn', 'args': {'id': 'p'}, 'all': [{'path': 'x', 'op': 'eq', 'value': 99}]})
        self.camp.action_update(a['id'], 'accepted', internal=True)
        obs = self.camp.ingest('get_pawn', {'id': 'p'}, {'id': 'p', 'x': 99}, origin='fixture')
        self.assertEqual(self.camp._actions()[a['id']]['status'], 'accepted')
        with self.assertRaises(Error): self.camp.action_update(a['id'], 'completed', obs['id'], 'Imported proof')

    def test_unrelated_observation_does_not_complete_action(self):
        a = self.camp.action('order_pawn', {'id': 'p'}, 'Move', 'movement', {
            'tool': 'get_pawn', 'args': {'id': 'p'}, 'all': [{'path': 'x', 'op': 'eq', 'value': 99}]})
        self.camp.action_update(a['id'], 'accepted', internal=True)
        obs = self.camp.ingest('get_status', {}, fixture('status'), origin='live')
        with self.assertRaises(Error): self.camp.action_update(a['id'], 'completed', obs['id'], 'Unrelated status')

class ContinuityRegression(ControlFixture):
    def test_same_game_reconnect_can_reconcile_without_replay(self):
        a = self.camp.action('order_pawn', {'id': 'p'}, 'Move', 'movement', {
            'tool': 'get_pawn', 'args': {'id': 'p'}, 'all': [{'path': 'x', 'op': 'eq', 'value': 4}]})
        self.camp.action_update(a['id'], 'accepted', internal=True)
        before_session = a['session_id']; calls = len(self.calls)
        self.control.connect(self.token)
        self.responses.append(fixture('status'))
        obs = self.control.call(self.token, 'get_status', {})
        self.control.bind(obs['id'], {'loaded': True, 'colonyName': 'Fixture Colony'}, 'Same authorized fixture world reviewed', self.token)
        self.camp.reconcile_actions([a['id']], obs['id'], 'Same world/save lineage, current tick and roster reviewed')
        self.assertEqual(len(self.calls), calls + 1)
        self.camp.ingest('get_pawn', {'id': 'p'}, {'id': 'p', 'x': 4}, origin='live')
        self.assertEqual(self.camp._actions()[a['id']]['status'], 'completed')
        self.assertEqual(self.camp._actions()[a['id']]['session_id'], before_session)

    def test_old_binding_does_not_reconcile_different_game(self):
        a = self.camp.action('order_pawn', {'id': 'p'}, 'Move', 'movement')
        self.control.connect(self.token)
        changed = fixture('status'); changed['colonyName'] = 'Different world'
        self.responses.append(changed)
        obs = self.control.call(self.token, 'get_status', {})
        self.control.bind(obs['id'], {'loaded': True, 'colonyName': 'Different world'}, 'Fixture identity', self.token)
        with self.assertRaises(Error): self.camp.reconcile_actions([a['id']], obs['id'], 'Wrong world')


class DeltaRegression(Workspace):
    def test_unchanged_status_and_bundle_return_small_deltas(self):
        value = fixture('status')
        value['bundled']['list_colonists']['colonists'] *= 100
        first = self.ingest('get_status', {}, value)
        second = self.ingest('get_status', {}, value)
        self.assertTrue(second['unchanged'])
        self.assertLess(len(json.dumps(second)), len(json.dumps(first)) / 3)
        self.assertEqual(second['delta']['changed_fields'], [])

    def test_filtered_full_details_still_retrievable(self):
        a = self.ingest('list_things', {'defName': 'WoodLog'}, {'things': [{'id': 'wood', 'def': 'WoodLog', 'x': 1}]})
        self.ingest('list_things', {'defName': 'MedicineIndustrial'}, {'things': []})
        self.assertEqual(self.camp.observation(a['id'])['data']['things'][0]['x'], 1)

    def test_projection_size_does_not_grow_with_repeated_observation_ids(self):
        for tick in range(150): self.camp.ingest('get_status', {}, {'loaded': False, 'ticksGame': tick}, origin='fixture')
        self.assertLess((self.camp.path / '.projection.json').stat().st_size, 6000)
        with patch('tools.rimworld.memory.journal', side_effect=AssertionError('Full journal scan')):
            self.assertEqual(self.camp.observation(self.camp.state()['last_observation'])['data']['ticksGame'], 149)

class HandoffLearningRegression(Workspace):
    def test_handoff_is_replaceable_and_resume_surfaces_later_changes(self):
        from tools.rimworld.continuity import handoff
        from tools.rimworld.runs import resume_run
        obs = self.ingest('get_status', {}, fixture('status'))
        (self.camp.path / 'STRATEGY.md').write_text('Protect food production because stores are low.\n')
        self.camp.issue({'title': 'Patient exposed', 'rationale': 'Danger', 'next_action': 'Move after route check',
                         'revisit': 'Now', 'resolution': 'Safe bed observed', 'critical': True})
        shot = handoff(self.camp, 'Context boundary', 'Inspect patient route', 'Orders still need live verification')
        original = Path(shot['path']).read_bytes()
        before = {str(p): p.read_bytes() for p in self.camp.path.rglob('*') if p.is_file()}
        resumed = resume_run(self.root, 'example')
        self.assertNotIn('strategy',resumed['handoff']['snapshot'])
        self.assertNotIn('Protect food',json.dumps(resumed))
        self.assertEqual(Path(resumed['handoff']['snapshot']['current_files']['strategy']).name,'STRATEGY.md')
        self.assertIn('Protect food',resume_run(self.root,'example',full=True)['handoff']['snapshot']['strategy'])
        self.assertEqual(before, {str(p): p.read_bytes() for p in self.camp.path.rglob('*') if p.is_file()})
        (self.camp.path / 'STRATEGY.md').write_text('New strategic decision')
        self.assertTrue(resume_run(self.root, 'example')['handoff']['changed_since_handoff']['strategy'])
        replacement = handoff(self.camp, 'New boundary', 'Follow new decision', 'Live state needs revalidation')
        self.assertEqual(Path(replacement['path']), Path(shot['path']))
        self.assertNotEqual(Path(shot['path']).read_bytes(), original)
        self.assertEqual(resume_run(self.root, 'example')['handoff']['snapshot']['next_action'], 'Follow new decision')

    def test_decision_outcome_candidate_and_distinct_incidents_stay_local(self):
        from tools.rimworld.continuity import decide, outcome, incident, learning_packet
        obs = self.ingest('get_status', {}, fixture('status'))
        decision = decide(self.camp, {'summary': 'Protect supplies', 'rationale': 'Food risk',
                          'expected_result': 'Stores recover', 'risks': 'Labor diverted', 'alternatives': 'Trade',
                          'reconsider_when': 'Harvest fails', 'evidence': [obs['id']], 'topics': ['economy']})
        result = outcome(self.camp, {'decision': decision['id'], 'summary': 'Harvest failed',
                         'result': 'failure', 'observed': 'Plants burned', 'evidence': [obs['id']], 'review': 'Investigate fire exposure'})
        learned = learning_packet(self.camp, 'economy')
        self.assertFalse(learned['decisions_awaiting_outcome'])
        self.assertEqual(learned['lesson_reviews'][0]['outcome'], result['id'])
        first = incident(self.camp, {'key': 'food-loss', 'episode': 'fire-one', 'summary': 'One fire', 'evidence': [obs['id']]})
        duplicate = incident(self.camp, {'key': 'food-loss', 'episode': 'fire-one', 'summary': 'Same fire', 'evidence': [obs['id']]})
        second = incident(self.camp, {'key': 'food-loss', 'episode': 'fire-two', 'summary': 'Separate fire', 'evidence': [obs['id']]})
        self.assertEqual(first['id'], duplicate['id'])
        issue = self.camp.issue({'title': 'Food losses', 'rationale': 'Risk', 'next_action': 'Protect fields',
                               'revisit': 'Now', 'resolution': 'Firebreak inspected',
                               'incident_ids': [first['id'], duplicate['id'], second['id']]})
        self.assertEqual(issue['occurrences'], 2)

class SafetyRegression(ControlFixture):
    def batch(self, steps):
        path = self.root / 'batch.json'; atomic_json(path, steps)
        args = parser().parse_args(['--root', str(self.root), '--run', 'example', 'batch',
                                    '--file', str(path), '--token', self.token])
        with patch('tools.rimworld.cli.Control', return_value=self.control): return run(args)

    def test_critical_alert_and_partial_bundle_stop_following_mutation(self):
        for response in ({'loaded': True, 'ticksGame': 300000, 'maps': [], 'colonyName': 'Fixture Colony',
                          'bundled': {'get_alerts': {'activeAlerts': [{'priority': 'Critical', 'label': 'Extreme break risk'}]}}},
                         {'loaded': True, 'ticksGame': 300000, 'maps': [], 'colonyName': 'Fixture Colony',
                          'bundled': {'get_alerts': {'error': 'Unavailable'}}}):
            self.responses.append(response); before = len(self.calls)
            result = self.batch([{'tool': 'get_status'}, {'tool': 'order_pawn', 'args': {'id': 'p', 'command': 'Move'}, 'intent': 'Move'}])
            self.assertTrue(result['stopped']); self.assertEqual(len(self.calls), before + 1)


    def test_hard_stored_deadline_limits_wait_soft_reminder_does_not(self):
        i = self.camp.issue({'title': 'Review supplies', 'rationale': 'Need food', 'next_action': 'Inspect pantry',
                            'revisit': 'Now', 'revisit_tick': 299999, 'resolution': 'Reviewed'})
        self.responses.append({'ok': True, 'ticksWaited': 10, 'cause': 'timeout', 'pausedAfter': True})
        self.control.call(self.token, 'wait_for_event', {'maxGameHours':1,'pause':'always'})
        self.assertEqual(self.calls[-1]['arguments']['maxGameHours'], 1)
        self.camp.issue({'deadline': {'kind': 'hard', 'tick': 300009, 'reason': 'Patient urgent'}}, i['id'])
        before = len(self.calls)
        with self.assertRaises(Error): self.control.call(self.token, 'wait_for_event', {'maxGameHours':1,'pause':'always'})
        self.assertEqual(len(self.calls), before)

    def test_unpaused_wait_runs_pause_guard_before_handback(self):
        path = self.camp.path / 'raw/catalog.json'; catalog = json.loads(path.read_text())
        catalog['tools']['set_speed'] = {'name': 'set_speed', 'inputSchema': {'type': 'object', 'properties': {
            'action': {'type': 'string', 'enum': ['pause', 'unpause']}}, 'required': ['action']}}
        atomic_json(path, catalog)
        self.responses.extend([{'ok': True, 'cause': 'timeout', 'ticksWaited': 1, 'pausedAfter': False},
                               {'ok': True, 'paused': True}])
        result = self.control.call(self.token, 'wait_for_event', {'maxGameHours':1,'pause':'always'})
        self.assertTrue(result['pause_guard']['confirmed'])
        self.assertTrue(result['safety']['stop'])
        self.assertEqual(self.calls[-1]['name'], 'set_speed')
        self.assertEqual(self.calls[-1]['arguments'], {'action': 'pause'})
        self.assertFalse((self.control.path / 'pause-uncertain.json').exists())

    def test_missing_pause_capability_stays_visible_and_blocks_more_calls(self):
        self.responses.append({'ok': True, 'cause': 'timeout', 'ticksWaited': 1, 'pausedAfter': False})
        result = self.control.call(self.token, 'wait_for_event', {'maxGameHours':1,'pause':'always'})
        self.assertFalse(result['pause_guard']['confirmed'])
        with self.assertRaises(Error): self.control.call(self.token, 'get_status', {})

class IntegrityRegression(ControlFixture):
    def test_clock_reconciliation_preserves_warning_until_reviewed(self):
        earlier = fixture('status'); earlier['ticksGame'] = 100
        self.responses.append(earlier)
        obs = self.control.call(self.token, 'get_status', {})
        self.assertIn('clock_warning', self.camp.state())
        self.control.bind(obs['id'], {'loaded': True, 'colonyName': 'Fixture Colony'}, 'Identity reviewed after legitimate fixture clock discontinuity', self.token)
        self.camp.reconcile_clock(obs['id'], 'Synthetic clock reconciliation; no save was loaded')
        self.assertNotIn('clock_warning', self.camp.state())
        (self.camp.path / '.projection.json').unlink()
        self.assertNotIn('clock_warning', self.camp.state())

    def test_metrics_use_single_current_version_and_capture_observable_phases(self):
        from tools.rimworld import __version__
        from tools.rimworld.metrics import metrics
        self.responses.append(fixture('status'))
        self.control.call(self.token, 'get_status', {})
        result = metrics(self.camp)
        self.assertEqual(result['tooling_version'], __version__)
        self.assertGreater(result['automatic_telemetry']['context_bytes']['samples'], 0)
        self.assertIn('not isolated model', result['loop_timing_limits'])


    def test_stale_status_cannot_bind_current_game(self):
        old = self.camp.meta['binding']['evidence']
        self.responses.append(dict(fixture('status'), ticksGame=300001))
        self.control.call(self.token, 'get_status', {})
        with self.assertRaises(Error): self.control.bind(old, {'loaded': True, 'colonyName': 'Fixture Colony'}, 'Old status', self.token)

class ConservativeCoverage(unittest.TestCase):
    def test_old_live_timestamp_requires_revalidation(self):
        obs = normalize('get_status', {}, {'loaded': False}, 'c', 's', source_captured_at='2000-01-01T00:00:00+00:00')
        obs['epoch'] = 0
        self.assertTrue(freshness(obs, {'epoch': 0}, {'session_id': 's'})['revalidate'])

    def test_nonfinite_or_wrong_type_health_is_partial(self):
        for value in ('100', True, float('nan')):
            self.assertEqual(normalize('get_pawn', {'tab': 'health'}, {'overallHealthPercent': value, 'hediffs': []}, 'c', 's')['completeness'], 'partial')

    def test_global_warning_identity_is_stable_across_actor_commands(self):
        from tools.rimworld.safety import signals
        a = normalize('get_status', {}, {'loaded': False, '_threatWarning': 'One distant threat'}, 'c', 's')
        b = normalize('draft', {'id': 'p'}, {'ok': True, '_threatWarning': 'One distant threat'}, 'c', 's')
        self.assertEqual(signals(a)[0]['id'], signals(b)[0]['id'])

    def test_tutorial_information_is_retained_as_info_not_danger(self):
        from tools.rimworld.safety import signals
        obs = normalize('wait_for_event', {}, {'cause': 'timeout', 'pausedAfter': True, 'ticksWaited': 1,
                        '_notifications': [{'kind': 'learning', 'label': 'Work priorities', 'text': 'A tutorial hint'}]}, 'c', 's')
        self.assertEqual(signals(obs)[0]['severity'], 'info')
        self.assertIn('tutorial hint', str(compact(obs)))

class PublicationIntegrity(Workspace):
    def test_undeclared_external_and_wrong_run_images_are_rejected(self):
        import struct, zlib
        from tools.rimworld.history import add_shot, review_shot, checkpoint
        obs = self.ingest('get_status', {}, fixture('status'))
        def chunk(kind, data): return struct.pack('>I',len(data))+kind+data+struct.pack('>I',zlib.crc32(kind+data)&0xffffffff)
        png = self.root/'image.png'
        png.write_bytes(b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',2,2,8,2,0,0,0))+
                        chunk(b'IDAT',zlib.compress((b'\x00'+b'\xff'*6)*2))+chunk(b'IEND',b''))
        shot = add_shot(self.camp,png,300000,'Fixture','Fixture','Fixture',origin='fixture',evidence=[obs['id']],map_index=0)
        review_shot(self.camp,shot['id'],'Synthetic image visually represented by fixture only')
        chapter = self.root/'chapter.md'
        chapter.write_text('# Synthetic\n\n'+f"![Declared]({shot['path']})\n![Undeclared]({png})\n")
        spec={'day':5,'chapter_file':str(chapter),'shots':[shot['id']],'evidence':[obs['id']],'review':'Fixture',
              'report':{'overview':'Fixture','accomplishments':'Fixture','losses_and_risks':'Fixture','next_five_days':'Fixture','next_year':'Fixture'}}
        with self.assertRaises(Error): checkpoint(self.camp,spec)
        meta_path = self.camp.path/'screenshots'/(shot['id']+'.json')
        meta=json.loads(meta_path.read_text());meta['campaign_id']='different-run';atomic_json(meta_path,meta)
        with self.assertRaises(Error): review_shot(self.camp,shot['id'],'Wrong run')

class DerivedIndexRecovery(Workspace):
    def test_rebuild_restores_missing_index_without_touching_authority(self):
        obs=self.ingest('get_status',{},fixture('status'))
        before=(self.camp.path/'observations.jsonl').read_bytes()
        (self.camp.path/'reference/observation-index'/(obs['id']+'.json')).unlink()
        self.assertTrue(self.camp.rebuild()['rebuilt'])
        self.assertEqual(self.camp.observation(obs['id'])['tool'],'get_status')
        self.assertEqual((self.camp.path/'observations.jsonl').read_bytes(),before)

class DispatchFreshness(ControlFixture):
    def test_lost_wait_invalidates_previous_health_even_without_tick_result(self):
        from tools.rimworld.mcp import Uncertain
        health=self.camp.ingest('get_pawn',{'id':'p','tab':'health'},{'id':'p','hediffs':[],'overallHealthPercent':100},origin='live')
        self.responses.append(Uncertain('Wait response lost'))
        with self.assertRaises(Uncertain): self.control.call(self.token, 'wait_for_event', {'maxGameHours':1,'pause':'always'})
        value=freshness(self.camp.observation(health['id']),self.camp.state(),self.camp.meta)
        self.assertTrue(value['revalidate'])
        self.assertIn('dispatched',str(value['reasons']))
