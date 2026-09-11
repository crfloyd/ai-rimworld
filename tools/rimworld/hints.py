"""Actionable recovery advice for bounded reads and receipts. No strategy, no I/O."""

# Filters that narrow a read at the source. Keys are exact catalog tool names.
NARROW = {
 'list_things': 'category, defName, faction (any/player/hostile/neutral/wild), nearId or nearX+nearZ with radius, limit',
 'list_world_objects': 'kind (settlements/caravans/sites/space), faction name substring, fromTile',
 'list_unmanaged_items': 'limit, mapIndex',
 'get_area': 'minX/maxX/minZ/maxZ bounds, thing, layer, scale, summary',
 'get_map': 'summary, and an explicit bounded get_area instead of the whole map',
 'get_world': 'kind and faction filters where offered',
 'room_graph': 'limit, mapIndex',
 'find_world_tiles': 'explicit search constraints and limit',
 'list_trade': 'filter (label substring), limit',
 'get_pawn': 'tab (needs/health/gear/bio), detail',
 'list_colonists': 'no source filter; select fields or row_fields instead',
 'get_window_ui': 'for a trade dialog use list_trade; otherwise select only the needed fields',
}

# Tools whose schema offers the deliberate override of the upstream size guard.
CONFIRM = ('find_world_tiles', 'get_area', 'get_map', 'get_world', 'list_things',
           'list_unmanaged_items', 'list_world_objects', 'room_graph')

WIDE = ('Re-run with confirm:true to accept the full result. Delivery stays bounded and '
        'rw_retrieve {observation, view:"full"} then returns all of it without another game call.')


def oversized(data):
    """True only for the upstream large-output guard, which answers instead of the query."""
    return isinstance(data, dict) and data.get('largeOutput') is True


def narrowing(tool, data=None):
    """Both sanctioned exits from a size guard, named explicitly."""
    hint = {}
    if tool in NARROW:
        hint['narrow_with'] = NARROW[tool]
    if tool in CONFIRM:
        hint['wide_read'] = WIDE
    if not hint:
        return None
    if isinstance(data, dict):
        for key in ('chars', 'items', 'message'):
            if key in data:
                hint[key] = data[key]
    hint['basis'] = 'The query never ran; this is the guard speaking. Narrowing is usually cheaper than confirming.'
    return hint


PREFIXES = ('prioritize working on ', 'already working on ')


def job_phrase(label):
    """The job a float-menu label refers to, or None when it is not a work label."""
    text = str(label).strip().lower() if label is not None else ''
    for prefix in PREFIXES:
        if text.startswith(prefix):
            return text[len(prefix):].strip()
    return None


def already_satisfied(tool, args, data):
    """A prioritize order the pawn is already running is not a failed order."""
    if tool != 'order_pawn' or not isinstance(data, dict) or data.get('ok') is not False:
        return None
    if not str(data.get('error', '')).startswith('No order matched'):
        return None
    wanted = job_phrase((args or {}).get('command'))
    if not wanted:
        return None
    for offered in data.get('available') or []:
        if str(offered).strip().lower().startswith('already working on ') and job_phrase(offered) == wanted:
            return {'requested': (args or {}).get('command'), 'offered': offered,
                    'executed': False, 'intent_already_met': True,
                    'meaning': 'The pawn is already doing this job. Nothing was re-issued and nothing changed.'}
    return None


def withheld_rows(tool, data):
    """Upstream counted more tradeables than it returned; name the gap rather than hide it."""
    if tool != 'list_trade' or not isinstance(data, dict):
        return None
    returned, counted = data.get('returned'), data.get('tradeableCount')
    if type(returned) is not int or type(counted) is not int or returned >= counted:
        return None
    return {'returned': returned, 'counted': counted,
            'note': 'Upstream returned fewer rows than it counted. Colony silver is reported separately '
                    'in the silver field. Use filter to locate a specific item by label.'}
