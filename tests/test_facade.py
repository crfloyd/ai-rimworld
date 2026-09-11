import json
from unittest.mock import patch
from test_system import ControlFixture,CATALOG
from tools.rimworld.core import Error,canonical,read_json,atomic_json
from tools.rimworld import facade
from tools.rimworld.session import Session


class Facade(ControlFixture):
    def setUp(self):
        super().setUp();self.session=Session(self.control,self.token)

    def req(self,name,args=None,rid=1):
        return {'jsonrpc':'2.0','id':rid,'method':'tools/call','params':{'name':name,'arguments':args or {}}}

    def body(self,name,args=None,rid=1):
        r=self.session.handle(self.req(name,args,rid))
        if 'error' in r: raise Error(r['error']['message'])
        return json.loads(r['result']['content'][0]['text'])

    def add_tools(self,*names):
        from pathlib import Path
        real=read_json(Path(__file__).resolve().parents[1]/'api/catalog.json')['tools']
        path=self.camp.path/'raw/catalog.json';cat=read_json(path)
        for n in names:cat['tools'][n]=real[n]
        atomic_json(path,cat)

    def test_tools_list_is_small_and_hides_upstream(self):
        r=self.session.handle({'jsonrpc':'2.0','id':1,'method':'tools/list'})
        names={t['name'] for t in r['result']['tools']}
        self.assertEqual(names,set(facade.local()))
        self.assertNotIn('get_pawn',names)
        self.assertFalse(r['result']['_meta']['upstream_exposed'])
        self.assertEqual(r['result']['_meta']['upstream_tools'],len(CATALOG))
        self.assertEqual(r['result']['_meta']['discovery'],'rw_capabilities')
        # The advertised surface is the whole persistent cost; keep it an order of magnitude down.
        self.assertLess(len(canonical(r['result']['tools']).encode()),14278)

    def test_upstream_names_are_refused_without_the_flag(self):
        before=len(self.calls)
        r=self.session.handle(self.req('get_pawn',{'id':'p'}))
        self.assertIn('rw_read',r['error']['message'])
        self.assertEqual(before,len(self.calls))

    def test_expose_flag_restores_surface_and_dispatch(self):
        session=Session(self.control,self.token,expose_upstream=True)
        r=session.handle({'jsonrpc':'2.0','id':1,'method':'tools/list'})
        self.assertEqual({t['name'] for t in r['result']['tools']},set(CATALOG)|set(facade.local()))
        self.responses.append({'id':'p'})
        self.assertIn('result',session.handle(self.req('get_pawn',{'id':'p'})))

    def test_read_refuses_mutating_arguments_without_dispatch(self):
        self.add_tools('set_schedule','get_status')
        before=len(self.calls)
        for tool,args in (('order_pawn',{'id':'p','command':'Go here'}),
                          ('set_schedule',{'id':'p','assignment':'WWWW'}),
                          ('get_status',{'bundle_set':'get_pawn'})):
            with self.assertRaises(Error) as caught:
                self.body('rw_read',{'tool':tool,'args':args})
            self.assertIn('rw_act',str(caught.exception))
        self.assertEqual(before,len(self.calls))

    def test_documented_read_modes_are_reads_not_mutations(self):
        # Regression: a tool whose catalog effect is 'mutation' but which exposes one
        # documented read-only mode was rejected by rw_read and pushed to rw_act.
        # form_caravan mode=status is how a departure is verified, so this blocked
        # the outcome check a consequential order requires.
        from tools.rimworld.control import READ_MODES,effect
        self.add_tools(*READ_MODES)
        for tool,(argument,value) in READ_MODES.items():
            self.assertEqual(effect(tool,{argument:value}),'inspection-ui')
            self.assertEqual(effect(tool,{}),'mutation')
        # Full round trip on the case that stopped the live run.
        self.responses.append({'formations':[]})
        self.body('rw_read',{'tool':'form_caravan','args':{'mode':'status'}})
        with self.assertRaises(Error) as caught:
            self.body('rw_act',{'tool':'form_caravan','args':{'mode':'status'}},2)
        self.assertIn('rw_read',str(caught.exception))

    def test_every_mutation_tool_with_a_read_mode_is_declared(self):
        """The captured schemas are the authority on which read modes exist."""
        from pathlib import Path
        from tools.rimworld.control import READ_MODES
        cat=read_json(Path(__file__).resolve().parents[1]/'api/catalog.json')['tools']
        effects=read_json(Path(__file__).resolve().parents[1]/'api/effects.json')['tools']
        readish={'status','list','get','info','query','report','check','preview','inspect','view','show','read'}
        found=set()
        for name,tool in cat.items():
            if effects.get(name)!='mutation': continue
            for prop,spec in tool.get('inputSchema',{}).get('properties',{}).items():
                if any(isinstance(v,str) and v.lower() in readish for v in spec.get('enum') or ()):
                    found.add(name)
        self.assertEqual(found-{'manage_area'},set(READ_MODES))

    def test_read_accepts_argument_dependent_reads(self):
        self.add_tools('set_schedule')
        for tool,args in (('order_pawn',{'id':'p'}),('set_schedule',{'id':'p'})):
            self.responses.append({'id':'p','options':[]})
            self.assertIn('id',self.body('rw_read',{'tool':tool,'args':args})['data'])

    def test_act_refuses_reads_and_waits(self):
        before=len(self.calls)
        with self.assertRaises(Error) as caught: self.body('rw_act',{'tool':'get_pawn','args':{'id':'p'}})
        self.assertIn('rw_read',str(caught.exception))
        with self.assertRaises(Error) as caught: self.body('rw_act',{'tool':'wait_for_event','args':{}})
        self.assertIn('rw_wait',str(caught.exception))
        self.assertEqual(before,len(self.calls))

    def test_denied_tool_refused(self):
        before=len(self.calls)
        with self.assertRaises(Error): self.body('rw_act',{'tool':'load_game','args':{}})
        self.assertEqual(before,len(self.calls))

    def test_unknown_tool_points_at_discovery(self):
        with self.assertRaises(Error) as caught: self.body('rw_read',{'tool':'no_such_tool','args':{}})
        self.assertIn('rw_capabilities',str(caught.exception))

    def test_missing_exact_capability_suggests_close_tool(self):
        self.add_tools('draft')
        with self.assertRaises(Error) as caught:self.body('rw_capabilities',{'tool':'draft_pawn'})
        self.assertIn('draft',str(caught.exception));self.assertIn('Did you mean',str(caught.exception))

    def test_invalid_arguments_refused_before_dispatch(self):
        before=len(self.calls)
        with self.assertRaises(Error): self.body('rw_read',{'tool':'get_pawn','args':{'id':7}})
        self.assertEqual(before,len(self.calls))

    def test_pause_stays_available_while_a_request_is_unresolved(self):
        from tools.rimworld.mcp import Uncertain
        path=self.camp.path/'raw/catalog.json';catalog=read_json(path)
        catalog['tools']['set_speed']={'name':'set_speed','inputSchema':{'type':'object','properties':{'action':{'type':'string'}}}}
        atomic_json(path,catalog)
        self.responses.append(Uncertain('Lost response'))
        self.session.handle(self.req('rw_act',{'tool':'order_pawn','args':{'id':'p','command':'Go here'}}))
        pending=read_json(self.control.path/'pending.json')
        self.responses.append({'ok':True,'paused':True})
        value=self.body('rw_act',{'tool':'set_speed','args':{'action':'pause'}},2)
        self.assertTrue(value['original_request_still_unresolved'])
        self.assertEqual(read_json(self.control.path/'pending.json'),pending)

    def test_control_guards_still_fire_through_the_facade(self):
        atomic_json(self.control.path/'catalog-stale.json',{'at':'now'})
        before=len(self.calls)
        with self.assertRaises(Error): self.body('rw_read',{'tool':'get_pawn','args':{'id':'p'}})
        self.assertEqual(before,len(self.calls))

    def test_wait_injects_pause_always(self):
        self.responses.append({'event':'letter','cause':'threatAppeared','pausedAfter':True})
        self.body('rw_wait',{'maxSeconds':30,'context':'none'})
        self.assertEqual(self.calls[-1]['arguments']['pause'],'always')
        self.assertEqual(self.calls[-1]['name'],'wait_for_event')

    def test_wait_without_confirmed_pause_still_guards(self):
        self.responses.extend([{'event':None,'cause':'timeout','pausedAfter':False},{'ok':True,'paused':True}])
        value=self.body('rw_wait',{'maxSeconds':30,'context':'none'})
        self.assertIn('pause_guard',value)
        self.assertTrue((self.control.path/'pause-uncertain.json').exists())

    def test_wait_auto_context_and_explicit_verification_share_one_public_call(self):
        self.responses.extend([
            {'event':True,'cause':'notification','pausedAfter':True,
             '_notifications':[{'text':'Tatyana has an infection'}]},
            {'loaded':True,'colonyName':'Fixture Colony','ticksGame':301000,'paused':True,'bundled':{
                'list_colonists':{'colonists':[{'id':'p','name':'Tatyana Contreras','health':80}]},
                'get_alerts':{'dangerByMap':[],'activeAlerts':[]},
                'get_resources':{'resources':[{'defName':'MedicineHerbal','count':3}]}}},
            {'id':'p','tab':'health','hediffs':[{'label':'Infection','severity':.1}]},
            {'id':'p','tab':'health','hediffs':[{'label':'Infection','severity':.1}]}
        ])
        value=self.body('rw_wait',{'maxGameTicks':1000,'verify':[{'key':'patient','tool':'get_pawn','args':{'id':'p','tab':'health'}}]})
        self.assertEqual([c['name'] for c in self.calls[-4:]],['wait_for_event','get_status','get_pawn','get_pawn'])
        self.assertIn('medical',value['event_context']['topics'])
        self.assertEqual(value['event_context']['affected_pawns'][0]['facet'],'health')
        self.assertEqual(value['verification']['patient']['data']['id'],'p')
        self.assertTrue(value['verification_complete']);self.assertEqual(value['verification_not_run'],[])
        self.assertTrue((self.control.path/'composition.json').exists())
        from tools.rimworld.composition import delivered
        manifest=read_json(self.camp.path/'reference/compositions'/(value['composition']+'.json'))
        self.assertIn(('verify_patient','get_pawn'),[(o['key'],o['tool']) for o in manifest['observations']])
        delivered(self.control,self.token,value['composition'])

    def test_post_wait_enrichment_error_delivers_completed_wait_without_replay(self):
        self.responses.extend([
            {'event':True,'cause':'threatAppeared','pausedAfter':True},
            {'loaded':True,'colonyName':'Fixture Colony','ticksGame':301000,'paused':True,
             'bundled':{'list_colonists':{'colonists':[]},'get_alerts':{'activeAlerts':[]}}}
        ])
        value=self.body('rw_wait',{'maxGameTicks':1000})
        self.assertTrue(value['event_context_error']['wait_completed'])
        self.assertTrue(value['event_context_error']['no_replay'])
        manifest=read_json(self.camp.path/'reference/compositions'/(value['composition']+'.json'))
        self.assertEqual(manifest['status'],'ready_to_deliver')

    def test_wait_verification_preflights_before_advancing(self):
        before=len(self.calls)
        with self.assertRaises(Error):
            self.body('rw_wait',{'maxGameTicks':1000,
                'verify':[{'key':'bad','tool':'order_pawn','args':{'id':'p','command':'Go'}}]})
        self.assertEqual(before,len(self.calls));self.assertFalse((self.control.path/'composition.json').exists())

    def test_berserk_event_context_includes_letter_patient_and_nearby_responders(self):
        self.add_tools('read_letter','list_things')
        self.responses.extend([
            {'event':True,'cause':'letter','pausedAfter':True,
             '_notifications':[{'kind':'letter','id':195,'type':'ThreatSmall','text':'Berserk: Tatyana'}]},
            {'loaded':True,'colonyName':'Fixture Colony','ticksGame':301000,'paused':True,'bundled':{
                'list_colonists':{'colonists':[{'id':'p','name':'Tatyana Contreras','health':98,'mood':0,'mentalState':'berserk'},
                                                 {'id':'w','name':'Ward Vale','health':100,'mood':60}]},
                'get_alerts':{'dangerByMap':[],'activeAlerts':[{'label':'Major break risk','explanation':'Tatyana'}]},
                'get_resources':{'resources':[]}}},
            {'id':'p','name':'Tatyana Contreras','mood':0,'mentalState':'berserk','x':10,'z':10,'weapon':'Handgun'},
            {'id':'p','tab':'needs','mood':0,'thoughts':[{'label':'Intense pain'}]},
            {'id':'p','tab':'health','painPercent':42,'hediffs':[{'label':'Bite'}]},
            {'id':'p','tab':'gear','equipment':[{'label':'Handgun'}],'apparel':[]},
            {'id':195,'label':'Berserk: Tatyana','text':'The final straw was intense pain','ok':True},
            {'things':[{'id':'p','label':'Tatyana','hostile':True,'x':10,'z':10},
                       {'id':'w','label':'Ward','hostile':False,'x':12,'z':10,'weapon':'SMG'}]},
            {'id':'w','name':'Ward','health':100,'mood':60,'x':12,'z':10,'weapon':'SMG'}
        ])
        value=self.body('rw_wait',{'maxGameHours':1})
        context=value['event_context']
        self.assertEqual([x['facet'] for x in context['affected_pawns']],['summary','needs','health','gear'])
        summary_call=next(c for c in self.calls if c['name']=='get_pawn' and c['arguments'].get('id')=='p')
        self.assertNotIn('tab',summary_call['arguments'])
        self.assertEqual(context['letters'][0]['data']['id'],195)
        self.assertEqual(context['threats']['anchor'],'p')
        self.assertEqual(context['threats']['nearby_pawns'][0]['label'],'Ward')
        self.assertEqual(context['threats']['responders'][0]['data']['weapon'],'SMG')
        self.assertEqual(self.calls[-2]['arguments']['nearId'],'p')
        from tools.rimworld.composition import delivered
        delivered(self.control,self.token,value['composition'])

    def test_independent_action_batch_preflights_and_stops_on_reported_failure(self):
        self.add_tools('set_work_priority','draft')
        self.responses.extend([{'ok':True,'pawn':'p','priority':0},{'ok':False,'error':'Target moved'}])
        value=self.body('rw_act',{'independent':True,'actions':[
            {'tool':'set_work_priority','args':{'id':'p','workType':'Cooking','priority':0}},
            {'tool':'order_pawn','args':{'id':'p','command':'Haul'}},
            {'tool':'draft','args':{'ids':'p','action':'undraft'}}]})
        self.assertTrue(value['stopped']);self.assertEqual(value['not_run'],[2])
        self.assertEqual([c['name'] for c in self.calls[-2:]],['set_work_priority','order_pawn'])
        from tools.rimworld.composition import delivered
        delivered(self.control,self.token,value['composition'])
        before=len(self.calls)
        with self.assertRaises(Error):
            self.body('rw_act',{'independent':False,'actions':[{'tool':'order_pawn','args':{'id':'p','command':'Go'}}]},3)
        self.assertEqual(before,len(self.calls))

    def test_successful_same_dialog_batch_continues(self):
        self.add_tools('window_action')
        self.responses.extend([{'ok':True,'window':'Dialog_Trade','did':'textQueued','field':i,'text':str(i),
                                '_dialogOpen':True,'_paused':True} for i in range(3)])
        value=self.body('rw_act',{'independent':True,'actions':[
            {'tool':'window_action','args':{'field':i,'text':str(i)}} for i in range(3)]})
        self.assertFalse(value['stopped']);self.assertEqual(value['completed'],3)
        from tools.rimworld.composition import delivered
        delivered(self.control,self.token,value['composition'])

    def test_action_batch_preflights_every_step_before_dispatch(self):
        before=len(self.calls)
        with self.assertRaises(Error):
            self.body('rw_act',{'independent':True,'actions':[
                {'tool':'order_pawn','args':{'id':'p','command':'Go'}},
                {'tool':'order_pawn','args':{'id':7,'command':'Invalid'}}]})
        self.assertEqual(before,len(self.calls));self.assertFalse((self.control.path/'composition.json').exists())

    def test_capabilities_search_returns_names_not_schemas(self):
        found=self.body('rw_capabilities',{'query':'pawn'})
        self.assertTrue(found['matches'])
        self.assertNotIn('inputSchema',canonical(found['matches']))
        one=self.body('rw_capabilities',{'tool':'get_pawn'},2)
        self.assertIn('inputSchema',one['tool'])

    def test_capability_overview_and_workflow_preserve_affordances_without_schemas(self):
        self.add_tools('main_menu','game_setup_status','list_trade','set_trade','trade_action')
        overview=self.body('rw_capabilities',{'overview':True})
        self.assertIn('setup',overview['domains']);self.assertIn('combat',overview['domains'])
        self.assertNotIn('inputSchema',canonical(overview))
        # The default overview is an index: domain names, counts and purposes only.
        self.assertEqual(set(overview['domains']['combat']),{'tools','purpose'})
        detailed=self.body('rw_capabilities',{'overview':True,'full':True},7)
        self.assertIn('get_status',[row['tool'] for row in detailed['domains']['combat']])
        setup=self.body('rw_capabilities',{'domain':'setup'},2)
        self.assertIn('game_setup_status',[x['tool'] for x in setup['domains']['setup']])
        workflow=self.body('rw_capabilities',{'workflow':'new_game'},3)
        self.assertEqual(workflow['steps'][0]['tool'],'main_menu')
        trade=self.body('rw_capabilities',{'workflow':'trade'},4)
        self.assertEqual([x['tool'] for x in trade['steps']][:2],['list_trade','set_trade'])
        crisis=self.body('rw_capabilities',{'workflow':'resume_crisis'},5)
        self.assertEqual(crisis['steps'][0]['tool'],'get_status')
        with self.assertRaises(Error):self.body('rw_capabilities',{'overview':True,'domain':'food'},6)

    def test_public_telemetry_includes_offline_tools_and_exact_response_bytes(self):
        value=self.body('rw_capabilities',{'tool':'get_pawn'})
        rows=[json.loads(l) for l in (self.camp.path/'facade-telemetry.jsonl').read_text().splitlines()]
        row=rows[-1]
        self.assertEqual(row['public_tool'],'rw_capabilities')
        self.assertEqual(row['capability_tool'],'get_pawn')
        self.assertEqual(row['response_bytes'],len(json.dumps(value,ensure_ascii=False,allow_nan=False).encode()))
        self.assertIn('excludes JSON-RPC',row['response_bytes_basis'])

    def test_local_tools_are_classified_not_guessed(self):
        for name,effect in facade.LOCAL_EFFECTS.items():
            self.assertEqual(self.body('rw_capabilities',{'tool':name})['default_effect'],effect)

    def test_retrieve_recovers_full_evidence_without_contacting_the_game(self):
        self.responses.append({'id':'p','hint':'x'*400,'novel':{'deep':[1,2]}})
        compact=self.body('rw_read',{'tool':'get_pawn','args':{'id':'p'},'fields':['id']})
        before=len(self.calls)
        full=self.body('rw_retrieve',{'observation':compact['id'],'view':'full'},2)
        self.assertEqual(json.loads(full['result']['content'][0]['text'])['hint'],'x'*400)
        self.assertEqual(before,len(self.calls))
        self.assertEqual(self.body('rw_retrieve',{'observation':compact['id'],'view':'summary'},3)['view'],'summary')
        self.assertEqual(before,len(self.calls))

    def test_projection_reports_omissions_and_keeps_warnings(self):
        self.responses.append({'id':'p','hint':'x'*200,'warning':'something odd','keep':1})
        value=self.body('rw_read',{'tool':'get_pawn','args':{'id':'p'},'fields':['id']})
        self.assertIn('data.hint',value['omitted_keys'])
        self.assertEqual(value['data']['warning'],'something odd')  # warning-bearing keys survive projection
        self.assertNotIn('hint',value['data'])

    def test_row_projection_keeps_every_row(self):
        self.add_tools('list_things')
        rows=[{'id':str(i),'defName':'Steel','x':i,'z':i,'noise':'y'*40} for i in range(6)]
        self.responses.append({'things':rows})
        value=self.body('rw_read',{'tool':'list_things','args':{},'row_fields':['id','defName']})
        packed=value['data']['things']
        self.assertEqual(len(packed['rows'] if isinstance(packed,dict) else packed),6)
        self.assertIn('data.things[].noise',value['omitted_keys'])

    def test_model_facing_rows_are_ordinary_sliceable_arrays(self):
        self.add_tools('list_things')
        rows=[{'id':str(i),'defName':'Bed','x':i,'z':1} for i in range(10)]
        self.responses.append({'matched':10,'things':rows})
        value=self.body('rw_read',{'tool':'list_things','args':{'category':'building','defName':'Bed'}})
        self.assertIsInstance(value['data']['things'],list)
        self.assertEqual(value['data']['things'][:2],rows[:2])

    def test_reads_are_self_contained_unless_delta_has_an_explicit_base(self):
        self.add_tools('list_things')
        rows=[{'id':'p','name':'P'}]
        self.responses.extend([{'things':rows},{'things':rows},{'things':rows}])
        first=self.body('rw_read',{'tool':'list_things','args':{'category':'pawn'}},1)
        second=self.body('rw_read',{'tool':'list_things','args':{'category':'pawn'}},2)
        self.assertEqual(second['data']['things'],rows)
        self.assertTrue(second['change']['unchanged'])
        delta=self.body('rw_read',{'tool':'list_things','args':{'category':'pawn'},
                                   'delta':True,'since':first['id']},3)
        self.assertTrue(delta['unchanged']);self.assertEqual(delta['data'],{})
        before=len(self.calls)
        with self.assertRaises(Error):
            self.body('rw_read',{'tool':'list_things','args':{'category':'pawn'},'delta':True},4)
        self.assertEqual(before,len(self.calls))

    def test_trade_window_points_to_semantic_trade_tools(self):
        self.add_tools('get_window_ui','list_trade')
        self.responses.extend([
            {'ok':True,'window':'Dialog_Trade','buttons':[{'label':'<','row':'Steel'}]},
            {'ok':True,'active':True,'silver':100,'tradeables':[{'label':'Steel','buyPrice':2}]}
        ])
        value=self.body('rw_read',{'tool':'get_window_ui','args':{}})
        self.assertEqual(value['affordance']['prefer'],['list_trade','set_trade','trade_action'])
        self.assertEqual(value['trade']['data']['tradeables'][0]['label'],'Steel')
        self.assertNotIn('buttons',value['data']);self.assertEqual(value['ui_control_counts']['buttons'],1)

    def test_partial_bounded_results_keep_the_data_container(self):
        self.add_tools('list_things')
        rows=[{'id':str(i),'def':'MineableSteel','distance':i} for i in range(4)]
        self.responses.append({'matched':128,'returned':4,'truncated':True,'things':rows})
        value=self.body('rw_read',{'tool':'list_things','args':{'defName':'MineableSteel','limit':4}})
        self.assertEqual(value['data']['things'],rows)
        self.assertEqual(value['completeness'],'partial')

    def test_caller_limit_reports_true_total(self):
        self.add_tools('list_things')
        self.responses.append({'things':[{'id':str(i),'x':i} for i in range(40)]})
        value=self.body('rw_read',{'tool':'list_things','args':{},'limit':5})
        self.assertTrue(value['truncated']);self.assertEqual(value['total'],40);self.assertEqual(value['returned'],5)
        self.assertEqual(value['reason'],'caller_limit')

    def test_payload_budget_bounds_an_unfiltered_read(self):
        self.add_tools('list_things')
        rows=[{'id':'thing-%d'%i,'defName':'Plant_TreeOak','x':i,'z':i,'label':'oak '*20} for i in range(900)]
        self.responses.append({'things':rows})
        value=self.body('rw_read',{'tool':'list_things','args':{}})
        self.assertTrue(value['truncated'])
        self.assertEqual(value['reason'],'model_payload_budget')
        self.assertEqual(value['total'],900)
        self.assertLess(value['returned'],900)
        self.assertLessEqual(len(canonical(value).encode()),facade.PAYLOAD_BUDGET)
        self.assertIn('category',value['suggest'])
        before=len(self.calls)
        full=self.body('rw_retrieve',{'observation':value['e'],'view':'full'},2)
        self.assertEqual(len(json.loads(full['result']['content'][0]['text'])['things']),900)
        self.assertEqual(before,len(self.calls))

    def test_threat_warning_is_referenced_never_dropped(self):
        # One global warning repeated across different pawns: separate scopes, so the
        # existing per-scope delta cannot suppress it.
        threat={'hostiles':[{'id':'raider','kind':'Pirate'}],'detail':'z'*300}
        for pawn in ('a','b'):
            self.responses.append({'id':pawn,'_threatWarning':dict(threat)})
        first=self.body('rw_read',{'tool':'get_pawn','args':{'id':'a'}},1)
        self.assertEqual(first['data']['_threatWarning'],threat)
        ref=list(first['refs'])[0]
        second=self.body('rw_read',{'tool':'get_pawn','args':{'id':'b'}},2)
        self.assertEqual(second['data']['_threatWarning'],{'same_as':ref})
        self.assertLess(len(canonical(second).encode()),len(canonical(first).encode()))
        self.assertTrue([r for r in second.get('risks') or () if r['kind']=='_threatWarning'])
        before=len(self.calls)
        resolved=self.body('rw_retrieve',{'ref':ref},4)
        self.assertEqual(resolved['value'],threat);self.assertEqual(resolved['field'],'_threatWarning')
        self.assertEqual(before,len(self.calls))

    def test_small_repeated_values_remain_literal(self):
        for pawn in ('a','b'):
            self.responses.append({'id':pawn,'_paused':True})
        first=self.body('rw_read',{'tool':'get_pawn','args':{'id':'a'}},1)
        second=self.body('rw_read',{'tool':'get_pawn','args':{'id':'b'}},2)
        self.assertIs(first['data']['_paused'],True);self.assertIs(second['data']['_paused'],True)
        self.assertNotIn('refs',first);self.assertNotIn('refs',second)

    def test_changed_threat_is_never_referenced(self):
        self.responses.append({'id':'a','_threatWarning':{'hostiles':1}})
        self.body('rw_read',{'tool':'get_pawn','args':{'id':'a'}},1)
        self.responses.append({'id':'b','_threatWarning':{'hostiles':2}})
        second=self.body('rw_read',{'tool':'get_pawn','args':{'id':'b'}},2)
        self.assertEqual(second['data']['_threatWarning'],{'hostiles':2})

    def test_references_do_not_survive_a_presentation_reset(self):
        threat={'hostiles':[{'id':'raider'}]}
        for pawn in ('a','b','c'): self.responses.append({'id':pawn,'_threatWarning':dict(threat)})
        self.body('rw_read',{'tool':'get_pawn','args':{'id':'a'}},1)
        self.body('rw_read',{'tool':'get_pawn','args':{'id':'b'}},2)
        self.camp.meta['presentation_reset_at']='2026-09-09T00:00:00Z'
        atomic_json(self.camp.path/'campaign.json',self.camp.meta)
        self.control.campaign.meta['presentation_reset_at']='2026-09-09T00:00:00Z'
        again=self.body('rw_read',{'tool':'get_pawn','args':{'id':'c'}},3)
        self.assertEqual(again['data']['_threatWarning'],threat)  # literal again, never a stale reference
        self.assertIn('refs',again)

    def test_unknown_reference_is_refused(self):
        with self.assertRaises(Error) as caught: self.body('rw_retrieve',{'ref':'th99'})
        self.assertIn('connection',str(caught.exception))
        row=json.loads((self.camp.path/'facade-telemetry.jsonl').read_text().splitlines()[-1])
        self.assertEqual((row['public_tool'],row['status'],row['retrieve_selector']),('rw_retrieve','error','ref'))
        self.assertIsNone(row['response_bytes'])

    def test_offline_tools_are_not_blind_in_telemetry(self):
        """rw_capabilities and rw_retrieve never reach Control.call, so without their
        own rows two of seven public tools leave no trace at all."""
        self.body('rw_capabilities',{'query':'pawn'},1)
        self.responses.append({'id':'p','hint':'x'*50})
        read=self.body('rw_read',{'tool':'get_pawn','args':{'id':'p'}},2)
        self.body('rw_retrieve',{'observation':read['id'],'view':'full'},3)
        rows=[json.loads(l) for l in (self.camp.path/'telemetry.jsonl').read_text().splitlines()]
        facade=[r for r in rows if r.get('kind')=='facade_call']
        self.assertEqual([r['driver'] for r in facade],
                         ['facade_capabilities','facade_read','facade_retrieve'])
        for row in facade:
            self.assertIsInstance(row['model_bytes'],int)
            self.assertGreater(row['model_bytes'],0)
        self.assertFalse(facade[0]['game_contact'])   # discovery is offline
        self.assertTrue(facade[1]['game_contact'])
        self.assertFalse(facade[2]['game_contact'])   # retrieval replays evidence
        self.assertEqual(facade[2]['view'],'full')

    def test_model_bytes_measures_the_shaped_envelope(self):
        """Control.call records the upstream payload before shaping; the facade row
        must record what the caller actually received."""
        self.add_tools('list_things')
        self.responses.append({'things':[{'id':str(i),'x':i,'noise':'y'*60} for i in range(12)]})
        body=self.body('rw_read',{'tool':'list_things','args':{},'row_fields':['id']})
        rows=[json.loads(l) for l in (self.camp.path/'telemetry.jsonl').read_text().splitlines()]
        upstream=[r for r in rows if r.get('driver')=='facade_read' and r.get('kind')!='facade_call'][-1]
        shaped=[r for r in rows if r.get('kind')=='facade_call'][-1]
        self.assertEqual(shaped['model_bytes'],len(canonical(body).encode()))
        self.assertLess(shaped['model_bytes'],upstream['context_bytes'])
        self.assertTrue(shaped['projected'])

    def test_facade_calls_are_tagged_in_telemetry(self):
        self.responses.append({'id':'p'})
        self.body('rw_read',{'tool':'get_pawn','args':{'id':'p'}})
        rows=[json.loads(l) for l in (self.camp.path/'telemetry.jsonl').read_text().splitlines()]
        self.assertEqual(rows[-1]['driver'],'facade_read')
        public=json.loads((self.camp.path/'facade-telemetry.jsonl').read_text().splitlines()[-1])
        self.assertEqual((public['public_tool'],public['upstream_tool']),('rw_read','get_pawn'))
