"""Explicit read composition and one agent-authored guarded action. No planner."""
import json
import math
import os
import re
from .core import Error, atomic_json, identifier, lock, now, read_json
from .control import effect
from .mcp import validate
from .observations import same_value
from .responses import section


def obj(properties, required=()):
    return {'type':'object','properties':properties,'required':list(required),'additionalProperties':False}


STRING = {'type':'string','minLength':1}
ARGS = {'type':'object','additionalProperties':True}
KEY={'type':'string','pattern':'^[a-z][a-z0-9_-]{0,39}$'}
def includes(names):
    return {'type':'array','items':{'enum':list(names)},'minItems':1,'uniqueItems':True}
PAWN_FACETS=('summary','needs','health','gear','bio','schedule')
DECISION_TOPICS=('core','alerts','food','medical','mood','threat','work','research','conditions','world')
DECISION_PAWN=obj({'id':STRING,'include':includes(PAWN_FACETS)},['id'])
QUERY={'oneOf':[
    obj({'key':KEY,'tool':STRING,'args':ARGS},['key','tool']),
    obj({'key':KEY,'preset':{'const':'pawn'},'id':STRING,
         'include':includes(PAWN_FACETS),
         'detail':{'type':'boolean'}},['key','preset','id']),
    obj({'key':KEY,'preset':{'const':'production'},'id':STRING,'worker_id':STRING,
         'include':includes(('station','bills','recipes','resources','worker','work_options'))},['key','preset','id']),
    obj({'key':KEY,'preset':{'const':'decision'},'include':includes(DECISION_TOPICS),
         'pawns':{'type':'array','items':DECISION_PAWN,'maxItems':8},
         'mood_below':{'type':'number','minimum':0,'maximum':100}},['key','preset'])]}
READ_SCHEMA = obj({'provenance':{'type':'boolean'},'reuse':{'type':'boolean'},
                   'queries':{'type':'array','items':QUERY,'minItems':1,'maxItems':32}}, ['queries'])
COMMAND = obj({'tool':STRING,'args':ARGS}, ['tool'])
PREDICATE = obj({'source':STRING,'path':{'type':'string'},
                 'match':{'type':'object','additionalProperties':True},
                 'field':{'type':'string'}, 'op':{'enum':['eq','ne','lt','lte','gt','gte']},
                 'value':{}}, ['source','path','op','value'])
GUARD_SCHEMA = obj({'provenance':{'type':'boolean'},'queries':READ_SCHEMA['properties']['queries'],
                    'when':{'type':'array','items':PREDICATE,'minItems':1,'maxItems':8},
                    'then':COMMAND,'otherwise':COMMAND,
                    'verify':READ_SCHEMA['properties']['queries']}, ['queries','when','then'])
TOOLS = {
 'rw_observe': {'name':'rw_observe','description':
  'Gather selected reads in one exchange. Use explicit queries, pawn/production presets, or preset=decision for a materialized '
  'core/alerts/food/medical/mood/work/research/conditions/world packet plus selected pawn facets. reuse=true uses only '
  'connection-cached facts current under conservative wait/mutation invalidation. Captures are sequential, not atomic; '
  'unrequested facts remain unknown and evidence is retained.', 'inputSchema':READ_SCHEMA},
 'rw_guard': {'name':'rw_guard','description':
  'Run selected reads→exact JSON-Pointer conditions→at most one literal action→optional verification. All predicates must '
  'be true for then; known false may select otherwise. Missing, ambiguous, partial, unpaused or newly warned input abstains. '
  'No loops, waits, setup, dynamic targets or retries. A receipt is not gameplay completion; use rw_observe when judgment remains.',
  'inputSchema':GUARD_SCHEMA}
}
TOOLS['rw_observe']['annotations']={'readOnlyHint':True}
TOOLS['rw_guard']['annotations']={'readOnlyHint':False}

PAWN = {'summary': lambda q:('get_pawn',{'id':q['id']}),
        **{tab:(lambda q,t=tab:('get_pawn',dict(id=q['id'],tab=t,**({'detail':q['detail']} if 'detail' in q and t in ('health','needs') else {}))))
           for tab in ('needs','health','gear','bio')},
        'schedule': lambda q:('set_schedule',{'id':q['id']})}
PRODUCTION = {'station':lambda q:('inspect_thing',{'id':q['id']}),
              'bills':lambda q:('list_bills',{'id':q['id']}),
              'recipes':lambda q:('list_recipes',{'id':q['id']}),
              'resources':lambda q:('get_resources',{}),
              'worker':lambda q:('get_pawn',{'id':q['worker_id']}),
              'work_options':lambda q:('order_pawn',{'id':q['worker_id'],'targetId':q['id']})}


def expand(queries):
    expanded = []
    keys = set()
    for q in queries:
        if q['key'] in keys: raise Error('Duplicate query key: '+q['key'])
        keys.add(q['key'])
        if 'preset' not in q:
            if set(q)-{'key','tool','args'} or 'tool' not in q: raise Error('Explicit query requires key/tool/args only.')
            expanded.append({'key':q['key'],'tool':q['tool'],'args':q.get('args',{})})
            continue
        if q.get('preset')=='decision':
            prefix=q['key']
            topics=q.get('include') or ['core','alerts']
            if any(t!='world' for t in topics):expanded.append({'key':prefix+'.status','tool':'get_status','args':{}})
            if 'world' in topics:expanded.append({'key':prefix+'.world','tool':'list_world_objects','args':{}})
            if 'threat' in topics:
                args={'category':'pawn','limit':20}
                if q.get('pawns'):args.update(nearId=q['pawns'][0]['id'],radius=50)
                expanded.append({'key':prefix+'.threat','tool':'list_things','args':args})
            for i,pawn in enumerate(q.get('pawns') or []):
                for facet in pawn.get('include') or ['summary']:
                    tool,args=PAWN[facet]({'id':pawn['id']})
                    expanded.append({'key':prefix+'.pawn'+str(i)+'.'+facet,'tool':tool,'args':args})
            continue
        if 'tool' in q or 'args' in q or 'id' not in q: raise Error('Pawn/production preset requires an id and cannot also supply tool/args.')
        choices = PAWN if q['preset']=='pawn' else PRODUCTION
        includes = q.get('include', ['summary'] if q['preset']=='pawn' else ['station','bills'])
        if q['preset']=='pawn' and 'worker_id' in q: raise Error('worker_id is a production option.')
        if q['preset']=='production' and 'detail' in q: raise Error('detail is a pawn option.')
        for name in includes:
            if name not in choices: raise Error('Unsupported section '+name+'; available: '+', '.join(choices))
            if name in ('worker','work_options') and 'worker_id' not in q: raise Error(name+' requires worker_id.')
            tool,args = choices[name](q)
            # A single requested facet already has an unambiguous caller key.
            # Qualify only multi-facet presets, avoiding predictable `key.facet`
            # lookup mistakes without duplicating the returned data.
            key=q['key'] if len(includes)==1 else q['key']+'.'+name
            expanded.append({'key':key,'tool':tool,'args':args})
    if not 1 <= len(expanded) <= 32: raise Error('Use at most32 expanded read queries.')
    return expanded


def preflight(control, query, mutation=False):
    catalog = read_json(control.campaign.path/'raw/catalog.json')['tools']
    tool,args = query['tool'],query.get('args',{})
    if tool not in catalog: raise Error('Tool absent from captured catalog: '+tool)
    validate(catalog[tool]['inputSchema'], args)
    kind = control.effective_effect(tool,args,catalog)
    if mutation:
        if kind!='mutation' or tool=='set_speed': raise Error('Guard branches require an ordinary mutation, without waits/setup/speed changes.')
    elif not kind.startswith('inspection'):
        raise Error('Composition accepts classified ordinary reads only: '+tool)


MISSING = object()

def pointer(data, path):
    if path=='': return data
    if not path.startswith('/'): raise Error('Use an RFC6901 JSON Pointer (empty or starting with /).')
    parts=path[1:].split('/')
    for encoded in parts:
        if any(encoded[i]=='~' and (i+1==len(encoded) or encoded[i+1] not in '01') for i in range(len(encoded))):
            raise Error('Invalid JSON Pointer escape.')
    for encoded in parts:
        part=encoded.replace('~1','/').replace('~0','~')
        if isinstance(data,dict): data=data.get(part,MISSING)
        elif isinstance(data,list) and re.fullmatch(r'0|[1-9][0-9]*',part):
            data=data[int(part)] if int(part)<len(data) else MISSING
        else: return MISSING
    return data


def predicate(data, p):
    value=pointer(data,p['path'])
    if value is MISSING: return None
    if 'match' in p:
        if not isinstance(value,list): return None
        found=[row for row in value if isinstance(row,dict) and all(k in row and same_value(row[k],v) for k,v in p['match'].items())]
        if len(found)!=1: return None
        value=pointer(found[0],p.get('field',''))
    elif 'field' in p: raise Error('field requires match.')
    if value is MISSING: return None
    expected=p['value'];op=p['op']
    if any(type(v) is float and not math.isfinite(v) for v in (value,expected)): return None
    if op in ('eq','ne'):
        if type(value) is not type(expected): return None
        eq=same_value(value,expected);return eq if op=='eq' else not eq
    if any(type(v) not in (int,float) or not math.isfinite(v) for v in (value,expected)):return None
    return {'lt':value<expected,'lte':value<=expected,'gt':value>expected,'gte':value>=expected}[op]


def interruptions(value):
    """Explicit reported changes/warnings, never a strategic health classifier."""
    if isinstance(value,dict):
        for k,v in value.items():
            if k in ('error','warning','warnings','_notifications','_transportNotifications','_delta','_dialogOpen','_threatWarning','_protocolNotifications','_mcpAdditionalText') and v:
                return True
            if interruptions(v): return True
    elif isinstance(value,list):
        return any(interruptions(v) for v in value)
    return False


def capture(control, value):
    obs=control.campaign.observation(value['id'])
    result=section(control.campaign,obs)
    children=[control.campaign.observation(c['id']) for c in value.get('bundle',[])]
    if children:
        result['bundle_coverage']=[{'observation':c['id'],'tool':c['tool'],
            'completeness':c['completeness'],'missing':c['missing']} for c in children]
    controls={k:value[k] for k in ('identity_mismatch','pause_guard','wait_budget') if k in value}
    if controls:result['control']=controls
    incomplete=(bool(value.get('identity_mismatch') or value.get('pause_guard')) or obs['completeness']!='known'
                or any(c['completeness']!='known' for c in children)
                or bool(result.get('metadata',{}).get('unusable_json_blocks'))
                or result.get('result_properties',{}).get('isError') is True)
    return result,incomplete


def compact_result(result):
    """Only deduplicate our own provenance/coverage, never game-returned data."""
    result=dict(result)
    all_sections=list(result['sections'].values())+list(result.get('verification',{}).values())
    if 'action' in result:all_sections.append(result['action'])
    times=[s['source']['captured_at'] for s in all_sections]
    result['capture']=[min(times),max(times)] if times else []
    def trim(section):
        value={k:v for k,v in section.items() if k!='source'}
        if section['coverage']['state']=='known' and not any(c['completeness']!='known' for c in section.get('bundle_coverage',[])):
            value.pop('coverage',None);value.pop('bundle_coverage',None)
        return value
    result['sections']={k:trim(s) for k,s in result['sections'].items()}
    if 'verification' in result:result['verification']={k:trim(s) for k,s in result['verification'].items()}
    if 'action' in result:result['action']=trim(result['action'])
    result['queried_complete']=result['stopped'] is None
    if result['stopped'] is None:result.pop('stopped')
    result.pop('advancement_requested',None);result.pop('unrequested',None)
    return result


def _resources(data, words):
    rows=(data or {}).get('resources') or []
    return [r for r in rows if isinstance(r,dict) and any(w in (str(r.get('defName',''))+' '+str(r.get('label',''))).lower() for w in words)]


def decision_status(data, topics, mood_below=35):
    """Materialize only requested decision facets from one bundled status read."""
    bundled=data.get('bundled') or {}
    colonists=(bundled.get('list_colonists') or {}).get('colonists') or []
    alerts=bundled.get('get_alerts') or {}
    resources=bundled.get('get_resources') or {}
    result={}
    if 'core' in topics:
        result['core']={k:data[k] for k in ('ticksGame','paused','timeSpeed','maps','colonistCount') if k in data}
        result['core']['dangerByMap']=alerts.get('dangerByMap')
    if 'alerts' in topics:
        result['alerts']={'activeLetters':alerts.get('activeLetters',[]),'activeAlerts':alerts.get('activeAlerts',[]),
                          'recentMessages':alerts.get('recentMessages',[]),'dangerByMap':alerts.get('dangerByMap')}
    if 'food' in topics:
        result['food']={'resources':_resources(resources,('meal','meat','rice','pemmican','berr','egg','milk','corn','potato')),
                        'alerts':[a for a in alerts.get('activeAlerts',[]) if 'food' in str(a.get('label','')).lower()]}
    if 'medical' in topics:
        result['medical']=[p for p in colonists if p.get('health',100)<100 or 'health' in str(p.get('hint','')).lower() or p.get('downed')]
        result['medicine']=_resources(resources,('medicine','medkit'))
    if 'mood' in topics:
        result['mood']=[p for p in colonists if isinstance(p.get('mood'),(int,float)) and p['mood']<=mood_below or p.get('mentalState')]
    if 'threat' in topics:
        result['threat']={'warning':data.get('_threatWarning'),
                          'dangerByMap':alerts.get('dangerByMap'),
                          'mentalStates':[p for p in colonists if p.get('mentalState')]}
    if 'work' in topics:
        result['work']=[{k:p.get(k) for k in ('id','name','job','downed','mentalState') if k in p} for p in colonists]
    if 'research' in topics:result['research']=bundled.get('get_research')
    if 'conditions' in topics:result['conditions']=bundled.get('get_conditions')
    return result


def materialize_decisions(result, specs, evidence):
    decisions={}
    for q in specs:
        if q.get('preset')!='decision':continue
        key=q['key'];topics=q.get('include') or ['core','alerts'];packet={}
        status=result['sections'].pop(key+'.status',None)
        if status and 'data' in status:
            packet.update(decision_status(status['data'],topics,q.get('mood_below',35)))
        world=result['sections'].pop(key+'.world',None)
        if world and 'data' in world:packet['world']=world['data']
        threat=result['sections'].pop(key+'.threat',None)
        if threat and 'data' in threat:
            existing=packet.get('threat') or {}
            packet['threat']={**existing,'nearby':threat['data'],'evidence':evidence.get(key+'.threat')}
        selected=[]
        for i,pawn in enumerate(q.get('pawns') or []):
            facets={}
            for facet in pawn.get('include') or ['summary']:
                section=result['sections'].pop(key+'.pawn'+str(i)+'.'+facet,None)
                if section and 'data' in section:facets[facet]=section['data']
            selected.append({'id':pawn['id'],'facets':facets})
        if selected:packet['pawns']=selected
        packet['evidence']=[evidence[k] for k in evidence if k.startswith(key+'.')]
        decisions[key]=packet
    if decisions:result['decisions']=decisions
    return result


def group_presets(result, specs):
    """Preserve each caller key; nest facets instead of inventing top-level keys."""
    sections=result.get('sections',{})
    for q in specs:
        preset=q.get('preset')
        if preset not in ('pawn','production'):continue
        choices=PAWN if preset=='pawn' else PRODUCTION
        includes=q.get('include', ['summary'] if preset=='pawn' else ['station','bills'])
        if len(includes)==1:continue
        grouped={}
        for facet in includes:
            section=sections.pop(q['key']+'.'+facet,None)
            if section is not None:grouped[facet]=section
        if grouped:sections[q['key']]=grouped
    return result


class Composer:
    def __init__(self, control, token, on_observation=None, driver="agent_composition", memo=None):
        self.control=control;self.token=token;self.on_observation=on_observation or (lambda _:None)
        self.driver=driver;self.memo=memo;self.reuse=False
        self.path=control.path/'composition.json';self.record=None

    def save(self):
        atomic_json(self.path,self.record)
        atomic_json(self.control.campaign.path/'reference/compositions'/ (self.record['request_id']+'.json'),self.record)

    def read(self, queries, output):
        for i,q in enumerate(queries):
            self.record['phase']='reading';self.record['next_query']=q;self.save()
            cached=self.memo.reusable(q['tool'],q['args']) if self.memo is not None and self.reuse else None
            if cached:
                value={'id':cached};self.record.setdefault('reused',[]).append({'key':q['key'],'id':cached})
            else:
                value=self.control.call(self.token,q['tool'],q['args'],driver=self.driver)
                self.on_observation(value['id'])
            output[q['key']],incomplete=capture(self.control,value)
            if cached:output[q['key']]['reused']=True
            self.record['observations'].append({'key':q['key'],'id':value['id'],'source':output[q['key']]['source'],'coverage':output[q['key']]['coverage']});self.save()
            if incomplete:
                return {'reason':'Identity, pause, JSON or coverage requires review','after':q['key'],'not_run':[x['key'] for x in queries[i+1:]]}
        return None

    def execute(self, name, spec):
        from .facade import reserved
        reserved(read_json(self.control.campaign.path/'raw/catalog.json'))
        validate(TOOLS[name]['inputSchema'],spec)
        self.reuse=spec.get('reuse',False)
        queries=expand(spec['queries']);verify=expand(spec['verify']) if spec.get('verify') else []
        if len(queries)+len(verify)>32:raise Error('Use at most32 total reads including verification.')
        for q in queries+verify:preflight(self.control,q)
        if name=='rw_guard':
            for branch in ('then','otherwise'):
                if branch in spec:preflight(self.control,spec[branch],True)
            keys={q['key'] for q in queries}
            for p in spec['when']:
                if p['source'] not in keys:raise Error('Guard source is not a requested section: '+p['source'])
                pointer({},p['path'])
                if 'field' in p:pointer({},p['field'])
                if 'field' in p and 'match' not in p:raise Error('field requires match.')
                if 'match' in p and not p['match']:raise Error('match must name at least one exact field.')
        with lock(self.control.path/'operation.lock'):
            self.control._owner(self.token);self.control._no_pending()
            binding=self.control.campaign.meta.get('binding')
            if name=='rw_guard' and (not binding or binding['expected'].get('loaded') is not True):
                raise Error('Guard requires a reviewed loaded-game binding.')
            if not binding and any(q['tool']!='get_status' for q in queries):
                raise Error('Bind the reviewed game before composing other reads.')
            self.record={'request_id':identifier('compose-'),'kind':'composition','tool':name,'args':spec,
                         'pid':os.getpid(),'started_at':now(),'status':'inflight','phase':'starting','observations':[]}
            self.save();self.control._composition_id=self.record['request_id']
            result={'composition':self.record['request_id'],'sections':{},'advancement_requested':False,
                    'capture':'sequential','unrequested':'unknown'}
            try:
                result['stopped']=self.read(queries,result['sections'])
                if name=='rw_guard':self.choose(spec,result,verify)
                if name=='rw_guard':
                    self.record.update({k:result[k] for k in ('condition','selected_branch','action_status','verification_not_run') if k in result})
                self.record.update(status='ready_to_deliver',phase='complete',stopped=result['stopped']);self.save()
                if spec.get('provenance'):
                    return group_presets(result,spec['queries']) if name=='rw_observe' else result
                evidence={key:s['source']['observation'] for key,s in result['sections'].items()}
                shaped=materialize_decisions(compact_result(result),spec['queries'],evidence)
                return group_presets(shaped,spec['queries']) if name=='rw_observe' else shaped
            except BaseException as exc:
                self.record.update(status='unknown',error=str(exc));self.save();raise
            finally:
                self.control._composition_id=None

    def choose(self,spec,result,verify):
        decisions=[]
        for p in spec['when']:
            s=result['sections'].get(p['source'],{})
            decisions.append(predicate(s['data'],p) if 'data' in s else None)
        ambiguous=any(s.get('content') or s.get('result_properties',{}).get('structuredContent') is not None for s in result['sections'].values())
        paused=all(isinstance(s.get('data'),dict) and (s['data'].get('_paused') is True or s['data'].get('paused') is True) for s in result['sections'].values())
        if not paused or result['stopped'] or ambiguous or any(s.get('result_properties',{}).get('isError') is True for s in result['sections'].values()) or interruptions(result['sections']) or any(x is None for x in decisions):
            result['condition']='unknown';result['selected_branch']=None
            result['verification_not_run']=[q['key'] for q in verify];result['action_status']='not_dispatched';result['no_action_reason']='Incomplete/ambiguous condition, unconfirmed pause, or reported interruption; no fallback executed.';return
        truth=all(decisions);branch='then' if truth else 'otherwise'
        result['condition']=truth;result['selected_branch']=branch if branch in spec else None
        if branch not in spec:
            result['verification_not_run']=[q['key'] for q in verify];result['action_status']='not_requested';return
        command=spec[branch];self.record.update(phase='action',selected_branch=branch,action=command);self.save()
        value=self.control.call(self.token,command['tool'],command.get('args',{}),driver=self.driver)
        if self.memo is not None:self.memo.invalidate('mutation')
        self.on_observation(value['id'])
        result['action'],incomplete=capture(self.control,value);result['action_status']='receipt_only'
        self.record['action_evidence']=value['id'];self.save()
        if incomplete or interruptions(result['action']):
            result['stopped']={'reason':'Action response requires review','not_run':[q['key'] for q in verify]};return
        result['verification']={}
        result['stopped']=self.read(verify,result['verification'])


def delivered(control,token,composition_id):
    with lock(control.path/'operation.lock'):
        control._owner(token)
        path=control.path/'composition.json';record=read_json(path)
        if record['request_id']!=composition_id or record['status']!='ready_to_deliver':raise Error('Composition is not ready for delivery acknowledgement.')
        record.update(status='delivered',delivered_at=now())
        atomic_json(control.campaign.path/'reference/compositions'/(composition_id+'.json'),record)
        path.unlink()
