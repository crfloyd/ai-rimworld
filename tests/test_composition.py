import copy
import io
import json
from unittest.mock import patch
from test_system import ControlFixture, CATALOG
from tools.rimworld.core import Error, read_json, atomic_json
from tools.rimworld.composition import Composer, delivered, TOOLS, predicate
from tools.rimworld.session import Session, serve
from tools.rimworld.mcp import Uncertain
from tools.rimworld.continuity import runtime_snapshot
from tools.rimworld.cli import parser, run


class CompositionTests(ControlFixture):
    def setUp(self):
        super().setUp()
        self.base=len(self.calls)

    def query(self, **args):
        return {'key':'pawn','tool':'get_pawn','args':{'id':'p',**args}}

    def spec(self, **extra):
        return {'queries':[self.query()],**extra}

    def guard(self, **extra):
        return self.spec(when=[{'source':'pawn','path':'/mood','op':'lt','value':20}],
            then={'tool':'order_pawn','args':{'id':'p','command':'Drink tea'}},**extra)

    def execute(self, spec, name='rw_observe', ack=True):
        r=Composer(self.control,self.token).execute(name,dict(spec,provenance=True))
        if ack:delivered(self.control,self.token,r['composition'])
        return r

    def add_tools(self,*names):
        from pathlib import Path
        real=read_json(Path(__file__).resolve().parents[1]/'api/catalog.json')['tools']
        path=self.camp.path/'raw/catalog.json';cat=read_json(path)
        for n in names:cat['tools'][n]=real[n]
        atomic_json(path,cat)

    def test_pawn_tabs_group_full_facts_and_no_unrequested_fetch(self):
        facts=[{'id':'p','mood':80,'newField':{'false':False,'zero':0}}, {'needs':[{'label':'Novel need','percent':24}]}]
        self.responses.extend(facts)
        r=self.execute({'queries':[{'key':'reed','preset':'pawn','id':'p','include':['summary','needs']}]})
        self.assertEqual(list(r['sections']),['reed.summary','reed.needs'])
        self.assertEqual([x['data'] for x in r['sections'].values()],facts)
        self.assertEqual([c['arguments'] for c in self.calls[self.base:]],[{'id':'p'},{'id':'p','tab':'needs'}])
        self.assertFalse(self.camp._actions())
        self.assertFalse((self.control.path/'composition.json').exists())
        for sec in r['sections'].values():self.assertTrue(self.camp.has_observation(sec['source']['observation']))

    def test_production_maps_only_real_tools_without_invented_availability(self):
        self.add_tools('inspect_thing','list_bills','list_recipes','get_resources')
        facts=[{'id':'s','fuel':0},{'bills':[]},{'recipes':[]},{'resources':[]},{'options':[{'label':'Cannot cook: Missing food','disabled':True}]}]
        self.responses.extend(facts)
        r=self.execute({'queries':[{'key':'stove','preset':'production','id':'s','worker_id':'p',
            'include':['station','bills','recipes','resources','work_options']}]})
        self.assertEqual([c['name'] for c in self.calls[self.base:]],['inspect_thing','list_bills','list_recipes','get_resources','order_pawn'])
        self.assertEqual(r['sections']['stove.work_options']['data'],facts[-1])
        self.assertNotIn('ready',r)

    def test_preflight_all_reads_no_partial_dispatch_on_invalid_spec(self):
        bad=[{'queries':[self.query(),{'key':'bad','tool':'order_pawn','args':{'id':'p','command':'Move'}}]},
             {'queries':[self.query(),self.query()]},
             {'queries':[{'key':'p','preset':'pawn','id':'p','include':['work_priorities']}]},
             {'queries':[{'key':'s','preset':'production','id':'s','include':['work_options']}]},
             {'queries':[{'key':'p','preset':'pawn','id':'p','tool':'get_pawn'}]},
             {'queries':[{'key':'p','tool':'missing'}]}]
        for spec in bad:
            with self.assertRaises(Error):self.execute(spec)
        self.assertEqual(len(self.calls),self.base)
        self.assertFalse((self.control.path/'composition.json').exists())

    def test_partial_read_returns_missing_sections_not_silent_success(self):
        self.responses.append({'ok':False,'error':'Pawn unavailable'})
        r=self.execute({'queries':[self.query(),{'key':'second','tool':'get_pawn','args':{'id':'q'}}]})
        self.assertEqual(r['stopped']['not_run'],['second']);self.assertEqual(len(self.calls)-self.base,1)
        self.assertEqual(r['sections']['pawn']['data']['error'],'Pawn unavailable')

    def test_guard_true_executes_once_and_verifies_without_claiming_outcome(self):
        self.responses.extend([{'id':'p','mood':10,'_paused':True},{'ok':True,'executed':True}, {'id':'p','mood':10,'_paused':True}])
        r=self.execute(self.guard(verify=[self.query()]),'rw_guard')
        self.assertTrue(r['condition']);self.assertEqual(r['selected_branch'],'then')
        self.assertEqual(r['action_status'],'receipt_only');self.assertIn('pawn',r['verification'])
        self.assertEqual(len(self.calls)-self.base,3);self.assertFalse(self.camp._actions())

    def test_known_false_only_uses_explicit_otherwise(self):
        self.responses.extend([{'id':'p','mood':70,'_paused':True},{'ok':True}])
        r=self.execute(self.guard(otherwise={'tool':'order_pawn','args':{'id':'p','command':'Work'}}),'rw_guard')
        self.assertEqual(r['selected_branch'],'otherwise');self.assertEqual(self.calls[-1]['arguments']['command'],'Work')
        self.responses.append({'id':'p','mood':70,'_paused':True})
        r=self.execute(self.guard(),'rw_guard');self.assertEqual(r['action_status'],'not_requested')

    def test_missing_mistyped_nonfinite_or_unpaused_is_unknown_not_else(self):
        for data in [{'id':'p','_paused':True},{'id':'p','mood':False,'_paused':True},
                     {'id':'p','mood':10,'_paused':False},{'id':'p','mood':10}]:
            before=len(self.calls);self.responses.append(data)
            r=self.execute(self.guard(otherwise={'tool':'order_pawn','args':{'id':'p','command':'Else'}}),'rw_guard')
            self.assertEqual(r['condition'],'unknown');self.assertIsNone(r['selected_branch']);self.assertEqual(len(self.calls)-before,1)
        self.assertIsNone(predicate({'mood':float('nan')},{'path':'/mood','op':'ne','value':1.0}))
        self.assertIsNone(predicate({'mood':False},{'path':'/mood','op':'eq','value':0}))

    def test_exact_unique_array_selector_for_toggle_or_menu(self):
        cond={'source':'pawn','path':'/actions','match':{'label':'Medical'},'field':'/active','op':'eq','value':True}
        for actions,wanted in [([{'label':'Medical','active':True}],True),
                               ([{'label':'Medical','active':False}],False),
                               ([{'label':'Medical','active':True}]*2,'unknown'),([], 'unknown')]:
            self.responses.append({'id':'p','_paused':True,'actions':actions})
            if wanted is True:self.responses.append({'ok':True})
            spec=self.guard();spec['when']=[cond];r=self.execute(spec,'rw_guard')
            self.assertEqual(r['condition'],wanted)

    def test_new_warning_or_notification_suppresses_both_branches(self):
        for name in ['_threatWarning','_notifications','_protocolNotifications','warning','_delta']:
            self.responses.append({'id':'p','mood':10,'_paused':True,name:{'novel':1}});before=len(self.calls)
            r=self.execute(self.guard(otherwise={'tool':'order_pawn','args':{'id':'p','command':'Else'}}),'rw_guard')
            self.assertEqual(r['condition'],'unknown');self.assertEqual(len(self.calls)-before,1)

    def test_partial_bundle_never_becomes_false_clearance(self):
        d={'loaded':True,'colonyName':'Fixture Colony','_paused':True,
           'bundled':{'list_fires':{'fires':[],'truncated':True}}}
        self.responses.append(d)
        spec=self.guard();spec['queries']=[{'key':'status','tool':'get_status'}]
        spec['when']=[{'source':'status','path':'/bundled/list_fires/fires','op':'eq','value':[]}]
        r=self.execute(spec,'rw_guard')
        self.assertEqual(r['condition'],'unknown');self.assertEqual(len(self.calls)-self.base,1)
        self.assertEqual(r['sections']['status']['bundle_coverage'][0]['completeness'],'partial')

    def test_identity_change_stops_remaining_reads_and_action(self):
        self.responses.append({'loaded':True,'colonyName':'Other','_paused':True})
        spec=self.guard();spec['queries']=[{'key':'status','tool':'get_status'},self.query()]
        spec['when']=[{'source':'status','path':'/loaded','op':'eq','value':True}]
        r=self.execute(spec,'rw_guard');self.assertEqual(r['condition'],'unknown')
        self.assertIn('identity_mismatch',r['sections']['status']['control'])
        self.assertEqual(r['stopped']['not_run'],['pawn']);self.assertIsNone(self.camp.meta['binding'])

    def test_action_and_verification_preflight_before_reads(self):
        for branch in [{'tool':'wait_for_event','args':{'pause':'always'}}, {'tool':'load_game'},
                       {'tool':'order_pawn','args':{'id':'p','bogus':True}}]:
            spec=self.guard();spec['then']=branch
            with self.assertRaises(Error):self.execute(spec,'rw_guard')
        spec=self.guard(verify=[{'key':'x','tool':'missing'}])
        with self.assertRaises(Error):self.execute(spec,'rw_guard')
        self.assertEqual(len(self.calls),self.base)

    def test_unknown_branch_receipt_stops_verification(self):
        self.responses.extend([{'id':'p','mood':10,'_paused':True}, {'ok':False,'error':'Target moved'}])
        r=self.execute(self.guard(verify=[self.query()]),'rw_guard')
        self.assertEqual(r['stopped']['not_run'],['pawn']);self.assertEqual(len(self.calls)-self.base,2)

    def raw_client(self,payload):
        class Client:
            session={}
            def rpc(self,*args):return {'result':payload}
        return Client()

    def test_duplicate_keys_and_nonstandard_numbers_preserve_evidence_but_cannot_act(self):
        for body in ['{"id":"p","mood":100,"mood":10,"_paused":true}',
                     '{"id":"p","mood":10,"x":{"a":1,"a":2},"_paused":true}',
                     '{"id":"p","mood":10,"x":NaN,"_paused":true}',
                     '{"id":"p","mood":10,"x":1e999,"_paused":true}']:
            client=self.raw_client({'content':[{'type':'text','text':body}]})
            with patch.object(self.control,'client_factory',return_value=client):r=self.execute(self.guard(),'rw_guard')
            self.assertEqual(r['condition'],'unknown');self.assertIn('unusable_json_blocks',r['sections']['pawn']['metadata'])
            obs=self.camp.observation(r['sections']['pawn']['source']['observation'])
            self.assertEqual(read_json(self.camp.path/obs['raw'])['payload']['result']['content'][0]['text'],body)

    def test_media_extra_text_and_unknown_fields_retained(self):
        payload={'content':[{'type':'text','text':'{"id":"p","novel":false,"zero":0}','annotations':{'x':1}},
                            {'type':'image','mimeType':'image/png','data':'original'},
                            {'type':'text','text':'extra warning text'}], 'futureProperty':{'a':2}}
        with patch.object(self.control,'client_factory',return_value=self.raw_client(payload)):
            r=self.execute(self.spec())
        s=r['sections']['pawn'];self.assertEqual(s['data'],{'id':'p','novel':False,'zero':0})
        self.assertEqual(s['content'],payload['content'][1:]);self.assertEqual(s['result_properties']['futureProperty'],{'a':2})
        self.assertEqual(s['text_properties']['annotations'],{'x':1})

    def test_pending_marker_covers_between_calls_and_reconciliation(self):
        self.responses.append({'id':'p','mood':10,'_paused':True})
        original=self.control.call
        def interrupted(token,tool,args,**kwargs):
            if tool=='order_pawn':raise KeyboardInterrupt('Between read and mutation')
            return original(token,tool,args,**kwargs)
        with patch.object(self.control,'call',side_effect=interrupted),self.assertRaises(KeyboardInterrupt):
            self.execute(self.guard(),'rw_guard')
        c=self.control.inspect()['composition'];self.assertEqual(c['status'],'unknown')
        self.control.attach_handle(c['request_id'],'terminal','actual-handle')
        self.assertEqual(self.control.inspect()['composition']['orchestrator_handle']['value'],'actual-handle')
        self.assertIn('composition',runtime_snapshot(self.camp))
        with self.assertRaises(Error):self.control.call(self.token,'get_pawn',{'id':'p'})
        with self.assertRaises(Error):self.control.release(self.token,'Not safe')
        self.control.reconcile(self.token,'original error, no mutation dispatched','Verified terminal test process',True)
        self.assertFalse((self.control.path/'composition.json').exists())

    def test_uncertain_action_keeps_subrequest_and_composition_no_replay(self):
        self.responses.extend([{'id':'p','mood':10,'_paused':True},Uncertain('Lost action response')])
        with self.assertRaises(Uncertain):self.execute(self.guard(),'rw_guard')
        self.assertEqual(self.control.inspect()['pending']['tool'],'order_pawn')
        self.assertEqual(self.control.inspect()['composition']['status'],'unknown')
        before=len(self.calls)
        with self.assertRaises(Error):self.execute(self.guard(),'rw_guard')
        self.assertEqual(before,len(self.calls))

    def test_ready_marker_cleared_only_after_delivery_and_no_replay(self):
        self.responses.append({'id':'p'})
        r=self.execute(self.spec(),ack=False)
        self.assertEqual(self.control.inspect()['composition']['status'],'ready_to_deliver')
        with self.assertRaises(Error):self.control.call(self.token,'get_pawn',{'id':'p'})
        delivered(self.control,self.token,r['composition'])
        self.assertFalse((self.control.path/'composition.json').exists())

    def test_session_serves_composition_then_ordinary_call(self):
        req=lambda i,n,a:{'jsonrpc':'2.0','id':i,'method':'tools/call','params':{'name':n,'arguments':a}}
        self.responses.extend([{'id':'p','novel':9},{'id':'p'}]);out=io.StringIO()
        with patch.object(self.control,'ensure_paused',return_value={'confirmed':True}):
            serve(self.control,self.token,io.StringIO(json.dumps(req(1,'rw_observe',self.spec()))+'\n'+json.dumps(req(2,'get_pawn',{'id':'p'}))+'\n'),out,expose_upstream=True)
        replies=[json.loads(l) for l in out.getvalue().splitlines()];self.assertIn('result',replies[1])
        self.assertEqual(json.loads(replies[0]['result']['content'][0]['text'])['sections']['pawn']['data']['novel'],9)

    def test_broken_delivery_after_action_preserves_marker_and_blocks(self):
        self.responses.extend([{'id':'p','mood':10,'_paused':True},{'ok':True}])
        req={'jsonrpc':'2.0','id':1,'method':'tools/call','params':{'name':'rw_guard','arguments':self.guard()}}
        class Broken(io.StringIO):
            def write(self,value):raise BrokenPipeError('Lost consumer')
        with patch.object(self.control,'ensure_paused',return_value={'confirmed':True}),self.assertRaises(BrokenPipeError):
            serve(self.control,self.token,io.StringIO(json.dumps(req)+'\n'),Broken())
        self.assertIn('action_evidence',self.control.inspect()['composition'])
        with self.assertRaises(Error):self.control.call(self.token,'get_pawn',{'id':'p'})

    def test_cli_and_mcp_share_exact_expansion(self):
        self.responses.append({'id':'p','novel':True})
        args=parser().parse_args(['--root',str(self.root),'--run','example','observe','--json',json.dumps(self.spec()),'--token',self.token])
        with patch('tools.rimworld.cli.Control',return_value=self.control):r=run(args)
        self.assertEqual(r['sections']['pawn']['data']['novel'],True)
        delivered(self.control,self.token,r['composition'])

    def test_default_output_keeps_data_but_moves_provenance_to_manifest(self):
        data={'id':'obs-game-field','completeness':'novel','new':{'false':False,'zero':0}}
        self.responses.append(data)
        r=Composer(self.control,self.token).execute('rw_observe',self.spec())
        self.assertEqual(r['sections']['pawn']['data'],data)
        self.assertNotIn('source',r['sections']['pawn'])
        manifest=read_json(self.camp.path/'reference/compositions'/(r['composition']+'.json'))
        self.assertTrue(self.camp.has_observation(manifest['observations'][0]['id']))
        self.assertIn('captured_at',manifest['observations'][0]['source'])
        delivered(self.control,self.token,r['composition'])

    def test_error_response_does_not_acknowledge_failed_composition_delivery(self):
        # Valid first game JSON but invalid nonfinite unknown result property: final JSON encoding fails.
        payload={'content':[{'type':'text','text':'{"id":"p","_paused":true}'}], 'future':float('inf')}
        req={'jsonrpc':'2.0','id':1,'method':'tools/call','params':{'name':'rw_observe','arguments':self.spec()}}
        with patch.object(self.control,'client_factory',return_value=self.raw_client(payload)):
            r=Session(self.control,self.token).handle(req)
        self.assertIn('error',r)
        self.assertEqual(self.control.inspect()['composition']['status'],'unknown')
        self.assertTrue(r['error']['data']['pending'])

    def test_universal_cli_call_reaches_local_tool_without_upstream_dispatch(self):
        self.responses.append({'id':'p'})
        args=parser().parse_args(['--root',str(self.root),'--run','example','call','rw_observe','--args',json.dumps(self.spec()),'--token',self.token])
        with patch('tools.rimworld.cli.Control',return_value=self.control):r=run(args)
        self.assertEqual([c['name'] for c in self.calls[self.base:]],['get_pawn'])
        delivered(self.control,self.token,r['composition'])

    def test_guard_total_read_budget_includes_verification(self):
        spec=self.guard(verify=[{'key':'v'+str(i),'tool':'get_pawn','args':{'id':'p'}} for i in range(17)])
        spec['queries'] += [{'key':'q'+str(i),'tool':'get_pawn','args':{'id':'p'}} for i in range(15)]
        with self.assertRaises(Error):self.execute(spec,'rw_guard')
        self.assertEqual(len(self.calls),self.base)

    def test_session_composition_tags_subcalls_and_records_public_payload(self):
        session=Session(self.control,self.token)
        self.responses.append({'id':'p','mood':50})
        request={'jsonrpc':'2.0','id':7,'method':'tools/call','params':{
            'name':'rw_observe','arguments':self.spec()}}
        response=session.handle(request)
        self.assertIn('result',response)
        upstream=[json.loads(l) for l in (self.camp.path/'telemetry.jsonl').read_text().splitlines()]
        self.assertEqual(upstream[-1]['driver'],'facade_observe')
        public=json.loads((self.camp.path/'facade-telemetry.jsonl').read_text().splitlines()[-1])
        text=response['result']['content'][0]['text']
        self.assertEqual((public['public_tool'],public['view'],public['composed_queries']),('rw_observe','composed',1))
        self.assertEqual(public['response_bytes'],len(text.encode()))
