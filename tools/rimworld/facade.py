"""Small public MCP surface over the captured RimMolt catalog.

Every game operation still goes through Control.call. The facade shapes results
and persists only durable compound-delivery manifests; it never decides strategy.
"""
import os
import time

from .composition import (TOOLS as COMPOSED, QUERY, PAWN, capture, compact_result,
                          expand, interruptions, obj, preflight)
from .core import Error, atomic_json, canonical, identifier, lock, now, read_json
from .mcp import validate
from .observations import compact, delta_view, same_value
from .presentation import present

STRING={'type':'string','minLength':1}
ARGS={'type':'object','additionalProperties':True}
VIEW={'enum':['compact','summary','full']}
FIELDS={'type':'array','items':STRING,'minItems':1,'maxItems':32,'uniqueItems':True}

CAPABILITY_DOMAINS=['setup','colony','pawns','medical','food','combat','building','world','quests','trade','production']
CAPABILITY_WORKFLOWS=['new_game','medical_event','combat_event','caravan','food_crisis','trade','resume_crisis']
CAPABILITIES_SCHEMA=obj({'query':{'type':'string'},'tool':STRING,'overview':{'type':'boolean'},
                         'domain':{'enum':CAPABILITY_DOMAINS},'workflow':{'enum':CAPABILITY_WORKFLOWS}})
READ_SCHEMA=obj({'tool':STRING,'args':ARGS,'view':VIEW,'fields':FIELDS,'row_fields':FIELDS,
                 'limit':{'type':'integer','minimum':1},'delta':{'type':'boolean'},'since':STRING},['tool'])
ACTION=obj({'tool':STRING,'args':ARGS},['tool'])
ACT_SCHEMA={'type':'object','properties':{'tool':STRING,'args':ARGS,'view':VIEW,
            'actions':{'type':'array','items':ACTION,'minItems':1,'maxItems':16},
            'independent':{'type':'boolean'}},'additionalProperties':False,
            'oneOf':[{'required':['tool']},{'required':['actions','independent']}]}
WAIT_SCHEMA=obj({'maxSeconds':{'type':'integer','minimum':5,'maximum':600},
                 'maxGameTicks':{'type':'integer','minimum':1},'maxGameSeconds':{'type':'number','minimum':0},
                 'maxGameHours':{'type':'number','minimum':0},'maxGameDays':{'type':'number','minimum':0},
                 'force':{'type':'boolean'},'view':VIEW,'context':{'enum':['auto','none']},
                 'verify':{'type':'array','items':QUERY,'minItems':1,'maxItems':8}})
RETRIEVE_SCHEMA=obj({'observation':STRING,'tool':STRING,'entity':STRING,'ref':STRING,
                     'view':VIEW,'fields':FIELDS})

TOOLS={
 'rw_capabilities':{'name':'rw_capabilities','description':
  'Discover available actions without loading the catalog. overview/domain gives a compact affordance map; workflow gives an ordered '
  'new_game, medical_event, combat_event, caravan, food_crisis, trade or resume_crisis guide. query finds names; tool returns one exact schema/effect. '
  'Offline only; grants no permission.',
  'inputSchema':CAPABILITIES_SCHEMA,'annotations':{'readOnlyHint':True}},
 'rw_read':{'name':'rw_read','description':
  'Run one read-only RimMolt tool by name and get a self-contained compact result. delta=true with since=OBS returns an explicit patch. Filter at the source: '
  'list_things takes category/defName/faction/nearId+radius/limit/summary; get_area takes minX,maxX,minZ,maxZ bounds/thing/summary; '
  'get_pawn takes tab and detail. fields selects top-level keys, row_fields selects columns within row lists; '
  'warnings and risks are always kept. '
  'Mutating arguments are refused here. Evidence is stored whole; rw_retrieve recovers it.',
  'inputSchema':READ_SCHEMA,'annotations':{'readOnlyHint':True}},
 'rw_act':{'name':'rw_act','description':
  'Run one mutation, or a pre-reviewed fail-stop actions[] batch with independent=true. Reads use rw_read; time uses rw_wait. '
  'set_speed pause remains available during uncertainty. order_pawn queue=true appends a Shift-click job. '
  'A receipt is not arrival, treatment, delivery or completed construction.',
  'inputSchema':ACT_SCHEMA,'annotations':{'readOnlyHint':False}},
 'rw_wait':{'name':'rw_wait','description':
  'Advance supervised time until an event and return paused. Choose wall/game horizons; hard deadlines clamp them. '
  'context defaults auto and adds a compact event decision packet; none disables it. verify runs preflighted reads after the wait '
  'in the same exchange. Inspect pausedAfter and ticksWaited.',
  'inputSchema':WAIT_SCHEMA,'annotations':{'readOnlyHint':False}},
 'rw_retrieve':{'name':'rw_retrieve','description':
  'Recover already-captured evidence. observation replays one stored response (view full is the complete original), '
  'tool/entity lists latest matching observations, ref resolves a same_as reference from this connection. '
  'Reads local evidence only; never contacts the game or advances time.',
  'inputSchema':RETRIEVE_SCHEMA,'annotations':{'readOnlyHint':True}},
}

# Local names are reserved against the upstream catalog wherever discovery or
# dispatch merges the two. Effects are declared, never inferred from the name.
LOCAL_EFFECTS={'rw_observe':'composition-read','rw_guard':'guarded-mutation',
               'rw_capabilities':'offline-discovery','rw_retrieve':'offline-evidence',
               'rw_read':'proxied-read','rw_act':'proxied-mutation','rw_wait':'proxied-advance'}


def local():
    """Every locally served tool declaration, composed plus facade."""
    return {**COMPOSED,**TOOLS}


def reserved(catalog):
    """Refuse a captured catalog that shadows a local name."""
    if set(local()) & set(catalog.get('tools',catalog)):
        raise Error('Local composition name collides with upstream catalog.')


NATIVE={'list_things':'category, defName, faction, nearId or nearX/nearZ with radius, limit, summary',
        'get_area':'minX/maxX/minZ/maxZ bounds, thing, layer, scale, summary',
        'get_pawn':'tab (needs/health/gear/bio), detail',
        'list_world_objects':'mapIndex, limit where offered',
        'list_trade':'filter, limit',
        'get_window_ui':'For a trade dialog use list_trade; otherwise inspect list_windows and select only needed fields.'}


def classify(control, tool, args):
    """Re-derive the argument-dependent effect exactly as composition preflight does."""
    catalog=read_json(control.campaign.path/'raw/catalog.json')['tools']
    if tool not in catalog:
        raise Error('Tool absent from captured catalog: '+str(tool)+'; search rw_capabilities for the current name.')
    validate(catalog[tool]['inputSchema'],args)
    return control.effective_effect(tool,args,catalog)


def gate(kind, tool, want):
    """Narrow the facade surface. Control.call remains the authority."""
    if want=='read':
        if kind.startswith('inspection'): return
        if kind=='advance': raise Error(tool+' advances game time; use rw_wait.')
        if kind=='mutation': raise Error(tool+' with these arguments is a mutation, not a read; use rw_act.')
    elif want=='act':
        if kind=='mutation': return
        if kind=='advance': raise Error(tool+' advances game time; use rw_wait.')
        if kind.startswith('inspection'): raise Error(tool+' with these arguments is a read; use rw_read.')
    elif want=='wait':
        if kind=='advance': return
        raise Error('rw_wait serves wait_for_event only.')
    raise Error('Refused '+str(kind)+' operation: '+tool)


def capabilities(control, args):
    from .capabilities import discover, overview
    selected=[key for key in ('tool','domain','workflow') if args.get(key) is not None]
    if args.get('overview'):selected.append('overview')
    if args.get('query'):selected.append('query')
    if len(selected)>1:raise Error('Choose one capability selector: overview, domain, workflow, query or tool.')
    if args.get('overview') or args.get('domain') or args.get('workflow'):
        return overview(control.campaign.root,control.campaign,args.get('domain'),args.get('workflow'))
    return discover(control.campaign.root,args.get('query',''),args.get('tool'),control.campaign)


def journal(control, name, body, started, *, tool=None, view=None, game_contact=True):
    """One row per facade call recording what the model actually received.

    Control.call measures the upstream payload before facade shaping, and the two
    offline tools never reach it at all, so neither is visible without this.
    """
    from . import __version__
    from .core import append_json, now
    entry={'at':now(),'version':__version__,'kind':'facade_call','facade_tool':name,
           'tool':tool,'view':view or 'compact','driver':'facade_'+name[3:],
           'game_contact':game_contact,'seconds':time.monotonic()-started,
           'model_bytes':len(canonical(body).encode()),
           'model_bytes_basis':'Exact facade envelope serialized to the caller.'}
    if isinstance(body,dict):
        change=body.get('change') if isinstance(body.get('change'),dict) else {}
        entry.update(truncated=bool(body.get('truncated')),refs_minted=len(body.get('refs') or {}),
                     projected=bool(body.get('projected')),omitted=len(body.get('omitted_keys') or []),
                     unchanged=bool(body.get('unchanged') or change.get('unchanged')),
                     changed_fields=len(body.get('changed_fields') or change.get('changed_fields') or []),
                     event_context=bool(body.get('event_context')),
                     verification_sections=len(body.get('verification') or {}),
                     batch_actions=len(body.get('results') or []) if name=='rw_act' else 0,
                     decision_packets=len(body.get('decisions') or {}),
                     reused_sections=canonical(body).count('"reused":true'),
                     trade_context=bool(body.get('trade')),
                     partial_data=body.get('completeness')=='partial' and 'data' in body)
        if body.get('truncated'): entry['reason']=body.get('reason')
    append_json(control.campaign.path/'telemetry.jsonl',entry)
    return body


class Sequence:
    """Durable public compound call; delivery is acknowledged by Session/CLI."""
    def __init__(self,control,token,name,args):
        self.control=control;self.token=token
        self.path=control.path/'composition.json'
        self.record={'request_id':identifier('compose-'),'kind':'composition','tool':name,'args':args,
                     'pid':os.getpid(),'started_at':now(),'status':'inflight','phase':'starting','observations':[]}

    def save(self):
        atomic_json(self.path,self.record)
        atomic_json(self.control.campaign.path/'reference/compositions'/(self.record['request_id']+'.json'),self.record)

    def start(self):
        with lock(self.control.path/'operation.lock'):
            self.control._owner(self.token);self.control._no_pending();self.save()
            self.control._composition_id=self.record['request_id']
        return self

    def observed(self,key,value,requested=None,reused=False):
        obs=self.control.campaign.observation(value['id'])
        entry={'key':key,'id':value['id'],'tool':obs['tool'],'args':obs.get('args',{})}
        if requested is not None:
            entry.update(requested_tool=requested['tool'],requested_args=requested.get('args',{}),reused=reused)
        self.record['observations'].append(entry);self.save()

    def ready(self,**fields):
        self.record.update(status='ready_to_deliver',phase='complete',**fields);self.save()

    def failed(self,exc):
        self.record.update(status='unknown',error=str(exc));self.save()

    def close(self):self.control._composition_id=None


def change_metadata(value):
    delta=value.get('delta') or {}
    if 'changed_fields' not in delta and not value.get('unchanged'):return None
    result={'unchanged':bool(value.get('unchanged')),
            'previous':delta.get('previous_evidence')}
    if delta.get('changed_fields'):result['changed_fields']=delta['changed_fields']
    if delta.get('not_returned_now'):result['not_returned_now']=delta['not_returned_now']
    return result


def self_contained(control,value):
    """Current compact facts plus separate novelty metadata."""
    obs=control.campaign.observation(value['id'])
    current=compact(obs)
    if value.get('safety') is not None:current['safety']=value['safety']
    body=stable_data(literal_rows(present(current)))
    if obs.get('tool')=='get_window_ui' and 'trade' in canonical(obs.get('data',{})).lower():
        body={'affordance':{'prefer':['list_trade','set_trade','trade_action'],
              'reason':'A trade dialog is open; semantic trade tools avoid generic button geometry and expose prices/counts directly.'},**body}
    change=change_metadata(value)
    if change:body['change']=change
    return body,obs


def trade_window_context(control,token,body,window_obs,memo,observed):
    """Prefer semantic trade state to hundreds of generic UI controls."""
    gate(classify(control,'list_trade',{'limit':80}),'list_trade','read')
    value=control.call(token,'list_trade',{'limit':80},driver='facade_read_context')
    if observed:observed(value['id'])
    trade,trade_obs=self_contained(control,value)
    trade=budget(bound(trade,trade_obs,{},memo),trade_obs,'list_trade')
    data=body.get('data') if isinstance(body.get('data'),dict) else {}
    controls=('buttons','textFields','labels','tabs','checkboxes','radios')
    summary={key:len(data.get(key) or []) for key in controls if isinstance(data.get(key),list)}
    kept={key:data[key] for key in ('ok','window','captured','hint','_paused','_dialogOpen') if key in data}
    return {'affordance':{'prefer':['list_trade','set_trade','trade_action'],
             'reason':'Semantic trade state is included; generic control geometry remains in stored window evidence.'},
            'id':body.get('id'),'data':kept,'ui_control_counts':summary,'trade':trade,
            'omitted_keys':['data.'+key for key in controls if key in data],
            'recover':'rw_retrieve {observation:"'+window_obs['id']+'", view:"full"}',
            **{key:body[key] for key in ('warnings','risks','requires_review') if key in body}}


def delta_base(control,tool,args,since):
    base=control.campaign.observation(since)
    if (base.get('tool')!=tool or not same_value(base.get('args',{}),args) or
        base.get('campaign_id')!=control.campaign.meta['id'] or
        base.get('session_id')!=control.campaign.meta.get('session_id') or
        base.get('completeness')!='known'):
        raise Error('since must name a complete observation from this session with the same tool and arguments.')
    return base


def presented(control,value,args,memo,tool):
    obs=control.campaign.observation(value['id'])
    body,obs=self_contained(control,value)
    for key in ('identity_mismatch','pause_guard','wait_budget'):
        if key in value:body[key]=value[key]
    return budget(bound(body,obs,args,memo),obs,tool)


def explicit_failure(body):
    if not isinstance(body,dict):return True
    for container in ('data','status','health','needs','known_subset'):
        value=body.get(container)
        if isinstance(value,dict) and (value.get('ok') is False or value.get('error')):return True
    return body.get('completeness') not in (None,'known')


def expected_same_dialog(action,body,window):
    """A successful window action requires its dialog to remain open."""
    if action.get('tool')!='window_action':return False,None
    data=body.get('data') if isinstance(body,dict) else None
    if not isinstance(data,dict) or data.get('ok') is not True or not data.get('window'):return False,None
    if data.get('applied') is False or data.get('warning') or data.get('error'):return False,None
    if window is not None and data['window']!=window:return False,None
    risks=body.get('risks') or []
    if any(r.get('kind')!='_dialogOpen' for r in risks):return False,None
    warnings=body.get('warnings') or {}
    if any(key not in ('_dialogOpen','_paused') for key in warnings):return False,None
    return True,data['window']


def action_batch(control,token,args,setup,memo,observed):
    if args.get('independent') is not True:raise Error('Action batches require independent=true after reviewing that no step depends on an earlier outcome.')
    actions=args['actions']
    for action in actions:
        kind=classify(control,action['tool'],action.get('args',{}));gate(kind,action['tool'],'act')
        if action['tool']=='set_speed':raise Error('Pause/speed changes cannot be precommitted in an action batch.')
    sequence=Sequence(control,token,'rw_act',args).start();results=[];expected_window=None
    try:
        for index,action in enumerate(actions):
            sequence.record.update(phase='action',next_action=index);sequence.save()
            value=control.call(token,action['tool'],action.get('args',{}),setup=setup,driver='facade_act_batch')
            if memo is not None:memo.invalidate('mutation')
            if observed:observed(value['id'])
            sequence.observed(str(index),value)
            body=presented(control,value,{},memo,action['tool'])
            results.append({'index':index,'tool':action['tool'],'receipt':body})
            dialog_ok,dialog_window=expected_same_dialog(action,body,expected_window)
            if dialog_ok:expected_window=dialog_window
            if explicit_failure(body) or (body.get('requires_review') and not dialog_ok):
                remaining=list(range(index+1,len(actions)))
                result={'composition':sequence.record['request_id'],'completed':index+1,'not_run':remaining,
                        'stopped':True,'reason':'Action response requires review','results':results}
                sequence.ready(stopped=result['reason'],not_run=remaining);return result
        result={'composition':sequence.record['request_id'],'completed':len(results),'not_run':[],
                'stopped':False,'results':results,
                'outcome':'Receipts only; queued jobs and gameplay results still require event/outcome evidence.'}
        sequence.ready(stopped=None,not_run=[]);return result
    except BaseException as exc:
        sequence.failed(exc);raise
    finally:sequence.close()


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


def event_topics(body):
    text=canonical(body).lower();topics=['core','alerts']
    if any(word in text for word in ('food','meal','starv','malnutrition')):topics.append('food')
    if any(word in text for word in ('injur','infection','disease','bleed','poison','healed','damage')):topics.append('medical')
    if any(word in text for word in ('break risk','mental','wander','berserk','tantrum','mood')):topics.append('mood')
    if any(word in text for word in ('caravan','formation','arriv')):topics.append('world')
    if any(word in text for word in ('raid','threat','hostile','attack','fire')):topics.append('threat')
    return list(dict.fromkeys(topics))


def mentioned_pawns(colonists,text):
    """Match IDs, full names, or unambiguous human-scale name tokens."""
    import re
    tokens={}
    for pawn in colonists:
        for token in set(re.findall(r"[a-z0-9]+",str(pawn.get('name','')).lower())):
            if len(token)>=3:tokens[token]=tokens.get(token,0)+1
    text_tokens=set(re.findall(r"[a-z0-9]+",text))
    result=[]
    for pawn in colonists:
        identity=str(pawn.get('id','')).lower();name=str(pawn.get('name','')).lower()
        aliases=[t for t in re.findall(r"[a-z0-9]+",name) if len(t)>=3 and tokens.get(t)==1]
        if (identity and identity in text_tokens) or (name and name in text) or any(alias in text_tokens for alias in aliases):
            result.append(pawn)
    return result[:2]


def event_letter_ids(value):
    found=[]
    def visit(node):
        if isinstance(node,dict):
            if isinstance(node.get('id'),int) and (node.get('kind')=='letter' or str(node.get('type','')).lower() in ('threatsmall','threatbig','negativeevent','positiveevent','newquest')):
                found.append(node['id'])
            for child in node.values():visit(child)
        elif isinstance(node,list):
            for child in node:visit(child)
    visit(value)
    return list(dict.fromkeys(found))[:2]


def responder_row(row):
    keys=('id','name','label','kind','x','z','distance','weapon','health','mood','downed','drafted','hostile','mentalState','incapableOf')
    return {key:row[key] for key in keys if key in row}


def context_data(data):
    """Remove only context already represented once by the event packet."""
    return {key:value for key,value in data.items() if key not in ('_paused','_threatWarning')}


def event_details(control,token,wait_data,status_data,topics,memo,observed,sequence):
    """Bounded directly relevant reads; context selection only, never an action."""
    details={};bundled=status_data.get('bundled') or {}
    text=canonical({'wait':wait_data,'alerts':(bundled.get('get_alerts') or {}).get('activeAlerts',[])}).lower()
    colonists=(bundled.get('list_colonists') or {}).get('colonists') or []
    matched=mentioned_pawns(colonists,text)
    facets=[]
    if matched and ('mood' in topics or 'threat' in topics):facets.append('summary')
    if 'medical' in topics:facets.append('health')
    if 'mood' in topics:facets.extend(('needs','health'))
    if 'threat' in topics and matched:facets.append('gear')
    facets=list(dict.fromkeys(facets))
    attention=[]
    for pawn in matched:
        for facet in facets:
            tool,pawn_args=PAWN[facet]({'id':pawn['id']})
            value=control.call(token,tool,pawn_args,driver='facade_wait_context')
            if observed:observed(value['id'])
            sequence.observed('event_'+facet+'_'+pawn['id'],value)
            obs=control.campaign.observation(value['id'])
            attention.append({'id':pawn['id'],'name':pawn['name'],'facet':facet,'data':context_data(obs['data']),'evidence':obs['id'],
                              'omitted_repeated_context':['_paused','_threatWarning'],
                              'coverage':{'completeness':obs['completeness'],'missing':obs['missing']}})
    if attention:details['affected_pawns']=attention
    letters=[]
    for letter_id in event_letter_ids(wait_data):
        value=control.call(token,'read_letter',{'id':letter_id},driver='facade_wait_context')
        if observed:observed(value['id'])
        sequence.observed('event_letter_'+str(letter_id),value);obs=control.campaign.observation(value['id'])
        letters.append({'id':letter_id,'data':context_data(obs['data']),'evidence':obs['id'],
                        'omitted_repeated_context':['_paused','_threatWarning'],
                        'completeness':obs['completeness'],'missing':obs['missing']})
    if letters:details['letters']=letters
    if 'threat' in topics:
        nearby=matched[0] if matched else None
        query={'category':'pawn','limit':20}
        if nearby:query.update(nearId=nearby['id'],radius=50)
        value=control.call(token,'list_things',query,driver='facade_wait_context')
        if observed:observed(value['id'])
        sequence.observed('event_threats',value);obs=control.campaign.observation(value['id'])
        rows=obs['data'].get('things') or []
        colonist_ids={p.get('id') for p in colonists}
        responder_ids=[]
        for row in rows:
            if (isinstance(row,dict) and row.get('id') in colonist_ids and
                    row.get('id') not in {p.get('id') for p in matched} and not row.get('hostile')):
                responder_ids.append(row['id'])
        responders=[]
        for responder_id in responder_ids[:4]:
            response=control.call(token,'get_pawn',{'id':responder_id},driver='facade_wait_context')
            if observed:observed(response['id'])
            sequence.observed('event_responder_'+responder_id,response)
            response_obs=control.campaign.observation(response['id'])
            responders.append({'id':responder_id,'data':context_data(response_obs['data']),
                               'evidence':response_obs['id'],'completeness':response_obs['completeness'],
                               'missing':response_obs['missing']})
        details['threats']={'hostiles':[responder_row(r) for r in rows if isinstance(r,dict) and r.get('hostile')],
                            'nearby_pawns':[responder_row(r) for r in rows if isinstance(r,dict) and not r.get('hostile')],
                            'responders':responders,
                            'anchor':nearby.get('id') if nearby else None,'radius':50 if nearby else None,
                            'evidence':obs['id'],'completeness':obs['completeness'],'missing':obs['missing']}
        if 'fire' in text:
            value=control.call(token,'list_fires',{},driver='facade_wait_context')
            if observed:observed(value['id'])
            sequence.observed('event_fires',value);obs=control.campaign.observation(value['id'])
            details['fires']={'data':obs['data'],'evidence':obs['id'],
                              'completeness':obs['completeness'],'missing':obs['missing']}
    if 'world' in topics:
        value=control.call(token,'list_world_objects',{},driver='facade_wait_context')
        if observed:observed(value['id'])
        sequence.observed('event_world',value);obs=control.campaign.observation(value['id'])
        details['world']={'data':obs['data'],'evidence':obs['id'],
                          'completeness':obs['completeness'],'missing':obs['missing']}
    return details


def wait_sequence(control,token,args,setup,memo,observed):
    view=args.get('view','compact');verify=args.get('verify') or []
    if verify:
        for query in expand(verify):preflight(control,query)
    call_args=dict({k:v for k,v in args.items() if k not in ('view','context','verify')},pause='always')
    gate(classify(control,'wait_for_event',call_args),'wait_for_event','wait')
    sequence=Sequence(control,token,'rw_wait',args).start()
    try:
        sequence.record['phase']='wait';sequence.save()
        value=control.call(token,'wait_for_event',call_args,setup=setup,driver='facade_wait')
        if memo is not None:memo.invalidate('advance')
        if observed:observed(value['id'])
        sequence.observed('wait',value)
        obs=control.campaign.observation(value['id'])
        body=shape(control.campaign,obs,view) if view!='compact' else presented(control,value,args,memo,'wait_for_event')
        data=obs.get('data') if isinstance(obs,dict) else None
        event=bool(isinstance(data,dict) and (data.get('event') or data.get('_notifications'))) or bool(body.get('requires_review'))
        context_safe=not body.get('pause_guard') and not (control.path/'pause-uncertain.json').exists()
        if args.get('context','auto')=='auto' and event and context_safe:
            try:
                sequence.record['phase']='event_context';sequence.save()
                status=control.call(token,'get_status',{},driver='facade_wait_context')
                if observed:observed(status['id'])
                sequence.observed('event_context',status)
                status_data=control.campaign.observation(status['id'])['data']
                from .composition import decision_status
                topics=event_topics(body)
                packet=decision_status(status_data,topics)
                status_obs=control.campaign.observation(status['id'])
                packet.update(evidence=status['id'],topics=topics,captured_after_wait=True,
                              coverage={'completeness':status_obs['completeness'],'missing':status_obs['missing']})
                controls={k:status[k] for k in ('identity_mismatch','pause_guard') if k in status}
                if controls:packet['control']=controls
                packet.update(event_details(control,token,data or {},status_data,topics,memo,observed,sequence))
                body['event_context']=packet
                if status_obs['completeness']!='known' or controls:body['requires_review']=True
            except Error as exc:
                # The wait and pause evidence are already durable. Optional read-only enrichment
                # failure must not make the completed wait replayable or composition-unknown.
                body['event_context_error']={'error':str(exc),'wait_completed':True,
                                             'no_replay':True,'phase':'post_wait_enrichment'}
                body['requires_review']=True
                sequence.record['enrichment_error']=body['event_context_error'];sequence.save()
        if verify:
            sequence.record['phase']='verification';sequence.save()
            sections,evidence,not_run,degraded=run_reads(control,token,verify,memo,observed,'facade_wait_verify',sequence)
            body['verification']=sections;body['verification_evidence']=evidence
            body['verification_complete']=not not_run;body['verification_not_run']=not_run
            body['verification_degraded']=degraded
        body['composition']=sequence.record['request_id']
        sequence.ready(stopped=None);return body
    except BaseException as exc:
        sequence.failed(exc);raise
    finally:sequence.close()


def dispatch(control, token, name, args, setup=False, memo=None, observed=None):
    """One facade call. Game operations still pass through Control.call unchanged."""
    started=time.monotonic()
    validate(TOOLS[name]['inputSchema'],args)
    if memo is not None: memo.sync(control.campaign)
    if name=='rw_capabilities':
        body=capabilities(control,args)
        return journal(control,name,body,started,
                       tool=args.get('tool') or ('query:'+args.get('query','') if args.get('query') else 'index'),
                       game_contact=False)
    if name=='rw_retrieve':
        body=retrieve(control,args,memo)
        return journal(control,name,body,started,view=args.get('view','compact'),
                       tool='ref' if args.get('ref') else ('observation' if args.get('observation') else 'tool/entity'),
                       game_contact=False)
    view=args.get('view','compact')
    if name=='rw_wait':
        body=wait_sequence(control,token,args,setup,memo,observed)
        return journal(control,name,body,started,tool='wait_for_event',view=view)
    if name=='rw_act' and args.get('actions') is not None:
        body=action_batch(control,token,args,setup,memo,observed)
        return journal(control,name,body,started,tool='batch',view=view)
    else:
        tool,call_args=args['tool'],args.get('args',{})
        want='read' if name=='rw_read' else 'act'
        base=None
        if want=='read':
            requested_delta=args.get('delta') is True
            if requested_delta != ('since' in args):
                raise Error('Explicit delta reads require both delta=true and since=OBS; omit both for current self-contained data.')
        if want=='act' and tool=='set_speed' and call_args=={'action':'pause'}:
            guard=control.ensure_paused(token,emergency=True)
            if not guard.get('confirmed'): raise Error('Ordinary pause could not be confirmed: '+str(guard))
            value={'id':guard['evidence']}
        else:
            gate(classify(control,tool,call_args),tool,want)
            if want=='read' and requested_delta:
                if view!='compact':raise Error('Explicit delta reads use compact view; omit delta/since for summary or full.')
                base=delta_base(control,tool,call_args,args['since'])
            value=control.call(token,tool,call_args,setup=setup,driver='facade_'+want)
            if memo is not None and want=='act':memo.invalidate('mutation')
    if observed: observed(value['id'])
    obs=control.campaign.observation(value['id'])
    if view!='compact':
        return journal(control,name,shape(control.campaign,obs,view),started,tool=tool,view=view)
    if name=='rw_read' and base is not None:
        body=stable_data(literal_rows(present(delta_view(base,obs))))
    else:
        body,_=self_contained(control,value)
    if (name=='rw_read' and base is None and tool=='get_window_ui' and
            'trade' in canonical(obs.get('data',{})).lower()):
        body=trade_window_context(control,token,body,obs,memo,observed)
    for key in ('identity_mismatch','pause_guard','wait_budget'):
        if key in value: body[key]=value[key]
    if (control.path/'pending.json').exists() or (control.path/'composition.json').exists():
        body['original_request_still_unresolved']=True
    return journal(control,name,budget(bound(body,obs,args,memo),obs,tool),started,tool=tool,view=view)


def retrieve(control, args, memo=None):
    campaign=control.campaign
    if args.get('ref') is not None:
        if memo is None or args['ref'] not in memo.values_by_id:
            raise Error('Unknown reference; references are valid only within the connection that minted them.')
        entry=memo.values_by_id[args['ref']]
        return {'ref':args['ref'],'field':entry['field'],'value':entry['value'],'e':entry['evidence'],
                'basis':'Literal value first delivered in this connection; the full original remains in evidence.'}
    view=args.get('view','compact')
    if args.get('observation') is not None:
        return shape(campaign,campaign.observation(args['observation']),view,args.get('fields'))
    if args.get('tool') is None and args.get('entity') is None:
        raise Error('Select observation, tool/entity or ref.')
    found=campaign.retrieve(args.get('tool'),args.get('entity'))
    return {'observations':[shape(campaign,o,view,args.get('fields')) for o in found],'n':len(found),
            'basis':'Latest stored observation per query scope; not a live read.'}


BODIES=('data','health','needs','status','known_subset')


def literal_rows(value):
    """Use conventional JSON arrays at the model boundary.

    Columnar packing remains an internal compact representation. Requiring the
    caller to decode it costs a handover when normal list operations suffice.
    """
    if isinstance(value,dict):
        if value.get('encoding')=='columns-v1':
            from .observations import unpack_rows
            return [literal_rows(row) for row in unpack_rows(value)]
        return {key:literal_rows(item) for key,item in value.items()}
    if isinstance(value,list):return [literal_rows(item) for item in value]
    return value


def stable_data(body):
    """Keep usable partial facts at the same data path as complete facts."""
    if isinstance(body,dict) and 'data' not in body and 'known_subset' in body:
        body=dict(body);body['data']=body.pop('known_subset')
    return body


def rows(value):
    """A row list from either a plain list or the compact columns-v1 packing."""
    if isinstance(value,list) and value and all(isinstance(r,dict) for r in value): return value
    if isinstance(value,dict) and value.get('encoding')=='columns-v1':
        from .observations import unpack_rows
        return unpack_rows(value)
    return None


def repack(original, selected):
    """Return rows in the shape they arrived in; packing is applied only when smaller."""
    from .observations import pack_rows
    return pack_rows(selected) if isinstance(original,dict) else selected


def keep(body, risks):
    """Keys projection must never drop: anything carrying a warning or a risk."""
    forced=set(body.get('warnings') or ())
    for risk in risks or ():
        ref=risk.get('value_ref') or ''
        for container in BODIES:
            if ref.startswith('#/'+container+'/'):
                forced.add(ref.split('/')[2].replace('~1','/').replace('~0','~'))
        kind=risk.get('kind','')
        if kind.startswith('delta:'): forced.add('_delta')
        elif kind in ('error','warning','warnings','rejected','failedCells','_threatWarning','_dialogOpen'): forced.add(kind)
    forced.update(body.get('changed_fields') or ())
    return forced


def project(body, fields=None, row_fields=None):
    """Select requested keys/columns. Reports every omission; never silent."""
    if not fields and not row_fields: return body,[]
    forced=keep(body,body.get('risks'))
    omitted=[]
    result=dict(body)
    for container in BODIES:
        value=result.get(container)
        if not isinstance(value,dict): continue
        if fields:
            wanted=set(fields)|forced
            dropped=[k for k in value if k not in wanted]
            if dropped:
                value={k:v for k,v in value.items() if k in wanted}
                omitted.extend(container+'.'+k for k in dropped)
        if row_fields:
            value=dict(value)
            for key,item in list(value.items()):
                listed=rows(item)
                if listed is None: continue
                columns=set().union(*(set(r) for r in listed))
                dropped=columns-set(row_fields)
                if not dropped: continue
                value[key]=repack(item,[{k:v for k,v in r.items() if k in row_fields} for r in listed])
                omitted.extend(container+'.'+key+'[].'+k for k in sorted(dropped))
        result[container]=value
    return result,omitted


BOILERPLATE=('_threatWarning','hint','_paused','_dialogOpen')
PAYLOAD_BUDGET=32768


class Memo:
    """Connection-scoped references plus explicitly invalidated observation reuse."""
    def __init__(self):
        self.by_value={};self.values_by_id={};self.reset_at=None
        self.observations={};self.time_generation=0;self.mutation_generation=0

    def sync(self, campaign):
        """Any presentation reset invalidates every outstanding reference."""
        current=campaign.meta.get('presentation_reset_at')
        if current!=self.reset_at:
            self.by_value.clear();self.values_by_id.clear();self.observations.clear()
            self.time_generation=0;self.mutation_generation=0;self.reset_at=current

    @staticmethod
    def stability(tool,args):
        if tool=='get_pawn' and args.get('tab')=='bio':return 'stable'
        if tool=='set_schedule' and 'assignment' not in args:return 'stable'
        if tool=='assign_building' and args.get('action','list')=='list':return 'stable'
        return 'volatile'

    def remember(self,campaign,observation_id):
        obs=campaign.observation(observation_id)
        if obs.get('completeness')!='known':return
        key=canonical({'tool':obs['tool'],'args':obs.get('args',{})})
        self.observations[key]={'id':observation_id,'tool':obs['tool'],'args':obs.get('args',{}),
            'stability':self.stability(obs['tool'],obs.get('args',{})),
            'time_generation':self.time_generation,'mutation_generation':self.mutation_generation}

    def invalidate(self,kind):
        if kind=='advance':self.time_generation+=1
        elif kind=='mutation':self.mutation_generation+=1

    def reusable(self,tool,args):
        entry=self.observations.get(canonical({'tool':tool,'args':args}))
        if not entry:return None
        if entry['mutation_generation']!=self.mutation_generation:return None
        if entry['stability']=='volatile' and entry['time_generation']!=self.time_generation:return None
        return entry['id']

    def state_summary(self):
        current=[];stale=[]
        for entry in self.observations.values():
            valid=(entry['mutation_generation']==self.mutation_generation and
                   (entry['stability']=='stable' or entry['time_generation']==self.time_generation))
            target=current if valid else stale
            target.append({'tool':entry['tool'],'args':entry['args'],'e':entry['id'],'stability':entry['stability']})
        return {'current':current,'stale_count':len(stale),'basis':'Connection-scoped; waits invalidate volatile facts and mutations conservatively invalidate prior facts.'}

    def substitute(self, body, obs):
        """Reference a repeated global value; never elide a changed or critical one.

        The field itself always stays present, so an appearance is never hidden;
        only a byte-identical payload already delivered here becomes a reference.
        """
        if obs['completeness']!='known': return body,{}
        critical={r.get('kind') for r in body.get('risks') or () if r.get('severity')=='critical'}
        minted={}
        for container in BODIES:
            value=body.get(container)
            if not isinstance(value,dict): continue
            for field in BOILERPLATE:
                if field not in value or field in critical: continue
                token=canonical({'f':field,'v':value[field]})
                known=self.by_value.get(token)
                if known is None:
                    short=field.strip('_')[:2].lower()+str(len(self.values_by_id)+1)
                    replacement={'same_as':short}
                    # A reference that is not materially shorter cannot repay its
                    # mint metadata; keep small values such as booleans literal.
                    if len(canonical(value[field]).encode()) <= len(canonical(replacement).encode())+8:
                        continue
                    self.by_value[token]=short
                    self.values_by_id[short]={'field':field,'value':value[field],'evidence':obs['id']}
                    minted[short]=obs['id'];continue
                value=dict(value);value[field]={'same_as':known}
                body=dict(body);body[container]=value
        return body,minted


def bound(body, obs, args, memo):
    """Projection, caller limit and connection references. Every omission is reported."""
    fields,row_fields=args.get('fields'),args.get('row_fields')
    if fields or row_fields:
        body,omitted=project(body,fields,row_fields)
        if omitted: body['omitted_keys']=omitted
        body['projected']=sorted(set(fields or [])|set(row_fields or []))
    limit=args.get('limit')
    if limit: body=cap(body,limit,obs,'caller_limit')
    if memo is not None:
        body,minted=memo.substitute(body,obs)
        if minted: body['refs']=minted
    return body


def cap(body, limit, obs, reason):
    """Trim whole rows from the largest row list. Never mid-object, never silent."""
    best=None
    for container in BODIES:
        value=body.get(container)
        if not isinstance(value,dict): continue
        for key,item in value.items():
            listed=rows(item)
            if listed is None or len(listed)<=limit: continue
            if best is None or len(listed)>best[2]: best=(container,key,len(listed))
    if best is None: return body
    container,key,total=best
    original=body[container][key]
    value=dict(body[container]);value[key]=repack(original,rows(original)[:limit])
    body=dict(body);body[container]=value
    body['truncated']=True;body['reason']=reason
    body['total']=total;body['returned']=limit
    body['e']=obs['id']
    body['recover']='rw_retrieve {observation, view:"full"}'
    return body


def budget(body, obs, tool, ceiling=PAYLOAD_BUDGET):
    """Backstop for an unfiltered read. The whole response is already evidence."""
    if len(canonical(body).encode())<=ceiling: return body
    candidates=[]
    for container in BODIES:
        value=body.get(container)
        if not isinstance(value,dict): continue
        for key,item in value.items():
            listed=rows(item)
            if listed and len(listed)>1: candidates.append((len(listed),container,key))
    if candidates:
        total,container,key=max(candidates)
        original=body[container][key];listed=rows(original)
        keep_n=total
        while keep_n>1:
            keep_n=keep_n//2
            trial=dict(body);value=dict(body[container]);value[key]=repack(original,listed[:keep_n])
            trial[container]=value
            if len(canonical(trial).encode())<=ceiling:
                trial['truncated']=True;trial['reason']='model_payload_budget'
                trial['total']=total;trial['returned']=keep_n;trial['e']=obs['id']
                trial['budget_bytes']=ceiling
                trial['recover']='rw_retrieve {observation, view:"full"}'
                if tool in NATIVE: trial['suggest']=NATIVE[tool]
                return trial
    return {'e':obs['id'],'truncated':True,'reason':'model_payload_budget','budget_bytes':ceiling,
            'total':None,'returned':0,'tool':obs['tool'],'completeness':obs['completeness'],
            'risks':body.get('risks'),'requires_review':body.get('requires_review'),
            'recover':'rw_retrieve {observation, view:"full"}',
            **({'suggest':NATIVE[tool]} if tool in NATIVE else {})}


def shape(campaign, obs, view, fields=None):
    """One stored observation in the requested view. Never contacts the game."""
    from .observations import evidence_index
    from .responses import visible_result
    if view=='full':
        result,metadata=visible_result(campaign,obs)
        return {'e':obs['id'],'view':'full','result':result,'metadata':metadata}
    if view=='summary':
        return {**evidence_index(obs),'e':obs['id'],'view':'summary'}
    body=stable_data(literal_rows(present(compact(obs))))
    if fields:
        body,omitted=project(body,fields)
        if omitted: body['omitted_keys']=omitted
    return body
