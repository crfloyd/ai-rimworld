# Decision-Loop Friction Batch Implementation Plan

> **Status: implemented in 0.9.1.** All nine tasks landed; see CHANGELOG.md and VALIDATION.md.
>
> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Remove the tooling friction recorded in live play so an agent can discover every affordance, recover from a bounded read without losing a batch, and spend its context on facts that change decisions.

**Architecture:** Three seams change. Coverage classification gains a recoverable class so an upstream size guard stops one query instead of a whole composition. A new `hints` module turns bounded results into actionable retry advice and recognizes receipts that report failure for an already-satisfied intent. Capability discovery becomes a small domain index over the complete catalog with operational workflow notes, and the CLI gains the same entry points the MCP surface already has.

**Tech Stack:** Python 3 standard library only, `pyenv exec python` via `./rw`, `unittest` run under `pytest`.

**Spec:** `docs/friction.md` (live-play report) plus the decisions recorded in Global Constraints below.

## Global Constraints

- Run everything through `./rw` or the pinned `pyenv exec python`. Never change global Python. Never use raw `npm`/`yarn`.
- No game, MCP or UI calls during implementation. Every test runs against fixtures and saved receipts.
- Never weaken a real safety stop. Unpaused state, identity mismatch, unparseable JSON, upstream errors, missing or malformed fields keep their existing hard stop and the existing reason string `Identity, pause, JSON or coverage requires review`.
- Only the upstream large-output guard (`largeOutput: true`) and an upstream `truncated` flag become recoverable. Nothing else changes class.
- Never rewrite a game receipt. `ok: false` stays `ok: false`. Facade interpretation is added alongside as new keys, never by editing upstream fields.
- Never assert an unverified game behavior in a hint. Whether `trade_action cancel` can reverse a committed deal is unknown and stays unknown until the playtest.
- Leave the payload backstop at 32768 bytes, the composition query cap at 32, and the action batch cap at 16. None of them fired in 304 recorded calls.
- `load_game` is the one denied tool and is deliberately excluded from capability domains.
- The full offline suite must pass after every task: `python3 -m pytest tests -q`.

## File Structure

| File | Responsibility |
|---|---|
| `tools/rimworld/hints.py` | **New.** Native narrowing filters per tool, large-output retry advice, already-satisfied order recognition, trade-row gap detection. Pure functions, no I/O, no imports from `facade` or `composition`. |
| `tools/rimworld/composition.py` | Recoverable vs blocking coverage classification; decision preset `world_kind` and `visitors`; degraded sections survive a composition. |
| `tools/rimworld/facade.py` | Same recoverable rule for `rw_wait verify`; receipt annotation; `context:brief`; tightened event topics; narrowing hints on single reads and on budget truncation. |
| `tools/rimworld/capabilities.py` | Complete domain coverage, domain index overview, workflows carrying operational notes. |
| `tools/rimworld/cli.py` | `capabilities` overview/domain/workflow flags, JSON errors that name the right sibling flags, `--select` pointer suggestions. |
| `tests/test_hints.py` | **New.** Unit coverage for `hints.py`. |
| `tests/test_friction_batch.py` | **New.** End-to-end coverage for every friction item, built from the shapes in the recorded receipts. |
| `tests/test_composition.py`, `tests/test_facade.py`, `tests/test_discovery.py` | Additions where the existing fixtures already fit. |
| `docs/facade.md`, `docs/composition.md`, `AGENTS.md`, `PLAN.md`, `VALIDATION.md`, `TODO.md`, `docs/friction.md` | Operator-facing text. |

---

### Task 1: Narrowing hints and receipt recognition

**Files:**
- Create: `tools/rimworld/hints.py`
- Test: `tests/test_hints.py`

**Interfaces:**
- Consumes: nothing.
- Produces: `NARROW: dict[str,str]`, `CONFIRM: tuple[str,...]`, `oversized(data) -> bool`, `narrowing(tool, data=None) -> dict|None`, `job_phrase(label) -> str|None`, `already_satisfied(tool, args, data) -> dict|None`, `withheld_rows(tool, data) -> dict|None`.

- [x] **Step 1: Write the failing test**

```python
import unittest
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
        import json
        from pathlib import Path
        catalog = json.load(open(Path(__file__).resolve().parents[1] / 'api/catalog.json'))['tools']
        for tool in NARROW:
            self.assertIn(tool, catalog)
```

- [x] **Step 2: Run test to verify it fails**

Run: `python3 -m pytest tests/test_hints.py -q`
Expected: FAIL with `ModuleNotFoundError: No module named 'tools.rimworld.hints'`

- [x] **Step 3: Write minimal implementation**

```python
"""Actionable recovery advice for bounded reads and receipts. No strategy, no I/O."""

# Filters that narrow a read at the source. Keys are exact catalog tool names.
NARROW = {
 'list_things': 'category, defName, faction (any/player/hostile/neutral/wild), nearId or nearX+nearZ with radius, limit',
 'list_world_objects': 'kind (settlements/caravans/sites/space), faction name substring, fromTile',
 'list_unmanaged_items': 'limit, mapIndex',
 'get_area': 'minX/maxX/minZ/maxZ bounds, thing, layer, scale, summary',
 'get_map': 'summary, and an explicit bounded get_area instead of the whole map',
 'get_world': 'kind and faction filters where offered',
 'room_graph': 'limit, mapIndex',
 'find_world_tiles': 'explicit search constraints and limit',
 'list_trade': 'filter (label substring), limit',
 'get_pawn': 'tab (needs/health/gear/bio), detail',
 'list_colonists': 'no source filter; select fields or row_fields instead',
 'get_window_ui': 'for a trade dialog use list_trade; otherwise select only the needed fields',
}

# Tools whose schema offers the deliberate override of the upstream size guard.
CONFIRM = ('find_world_tiles', 'get_area', 'get_map', 'get_world', 'list_things',
           'list_unmanaged_items', 'list_world_objects', 'room_graph')

WIDE = ('Re-run with confirm:true to accept the full result. Delivery stays bounded and '
        'rw_retrieve {observation, view:"full"} then returns all of it without another game call.')


def oversized(data):
    """True only for the upstream large-output guard, which answers instead of the query."""
    return isinstance(data, dict) and data.get('largeOutput') is True


def narrowing(tool, data=None):
    """Both sanctioned exits from a size guard, named explicitly."""
    hint = {}
    if tool in NARROW:
        hint['narrow_with'] = NARROW[tool]
    if tool in CONFIRM:
        hint['wide_read'] = WIDE
    if not hint:
        return None
    if isinstance(data, dict):
        for key in ('chars', 'items', 'message'):
            if key in data:
                hint[key] = data[key]
    hint['basis'] = 'The query never ran; this is the guard speaking. Narrowing is usually cheaper than confirming.'
    return hint


PREFIXES = ('prioritize working on ', 'already working on ')


def job_phrase(label):
    """The job a float-menu label refers to, or None when it is not a work label."""
    text = str(label).strip().lower() if label is not None else ''
    for prefix in PREFIXES:
        if text.startswith(prefix):
            return text[len(prefix):].strip()
    return None


def already_satisfied(tool, args, data):
    """A prioritize order the pawn is already running is not a failed order."""
    if tool != 'order_pawn' or not isinstance(data, dict) or data.get('ok') is not False:
        return None
    if not str(data.get('error', '')).startswith('No order matched'):
        return None
    wanted = job_phrase((args or {}).get('command'))
    if not wanted:
        return None
    for offered in data.get('available') or []:
        if str(offered).strip().lower().startswith('already working on ') and job_phrase(offered) == wanted:
            return {'requested': (args or {}).get('command'), 'offered': offered,
                    'executed': False, 'intent_already_met': True,
                    'meaning': 'The pawn is already doing this job. Nothing was re-issued and nothing changed.'}
    return None


def withheld_rows(tool, data):
    """Upstream counted more tradeables than it returned; name the gap rather than hide it."""
    if tool != 'list_trade' or not isinstance(data, dict):
        return None
    returned, counted = data.get('returned'), data.get('tradeableCount')
    if type(returned) is not int or type(counted) is not int or returned >= counted:
        return None
    return {'returned': returned, 'counted': counted,
            'note': 'Upstream returned fewer rows than it counted. Colony silver is reported separately '
                    'in the silver field. Use filter to locate a specific item by label.'}
```

- [x] **Step 4: Run test to verify it passes**

Run: `python3 -m pytest tests/test_hints.py -q`
Expected: PASS, 9 tests

- [x] **Step 5: Commit**

```bash
git add tools/rimworld/hints.py tests/test_hints.py
git commit -m "Add narrowing hints and receipt recognition helpers"
```

---

### Task 2: Recoverable coverage stops one query, not the batch

**Files:**
- Modify: `tools/rimworld/composition.py` (`capture`, `Composer.read`, `Composer.execute`, `compact_result`)
- Modify: `tools/rimworld/facade.py` (`run_reads`, `wait_sequence`)
- Test: `tests/test_friction_batch.py`

**Interfaces:**
- Consumes: `hints.narrowing`, `hints.oversized` from Task 1.
- Produces: `composition.capture(control, value) -> (section, problem|None)` where `problem` is `{'blocking': bool, 'reason': str, 'retry': dict|None}`. `Composer.read(queries, output, degraded=None)`. `facade.run_reads(...) -> (sections, evidence, not_run, degraded)`.

Note for the implementer: `capture` previously returned a plain boolean as its second value and both call sites tested it with `if incomplete:`. Every call site must be updated in this task or a recoverable result will silently stop a batch.

- [x] **Step 1: Write the failing test**

```python
import json
from test_system import ControlFixture
from tools.rimworld.core import Error
from tools.rimworld.session import Session

LARGE_WORLD = {'_paused': True, 'chars': 58785, 'items': 263, 'largeOutput': True,
               'message': 'Output is large (58785 chars). Re-call with confirm=true to get it anyway, '
                          'or narrow it: narrow with kind (settlements/caravans/sites/space) '
                          'and/or a faction name filter.'}


class FrictionBatch(ControlFixture):
    def setUp(self):
        super().setUp()
        self.session = Session(self.control, self.token)

    def body(self, name, args=None, rid=1):
        r = self.session.handle({'jsonrpc': '2.0', 'id': rid, 'method': 'tools/call',
                                 'params': {'name': name, 'arguments': args or {}}})
        if 'error' in r:
            raise Error(r['error']['message'])
        return json.loads(r['result']['content'][0]['text'])

    def add_tools(self, *names):
        from pathlib import Path
        from tools.rimworld.core import read_json, atomic_json
        real = read_json(Path(__file__).resolve().parents[1] / 'api/catalog.json')['tools']
        path = self.camp.path / 'raw/catalog.json'
        catalog = read_json(path)
        for name in names:
            catalog['tools'][name] = real[name]
        atomic_json(path, catalog)

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
        self.assertEqual(len(self.calls[-2:]), 2)

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
```

- [x] **Step 2: Run test to verify it fails**

Run: `python3 -m pytest tests/test_friction_batch.py -q`
Expected: FAIL. The first test fails on `KeyError: 'degraded'` because the composition still stops.

- [x] **Step 3: Write minimal implementation**

In `tools/rimworld/composition.py`, replace the body of `capture` after `controls` with an explicit classification and return the problem record:

```python
def capture(control, value):
    obs=control.campaign.observation(value['id'])
    result=section(control.campaign,obs)
    children=[control.campaign.observation(c['id']) for c in value.get('bundle',[])]
    if children:
        result['bundle_coverage']=[{'observation':c['id'],'tool':c['tool'],
            'completeness':c['completeness'],'missing':c['missing']} for c in children]
    controls={k:value[k] for k in ('identity_mismatch','pause_guard','wait_budget') if k in value}
    if controls:result['control']=controls
    return result,coverage_problem(value,obs,result,children)


REVIEW='Identity, pause, JSON or coverage requires review'


def coverage_problem(value, obs, result, children):
    """Separate a recoverable bounded answer from a state that genuinely needs review.

    Only the upstream size guard and an upstream truncation flag are recoverable:
    they are complete, self-describing refusals that name their own retry. Every
    other incompleteness keeps its original hard stop.
    """
    from .hints import narrowing, oversized
    data=obs.get('data') if isinstance(obs.get('data'),dict) else {}
    review=(bool(value.get('identity_mismatch') or value.get('pause_guard'))
            or bool(result.get('metadata',{}).get('unusable_json_blocks'))
            or result.get('result_properties',{}).get('isError') is True
            or obs['completeness']=='unavailable'
            or bool(obs.get('missing')) or bool(obs.get('malformed'))
            or any(c['completeness']!='known' for c in children))
    if review:
        return {'blocking':True,'reason':REVIEW}
    if obs['completeness']=='known':
        return None
    if oversized(data) or data.get('truncated'):
        reason=('The upstream large-output guard answered instead of the query'
                if oversized(data) else 'Upstream bounded this result')
        return {'blocking':False,'reason':reason,'retry':narrowing(obs['tool'],data)}
    return {'blocking':True,'reason':REVIEW}
```

Update `Composer.read` to record rather than stop for a recoverable problem:

```python
    def read(self, queries, output, degraded=None):
        for i,q in enumerate(queries):
            self.record['phase']='reading';self.record['next_query']=q;self.save()
            cached=self.memo.reusable(q['tool'],q['args']) if self.memo is not None and self.reuse else None
            if cached:
                value={'id':cached};self.record.setdefault('reused',[]).append({'key':q['key'],'id':cached})
            else:
                value=self.control.call(self.token,q['tool'],q['args'],driver=self.driver)
                self.on_observation(value['id'])
            output[q['key']],problem=capture(self.control,value)
            if cached:output[q['key']]['reused']=True
            self.record['observations'].append({'key':q['key'],'id':value['id'],'source':output[q['key']]['source'],'coverage':output[q['key']]['coverage']});self.save()
            if problem and not problem['blocking']:
                output[q['key']]['degraded']=problem
                if degraded is not None:degraded.append(q['key'])
                self.record.setdefault('degraded',[]).append(q['key']);self.save()
                continue
            if problem:
                return {'reason':problem['reason'],'after':q['key'],'not_run':[x['key'] for x in queries[i+1:]]}
        return None
```

In `Composer.execute`, thread the degraded list through both read phases:

```python
            result={'composition':self.record['request_id'],'sections':{},'advancement_requested':False,
                    'capture':'sequential','unrequested':'unknown','degraded':[]}
            try:
                result['stopped']=self.read(queries,result['sections'],result['degraded'])
```

and in `choose`, replace `result['stopped']=self.read(verify,result['verification'])` with
`result['stopped']=self.read(verify,result['verification'],result['degraded'])`.

In `compact_result`, drop the key when nothing degraded, immediately before `result['queried_complete']=...`:

```python
    if not result.get('degraded'):result.pop('degraded',None)
```

In `choose`, the abstain condition already calls `interruptions(...)`; leave it untouched so a guard never acts on a degraded section.

In `tools/rimworld/facade.py`, update `run_reads` to the same rule:

```python
def run_reads(control,token,queries,memo,observed,driver,sequence=None):
    expanded=expand(queries)
    for query in expanded:preflight(control,query)
    sections={};evidence=[]
    not_run=[];degraded=[]
    for index,query in enumerate(expanded):
        cached=memo.reusable(query['tool'],query['args']) if memo is not None else None
        if cached:value={'id':cached}
        else:
            value=control.call(token,query['tool'],query['args'],driver=driver)
            if observed:observed(value['id'])
        if sequence is not None:sequence.observed('verify_'+query['key'],value,requested=query,reused=bool(cached))
        section,problem=capture(control,value)
        compacted=compact_result({'sections':{query['key']:section},'verification':{},'capture':'sequential',
                                  'advancement_requested':False,'unrequested':'unknown','stopped':None})['sections'][query['key']]
        if cached:compacted['reused']=True
        if problem and not problem['blocking']:
            compacted['degraded']=problem;degraded.append(query['key'])
        sections[query['key']]=compacted;evidence.append(value['id'])
        if problem and problem['blocking']:
            not_run=[q['key'] for q in expanded[index+1:]];break
    return sections,evidence,not_run,degraded
```

In `wait_sequence`, unpack the fourth value and surface it:

```python
            sections,evidence,not_run,degraded=run_reads(control,token,verify,memo,observed,'facade_wait_verify',sequence)
            body['verification']=sections;body['verification_evidence']=evidence
            body['verification_complete']=not not_run;body['verification_not_run']=not_run
            if degraded:body['verification_degraded']=degraded
```

Because a test asserts `verification_degraded` is present as a list, set it unconditionally when `verify` was requested:

```python
            body['verification_degraded']=degraded
```

- [x] **Step 4: Run the new tests, then the whole suite**

Run: `python3 -m pytest tests/test_friction_batch.py -q`
Expected: PASS, 4 tests

Run: `python3 -m pytest tests -q`
Expected: PASS, no regressions. If `tests/test_composition.py` asserts the old two-value `capture` contract, update those call sites to the new record shape rather than reverting the behavior.

- [x] **Step 5: Commit**

```bash
git add tools/rimworld/composition.py tools/rimworld/facade.py tests/test_friction_batch.py
git commit -m "Continue a composition past a recoverable size guard"
```

---

### Task 3: Decision preset stops tripping the guard and can see map visitors

**Files:**
- Modify: `tools/rimworld/composition.py` (`DECISION_TOPICS`, `QUERY`, `expand`, `materialize_decisions`)
- Modify: `tools/rimworld/facade.py` (`event_details` world read)
- Test: `tests/test_friction_batch.py`

**Interfaces:**
- Consumes: Task 2's degraded handling.
- Produces: decision query accepts optional `world_kind` (enum `all|settlements|caravans|sites|space`, default `caravans`) and topic `visitors`. Packet keys `world` and `visitors`.

- [x] **Step 1: Write the failing test**

```python
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
        self.responses.extend([fixture_status(), {'_paused': True, 'things': [
            {'id': 'Human169082', 'label': 'Chaz', 'kind': 'Town_Trader', 'x': 140, 'z': 94}]}])
        value = self.body('rw_observe', {'queries': [
            {'key': 'now', 'preset': 'decision', 'include': ['core', 'visitors']}]})
        self.assertEqual(self.calls[-1]['arguments'],
                         {'category': 'pawn', 'faction': 'neutral', 'limit': 40})
        self.assertEqual(value['decisions']['now']['visitors']['things'][0]['label'], 'Chaz')

    def test_a_large_world_no_longer_cancels_the_rest_of_a_decision_packet(self):
        self.add_tools('list_world_objects', 'get_pawn')
        self.responses.extend([fixture_status(), LARGE_WORLD,
                               {'_paused': True, 'id': 'Human1', 'name': 'Tatyana', 'mood': 40}])
        value = self.body('rw_observe', {'queries': [
            {'key': 'now', 'preset': 'decision', 'include': ['core', 'world'],
             'world_kind': 'all', 'pawns': [{'id': 'Human1', 'include': ['summary']}]}]})
        self.assertNotIn('stopped', value)
        self.assertEqual(value['decisions']['now']['pawns'][0]['facets']['summary']['name'], 'Tatyana')
        self.assertEqual(value['degraded'], ['now.world'])
```

Add this helper near the top of `tests/test_friction_batch.py` so the status read has a real shape:

```python
def fixture_status():
    from test_system import fixture
    return fixture('status')
```

- [x] **Step 2: Run test to verify it fails**

Run: `python3 -m pytest tests/test_friction_batch.py -q -k decision`
Expected: FAIL. The world read is dispatched with `{}` and `visitors` is rejected by the schema.

- [x] **Step 3: Write minimal implementation**

In `tools/rimworld/composition.py`:

```python
DECISION_TOPICS=('core','alerts','food','medical','mood','threat','work','research','conditions','world','visitors')
WORLD_KINDS=('all','settlements','caravans','sites','space')
```

Add `world_kind` to the decision branch of `QUERY`:

```python
    obj({'key':KEY,'preset':{'const':'decision'},'include':includes(DECISION_TOPICS),
         'pawns':{'type':'array','items':DECISION_PAWN,'maxItems':8},
         'world_kind':{'enum':list(WORLD_KINDS)},
         'mood_below':{'type':'number','minimum':0,'maximum':100}},['key','preset'])]}
```

In `expand`, inside the decision branch, replace the world line and add visitors:

```python
            if any(t not in ('world','visitors') for t in topics):expanded.append({'key':prefix+'.status','tool':'get_status','args':{}})
            if 'world' in topics:
                expanded.append({'key':prefix+'.world','tool':'list_world_objects',
                                 'args':{'kind':q.get('world_kind','caravans')}})
            if 'visitors' in topics:
                expanded.append({'key':prefix+'.visitors','tool':'list_things',
                                 'args':{'category':'pawn','faction':'neutral','limit':40}})
```

In `materialize_decisions`, after the world block:

```python
        visitors=result['sections'].pop(key+'.visitors',None)
        if visitors and 'data' in visitors:packet['visitors']=visitors['data']
```

The food facet is built from the status bundle alone, so it cannot see a suspended cooking bill or a loose pile. Say so in the packet rather than letting an empty-looking larder read as proof. In `decision_status`, extend the food block:

```python
    if 'food' in topics:
        result['food']={'resources':_resources(resources,('meal','meat','rice','pemmican','berr','egg','milk','corn','potato')),
                        'alerts':[a for a in alerts.get('activeAlerts',[]) if 'food' in str(a.get('label','')).lower()],
                        'not_covered':'Stockpiled counts only. A suspended cooking bill (list_bills on the stove) and '
                                      'loose or forbidden food (list_unmanaged_items) are not in this packet and are the '
                                      'two most common causes of a food alert with ingredients on hand.'}
```

Add a test for it beside the other decision tests:

```python
    def test_the_food_facet_names_what_it_cannot_see(self):
        self.responses.extend([fixture_status()])
        value = self.body('rw_observe', {'queries': [
            {'key': 'now', 'preset': 'decision', 'include': ['food']}]})
        note = value['decisions']['now']['food']['not_covered']
        self.assertIn('list_bills', note)
        self.assertIn('list_unmanaged_items', note)
```

In `tools/rimworld/facade.py`, `event_details`, replace the unfiltered world read so automatic context never trips the same guard, and add the map-visitor read that the recorded run had no way to reach:

```python
    if 'world' in topics:
        value=control.call(token,'list_world_objects',{'kind':'caravans'},driver='facade_wait_context')
        if observed:observed(value['id'])
        sequence.observed('event_world',value);obs=control.campaign.observation(value['id'])
        details['world']={'data':obs['data'],'evidence':obs['id'],'scope':'kind=caravans',
                          'completeness':obs['completeness'],'missing':obs['missing']}
        visitors=control.call(token,'list_things',{'category':'pawn','faction':'neutral','limit':20},
                              driver='facade_wait_context')
        if observed:observed(visitors['id'])
        sequence.observed('event_visitors',visitors)
        visitor_obs=control.campaign.observation(visitors['id'])
        details['visitors']={'rows':[responder_row(r) for r in (visitor_obs['data'].get('things') or [])
                                     if isinstance(r,dict)],
                             'evidence':visitor_obs['id'],
                             'basis':'Neutral pawns on this map. A visiting trade caravan is map pawns, not a world caravan row.',
                             'completeness':visitor_obs['completeness'],'missing':visitor_obs['missing']}
```

- [x] **Step 4: Run tests**

Run: `python3 -m pytest tests/test_friction_batch.py -q && python3 -m pytest tests -q`
Expected: PASS

- [x] **Step 5: Commit**

```bash
git add tools/rimworld/composition.py tools/rimworld/facade.py tests/test_friction_batch.py
git commit -m "Narrow decision world reads and add map-visitor discovery"
```

---

### Task 4: Receipts say what they mean

**Files:**
- Modify: `tools/rimworld/facade.py` (`self_contained`, `explicit_failure`, `action_batch`, `budget`, `NATIVE` removal)
- Test: `tests/test_friction_batch.py`

**Interfaces:**
- Consumes: `hints.already_satisfied`, `hints.narrowing`, `hints.oversized`, `hints.withheld_rows`, `hints.NARROW`.
- Produces: `facade.annotate(body, obs) -> dict`. Compact bodies may carry `retry`, `already_satisfied`, `rows_withheld`, `deal`.

- [x] **Step 1: Write the failing test**

```python
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
        from tools.rimworld.composition import delivered
        delivered(self.control, self.token, value['composition'])

    def test_a_genuine_order_failure_still_aborts_the_batch(self):
        self.responses.extend([{'ok': False, '_paused': True, 'error': 'Pawn is downed.', 'available': []}])
        value = self.body('rw_act', {'independent': True, 'actions': [
            {'tool': 'order_pawn', 'args': {'id': 'a', 'command': 'Prioritize working on campfire (blueprint)'}},
            {'tool': 'order_pawn', 'args': {'id': 'b', 'command': 'Go here', 'x': 1, 'z': 2}}]})
        self.assertTrue(value['stopped'])
        self.assertEqual(value['not_run'], [1])
        from tools.rimworld.composition import delivered
        delivered(self.control, self.token, value['composition'])

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
```

- [x] **Step 2: Run test to verify it fails**

Run: `python3 -m pytest tests/test_friction_batch.py -q -k "already or oversized or withheld or deal"`
Expected: FAIL with `KeyError: 'already_satisfied'`

- [x] **Step 3: Write minimal implementation**

In `tools/rimworld/facade.py`, delete the module-level `NATIVE` dict and import the shared table instead. Replace `if tool in NATIVE: trial['suggest']=NATIVE[tool]` and the twin line in the fallback with `hints.NARROW`:

```python
from .hints import NARROW, already_satisfied, narrowing, oversized, withheld_rows
```

and inside `budget`:

```python
                if tool in NARROW: trial['suggest']=NARROW[tool]
```

```python
            **({'suggest':NARROW[tool]} if tool in NARROW else {})
```

Add one annotation function and call it from `self_contained`:

```python
def annotate(body, obs):
    """Facade interpretation alongside the receipt. Upstream fields are never edited."""
    data=obs.get('data') if isinstance(obs.get('data'),dict) else {}
    tool,args=obs.get('tool'),obs.get('args') or {}
    if oversized(data):
        hint=narrowing(tool,data)
        if hint:body['retry']=hint
    found=already_satisfied(tool,args,data)
    if found:body['already_satisfied']=found
    gap=withheld_rows(tool,data)
    if gap:body['rows_withheld']=gap
    if tool=='trade_action' and args.get('action')=='accept' and data.get('ok') is True:
        body['deal']={'committed':bool(data.get('traded')),'dialog_open':bool(data.get('_dialogOpen')),
                      'next':'A blocking message box must be dismissed with window_action before trade_action cancel.',
                      'confirm_goods':'Bought items land on the ground at the trader. Confirm with list_things '
                                      'near the trader or list_unmanaged_items; get_resources counts hauled stock only.',
                      'unverified':'Whether cancel can reverse a committed deal is not established by this receipt.'}
    return body
```

Call it at the end of `self_contained`, immediately before the `change` block:

```python
    body=annotate(body,obs)
    change=change_metadata(value)
```

Make an already-satisfied order a non-blocking outcome inside an independent batch. In `action_batch`, after `dialog_ok,dialog_window=expected_same_dialog(...)`:

```python
            satisfied=bool(body.get('already_satisfied'))
            if dialog_ok:expected_window=dialog_window
            if (explicit_failure(body) and not satisfied) or (body.get('requires_review') and not dialog_ok and not satisfied):
```

- [x] **Step 4: Run tests**

Run: `python3 -m pytest tests/test_friction_batch.py -q && python3 -m pytest tests -q`
Expected: PASS

- [x] **Step 5: Commit**

```bash
git add tools/rimworld/facade.py tests/test_friction_batch.py
git commit -m "Annotate receipts for already-running jobs, withheld rows and accepted deals"
```

---

### Task 5: Event context matches the event

**Files:**
- Modify: `tools/rimworld/facade.py` (`event_topics`, new `event_text`, `WAIT_SCHEMA`, `wait_sequence`, `rw_wait` description)
- Test: `tests/test_friction_batch.py`

**Interfaces:**
- Consumes: nothing new.
- Produces: `facade.event_text(body) -> str`. `rw_wait` accepts `context` values `auto`, `brief`, `none`.

Why this changes: `event_topics` matched substrings over the whole serialized body, including our own field names and the standing threat warning. During one berserk episode every wait therefore pulled the full mood, medical, threat and gear sweep. Twelve such waits cost 194 KB. Scoping the match to the actual event narrative keeps a real raid loud and stops a standing warning from re-triggering forever. The threat flag itself is on every response regardless, so nothing is hidden; only the extra reads stop.

- [x] **Step 1: Write the failing test**

```python
    STANDING = {'_paused': True, 'cause': 'timeout', 'ticksWaited': 2500, 'pausedAfter': True,
                '_threatWarning': {'count': 1, 'nearestDist': 0,
                                   'hostilesSample': [{'id': 'Human63400', 'kind': 'Colonist',
                                                       'label': 'Tatyana', 'dist': 0}],
                                   'note': 'Hostiles within 50 cells of a colonist.'}}

    def test_a_standing_colonist_warning_does_not_retrigger_a_threat_sweep(self):
        from tools.rimworld.facade import event_topics
        topics = event_topics({'data': self.STANDING})
        self.assertNotIn('threat', topics)
        self.assertNotIn('mood', topics)
        self.assertEqual(topics[:2], ['core', 'alerts'])

    def test_a_real_raid_still_pulls_threat_context(self):
        from tools.rimworld.facade import event_topics
        raid = {'cause': 'letter', 'event': 'Raid: tribal warriors are attacking',
                '_threatWarning': {'count': 6, 'hostilesSample': [{'kind': 'Tribal', 'dist': 12}]}}
        self.assertIn('threat', event_topics({'data': raid}))

    def test_event_topics_ignore_our_own_field_names(self):
        from tools.rimworld.facade import event_topics
        noisy = {'cause': 'timeout', 'colonists': [{'name': 'a', 'mood': 90, 'mentalState': None}]}
        self.assertNotIn('mood', event_topics({'data': noisy}))

    def test_context_brief_skips_the_pawn_and_responder_sweep(self):
        self.responses.extend([
            {'_paused': True, 'cause': 'letter', 'event': 'Tatyana has gone berserk',
             '_notifications': [{'kind': 'letter', 'id': 193}]},
            fixture_status()])
        before = len(self.calls)
        value = self.body('rw_wait', {'maxSeconds': 30, 'context': 'brief'})
        self.assertEqual(len(self.calls) - before, 2)
        self.assertIn('core', value['event_context'])
        self.assertNotIn('affected_pawns', value['event_context'])
        self.assertIn('rw_observe', value['event_context']['detail'])

    def test_context_none_reads_nothing_extra(self):
        self.responses.extend([{'_paused': True, 'cause': 'letter', 'event': 'Tatyana has gone berserk'}])
        before = len(self.calls)
        value = self.body('rw_wait', {'maxSeconds': 30, 'context': 'none'})
        self.assertEqual(len(self.calls) - before, 1)
        self.assertNotIn('event_context', value)
```

- [x] **Step 2: Run test to verify it fails**

Run: `python3 -m pytest tests/test_friction_batch.py -q -k "topics or context or raid or standing"`
Expected: FAIL. `event_topics` returns `threat` and `mood` for the standing warning, and `context: "brief"` is rejected by the schema.

- [x] **Step 3: Write minimal implementation**

In `tools/rimworld/facade.py`, replace `event_topics` and add `event_text` above it:

```python
def event_text(body):
    """Only the event narrative: the wait cause, the event and its notifications.

    The whole serialized body also contains our own field names and a standing
    threat warning, so matching against it re-triggers the same deep sweep on
    every later wait.
    """
    data=body.get('data') if isinstance(body,dict) else None
    if not isinstance(data,dict):return ''
    parts=[data.get('cause'),data.get('event'),data.get('message')]
    notes=data.get('_notifications')
    if isinstance(notes,list):parts.extend(notes)
    elif notes:parts.append(notes)
    return canonical([p for p in parts if p]).lower()


def nonhuman_hostiles(body):
    """A standing warning about a berserk colonist is not an incoming threat."""
    data=body.get('data') if isinstance(body,dict) else None
    warning=data.get('_threatWarning') if isinstance(data,dict) else None
    sample=warning.get('hostilesSample') if isinstance(warning,dict) else None
    if not isinstance(sample,list):return False
    return any(isinstance(row,dict) and str(row.get('kind','')).lower() not in ('colonist','')
               for row in sample)


def event_topics(body):
    text=event_text(body);topics=['core','alerts']
    if any(word in text for word in ('food','meal','starv','malnutrition')):topics.append('food')
    if any(word in text for word in ('injur','infection','disease','bleed','poison','healed','damage')):topics.append('medical')
    if any(word in text for word in ('break risk','mental','wander','berserk','tantrum','mood','daze','binge')):topics.append('mood')
    if any(word in text for word in ('caravan','formation','arriv','trader','visitor')):topics.append('world')
    if any(word in text for word in ('raid','threat','hostile','attack','fire','siege','infestation','manhunter')) or nonhuman_hostiles(body):
        topics.append('threat')
    return list(dict.fromkeys(topics))
```

Widen the `context` enum in `WAIT_SCHEMA`:

```python
                 'force':{'type':'boolean'},'view':VIEW,'context':{'enum':['auto','brief','none']},
```

In `wait_sequence`, gate the deep sweep on the mode:

```python
        mode=args.get('context','auto')
        if mode!='none' and event and context_safe:
```

and inside that block, replace the unconditional `packet.update(event_details(...))` with:

```python
                if mode=='auto':
                    packet.update(event_details(control,token,data or {},status_data,topics,memo,observed,sequence))
                else:
                    packet['detail']=('brief: pawn facets, responders, threat rows and letters were not read. '
                                      'Use context:"auto", or rw_observe for exactly the facets this decision needs.')
```

Update the `rw_wait` description to name the third value:

```python
  'context defaults auto and adds a compact event decision packet; brief keeps only the status packet; none disables it. '
```

- [x] **Step 4: Run tests**

Run: `python3 -m pytest tests/test_friction_batch.py -q && python3 -m pytest tests -q`
Expected: PASS

- [x] **Step 5: Commit**

```bash
git add tools/rimworld/facade.py tests/test_friction_batch.py
git commit -m "Scope event context to the actual event and add a brief level"
```

---

### Task 6: Every tool is discoverable

**Files:**
- Modify: `tools/rimworld/capabilities.py` (`DOMAINS`, `PURPOSE`, `overview`)
- Modify: `tools/rimworld/facade.py` (`CAPABILITY_DOMAINS`, `CAPABILITIES_SCHEMA`, `capabilities`, `rw_capabilities` description)
- Test: `tests/test_discovery.py`

**Interfaces:**
- Consumes: nothing new.
- Produces: `capabilities.DOMAINS` covering every catalog tool except `load_game`; `capabilities.PURPOSE: dict[str,str]` one line per domain; `overview(root, campaign=None, domain=None, workflow=None, full=False)`. `rw_capabilities` accepts `full: true` alongside `overview: true`.

Why the overview shape changes: the curated map named 54 of 113 tools and cost 12008 bytes, and it was fetched five times in one session for 35965 bytes. Covering all 112 permitted tools at that shape would cost about as much as the raw catalog. A domain index costs roughly a tenth and the agent drills into exactly one domain.

- [x] **Step 1: Write the failing test**

```python
import json
import unittest
from pathlib import Path
from tools.rimworld.capabilities import DOMAINS, PURPOSE, WORKFLOWS, overview
from tools.rimworld.core import canonical

ROOT = Path(__file__).resolve().parents[1]
EXCLUDED = {'load_game'}


class Coverage(unittest.TestCase):
    def test_every_permitted_catalog_tool_appears_in_a_domain(self):
        catalog = set(json.load(open(ROOT / 'api/catalog.json'))['tools'])
        covered = {name for names in DOMAINS.values() for name in names}
        self.assertEqual(catalog - EXCLUDED - covered, set())

    def test_domains_name_only_real_tools(self):
        catalog = set(json.load(open(ROOT / 'api/catalog.json'))['tools'])
        for domain, names in DOMAINS.items():
            for name in names:
                self.assertIn(name, catalog, domain + ' names a missing tool: ' + name)

    def test_every_domain_has_a_one_line_purpose(self):
        self.assertEqual(set(PURPOSE), set(DOMAINS))
        for text in PURPOSE.values():
            self.assertTrue(text and len(text) < 160)

    def test_overview_is_a_small_index_not_every_tool(self):
        value = overview(ROOT)
        self.assertLess(len(canonical(value).encode()), 2600)
        self.assertEqual(set(value['domains']), set(DOMAINS))
        self.assertEqual(value['domains']['trade']['tools'], len(DOMAINS['trade']))
        self.assertIn('purpose', value['domains']['trade'])
        self.assertNotIn('list_trade', canonical(value))

    def test_overview_full_returns_the_whole_map(self):
        value = overview(ROOT, full=True)
        self.assertIn('list_trade', canonical(value))
        self.assertIn('purpose', value['domains']['trade'][0])

    def test_one_domain_still_lists_its_tools(self):
        value = overview(ROOT, domain='trade')
        names = [row['tool'] for row in value['domains']['trade']]
        self.assertIn('order_pawn', names)
        self.assertIn('list_things', names)
        self.assertIn('list_unmanaged_items', names)
```

- [x] **Step 2: Run test to verify it fails**

Run: `python3 -m pytest tests/test_discovery.py -q`
Expected: FAIL. 59 tools are uncovered and `PURPOSE` does not exist.

- [x] **Step 3: Write minimal implementation**

Replace `DOMAINS` in `tools/rimworld/capabilities.py` with complete coverage and add purposes. A tool may appear in more than one domain where it genuinely serves both.

```python
DOMAINS = {
    'setup': ('main_menu','game_setup_status','select_scenario','select_storyteller','create_world',
              'choose_ideoligion','edit_ideoligion','edit_starting_pawn','find_world_tiles',
              'select_starting_site','start_game'),
    'colony': ('get_status','list_colonists','get_alerts','get_resources','get_conditions','get_research',
               'get_map','get_room','get_resource_readout','list_power_grids','list_unmanaged_items'),
    'pawns': ('get_pawn','order_pawn','draft','set_work_priority','set_schedule','set_allowed_area',
              'manage_gear','assign_building','rename_pawn','set_hostility_response','manage_prisoner'),
    'medical': ('get_pawn','list_surgeries','add_surgery','set_medical_care','order_pawn'),
    'food': ('get_resources','list_things','list_bills','add_bill','set_work_priority','order_pawn',
             'list_unmanaged_items','set_growing_zone','manage_food_policy','set_food_policy'),
    'combat': ('get_status','list_things','list_fires','get_area','draft','order_pawn','manage_gear',
               'set_hostility_response','list_mechs','set_mech_control'),
    'building': ('get_map','get_area','list_architect','build','inspect_thing','do_thing_action',
                 'manage_zone','designate','get_room','room_graph','list_power_grids'),
    'zones': ('manage_zone','list_zones','select_zone','delete_zone','rename_zone','set_growing_zone',
              'set_stockpile_filter','set_stockpile_priority','manage_area','set_allowed_area','designate'),
    'world': ('get_world','list_world_objects','get_world_tile','find_world_tiles','form_caravan',
              'caravan_action','world_object_action','world_target'),
    'quests': ('get_world','read_letter','get_quest','quest_action'),
    'trade': ('get_alerts','list_things','get_pawn','order_pawn','list_trade','set_trade','trade_action',
              'get_window_ui','window_action','list_unmanaged_items'),
    'production': ('inspect_thing','list_bills','list_recipes','add_bill','set_bill','delete_bill',
                   'get_resources','set_research','list_study_targets','set_study'),
    'animals': ('list_animals','list_wildlife','manage_animal','manage_zone'),
    'policies': ('list_policies','manage_food_policy','manage_apparel_policy','manage_drug_policy',
                 'set_food_policy','set_drug_policy','set_outfit','manage_area'),
    'inspection': ('inspect_thing','get_inspect_pane','get_info_card','list_windows','get_window_ui',
                   'get_room','room_graph','entity_codex','help','learning_helper','get_live_chat'),
    'culture': ('choose_ideoligion','edit_ideoligion','reform_ideoligion','set_ideo_role','get_royalty',
                'list_titles','manage_permits','use_permit','list_genes','create_xenogerm',
                'implant_xenogerm','get_anomaly'),
    'system': ('get_status','set_speed','wait_for_event','save_game','return_to_title','screenshot','say',
               'list_main_buttons'),
}

PURPOSE = {
    'setup': 'Create a world and colony from the main menu through the first landing.',
    'colony': 'Whole-colony state: status, colonists, alerts, stock, weather, research, rooms and power.',
    'pawns': 'One colonist: read them, order them, set work, schedule, area, gear and assignments.',
    'medical': 'Injury, illness, treatment priority and surgery.',
    'food': 'Ingredients, cooking bills, growing and the haulers who move it.',
    'combat': 'Threats, fires, drafting, positioning and gear for a fight.',
    'building': 'Place, inspect and operate structures; read the map and rooms around them.',
    'zones': 'Stockpiles, growing zones, allowed areas and designations.',
    'world': 'The planet map, other settlements and your caravans.',
    'quests': 'Letters, quests and their accept or decline actions.',
    'trade': 'Find a trader, open a deal, settle it and confirm the goods arrived.',
    'production': 'Work tables, bills, recipes and research.',
    'animals': 'Tame animals, wildlife and animal handling.',
    'policies': 'Food, drug, apparel and area policies applied to colonists.',
    'inspection': 'Read exactly what the player sees: inspect pane, info cards, open windows and help.',
    'culture': 'Ideoligion, royalty, genes, xenotypes and anomaly content.',
    'system': 'Game speed, supervised time, saving, screenshots and top-level UI.',
}
```

Rewrite `overview` to return an index by default:

```python
def overview(root, campaign=None, domain=None, workflow=None, full=False):
    """Compact affordance map: a domain index by default, never full schemas."""
    path=(campaign.path/'raw/catalog.json') if campaign else Path(root)/'api/catalog.json'
    catalog=read_json(path)
    from .facade import local, reserved
    merged=dict(catalog['tools']);reserved(catalog);merged.update(local())
    if domain is not None and domain not in DOMAINS: raise Error('Unknown capability domain: '+domain)
    if workflow is not None and workflow not in WORKFLOWS: raise Error('Unknown capability workflow: '+workflow)
    def one(name,note=None):
        if name not in merged:return None
        row={'tool':name,'purpose':merged[name].get('description','').split('. ')[0]}
        if note:row['note']=note
        return row
    if workflow is not None:
        steps=[one(name,note) for name,note in WORKFLOWS[workflow]]
        return {'workflow':workflow,'steps':[v for v in steps if v],
                'note':'Ordered affordance guide, not permission or proof that the current UI stage supports each step.'}
    if domain is not None:
        return {'domains':{domain:[v for v in (one(name) for name in DOMAINS[domain]) if v]},
                'purpose':PURPOSE[domain],
                'detail':'Fetch one exact schema with rw_capabilities {tool:NAME}.'}
    if full:
        return {'domains':{key:[v for v in (one(name) for name in values) if v] for key,values in DOMAINS.items()},
                'purposes':PURPOSE,'workflows':sorted(WORKFLOWS),
                'detail':'Fetch one exact schema with rw_capabilities {tool:NAME}.'}
    return {'domains':{key:{'tools':len(values),'purpose':PURPOSE[key]} for key,values in DOMAINS.items()},
            'workflows':sorted(WORKFLOWS),
            'detail':'rw_capabilities {domain:"NAME"} lists a domain, {workflow:"NAME"} gives an ordered guide, '
                     '{overview:true,full:true} lists every domain\'s tools, {tool:"NAME"} returns one exact schema.'}
```

In `tools/rimworld/facade.py`, extend the domain enum, accept `full`, and pass it through:

```python
CAPABILITY_DOMAINS=['setup','colony','pawns','medical','food','combat','building','zones','world','quests',
                    'trade','production','animals','policies','inspection','culture','system']
CAPABILITIES_SCHEMA=obj({'query':{'type':'string'},'tool':STRING,'overview':{'type':'boolean'},
                         'full':{'type':'boolean'},
                         'domain':{'enum':CAPABILITY_DOMAINS},'workflow':{'enum':CAPABILITY_WORKFLOWS}})
```

```python
    if args.get('overview') or args.get('domain') or args.get('workflow'):
        return overview(control.campaign.root,control.campaign,args.get('domain'),args.get('workflow'),
                        full=bool(args.get('full')))
```

Update the `rw_capabilities` description:

```python
  'Discover available actions without loading the catalog. overview gives a domain index; domain lists one area; '
  'overview with full:true lists every domain\'s tools. workflow gives an ordered '
  'new_game, medical_event, combat_event, caravan, food_crisis, trade or resume_crisis guide. query finds names; tool returns one exact schema/effect. '
  'Offline only; grants no permission.',
```

Keep `CAPABILITY_DOMAINS` and `capabilities.DOMAINS` in agreement with a test:

```python
    def test_facade_domain_enum_matches_the_capability_map(self):
        from tools.rimworld.facade import CAPABILITY_DOMAINS
        self.assertEqual(set(CAPABILITY_DOMAINS), set(DOMAINS))
```

- [x] **Step 4: Run tests**

Run: `python3 -m pytest tests/test_discovery.py -q && python3 -m pytest tests -q`
Expected: PASS. `tests/test_facade.py::test_capability_overview_and_workflow_preserve_affordances_without_schemas` asserts the old nested overview shape; update it to assert the index shape plus a `full:true` drill-down rather than reverting the change.

- [x] **Step 5: Commit**

```bash
git add tools/rimworld/capabilities.py tools/rimworld/facade.py tests/test_discovery.py tests/test_facade.py
git commit -m "Cover the whole catalog with a small domain index"
```

---

### Task 7: Workflows carry the step that was actually missed

**Files:**
- Modify: `tools/rimworld/capabilities.py` (`WORKFLOWS`)
- Test: `tests/test_discovery.py`

**Interfaces:**
- Consumes: Task 6's `overview` step builder, which already reads `(name, note)` pairs.
- Produces: `WORKFLOWS: dict[str, tuple[tuple[str, str], ...]]`, gaining `build_structure`.
- Also modify `tools/rimworld/facade.py`: add `build_structure` to `CAPABILITY_WORKFLOWS` and name it in the `rw_capabilities` description. A test must assert `set(CAPABILITY_WORKFLOWS) == set(WORKFLOWS)`.

- [x] **Step 1: Write the failing test**

```python
    def test_trade_workflow_starts_at_finding_the_trader_and_ends_at_confirming_goods(self):
        steps = overview(ROOT, workflow='trade')['steps']
        names = [row['tool'] for row in steps]
        self.assertEqual(names[0], 'get_alerts')
        self.assertLess(names.index('list_things'), names.index('list_trade'))
        self.assertLess(names.index('order_pawn'), names.index('list_trade'))
        self.assertEqual(names[-1], 'list_unmanaged_items')
        notes = ' '.join(row.get('note', '') for row in steps).lower()
        self.assertIn('map pawns', notes)
        self.assertIn('ground', notes)
        self.assertIn('do not batch', notes)

    def test_food_crisis_reaches_bills_before_concluding_there_is_no_food(self):
        steps = overview(ROOT, workflow='food_crisis')['steps']
        names = [row['tool'] for row in steps]
        self.assertLess(names.index('list_bills'), names.index('get_resources'))
        notes = {row['tool']: row.get('note', '') for row in steps}
        self.assertIn('suspended', notes['list_bills'].lower())
        self.assertIn('unmanaged', ' '.join(names).lower() + ' ' + str(names))

    def test_building_workflow_teaches_the_interaction_spot_rule(self):
        steps = overview(ROOT, workflow='build_structure')['steps']
        notes = {row['tool']: row.get('note', '') for row in steps}
        self.assertIn('interactionCell', notes['build'])
        self.assertIn('rot', notes['build'])

    def test_the_facade_workflow_enum_matches_the_capability_map(self):
        from tools.rimworld.facade import CAPABILITY_WORKFLOWS
        self.assertEqual(set(CAPABILITY_WORKFLOWS), set(WORKFLOWS))

    def test_every_workflow_step_is_a_name_and_note_pair(self):
        for name, steps in WORKFLOWS.items():
            for entry in steps:
                self.assertEqual(len(entry), 2, name)
                self.assertIsInstance(entry[0], str)
                self.assertIsInstance(entry[1], str)
                self.assertTrue(entry[1], name + ':' + entry[0])
```

- [x] **Step 2: Run test to verify it fails**

Run: `python3 -m pytest tests/test_discovery.py -q -k workflow`
Expected: FAIL. Workflow entries are bare strings.

- [x] **Step 3: Write minimal implementation**

```python
WORKFLOWS = {
    'new_game': (
        ('main_menu','Only valid at the entry screen.'),
        ('game_setup_status','Ask where you are and what the next legal step is; re-read it between stages.'),
        ('select_scenario','Pick by name.'),
        ('select_storyteller','Storyteller, difficulty and reload mode together.'),
        ('create_world','Asynchronous; poll game_setup_status until the starting-site stage.'),
        ('choose_ideoligion','Ideology only.'),
        ('edit_ideoligion','Ideology only.'),
        ('select_starting_site','Pick the landing tile.'),
        ('edit_starting_pawn','Fix starting colonists before the game begins; it is not editable afterward.'),
        ('start_game','Commits the setup.'),
        ('get_status','Confirm a colony is actually loaded before any colony read.'),
        ('get_map','Establish home coordinates once.'),
    ),
    'medical_event': (
        ('get_status','Danger and colonist state first.'),
        ('get_pawn','tab=health for hediffs, bleeding rate, immunity race and capacities.'),
        ('set_medical_care','Medicine quality is a policy, not an order.'),
        ('order_pawn','Rescue, tend or prioritize a doctor; a receipt is not treatment.'),
        ('list_surgeries','Only what this pawn can actually receive.'),
        ('add_surgery','Queues an operation; it still needs a surgeon, medicine and time.'),
    ),
    'combat_event': (
        ('get_status','Danger rating and who is down.'),
        ('list_things','category=pawn faction=hostile for the actual attackers.'),
        ('list_fires','Fires spread and are often the larger loss.'),
        ('get_area','Bounded terrain and cover around the fight only.'),
        ('draft','Drafted colonists shoot at hostiles automatically, including a berserk colonist. Do not draft an armed pawn next to one you want alive.'),
        ('order_pawn','Move, attack or carry a downed pawn to a bed.'),
        ('rw_wait','Short horizons during a fight; the event packet returns who changed.'),
    ),
    'caravan': (
        ('list_world_objects','kind=caravans or kind=settlements; an unfiltered call trips the size guard.'),
        ('form_caravan','mode=status is the read form and is how departure is verified.'),
        ('caravan_action','Move, rest or split an existing caravan.'),
        ('get_world_tile','Terrain and travel cost for the next leg.'),
        ('world_object_action','Interact with what the caravan reached.'),
    ),
    'food_crisis': (
        ('get_status','Confirm the alert and the colonist count it applies to.'),
        ('list_bills','Do this before concluding there are no ingredients: a suspended cooking bill looks exactly like an empty larder, and the Low Food alert never mentions bills.'),
        ('get_resources','Stockpiled counts only. It does not see loose or forbidden food.'),
        ('list_unmanaged_items','Forbidden and unhauled food a human would see lying on the floor.'),
        ('list_things','category=item with a defName to locate a specific food on the map.'),
        ('add_bill','Add or unsuspend the meal bill once ingredients are confirmed.'),
        ('set_work_priority','A cook who will never cook is the other common cause.'),
        ('order_pawn','Prioritize the cook or a hauler directly.'),
    ),
    'trade': (
        ('get_alerts','A trade letter names an approaching trader and expires; read it before it is dismissed.'),
        ('list_things','Find the trader with category=pawn faction=neutral. Visiting traders are map pawns, not list_world_objects caravans, and that world list can be legitimately empty while the trader stands on your map.'),
        ('get_pawn','tab=health on the intended negotiator. Social incapability blocks the deal outright and a damaged talking capacity silently worsens prices.'),
        ('order_pawn','Execute "Trade with …" on the trader. The colonist walks there first, so the dialog is not open yet.'),
        ('list_trade','Poll until active is true. returned below tradeableCount means rows were withheld.'),
        ('set_trade','One row per call. Do not batch these: every receipt carries the open-dialog review flag.'),
        ('trade_action','accept commits the deal and may leave the dialog plus a message box open.'),
        ('window_action','Dismiss a blocking message box before trade_action cancel.'),
        ('list_unmanaged_items','Bought goods drop at the trader\'s feet, so get_resources still reads pre-trade until a hauler moves them. This is how you confirm the deal delivered.'),
    ),
    'build_structure': (
        ('list_architect','Find the exact defName and footprint before guessing a cell.'),
        ('get_area','Bounded terrain and existing buildings where you intend to place it.'),
        ('build','A refusal carries placement.interactionCell and a reason. A cell can be empty and still be refused because the new building\'s interaction spot overlaps a research bench, shelf or another interaction spot. Read interactionCell, then try rot 0 through 3 before moving the cell: rotation moves the offset.'),
        ('inspect_thing','The inspect pane is where fuel, power and toggles live; a list_things row does not carry them.'),
        ('order_pawn','Prioritize a builder at the blueprint. If the reply says the pawn is already working on it, the intent is already met.'),
    ),
    'resume_crisis': (
        ('get_status','Identity, pause and danger before anything else.'),
        ('rw_observe','One decision packet instead of a read-per-fact rebuild.'),
        ('read_letter','The letter text is the only place the actual event is spelled out.'),
        ('get_pawn','Only the facets the next decision needs.'),
        ('list_things','Bounded and anchored; never the whole map.'),
        ('draft','Only once the target is chosen.'),
        ('order_pawn','Immediate order first, then queue=true for reviewed follow-up jobs.'),
        ('rw_wait','The longest horizon the current evidence justifies.'),
    ),
}
```

- [x] **Step 4: Run tests**

Run: `python3 -m pytest tests/test_discovery.py -q && python3 -m pytest tests -q`
Expected: PASS

- [x] **Step 5: Commit**

```bash
git add tools/rimworld/capabilities.py tests/test_discovery.py
git commit -m "Give workflows the preconditions and confirmations play actually needed"
```

---

### Task 8: The command line reaches what the MCP surface reaches

**Files:**
- Modify: `tools/rimworld/cli.py` (`parser`, `run`, `main`, new `Parser`, `FLAG_HELP`, `pointer_examples`)
- Test: `tests/test_friction_batch.py`

**Interfaces:**
- Consumes: Task 6's `overview` signature.
- Produces: `./rw capabilities --overview [--full] | --domain NAME | --workflow NAME`. `cli.pointer_examples(value, limit=8) -> list[str]`. Argument errors print one JSON object instead of a usage dump.

- [x] **Step 1: Write the failing test**

```python
import io
import json
import unittest
from contextlib import redirect_stdout
from tools.rimworld.cli import main, pointer_examples


class CommandLine(unittest.TestCase):
    def run_cli(self, *argv):
        out = io.StringIO()
        with redirect_stdout(out):
            code = main(list(argv))
        return code, json.loads(out.getvalue())

    def test_capabilities_overview_is_reachable_offline(self):
        code, value = self.run_cli('capabilities', '--overview')
        self.assertEqual(code, 0)
        self.assertIn('trade', value['domains'])
        self.assertEqual(set(value['domains']['trade']), {'tools', 'purpose'})

    def test_capabilities_domain_and_workflow_are_reachable_offline(self):
        code, value = self.run_cli('capabilities', '--domain', 'trade')
        self.assertEqual(code, 0)
        self.assertIn('order_pawn', [r['tool'] for r in value['domains']['trade']])
        code, value = self.run_cli('capabilities', '--workflow', 'food_crisis')
        self.assertEqual(code, 0)
        self.assertEqual(value['workflow'], 'food_crisis')

    def test_capabilities_overview_full_lists_tools(self):
        code, value = self.run_cli('capabilities', '--overview', '--full')
        self.assertEqual(code, 0)
        self.assertIn('list_trade', json.dumps(value))

    def test_a_wrong_flag_returns_json_naming_the_right_one(self):
        code, value = self.run_cli('--run', 'x', 'observe', '--args', '{}', '--token', 't')
        self.assertEqual(code, 2)
        self.assertFalse(value['ok'])
        self.assertIn('--json', value['use'])
        self.assertIn('--args', value['use'])
        self.assertIs(value['game_contact'], False)

    def test_retrieve_says_it_takes_no_token(self):
        code, value = self.run_cli('--run', 'x', 'retrieve', '--token', 't')
        self.assertEqual(code, 2)
        self.assertIn('no --token', value['use'])

    def test_pointer_examples_come_from_the_actual_response(self):
        body = {'id': 'obs-1', 'data': {'mood': 42, 'needs': [{'label': 'Food', 'level': 0.2}]}}
        found = pointer_examples(body)
        self.assertIn('/data/mood', found)
        self.assertIn('/data/needs', found)
        self.assertNotIn('/needs', found)
```

Add one test to `tests/test_friction_batch.py` for the selector error body, since it needs a real campaign:

```python
    def test_a_failed_selector_suggests_pointers_from_the_response(self):
        import io, json as js
        from contextlib import redirect_stdout
        from tools.rimworld.cli import main
        out = io.StringIO()
        with redirect_stdout(out):
            code = main(['--root', str(self.root), '--run', self.camp.name,
                         'retrieve', '--observation', self.bound_observation, '--select', '/needs'])
        value = js.loads(out.getvalue())
        self.assertEqual(code, 2)
        self.assertTrue(value['operation_completed'])
        self.assertTrue(value['available_pointers'])
        self.assertIn('Do not replay', value['replay'])
```

The implementer should set `self.bound_observation` in `setUp` from the status observation the fixture already binds, and add `--select` to the `retrieve` subparser in the same task so the test can run it.

- [x] **Step 2: Run test to verify it fails**

Run: `python3 -m pytest tests/test_friction_batch.py -q -k "cli or capabilities or flag or pointer or selector"`
Expected: FAIL with `ImportError: cannot import name 'pointer_examples'` and `SystemExit` from argparse.

- [x] **Step 3: Write minimal implementation**

In `tools/rimworld/cli.py`, add above `parser()`:

```python
FLAG_HELP={
 'observe':'observe takes --json JSON or --file FILE (not --args). Only call takes --args.',
 'guard':'guard takes --json JSON or --file FILE (not --args). Only call takes --args.',
 'call':'call takes TOOL --args JSON --token TOKEN. observe and guard take --json.',
 'retrieve':'retrieve reads local evidence and takes no --token. Use --observation OBS, or --tool/--entity.',
 'capabilities':'capabilities is offline: a bare query, or --tool NAME, --overview [--full], --domain NAME, --workflow NAME.',
 'spatial':'spatial selects inside a saved observation: --observation OBS with --rect or --ids.',
 'act':'act takes --json JSON --token TOKEN.',
}


class Parser(argparse.ArgumentParser):
    """One JSON object per failure, matching every other result on this surface."""
    def error(self, message):
        name=getattr(self,'rw_command',None)
        body={'ok':False,'error':message,'game_contact':False}
        if name:body['command']=name
        if name in FLAG_HELP:body['use']=FLAG_HELP[name]
        print(json.dumps(body,ensure_ascii=False),flush=True)
        raise SystemExit(2)


def pointer_examples(value, limit=8):
    """Real JSON Pointers into the response the caller just received."""
    found=[]
    def visit(node,path,depth):
        if len(found)>=limit or depth>2:return
        if isinstance(node,dict):
            for key,child in node.items():
                pointer=path+'/'+str(key).replace('~','~0').replace('/','~1')
                found.append(pointer)
                if isinstance(child,(dict,list)):visit(child,pointer,depth+1)
        elif isinstance(node,list) and node:
            visit(node[0],path+'/0',depth+1)
    visit(value,'',0)
    return found[:limit]
```

In `parser()`, use the class for the root and every subparser, and tag each one:

```python
def parser():
    p = Parser(description="RimWorld evidence, control, memory and history support.")
    ...
    sub = p.add_subparsers(dest="command", required=True, parser_class=Parser)
```

At the end of `parser()`, before `return p`, tag each subparser so `error` can name it:

```python
    for name,child in sub.choices.items():
        child.rw_command=name
    return p
```

Extend the `capabilities` subparser and add `--select` to `retrieve`:

```python
    q = sub.add_parser("capabilities", help="Offline API discovery; run optional, no game contact.")
    q.add_argument("query", nargs="?", default=""); q.add_argument("--tool")
    q.add_argument("--overview", action="store_true")
    q.add_argument("--full", action="store_true")
    q.add_argument("--domain"); q.add_argument("--workflow")
```

```python
    q = sub.add_parser("retrieve", help="Read full saved evidence selectively.")
    q.add_argument("--tool"); q.add_argument("--entity"); q.add_argument("--observation")
    q.add_argument('--select',action='append',help='Return one or more JSON Pointer paths from the completed response.')
```

In `run()`, route the new capability flags:

```python
    if args.command == "capabilities":
        from .capabilities import discover, overview
        campaign=Campaign(args.root,args.campaign) if args.campaign else None
        if args.overview or args.domain or args.workflow:
            return overview(args.root,campaign,args.domain,args.workflow,full=args.full)
        return discover(args.root,args.query,args.tool,campaign)
```

In `main()`, add the pointer suggestions to the selection-error body:

```python
                display={'ok':False,'phase':'local_selection','operation_completed':True,
                         'error':selection_error,'evidence':evidence_ids(result),
                         'available_top_level':list(result) if isinstance(result,dict) else None,
                         'available_pointers':pointer_examples(result if isinstance(result,dict) else {}),
                         'replay':'Do not replay the completed game operation; correct only the local selector.'}
```

- [x] **Step 4: Run tests**

Run: `python3 -m pytest tests/test_friction_batch.py -q && python3 -m pytest tests -q`
Expected: PASS. If any existing test asserts argparse's usage text on stderr, update it to the JSON body.

Also confirm by hand that nothing regressed at the shell:

```bash
./rw capabilities --overview && ./rw capabilities --workflow trade && ./rw --run continuance retrieve --token t
```

- [x] **Step 5: Commit**

```bash
git add tools/rimworld/cli.py tests/test_friction_batch.py
git commit -m "Reach discovery from the command line and fail with usable JSON"
```

---

### Task 9: Documentation and project records

**Files:**
- Modify: `docs/facade.md`, `docs/composition.md`, `AGENTS.md`, `PLAN.md`, `VALIDATION.md`, `TODO.md`, `docs/friction.md`
- Test: `tests/test_friction_batch.py`

**Interfaces:**
- Consumes: every earlier task.
- Produces: no code interface. One documentation test guards the facts a player must not have to rediscover.

- [x] **Step 1: Write the failing test**

```python
    def test_the_operational_guide_names_the_facts_play_had_to_rediscover(self):
        from pathlib import Path
        text = Path(__file__).resolve().parents[1].joinpath('docs/facade.md').read_text()
        for phrase in ('confirm:true', 'never run two', 'seen_structure', 'context:"brief"',
                       'degraded', 'list_unmanaged_items'):
            self.assertIn(phrase, text, 'facade.md must document ' + phrase)

    def test_the_cli_flag_sets_are_written_down_once(self):
        from pathlib import Path
        text = Path(__file__).resolve().parents[1].joinpath('docs/facade.md').read_text()
        for phrase in ('call --args', 'observe --json', 'retrieve'):
            self.assertIn(phrase, text)
```

- [x] **Step 2: Run test to verify it fails**

Run: `python3 -m pytest tests/test_friction_batch.py -q -k "guide or flag_sets"`
Expected: FAIL on the first missing phrase.

- [x] **Step 3: Write the documentation**

In `docs/facade.md`, add these sections and edits.

Under "Fast decision-loop guidance", add a command-line cheat sheet:

```markdown
### One-shot CLI flag sets

Three commands, three argument shapes. Getting this wrong costs a turn before any game decision is made.

| Command | Arguments |
|---|---|
| `./rw --run NAME call TOOL --args JSON --token TOKEN` | `--args` |
| `./rw --run NAME observe --json JSON --token TOKEN` | `--json` or `--file`, never `--args` |
| `./rw --run NAME guard --json JSON --token TOKEN` | `--json` or `--file` |
| `./rw --run NAME retrieve --observation OBS` | local evidence, no `--token` |
| `./rw capabilities --overview` | offline, no run and no token needed |

Never run two `./rw` processes at once. Every controller entry point takes one exclusive `operation.lock`, so two reads issued together fail rather than run in parallel. Batch inside `rw_observe` or `rw_act actions` instead.
```

Add a new section after "Selection and limits":

```markdown
## When a read is too large

The game itself refuses a response over roughly 25,000 characters and answers with a guard instead of the data. The query never ran. Two exits are sanctioned and the response names both:

- **Narrow it.** `retry.narrow_with` lists the filters that tool accepts at the source. `list_world_objects` takes `kind`; `list_things` takes category, defName, faction and an anchor with a radius. Narrowing is almost always the right answer.
- **Confirm it.** `confirm:true` on `list_things`, `list_world_objects`, `list_unmanaged_items`, `get_area`, `get_map`, `get_world`, `room_graph` and `find_world_tiles` accepts the full result deliberately. Delivery is still bounded by the payload budget, and `rw_retrieve {observation, view:"full"}` then returns everything locally without another game call.

A guard like this no longer stops a composition. The affected section is marked `degraded` with its retry advice, every other query still runs, and the response lists degraded keys separately from `stopped`. A genuine problem, meaning unconfirmed pause, identity mismatch, unparseable JSON, an upstream error, or missing and malformed fields, still stops everything after it and says so.
```

Add to "Decision observations and reuse":

```markdown
The `world` topic reads `list_world_objects` with `kind` defaulting to `caravans`; pass `world_kind` to choose another. The `visitors` topic reads neutral pawns on the current map, which is where a visiting trade caravan actually is. A world caravan list can be legitimately empty while the trader stands in your base.
```

Add to the wait section:

```markdown
`context:"brief"` keeps the post-wait status packet and skips the pawn facet, responder, threat-row and letter sweep. Use it for a routine wait during a long-running situation you already understand, and `context:"auto"` when the event is new. Event topics are chosen from the event narrative itself, not from a standing threat flag, so a berserk colonist does not re-trigger a full sweep on every later wait.
```

Add to "Views":

```markdown
`seen_structure` on a raw retrieved record is the union of every field path that tool has ever returned in this run. It is not a claim about this capture. Read the current `data` for the live fact; a flag listed there and absent from `data` is history, not a present threat.
```

In `docs/composition.md`, add after the preset table:

```markdown
A section whose only problem is an upstream size guard or truncation is marked `degraded` with its retry advice and the remaining queries still run. `degraded` lists those keys; `stopped` still means everything after it was abandoned for review.
```

In `AGENTS.md`, in the "Ordinary play" paragraph about one-shot CLI, add one sentence:

Never run two `./rw` processes concurrently; the controller holds one exclusive lock and a second process fails rather than parallelizing.

In `PLAN.md`, replace the Status paragraph with the new scope and point at this plan. In `VALIDATION.md`, record the measured before-and-after numbers from the recorded session and the new test count. In `TODO.md`, add a checked "Live friction batch two" list mirroring these tasks, and an unchecked line: "Confirm during the next live run whether a `set_trade` batch can safely continue on an unchanged trade dialog, and whether `trade_action cancel` after a committed deal can reverse it. Both are currently unverified." In `docs/friction.md`, add a short status block at the top naming this plan and listing the two items deliberately left for the playtest.

- [x] **Step 4: Run the full suite and a manual smoke check**

Run: `python3 -m pytest tests -q`
Expected: PASS

```bash
./rw capabilities --overview | wc -c
./rw capabilities --workflow trade
```

- [x] **Step 5: Commit**

```bash
git add docs AGENTS.md PLAN.md VALIDATION.md TODO.md tests/test_friction_batch.py
git commit -m "Document the recovery paths, flag sets and lock rule play had to rediscover"
```

---

## Deliberately not in scope

- Raising the 32768-byte payload budget, the 32-query composition cap or the 16-action batch cap. None fired in 304 recorded calls.
- Extending the same-dialog batch exception to `set_trade`. Whether the game tolerates it is unverified; the trade workflow now says not to batch them, and the playtest settles it.
- Any claim about whether `trade_action cancel` can reverse a committed deal.
- Generic non-trade window shaping. The 22 KB window dumps in the log predate the trade shaping that already landed; the one non-trade window read afterwards cost 1,939 bytes.
- The slave medical bed question, which needs an inspect-before-and-after on a live bed.
