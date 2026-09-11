import copy
import io
import json
import os
from pathlib import Path
import struct
import subprocess
import sys
import tempfile
import unittest
import zlib
from unittest.mock import patch

from tools.rimworld.core import Error, atomic_json, journal, read_json
from tools.rimworld.observations import normalize, compact, matches
from tools.rimworld.memory import Campaign, init_campaign
from tools.rimworld.mcp import Client, Uncertain, endpoint_key, validate
from tools.rimworld.control import Control
from tools.rimworld.knowledge import save_lesson, retrieve
from tools.rimworld.history import add_shot, review_shot, checkpoint
from tools.rimworld.metrics import metrics

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = Path(__file__).parent / "fixtures"
SPEC = {"objective": "Fixture validation only", "mode": "fresh",
        "rules": {"honest_play": True, "reloads": "forbidden"},
        "setup": {"dlc": ["Biotech"], "mods": [], "scenario": "fixture"}}


def fixture(name):
    return read_json(FIXTURES / (name + ".json"))


def schema(properties):
    return {"type": "object", "properties": properties}


CATALOG = {
    "get_status": {"name": "get_status", "inputSchema": schema({})},
    "get_pawn": {"name": "get_pawn", "inputSchema": schema({
        "id": {"type": "string"}, "tab": {"type": "string"}, "detail": {"type": "boolean"}})},
    "order_pawn": {"name": "order_pawn", "inputSchema": schema({
        "id": {"type": "string"}, "targetId": {"type": "string"}, "command": {"type": "string"},
        "x": {"type": "integer"}, "z": {"type": "integer"}})},
    "wait_for_event": {"name": "wait_for_event", "inputSchema": schema({
        "maxGameTicks": {"type": "number"}, "maxGameSeconds": {"type": "number"}, "maxGameDays": {"type": "number"}, "maxSeconds": {"type": "integer"}, "maxGameHours": {"type": "number"},
        "pause": {"type": "string"}, "force": {"type": "boolean"}})},
    "load_game": {"name": "load_game", "inputSchema": schema({})},
}


class Workspace(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.meta = init_campaign(self.root, "example", copy.deepcopy(SPEC))
        self.camp = Campaign(self.root, "example")

    def tearDown(self):
        self.temp.cleanup()

    def fixture_action(self, *args, **kwargs):
        return self.camp.action(*args, **kwargs, origin="fixture")

    def ingest(self, tool, args, payload):
        return self.camp.ingest(tool, args, payload, origin="fixture")


class NormalizationTests(unittest.TestCase):
    def obs(self, tool, args, response):
        return normalize(tool, args, response, "campaign-example", "session-example", "fixture")

    def test_large_output_is_not_empty(self):
        result = self.obs("get_area", {}, fixture("large-area"))
        self.assertEqual(result["completeness"], "partial")
        self.assertIn("things", result["missing"])
        self.assertNotIn("counts", compact(result))
        self.assertIn("largeOutput", compact(result)["warnings"])

    def test_missing_field_distinct_from_known_empty(self):
        missing = self.obs("get_area", {}, {"terrainSummary": {}})
        empty = self.obs("get_area", {}, {"terrainSummary": {}, "things": []})
        self.assertEqual(missing["completeness"], "partial")
        self.assertEqual(empty["completeness"], "known")
        self.assertEqual(compact(empty)["counts"], {})

    def test_partial_application_and_warning_survive(self):
        result = self.obs("designate", {}, {"ok": True, "applied": 1, "rejected": 2,
                                            "failedCells": [{"x": 0, "z": 0, "reason": "blocked"}]})
        self.assertEqual(result["completeness"], "partial")
        self.assertEqual(compact(result)["warnings"]["rejected"], 2)

    def test_mcp_error_and_ambiguous_text(self):
        for payload in (
            {"jsonrpc": "2.0", "id": 1, "error": {"message": "failed"}},
            {"isError": True, "content": [{"type": "text", "text": '{"ok":false}'}]},
            {"content": [{"type": "text", "text": "{}"}, {"type": "text", "text": "{}"}]},
        ):
            self.assertEqual(self.obs("get_pawn", {}, payload)["completeness"], "unavailable")

    def test_medical_exact_value_retained(self):
        result = compact(self.obs("get_pawn", {"id": "PawnA", "tab": "health"}, fixture("health")))
        self.assertEqual(result["health"]["hediffs"][0]["immunity"], 100)
        self.assertIn("99.7%", result["health"]["hediffs"][0]["tooltip"])

    def test_verification_unknown_does_not_pass(self):
        check = {"tool": "get_pawn", "args": {"id": "PawnA"},
                 "all": [{"path": "equipment.0.label", "op": "eq", "value": "rifle"}]}
        self.assertIsNone(matches(self.obs("get_pawn", {"id": "PawnA"}, {"id": "PawnA"}), check))

    def test_unavailable_map_is_not_map_zero(self):
        self.assertIsNone(self.obs("get_area", {}, {"things": [], "terrainSummary": {}})["map_index"])


class MemoryTests(Workspace):
    def test_fresh_campaign_has_no_inherited_ids(self):
        self.assertIn("No observations yet", self.camp.refresh())
        second = init_campaign(self.root, "different", SPEC)
        self.assertNotEqual(second["id"], self.meta["id"])
        self.assertIsNone(second["binding"])
        self.assertFalse((self.camp.path / "raw" / "catalog.json").exists())

    def test_campaign_path_escape_and_overwrite_refused(self):
        with self.assertRaises(Error):
            init_campaign(self.root, "../other", SPEC)
        with self.assertRaises(Error):
            init_campaign(self.root, "example", SPEC)

    def test_failed_observation_retains_prior_threat(self):
        self.ingest("get_alerts", {}, {"activeAlerts": [{"label": "Fire"}]})
        self.ingest("get_alerts", {}, {"ok": False, "error": "Unavailable"})
        entry = next(iter(self.camp.state()["facts"].values()))
        self.assertEqual(entry["last_known"]["data"]["activeAlerts"][0]["label"], "Fire")
        self.assertIn("Last known, requiring revalidation", self.camp.refresh())

    def test_bundle_and_multi_map_freshness(self):
        self.ingest("get_status", {}, fixture("status"))
        self.assertIn("Away fixture", self.camp.refresh())
        self.assertIn("individual timing not supplied", self.camp.refresh())
        self.ingest("wait_for_event", {}, {"ok": True, "ticksWaited": 2500, "cause": "timeout",
                                           "pausedAfter": True})
        self.assertEqual(self.camp.state()["latest_tick"], 302500)
        self.assertIn("REVALIDATE", self.camp.refresh())

    def test_issue_survives_observation_and_fresh_instance(self):
        issue = self.camp.issue({"title": "Repeated mood penalty", "rationale": "Causing breaks",
                                "next_action": "Inspect conversion", "revisit": "Before next work day",
                                "resolution": "Cause addressed", "temporary_override": "Hunting disabled",
                                "restore_when": "Recovered and equipped"})
        self.ingest("get_status", {}, fixture("status"))
        fresh = Campaign(self.root, "example")
        self.assertIn(issue["id"], fresh.refresh())
        self.assertIn("Recovered and equipped", fresh.refresh())
        self.assertEqual(fresh.issue_record(issue["id"])["rationale"], "Causing breaks")
        current_view = (fresh.path / "ISSUES.md").read_text()
        self.assertIn("Inspect conversion", current_view)
        self.assertNotIn('"rationale"', current_view)
        with self.assertRaises(Error):
            fresh.issue({"status": "resolved"}, issue["id"])

    def test_generated_current_views_are_bounded_indexes(self):
        for number in range(30):
            self.ingest("get_pawn", {"id": f"Pawn{number}"},
                        {"id": f"Pawn{number}", "name": "P" + str(number),
                         "job": "working", "hediffs": [{"label": "old detail " + "x" * 500}]})
        state = (self.camp.path / "STATE.md").read_text()
        self.assertIn("additional indexed scopes omitted", state)
        self.assertNotIn("old detail", state)
        self.assertLess(len(state.encode()), 20000)

    def test_action_acceptance_not_completion_and_fresh_check(self):
        action = self.fixture_action("order_pawn", {}, "Reach refuge", "movement",
                                 {"tool": "get_pawn", "args": {"id": "PawnA"},
                                  "all": [{"path": "x", "op": "eq", "value": 4},
                                          {"path": "z", "op": "eq", "value": 8},
                                          {"path": "mapIndex", "op": "eq", "value": 1}]})
        self.camp.action_update(action["id"], "accepted", internal=True)
        self.assertEqual(self.camp._actions()[action["id"]]["status"], "accepted")
        self.ingest("get_pawn", {"id": "PawnA"}, {"id": "PawnA", "x": 4, "z": 8, "mapIndex": 0})
        self.assertEqual(self.camp._actions()[action["id"]]["status"], "accepted")
        self.ingest("get_pawn", {"id": "PawnA"}, {"id": "PawnA", "x": 4, "z": 8, "mapIndex": 1})
        self.assertEqual(self.camp._actions()[action["id"]]["status"], "completed")

    def test_old_evidence_cannot_verify_new_order(self):
        obs = self.ingest("get_pawn", {"id": "PawnA"}, {"id": "PawnA"})
        action = self.fixture_action("order_pawn", {}, "Tend", "treatment")
        with self.assertRaises(Error):
            self.camp.action_update(action["id"], "completed", obs["id"], "Already tended")

    def test_incomplete_evidence_cannot_verify(self):
        action = self.fixture_action("order_pawn", {}, "Extinguish", "extinguishing")
        obs = self.ingest("get_pawn", {"id": "PawnA"}, {"ok": False, "error": "missing"})
        with self.assertRaises(Error):
            self.camp.action_update(action["id"], "completed", obs["id"], "Assumed out")

    def test_interrupted_action_stays_open_and_new_hazard_survives(self):
        action = self.fixture_action("order_pawn", {}, "Rescue safely", "rescue")
        self.camp.action_update(action["id"], "accepted", internal=True)
        obs = self.ingest("get_pawn", {"id": "PawnA"}, {"id": "PawnA", "job": "fleeing", "x": 1, "z": 2})
        self.camp.action_update(action["id"], "interrupted", obs["id"], "Patient dropped outside fire")
        self.ingest("wait_for_event", {}, {"ok": True, "cause": "threatAppeared",
                                           "ticksWaited": 10, "pausedAfter": True,
                                           "_threatWarning": "Previously downed enemy rose"})
        brief = Campaign(self.root, "example").refresh()
        self.assertIn("interrupted", brief)
        self.assertIn("Previously downed enemy rose", brief)

    def test_corrupt_journal_never_disappears(self):
        with (self.camp.path / "observations.jsonl").open("a") as f:
            f.write('{"unfinished":')
        with self.assertRaises(Error):
            self.camp.refresh()

    def test_projection_can_rebuild_from_original_stream(self):
        self.ingest("get_status", {}, fixture("status"))
        (self.camp.path / ".projection.json").unlink()
        self.assertEqual(Campaign(self.root, "example").state()["latest_tick"], 300000)

    def test_session_mismatch_does_not_complete(self):
        action = self.fixture_action("order_pawn", {}, "Move", "movement", {
            "tool": "get_pawn", "all": [{"path": "x", "op": "eq", "value": 4}]})
        self.camp.action_update(action["id"], "accepted", internal=True)
        self.camp.ingest("get_pawn", {}, {"id": "PawnA", "x": 4}, origin="fixture", session_id="other")
        self.assertEqual(self.camp._actions()[action["id"]]["status"], "accepted")

class SchemaTests(unittest.TestCase):
    def test_types_unknown_args_enum_and_constraints(self):
        s = schema({'n': {'type': 'integer', 'minimum': 1}, 'mode': {'enum': ['a', 'b']}})
        validate(s, {'n': 2, 'mode': 'a'})
        for value in ({'n': True}, {'n': 0}, {'mode': 'x'}, {'unknown': 1}):
            with self.assertRaises(Error):
                validate(s, value)

    def test_reference_composition_and_unsupported_constraint(self):
        s = {'$defs': {'id': {'type': 'string'}}, 'type': 'object',
             'properties': {'id': {'$ref': '#/$defs/id'}}, 'required': ['id']}
        validate(s, {'id': 'pawn'})
        with self.assertRaises(Error):
            validate(s, {'id': 3})
        with self.assertRaises(Error):
            validate({'type': 'string', 'format': 'date'}, 'bad')


class Response(io.BytesIO):
    def __init__(self, data, content_type='application/json', status=200, extra=None):
        super().__init__(data)
        self.headers = dict({'Content-Type': content_type}, **(extra or {}))
        self.status = status


class TransportTests(unittest.TestCase):
    def test_json_headers_and_identity(self):
        requests = []
        def opener(request, timeout):
            requests.append(request)
            rid = json.loads(request.data)['id']
            return Response(json.dumps({'jsonrpc': '2.0', 'id': rid, 'result': {'ok': True}}).encode())
        c = Client('http://localhost:8787/mcp', {'session_id': 'test-session', 'protocol': '2025-03-26'}, opener)
        self.assertEqual(c.rpc('tools/list')['result'], {'ok': True})
        headers = {k.lower(): v for k, v in requests[0].header_items()}
        self.assertIn('text/event-stream', headers['accept'])
        self.assertEqual(headers['mcp-session-id'], 'test-session')

    def test_sse_notification_and_matching_response(self):
        def opener(request, timeout):
            rid = json.loads(request.data)['id']
            return Response(('data: {"jsonrpc":"2.0","method":"notifications/message","params":{}}\n\n' +
                             'id: event-1\ndata: ' + json.dumps({'jsonrpc': '2.0', 'id': rid, 'result': {'ok': True}}) +
                             '\n\n').encode(), 'text/event-stream')
        c = Client('http://localhost:8787/mcp', opener=opener)
        self.assertTrue(c.rpc('tools/call')['result']['ok'])
        self.assertEqual(len(c.notifications), 1)
        self.assertEqual(c.session['last_event_id'], 'event-1')

    def test_timeout_never_retries(self):
        calls = []
        def opener(request, timeout):
            calls.append(request)
            raise TimeoutError('late')
        with self.assertRaises(Uncertain):
            Client('http://localhost:8787/mcp', opener=opener).rpc('tools/call')
        self.assertEqual(len(calls), 1)

    def test_mismatched_id_and_ended_stream_are_unknown(self):
        for data, kind in ((b'{"jsonrpc":"2.0","id":"wrong","result":{}}', 'application/json'),
                           (b'data: {"method":"notifications/message"}\n\n', 'text/event-stream')):
            with self.assertRaises(Uncertain):
                Client('http://localhost:8787/mcp', opener=lambda *a, **k: Response(data, kind)).rpc('tools/call')

    def test_initialize_and_paginated_catalog(self):
        seen = []
        def opener(request, timeout):
            body = json.loads(request.data); seen.append(body)
            if body['method'] == 'notifications/initialized':
                return Response(b'', status=202)
            if body['method'] == 'initialize':
                result = {'protocolVersion': '2025-03-26', 'capabilities': {}, 'serverInfo': {'name': 'fixture'}}
            elif body.get('params', {}).get('cursor'):
                result = {'tools': [CATALOG['get_pawn']]}
            else:
                result = {'tools': [CATALOG['get_status']], 'nextCursor': 'page-2'}
            return Response(json.dumps({'jsonrpc': '2.0', 'id': body['id'], 'result': result}).encode())
        c = Client('http://localhost:8787/mcp', opener=opener)
        c.initialize()
        self.assertEqual(set(c.catalog()), {'get_status', 'get_pawn'})
        self.assertEqual(seen[1]['method'], 'notifications/initialized')

    def test_endpoint_aliases_share_ownership(self):
        self.assertEqual(endpoint_key('http://localhost:8787/mcp/'),
                         endpoint_key('http://127.0.0.1:8787/mcp'))


class ControlFixture(Workspace):
    def setUp(self):
        super().setUp()
        self.responses = []
        self.calls = []
        outer = self
        class Fake:
            def __init__(self, endpoint, session=None):
                self.session = session or {}
            def initialize(self):
                self.session = {'protocol': '2025-03-26'}
                return {'protocolVersion': '2025-03-26'}
            def catalog(self):
                return CATALOG
            def rpc(self, method, params, request_id):
                outer.calls.append(params)
                result = outer.responses.pop(0)
                if isinstance(result, Exception):
                    raise result
                return {'jsonrpc': '2.0', 'id': request_id, 'result': {
                    'content': [{'type': 'text', 'text': json.dumps(result)}]}}
        self.control = Control(self.camp, client_factory=Fake)
        self.token = self.control.claim('fixture', True, 'Offline fake server; no real game')['token']
        self.control.connect(self.token)
        self.responses.append(fixture('status'))
        obs = self.control.call(self.token, 'get_status', {})
        self.control.bind(obs['id'], {'loaded': True, 'colonyName': 'Fixture Colony'}, 'Reviewed fixture identity', self.token)

class ControlTests(ControlFixture):
    def test_exclusive_owner_no_timeout_takeover(self):
        with self.assertRaises(Error):
            self.control.claim('other', True, 'Another fixture')

    def test_timeout_leaves_pending_and_no_duplicate(self):
        self.responses.append(Uncertain('Response expired'))
        with self.assertRaises(Uncertain):
            self.control.call(self.token, 'order_pawn', {'id': 'PawnA', 'command': 'Rescue'}, 'Rescue', 'rescue', track=True)
        before = len(self.calls)
        with self.assertRaises(Error):
            self.control.call(self.token, 'order_pawn', {'id': 'PawnA', 'command': 'Rescue'}, 'Rescue', 'rescue', track=True)
        self.assertEqual(len(self.calls), before)
        self.assertEqual(self.control.inspect()['pending']['status'], 'unknown')
        self.assertIn('unknown', [a['status'] for a in self.camp._actions().values()])

    def test_handle_and_reviewed_reconciliation(self):
        self.responses.append(Uncertain('late'))
        with self.assertRaises(Uncertain):
            self.control.call(self.token, 'get_status', {})
        request = self.control.inspect()['pending']['request_id']
        self.control.attach_handle(request, 'exec', 'fixture-handle')
        self.assertEqual(self.control.inspect()['pending']['orchestrator_handle']['value'], 'fixture-handle')
        with self.assertRaises(Error):
            self.control.reconcile(self.token, 'only a timeout', 'assumed', False)
        self.control.reconcile(self.token, 'fixture terminal response', 'Reviewed terminal evidence', True)
        self.assertNotIn('pending', self.control.inspect())

    def test_prohibited_load_and_unvalidated_argument_do_not_send(self):
        count = len(self.calls)
        with self.assertRaises(Error):
            self.control.call(self.token, 'load_game', {}, 'Undo a loss')
        with self.assertRaises(Error):
            self.control.call(self.token, 'order_pawn', {'bogus': 3}, 'Bad')
        self.assertEqual(len(self.calls), count)

    def test_changed_game_clears_binding(self):
        changed = fixture('status'); changed['colonyName'] = 'Another game'
        self.responses.append(changed)
        response = self.control.call(self.token, 'get_status', {})
        self.assertIn('identity_mismatch', response)
        with self.assertRaises(Error):
            self.control.call(self.token, 'order_pawn', {'id': 'PawnA'}, 'Wrong game', 'movement')



class HistoryKnowledgeTests(Workspace):
    def test_reviewed_screenshot_checkpoint_idempotence(self):
        self.ingest('get_status', {}, fixture('status'))
        obs_id = self.camp.state()['last_observation']
        png = self.root / 'fixture.png'
        def chunk(kind, value):
            return struct.pack(">I", len(value)) + kind + value + struct.pack(">I", zlib.crc32(kind + value) & 0xffffffff)
        png.write_bytes(b'\x89PNG\r\n\x1a\n' +
                        chunk(b"IHDR", struct.pack(">IIBBBBB", 20, 20, 8, 2, 0, 0, 0)) +
                        chunk(b"IDAT", zlib.compress((b"\x00" + b"\xff" * 60) * 20)) +
                        chunk(b"IEND", b""))
        shot = add_shot(self.camp, png, 300000, 'Synthetic test image', 'Fixture only', 'Test framing', origin='fixture', evidence=[obs_id])
        chapter = self.root / 'chapter.md'
        chapter.write_text('# A fixture chapter\n\nThe example colony reached the checkpoint.\n\n' +
                           f"![Fixture]({shot['path']})\n")
        spec = {'day': 5, 'chapter_file': str(chapter), 'evidence': [obs_id], 'shots': [shot['id']],
                'review': 'Offline synthetic fixture; no claim of real gameplay.',
                'report': {'overview': 'Fixture', 'accomplishments': 'Fixture checkpoint',
                           'losses_and_risks': 'Synthetic', 'next_five_days': 'Test', 'next_year': 'Test'}}
        with self.assertRaises(Error):
            checkpoint(self.camp, spec)
        review_shot(self.camp, shot['id'], 'Synthetic image for local validation only.')
        checkpoint(self.camp, spec)
        checkpoint(self.camp, spec)
        self.assertEqual((self.camp.path / 'History.md').read_text().count('# A fixture chapter'), 1)
        self.assertEqual(self.camp.checkpoints()['next_day'], 10)

    def test_future_checkpoint_and_missing_image_refused(self):
        self.ingest('get_status', {}, fixture('status'))
        with self.assertRaises(Error):
            checkpoint(self.camp, {'day': 10, 'chapter_file': 'missing'})

    def test_disputed_lesson_is_not_active_guidance(self):
        lesson = {'id': 'test-lesson', 'title': 'Test', 'topics': ['combat'],
                  'applicability': {'required_dlc': []}, 'observed': 'An interrupted order',
                  'explanation': 'Hypothesis', 'recommendation': 'Check', 'exceptions': 'May vary',
                  'verify': 'Read actual outcome', 'evidence': [{'source': 'fixture:local'}],
                  'status': 'provisional'}
        save_lesson(self.root, lesson, 'Reviewed fixture', shared=True)
        self.assertEqual(len(retrieve(self.root, 'combat')['lessons']), 1)
        lesson['status'] = 'disputed'
        save_lesson(self.root, lesson, 'Contradictory fixture evidence', shared=True)
        result = retrieve(self.root, 'combat')
        self.assertFalse(result['lessons'])
        self.assertEqual(result['cautions'][0]['status'], 'disputed')

    def test_metrics_unknown_and_explicit_clock_scope(self):
        self.ingest('get_status', {}, fixture('status'))
        result = metrics(self.camp)
        self.assertIsNone(result['request_seconds']['median'])
        self.assertIn('model reasoning', result['unmeasured_unless_explicitly_marked'])

    def test_fresh_context_cli_needs_no_parent_files(self):
        command = [sys.executable, '-B', str(ROOT / 'rw'), '--root', str(self.root),
                   '--campaign', 'example', 'brief']
        result = subprocess.run(command, text=True, capture_output=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn('all colony facts are unknown', result.stdout)
        status = [sys.executable, '-B', str(ROOT / 'rw'), '--root', str(self.root),
                  '--campaign', 'example', 'ingest', 'get_status', '--origin', 'fixture',
                  '--response', str(FIXTURES / 'status.json')]
        self.assertEqual(subprocess.run(status, capture_output=True).returncode, 0)
        result = subprocess.run(command, text=True, capture_output=True)
        self.assertIn('Medical treatment needed', result.stdout)
        self.assertIn('Away fixture', result.stdout)


class AdditionalRegressionTests(Workspace):
    def test_changed_selection_does_not_verify_wrong_pawn(self):
        action = self.fixture_action("normal_ui", {}, "Equip the intended pawn", "equipment", {
            "tool": "get_pawn", "args": {"id": "PawnA", "tab": "gear"},
            "all": [{"path": "equipment.0.label", "op": "eq", "value": "Rifle"}]})
        self.camp.action_update(action["id"], "accepted", internal=True)
        self.ingest("get_pawn", {"id": "PawnB", "tab": "gear"},
                    {"id": "PawnB", "equipment": [{"label": "Rifle"}], "apparel": []})
        self.assertEqual(self.camp._actions()[action["id"]]["status"], "accepted")

    def test_malformed_lists_are_not_known_empty(self):
        obs = normalize('get_area', {}, {'things': None, 'terrainSummary': {}}, 'c', 's')
        self.assertEqual(obs['completeness'], 'partial')
        self.assertIn('Malformed', compact(obs)['warnings']['warning'])

    def test_plain_mcp_warning_is_preserved(self):
        response = {'content': [{'type': 'text', 'text': '{"ok":true}'},
                                {'type': 'text', 'text': 'A new hazard needs inspection.'}]}
        obs = normalize('order_pawn', {}, response, 'c', 's')
        self.assertIn('hazard', compact(obs)['warnings']['_mcpAdditionalText'][0])

    def test_protocol_notifications_are_preserved(self):
        payload = {'jsonrpc': '2.0', 'id': 1, 'result': {'content': [{'type': 'text', 'text': '{"ok":true}'}]},
                   '_transportNotifications': [{'method': 'notifications/tools/list_changed'}]}
        obs = normalize('order_pawn', {}, payload, 'c', 's')
        self.assertEqual(compact(obs)['warnings']['_protocolNotifications'][0]['method'],
                         'notifications/tools/list_changed')

    def test_resolved_detail_can_leave_context_without_deleting_evidence(self):
        first = self.ingest('get_pawn', {'id': 'PawnA'}, {'id': 'PawnA', 'job': 'isolated'})
        current = self.ingest('get_pawn', {'id': 'PawnA'}, {'id': 'PawnA', 'job': 'safe'})
        self.camp.retire(first['id'], current['id'], 'Reviewed return to safety in the current snapshot')
        self.assertNotIn('isolated', self.camp.refresh())
        self.assertEqual(self.camp.observation(first['id'])['data']['job'], 'isolated')
        self.ingest('get_pawn', {'id': 'PawnA'}, {'id': 'PawnA', 'job': 'new risk'})
        self.assertIn('new risk', self.camp.refresh())

    def test_recurrence_and_deadline_trigger_review(self):
        self.ingest('get_status', {}, fixture('status'))
        self.camp.issue({'title': 'Recurring cause', 'rationale': 'Risk', 'next_action': 'Investigate',
                         'revisit': 'Now', 'revisit_tick': 299999, 'resolution': 'Cause removed',
                         'occurrences': 2})
        review = self.camp.issue_reviews()[0]
        self.assertTrue(review['recurring'])
        self.assertTrue(review['revisit_due'])

    def test_corrupt_png_refused(self):
        png = self.root / 'bad.png'
        png.write_bytes(b'\x89PNG\r\n\x1a\n' + b'broken')
        with self.assertRaises(Error):
            add_shot(self.camp, png, 0, 'test', 'test', 'test')

    def test_invalid_issue_deadline_cannot_poison_memory(self):
        with self.assertRaises(Error):
            self.camp.issue({'title': 'Issue', 'rationale': 'why', 'next_action': 'act',
                             'revisit': 'soon', 'resolution': 'proof', 'revisit_tick': 'tomorrow'})
        self.assertEqual(self.camp._issues(), {})

    def test_skipped_checkpoint_is_still_due(self):
        self.camp.event({'kind': 'checkpoint', 'day': 15, 'summary': 'Imported checkpoint'})
        self.assertEqual(self.camp.checkpoints()['next_day'], 5)


class MoreControlTests(ControlFixture):
    def test_whole_batch_rejects_bad_later_tool_before_first_action(self):
        from tools.rimworld.cli import parser, run
        steps = self.root / 'batch.json'
        atomic_json(steps, [
            {'tool': 'order_pawn', 'args': {'id': 'PawnA', 'command': 'Rescue'},
             'intent': 'Rescue', 'family': 'rescue'},
            {'tool': 'load_game', 'args': {}, 'intent': 'Forbidden'}])
        args = parser().parse_args(['--root', str(self.root), '--campaign', 'example',
                                    'batch', '--token', self.token, '--file', str(steps)])
        before = len(self.calls)
        with patch('tools.rimworld.cli.Control', return_value=self.control):
            with self.assertRaises(Error):
                run(args)
        self.assertEqual(len(self.calls), before)

    def test_catalog_change_requires_reviewed_reconnect(self):
        atomic_json(self.control.path / 'catalog-stale.json', {'reason': 'schema changed'})
        before = len(self.calls)
        with self.assertRaises(Error):
            self.control.call(self.token, 'get_status', {})
        self.assertEqual(len(self.calls), before)

    def test_explicit_untracked_low_impact_change_keeps_request_only(self):
        self.responses.append({'ok': True, 'executed': True})
        self.control.call(self.token, 'order_pawn', {'id': 'PawnA', 'command': 'Ordinary task'},
                          intent='Low-impact work', track=False)
        self.assertFalse(self.camp._actions())
        self.assertFalse((self.control.path / 'pending.json').exists())

    def test_batch_stops_on_new_warning(self):
        from tools.rimworld.cli import parser, run
        steps = self.root / 'batch.json'
        atomic_json(steps, [{'tool': 'get_status'}, {'tool': 'get_pawn', 'args': {'id': 'PawnA'}}])
        changed = fixture('status')
        changed['_threatWarning'] = 'New fire'
        self.responses.append(changed)
        args = parser().parse_args(['--root', str(self.root), '--campaign', 'example',
                                    'batch', '--token', self.token, '--file', str(steps)])
        before = len(self.calls)
        with patch('tools.rimworld.cli.Control', return_value=self.control):
            result = run(args)
        self.assertTrue(result['stopped'])
        self.assertEqual(len(self.calls), before + 1)


if __name__ == '__main__':
    unittest.main()
