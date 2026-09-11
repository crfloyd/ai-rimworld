import copy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from tools.rimworld.cli import parser, run
from tools.rimworld.core import Error, atomic_json, read_json
from tools.rimworld.memory import Campaign, init_campaign
from tools.rimworld.runs import list_runs, resume_run


SPEC = {
    'objective': 'Synthetic startup validation', 'mode': 'fresh',
    'rules': {'honest_play': True, 'autonomy': 'delegated in fixture', 'recovery': 'no reloads'},
    'setup': {'scenario': 'fixture', 'difficulty': 'fixture', 'dlc': [], 'mods': []},
    'intake': {'request': 'Detailed synthetic brief', 'field_sources': {'setup.difficulty': 'explicit fixture brief'},
               'unresolved_questions': [], 'delegated_choices': ['world details']},
}


class RunEntryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.spec = self.root / 'spec.json'
        atomic_json(self.spec, SPEC)

    def tearDown(self):
        self.temp.cleanup()

    def cli(self, *args):
        return run(parser().parse_args(['--root', str(self.root), *args]))

    def snapshot(self):
        return {str(p.relative_to(self.root)): p.read_bytes() for p in self.root.rglob('*') if p.is_file()}

    def test_empty_listing_neither_creates_records_nor_contacts_game(self):
        before = self.snapshot()
        with patch('tools.rimworld.control.Control.connect', side_effect=AssertionError('No live call')):
            result = self.cli('runs')
        self.assertEqual(result['runs'], [])
        self.assertFalse(result['live_game_checked'])
        self.assertEqual(self.snapshot(), before)
        self.assertFalse((self.root / 'campaigns').exists())

    def test_new_runs_are_independent_and_preserve_answers(self):
        first = self.cli('new', 'ember', '--spec', str(self.spec))
        campaign = Campaign(self.root, 'ember')
        campaign.ingest('get_status', {}, {'loaded': False}, origin='fixture', tick=60000)
        prior = {str(p.relative_to(campaign.path)): p.read_bytes() for p in campaign.path.rglob('*') if p.is_file()}
        second = self.cli('new', 'winter', '--spec', str(self.spec))
        self.assertNotEqual(first['id'], second['id'])
        self.assertEqual(second['intake'], SPEC['intake'])
        self.assertEqual(prior, {str(p.relative_to(campaign.path)): p.read_bytes() for p in campaign.path.rglob('*') if p.is_file()})
        self.assertEqual((self.root / 'campaigns/winter/observations.jsonl').read_text(), '')
        self.assertIsNone(second['binding'])
        self.assertEqual(read_json(self.spec), SPEC)

    def test_new_refuses_existing_name_without_modifying_it(self):
        self.cli('new', 'ember', '--spec', str(self.spec))
        before = self.snapshot()
        with self.assertRaises(Error):
            self.cli('new', 'ember', '--spec', str(self.spec))
        self.assertEqual(self.snapshot(), before)

    def test_new_refuses_unanswered_questions_and_resume_mode(self):
        for change in ({'mode': 'resume'}, {'intake': {'unresolved_questions': ['Reload rules?']}}):
            spec = copy.deepcopy(SPEC)
            spec.update(change)
            atomic_json(self.spec, spec)
            with self.assertRaises(Error):
                self.cli('new', 'ember', '--spec', str(self.spec))
            self.assertFalse((self.root / 'campaigns').exists())

    def test_resume_is_read_only_and_does_not_set_global_selection(self):
        self.cli('new', 'ember', '--spec', str(self.spec))
        before = self.snapshot()
        result = self.cli('resume', 'ember')
        self.assertEqual(result['name'], 'ember')
        self.assertIsNone(result['last_recorded_day'])
        self.assertEqual(result['missing_files'], [])
        self.assertEqual([Path(p).name for p in result['read_first']], ['CAMPAIGN.md','STRATEGY.md','ISSUES.md'])
        self.assertFalse(result['live_game_checked'])
        self.assertEqual(result['next_commands'][0],'./rw --run ember controller inspect')
        self.assertIn('./rw --run ember controller claim',result['next_commands'][1])
        self.assertIn('not a live stdio process',result['cached_session_note'])
        self.assertEqual(self.snapshot(), before)
        self.assertFalse((self.root / '.runtime').exists())

    def test_missing_resume_is_never_a_new_run(self):
        with self.assertRaises(Error):
            self.cli('resume', 'missing')
        self.assertFalse((self.root / 'campaigns').exists())

    def test_selectors_and_conflicts(self):
        self.cli('new', 'ember', '--spec', str(self.spec))
        self.assertEqual(parser().parse_args(['--run', 'ember', 'brief']).campaign, 'ember')
        self.assertEqual(parser().parse_args(['--campaign', 'ember', 'brief']).campaign, 'ember')
        self.assertEqual(self.cli('list'), self.cli('runs'))
        before = self.snapshot()
        with self.assertRaises(Error):
            self.cli('--run', 'wrong', 'resume', 'ember')
        self.assertEqual(before, self.snapshot())

    def test_listing_reads_compact_summary_not_history_or_projection(self):
        self.cli('new', 'ember', '--spec', str(self.spec))
        campaign = Campaign(self.root, 'ember')
        campaign.ingest('get_status', {}, {'loaded': False}, origin='fixture', tick=150000)
        allowed = {'campaign.json', 'summary.json'}
        def bounded_read(path):
            self.assertIn(Path(path).name, allowed)
            return read_json(path)
        before = self.snapshot()
        with patch('tools.rimworld.runs.read_json', side_effect=bounded_read):
            result = self.cli('runs')['runs'][0]
        self.assertEqual(result['last_recorded_day'], 2.5)
        self.assertEqual(result['observation_origin'], 'fixture')
        self.assertEqual(result['open_issues'], 0)
        self.assertNotIn('facts', result)
        self.assertEqual(before, self.snapshot())

    def test_missing_and_corrupt_summaries_remain_visible(self):
        self.cli('new', 'ember', '--spec', str(self.spec))
        summary = self.root / 'campaigns/ember/summary.json'
        summary.unlink()
        result = resume_run(self.root, 'ember')
        self.assertIsNone(result['last_recorded_day'])
        self.assertTrue(result['warnings'])
        self.assertFalse(summary.exists())
        summary.write_text('{broken')
        result = self.cli('runs')['runs'][0]
        self.assertTrue(result['warnings'])
        self.assertIsNone(result['last_recorded_day'])

    def test_summary_with_wrong_identity_or_nonfinite_time_is_not_trusted(self):
        meta = self.cli('new', 'ember', '--spec', str(self.spec))
        summary = self.root / 'campaigns/ember/summary.json'
        for value in ({'campaign_id': 'other', 'latest_tick': 60000},
                      {'campaign_id': meta['id'], 'latest_tick': float('nan')}):
            atomic_json(summary, value)
            result = self.cli('runs')['runs'][0]
            self.assertIsNone(result['last_recorded_day'])
            self.assertTrue(result['warnings'])

    def test_damaged_run_is_reported_instead_of_hidden(self):
        self.cli('new', 'ember', '--spec', str(self.spec))
        broken = self.root / 'campaigns/broken'
        broken.mkdir()
        result = list_runs(self.root)
        self.assertEqual([r['name'] for r in result['runs']], ['ember'])
        self.assertEqual(result['errors'][0]['directory'], 'broken')

    def test_new_and_resume_reject_symlinked_compartments(self):
        outside = self.root / 'elsewhere'
        outside.mkdir()
        (self.root / 'campaigns').symlink_to(outside, target_is_directory=True)
        with self.assertRaises(Error):
            init_campaign(self.root, 'ember', SPEC)
        with self.assertRaises(Error):
            resume_run(self.root, 'ember')
        self.assertEqual(list(outside.iterdir()), [])
