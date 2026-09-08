"""Reusable, conservative outcome contracts. Missing response fields remain unknown."""
from .core import Error, require_fields


def eq(path, value): return {'path': path, 'op': 'eq', 'value': value}


def contract(spec):
    require_fields(spec, ('family',))
    if spec.get('checks'):
        validate_check({'checks':spec['checks']})
        return {'checks':spec['checks'],'contract':spec,'limitation':'Agent-supplied checks; fresh complete scoped evidence still required.'}
    family = spec['family']; checks = []
    if family in ('movement', 'rescue'):
        require_fields(spec, ('pawn', 'mapIndex', 'x', 'z'))
        predicates = [eq(k, spec[k]) for k in ('mapIndex', 'x', 'z')]
        if family == 'rescue':
            predicates.append(eq('inBed', True))
            if not spec.get('safety_checks'): raise Error('Rescue needs explicit fresh refuge hazard checks as well as bed/position evidence.')
        checks.append({'tool': 'get_pawn', 'args': {'id': spec['pawn']}, 'all': predicates})
    elif family == 'equipment':
        require_fields(spec, ('pawn', 'slot', 'item_label'))
        if spec['slot'] not in ('equipment', 'apparel'): raise Error('Equipment completion requires equipped/worn, not inventory.')
        checks.append({'tool': 'get_pawn', 'args': {'id': spec['pawn'], 'tab': 'gear'},
                       'all': [{'path': spec['slot'], 'op': 'any_item', 'all': [eq('label', spec['item_label'])]}]})
    elif family == 'construction':
        require_fields(spec, ('mapIndex', 'x', 'z', 'def'))
        if spec['def'].lower().startswith(('frame_', 'blueprint_')): raise Error('Specify the completed building definition.')
        checks.append({'tool': 'get_area', 'args': {'mapIndex': spec['mapIndex'], 'minX': spec['x'], 'maxX': spec['x'],
                                                   'minZ': spec['z'], 'maxZ': spec['z']},
                       'all': [{'path': 'things', 'op': 'any_item', 'all': [eq(k, spec[k]) for k in ('def', 'x', 'z')]}]})
    elif family == 'extinguishing':
        require_fields(spec, ('mapIndex',))
        checks.append({'tool': 'list_fires', 'args': {'mapIndex': spec['mapIndex']}, 'all': [eq('fires', [])]})
    elif family == 'treatment':
        require_fields(spec, ('pawn', 'condition', 'treatment_tick_field', 'after_tick', 'field_review'))
        checks.append({'tool': 'get_pawn', 'args': {'id': spec['pawn'], 'tab': 'health'}, 'all': [
            {'path': 'hediffs', 'op': 'any_item', 'all': [eq('label', spec['condition']),
                {'path': spec['treatment_tick_field'], 'op': 'gt', 'value': spec['after_tick']}]}]})
    else:
        raise Error('Use an explicit check for this family; combat victory and general tasks have no universal completion shortcut.')
    checks += spec.get('safety_checks', [])
    return {'checks': checks, 'contract': spec,
            'limitation': 'Fields are required, not guessed. If this RimMolt version omits them, use current scoped visual evidence or a reviewed explicit check.'}


def validate_check(check):
    from .observations import matches
    checks = check.get('checks', [check])
    if not isinstance(checks, list) or not checks: raise Error('Supply at least one outcome check.')
    for c in checks:
        require_fields(c, ('tool', 'all'))
        def predicates(values):
            if not isinstance(values, list) or not values: raise Error('Outcome predicates cannot be empty.')
            for p in values:
                require_fields(p, ('path', 'op'))
                if p['op'] in ('any_item', 'no_item'):
                    predicates(p.get('all'))
                elif p['op'] not in ('eq', 'contains', 'exists', 'gt', 'gte', 'lt', 'lte'):
                    raise Error('Unsupported verification operator.')
        predicates(c['all'])
    return check


def satisfied(campaign, action, state):
    from .observations import matches
    checks = action['check'].get('checks', [action['check']])
    evidence = []
    for check in checks:
        found = None
        from .facts import entries
        for entry in entries(state, tools=(check['tool'],)):
            obs = entry['latest']
            try: campaign._eligible_evidence(obs, action, state)
            except Error: continue
            if matches(obs, check) is True:
                found = obs['id']; break
        if found is None: return None
        evidence.append(found)
    return evidence
