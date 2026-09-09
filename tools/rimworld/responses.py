"""Faithful player-visible MCP results shared by ordinary and composed calls."""
import copy
import json
import math
from .core import Error, read_json
from .observations import visible_data


class AmbiguousJSON(ValueError):
    pass


def strict_json(text):
    def pairs(items):
        result = {}
        for key,value in items:
            if key in result: raise AmbiguousJSON('Duplicate JSON object key')
            result[key]=value
        return result
    def nonfinite(value):
        raise AmbiguousJSON('Nonfinite JSON number')
    def number(value):
        parsed=float(value)
        if not math.isfinite(parsed): return nonfinite(value)
        return parsed
    return json.loads(text,object_pairs_hook=pairs,parse_constant=nonfinite,parse_float=number)


def visible_result(campaign, observation):
    raw = read_json(campaign.path / observation['raw'])['payload']
    result = copy.deepcopy(raw.get('result', raw))
    if not isinstance(result, dict):
        raise Error('Unexpected MCP result shape; original evidence retained.')
    exclusions = []
    unusable = []
    for index, block in enumerate(result.get('content', [])):
        if block.get('type') != 'text':
            continue
        try:
            data = strict_json(block['text'])
        except AmbiguousJSON as exc:
            unusable.append({'block':index,'reason':str(exc)})
            block['text']='Unusable game JSON: '+str(exc)+'. Original retained in evidence; no facts inferred.'
            continue
        except (ValueError, TypeError):
            continue
        data, excluded = visible_data(data, observation['tool'])
        if excluded:
            block['text'] = json.dumps(data, ensure_ascii=False)
            exclusions.extend('content/'+str(index)+'/text/'+p for p in excluded)
    if 'structuredContent' in result:
        result['structuredContent'], excluded = visible_data(result['structuredContent'], observation['tool'])
        exclusions.extend('structuredContent/'+p for p in excluded)
    metadata = {'_evidence': observation['id']}
    if unusable: metadata['unusable_json_blocks']=unusable
    if raw.get('_transportNotifications'):
        metadata['_transportNotifications'], excluded = visible_data(raw['_transportNotifications'], observation['tool'])
        exclusions.extend('_transportNotifications/'+p for p in excluded)
    if exclusions:
        metadata['visibility_exclusions'] = {'reason': 'Hostile AI targeting is not player-visible', 'paths': exclusions}
    if observation['completeness'] != 'known':
        metadata.update(completeness=observation['completeness'], missing=observation['missing'])
    return result, metadata


def section(campaign, observation):
    """Unwrap JSON text once; retain other content and every result property."""
    result, metadata = visible_result(campaign, observation)
    blocks = result.pop('content', [])
    value = {'source': {'observation': observation['id'], 'captured_at': observation['captured_at']},
             'coverage': {'state': observation['completeness']}}
    if observation.get('tick') is not None:
        value['source']['tick']=observation['tick']
        value['source']['tick_basis']=observation.get('tick_basis')
    if observation['missing']:value['coverage']['missing']=observation['missing']
    if observation.get('malformed'):value['coverage']['malformed']=observation['malformed']
    if blocks and blocks[0].get('type') == 'text':
        try:
            value['data'] = strict_json(blocks[0]['text'])
        except (ValueError, TypeError):
            pass
        else:
            annotations = {k:v for k,v in blocks[0].items() if k not in ('type', 'text')}
            if annotations: value['text_properties'] = annotations
            blocks = blocks[1:]
    if blocks: value['content'] = blocks
    # MCP defines omitted isError as false; keep true or malformed values and all unknown properties.
    if result.get('isError') is False:result.pop('isError')
    if result: value['result_properties'] = result
    metadata.pop('_evidence')
    if metadata: value['metadata'] = metadata
    return value
