import json,sys,hashlib,collections
from pathlib import Path
import argparse
parser=argparse.ArgumentParser(description='Offline synthetic runner coverage probes; no game calls.')
parser.add_argument('--root', type=Path, required=True)
parser.add_argument('--output', type=Path, required=True)
options=parser.parse_args()
root=options.root.resolve()
sys.path.insert(0,str(root/'tools'))
from rimworld.control import effect
from rimworld.observations import normalize,compact
from rimworld.presentation import present
from rimworld.safety import signals
cat=json.loads((root/'campaigns/continuance/raw/catalog.json').read_text())
def probe(tool,args,data):
 o=normalize(tool,args,data,'review','offline',origin='fixture')
 return {'input':data,'completeness':o['completeness'],'coverage':o['coverage'],'risks':signals(o),'agent_view':present(compact(o))}
results={'basis':'Offline synthetic probes of installed 0.3.1; no game calls. Invented fields test information handling, not claimed RimMolt fields.',
 'valid_summary_shape':probe('list_things',{'summary':True}, {'loaded':True,'mapIndex':0,'matched':0,'mode':'summary','groups':[]}),
 'novel_unmodeled':probe('get_anomaly',{}, {'novelHazard':{'danger':True}}),
 'novel_area_field':probe('get_area',{}, {'things':[],'terrainSummary':{},'novelHazard':{'danger':True}}),
 'novel_thing_field':probe('list_things',{}, {'things':[{'def':'Example','id':'example','novelHazard':True}]}),
 'new_delta_field':probe('get_status',{}, {'loaded':False,'_delta':{'novelHazard':True}}),
 'classification':{n:effect(n,{}) for n in sorted(cat['tools'])}}
results['classification_counts']=dict(collections.Counter(results['classification'].values()))
options.output.parent.mkdir(parents=True,exist_ok=True)
options.output.write_text(json.dumps(results,indent=2)+'\n')
print(json.dumps({'counts':results['classification_counts'],'probes':{k:{'completeness':v['completeness'],'risks':len(v['risks']),'view':v['agent_view']} for k,v in results.items() if isinstance(v,dict) and 'agent_view' in v}},indent=2))
