import json
from test_system import Workspace
from tools.rimworld.continuity import handoff
from tools.rimworld.runs import resume_run
from tools.rimworld.observations import evidence_index


class StartupNavigation(Workspace):
    def test_unknown_warning_index_retains_scope_and_full_evidence(self):
        data={'loaded':True,'id':'patient','downed':True,
              'hediffs':[{'label':'novel infection','severity':0.8}],
              'warning':{'label':'Unknown mechanism','events':[{'unexpected':False}]*80}}
        result=self.ingest('get_pawn',{'id':'patient','tab':'health'},data)
        original=self.camp.observation(result['id'])
        index=evidence_index(original)
        self.assertTrue(index['scalars']['downed'])
        self.assertIn('warning',index['warnings'])
        risk=next(v for v in index['risks'] if v['kind']=='warning')
        self.assertEqual(risk['scalars']['label'],'Unknown mechanism')
        self.assertIn('events',risk['nested_fields'])
        self.assertTrue(risk['retrieve_required'])
        self.assertIn('novel infection',json.dumps(index['details']))
        self.assertEqual(self.camp.observation(result['id'])['data'],original['data'])
        self.assertLess(len(json.dumps(index)),len(json.dumps(original)))

    def test_resume_defaults_to_index_but_full_snapshot_remains_available(self):
        self.ingest('get_status',{}, {'loaded':True,'ticksGame':1,'warning':{'novel':['fact']*100}})
        self.camp.issue({'title':'Unresolved','rationale':'Unknown condition','next_action':'Inspect',
                         'revisit':'Before playing','resolution':'Concrete evidence','critical':True})
        result=handoff(self.camp,'Context boundary','Inspect unresolved condition','Unknown until revalidated')
        before={str(p):p.read_bytes() for p in self.camp.path.rglob('*') if p.is_file()}
        lean=resume_run(self.root,'example')['handoff']['snapshot']
        full=resume_run(self.root,'example',full=True)['handoff']['snapshot']
        self.assertNotIn('packet',lean)
        self.assertIn('packet_index',lean)
        self.assertIn('Unknown until revalidated',lean['uncertainties'])
        self.assertTrue(full['packet']['issues'])
        self.assertEqual(lean['packet_index']['active_risk_records'],len(full['packet']['active_risks']))
        self.assertEqual(before,{str(p):p.read_bytes() for p in self.camp.path.rglob('*') if p.is_file()})
