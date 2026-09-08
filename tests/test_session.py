import io,json
from unittest.mock import patch
from test_system import ControlFixture,CATALOG
from tools.rimworld.core import Error,read_json,atomic_json
from tools.rimworld.mcp import Uncertain
from tools.rimworld.session import Session,serve

class PersistentMCP(ControlFixture):
    def setUp(self):
        super().setUp();self.session=Session(self.control,self.token)
    def req(self,name,args=None,rid=1):
        return {'jsonrpc':'2.0','id':rid,'method':'tools/call','params':{'name':name,'arguments':args or {}}}
    def test_initialize_catalog_and_notifications_do_not_contact_game(self):
        before=len(self.calls)
        r=self.session.handle({'jsonrpc':'2.0','id':1,'method':'initialize','params':{'protocolVersion':'2025-03-26'}})
        self.assertEqual(r['result']['protocolVersion'],'2025-03-26')
        r=self.session.handle({'jsonrpc':'2.0','id':2,'method':'tools/list'})
        self.assertEqual({t['name'] for t in r['result']['tools']},set(CATALOG))
        self.assertIsNone(self.session.handle({'jsonrpc':'2.0','method':'tools/call','params':{'name':'order_pawn'}}))
        self.assertEqual(before,len(self.calls))
    def test_each_read_is_full_and_novel_fields_survive(self):
        data={'id':'p','novel':{'nested':[False,0,{'future':1}]}}
        for rid in (1,2):
            self.responses.append(data)
            result=self.session.handle(self.req('get_pawn',{'id':'p'},rid))
            self.assertEqual(result['id'],rid)
            self.assertEqual(json.loads(result['result']['content'][0]['text']),data)
            self.assertIn('_evidence',result['result']['content'][-1]['text'])
    def test_media_unknown_properties_and_visibility_boundary(self):
        payload={'content':[{'type':'text','text':json.dumps({'_threatWarning':{'targeting':'hidden','novelVisible':7}})},
                            {'type':'image','mimeType':'image/png','data':'fixture'}], 'novelResultProperty':{'future':True}}
        class Client:
            session={}
            def rpc(self,method,params,request_id):return {'jsonrpc':'2.0','id':request_id,'result':payload}
        with patch.object(self.control,'client_factory',return_value=Client()):r=self.session.handle(self.req('get_pawn',{'id':'p'}))
        d=json.loads(r['result']['content'][0]['text'])
        self.assertNotIn('targeting',d['_threatWarning']);self.assertEqual(d['_threatWarning']['novelVisible'],7)
        self.assertEqual(r['result']['content'][1],payload['content'][1]);self.assertEqual(r['result']['novelResultProperty'],payload['novelResultProperty'])
        self.assertIn('hidden',payload['content'][0]['text'])
    def test_array_root_and_structured_content_keep_visible_fields(self):
        payload={'content':[{'type':'text','text':json.dumps([{'targeting':'hidden','novel':1}])}],
                 'structuredContent':{'targeting':'hidden structured','novel':2}}
        catalog=read_json(self.camp.path/'raw/catalog.json');catalog['tools']['get_area']={'name':'get_area','inputSchema':{'type':'object','properties':{}}}
        atomic_json(self.camp.path/'raw/catalog.json',catalog)
        class Client:
            session={}
            def rpc(self,method,params,request_id):return {'jsonrpc':'2.0','id':request_id,'result':payload}
        with patch.object(self.control,'client_factory',return_value=Client()):r=self.session.handle(self.req('get_area'))
        self.assertEqual(json.loads(r['result']['content'][0]['text']),[{'novel':1}])
        self.assertEqual(r['result']['structuredContent'],{'novel':2})
        meta=json.loads(r['result']['content'][-1]['text']);self.assertEqual(len(meta['visibility_exclusions']['paths']),2)
        self.assertIn('hidden',payload['content'][0]['text'])

    def test_uncertain_request_blocks_next_call_without_replay(self):
        self.responses.append(Uncertain('Lost response'))
        self.assertTrue(self.session.handle(self.req('order_pawn',{'id':'p','command':'Go here'}))['error']['data']['pending'])
        before=len(self.calls);self.session.handle(self.req('order_pawn',{'id':'p','command':'Go here'},2))
        self.assertEqual(before,len(self.calls))
    def test_pause_remains_available_without_clearing_uncertain_request(self):
        path=self.camp.path/'raw/catalog.json';catalog=read_json(path)
        catalog['tools']['set_speed']={'name':'set_speed','inputSchema':{'type':'object','properties':{'action':{'type':'string'}}}}
        atomic_json(path,catalog)
        self.responses.append(Uncertain('Lost response'))
        self.session.handle(self.req('order_pawn',{'id':'p','command':'Go here'}))
        pending=read_json(self.control.path/'pending.json')
        self.responses.append({'ok':True,'paused':True})
        r=self.session.handle(self.req('set_speed',{'action':'pause'},2))
        self.assertIn('result',r);self.assertEqual(read_json(self.control.path/'pending.json'),pending)
        self.assertIn('original_request_still_unresolved',r['result']['content'][-1]['text'])
        before=len(self.calls);self.session.handle(self.req('get_pawn',{'id':'p'},3));self.assertEqual(before,len(self.calls))

    def test_local_output_failure_records_uncertainty(self):
        self.responses.append({'id':'p'})
        class Broken(io.StringIO):
            def write(self,text):raise BrokenPipeError('Disconnected consumer')
        with patch.object(self.control,'ensure_paused',return_value={'confirmed':True}),self.assertRaises(BrokenPipeError):
            serve(self.control,self.token,io.StringIO(json.dumps(self.req('get_pawn',{'id':'p'}))+'\n'),Broken())
        self.assertEqual(read_json(self.control.path/'pending.json')['status'],'unknown')
    def test_interrupted_delivery_records_uncertainty(self):
        self.responses.append({'ok':True,'executed':True})
        class Interrupted(io.StringIO):
            def write(self,text):raise KeyboardInterrupt('Interrupted output')
        with patch.object(self.control,'ensure_paused',return_value={'confirmed':True}),self.assertRaises(KeyboardInterrupt):
            serve(self.control,self.token,io.StringIO(json.dumps(self.req('order_pawn',{'id':'p','command':'Go here'}))+'\n'),Interrupted())
        self.assertEqual(read_json(self.control.path/'pending.json')['status'],'unknown')
        before=len(self.calls);self.session.handle(self.req('order_pawn',{'id':'p','command':'Go here'},2));self.assertEqual(before,len(self.calls))

    def test_unfamiliar_transport_notification_reaches_caller(self):
        notification={'jsonrpc':'2.0','method':'notifications/message','params':{'data':{'novelWarning':[False,0]}}}
        class Client:
            session={};notifications=[notification]
            def rpc(self,method,params,request_id):return {'jsonrpc':'2.0','id':request_id,'result':{'content':[{'type':'text','text':'{"id":"p"}'}]}}
        with patch.object(self.control,'client_factory',return_value=Client()):r=self.session.handle(self.req('get_pawn',{'id':'p'}))
        meta=json.loads(r['result']['content'][-1]['text']);self.assertEqual(meta['_transportNotifications'],[notification])

    def test_eof_pause_failure_remains_visible(self):
        with patch.object(self.control,'ensure_paused',return_value={'confirmed':False}),self.assertRaises(Error):serve(self.control,self.token,io.StringIO(''),io.StringIO())
        self.assertTrue((self.control.path/'pause-uncertain.json').exists())
    def test_malformed_json_followed_by_valid_request(self):
        output=io.StringIO();self.responses.append({'id':'p'})
        with patch.object(self.control,'ensure_paused',return_value={'confirmed':True}):serve(self.control,self.token,io.StringIO('bad\n'+json.dumps(self.req('get_pawn',{'id':'p'}))+'\n'),output)
        rows=[json.loads(line) for line in output.getvalue().splitlines()]
        self.assertEqual(rows[0]['error']['code'],-32700);self.assertIn('result',rows[1])

class StandardWaits(ControlFixture):
    def test_standard_long_horizon_without_arbitrary_risk_category(self):
        self.responses.append({'ok':True,'ticksWaited':2500,'pausedAfter':True,'cause':'timeout'})
        r=self.control.call(self.token,'wait_for_event',{'maxSeconds':120,'maxGameHours':6,'pause':'always'})
        self.assertEqual(self.calls[-1]['arguments']['maxGameHours'],6);self.assertNotIn('action_id',r)
    def test_invalid_or_unpaused_budget_never_dispatched(self):
        before=len(self.calls)
        for args in ({'pause':'auto'},{'pause':'never'},{'maxSeconds':True,'pause':'always'},{'maxSeconds':601,'pause':'always'},
                     {'maxGameHours':-1,'pause':'always'},{'maxGameDays':float('inf'),'pause':'always'}):
            with self.assertRaises(Error):self.control.call(self.token,'wait_for_event',args)
        self.assertEqual(before,len(self.calls))
    def test_hard_deadline_caps_standard_tick_budget_and_is_visible(self):
        self.camp.issue({'title':'Patient deadline','rationale':'Fixture','next_action':'Review','revisit':'Before deadline','resolution':'Evidence',
                         'deadline':{'kind':'hard','tick':300500,'reason':'Fixture deadline'}})
        self.responses.append({'ok':True,'ticksWaited':500,'pausedAfter':True,'cause':'timeout'})
        r=self.control.call(self.token,'wait_for_event',{'maxSeconds':120,'maxGameHours':6,'pause':'always'})
        self.assertEqual(self.calls[-1]['arguments']['maxGameTicks'],500);self.assertEqual(r['wait_budget']['hard_deadline_tick'],300500)
        with self.assertRaises(Error):self.control.call(self.token,'wait_for_event',{'pause':'always'})
