import sys,json,time,statistics,tempfile,copy
from pathlib import Path
ROOT=Path('/Users/corey/git/ai-rimworld')
sys.path[:0]=[str(ROOT),str(ROOT/'tests')]
from tools.rimworld.core import atomic_json
from tools.rimworld.memory import Campaign,init_campaign
from tools.rimworld.safety import deadlines
from tools.rimworld.monitor import coverage
from tools.rimworld.observations import normalize
from test_monitor import ScenarioSetup
results={}
f=ScenarioSetup();f.setUp()
try:
 spec=copy.deepcopy(f.spec);spec['queries'][-1]['args']['category']='pawn'
 obs=[]
 for q,data in zip(spec['queries'],f.safe_reads()):
  r=f.camp.ingest(q['tool'],q.get('args',{}),data,origin='live')
  obs += [f.camp.observation(r['id'])]+[f.camp.observation(b['id']) for b in r.get('bundle',[])]
 results['lowercase_coverage']=coverage(f.camp,obs,spec)
 issue=f.camp.issue({'title':'review now','rationale':'review deadline due','next_action':'inspect','revisit':'at tick 300000','resolution':'review done','deadline':{'kind':'review','tick':300000,'reason':'due'}})
 results['review_deadline']=deadlines(f.camp)
 a=f.camp.action('order_pawn',{'id':'p'},'Move','movement')
 idx=f.camp.path/'reference/action-index'/ (a['id']+'.json')
 idx.unlink();f.camp.rebuild();results['action_index_after_rebuild']=f.camp.action_record(a['id'])
finally:f.tearDown()
for mode in ['repeated','unique']:
 with tempfile.TemporaryDirectory(prefix='rw-audit-') as tmp:
  root=Path(tmp);init_campaign(root,'probe',{'mode':'fresh','objective':'Offline audit only','rules':'no game','setup':{},'learning':{'shared_baseline':'none'}});c=Campaign(root,'probe');dur=[]
  for i in range(250):
   args={'minX':i if mode=='unique' else 0,'maxX':i if mode=='unique' else 0,'minZ':0,'maxZ':0}
   data={'things':[{'id':'item'+str(j),'def':'Steel','x':i,'z':j} for j in range(40)],'terrainSummary':{'Soil':1}}
   start=time.perf_counter();c.ingest('get_area',args,data,origin='fixture');dur.append((time.perf_counter()-start)*1000)
  results[mode]={'first25_ms':statistics.median(dur[:25]),'last25_ms':statistics.median(dur[-25:]),'projection_bytes':(c.path/'.projection.json').stat().st_size,'scope_count':len(c.state()['facts'])}
print(json.dumps(results,indent=2))
Path('/tmp/ai-rimworld-audit-20260908/probe-results.json').write_text(json.dumps(results,indent=2))
