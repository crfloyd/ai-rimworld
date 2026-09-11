"""Small stable public MCP surface over the captured RimMolt catalog.

Shaping and dispatch only. Every game operation still goes through Control.call;
this module never persists evidence, classifies effects or decides strategy.
"""
import time

from .composition import TOOLS as COMPOSED, obj
from .core import Error, canonical, read_json
from .mcp import validate
from .observations import compact
from .presentation import present

STRING={'type':'string','minLength':1}
ARGS={'type':'object','additionalProperties':True}
VIEW={'enum':['compact','summary','full']}
FIELDS={'type':'array','items':STRING,'minItems':1,'maxItems':32,'uniqueItems':True}

CAPABILITIES_SCHEMA=obj({'query':{'type':'string'},'tool':STRING})
READ_SCHEMA=obj({'tool':STRING,'args':ARGS,'view':VIEW,'fields':FIELDS,'row_fields':FIELDS,
                 'limit':{'type':'integer','minimum':1}},['tool'])
ACT_SCHEMA=obj({'tool':STRING,'args':ARGS,'view':VIEW},['tool'])
WAIT_SCHEMA=obj({'maxSeconds':{'type':'integer','minimum':5,'maximum':600},
                 'maxGameTicks':{'type':'integer','minimum':1},'maxGameSeconds':{'type':'number','minimum':0},
                 'maxGameHours':{'type':'number','minimum':0},'maxGameDays':{'type':'number','minimum':0},
                 'force':{'type':'boolean'},'view':VIEW})
RETRIEVE_SCHEMA=obj({'observation':STRING,'tool':STRING,'entity':STRING,'ref':STRING,
                     'view':VIEW,'fields':FIELDS})

TOOLS={
 'rw_capabilities':{'name':'rw_capabilities','description':
  'Find upstream RimMolt tools without loading the whole catalog. query returns ranked name+one-line matches; '
  'tool returns that one exact schema and its default effect. Names found here are used as the tool argument to '
  'rw_read/rw_act. Offline catalog lookup; contacts no game and grants no permission.',
  'inputSchema':CAPABILITIES_SCHEMA,'annotations':{'readOnlyHint':True}},
 'rw_read':{'name':'rw_read','description':
  'Run one read-only RimMolt tool by name and get a compact result. Filter at the source: '
  'list_things takes category/defName/faction/nearId+radius/limit/summary; get_area takes minX,maxX,minZ,maxZ bounds/thing/summary; '
  'get_pawn takes tab and detail. fields selects top-level keys, row_fields selects columns within row lists; '
  'warnings, risks and changed fields are always kept. Repeat reads of one scope return only what changed. '
  'Mutating arguments are refused here. Evidence is stored whole; rw_retrieve recovers it.',
  'inputSchema':READ_SCHEMA,'annotations':{'readOnlyHint':True}},
 'rw_act':{'name':'rw_act','description':
  'Run one effectful RimMolt tool by name. Ordinary game orders only; time advancement belongs to rw_wait and '
  'reads to rw_read. set_speed with action pause is the ordinary pause and stays available while a request is unresolved. '
  'For reviewed multi-job pawn sequences, order_pawn queue=true appends a Shift-click-style job after the current queue. '
  'An accepted order is a receipt, not arrival, treatment, delivery or completed construction; verify the actual result.',
  'inputSchema':ACT_SCHEMA,'annotations':{'readOnlyHint':False}},
 'rw_wait':{'name':'rw_wait','description':
  'Advance supervised time until a notable event, then return its cause paused. Prefer this over repeated polling. '
  'Choose a horizon: maxSeconds is the wall budget (5-600), maxGameTicks/maxGameSeconds/maxGameHours/maxGameDays the game-time limit, '
  'clamped to the earliest recorded deadline. Inspect the real event and pausedAfter; a wait ending early may have hit its game-time limit.',
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
        'list_world_objects':'mapIndex, limit where offered'}


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
    from .capabilities import discover
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
        entry.update(truncated=bool(body.get('truncated')),refs_minted=len(body.get('refs') or {}),
                     projected=bool(body.get('projected')),omitted=len(body.get('omitted_keys') or []),
                     unchanged=bool(body.get('unchanged')),
                     changed_fields=len(body.get('changed_fields') or []))
        if body.get('truncated'): entry['reason']=body.get('reason')
    append_json(control.campaign.path/'telemetry.jsonl',entry)
    return body


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
        # pause is injected, never offered: wait_arguments hard-requires 'always'.
        tool='wait_for_event'
        call_args=dict({k:v for k,v in args.items() if k!='view'},pause='always')
        gate(classify(control,tool,call_args),tool,'wait')
        value=control.call(token,tool,call_args,setup=setup,driver='facade_wait')
    else:
        tool,call_args=args['tool'],args.get('args',{})
        want='read' if name=='rw_read' else 'act'
        if want=='act' and tool=='set_speed' and call_args=={'action':'pause'}:
            guard=control.ensure_paused(token,emergency=True)
            if not guard.get('confirmed'): raise Error('Ordinary pause could not be confirmed: '+str(guard))
            value={'id':guard['evidence']}
        else:
            gate(classify(control,tool,call_args),tool,want)
            value=control.call(token,tool,call_args,setup=setup,driver='facade_'+want)
    if observed: observed(value['id'])
    obs=control.campaign.observation(value['id'])
    if view!='compact':
        return journal(control,name,shape(control.campaign,obs,view),started,tool=tool,view=view)
    # present() shapes the ingest delta view, which carries risks and changed fields;
    # the stored observation alone has neither.
    body=present(value if 'completeness' in value else compact(obs))
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
    """Connection-scoped substitution table. Never survives a reconnect or reset."""
    def __init__(self):
        self.by_value={};self.values_by_id={};self.reset_at=None

    def sync(self, campaign):
        """Any presentation reset invalidates every outstanding reference."""
        current=campaign.meta.get('presentation_reset_at')
        if current!=self.reset_at:
            self.by_value.clear();self.values_by_id.clear();self.reset_at=current

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
    body=present(compact(obs))
    if fields:
        body,omitted=project(body,fields)
        if omitted: body['omitted_keys']=omitted
    return body
