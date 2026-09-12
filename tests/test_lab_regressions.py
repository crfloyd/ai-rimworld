"""Offline regressions grounded in the independent audit and live catalog shapes."""
import copy
import json
from pathlib import Path
from unittest.mock import patch
from test_system import Workspace, fixture
from tools.rimworld.core import atomic_json, Error
from tools.rimworld.mcp import validate
from tools.rimworld.memory import Campaign
from tools.rimworld.facts import entries
from tools.rimworld.safety import deadlines, signals
from tools.rimworld.observations import normalize, delta_view
from tools.rimworld.continuity import packet




class Persistence(Workspace):
    def test_varied_scope_index_retains_history_and_selective_reads(self):
        first = None
        for x in range(80):
            r = self.ingest('get_area', {'minX':x,'maxX':x,'minZ':0,'maxZ':0},
                            {'things':[{'id':str(i),'def':'Steel','x':x,'z':i} for i in range(40)], 'terrainSummary':{'Soil':1}})
            first = first or r['id']
        state = self.camp.state()
        self.assertEqual(len(state['facts']),80)
        self.assertLess((self.camp.path/'.projection.json').stat().st_size,2000)
        self.assertEqual(list(entries(state, tools=('get_pawn',))), [])
        self.assertEqual(self.camp.observation(first)['data']['things'][0]['x'],0)
        self.assertEqual(packet(self.camp)['active_risks'], [])
        before = (self.camp.path/'observations.jsonl').read_bytes()
        (self.camp.path/'reference/facts.sqlite').unlink()
        self.assertEqual(len(self.camp.state()['facts']),80)
        self.assertEqual(before,(self.camp.path/'observations.jsonl').read_bytes())

    def test_failed_scoped_read_keeps_previous_and_danger(self):
        args={'minX':1,'maxX':1,'minZ':1,'maxZ':1}
        first=self.ingest('get_area',args,{'things':[{'id':'enemy','hostile':True}], 'terrainSummary':{}})
        self.ingest('get_area',args,{'error':'unavailable'})
        entry=next(iter(self.camp.state()['facts'].values()))
        self.assertEqual(entry['last_known']['id'],first['id'])
        self.assertTrue(packet(self.camp)['missing_coverage'])
        self.assertIn('Last known, requiring revalidation', self.camp.refresh())

    def test_rebuild_and_demand_lookup_recover_action_index(self):
        a=self.fixture_action('order_pawn',{'id':'p'},'Move','movement')
        index=self.camp.path/'reference/action-index'/(a['id']+'.json')
        journal=(self.camp.path/'actions.jsonl').read_bytes()
        index.unlink();self.camp.rebuild()
        self.assertEqual(self.camp.action_record(a['id'])['id'],a['id'])
        index.unlink()
        self.assertEqual(self.camp.action_record(a['id'])['id'],a['id'])
        self.assertEqual(journal,(self.camp.path/'actions.jsonl').read_bytes())

    def test_review_deadline_before_at_after_and_unknown_clock(self):
        issue=self.camp.issue({'title':'Review','rationale':'Progress decision','next_action':'Inspect',
            'revisit':'at deadline','resolution':'Review completed', 'deadline':{'kind':'review','tick':100,'reason':'Review progress'}})
        self.assertIn(issue['id'],deadlines(self.camp)['soft_reviews'])
        for tick, due in [(99,False),(100,True),(101,True)]:
            self.ingest('get_status',{}, {'loaded':False,'ticksGame':tick})
            self.assertEqual(issue['id'] in deadlines(self.camp)['soft_reviews'],due)

    def test_medical_delta_compact_but_changed_condition_invalidates_risk(self):
        data={'id':'p','overallHealthPercent':66,'painPercent':37,
              'hediffs':[{'label':'Bruise','part':str(i),'severity':3.123,'tended':False} for i in range(25)]}
        old=normalize('get_pawn',{'id':'p','tab':'health'},data,'c','s','fixture')
        delta=delta_view(old,old)
        self.assertLess(len(json.dumps(delta)),len(json.dumps(data)))
        self.assertTrue(delta['unchanged'])
        old_risk=next(r for r in signals(old) if r['kind']=='health_conditions')
        new=copy.deepcopy(old);new['data']['hediffs'][0]['severity']=4.123
        new_risk=next(r for r in signals(new) if r['kind']=='health_conditions')
        self.assertNotEqual(old_risk['id'],new_risk['id'])
        from tools.rimworld.observations import apply_list_patch
        self.assertEqual(apply_list_patch(old['data']['hediffs'],delta_view(old,new)['list_changes']['fields']['hediffs'])[0]['severity'],4.123)
        new['data']['bleedRatePerDay']=0.9
        self.assertEqual(next(r for r in signals(new) if r['kind']=='bleedRatePerDay')['severity'],'critical')

    def test_index_replay_after_failed_derived_write(self):
        self.ingest('get_status',{}, {'loaded':False,'ticksGame':1})
        from tools.rimworld import memory
        original=memory.atomic_json
        def fail_index(path,value):
            if 'observation-index' in str(path): raise OSError('injected derived write failure')
            return original(path,value)
        with patch('tools.rimworld.memory.atomic_json',side_effect=fail_index):
            with self.assertRaises(OSError):self.ingest('get_status',{}, {'loaded':False,'ticksGame':2})
        c=Campaign(self.root,'example')
        self.assertEqual(c.state()['latest_tick'],2)
        self.assertEqual(c.state()['count'],2)
        self.assertEqual(c.state()['latest_tick'],2)


    def test_presentation_retains_uncertainty_and_compact_active_risks(self):
        from tools.rimworld.presentation import present
        data={'id':'p','overallHealthPercent':80,'hediffs':[{'label':'Injury','severity':2.125,'part':str(i)} for i in range(25)]}
        old=normalize('get_pawn',{'id':'p','tab':'health'},data,'c','s','fixture')
        view=present(delta_view(old,old))
        self.assertLess(len(json.dumps(view)),len(json.dumps(data))/2)
        self.assertEqual(view['risks'][0]['value']['overallHealthPercent'],80)
        failed=normalize('get_pawn',{'id':'p','tab':'health'},{'error':'lost response'},'c','s','fixture')
        result=present(delta_view(old,failed))
        self.assertNotEqual(result['completeness'],'known')
        self.assertIn('coverage_loss',str(result))
        status=normalize('get_status',{}, {'loaded':False,'_delta':{'pawnDamage':[{'name':'p','hpBefore':80,'hpAfter':60}]}},'c','s','fixture')
        self.assertEqual(next(r for r in signals(status) if r['kind']=='delta:pawnDamage')['severity'],'critical')


    def test_real_draft_receipt_without_ok_is_accepted_not_completed(self):
        from tools.rimworld.control import receipt_status
        data={'action':'draft','drafted':['Ward'],'alreadyInState':[],'skipped':[]}
        self.assertEqual(receipt_status('draft',{'action':'draft'},data,'known'),'accepted')
        self.assertEqual(receipt_status('draft',{'action':'draft'},data,'partial'),'unknown')
        data['skipped']=['missing pawn']
        self.assertEqual(receipt_status('draft',{'action':'draft'},data,'known'),'blocked')


    def test_list_patch_exactly_reconstructs_reordered_duplicate_rows(self):
        data={'id':'p','overallHealthPercent':90,'hediffs':[{'label':'Bruise','part':'leg','severity':i/10} for i in range(30)]}
        old=normalize('get_pawn',{'id':'p','tab':'health'},data,'c','s','fixture')
        new=copy.deepcopy(old);new['data']['hediffs'][0],new['data']['hediffs'][1]=new['data']['hediffs'][1],new['data']['hediffs'][0]
        delta=delta_view(old,new);reconstructed=copy.deepcopy(data['hediffs'])
        patch=delta['list_changes']['fields']['hediffs']
        from tools.rimworld.observations import apply_list_patch
        reconstructed=apply_list_patch(reconstructed,patch)
        self.assertEqual(reconstructed,new['data']['hediffs'])
        new['data']['hediffs'].append({'label':'New injury','severity':5})
        self.assertEqual(delta_view(old,new)['health']['hediffs'],new['data']['hediffs'])


    def test_cli_retrieve_keeps_full_provenance(self):
        import io
        from contextlib import redirect_stdout
        from tools.rimworld.cli import main
        r=self.ingest('get_pawn',{'id':'p'},{'id':'p','health':80})
        output=io.StringIO()
        with redirect_stdout(output):
            code=main(['--root',str(self.root),'--run','example','retrieve','--observation',r['id']])
        self.assertEqual(code,0)
        value=json.loads(output.getvalue())
        self.assertEqual(value['args'],{'id':'p'})
        self.assertEqual(value['origin'],'fixture')
        self.assertIn('data',value)

    def test_cli_selects_once_and_marks_only_local_selector_failure(self):
        import io
        from contextlib import redirect_stdout
        from tools.rimworld.cli import main
        completed={'id':'obs-completed','data':{'cause':'timeout','ticksWaited':500}}
        base=['--root',str(self.root),'--run','example','call','rw_read','--args','{}','--token','owner-test']
        output=io.StringIO()
        with patch('tools.rimworld.cli.run',return_value=completed),redirect_stdout(output):
            code=main(base+['--select','/data/cause','--select','/data/ticksWaited'])
        self.assertEqual(code,0);self.assertEqual(json.loads(output.getvalue()),
            {'/data/cause':'timeout','/data/ticksWaited':500})
        output=io.StringIO()
        with patch('tools.rimworld.cli.run',return_value=completed),redirect_stdout(output):
            code=main(base+['--select','/data/missing'])
        failure=json.loads(output.getvalue())
        self.assertEqual(code,2);self.assertTrue(failure['operation_completed'])
        self.assertEqual(failure['phase'],'local_selection');self.assertIn('Do not replay',failure['replay'])
        self.assertEqual(failure['evidence'],['obs-completed'])


    def test_hidden_handoff_reads_cannot_be_delta_baseline(self):
        from tools.rimworld.core import now
        data={'id':'p','overallHealthPercent':70,'hediffs':[{'label':'Injury','severity':3}]}
        self.ingest('get_pawn',{'id':'p','tab':'health'},data)
        self.camp.meta['presentation_reset_at']=now()
        atomic_json(self.camp.path/'campaign.json',self.camp.meta)
        first=self.ingest('get_pawn',{'id':'p','tab':'health'},data)
        self.assertEqual(first['health']['hediffs'],data['hediffs'])
        self.assertNotIn('unchanged',first)
        second=self.ingest('get_pawn',{'id':'p','tab':'health'},data)
        self.assertTrue(second['unchanged'])


    def test_real_empty_fire_response_requires_explicit_zero_count(self):
        args={'mapIndex':0}
        o=normalize('list_fires',args,{'ok':True,'mapIndex':0,'fireCount':0},'c','s','fixture')
        self.assertEqual(o['completeness'],'known')
        self.assertEqual(o['data']['fires'],[])
        self.assertIn('fireCount=0',o['coverage']['known_empty_basis'])
        for data in [{'ok':True},{'ok':True,'fireCount':1},{'ok':True,'fireCount':False},{'ok':False,'fireCount':0},{'ok':True,'fireCount':0,'truncated':True}]:
            self.assertNotEqual(normalize('list_fires',args,data,'c','s','fixture')['completeness'],'known')


    def test_alert_priority_preserves_agent_review_without_guessing_unknowns(self):
        from tools.rimworld.safety import signals
        for priority, expected in [('High','review'), ('Medium','review'), ('Low','review'),
                                   ('Critical','critical'), ('NewModPriority','unknown'),
                                   (3,'unknown'), (None,'unknown')]:
            alert={'label':'Arbitrary alert, not a strategy whitelist','priority':priority,'explanation':'Keep this evidence'}
            obs=normalize('get_alerts',{}, {'activeAlerts':[alert]},'c','s','fixture')
            found=[s for s in signals(obs) if s['kind']=='alert']
            self.assertEqual(len(found),1)
            self.assertEqual(found[0]['severity'],expected)
            self.assertEqual(found[0]['value'],alert)
