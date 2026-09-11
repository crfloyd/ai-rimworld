import json,tempfile,unittest
from pathlib import Path
from tools.rimworld.capabilities import DOMAINS,PURPOSE,WORKFLOWS,discover,overview,spatial
from tools.rimworld.control import effect
from tools.rimworld.facade import LOCAL_EFFECTS,local
from tools.rimworld.mechanics import search,save
from tools.rimworld.observations import normalize,unpack_rows
from tools.rimworld.core import Error,canonical

ROOT=Path(__file__).resolve().parents[1]
EXCLUDED={'load_game'}


class Coverage(unittest.TestCase):
    def test_every_permitted_catalog_tool_appears_in_a_domain(self):
        catalog=set(json.loads((ROOT/'api/catalog.json').read_text())['tools'])
        covered={name for names in DOMAINS.values() for name in names}
        self.assertEqual(catalog-EXCLUDED-covered,set())

    def test_domains_name_only_real_tools(self):
        catalog=set(json.loads((ROOT/'api/catalog.json').read_text())['tools'])
        for domain,names in DOMAINS.items():
            for name in names:
                self.assertIn(name,catalog,domain+' names a missing tool: '+name)

    def test_every_domain_has_a_one_line_purpose(self):
        self.assertEqual(set(PURPOSE),set(DOMAINS))
        for text in PURPOSE.values():
            self.assertTrue(text and len(text)<160)

    def test_overview_is_a_small_index_not_every_tool(self):
        value=overview(ROOT)
        self.assertLess(len(canonical(value).encode()),2600)
        self.assertEqual(set(value['domains']),set(DOMAINS))
        self.assertEqual(value['domains']['trade']['tools'],len(DOMAINS['trade']))
        self.assertIn('purpose',value['domains']['trade'])
        self.assertNotIn('list_trade',canonical(value))

    def test_overview_full_returns_the_whole_map(self):
        value=overview(ROOT,full=True)
        self.assertIn('list_trade',canonical(value))
        self.assertIn('purpose',value['domains']['trade'][0])

    def test_one_domain_still_lists_its_tools(self):
        value=overview(ROOT,domain='trade')
        names=[row['tool'] for row in value['domains']['trade']]
        self.assertIn('order_pawn',names)
        self.assertIn('list_things',names)
        self.assertIn('list_unmanaged_items',names)

    def test_facade_domain_enum_matches_the_capability_map(self):
        from tools.rimworld.facade import CAPABILITY_DOMAINS
        self.assertEqual(set(CAPABILITY_DOMAINS),set(DOMAINS))

class Discovery(unittest.TestCase):
    def test_every_catalog_tool_discoverable_and_classified(self):
        cat=json.loads((ROOT/'api/catalog.json').read_text())
        self.assertEqual(discover(ROOT)['total'],len(cat['tools'])+len(local()))
        for n,t in local().items():
            self.assertEqual(discover(ROOT,tool=n)['default_effect'],LOCAL_EFFECTS[n])
        for n,t in cat['tools'].items():
            self.assertEqual(discover(ROOT,tool=n)['tool'],t)
            self.assertNotEqual(effect(n,{}),'unclassified')
        self.assertEqual(effect('not_yet_reviewed',{}),'unclassified')
        self.assertEqual(effect('spawn_pawn',{}),'denied')
        self.assertEqual(effect('order_pawn',{'command':'Attack'}),'mutation')
    def test_selected_spatial_properties_and_unknown_positions(self):
        obs=normalize('get_area',{}, {'things':[{'id':'a','x':2,'z':3,'novel':1},{'id':'b','x':50,'z':1},{'id':'c'}],'terrainSummary':{}},'c','s','recorded')
        r=spatial(obs,[0,4,0,4]);self.assertEqual(unpack_rows(r['things'])[0]['novel'],1)
        self.assertEqual(r['excluded_by_selection'],1);self.assertEqual(r['unlocated_or_malformed'],[{'id':'c'}])
        self.assertFalse(r['live_checked'])
    def test_global_knowledge_rebuild_and_status_applicability(self):
        with tempfile.TemporaryDirectory() as d:
            r=json.loads((ROOT/'knowledge/mechanics/gravship-foundation.json').read_text())
            save(d,r);out=search(d,'gravship',environment={'game_version':'1.6.4871','dlc':[]})
            self.assertEqual(out['total_matches'],1);self.assertEqual(out['matches'][0]['applicability_check']['status'],'check_required')
            Path(d,'.runtime/mechanics.sqlite').unlink()
            self.assertEqual(search(d,id=r['id'])['record']['body'],r['body'])
            r['status']='disputed';save(d,r)
            self.assertEqual(search(d,'gravship')['matches'][0]['status'],'disputed')
            self.assertTrue(list(Path(d,'knowledge/mechanics/revisions',r['id']).glob('*.json')))
            r['campaign_id']='other'
            with self.assertRaises(Error):save(d,r)
    def test_malformed_bank_is_visible_failure(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d,'knowledge/mechanics');p.mkdir(parents=True);(p/'broken.json').write_text('{}')
            with self.assertRaises(Error):search(d,'medicine')
