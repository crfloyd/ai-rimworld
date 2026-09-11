"""The one-shot CLI reaches what the MCP surface reaches, and fails readably."""
import io
import json
import unittest
from contextlib import redirect_stdout

from tools.rimworld.cli import main, pointer_examples


def run_cli(*argv):
    out = io.StringIO()
    try:
        with redirect_stdout(out):
            code = main(list(argv))
    except SystemExit as exc:
        code = exc.code
    return code, json.loads(out.getvalue())


class CommandLine(unittest.TestCase):
    def test_capabilities_overview_is_reachable_offline(self):
        code, value = run_cli('capabilities', '--overview')
        self.assertEqual(code, 0)
        self.assertIn('trade', value['domains'])
        self.assertEqual(set(value['domains']['trade']), {'tools', 'purpose'})

    def test_capabilities_domain_and_workflow_are_reachable_offline(self):
        code, value = run_cli('capabilities', '--domain', 'trade')
        self.assertEqual(code, 0)
        self.assertIn('order_pawn', [r['tool'] for r in value['domains']['trade']])
        code, value = run_cli('capabilities', '--workflow', 'food_crisis')
        self.assertEqual(code, 0)
        self.assertEqual(value['workflow'], 'food_crisis')

    def test_capabilities_overview_full_lists_tools(self):
        code, value = run_cli('capabilities', '--overview', '--full')
        self.assertEqual(code, 0)
        self.assertIn('list_trade', json.dumps(value))

    def test_a_wrong_flag_returns_json_naming_the_right_one(self):
        code, value = run_cli('--run', 'x', 'observe', '--args', '{}', '--token', 't')
        self.assertEqual(code, 2)
        self.assertFalse(value['ok'])
        self.assertIn('--json', value['use'])
        self.assertIn('--args', value['use'])
        self.assertIs(value['game_contact'], False)

    def test_retrieve_says_it_takes_no_token(self):
        code, value = run_cli('--run', 'x', 'retrieve', '--token', 't')
        self.assertEqual(code, 2)
        self.assertIn('no --token', value['use'])

    def test_pointer_examples_come_from_the_actual_response(self):
        body = {'id': 'obs-1', 'data': {'mood': 42, 'needs': [{'label': 'Food', 'level': 0.2}]}}
        found = pointer_examples(body)
        self.assertIn('/data/mood', found)
        self.assertIn('/data/needs', found)
        self.assertNotIn('/needs', found)
