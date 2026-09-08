"""Supervised wait budgets and transport allowance; no live game calls."""
import json
import unittest
from test_system import ControlFixture, Response
from tools.rimworld.core import Error
from tools.rimworld.mcp import Client, Uncertain




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
