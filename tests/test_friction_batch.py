"""Live-friction batch two: recoverable coverage, receipt clarity, scoped event context."""
import io
import json
from contextlib import redirect_stdout
from pathlib import Path

from test_system import ControlFixture, fixture
from tools.rimworld.composition import delivered
from tools.rimworld.core import Error, atomic_json, read_json
from tools.rimworld.session import Session

ROOT = Path(__file__).resolve().parents[1]

LARGE_WORLD = {'_paused': True, 'chars': 58785, 'items': 263, 'largeOutput': True,
               'message': 'Output is large (58785 chars). Re-call with confirm=true to get it anyway, '
                          'or narrow it: narrow with kind (settlements/caravans/sites/space) '
                          'and/or a faction name filter.'}

STANDING = {'_paused': True, 'cause': 'timeout', 'ticksWaited': 2500, 'pausedAfter': True,
            '_threatWarning': {'count': 1, 'nearestDist': 0,
                               'hostilesSample': [{'id': 'Human63400', 'kind': 'Colonist',
                                                   'label': 'Tatyana', 'dist': 0}],
                               'note': 'Hostiles within 50 cells of a colonist.'}}


class FrictionBatch(ControlFixture):
    def setUp(self):
        super().setUp()
        self.session = Session(self.control, self.token)
        self.bound_observation = self.camp.meta['binding']['evidence']

    def body(self, name, args=None, rid=1):
        r = self.session.handle({'jsonrpc': '2.0', 'id': rid, 'method': 'tools/call',
                                 'params': {'name': name, 'arguments': args or {}}})
        if 'error' in r:
            raise Error(r['error']['message'])
        value = json.loads(r['result']['content'][0]['text'])
        if isinstance(value, dict) and isinstance(value.get('composition'), str):
            delivered(self.control, self.token, value['composition'])
        return value

    def add_tools(self, *names):
        real = read_json(ROOT / 'api/catalog.json')['tools']
        path = self.camp.path / 'raw/catalog.json'
        catalog = read_json(path)
        for name in names:
            catalog['tools'][name] = real[name]
        atomic_json(path, catalog)

    # --- Task 2: recoverable coverage ------------------------------------------------

    def test_large_output_degrades_one_section_and_siblings_still_run(self):
        self.add_tools('list_world_objects', 'get_conditions')
        self.responses.extend([LARGE_WORLD, {'_paused': True, 'outdoorTemp': -12, 'weather': 'Clear'}])
        value = self.body('rw_observe', {'queries': [
            {'key': 'world', 'tool': 'list_world_objects', 'args': {}},
            {'key': 'weather', 'tool': 'get_conditions', 'args': {}}]})
        self.assertNotIn('stopped', value)
        self.assertTrue(value['queried_complete'])
        self.assertEqual(value['degraded'], ['world'])
        self.assertEqual(value['sections']['weather']['data']['outdoorTemp'], -12)
        retry = value['sections']['world']['degraded']['retry']
        self.assertIn('kind', retry['narrow_with'])
        self.assertIn('confirm:true', retry['wide_read'])

    def test_a_real_error_still_stops_every_later_query(self):
        self.add_tools('list_world_objects', 'get_conditions')
        self.responses.extend([{'ok': False, 'error': 'No world loaded'}])
        value = self.body('rw_observe', {'queries': [
            {'key': 'world', 'tool': 'list_world_objects', 'args': {}},
            {'key': 'weather', 'tool': 'get_conditions', 'args': {}}]})
        self.assertEqual(value['stopped']['after'], 'world')
        self.assertEqual(value['stopped']['not_run'], ['weather'])
        self.assertIn('requires review', value['stopped']['reason'])
        self.assertFalse(value['queried_complete'])

    def test_missing_or_malformed_fields_still_stop(self):
        self.add_tools('list_colonists', 'get_conditions')
        self.responses.extend([{'_paused': True, 'colonists': 'not-a-list'}])
        value = self.body('rw_observe', {'queries': [
            {'key': 'who', 'tool': 'list_colonists', 'args': {}},
            {'key': 'weather', 'tool': 'get_conditions', 'args': {}}]})
        self.assertEqual(value['stopped']['not_run'], ['weather'])

    def test_wait_verification_degrades_without_losing_later_reads(self):
        self.add_tools('list_world_objects', 'get_conditions')
        self.responses.extend([
            {'_paused': True, 'cause': 'timeout', 'ticksWaited': 200, 'pausedAfter': True},
            LARGE_WORLD, {'_paused': True, 'outdoorTemp': -12}])
        value = self.body('rw_wait', {'maxSeconds': 30, 'context': 'none', 'verify': [
            {'key': 'world', 'tool': 'list_world_objects', 'args': {}},
            {'key': 'weather', 'tool': 'get_conditions', 'args': {}}]})
        self.assertTrue(value['verification_complete'])
        self.assertEqual(value['verification_not_run'], [])
        self.assertEqual(value['verification_degraded'], ['world'])
        self.assertEqual(value['verification']['weather']['data']['outdoorTemp'], -12)

    # --- Task 3: decision preset reach ------------------------------------------------

    def test_decision_world_defaults_to_a_narrow_kind(self):
        self.add_tools('list_world_objects')
        self.responses.extend([{'_paused': True, 'objects': [], 'ok': True}])
        value = self.body('rw_observe', {'queries': [
            {'key': 'now', 'preset': 'decision', 'include': ['world']}]})
        self.assertEqual(self.calls[-1]['arguments'], {'kind': 'caravans'})
        self.assertIn('world', value['decisions']['now'])

    def test_decision_world_kind_is_caller_selectable(self):
        self.add_tools('list_world_objects')
        self.responses.extend([{'_paused': True, 'objects': [], 'ok': True}])
        self.body('rw_observe', {'queries': [
            {'key': 'now', 'preset': 'decision', 'include': ['world'], 'world_kind': 'settlements'}]})
        self.assertEqual(self.calls[-1]['arguments'], {'kind': 'settlements'})

    def test_decision_visitors_reads_neutral_map_pawns(self):
        self.add_tools('list_things')
        self.responses.extend([fixture('status'), {'_paused': True, 'things': [
            {'id': 'Human169082', 'label': 'Chaz', 'kind': 'Town_Trader', 'x': 140, 'z': 94}]}])
        value = self.body('rw_observe', {'queries': [
            {'key': 'now', 'preset': 'decision', 'include': ['core', 'visitors']}]})
        self.assertEqual(self.calls[-1]['arguments'],
                         {'category': 'pawn', 'faction': 'neutral', 'limit': 40})
        self.assertEqual(value['decisions']['now']['visitors']['things'][0]['label'], 'Chaz')

    def test_a_large_world_no_longer_cancels_the_rest_of_a_decision_packet(self):
        self.add_tools('list_world_objects')
        self.responses.extend([fixture('status'), LARGE_WORLD,
                               {'_paused': True, 'id': 'Human1', 'name': 'Tatyana', 'mood': 40}])
        value = self.body('rw_observe', {'queries': [
            {'key': 'now', 'preset': 'decision', 'include': ['core', 'world'],
             'world_kind': 'all', 'pawns': [{'id': 'Human1', 'include': ['summary']}]}]})
        self.assertNotIn('stopped', value)
        self.assertEqual(value['decisions']['now']['pawns'][0]['facets']['summary']['name'], 'Tatyana')
        self.assertEqual(value['degraded'], ['now.world'])

    def test_the_food_facet_names_what_it_cannot_see(self):
        self.responses.extend([fixture('status')])
        value = self.body('rw_observe', {'queries': [
            {'key': 'now', 'preset': 'decision', 'include': ['food']}]})
        note = value['decisions']['now']['food']['not_covered']
        self.assertIn('list_bills', note)
        self.assertIn('list_unmanaged_items', note)

    def test_automatic_world_context_is_narrow_and_finds_map_visitors(self):
        self.add_tools('list_world_objects', 'list_things')
        self.responses.extend([
            {'_paused': True, 'cause': 'letter', 'event': 'A trade caravan is arriving',
             'ticksWaited': 900, 'pausedAfter': True},
            fixture('status'),
            {'_paused': True, 'objects': [], 'ok': True},
            {'_paused': True, 'things': [{'id': 'Human169082', 'label': 'Chaz', 'kind': 'Town_Trader'}]}])
        value = self.body('rw_wait', {'maxSeconds': 30})
        context = value['event_context']
        self.assertEqual(context['world']['scope'], 'kind=caravans')
        self.assertEqual(context['visitors']['rows'][0]['label'], 'Chaz')
        self.assertIn('map pawns', context['visitors']['basis'])

    # --- Task 4: receipts say what they mean ------------------------------------------

    def test_an_already_running_job_is_named_not_just_reported_as_an_error(self):
        self.responses.extend([{'ok': False, '_paused': True,
                                'error': "No order matched 'Prioritize working on campfire (blueprint)'.",
                                'available': ['Already working on campfire (blueprint)']}])
        value = self.body('rw_act', {'tool': 'order_pawn', 'args': {
            'id': 'Human738', 'targetId': 'Blueprint_Campfire169343',
            'command': 'Prioritize working on campfire (blueprint)'}})
        self.assertTrue(value['already_satisfied']['intent_already_met'])
        self.assertFalse(value['already_satisfied']['executed'])
        self.assertIs(value['data']['ok'], False)

    def test_an_already_running_job_does_not_abort_an_independent_batch(self):
        self.responses.extend([
            {'ok': False, '_paused': True,
             'error': "No order matched 'Prioritize working on campfire (blueprint)'.",
             'available': ['Already working on campfire (blueprint)']},
            {'ok': True, '_paused': True, 'queued': False}])
        value = self.body('rw_act', {'independent': True, 'actions': [
            {'tool': 'order_pawn', 'args': {'id': 'a', 'command': 'Prioritize working on campfire (blueprint)'}},
            {'tool': 'order_pawn', 'args': {'id': 'b', 'command': 'Go here', 'x': 1, 'z': 2}}]})
        self.assertFalse(value['stopped'])
        self.assertEqual(value['completed'], 2)

    def test_a_genuine_order_failure_still_aborts_the_batch(self):
        self.responses.extend([{'ok': False, '_paused': True, 'error': 'Pawn is downed.', 'available': []}])
        value = self.body('rw_act', {'independent': True, 'actions': [
            {'tool': 'order_pawn', 'args': {'id': 'a', 'command': 'Prioritize working on campfire (blueprint)'}},
            {'tool': 'order_pawn', 'args': {'id': 'b', 'command': 'Go here', 'x': 1, 'z': 2}}]})
        self.assertTrue(value['stopped'])
        self.assertEqual(value['not_run'], [1])

    def test_a_single_oversized_read_returns_its_retry_advice(self):
        self.add_tools('list_world_objects')
        self.responses.extend([LARGE_WORLD])
        value = self.body('rw_read', {'tool': 'list_world_objects', 'args': {}})
        self.assertIn('kind', value['retry']['narrow_with'])
        self.assertIn('confirm:true', value['retry']['wide_read'])

    def test_a_trade_list_names_the_rows_upstream_withheld(self):
        self.add_tools('list_trade')
        self.responses.extend([{'_paused': True, '_dialogOpen': True, 'ok': True, 'active': True,
                                'silver': 144, 'returned': 2, 'tradeableCount': 3,
                                'tradeables': [{'index': 0, 'label': 'Alpaca meat'},
                                               {'index': 1, 'label': 'Egg'}]}])
        value = self.body('rw_read', {'tool': 'list_trade', 'args': {}})
        self.assertEqual(value['rows_withheld']['returned'], 2)
        self.assertEqual(value['rows_withheld']['counted'], 3)

    def test_an_accepted_deal_states_what_the_receipt_proves(self):
        self.add_tools('trade_action')
        self.responses.extend([{'_paused': True, '_dialogOpen': True, 'ok': True, 'traded': True}])
        value = self.body('rw_act', {'tool': 'trade_action', 'args': {'action': 'accept'}})
        self.assertTrue(value['deal']['committed'])
        self.assertTrue(value['deal']['dialog_open'])
        self.assertIn('list_unmanaged_items', value['deal']['confirm_goods'])
        self.assertNotIn('reverse', value['deal']['next'].lower())

    # --- Task 5: event context matches the event --------------------------------------

    def test_a_standing_colonist_warning_does_not_retrigger_a_threat_sweep(self):
        from tools.rimworld.facade import event_topics
        topics = event_topics({'data': STANDING})
        self.assertNotIn('threat', topics)
        self.assertNotIn('mood', topics)
        self.assertEqual(topics[:2], ['core', 'alerts'])

    def test_a_real_raid_still_pulls_threat_context(self):
        from tools.rimworld.facade import event_topics
        raid = {'cause': 'letter', 'event': 'Raid: tribal warriors are attacking',
                '_threatWarning': {'count': 6, 'hostilesSample': [{'kind': 'Tribal', 'dist': 12}]}}
        self.assertIn('threat', event_topics({'data': raid}))

    def test_a_berserk_colonist_still_reaches_threat_through_the_letter(self):
        from tools.rimworld.facade import event_topics
        berserk = {'cause': 'letter', 'event': 'Tatyana has gone berserk and is attacking',
                   '_threatWarning': {'hostilesSample': [{'kind': 'Colonist', 'dist': 0}]}}
        topics = event_topics({'data': berserk})
        self.assertIn('mood', topics)
        self.assertIn('threat', topics)

    def test_event_topics_ignore_our_own_field_names(self):
        from tools.rimworld.facade import event_topics
        noisy = {'cause': 'timeout', 'colonists': [{'name': 'a', 'mood': 90, 'mentalState': None}]}
        self.assertNotIn('mood', event_topics({'data': noisy}))

    def test_context_brief_skips_the_pawn_and_responder_sweep(self):
        self.responses.extend([
            {'_paused': True, 'cause': 'letter', 'event': 'Tatyana has gone berserk',
             'ticksWaited': 400, 'pausedAfter': True},
            fixture('status')])
        before = len(self.calls)
        value = self.body('rw_wait', {'maxSeconds': 30, 'context': 'brief'})
        self.assertEqual(len(self.calls) - before, 2)
        self.assertIn('core', value['event_context'])
        self.assertNotIn('affected_pawns', value['event_context'])
        self.assertIn('rw_observe', value['event_context']['detail'])

    def test_context_none_reads_nothing_extra(self):
        self.responses.extend([{'_paused': True, 'cause': 'letter', 'event': 'Tatyana has gone berserk',
                                'ticksWaited': 400, 'pausedAfter': True}])
        before = len(self.calls)
        value = self.body('rw_wait', {'maxSeconds': 30, 'context': 'none'})
        self.assertEqual(len(self.calls) - before, 1)
        self.assertNotIn('event_context', value)

    # --- Task 8: local selection failures suggest real pointers -----------------------

    def test_a_failed_selector_suggests_pointers_from_the_response(self):
        from tools.rimworld.cli import main
        out = io.StringIO()
        with redirect_stdout(out):
            code = main(['--root', str(self.root), '--run', 'example',
                         'retrieve', '--observation', self.bound_observation, '--select', '/needs'])
        value = json.loads(out.getvalue())
        self.assertEqual(code, 2)
        self.assertTrue(value['operation_completed'])
        self.assertIn('/data', value['available_pointers'])
        self.assertIn('Do not replay', value['replay'])
