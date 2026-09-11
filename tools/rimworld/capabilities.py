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
    'colony': ('get_status','list_colonists','get_alerts','get_resources','get_conditions','get_research',
               'get_map','get_room','get_resource_readout','list_power_grids','list_unmanaged_items'),
    'pawns': ('get_pawn','order_pawn','draft','set_work_priority','set_schedule','set_allowed_area',
              'manage_gear','assign_building','rename_pawn','set_hostility_response','manage_prisoner'),
    'medical': ('get_pawn','list_surgeries','add_surgery','set_medical_care','order_pawn'),
    'food': ('get_resources','list_things','list_bills','add_bill','set_work_priority','order_pawn',
             'list_unmanaged_items','set_growing_zone','manage_food_policy','set_food_policy'),
    'combat': ('get_status','list_things','list_fires','get_area','draft','order_pawn','manage_gear',
               'set_hostility_response','list_mechs','set_mech_control'),
    'building': ('get_map','get_area','list_architect','build','inspect_thing','do_thing_action',
                 'list_zones','designate','get_room','room_graph','list_power_grids'),
    'zones': ('list_zones','select_zone','delete_zone','rename_zone','set_growing_zone',
              'set_stockpile_filter','set_stockpile_priority','manage_area','set_allowed_area','designate'),
    'world': ('get_world','list_world_objects','get_world_tile','find_world_tiles','form_caravan',
              'caravan_action','world_object_action','world_target'),
    'quests': ('get_world','read_letter','get_quest','quest_action'),
    'trade': ('get_alerts','list_things','get_pawn','order_pawn','list_trade','set_trade','trade_action',
              'get_window_ui','window_action','list_unmanaged_items'),
    'production': ('inspect_thing','list_bills','list_recipes','add_bill','set_bill','delete_bill',
                   'get_resources','set_research','list_study_targets','set_study'),
    'animals': ('list_animals','list_wildlife','manage_animal','manage_area'),
    'policies': ('list_policies','manage_food_policy','manage_apparel_policy','manage_drug_policy',
                 'set_food_policy','set_drug_policy','set_outfit','manage_area'),
    'inspection': ('inspect_thing','get_inspect_pane','get_info_card','list_windows','get_window_ui',
                   'get_room','room_graph','entity_codex','help','learning_helper','get_live_chat'),
    'culture': ('choose_ideoligion','edit_ideoligion','reform_ideoligion','set_ideo_role','get_royalty',
                'list_titles','manage_permits','use_permit','list_genes','create_xenogerm',
                'implant_xenogerm','get_anomaly'),
    'system': ('get_status','set_speed','wait_for_event','save_game','return_to_title','screenshot','say',
               'list_main_buttons'),
}

PURPOSE = {
    'setup': 'Create a world and colony from the main menu through the first landing.',
    'colony': 'Whole-colony state: status, colonists, alerts, stock, weather, research, rooms and power.',
    'pawns': 'One colonist: read them, order them, set work, schedule, area, gear and assignments.',
    'medical': 'Injury, illness, treatment priority and surgery.',
    'food': 'Ingredients, cooking bills, growing and the haulers who move it.',
    'combat': 'Threats, fires, drafting, positioning and gear for a fight.',
    'building': 'Place, inspect and operate structures; read the map and rooms around them.',
    'zones': 'Stockpiles, growing zones, allowed areas and designations.',
    'world': 'The planet map, other settlements and your caravans.',
    'quests': 'Letters, quests and their accept or decline actions.',
    'trade': 'Find a trader, open a deal, settle it and confirm the goods arrived.',
    'production': 'Work tables, bills, recipes and research.',
    'animals': 'Tame animals, wildlife and animal handling.',
    'policies': 'Food, drug, apparel and area policies applied to colonists.',
    'inspection': 'Read exactly what the player sees: inspect pane, info cards, open windows and help.',
    'culture': 'Ideoligion, royalty, genes, xenotypes and anomaly content.',
    'system': 'Game speed, supervised time, saving, screenshots and top-level UI.',
}

WORKFLOWS = {
    'new_game': (
        ('main_menu','Only valid at the entry screen.'),
        ('game_setup_status','Ask where you are and what the next legal step is; re-read it between stages.'),
        ('select_scenario','Pick by name.'),
        ('select_storyteller','Storyteller, difficulty and reload mode together.'),
        ('create_world','Asynchronous; poll game_setup_status until the starting-site stage.'),
        ('choose_ideoligion','Ideology only.'),
        ('edit_ideoligion','Ideology only.'),
        ('select_starting_site','Pick the landing tile.'),
        ('edit_starting_pawn','Fix starting colonists before the game begins; they are not editable afterward.'),
        ('start_game','Commits the setup.'),
        ('get_status','Confirm a colony is actually loaded before any colony read.'),
        ('get_map','Establish home coordinates once.'),
    ),
    'medical_event': (
        ('get_status','Danger and colonist state first.'),
        ('get_pawn','tab=health for hediffs, bleeding rate, the immunity race and capacities.'),
        ('set_medical_care','Medicine quality is a policy, not an order.'),
        ('order_pawn','Rescue, tend or prioritize a doctor; a receipt is not treatment.'),
        ('list_surgeries','Only what this pawn can actually receive.'),
        ('add_surgery','Queues an operation; it still needs a surgeon, medicine and time.'),
    ),
    'combat_event': (
        ('get_status','Danger rating and who is down.'),
        ('list_things','category=pawn faction=hostile for the actual attackers.'),
        ('list_fires','Fires spread and are often the larger loss.'),
        ('get_area','Bounded terrain and cover around the fight only.'),
        ('draft','A drafted colonist with a ranged weapon shoots at anything hostile, including a berserk colonist. '
                 'Do not draft an armed pawn beside one you want alive.'),
        ('order_pawn','Move, attack, or carry a downed pawn to a bed.'),
        ('rw_wait','Short horizons during a fight; the event packet reports who changed.'),
    ),
    'caravan': (
        ('list_world_objects','kind=caravans or kind=settlements. An unfiltered call trips the size guard.'),
        ('form_caravan','mode=status is the read form and is how a departure is verified.'),
        ('caravan_action','Move, rest or split an existing caravan.'),
        ('get_world_tile','Terrain and travel cost for the next leg.'),
        ('world_object_action','Interact with whatever the caravan reached.'),
    ),
    'food_crisis': (
        ('get_status','Confirm the alert and the colonist count it applies to.'),
        ('list_bills','Do this before concluding there are no ingredients. A suspended cooking bill looks exactly '
                      'like an empty larder, and the Low Food alert never mentions bills.'),
        ('get_resources','Stockpiled counts only. It does not see loose or forbidden food.'),
        ('list_unmanaged_items','Forbidden and unhauled food a human would see lying on the floor.'),
        ('list_things','category=item with a defName to locate one specific food on the map.'),
        ('add_bill','Add or unsuspend the meal bill once ingredients are confirmed.'),
        ('set_work_priority','A cook who will never cook is the other common cause.'),
        ('order_pawn','Prioritize the cook or a hauler directly.'),
    ),
    'trade': (
        ('get_alerts','A trade letter names an approaching trader and expires; read it before it is dismissed.'),
        ('list_things','Find the trader with category=pawn faction=neutral. Visiting traders are map pawns, not '
                       'list_world_objects caravans, so that world list can be legitimately empty while the trader '
                       'stands in your colony.'),
        ('get_pawn','tab=health on the intended negotiator. Social incapability blocks the deal outright and a '
                    'damaged talking capacity silently worsens prices.'),
        ('order_pawn','Execute "Trade with …" on the trader. The colonist walks there first, so the dialog is not '
                      'open yet and list_trade is not active yet.'),
        ('list_trade','Poll until active is true. returned below tradeableCount means rows were withheld.'),
        ('set_trade','One row per call. Do not batch these: every receipt carries the open-dialog review flag.'),
        ('trade_action','accept commits the deal and may leave the dialog plus a message box open.'),
        ('window_action','Dismiss a blocking message box before trade_action cancel.'),
        ('list_unmanaged_items','Bought goods drop on the ground at the trader, so get_resources still reads '
                                'pre-trade until a hauler moves them. This is how you confirm the deal delivered.'),
    ),
    'build_structure': (
        ('list_architect','Find the exact defName and footprint before guessing a cell.'),
        ('get_area','Bounded terrain and existing buildings where you intend to place it.'),
        ('build','A refusal carries placement.interactionCell and a reason. A cell can be empty and still be refused '
                 'because the new building\'s interaction spot overlaps a research bench, shelf or another interaction '
                 'spot. Read interactionCell, then try rot 0 through 3 before moving the cell: rotation moves the offset.'),
        ('inspect_thing','The inspect pane is where fuel, power and toggles live; a list_things row does not carry them.'),
        ('order_pawn','Prioritize a builder at the blueprint. A reply that the pawn is already working on it means the '
                      'intent is already met.'),
    ),
    'resume_crisis': (
        ('get_status','Identity, pause and danger before anything else.'),
        ('rw_observe','One decision packet instead of a read-per-fact rebuild.'),
        ('read_letter','The letter text is the only place the actual event is spelled out.'),
        ('get_pawn','Only the facets the next decision needs.'),
        ('list_things','Bounded and anchored; never the whole map.'),
        ('draft','Only once the target is chosen.'),
        ('order_pawn','Immediate order first, then queue=true for reviewed follow-up jobs.'),
        ('rw_wait','The longest horizon the current evidence justifies.'),
    ),
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


def overview(root, campaign=None, domain=None, workflow=None, full=False):
    """Compact affordance map: a domain index by default, never full schemas."""
    path=(campaign.path/'raw/catalog.json') if campaign else Path(root)/'api/catalog.json'
    catalog=read_json(path)
    from .facade import local, reserved
    merged=dict(catalog['tools']);reserved(catalog);merged.update(local())
    if domain is not None and domain not in DOMAINS: raise Error('Unknown capability domain: '+domain)
    if workflow is not None and workflow not in WORKFLOWS: raise Error('Unknown capability workflow: '+workflow)
    def one(name,note=None):
        if name not in merged:return None
        row={'tool':name,'purpose':merged[name].get('description','').split('. ')[0]}
        if note:row['note']=note
        return row
    if workflow is not None:
        entries=[(e,None) if isinstance(e,str) else e for e in WORKFLOWS[workflow]]
        steps=[one(name,note) for name,note in entries]
        return {'workflow':workflow,'steps':[v for v in steps if v],
                'note':'Ordered affordance guide, not permission or proof that the current UI stage supports each step.'}
    if domain is not None:
        return {'domains':{domain:[v for v in (one(name) for name in DOMAINS[domain]) if v]},
                'purpose':PURPOSE[domain],
                'detail':'Fetch one exact schema with rw_capabilities {tool:NAME}.'}
    if full:
        return {'domains':{key:[v for v in (one(name) for name in values) if v] for key,values in DOMAINS.items()},
                'purposes':PURPOSE,'workflows':sorted(WORKFLOWS),
                'detail':'Fetch one exact schema with rw_capabilities {tool:NAME}.'}
    return {'domains':{key:{'tools':len(values),'purpose':PURPOSE[key]} for key,values in DOMAINS.items()},
            'workflows':sorted(WORKFLOWS),
            'detail':'rw_capabilities {domain:"NAME"} lists one area, {workflow:"NAME"} gives an ordered guide, '
                     '{overview:true,full:true} lists every tool in every domain, {tool:"NAME"} returns one exact schema.'}


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
