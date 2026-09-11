"""Offline, complete capability discovery. Catalog data never grants permission."""
from pathlib import Path
from . import __version__
from functools import lru_cache
import difflib
import re
from .core import Error,read_json

DOMAINS = {
    'setup': ('main_menu','game_setup_status','select_scenario','select_storyteller','create_world',
              'choose_ideoligion','edit_ideoligion','edit_starting_pawn','find_world_tiles',
              'select_starting_site','start_game'),
    'colony': ('get_status','list_colonists','get_alerts','get_resources','get_conditions','get_research'),
    'pawns': ('get_pawn','order_pawn','draft','set_work_priority','set_schedule','set_allowed_area',
              'manage_gear','assign_building'),
    'medical': ('get_pawn','list_surgeries','add_surgery','set_medical_care','order_pawn'),
    'food': ('get_resources','list_things','list_bills','add_bill','set_work_priority','order_pawn'),
    'combat': ('get_status','list_things','list_fires','get_area','draft','order_pawn','manage_gear'),
    'building': ('get_map','get_area','list_architect','build','inspect_thing','do_thing_action','manage_zone'),
    'world': ('get_world','list_world_objects','get_world_tile','find_world_tiles','form_caravan',
              'caravan_action','world_object_action'),
    'quests': ('get_world','read_letter','get_quest','quest_action'),
    'trade': ('list_trade','set_trade','trade_action','get_window_ui','window_action'),
    'production': ('inspect_thing','list_bills','list_recipes','add_bill','delete_bill','get_resources'),
}

WORKFLOWS = {
    'new_game': ('main_menu','game_setup_status','select_scenario','select_storyteller','create_world',
                 'game_setup_status','choose_ideoligion','edit_ideoligion','select_starting_site',
                 'edit_starting_pawn','start_game','game_setup_status','get_status','get_map'),
    'medical_event': ('get_status','get_pawn','set_medical_care','order_pawn','list_surgeries','add_surgery'),
    'combat_event': ('get_status','list_things','list_fires','get_area','draft','order_pawn','rw_wait'),
    'caravan': ('list_world_objects','form_caravan','caravan_action','get_world_tile','world_object_action'),
    'food_crisis': ('get_status','get_resources','list_things','list_bills','set_work_priority','order_pawn'),
    'trade': ('list_trade','set_trade','list_trade','trade_action'),
    'resume_crisis': ('get_status','rw_observe','read_letter','get_pawn','list_things','draft','order_pawn','rw_wait'),
}

@lru_cache(maxsize=1)
def default_effects():
    return read_json(Path(__file__).resolve().parents[2]/'api/effects.json')['tools']

def discover(root, query='', tool=None, campaign=None):
    path=(campaign.path/'raw/catalog.json') if campaign else Path(root)/'api/catalog.json'
    catalog=read_json(path)
    from .control import effect
    from .facade import LOCAL_EFFECTS, local, reserved
    TOOLS=local()
    catalog=dict(catalog,tools=dict(catalog['tools']))
    reserved(catalog)
    catalog['tools'].update(TOOLS)
    def classification(name):return LOCAL_EFFECTS[name] if name in TOOLS else effect(name,{})
    if tool:
        if tool not in catalog['tools']:
            names=list(catalog['tools'])
            close=difflib.get_close_matches(tool,names,n=5,cutoff=.35)
            stem=set(re.findall(r'[a-z0-9]+',tool.lower().replace('_',' ')))
            related=[name for name in names if stem and stem & set(name.lower().split('_'))]
            suggestions=list(dict.fromkeys(close+related))[:5]
            suffix=(' Did you mean: '+', '.join(suggestions)+'?' if suggestions else ' Search with query or a capability domain/workflow.')
            raise Error('Tool not present in this catalog.'+suffix)
        provenance=({'origin':'local','local_version':__version__,
                     'upstream_catalog_captured_at':catalog.get('captured_at')} if tool in TOOLS else
                    {'origin':'upstream','captured_at':catalog.get('captured_at')})
        return {'tool':catalog['tools'][tool],'default_effect':classification(tool),**provenance,
                'live_checked':False,
                'limitation':'No output schemas; current offered actions and run rules govern execution. Inspect argument-dependent effects.'}
    words=re.findall(r'[a-z0-9]+',query.lower())
    items=[]
    for name,t in catalog['tools'].items():
        text=(name+' '+t.get('description','')).lower()
        if not all(w in text for w in words):continue
        items.append({'tool':name,'effect':classification(name),'origin':'local' if name in TOOLS else 'upstream',
                      'description':t.get('description','').split('. ')[0]})
    return {'matches':items,'total':len(items),'catalog_tools':len(catalog['tools']),
            'captured_at':catalog.get('captured_at'),'live_checked':False,
            'detail':'capabilities --tool NAME; complete declarations on demand, no automatic execution'}


def overview(root, campaign=None, domain=None, workflow=None):
    """Compact affordance map: names and one-line purposes, never full schemas."""
    path=(campaign.path/'raw/catalog.json') if campaign else Path(root)/'api/catalog.json'
    catalog=read_json(path)
    from .facade import local, reserved
    merged=dict(catalog['tools']);reserved(catalog);merged.update(local())
    if domain is not None and domain not in DOMAINS: raise Error('Unknown capability domain: '+domain)
    if workflow is not None and workflow not in WORKFLOWS: raise Error('Unknown capability workflow: '+workflow)
    def one(name):
        if name not in merged:return None
        return {'tool':name,'purpose':merged[name].get('description','').split('. ')[0]}
    if workflow is not None:
        steps=[one(name) for name in WORKFLOWS[workflow]]
        return {'workflow':workflow,'steps':[v for v in steps if v],
                'note':'Ordered affordance guide, not permission or proof that the current UI stage supports each step.'}
    names={domain:DOMAINS[domain]} if domain else DOMAINS
    return {'domains':{key:[v for v in (one(name) for name in values) if v] for key,values in names.items()},
            'workflows':sorted(WORKFLOWS),'detail':'Fetch one exact schema with rw_capabilities {tool:NAME}.'}

def spatial(observation, rect=None, ids=None):
    """Explicit local selection, with provenance and omitted counts; no live refresh."""
    rows=observation['data'].get('things')
    if not isinstance(rows,list):raise Error('Spatial retrieval requires entity rows, not an aggregate.')
    if rect is not None:
        if len(rect)!=4 or rect[0]>rect[1] or rect[2]>rect[3]:raise Error('Use minX maxX minZ maxZ.')
    selected=[];unknown=[]
    for r in rows:
        if not isinstance(r,dict):unknown.append(r);continue
        if ids and r.get('id') not in ids:continue
        if rect:
            if type(r.get('x')) not in (int,float) or type(r.get('z')) not in (int,float):unknown.append(r);continue
            if not (rect[0]<=r['x']<=rect[1] and rect[2]<=r['z']<=rect[3]):continue
        selected.append(r)
    return {'observation':observation['id'],'map_index':observation.get('map_index'),
            'source_captured_at':observation.get('source_captured_at'),'origin':observation['origin'],
            'completeness':observation['completeness'],'coverage':observation.get('coverage'),
            'selection':{'rect':rect,'ids':ids},'selected':len(selected),'source_rows':len(rows),
            'excluded_by_selection':len(rows)-len(selected)-len(unknown),
            'unlocated_or_malformed':unknown,'things':selected,
            'terrain':observation['data'].get('terrainSummary'),
            'terrain_scope':'Original query scope; not recomputed for the selection',
            'live_checked':False,'limitations':'Recorded positions only; no inferred line of sight, reachability or placement validity.'}
