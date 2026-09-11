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
