"""Siege post-mortem follow-up (friction 5a-5g), continuance ticks 4636041-4708677.

The run's own evidence: a wait returned `_delta.newBuildings` naming two `Turret_Mortar`
and raised no risk card, because `signals()` skipped building deltas entirely.
"""
import json
from pathlib import Path

from test_system import ControlFixture, fixture
from tools.rimworld.composition import delivered
from tools.rimworld.core import Error, atomic_json, read_json
from tools.rimworld.observations import normalize
from tools.rimworld.cli import select_output
from tools.rimworld.safety import assess, signals
from tools.rimworld.session import Session

ROOT = Path(__file__).resolve().parents[1]

# Verbatim from obs at 2026-09-12T13:21:15, the wait that reported the siege construction.
SIEGE_BUILD = {'newBuildings': [{'count': 26, 'def': 'Barricade', 'label': 'barricade'},
                                {'count': 2, 'def': 'Turret_Mortar', 'label': 'mortar'}]}

# The 13:20:29 wait, as the facade returned it, before the caller's pointer selection.
SELECTED_AWAY = {
    'data': {'cause': 'letter', 'ticksWaited': 2998, 'time': {'hour': 0},
             '_notifications': [{'id': 234, 'kind': 'letter', 'label': 'Siege: Psyck Crew',
                                 'tick': 4665000, 'type': 'ThreatBig'}]},
    'risks': [{'kind': 'notification', 'severity': 'review',
               'value_ref': '#/data/_notifications'}]}

# The scythers that justified force: dormant in the same cells for four in-game days.
SCYTHERS = {'count': 5, 'nearestDist': 78,
            'hostilesSample': [{'id': 'Mech_Scyther195951', 'kind': 'Mech_Scyther',
                                'label': 'Scyther', 'dist': 78, 'x': 86, 'z': 188}],
            'note': 'Hostiles within 50 cells of a colonist.'}

# The faction that arrived afterwards and inherited that justification.
PSYCK = {'count': 6, 'nearestDist': 6,
         'hostilesSample': [{'id': 'Human224261', 'kind': 'Mercenary_Gunner',
                             'label': 'Tony', 'dist': 6, 'x': 12, 'z': 94},
                            {'id': 'Human224240', 'kind': 'Pirate',
                             'label': 'Meska', 'dist': 8, 'x': 16, 'z': 92}],
         'note': 'Hostiles within 50 cells of a colonist.'}


class SiegePostmortem(ControlFixture):
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

    def siege_wait(self):
        """The 13:21:15 wait: a plain six-hour timeout whose only signal is the delta."""
        self.add_tools('list_things')
        self.responses.extend([
            {'_paused': True, 'ok': True, 'event': False, 'cause': 'timeout',
             'ticksWaited': 15001, 'pausedAfter': True, '_delta': SIEGE_BUILD},
            fixture('status'),
            {'_paused': True, 'loaded': True, 'matched': 0, 'returned': 0, 'things': []},
            {'_paused': True, 'loaded': True, 'matched': 2, 'returned': 2, 'things': [
                {'def': 'Turret_Mortar', 'faction': 'Psyck Crew', 'hostile': True,
                 'id': 'Turret_Mortar224478', 'label': 'Steel mortar', 'x': 15, 'z': 92},
                {'def': 'Turret_Mortar', 'faction': 'Psyck Crew', 'hostile': True,
                 'id': 'Turret_Mortar224480', 'label': 'Steel mortar', 'x': 15, 'z': 96}]}])

    # --- 5a part one: a building delta is no longer discarded -------------------------

    def test_artillery_in_a_building_delta_raises_a_critical_risk(self):
        obs = self.wait_obs({'_paused': True, 'ok': True, 'event': False, 'cause': 'timeout',
                             'ticksWaited': 15001, 'pausedAfter': True, '_delta': SIEGE_BUILD})
        card = next(r for r in signals(obs) if r['kind'] == 'delta:newBuildings')
        self.assertEqual(card['severity'], 'critical')
        self.assertIn('Turret_Mortar', json.dumps(card['value']))

    def test_the_artillery_delta_sets_requires_review(self):
        obs = self.wait_obs({'_paused': True, 'ok': True, 'event': False, 'cause': 'timeout',
                             'ticksWaited': 15001, 'pausedAfter': True, '_delta': SIEGE_BUILD})
        self.assertTrue(assess(self.camp, [obs])['stop'])

    def test_ordinary_construction_in_a_delta_raises_nothing(self):
        """The delta carries no faction, so def class is the only honest discriminator.

        Classifying every finished table would rebuild the alarm fatigue that made
        force feel routine in the first place.
        """
        obs = self.wait_obs({'_paused': True, 'ok': True, 'cause': 'timeout', 'pausedAfter': True,
                             '_delta': {'newBuildings': [{'count': 1, 'def': 'Table1x2c',
                                                          'label': 'table (1x2)'}]}})
        self.assertEqual([r for r in signals(obs) if r['kind'].startswith('delta:new')], [])

    def test_losing_a_hostile_mortar_is_worth_a_card_but_not_a_stop(self):
        obs = self.wait_obs({'_paused': True, 'ok': True, 'cause': 'timeout', 'pausedAfter': True,
                             '_delta': {'removedBuildings': [{'count': 1, 'def': 'Turret_Mortar',
                                                              'label': 'mortar'}]}})
        card = next(r for r in signals(obs) if r['kind'] == 'delta:removedBuildings')
        self.assertEqual(card['severity'], 'review')

    # --- 5a part two: that wait built no packet, because a timeout is not an event ----

    def test_artillery_construction_counts_as_an_event_for_context(self):
        self.siege_wait()
        value = self.body('rw_wait', {'maxGameHours': 6})
        self.assertIn('event_context', value)
        self.assertNotIn('event_context_error', value)

    def test_artillery_construction_puts_threat_in_the_packet_topics(self):
        self.siege_wait()
        value = self.body('rw_wait', {'maxGameHours': 6})
        self.assertIn('threat', value['event_context']['topics'])

    # --- 5a part three: the threat sweep scans pawns, and a mortar is a building -----

    def test_threat_packet_names_hostile_artillery_with_its_positions(self):
        self.siege_wait()
        value = self.body('rw_wait', {'maxGameHours': 6})
        term = value['event_context']['threats']['artillery']
        self.assertEqual(term['count'], 2)
        self.assertEqual([(r['x'], r['z']) for r in term['buildings']], [(15, 92), (15, 96)])
        self.assertEqual(term['factions'], ['Psyck Crew'])

    def test_artillery_term_is_independent_of_distance_to_any_colonist(self):
        """dangerRating stays "None" and no colonist is near: the term must still appear."""
        self.siege_wait()
        value = self.body('rw_wait', {'maxGameHours': 6})
        self.assertEqual(value['event_context']['threats']['hostiles'], [])
        self.assertTrue(value['event_context']['threats']['artillery']['count'])

    # --- 5e: `--select /data/time/hour --select /data/cause` discarded the siege -------

    def test_pointer_selection_retains_a_notice_when_it_drops_a_risk(self):
        out = select_output(SELECTED_AWAY, ['/data/time/hour', '/data/cause'])
        self.assertEqual(out['selected']['/data/cause'], 'letter')
        dropped = out['retained_risks']
        self.assertEqual([r['value_ref'] for r in dropped], ['#/data/_notifications'])
        self.assertEqual(dropped[0]['severity'], 'review')

    def test_selecting_the_risk_itself_adds_no_notice(self):
        out = select_output(SELECTED_AWAY, ['/data/_notifications'])
        self.assertEqual(out[0]['type'], 'ThreatBig')

    def test_selection_with_no_risks_present_is_unchanged(self):
        self.assertEqual(select_output({'data': {'cause': 'timeout'}}, ['/data/cause']), 'timeout')

    # --- 5d: force carried a justification written about dormant scythers -------------

    def quiet(self):
        return {'_paused': True, 'ok': True, 'event': False, 'cause': 'timeout',
                'ticksWaited': 15000, 'pausedAfter': True}

    def test_the_first_force_of_a_session_must_state_a_reason(self):
        self.responses.extend([self.quiet()])
        with self.assertRaises(Error) as caught:
            self.body('rw_wait', {'maxGameHours': 6, 'force': True})
        self.assertIn('force_reason', str(caught.exception))

    def test_the_stated_reason_is_journalled_as_an_advance_review(self):
        self.responses.extend([self.quiet()])
        self.body('rw_wait', {'maxGameHours': 6, 'force': True,
                              'force_reason': 'Five scythers dormant four days at 78 cells.'})
        events = [json.loads(l) for l in
                  (self.camp.path / 'events.jsonl').read_text().splitlines()]
        review = next(e for e in events if e['kind'] == 'advance_review')
        self.assertIn('dormant four days', review['force_reason'])

    def test_a_later_force_in_the_same_session_need_not_restate_it(self):
        self.responses.extend([self.quiet(), self.quiet()])
        self.body('rw_wait', {'maxGameHours': 6, 'force': True, 'force_reason': 'Dormant cluster.'})
        self.assertTrue(self.body('rw_wait', {'maxGameHours': 6, 'force': True})['data']['ok'])

    def test_force_reason_never_reaches_the_game_call(self):
        self.responses.extend([self.quiet()])
        self.body('rw_wait', {'maxGameHours': 6, 'force': True, 'force_reason': 'Dormant cluster.'})
        wait = next(c for c in self.calls if c['name'] == 'wait_for_event')
        self.assertNotIn('force_reason', wait['arguments'])

    def test_force_is_refused_once_when_a_new_hostile_signature_appears(self):
        self.responses.extend([self.quiet(), dict(self.quiet(), _threatWarning=PSYCK)])
        self.body('rw_wait', {'maxGameHours': 6, 'force': True, 'force_reason': 'Five scythers dormant four in-game days at 78 cells.'})
        self.body('rw_wait', {'maxGameHours': 6, 'force': True})
        with self.assertRaises(Error) as caught:
            self.body('rw_wait', {'maxGameHours': 6, 'force': True})
        self.assertIn('Mercenary_Gunner', str(caught.exception))

    def test_re_affirming_force_after_the_refusal_proceeds(self):
        self.responses.extend([self.quiet(), dict(self.quiet(), _threatWarning=PSYCK), self.quiet()])
        self.body('rw_wait', {'maxGameHours': 6, 'force': True, 'force_reason': 'Five scythers dormant four in-game days at 78 cells.'})
        self.body('rw_wait', {'maxGameHours': 6, 'force': True})
        with self.assertRaises(Error):
            self.body('rw_wait', {'maxGameHours': 6, 'force': True})
        self.assertTrue(self.body('rw_wait', {'maxGameHours': 6, 'force': True})['data']['ok'])

    def test_an_unchanged_dormant_cluster_never_refuses_force(self):
        self.responses.extend([dict(self.quiet(), _threatWarning=SCYTHERS)] * 3)
        self.body('rw_wait', {'maxGameHours': 6, 'force': True, 'force_reason': 'Five scythers dormant four in-game days at 78 cells.'})
        for _ in range(2):
            self.body('rw_wait', {'maxGameHours': 6, 'force': True})

    def test_a_wait_without_force_is_never_refused(self):
        self.responses.extend([self.quiet(), dict(self.quiet(), _threatWarning=PSYCK), self.quiet()])
        self.body('rw_wait', {'maxGameHours': 6, 'force': True,
                              'force_reason': 'Five scythers dormant four in-game days at 78 cells.'})
        self.body('rw_wait', {'maxGameHours': 6, 'force': True})
        self.assertTrue(self.body('rw_wait', {'maxGameHours': 6})['data']['ok'])

    # --- 5c: the siege letter and a funeral notice both read cause: "letter" ----------

    def test_a_threat_letter_reports_its_severity_beside_the_cause(self):
        self.responses.extend([{'_paused': True, 'ok': True, 'event': True, 'cause': 'letter',
                                'ticksWaited': 2998, 'pausedAfter': True,
                                '_notifications': [{'id': 234, 'kind': 'letter', 'type': 'ThreatBig',
                                                    'label': 'Siege: Psyck Crew'}]},
                               fixture('status')])
        value = self.body('rw_wait', {'maxGameHours': 6, 'context': 'brief'})
        self.assertEqual(value['data']['cause'], 'letter')
        self.assertEqual(value['letter_severity'], 'ThreatBig')

    def test_a_funeral_letter_is_distinguishable_from_the_siege_letter(self):
        self.responses.extend([{'_paused': True, 'ok': True, 'event': True, 'cause': 'letter',
                                'ticksWaited': 1630, 'pausedAfter': True,
                                '_notifications': [{'id': 240, 'kind': 'letter', 'type': 'NeutralEvent',
                                                    'label': 'Human Funeral opportunity for Stella'}]},
                               fixture('status')])
        value = self.body('rw_wait', {'maxGameHours': 6, 'context': 'brief'})
        self.assertEqual(value['letter_severity'], 'NeutralEvent')

    def test_the_worst_severity_in_a_mixed_batch_wins(self):
        self.responses.extend([{'_paused': True, 'ok': True, 'event': True, 'cause': 'letter',
                                'ticksWaited': 289, 'pausedAfter': True, '_notifications': [
                                    {'type': 'PositiveEvent', 'label': 'Forge can walk again'},
                                    {'type': 'Death', 'label': 'Death: Reed'}]},
                               fixture('status')])
        self.assertEqual(self.body('rw_wait', {'maxGameHours': 6, 'context': 'brief'})['letter_severity'],
                         'Death')

    # --- force left no trace: upstream omits crisisCap entirely when it is bypassed ---

    def test_a_forced_wait_records_the_basis_it_was_justified_against(self):
        self.responses.extend([dict(self.quiet(), _threatWarning=SCYTHERS),
                               dict(self.quiet(), _threatWarning=SCYTHERS)])
        self.body('rw_wait', {'maxGameHours': 6, 'force': True, 'force_reason': 'Five scythers dormant four in-game days at 78 cells.'})
        value = self.body('rw_wait', {'maxGameHours': 6, 'force': True})
        self.assertEqual(value['forced']['basis']['kinds'], ['Mech_Scyther'])
        self.assertEqual(value['forced']['basis']['band'], '40-80')

    def test_an_unforced_wait_carries_no_force_record(self):
        self.responses.extend([self.quiet()])
        self.assertNotIn('forced', self.body('rw_wait', {'maxGameHours': 6}))

    # --- interior heat: get_conditions reports outdoorC only, which stayed benign ----

    def fire_event(self, rooms):
        self.add_tools('list_things', 'list_fires', 'room_graph')
        self.responses.extend([
            {'_paused': True, 'ok': True, 'event': True, 'cause': 'notification',
             'ticksWaited': 1316, 'pausedAfter': True,
             '_notifications': [{'kind': 'message', 'type': 'ThreatBig', 'text': 'Critical alert: Fire!'}]},
            fixture('status'),
            {'_paused': True, 'matched': 0, 'returned': 0, 'things': []},
            {'_paused': True, 'matched': 0, 'returned': 0, 'things': []},
            {'_paused': True, 'ok': True, 'fireCount': 7, 'firesInHomeArea': 7,
             'fires': [{'size': 0.9, 'x': 127, 'z': 124}]},
            {'_paused': True, 'ok': True, 'rooms': rooms}])

    def test_the_hottest_enclosed_room_is_named_with_its_temperature(self):
        self.fire_event([
            {'role': 'outdoors', 'temperature': 24.9, 'cellCount': 0},
            {'role': 'Barracks', 'temperature': 146.9, 'cellCount': 81, 'x': 127, 'z': 124,
             'canReachMapEdge': False},
            {'role': 'Kitchen', 'temperature': 31.0, 'cellCount': 20, 'x': 140, 'z': 130}])
        hottest = self.body('rw_wait', {'maxGameHours': 1})['event_context']['fires']['enclosure']
        self.assertEqual(hottest['temperature'], 146.9)
        self.assertEqual(hottest['role'], 'Barracks')
        self.assertEqual(hottest['cell'], {'x': 127, 'z': 124})
        self.assertTrue(hottest['lethal'])
        self.assertIn('rescue', hottest['detail'])

    def test_the_outdoors_node_never_wins_the_hottest_room(self):
        self.fire_event([{'role': 'outdoors', 'temperature': 900.0, 'cellCount': 0},
                         {'role': 'Kitchen', 'temperature': 22.0, 'cellCount': 20, 'x': 1, 'z': 1}])
        hottest = self.body('rw_wait', {'maxGameHours': 1})['event_context']['fires']['enclosure']
        self.assertEqual(hottest['role'], 'Kitchen')
        self.assertFalse(hottest['lethal'])

    def test_an_unrecognised_room_graph_shape_reports_coverage_loss(self):
        self.fire_event(None)
        self.responses[-1] = {'_paused': True, 'ok': True, 'somethingElse': []}
        hottest = self.body('rw_wait', {'maxGameHours': 1})['event_context']['fires']['enclosure']
        self.assertIsNone(hottest['temperature'])
        self.assertIn('unrecognised', hottest['detail'])

    # --- the generated-file trap: two rewrites recording six deaths were discarded ----

    def test_issues_view_says_it_is_generated_and_names_how_to_change_it(self):
        self.camp.issue({'title': 'Colony food storage is empty', 'rationale': 'No buffer at all',
                         'next_action': 'Harvest ripe rice',
                         'revisit': 'Before any long wait', 'resolution': 'A day of cooked food'})
        self.camp.refresh()
        text = (self.camp.path / 'ISSUES.md').read_text()
        self.assertIn('Generated', text.splitlines()[2])
        self.assertIn('overwritten', text)
        self.assertIn('issue --id', text)

    def test_state_view_carries_the_same_overwrite_warning(self):
        self.camp.refresh()
        self.assertIn('overwritten', (self.camp.path / 'STATE.md').read_text())

    # --- 5g: two telemetry files, different schemas, neither naming what it holds ----

    def test_each_telemetry_stream_names_itself_in_every_row(self):
        self.responses.extend([self.quiet()])
        self.body('rw_wait', {'maxGameHours': 6})
        public = [json.loads(l) for l in
                  (self.camp.path / 'facade-telemetry.jsonl').read_text().splitlines()]
        game = [json.loads(l) for l in
                (self.camp.path / 'telemetry.jsonl').read_text().splitlines()]
        self.assertEqual({r['stream'] for r in public}, {'public_tool_calls'})
        self.assertEqual({r['stream'] for r in game}, {'game_calls'})

    def test_a_quiet_timeout_with_no_construction_still_builds_no_packet(self):
        self.responses.extend([{'_paused': True, 'ok': True, 'event': False, 'cause': 'timeout',
                                'ticksWaited': 15001, 'pausedAfter': True}])
        before = len(self.calls)
        value = self.body('rw_wait', {'maxGameHours': 6})
        self.assertEqual(len(self.calls) - before, 1)
        self.assertNotIn('event_context', value)
