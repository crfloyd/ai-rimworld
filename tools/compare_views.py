#!/usr/bin/env python3
"""Offline base-MCP versus runner views from recorded lab calls; never contacts a game."""
import argparse
import json
from pathlib import Path
import sys
import tempfile
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from tools.rimworld.memory import Campaign, init_campaign
from tools.rimworld.observations import decode
from tools.rimworld.presentation import present
from tools.rimworld.core import canonical


def compare(records):
    rows=[]
    with tempfile.TemporaryDirectory(prefix='rw-view-comparison-') as temp:
        root=Path(temp)
        init_campaign(root,'recorded',{'mode':'resume','objective':'Offline response comparison','rules':'No game access','setup':{},'learning':{'shared_baseline':'none'}})
        c=Campaign(root,'recorded')
        for record in records:
            payload=record['response'];data,_=decode(payload);data.pop('_mcpText',None)
            view=c.ingest(record['tool'],record.get('args',{}),payload,origin='recorded')
            raw_bytes=len(canonical(data).encode());view_bytes=len(canonical(present(view)).encode())
            rows.append({'tool':record['tool'],'args':record.get('args',{}),'base_decoded_bytes':raw_bytes,
                         'runner_view_bytes':view_bytes,'ratio':round(view_bytes/max(1,raw_bytes),3),
                         'unchanged':view.get('unchanged',False),'evidence':view['id']})
    return {'scope':'Offline formatted ingestion views, excluding controller safety IDs; bytes are not model tokens or a decision-quality score.',
            'rows':rows,'total_base_bytes':sum(r['base_decoded_bytes'] for r in rows),'total_view_bytes':sum(r['runner_view_bytes'] for r in rows)}


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('records',type=Path);parser.add_argument('--output',type=Path)
    args=parser.parse_args();result=compare([json.loads(l) for l in args.records.read_text().splitlines() if l.strip()])
    text=json.dumps(result,indent=2)+'\n'
    if args.output:
        with args.output.open('x') as f:f.write(text)
    print(text)
