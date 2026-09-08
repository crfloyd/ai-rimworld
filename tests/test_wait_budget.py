"""Supervised wait budgets and transport allowance; no live game calls."""
import json
import unittest
from test_system import ControlFixture, Response
from tools.rimworld.core import Error
from tools.rimworld.mcp import Client, Uncertain
from tools.rimworld.cli import parser


class WaitBudget(ControlFixture):
    def test_long_wait_preserves_medical_deadline_and_pause(self):
        self.responses.append({'ok': True, 'ticksWaited': 500, 'cause': 'timeout', 'pausedAfter': True})
        self.control.advance(self.token, 1, 'medical', 'Recover', deadline_tick=300500,
                             review='Patient deadline remains binding', max_seconds=120)
        self.assertEqual(self.calls[-1]['arguments'],
                         {'maxSeconds': 120, 'maxGameHours': 0.2, 'pause': 'always'})

    def test_invalid_budgets_and_combat_horizon_never_dispatch(self):
        before = len(self.calls)
        for seconds in (True, 4, 601, 120.0, float('inf'), None):
            with self.subTest(seconds=seconds), self.assertRaises(Error):
                self.control.advance(self.token, 1, 'routine', 'Work', review='Review', max_seconds=seconds)
        with self.assertRaises(Error):
            self.control.advance(self.token, 1, 'combat', 'Fight', review='Review', max_seconds=600)
        self.assertEqual(len(self.calls), before)

    def test_cli_budget_default_and_explicit(self):
        args = ['--run', 'example', 'advance', '--token', 'fixture', '--hours', '2',
                '--risk', 'routine', '--intent', 'Work', '--review', 'Review']
        self.assertEqual(parser().parse_args(args).max_seconds, 40)
        self.assertEqual(parser().parse_args(args + ['--max-seconds', '120']).max_seconds, 120)


class WaitTransport(unittest.TestCase):
    def test_timeout_is_request_local_and_covers_server_default(self):
        seen = []
        def opener(request, timeout):
            seen.append(timeout)
            return Response(json.dumps({'id': json.loads(request.data)['id'], 'result': {}}).encode())
        client = Client('http://localhost:8787/mcp', opener=opener)
        for args in ({'maxSeconds': 120}, {}, {'maxSeconds': 600}, {'maxSeconds': 5}):
            client.rpc('tools/call', {'name': 'wait_for_event', 'arguments': args})
        client.rpc('tools/list')
        self.assertEqual(seen, [135, 75, 615, 55, 55])
        self.assertEqual(client.timeout, 55)

    def test_long_timeout_never_replays(self):
        seen = []
        def opener(request, timeout):
            seen.append(timeout)
            raise TimeoutError('late')
        with self.assertRaises(Uncertain):
            Client('http://localhost:8787/mcp', opener=opener).rpc(
                'tools/call', {'name': 'wait_for_event', 'arguments': {'maxSeconds': 120}})
        self.assertEqual(seen, [135])
