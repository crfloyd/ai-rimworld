"""Persistent standard MCP transport. No plans, polling policy, or game strategy."""
import copy
import json
import os
import sys

from . import __version__
from .core import Error, append_json, atomic_json, canonical, lock, now, read_json
from .mcp import PROTOCOLS
from .responses import visible_result
from .composition import TOOLS, Composer, delivered
from . import facade
from .facade import reserved


class Session:
    def __init__(self, control, token, setup=False, expose_upstream=False):
        control._owner(token)
        control._no_pending()
        self.control, self.token, self.setup = control, token, setup
        self.expose_upstream = expose_upstream or control.campaign.meta.get('expose_upstream_tools') is True
        self.memo = facade.Memo()
        self.last_observation = None
        self.last_composition = None

    def record_public_call(self, request_id, name, args, status, text=None, error=None):
        """Record the exact local-tool payload offered to the MCP consumer.

        This complements upstream Control.call telemetry: offline facade tools have
        no upstream request, while compositions have several. Telemetry must never
        turn an otherwise deliverable gameplay response into an uncertain call.
        """
        row={'at':now(),'version':__version__,'session_id':self.control.campaign.meta.get('session_id'),
             'request_id':request_id,'public_tool':name,'status':status,
             'view':args.get('view','compact') if name not in TOOLS else 'composed',
             'response_bytes':len(text.encode()) if text is not None else None,
             'response_bytes_basis':'Exact UTF-8 bytes of the single model-facing text content; excludes JSON-RPC framing.'}
        if name in ('rw_read','rw_act'):
            row['upstream_tool']=args.get('tool')
            if name=='rw_read':
                row['delta_requested']=args.get('delta') is True
                row['delta_base']=args.get('since')
            if name=='rw_act' and args.get('actions') is not None:row['batch_actions']=len(args['actions'])
        elif name=='rw_capabilities':
            row['capability_query']=args.get('query');row['capability_tool']=args.get('tool')
            row['capability_domain']=args.get('domain');row['capability_workflow']=args.get('workflow')
        elif name=='rw_retrieve':
            row['retrieve_selector']=next((k for k in ('observation','tool','entity','ref') if args.get(k) is not None),None)
            row['retrieve_value']=args.get(row['retrieve_selector']) if row['retrieve_selector'] else None
        elif name in TOOLS:
            row['composed_queries']=len(args.get('queries') or [])
            row['composed_verify']=len(args.get('verify') or [])
            row['decision_queries']=sum(q.get('preset')=='decision' for q in args.get('queries') or [])
            row['reuse_requested']=args.get('reuse') is True
        if error is not None: row['error']=str(error)
        try:
            # Two telemetry files sit side by side with different schemas. Name the
            # stream in every row so a query that finds nothing can tell an empty
            # result from the wrong file.
            append_json(self.control.campaign.path/'facade-telemetry.jsonl',
                        dict(row,stream='public_tool_calls'))
        except Exception:
            # Evidence and the gameplay response are more important than optional
            # measurement. A missing row is detectable against the MCP transcript.
            pass

    def delivery_failed(self, request, error):
        """A known response lost locally must not become a retryable mutation."""
        with lock(self.control.path/'operation.lock'):
            self.control._owner(self.token)
            compound = self.control.path/'composition.json'
            if compound.exists():
                record=read_json(compound)
                record.update(status='unknown',error='Local response delivery failed: '+str(error))
                atomic_json(compound,record)
                atomic_json(self.control.campaign.path/'reference/compositions'/(record['request_id']+'.json'),record)
            path = self.control.path/'pending.json'
            if self.last_observation is not None and not path.exists():
                atomic_json(path, {'request_id':'delivery-'+str(request.get('id')),
                    'pid':os.getpid(),'status':'unknown','evidence':self.last_observation,
                    'tool':request.get('params',{}).get('name'),'started_at':now(),
                    'error':'Local response delivery failed: '+str(error)})

    def handle(self, request):
        self.last_observation = None
        self.last_composition = None
        public_call=None;public_recorded=False
        if not isinstance(request,dict) or request.get('jsonrpc') != '2.0' or not isinstance(request.get('method'),str):
            return {'jsonrpc':'2.0','id':None,'error':{'code':-32600,'message':'Expected one JSON-RPC2.0 request.'}}
        # Notifications must not execute a game operation without a reply ID.
        if 'id' not in request:
            return None
        rid, method = request['id'], request['method']
        params=request.get('params',{})
        if not isinstance(params,dict):
            return {'jsonrpc':'2.0','id':rid,'error':{'code':-32602,'message':'params must be an object.'}}
        try:
            if method == 'initialize':
                version=params.get('protocolVersion')
                result={'protocolVersion':version if version in PROTOCOLS else PROTOCOLS[0],
                        'capabilities':{'tools':{}},'serverInfo':{'name':'ai-rimworld','version':__version__}}
            elif method == 'ping': result={}
            elif method == 'tools/list':
                if (self.control.path/'catalog-stale.json').exists(): raise Error('Server catalog changed; close this session, connect and rebind before discovery.')
                catalog=read_json(self.control.campaign.path/'raw/catalog.json')
                reserved(catalog)
                served=facade.local()
                tools=list(served.values())
                if self.expose_upstream: tools=list(catalog['tools'].values())+tools
                result={'tools':tools,'_meta':{'captured_at':catalog['captured_at'],'local_tools':list(served),
                        'local_version':__version__,'upstream_tools':len(catalog['tools']),
                        'upstream_exposed':self.expose_upstream,'discovery':'rw_capabilities'}}
            elif method == 'tools/call':
                name, args=params.get('name'),params.get('arguments',{})
                if not isinstance(name,str) or not isinstance(args,dict): raise Error('Use a tool name and arguments object.')
                if name in TOOLS:
                    public_call=(name,args)
                    reserved(read_json(self.control.campaign.path/'raw/catalog.json'))
                    self.memo.sync(self.control.campaign)
                    def observed(obs_id):
                        self.last_observation=obs_id;self.memo.remember(self.control.campaign,obs_id)
                    value=Composer(self.control,self.token,observed,driver='facade_'+name.removeprefix('rw_'),memo=self.memo).execute(name,args)
                    self.last_composition=value['composition']
                    text=json.dumps(value,ensure_ascii=False,allow_nan=False)
                    self.record_public_call(rid,name,args,'ok',text=text);public_recorded=True
                    return {'jsonrpc':'2.0','id':rid,'result':{'content':[{'type':'text','text':text}]}}
                if name in facade.TOOLS:
                    public_call=(name,args)
                    reserved(read_json(self.control.campaign.path/'raw/catalog.json'))
                    def observed(obs_id):
                        self.last_observation=obs_id;self.memo.remember(self.control.campaign,obs_id)
                    value=facade.dispatch(self.control,self.token,name,args,setup=self.setup,memo=self.memo,observed=observed)
                    if isinstance(value,dict) and value.get('composition'):
                        self.last_composition=value['composition']
                    text=json.dumps(value,ensure_ascii=False,allow_nan=False)
                    self.record_public_call(rid,name,args,'ok',text=text);public_recorded=True
                    return {'jsonrpc':'2.0','id':rid,'result':{'content':[{'type':'text','text':text}]}}
                if not self.expose_upstream:
                    raise Error('Upstream tool names are not served directly; use rw_read, rw_act or rw_wait, and rw_capabilities to find a name.')
                pending_pause = any((self.control.path/p).exists() for p in ('pending.json','composition.json'))
                if name == 'set_speed' and args == {'action':'pause'}:
                    guard=self.control.ensure_paused(self.token,emergency=True)
                    if not guard.get('confirmed'): raise Error('Ordinary pause could not be confirmed: '+str(guard))
                    value={'id':guard['evidence']}
                else:
                    value=self.control.call(self.token,name,args,setup=self.setup)
                self.last_observation=value['id']
                obs=self.control.campaign.observation(value['id'])
                result, metadata=visible_result(self.control.campaign,obs)
                if pending_pause: metadata['original_request_still_unresolved']=True
                if obs['completeness']!='known': metadata.update(completeness=obs['completeness'],missing=obs['missing'])
                for key in ('identity_mismatch','pause_guard','wait_budget'):
                    if key in value: metadata[key]=value[key]
                result.setdefault('content',[]).append({'type':'text','text':json.dumps(metadata)})
            else:
                return {'jsonrpc':'2.0','id':rid,'error':{'code':-32601,'message':'Unknown MCP method.'}}
            return {'jsonrpc':'2.0','id':rid,'result':result}
        except BaseException as exc:
            self.last_composition=None
            if public_call is not None and not public_recorded:
                self.record_public_call(rid,public_call[0],public_call[1],'error',error=exc)
            self.delivery_failed(request,exc)
            if not isinstance(exc,Exception): raise
            return {'jsonrpc':'2.0','id':rid,'error':{'code':-32000,'message':str(exc),
                'data':{'pending':any((self.control.path/p).exists() for p in ('pending.json','composition.json'))}}}


def serve(control, token, input_stream=None, output_stream=None, setup=False, expose_upstream=False):
    input_stream=input_stream or sys.stdin
    output_stream=output_stream or sys.stdout
    session=Session(control,token,setup=setup,expose_upstream=expose_upstream)
    terminal=None
    if input_stream.isatty():
        import termios
        terminal=termios.tcgetattr(input_stream.fileno());attrs=copy.deepcopy(terminal)
        attrs[3] &= ~termios.ECHO
        termios.tcsetattr(input_stream.fileno(),termios.TCSANOW,attrs)
    try:
        for line in input_stream:
            session.last_observation = None
            request = {}
            try:
                try: request=json.loads(line)
                except ValueError:
                    response={'jsonrpc':'2.0','id':None,'error':{'code':-32700,'message':'Invalid JSON.'}}
                else: response=session.handle(request)
                if response is not None:
                    output_stream.write(json.dumps(response,ensure_ascii=False,allow_nan=False)+'\n')
                    output_stream.flush()
                    if session.last_composition:
                        delivered(control,token,session.last_composition)
                        session.last_composition=None
            except BaseException as exc:
                session.delivery_failed(request,exc)
                raise
    finally:
        # EOF is transport closure, not a gameplay result or cancellation.
        try:
            pause=control.ensure_paused(token,emergency=True)
            if not pause.get('confirmed'):
                atomic_json(control.path/'pause-uncertain.json',{'at':now(),'reason':'Session closed without confirmed pause','detail':pause})
                raise Error('Session closed without a confirmed pause; review control before further calls.')
        finally:
            if terminal is not None:
                termios.tcsetattr(input_stream.fileno(),termios.TCSANOW,terminal)
