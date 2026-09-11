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
from tools.rimworld import facade


def compare(records, facade_view=False):
    rows=[]
    memo=facade.Memo() if facade_view else None
    with tempfile.TemporaryDirectory(prefix='rw-view-comparison-') as temp:
        root=Path(temp)
        init_campaign(root,'recorded',{'mode':'resume','objective':'Offline response comparison','rules':'No game access','setup':{},'learning':{'shared_baseline':'none'}})
        c=Campaign(root,'recorded')
        for record in records:
            payload=record['response'];data,_=decode(payload);data.pop('_mcpText',None)
            view=c.ingest(record['tool'],record.get('args',{}),payload,origin='recorded')
            raw_bytes=len(canonical(data).encode());view_bytes=len(canonical(present(view)).encode())
            row={'tool':record['tool'],'args':record.get('args',{}),'base_decoded_bytes':raw_bytes,
                 'runner_view_bytes':view_bytes,'ratio':round(view_bytes/max(1,raw_bytes),3),
                 'unchanged':view.get('unchanged',False),'evidence':view['id']}
            if facade_view:
                obs=c.observation(view['id'])
                body=present(view)
                body,_minted=memo.substitute(body,obs)
                body=facade.budget(body,obs,record['tool'])
                row['facade_view_bytes']=len(canonical(body).encode())
                row['facade_ratio']=round(row['facade_view_bytes']/max(1,raw_bytes),3)
            rows.append(row)
    result={'scope':'Offline formatted ingestion views, excluding controller safety IDs; bytes are not model tokens or a decision-quality score.',
            'rows':rows,'total_base_bytes':sum(r['base_decoded_bytes'] for r in rows),'total_view_bytes':sum(r['runner_view_bytes'] for r in rows)}
    if facade_view:
        result['total_facade_bytes']=sum(r['facade_view_bytes'] for r in rows)
        result['by_tool']=by_tool(rows)
    return result


def by_tool(rows):
    totals={}
    for r in rows:
        t=totals.setdefault(r['tool'],{'calls':0,'base':0,'runner':0,'facade':0})
        t['calls']+=1;t['base']+=r['base_decoded_bytes'];t['runner']+=r['runner_view_bytes']
        t['facade']+=r.get('facade_view_bytes',r['runner_view_bytes'])
    for t in totals.values():
        t['facade_vs_runner']=round(t['facade']/max(1,t['runner']),3)
    return dict(sorted(totals.items(),key=lambda kv:-kv[1]['runner']))


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('records',type=Path);parser.add_argument('--output',type=Path)
    parser.add_argument('--facade',action='store_true',help='Also measure the facade envelope (references, budget).')
    args=parser.parse_args();result=compare([json.loads(l) for l in args.records.read_text().splitlines() if l.strip()],args.facade)
    text=json.dumps(result,indent=2)+'\n'
    if args.output:
        with args.output.open('x') as f:f.write(text)
    print(text)
