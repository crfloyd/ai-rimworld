"""Small offline run directory views. Selection never switches the running game."""

import math
from pathlib import Path

from .core import Error, read_json, slug


READ_FIRST = ('CAMPAIGN.md', 'STRATEGY.md', 'ISSUES.md')


def describe_run(root, name):
    root = Path(root).resolve()
    directory = root / 'campaigns' / slug(name)
    if (root / 'campaigns').is_symlink() or directory.is_symlink():
        raise Error('Run directories must be local directories, not symlinks.')
    meta_file = directory / 'campaign.json'
    if meta_file.is_symlink():
        raise Error('Run metadata must not be a symlink.')
    meta = read_json(meta_file)
    if not isinstance(meta, dict) or meta.get('name') != name or not meta.get('id'):
        raise Error('Run metadata does not match its directory identity.')
    result = {
        'name': name, 'id': meta['id'], 'path': str(directory),
        'objective': meta.get('objective'), 'created_at': meta.get('created_at'),
        'last_recorded_day': None, 'time_basis': 'unknown',
        'last_observation_at': None, 'observation_origin': None, 'summary_generated_at': None,
        'open_issues': None, 'pending_actions': None,
        'history': str(directory / 'History.md'), 'warnings': [],
    }
    # This deliberately does not load full projections or observation journals.
    summary_path = directory / 'summary.json'
    if summary_path.is_symlink():
        raise Error('Run summary must not be a symlink.')
    if summary_path.exists():
        try:
            summary = read_json(summary_path)
            if not isinstance(summary, dict) or summary.get('campaign_id') != meta['id']:
                raise Error('Summary campaign identity mismatch.')
            tick = summary.get('latest_tick')
            per_day = meta.get('ticks_per_day')
            if tick is not None:
                if type(tick) not in (int, float) or not math.isfinite(tick) or tick < 0 or type(per_day) is not int or per_day <= 0:
                    raise Error('Summary has invalid game time.')
                result['last_recorded_day'] = tick / per_day
            result.update({
                'time_basis': summary.get('tick_basis', 'unknown'),
                'summary_generated_at': summary.get('generated_at'),
                'last_observation_at': summary.get('last_observation_at'),
                'observation_origin': summary.get('observation_origin'),
                'open_issues': summary.get('open_issues'),
                'pending_actions': summary.get('pending_actions'),
            })
        except Error as exc:
            result['warnings'].append(str(exc))
    else:
        result['warnings'].append('No compact summary yet; refresh the selected run locally when resuming.')
    return result


def list_runs(root):
    directory = Path(root).resolve() / 'campaigns'
    result = {'runs': [], 'errors': [], 'live_game_checked': False}
    if directory.is_symlink():
        raise Error('The campaigns directory must not be a symlink.')
    if not directory.exists():
        return result
    for path in sorted(directory.iterdir()):
        if not path.is_dir() and not path.is_symlink():
            continue
        try:
            result['runs'].append(describe_run(root, path.name))
        except (Error, OSError) as exc:
            result['errors'].append({'directory': path.name, 'error': str(exc)})
    return result


def resume_run(root, name, *, full=False):
    result = describe_run(root, name)
    directory = Path(result['path'])
    result['read_first'] = [str(directory / f) for f in READ_FIRST]
    result['missing_files'] = [f for f in result['read_first'] if not Path(f).is_file()]
    from .memory import Campaign
    from .continuity import resume_snapshot
    result['handoff'] = resume_snapshot(Campaign(root, name), full=full)
    result['live_game_checked'] = False
    result['next'] = (
        f'Read this run\'s rules, current strategy and issues; use --run {name} explicitly. '
        'Retrieve historical evidence only where the decision needs it; STATE/full packets are optional indexes. Establish actual controller handoff, then inspect '
        'and bind the authorized live game. This command did not load a save, resume time, '
        'change any file, or set a global active run.'
    )
    return result
