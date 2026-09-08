"""Agent-facing output only. Full observations, risk fingerprints and provenance stay durable."""

import json


def _value_key(value):
    # JSON encoding distinguishes false/0 and nested type changes.
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False)


def _value_paths(value, path='#'):
    """Index exact already-visible values; references never cross a response."""
    result = {}
    def visit(node, pointer):
        if isinstance(node, (dict, list)):
            key = _value_key(node)
            if key not in result or len(pointer) < len(result[key]):
                result[key] = pointer
            entries = node.items() if isinstance(node, dict) else enumerate(node)
            for name, child in entries:
                escaped = str(name).replace('~', '~0').replace('/', '~1')
                visit(child, pointer + '/' + escaped)
    visit(value, path)
    return result


def present(value):
    if isinstance(value,list): return [present(v) for v in value]
    if not isinstance(value,dict): return value
    if all(k in value for k in ('kind','severity','acknowledgeable','evidence')):
        card={k:value[k] for k in ('kind','severity','evidence')}
        card['value']={k:v for k,v in value['value'].items() if k not in ('conditions_digest','detail')} if isinstance(value.get('value'),dict) else value.get('value')
        if value.get('scope',{}).get('id'):card['subject']=value['scope']['id']
        if 'freshness' in value:card['freshness']=value['freshness']
        return card
    if not (str(value.get('id','')).startswith('obs-') and 'completeness' in value):
        return {k:present(v) for k,v in value.items()}
    result={'id':value['id']}
    # Keep actual game facts and explicit omissions/uncertainty. Do not repeat
    # arguments, wall timestamps, origin, scope, raw path and empty metadata on
    # every read; the observation ID resolves all of them.
    for key in ('data','health','needs','status','counts','total','terrain','known_subset','message','model','query_kind','structure_changes',
                'omitted','list_changes','action_id','identity_mismatch','pause_guard','bundle'):
        if key in value and value[key] is not None: result[key]=present(value[key])
    if value['completeness']!='known':
        result['completeness']=value['completeness']
        result['missing']=value.get('missing',[])
        result['coverage']=value.get('coverage')
    delta=value.get('delta',{})
    if value.get('unchanged'):result['unchanged']=True
    elif 'changed_fields' in delta:result['changed_fields']=delta['changed_fields']
    if delta.get('not_returned_now'):result['not_returned_now']=delta['not_returned_now']
    if 'changed_fields' in delta or value.get('unchanged'):
        result['previous']=delta.get('previous_evidence')
    bodies=[value.get(k,{}) for k in ('data','health','needs','status','known_subset')]
    warnings={k:v for k,v in value.get('warnings',{}).items() if not any(isinstance(b,dict) and k in b and _value_key(b[k]) == _value_key(v) for b in bodies)}
    if warnings:result['warnings']=warnings
    # Classification remains explicit. Reference an exact value already shown
    # in this observation instead of copying it. Unchanged/partial/delta reads
    # retain any value absent from their visible body, including novel risks.
    paths = _value_paths(result) if value.get('risks') else {}
    risks=[]
    for risk in value.get('risks',[]):
        card={'kind':risk['kind'],'severity':risk['severity']}
        risk_value = ({k:v for k,v in risk['value'].items() if k not in ('conditions_digest','detail')}
                      if isinstance(risk.get('value'),dict) else risk.get('value'))
        pointer = paths.get(_value_key(risk_value))
        if pointer is not None and len(_value_key({'value_ref':pointer})) < len(_value_key({'value':risk_value})):
            card['value_ref'] = pointer
        else:
            card['value'] = risk_value
        if risk.get('scope',{}).get('id'): card['subject']=risk['scope']['id']
        risks.append(card)
    if risks:result['risks']=risks
    safety=value.get('safety')
    if safety and safety.get('stop'):result['requires_review']=True
    if safety and safety.get('acknowledged_ids'):result['acknowledged_risks']=len(safety['acknowledged_ids'])
    return result
