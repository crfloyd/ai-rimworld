"""Persistent standard MCP transport. No plans, polling policy, or game strategy."""
import copy
import json
import os
import sys

from . import __version__
from .core import Error, atomic_json, lock, now, read_json
from .mcp import PROTOCOLS
from .observations import visible_data


class Session:
    def __init__(self, control, token, setup=False):
        control._owner(token)
        control._no_pending()
        self.control, self.token, self.setup = control, token, setup
        self.last_observation = None

    def delivery_failed(self, request, error):
        """A known response lost locally must not become a retryable mutation."""
        if self.last_observation is None:
            return
        with lock(self.control.path/'operation.lock'):
            self.control._owner(self.token)
            path = self.control.path/'pending.json'
            if not path.exists():
                atomic_json(path, {'request_id':'delivery-'+str(request.get('id')),
                    'pid':os.getpid(),'status':'unknown','evidence':self.last_observation,
                    'tool':request.get('params',{}).get('name'),'started_at':now(),
                    'error':'Local response delivery failed: '+str(error)})

    def handle(self, request):
        self.last_observation = None
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
                result={'tools':list(catalog['tools'].values()),'_meta':{'captured_at':catalog['captured_at']}}
            elif method == 'tools/call':
                name, args=params.get('name'),params.get('arguments',{})
                if not isinstance(name,str) or not isinstance(args,dict): raise Error('Use a tool name and arguments object.')
                pending_pause = (self.control.path/'pending.json').exists()
                if name == 'set_speed' and args == {'action':'pause'}:
                    guard=self.control.ensure_paused(self.token,emergency=True)
                    if not guard.get('confirmed'): raise Error('Ordinary pause could not be confirmed: '+str(guard))
                    value={'id':guard['evidence']}
                else:
                    value=self.control.call(self.token,name,args,setup=self.setup)
                self.last_observation=value['id']
                obs=self.control.campaign.observation(value['id'])
                raw=read_json(self.control.campaign.path/obs['raw'])['payload']
                result=copy.deepcopy(raw.get('result',raw))
                if not isinstance(result,dict): raise Error('Unexpected MCP result shape; original evidence retained.')
                # Forward all content/media/unknown properties. Only the existing
                # explicit hidden-AI visibility boundary changes game text.
                exclusions=[]
                for index, block in enumerate(result.get('content',[])):
                    if block.get('type') != 'text': continue
                    try: data=json.loads(block['text'])
                    except (ValueError,TypeError): continue
                    data, excluded=visible_data(data,name)
                    if excluded:
                        block['text']=json.dumps(data,ensure_ascii=False)
                        exclusions.extend('content/'+str(index)+'/text/'+path for path in excluded)
                if 'structuredContent' in result:
                    result['structuredContent'], excluded=visible_data(result['structuredContent'],name)
                    exclusions.extend('structuredContent/'+path for path in excluded)
                metadata={'_evidence':value['id']}
                if raw.get('_transportNotifications'):
                    notifications, excluded=visible_data(raw['_transportNotifications'],name)
                    metadata['_transportNotifications']=notifications
                    exclusions.extend('_transportNotifications/'+path for path in excluded)
                if exclusions: metadata['visibility_exclusions']={'reason':'Hostile AI targeting is not player-visible','paths':exclusions}
                if pending_pause: metadata['original_request_still_unresolved']=True
                if obs['completeness']!='known': metadata.update(completeness=obs['completeness'],missing=obs['missing'])
                for key in ('identity_mismatch','pause_guard','wait_budget'):
                    if key in value: metadata[key]=value[key]
                result.setdefault('content',[]).append({'type':'text','text':json.dumps(metadata)})
            else:
                return {'jsonrpc':'2.0','id':rid,'error':{'code':-32601,'message':'Unknown MCP method.'}}
            return {'jsonrpc':'2.0','id':rid,'result':result}
        except BaseException as exc:
            self.delivery_failed(request,exc)
            if not isinstance(exc,Exception): raise
            return {'jsonrpc':'2.0','id':rid,'error':{'code':-32000,'message':str(exc),
                'data':{'pending':(self.control.path/'pending.json').exists()}}}


def serve(control, token, input_stream=None, output_stream=None, setup=False):
    input_stream=input_stream or sys.stdin
    output_stream=output_stream or sys.stdout
    session=Session(control,token,setup=setup)
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
