#!/usr/bin/env python3
"""Offline local persistence/output benchmark. Creates only temporary synthetic campaigns."""
import argparse
import json
from pathlib import Path
import statistics
import sys
import tempfile
import time
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from tools.rimworld import __version__
from tools.rimworld.core import digest
from tools.rimworld.presentation import present
from tools.rimworld.memory import Campaign, init_campaign


def run(count, scopes=1):
    with tempfile.TemporaryDirectory(prefix='rimworld-benchmark-') as temp:
        root = Path(temp)
        init_campaign(root, 'synthetic', {'mode': 'fresh', 'objective': 'Offline benchmark', 'rules': 'No game access', 'setup': {}})
        c = Campaign(root, 'synthetic')
        durations = []
        for tick in range(count):
            started = time.perf_counter()
            if scopes == 1:
                c.ingest('get_status', {}, {'loaded': False, 'ticksGame': tick}, origin='fixture')
            else:
                x=tick % scopes
                c.ingest('get_area', {'minX':x,'maxX':x,'minZ':0,'maxZ':0},
                         {'things':[{'id':'item'+str(i),'def':'Steel','x':x,'z':i} for i in range(40)],'terrainSummary':{'Soil':1}},origin='fixture')
            durations.append((time.perf_counter()-started)*1000)
        projection_bytes = (c.path / '.projection.json').stat().st_size
        index_bytes=(c.path/'reference/facts.sqlite').stat().st_size
        scope_count=len(c.state()['facts'])
        long_status = {'loaded': True, 'ticksGame': count, 'maps': [{'mapIndex': 0}],
                       'bundled': {'get_alerts': {'activeAlerts': []},
                                   'list_colonists': {'colonists': [{'id': 'fixture-'+str(i), 'job': 'ordinary synthetic work',
                                                                  'health': 100, 'x': i, 'z': 0} for i in range(100)]}}}
        first = c.ingest('get_status', {}, long_status, origin='fixture')
        second = c.ingest('get_status', {}, long_status, origin='fixture')
        started = time.perf_counter(); retrieved = c.observation(first['id']); lookup_ms = (time.perf_counter()-started)*1000
        return {'version': __version__, 'origin': 'offline synthetic fixtures', 'observations': count,
                'first_ingest_ms': durations[0], 'initial_50_median_ms': statistics.median(durations[:50]),
                'final_50_median_ms': statistics.median(durations[-50:]), 'projection_bytes': projection_bytes, 'facts_index_bytes':index_bytes,'distinct_query_scopes':scope_count,
                'first_status_output_bytes': len(json.dumps(present(first)).encode()),
                'unchanged_status_output_bytes': len(json.dumps(present(second)).encode()),
                'indexed_lookup_ms': lookup_ms, 'retrieved_original_tick': retrieved['tick'],
                'measurement_scope': 'Local normalized ingestion/projection and JSON output only. No MCP, model, live-game time, danger recall or win-rate measurement.',
                'runtime_source_digest': digest({str(p.relative_to(Path(__file__).resolve().parents[1])): p.read_text()
                    for p in sorted((Path(__file__).resolve().parent/'rimworld').glob('*.py'))})}


if __name__ == '__main__':
    p=argparse.ArgumentParser();p.add_argument('--observations',type=int,default=5000)
    p.add_argument('--output',type=Path);p.add_argument('--scopes',type=int,default=1);a=p.parse_args()
    if a.observations < 50: p.error('Use at least 50 observations for the reported windows.')
    if a.output and a.output.exists(): p.error('Use a new output file; preserve prior evidence.')
    if not 1 <= a.scopes <= a.observations: p.error('scopes must be between 1 and observation count.')
    value=run(a.observations,a.scopes)
    if a.output: a.output.write_text(json.dumps(value,indent=2)+'\n')
    print(json.dumps(value,indent=2))
