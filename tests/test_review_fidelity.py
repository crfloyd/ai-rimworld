"""Reproductions from independent review: types, session resets and uncertain delivery."""
import copy
import json
from unittest.mock import patch
from test_system import Workspace, ControlFixture, fixture
from tools.rimworld.observations import normalize, delta_view, make_list_patch, apply_list_patch, same_value


class PresentationFidelity(Workspace):
    def test_new_session_full_root_and_bundle_then_same_session_delta(self):
        data={'loaded':True,'ticksGame':123,'maps':[],
              'bundled':{'get_pawn':{'id':'p','newField':False}}}
        self.camp.ingest('get_status',{},data,origin='fixture',session_id='one')
        result=self.camp.ingest('get_status',{},data,origin='fixture',session_id='two')
        self.assertTrue(result['status']['loaded'])
        self.assertIs(result['bundle'][0]['data']['newField'],False)
        for view in [result,*result['bundle']]:
            self.assertNotIn('unchanged',view)
            self.assertTrue(view['delta']['first_observation'])
        following=self.camp.ingest('get_status',{},data,origin='fixture',session_id='two')
        self.assertTrue(following['unchanged'])
        self.assertTrue(following['bundle'][0]['unchanged'])

    def test_scalar_and_nested_type_changes_survive_presentation_and_row_patches(self):
        for before,after in [(0,False),(False,0),(1,True),(True,1),(0,0.0),
                             ({'x':[0]}, {'x':[False]}),([{'x':1}],[{'x':True}])]:
            old=normalize('get_pawn',{'id':'p'},{'id':'p','value':before},'c','s','fixture')
            new=normalize('get_pawn',{'id':'p'},{'id':'p','value':after},'c','s','fixture')
            result=delta_view(old,new)
            self.assertIn('value',result['delta']['changed_fields'])
            self.assertEqual(json.dumps(result['data']['value']),json.dumps(after))
            baseline=[{'id':'p','unchanged':'x'*500,'value':before}]
            current=[{'id':'p','unchanged':'x'*500,'value':after}]
            reconstructed=apply_list_patch(baseline,make_list_patch(baseline,current))
            self.assertEqual(json.dumps(reconstructed,sort_keys=True),json.dumps(current,sort_keys=True))
        self.assertTrue(same_value({'a':[0,False,None]},{'a':[0,False,None]}))

    def test_type_changed_row_identity_is_not_same_entity(self):
        baseline=[{'id':0,'value':'old'}]
        current=[{'id':False,'value':'new'}]
        reconstructed=apply_list_patch(baseline,make_list_patch(baseline,current))
        self.assertIs(reconstructed[0]['id'],False)
        with self.assertRaises(ValueError):
            apply_list_patch(baseline,{'length':1,'update':{'0':{'identity':False,'set':{'value':'new'}}}})

    def test_direct_delta_rejects_another_lineage(self):
        old=normalize('get_pawn',{'id':'p'},{'id':'p','value':3},'c','s','fixture')
        for key,value in [('session_id','other'),('campaign_id','other'),('origin','live'),('scope',{'id':'other'}),('presentation_version',None)]:
            new=copy.deepcopy(old);new[key]=value
            result=delta_view(old,new)
            self.assertEqual(result['data']['value'],3)
            self.assertNotIn('unchanged',result)


class ControllerDelivery(ControlFixture):
    def test_reconnect_first_status_is_full(self):
        self.control.connect(self.token)
        self.responses.append(fixture('status'))
        result=self.control.call(self.token,'get_status',{})
        self.assertTrue(result['status']['loaded'])
        self.assertNotIn('unchanged',result)
        self.assertIn('presentation_reset_at',self.camp.meta)

    def test_post_ingest_failure_resets_unseen_baseline_without_replay(self):
        data={'id':'p','newField':False}
        self.responses.append(data)
        with patch('tools.rimworld.control.assess',side_effect=RuntimeError('Delivery failed after persistence')):
            with self.assertRaises(RuntimeError):self.control.call(self.token,'get_pawn',{'id':'p'})
        self.assertTrue((self.control.path/'pending.json').exists())
        self.assertIn('presentation_reset_at',self.camp.meta)
        calls=len(self.calls)
        # Inspect local presentation only: no replay or clearing of the uncertain game request.
        result=self.camp.ingest('get_pawn',{'id':'p'},data,origin='live')
        self.assertIs(result['data']['newField'],False)
        self.assertNotIn('unchanged',result)
        self.assertEqual(len(self.calls),calls)
        self.assertTrue((self.control.path/'pending.json').exists())
