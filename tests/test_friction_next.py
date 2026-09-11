"""Live-friction follow-up: wait-loop salience, caller-limit coverage, shaping parity."""
import json
from pathlib import Path

from test_system import ControlFixture, fixture
from tools.rimworld.composition import delivered
from tools.rimworld.core import Error, atomic_json, read_json
from tools.rimworld.observations import normalize
from tools.rimworld.safety import assess, signals
from tools.rimworld.session import Session

ROOT = Path(__file__).resolve().parents[1]

CRISIS = {'_paused': True, 'ok': True, 'event': False, 'cause': 'timeout',
          'ticksWaited': 2505, 'pausedAfter': True,
          'crisisCap': {'cappedAtTicks': 2500, 'reasons': ['hostiles'],
                        'note': 'Wait was capped at 1 in-game hour because of an active crisis. '
                                'Address it, or pass force:true to wait longer.'}}

THREAT = {'count': 1, 'nearestDist': 55,
          'hostilesSample': [{'id': 'Mech1', 'kind': 'Mech_Pikeman', 'label': 'pikeman', 'dist': 55}],
          'note': 'Hostiles within 50 cells of a colonist.'}

HEALING = {'pawnDamage': [{'name': 'Tatyana', 'hpBefore': 80, 'hpAfter': 90}]}

PAUSING = {'_paused': True, '_dialogOpen': True, 'ok': True, 'windows': [
    {'index': 0, 'type': 'Dialog_NodeTree', 'forcePause': True, 'kind': 'choice',
     'text': 'Research finished: Deep drilling',
     'options': [{'index': 0, 'label': 'OK'}]},
    {'index': 1, 'type': 'SayWindow', 'forcePause': False, 'kind': 'other'}]}


class FrictionNext(ControlFixture):
    def setUp(self):
        super().setUp()
        self.session = Session(self.control, self.token)

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

    def wait_obs(self, payload, args=None):
        return normalize('wait_for_event', args or {}, payload, 'c', 's', 'fixture')

    # --- 1a: crisisCap is info and does not drive event context -----------------------

    def test_crisis_cap_is_info_not_a_blocker(self):
        obs = self.wait_obs(CRISIS)
        card = next(r for r in signals(obs) if r['kind'] == 'crisis_cap')
        self.assertEqual(card['severity'], 'info')
        self.assertEqual(card['value']['cappedAtTicks'], 2500)
        self.assertFalse(assess(self.camp, [obs])['stop'])

    def test_a_quiet_capped_timeout_does_not_set_review_or_read_status(self):
        self.responses.extend([dict(CRISIS)])
        before = len(self.calls)
        value = self.body('rw_wait', {'maxGameTicks': 20000})
        self.assertEqual(len(self.calls) - before, 1)
        self.assertNotIn('event_context', value)
        self.assertNotIn('requires_review', value)
        self.assertEqual(value['data']['crisisCap']['reasons'], ['hostiles'])
        self.assertIn('force:true', value['data']['crisisCap']['note'])

    def test_cap_plus_threat_plus_healing_still_skips_event_context(self):
        payload = dict(CRISIS, _threatWarning=THREAT, _delta=HEALING)
        self.responses.extend([payload])
        before = len(self.calls)
        value = self.body('rw_wait', {'maxGameTicks': 20000})
        self.assertEqual(len(self.calls) - before, 1)
        self.assertNotIn('event_context', value)
        self.assertEqual(value['data']['crisisCap']['cappedAtTicks'], 2500)
        self.assertEqual(value['data']['_threatWarning']['nearestDist'], 55)

    def test_a_real_threat_event_still_builds_its_packet(self):
        self.responses.extend([
            {'_paused': True, 'ok': True, 'event': True, 'cause': 'threatAppeared',
             'ticksWaited': 400, 'pausedAfter': True},
            fixture('status')])
        value = self.body('rw_wait', {'maxSeconds': 30, 'context': 'brief'})
        self.assertIn('event_context', value)
        self.assertIn('core', value['event_context'])

    def test_wait_contract_names_crisis_cap_versus_wait_budget(self):
        text = self.body('rw_capabilities', {'tool': 'rw_wait'})['tool']['description']
        self.assertIn('crisisCap', text)
        self.assertIn('force', text)
        self.assertIn('wait_budget', text)

    def test_facade_guide_names_crisis_cap_and_force(self):
        text = (ROOT / 'docs/facade.md').read_text()
        self.assertIn('crisisCap', text)
        self.assertRegex(text, r'force')
        self.assertIn('wait_budget', text)

    # --- 1c: zero-tick forcePaused names the window ----------------------------------

    def test_zero_tick_force_paused_names_the_window_and_dismissal(self):
        self.add_tools('list_windows')
        self.responses.extend([
            {'_paused': True, 'ok': True, 'event': True, 'cause': 'forcePaused',
             'ticksWaited': 0, 'pausedAfter': True},
            PAUSING,
            fixture('status')])
        before = len(self.calls)
        value = self.body('rw_wait', {'maxSeconds': 30})
        blocker = value['pausing_window']
        self.assertEqual(blocker['type'], 'Dialog_NodeTree')
        self.assertTrue(blocker['forcePause'])
        self.assertIn('Deep drilling', blocker['text'])
        self.assertEqual(blocker['dismiss']['tool'], 'window_action')
        self.assertEqual(blocker['dismiss']['args']['option'], 'OK')
        self.assertEqual(blocker['dismiss']['args']['index'], 0)
        names = [c['name'] for c in self.calls[before:] if c['name'] in ('wait_for_event', 'list_windows', 'get_status')]
        self.assertEqual(names[:2], ['wait_for_event', 'list_windows'])

    def test_a_progressing_wait_does_not_read_windows(self):
        self.add_tools('list_windows')
        self.responses.extend([dict(CRISIS)])
        before = len(self.calls)
        self.body('rw_wait', {'maxGameTicks': 20000, 'context': 'none'})
        self.assertEqual(len(self.calls) - before, 1)

    def test_a_progressing_force_paused_wait_does_not_read_windows(self):
        self.add_tools('list_windows')
        self.responses.extend([
            {'_paused': True, 'ok': True, 'event': True, 'cause': 'forcePaused',
             'ticksWaited': 12, 'pausedAfter': True},
            fixture('status')])
        before = len(self.calls)
        value = self.body('rw_wait', {'maxSeconds': 30, 'context': 'none'})
        self.assertNotIn('list_windows', [c['name'] for c in self.calls[before:]])
        self.assertNotIn('pausing_window', value)

    def test_wait_does_not_inject_force(self):
        self.responses.extend([dict(CRISIS)])
        self.body('rw_wait', {'maxGameTicks': 20000, 'context': 'none'})
        args = [c['arguments'] for c in self.calls if c['name'] == 'wait_for_event'][-1]
        self.assertNotIn('force', args)
        self.assertEqual(args.get('pause'), 'always')

    # --- 2a: caller-honored truncated is known, not degraded --------------------------

    def test_honored_caller_limit_is_known_not_degraded(self):
        self.add_tools('list_things', 'get_conditions')
        rows = [{'id': 'p'+str(i), 'label': 'pawn '+str(i)} for i in range(20)]
        self.responses.extend([
            {'_paused': True, 'matched': 33, 'returned': 20, 'truncated': True, 'things': rows},
            {'_paused': True, 'outdoorTemp': -12}])
        value = self.body('rw_observe', {'queries': [
            {'key': 'threat', 'tool': 'list_things', 'args': {'category': 'pawn', 'limit': 20}},
            {'key': 'weather', 'tool': 'get_conditions', 'args': {}}]})
        self.assertNotIn('stopped', value)
        self.assertNotIn('degraded', value)
        self.assertTrue(value['queried_complete'])
        self.assertTrue(value['sections']['threat']['data']['truncated'])
        self.assertEqual(value['sections']['threat']['data']['returned'], 20)
        self.assertEqual(value['sections']['weather']['data']['outdoorTemp'], -12)

    def test_truncated_below_the_caller_limit_still_degrades(self):
        self.add_tools('list_things', 'get_conditions')
        rows = [{'id': 'p'+str(i)} for i in range(10)]
        self.responses.extend([
            {'_paused': True, 'matched': 40, 'returned': 10, 'truncated': True, 'things': rows},
            {'_paused': True, 'outdoorTemp': -12}])
        value = self.body('rw_observe', {'queries': [
            {'key': 'threat', 'tool': 'list_things', 'args': {'category': 'pawn', 'limit': 20}},
            {'key': 'weather', 'tool': 'get_conditions', 'args': {}}]})
        self.assertEqual(value['degraded'], ['threat'])
        self.assertEqual(value['sections']['weather']['data']['outdoorTemp'], -12)

    def test_normalize_treats_honored_limit_as_known(self):
        rows = [{'id': 'p'+str(i)} for i in range(20)]
        known = normalize('list_things', {'limit': 20},
                          {'matched': 33, 'returned': 20, 'truncated': True, 'things': rows},
                          'c', 's', 'fixture')
        self.assertEqual(known['completeness'], 'known')
        short = normalize('list_things', {'limit': 20},
                          {'matched': 40, 'returned': 10, 'truncated': True, 'things': rows[:10]},
                          'c', 's', 'fixture')
        self.assertEqual(short['completeness'], 'partial')

    def test_large_output_still_degrades(self):
        self.add_tools('list_world_objects', 'get_conditions')
        self.responses.extend([
            {'_paused': True, 'chars': 58785, 'items': 263, 'largeOutput': True,
             'message': 'Output is large'},
            {'_paused': True, 'outdoorTemp': -12}])
        value = self.body('rw_observe', {'queries': [
            {'key': 'world', 'tool': 'list_world_objects', 'args': {}},
            {'key': 'weather', 'tool': 'get_conditions', 'args': {}}]})
        self.assertEqual(value['degraded'], ['world'])
        self.assertEqual(value['sections']['weather']['data']['outdoorTemp'], -12)

    # --- 3a: annotate inside compositions --------------------------------------------

    def test_observe_names_withheld_trade_rows(self):
        self.add_tools('list_trade')
        self.responses.extend([{'_paused': True, '_dialogOpen': True, 'ok': True, 'active': True,
                                'silver': 144, 'returned': 2, 'tradeableCount': 3,
                                'tradeables': [{'index': 0, 'label': 'Alpaca meat'},
                                               {'index': 1, 'label': 'Egg'}]}])
        value = self.body('rw_observe', {'queries': [
            {'key': 'deal', 'tool': 'list_trade', 'args': {}}]})
        self.assertEqual(value['sections']['deal']['rows_withheld']['counted'], 3)

    # --- 3b: decision presets materialize in wait verify -----------------------------

    def test_wait_verify_materializes_a_decision_preset(self):
        self.responses.extend([
            {'_paused': True, 'ok': True, 'event': True, 'cause': 'letter',
             'ticksWaited': 200, 'pausedAfter': True,
             '_notifications': [{'kind': 'letter', 'text': 'A trader arrived'}]},
            fixture('status')])
        value = self.body('rw_wait', {'maxSeconds': 30, 'context': 'none', 'verify': [
            {'key': 'now', 'preset': 'decision', 'include': ['core']}]})
        self.assertIn('ticksGame', value['decisions']['now']['core'])
        self.assertNotIn('now.status', value['verification'])
        bundled = (value.get('verification') or {}).get('now.status', {}).get('data', {}).get('bundled')
        self.assertFalse(bundled)

    # --- 3c: mutation receipts drop the standing threat block ------------------------

    def test_mutation_receipts_shed_the_threat_payload_but_keep_its_signal(self):
        # The block is trimmed for bytes, but its presence is also the fail-stop that
        # interruptions() and the action batch rely on, so the field and its risk card stay.
        threat = dict(THREAT)
        self.responses.extend([
            {'ok': True, 'executed': True, 'pawn': 'Ward', 'label': 'Go here',
             '_paused': True, '_threatWarning': threat}])
        value = self.body('rw_act', {'tool': 'order_pawn',
                                     'args': {'id': 'Human3874', 'x': 1, 'z': 2, 'command': 'Go here'}})
        kept = value['data']['_threatWarning']
        self.assertEqual(kept['nearestDist'], 55)
        self.assertNotIn('hostilesSample', kept)
        self.assertNotIn('note', kept)
        self.assertTrue(any(r.get('kind') == '_threatWarning' for r in value.get('risks') or ()))

    def test_reads_and_waits_keep_the_standing_threat_block(self):
        threat = dict(THREAT)
        self.responses.extend([
            {'id': 'Human3874', 'name': 'Ward', '_paused': True, '_threatWarning': threat}])
        read = self.body('rw_read', {'tool': 'get_pawn', 'args': {'id': 'Human3874'}})
        self.assertEqual(read['data']['_threatWarning']['nearestDist'], 55)
        self.responses.extend([dict(CRISIS, _threatWarning=threat)])
        wait = self.body('rw_wait', {'maxGameTicks': 2500, 'context': 'none'}, 2)
        warning = wait['data']['_threatWarning']
        self.assertTrue('nearestDist' in warning or 'same_as' in warning)

    # --- set_trade same-dialog exception ---------------------------------------------

    def test_set_trade_batch_continues_on_the_open_dialog_flag(self):
        self.add_tools('set_trade')
        self.responses.extend([
            {'_paused': True, '_dialogOpen': True, 'ok': True, 'transfer': -n,
             'silverAfterDeal': 200 + n, 'index': n, 'label': 'item'}
            for n in (1, 2, 3)])
        value = self.body('rw_act', {'independent': True, 'actions': [
            {'tool': 'set_trade', 'args': {'index': n, 'transfer': -n}} for n in (1, 2, 3)]})
        self.assertFalse(value['stopped'])
        self.assertEqual(value['completed'], 3)

    def test_trade_action_still_stops_a_batch(self):
        self.add_tools('set_trade', 'trade_action')
        self.responses.extend([
            {'_paused': True, '_dialogOpen': True, 'ok': True, 'transfer': -1, 'silverAfterDeal': 201},
            {'_paused': True, '_dialogOpen': True, 'ok': True, 'traded': True},
            {'_paused': True, '_dialogOpen': True, 'ok': True, 'transfer': -2, 'silverAfterDeal': 202}])
        value = self.body('rw_act', {'independent': True, 'actions': [
            {'tool': 'set_trade', 'args': {'index': 1, 'transfer': -1}},
            {'tool': 'trade_action', 'args': {'action': 'accept'}},
            {'tool': 'set_trade', 'args': {'index': 2, 'transfer': -2}}]})
        self.assertTrue(value['stopped'])
        self.assertEqual(value['not_run'], [2])

    def test_deal_annotation_confirms_goods_near_the_trader(self):
        self.add_tools('trade_action')
        self.responses.extend([{'_paused': True, '_dialogOpen': True, 'ok': True, 'traded': True}])
        value = self.body('rw_act', {'tool': 'trade_action', 'args': {'action': 'accept'}})
        self.assertIn('list_things', value['deal']['confirm_goods'])
        self.assertIn('near', value['deal']['confirm_goods'].lower())
        self.assertNotIn('list_unmanaged_items', value['deal']['confirm_goods'])

    # --- 4d: empty float menu is named -----------------------------------------------

    def test_empty_order_options_name_a_cause(self):
        self.responses.extend([{'_paused': True, 'options': [], 'pawn': 'Tatyana'}])
        value = self.body('rw_read', {'tool': 'order_pawn', 'args': {'id': 'Human63400'}})
        self.assertIn('mental', value['empty_options'].lower())

    # --- workflow notes --------------------------------------------------------------

    def test_trade_workflow_confirms_goods_near_the_trader(self):
        self.add_tools('get_alerts', 'list_things', 'get_pawn', 'list_trade', 'set_trade',
                       'trade_action', 'window_action', 'list_unmanaged_items', 'list_fires',
                       'get_area', 'draft', 'inspect_thing')
        steps = self.body('rw_capabilities', {'workflow': 'trade'})['steps']
        confirm = steps[-1]
        self.assertEqual(confirm['tool'], 'list_things')
        self.assertIn('nearId', confirm['note'])
        self.assertIn('radius', confirm['note'])
        notes = ' '.join(row.get('note', '') for row in steps).lower()
        self.assertIn('batch', notes)
        combat = ' '.join(row.get('note', '') for row in
                          self.body('rw_capabilities', {'workflow': 'combat_event'}, 2)['steps']).lower()
        self.assertIn('weapon', combat)
        self.assertIn('threatbig', combat)
        self.assertIn('defname', combat)
        self.assertIn('options:[]', combat)
        food = ' '.join(row.get('note', '') for row in
                        self.body('rw_capabilities', {'workflow': 'food_crisis'}, 3)['steps']).lower()
        self.assertIn('defname', food)
        resume = ' '.join(row.get('note', '') for row in
                          self.body('rw_capabilities', {'workflow': 'resume_crisis'}, 4)['steps']).lower()
        self.assertIn('weapon', resume)


class ThreatInterlock(ControlFixture):
    """The standing-threat block on a mutation receipt is also the batch/guard fail-stop."""

    def setUp(self):
        super().setUp()
        self.session = Session(self.control, self.token)

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

    def moves(self, n):
        return [{'tool': 'order_pawn', 'args': {'id': chr(97 + i), 'command': 'Go here',
                                                'x': i, 'z': i}} for i in range(n)]

    def test_a_batch_stops_when_the_threat_changes_mid_batch(self):
        self.responses.extend([
            {'ok': True, '_paused': True, 'pawn': 'a', '_threatWarning': {'count': 1, 'nearestDist': 55}},
            {'ok': True, '_paused': True, 'pawn': 'b', '_threatWarning': {'count': 6, 'nearestDist': 9}}])
        value = self.body('rw_act', {'independent': True, 'actions': self.moves(3)})
        self.assertTrue(value['stopped'])
        self.assertEqual(value['completed'], 2)
        self.assertEqual(value['not_run'], [2])

    def test_a_batch_continues_through_an_unchanged_standing_threat(self):
        standing = {'count': 1, 'nearestDist': 55}
        self.responses.extend([
            {'ok': True, '_paused': True, 'pawn': 'a', '_threatWarning': dict(standing)},
            {'ok': True, '_paused': True, 'pawn': 'b', '_threatWarning': dict(standing)},
            {'ok': True, '_paused': True, 'pawn': 'c', '_threatWarning': dict(standing)}])
        value = self.body('rw_act', {'independent': True, 'actions': self.moves(3)})
        self.assertFalse(value['stopped'])
        self.assertEqual(value['completed'], 3)

    def test_a_guard_still_stops_after_its_action_when_a_threat_is_present(self):
        from tools.rimworld.composition import Composer
        self.responses.extend([
            {'id': 'p', 'mood': 10, '_paused': True},
            {'ok': True, 'executed': True, '_paused': True,
             '_threatWarning': {'count': 6, 'nearestDist': 9}}])
        spec = {'queries': [{'key': 'pawn', 'tool': 'get_pawn', 'args': {'id': 'p'}}],
                'when': [{'source': 'pawn', 'path': '/mood', 'op': 'lt', 'value': 50}],
                'then': {'tool': 'order_pawn', 'args': {'id': 'p', 'command': 'Go here', 'x': 1, 'z': 2}},
                'verify': [{'key': 'after', 'tool': 'get_pawn', 'args': {'id': 'p'}}]}
        before = len(self.calls)
        result = Composer(self.control, self.token).execute('rw_guard', spec)
        delivered(self.control, self.token, result['composition'])
        self.assertEqual(result['stopped']['reason'], 'Action response requires review')
        self.assertEqual(result['stopped']['not_run'], ['after'])
        self.assertEqual(len(self.calls) - before, 2)

    def test_a_mutation_receipt_sheds_the_bulky_threat_payload(self):
        self.responses.append({'ok': True, '_paused': True, 'pawn': 'a', '_threatWarning': {
            'count': 2, 'nearestDist': 9,
            'colonists': [{'name': 'x%d' % i, 'enemyDist': i} for i in range(9)],
            'hostilesSample': [{'id': 'Mech1', 'kind': 'Mech_Lancer', 'label': 'lancer', 'dist': 9}],
            'note': 'Hostiles within 50 cells of a colonist.'}})
        value = self.body('rw_act', {'tool': 'order_pawn',
                                     'args': {'id': 'a', 'command': 'Go here', 'x': 1, 'z': 2}})
        kept = value['data']['_threatWarning']
        self.assertEqual(kept['count'], 2)
        self.assertEqual(kept['nearestDist'], 9)
        self.assertNotIn('colonists', kept)
        self.assertNotIn('hostilesSample', kept)
        self.assertTrue(value.get('requires_review'))


class WaitAndBatchShapes(ControlFixture):
    def setUp(self):
        super().setUp()
        self.session = Session(self.control, self.token)

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

    def test_no_force_pausing_window_is_not_reported_as_the_blocker(self):
        from tools.rimworld.facade import pausing_dialog
        self.assertIsNone(pausing_dialog({'windows': [
            {'index': 0, 'type': 'MainTabWindow_Inspect', 'kind': 'mainTab', 'forcePause': False}]}))

    def test_a_cleared_block_says_so_instead_of_naming_the_inspect_tab(self):
        self.add_tools('list_windows')
        self.responses.extend([
            {'_paused': True, 'ok': True, 'cause': 'forcePaused', 'ticksWaited': 0, 'pausedAfter': True},
            {'_paused': True, 'ok': True, 'windows': [
                {'index': 0, 'type': 'MainTabWindow_Inspect', 'kind': 'mainTab', 'forcePause': False}]}])
        value = self.body('rw_wait', {'maxSeconds': 30, 'context': 'none'})
        self.assertTrue(value['pausing_window']['none_found'])
        self.assertNotIn('dismiss', value['pausing_window'])

    def test_a_mixed_trade_batch_continues_in_either_order(self):
        self.add_tools('set_trade', 'window_action')
        row = {'ok': True, '_paused': True, '_dialogOpen': True, 'index': 12,
               'label': 'jade', 'transfer': -35}
        box = {'ok': True, '_paused': True, '_dialogOpen': True,
               'window': 'Dialog_Trade', 'did': 'button', 'button': 'OK'}
        self.responses.extend([dict(row), dict(box), dict(row)])
        value = self.body('rw_act', {'independent': True, 'actions': [
            {'tool': 'set_trade', 'args': {'index': 12, 'action': 'sell', 'count': 35}},
            {'tool': 'window_action', 'args': {'button': 'OK'}},
            {'tool': 'set_trade', 'args': {'index': 13, 'action': 'sell', 'count': 1}}]})
        self.assertFalse(value['stopped'])
        self.assertEqual(value['completed'], 3)
        self.responses.extend([dict(box), dict(row)])
        value = self.body('rw_act', {'independent': True, 'actions': [
            {'tool': 'window_action', 'args': {'button': 'OK'}},
            {'tool': 'set_trade', 'args': {'index': 12, 'action': 'sell', 'count': 35}}]}, 2)
        self.assertFalse(value['stopped'])
        self.assertEqual(value['completed'], 2)

    def test_a_set_trade_receipt_that_applied_no_row_stops_the_batch(self):
        self.add_tools('set_trade')
        self.responses.append({'ok': True, '_paused': True, '_dialogOpen': True})
        value = self.body('rw_act', {'independent': True, 'actions': [
            {'tool': 'set_trade', 'args': {'index': 12, 'action': 'sell', 'count': 35}},
            {'tool': 'set_trade', 'args': {'index': 13, 'action': 'sell', 'count': 1}}]})
        self.assertTrue(value['stopped'])
        self.assertEqual(value['not_run'], [1])
