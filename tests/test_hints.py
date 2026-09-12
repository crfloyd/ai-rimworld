import json
import unittest
from pathlib import Path

from tools.rimworld.hints import (NARROW, already_satisfied, job_phrase,
                                  narrowing, oversized, withheld_rows)

LARGE = {'largeOutput': True, 'chars': 58785, 'items': 263,
         'message': 'Output is large (58785 chars). Re-call with confirm=true to get it anyway, '
                    'or narrow it: narrow with kind (settlements/caravans/sites/space) '
                    'and/or a faction name filter.'}


class Hints(unittest.TestCase):
    def test_oversized_only_for_the_upstream_guard(self):
        self.assertTrue(oversized(LARGE))
        self.assertFalse(oversized({'ok': True, 'objects': []}))
        self.assertFalse(oversized({'largeOutput': False}))
        self.assertFalse(oversized('not a dict'))

    def test_narrowing_names_both_exits_and_keeps_upstream_numbers(self):
        hint = narrowing('list_world_objects', LARGE)
        self.assertIn('kind', hint['narrow_with'])
        self.assertIn('confirm:true', hint['wide_read'])
        self.assertIn('rw_retrieve', hint['wide_read'])
        self.assertEqual(hint['items'], 263)
        self.assertEqual(hint['chars'], 58785)
        self.assertIn('never ran', hint['basis'])

    def test_narrowing_omits_confirm_for_tools_without_it(self):
        hint = narrowing('list_trade', {})
        self.assertIn('filter', hint['narrow_with'])
        self.assertNotIn('wide_read', hint)

    def test_narrowing_is_none_for_an_unlisted_tool(self):
        self.assertIsNone(narrowing('get_alerts', {}))

    def test_job_phrase_strips_either_float_menu_prefix(self):
        self.assertEqual(job_phrase('Prioritize working on campfire (blueprint)'), 'campfire (blueprint)')
        self.assertEqual(job_phrase('Already working on campfire (blueprint)'), 'campfire (blueprint)')
        self.assertIsNone(job_phrase('Go here'))
        self.assertIsNone(job_phrase(None))

    def test_already_satisfied_recognizes_the_recorded_receipt(self):
        data = {'ok': False, 'error': "No order matched 'Prioritize working on campfire (blueprint)'.",
                'available': ['Already working on campfire (blueprint)'], '_paused': True}
        args = {'id': 'Human738', 'targetId': 'Blueprint_Campfire169343',
                'command': 'Prioritize working on campfire (blueprint)'}
        found = already_satisfied('order_pawn', args, data)
        self.assertTrue(found['intent_already_met'])
        self.assertFalse(found['executed'])
        self.assertEqual(found['offered'], 'Already working on campfire (blueprint)')

    def test_already_satisfied_refuses_a_different_job_or_a_real_failure(self):
        args = {'command': 'Prioritize working on campfire (blueprint)'}
        self.assertIsNone(already_satisfied('order_pawn', args, {
            'ok': False, 'error': "No order matched 'x'.", 'available': ['Already working on the stove']}))
        self.assertIsNone(already_satisfied('order_pawn', args, {
            'ok': False, 'error': 'Pawn is downed.', 'available': []}))
        self.assertIsNone(already_satisfied('order_pawn', args, {'ok': True}))
        self.assertIsNone(already_satisfied('draft', args, {
            'ok': False, 'error': "No order matched 'x'.",
            'available': ['Already working on campfire (blueprint)']}))

    def test_withheld_rows_reports_the_recorded_trade_gap(self):
        found = withheld_rows('list_trade', {'returned': 64, 'tradeableCount': 65, 'tradeables': []})
        self.assertEqual(found['returned'], 64)
        self.assertEqual(found['counted'], 65)
        self.assertIn('filter', found['note'])
        self.assertIsNone(withheld_rows('list_trade', {'returned': 65, 'tradeableCount': 65}))
        self.assertIsNone(withheld_rows('list_things', {'returned': 1, 'tradeableCount': 9}))

    def test_every_narrow_entry_names_a_real_catalog_tool(self):
        catalog = json.load(open(Path(__file__).resolve().parents[1] / 'api/catalog.json'))['tools']
        for tool in NARROW:
            self.assertIn(tool, catalog)
