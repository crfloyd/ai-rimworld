import copy,json,unittest
from tools.rimworld.observations import normalize,compact,delta_view,pack_rows,unpack_rows
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
        v=present(delta_view(old,new));self.assertTrue(v['list_changes']['fields']['things']['replace']['9']['novel'])
    def test_partial_known_rows_not_clipped(self):
        rows=[{'id':str(i),'new':i} for i in range(50)]
        v=present(compact(self.obs('list_things',{'things':rows,'truncated':True})))
        self.assertEqual(unpack_rows(v['known_subset']['things']),rows)
        self.assertEqual(v['completeness'],'partial')
