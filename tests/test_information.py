import copy,json,unittest
from tools.rimworld.observations import normalize,compact,delta_view,pack_rows,unpack_rows,apply_list_patch
from tools.rimworld.presentation import present

class Information(unittest.TestCase):
    def obs(self,tool,data,args=None):return normalize(tool,args or {},data,'c','s','fixture')
    def test_novel_properties_survive_spatial_compaction(self):
        rows=[{'id':str(i),'def':'Steel','x':i,'z':2,'unfamiliar':{'state':'interesting'}} for i in range(40)]
        d={'things':rows,'terrainSummary':{},'unexpected':{'opportunity':True}}
        v=present(compact(self.obs('get_area',d)))
        self.assertEqual(v['data']['unexpected'],d['unexpected'])
        self.assertEqual(unpack_rows(v['data']['things']),rows)
        self.assertLess(len(json.dumps(v['data'])),len(json.dumps(d)))
    def test_null_absent_and_order_round_trip(self):
        rows=[{'id':str(i),'longname':None,'anotherlongname':i} for i in range(40)]
        del rows[2]['longname'];rows[3]['novel']=False
        self.assertEqual(unpack_rows(pack_rows(rows)),rows)
    def test_summary_model_and_unmodeled_visible(self):
        s=self.obs('list_things',{'groups':[]},{'summary':True})
        self.assertEqual(s['completeness'],'known')
        self.assertEqual(present(compact(s))['query_kind'],'aggregate')
        s=self.obs('get_anomaly',{'novel':1})
        self.assertEqual(present(compact(s))['model'],'unmodeled')
    def test_entity_changes_include_all_properties(self):
        old=self.obs('list_things',{'things':[{'id':str(i),'def':'Steel','x':i} for i in range(40)]})
        new=copy.deepcopy(old);new['id']='new';new['data']['things'][9]['novel']=True
        v=present(delta_view(old,new));self.assertEqual(apply_list_patch(old['data']['things'],v['list_changes']['fields']['things']),new['data']['things'])
    def test_partial_known_rows_not_clipped(self):
        rows=[{'id':str(i),'new':i} for i in range(50)]
        v=present(compact(self.obs('list_things',{'things':rows,'truncated':True})))
        self.assertEqual(unpack_rows(v['known_subset']['things']),rows)
        self.assertEqual(v['completeness'],'partial')

from test_system import ControlFixture,Workspace
from tools.rimworld.outcomes import contract
from tools.rimworld.knowledge import recall
class Intentions(ControlFixture):
    def test_explicit_general_intention_is_tracked_without_claiming_completion(self):
        self.responses.append({'ok':True})
        r=self.control.call(self.token,'order_pawn',{'id':'PawnA','command':'Ordinary task'},intent='Observe its actual outcome',track=True)
        actions=list(self.camp._actions().values())
        self.assertEqual(len(actions),1);self.assertEqual(actions[0]['status'],'accepted')
    def test_unknown_family_with_explicit_check(self):
        check=contract({'family':'new-mechanic','checks':[{'tool':'get_pawn','args':{'id':'p'},'all':[{'path':'someNewValue','op':'eq','value':3}]}]})
        a=self.camp.action('normal_ui',{},'Complete newly discovered mechanic','new-mechanic',check,origin='fixture')
        self.assertEqual(a['status'],'requested')
        self.assertEqual(a['family'],'new-mechanic')
    def test_recall_preserves_pending_question_without_claiming_freshness(self):
        self.camp.action('normal_ui',{},'Investigate gravship foundation','ship-investigation',origin='fixture')
        r=recall(self.camp,'gravship')
        self.assertEqual(len(r['pending_intentions']),1)
        self.assertFalse(r['live_checked'])

from test_monitor import ScenarioSetup
from tools.rimworld.monitor import create_plan,coverage
from tools.rimworld.core import Error
class ObservationPolicy(ScenarioSetup):
    def test_additional_patient_requires_own_health_and_needs(self):
        spec=copy.deepcopy(self.spec);spec['watch_patients']=['prisoner']
        plan=create_plan(self.camp,spec);obs=[]
        for query,data in zip(plan['queries'],self.safe_reads()):
            r=self.camp.ingest(query['tool'],query.get('args',{}),data,origin='live')
            obs += [self.camp.observation(x['id']) for x in [r,*r.get('bundle',[])]]
        gaps=coverage(self.camp,obs,plan)
        self.assertEqual({g['args']['tab'] for g in gaps if g.get('args',{}).get('id')=='prisoner'},{'health','needs'})
    def test_mandatory_safety_cadence_cannot_silently_skip(self):
        spec=copy.deepcopy(self.spec);spec['queries'][0]['every_cycles']=2
        with self.assertRaises(Error):create_plan(self.camp,spec)

class Novelty(unittest.TestCase):
    def test_shape_notice_preserves_value(self):
        old=normalize('get_status',{}, {'loaded':False},'c','s','fixture')
        new=normalize('get_status',{}, {'loaded':False,'futureFeature':{'value':2}},'c','s','fixture')
        v=present(delta_view(old,new))
        self.assertIn('$/futureFeature/value:number',v['structure_changes']['added_paths'])
        self.assertEqual(v['status']['futureFeature']['value'],2)
    def test_known_hidden_targeting_exclusion_is_explicit_and_raw_unchanged(self):
        d={'things':[{'id':'enemy','hostile':True,'targeting':'hidden AI goal','novelVisible':7}]}
        obs=normalize('list_things',{},d,'c','s','fixture')
        self.assertIn('targeting',d['things'][0])
        self.assertNotIn('targeting',obs['data']['things'][0])
        self.assertEqual(obs['data']['things'][0]['novelVisible'],7)
        self.assertIn('_visibilityExclusions',obs['data'])

class IndexView(unittest.TestCase):
    def test_index_keeps_warning_and_discovery_without_repeating_payload(self):
        from tools.rimworld.observations import evidence_index
        o=normalize('get_pawn',{'id':'p','tab':'health'},
            {'loaded':True,'id':'p','downed':True,'hediffs':[{'label':'infection','severity':.8}],
             'novelMechanic':{'unrecognized':[1,2,3]}},'c','s','fixture')
        v=evidence_index(o)
        self.assertTrue(v['scalars']['downed'])
        self.assertEqual(v['nested']['novelMechanic']['keys'],['unrecognized'])
        self.assertTrue(any(x['kind']=='incapacitated' for x in v['risks']))
        self.assertEqual(v['id'],o['id']);self.assertNotIn('health',v)
        self.assertEqual(o['data']['hediffs'][0]['label'],'infection')
    def test_schedule_query_and_change_have_different_effects(self):
        from tools.rimworld.control import effect
        self.assertEqual(effect('set_schedule',{'id':'p'}),'inspection-ui')
        self.assertEqual(effect('set_schedule',{'id':'p','assignment':'Sleep'}),'mutation')
    def test_argument_error_exposes_available_names(self):
        from tools.rimworld.mcp import validate
        with self.assertRaisesRegex(Error,'allowed fields.*id'):
            validate({'type':'object','properties':{'id':{'type':'integer'}}},{'questId':22})

class ShapeLineage(Workspace):
    def test_reappearing_shape_is_not_novel_but_values_remain(self):
        first=self.ingest('wait_for_event',{}, {'ok':True,'pausedAfter':True,'ticksWaited':1,'cause':'timeout','novel':{'x':1}})
        self.ingest('wait_for_event',{}, {'ok':True,'pausedAfter':True,'ticksWaited':1,'cause':'timeout'})
        last=self.ingest('wait_for_event',{}, {'ok':True,'pausedAfter':True,'ticksWaited':1,'cause':'timeout','novel':{'x':2}})
        self.assertNotIn('structure_changes',last)
        self.assertEqual(last['data']['novel'],{'x':2})
        new=self.ingest('wait_for_event',{}, {'ok':True,'pausedAfter':True,'ticksWaited':1,'cause':'timeout','novel':{'x':'changed type'}})
        self.assertIn('$/novel/x:string',new['structure_changes']['added_paths'])
    def test_session_change_does_not_inherit_shape_lineage(self):
        self.camp.ingest('get_quest',{}, {'a':{'x':1}},origin='fixture',session_id='old')
        self.camp.ingest('get_quest',{}, {'b':1},origin='fixture',session_id='new')
        r=self.camp.ingest('get_quest',{}, {'a':{'x':1}},origin='fixture',session_id='new')
        self.assertIn('$/a/x:number',r['structure_changes']['added_paths'])

class ZeroRejections(unittest.TestCase):
    def test_zero_rejections_do_not_interrupt_but_nonzero_and_unknown_do(self):
        from tools.rimworld.safety import signals
        def risks(value):
            o=normalize('manage_area',{}, {'ok':True,'rejected':value},'c','s','fixture')
            return [x for x in signals(o) if x['kind']=='rejected']
        self.assertFalse(risks(0));self.assertTrue(risks(1));self.assertTrue(risks('unknown'))

class RowUpdates(unittest.TestCase):
    def test_patch_preserves_absence_null_new_fields_and_reordering(self):
        from tools.rimworld.observations import make_list_patch,apply_list_patch,pack_rows
        old=[{'id':'p'+str(i),'biography':'long biography '*30,'mood':50,'optional':None} for i in range(20)]
        new=copy.deepcopy(old);new[0]['mood']=49;del new[0]['optional'];new[1]['new_mod_value']=None
        new[2],new[3]=new[3],new[2]
        patch=make_list_patch(old,new)
        self.assertEqual(apply_list_patch(pack_rows(old),patch),new)
        self.assertIn('0',patch['update']);self.assertIn('2',patch['replace'])
        bad=copy.deepcopy(old);bad[0]['id']='another'
        with self.assertRaises(ValueError):apply_list_patch(bad,patch)
