"""Offline, complete capability discovery. Catalog data never grants permission."""
from pathlib import Path
from . import __version__
from functools import lru_cache
import re
from .core import Error,read_json

@lru_cache(maxsize=1)
def default_effects():
    return read_json(Path(__file__).resolve().parents[2]/'api/effects.json')['tools']

def discover(root, query='', tool=None, campaign=None):
    path=(campaign.path/'raw/catalog.json') if campaign else Path(root)/'api/catalog.json'
    catalog=read_json(path)
    from .control import effect
    from .composition import TOOLS
    catalog=dict(catalog,tools=dict(catalog['tools']))
    if set(TOOLS) & set(catalog['tools']):raise Error('Local composition name collides with upstream catalog.')
    catalog['tools'].update(TOOLS)
    def classification(name):return ('composition-read' if name=='rw_observe' else 'guarded-mutation') if name in TOOLS else effect(name,{})
    if tool:
        if tool not in catalog['tools']:raise Error('Tool not present in this catalog.')
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

def spatial(observation, rect=None, ids=None):
    """Explicit local selection, with provenance and omitted counts; no live refresh."""
    from .observations import pack_rows
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
            'unlocated_or_malformed':unknown,'things':pack_rows(selected),
            'terrain':observation['data'].get('terrainSummary'),
            'terrain_scope':'Original query scope; not recomputed for the selection',
            'live_checked':False,'limitations':'Recorded positions only; no inferred line of sight, reachability or placement validity.'}
