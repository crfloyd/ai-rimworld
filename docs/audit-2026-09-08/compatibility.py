import json,sys
from pathlib import Path
sys.path.insert(0,'/Users/corey/git/ai-rimworld')
from tools.rimworld.mcp import validate
from tools.rimworld.observations import normalize,delta_view
source=Path('/tmp/rimmolt-playthrough')
catalog=json.loads((source/'tools.json').read_text())
schema=next(t['inputSchema'] for t in catalog['result']['tools'] if t['name']=='list_things')
results={}
for category in ['Pawn','pawn']:
 try: validate(schema,{'category':category,'mapIndex':0});results[category]='valid'
 except Exception as e:results[category]=str(e)
for line in (source/'history.jsonl').open():
 row=json.loads(line)
 if row.get('tool')=='get_pawn' and row.get('args',{}).get('tab')=='health':
  data=json.loads(row['result']) if isinstance(row['result'],str) else row['result']
  obs=normalize('get_pawn',row['args'],data,'audit','recorded',origin='recorded')
  results['medical']={'raw_json_bytes':len(json.dumps(data).encode()),'unchanged_delta_json_bytes':len(json.dumps(delta_view(obs,obs)).encode())}
  break
print(json.dumps(results,indent=2))
Path('/tmp/ai-rimworld-audit-20260908/compatibility-results.json').write_text(json.dumps(results,indent=2))
