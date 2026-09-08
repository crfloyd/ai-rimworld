from test_system import ControlFixture
from tools.rimworld.core import Error, journal, atomic_json
from tools.rimworld.mcp import Uncertain
from tools.rimworld.cli import parser, run
from unittest.mock import patch
from tools.rimworld.observations import normalize
from tools.rimworld.safety import signals
import unittest


class SimpleCalls(ControlFixture):
    def test_default_mutation_journals_without_open_goal_or_intent_requirement(self):
        self.responses.append({'ok':True,'executed':True})
        r=self.control.call(self.token,'order_pawn',{'id':'PawnA','command':'Go here'})
        self.assertNotIn('action_id',r)
        self.assertFalse(self.camp._actions())
        self.assertEqual(journal(self.control.path/'history.jsonl')[0][-1]['status'],'returned')
        self.assertTrue(self.camp.has_observation(r['id']))

    def test_untracked_uncertainty_still_blocks_replay(self):
        self.responses.append(Uncertain('Lost response'))
        with self.assertRaises(Uncertain):self.control.call(self.token,'order_pawn',{'id':'PawnA','command':'Go here'})
        before=len(self.calls)
        with self.assertRaises(Error):self.control.call(self.token,'order_pawn',{'id':'PawnA','command':'Go here'})
        self.assertEqual(before,len(self.calls))
        self.assertEqual(self.control.inspect()['pending']['status'],'unknown')
        self.assertFalse(self.camp._actions())

    def test_explicit_tracking_keeps_intent_and_completion_requirements(self):
        with self.assertRaises(Error):self.control.call(self.token,'order_pawn',{'id':'PawnA','command':'Go here'},track=True)
        self.responses.append({'ok':True,'executed':True})
        r=self.control.call(self.token,'order_pawn',{'id':'PawnA','command':'Go here'},intent='Reach shelter',track=True)
        a=self.camp._actions()[r['action_id']]
        self.assertEqual(a['status'],'accepted')
        with self.assertRaises(Error):self.camp.action_update(a['id'],'completed',r['id'],'Receipt is not arrival')

    def test_check_implies_tracking_and_still_requires_intent(self):
        check={'tool':'get_pawn','args':{'id':'PawnA'},'all':[{'path':'x','op':'eq','value':8}]}
        with self.assertRaises(Error):self.control.call(self.token,'order_pawn',{'id':'PawnA','command':'Go here'},check=check)
        self.responses.append({'ok':True,'executed':True})
        r=self.control.call(self.token,'order_pawn',{'id':'PawnA','command':'Go here'},intent='Reach checked location',check=check)
        self.assertEqual(self.camp._actions()[r['action_id']]['status'],'accepted')

    def test_cli_call_and_batch_execute_without_intent_or_goal_records(self):
        argv=['--root',str(self.root),'--run','example']
        steps=self.root/'simple-batch.json'
        atomic_json(steps,[{'tool':'order_pawn','args':{'id':'PawnA','command':'One'}},
                           {'tool':'order_pawn','args':{'id':'PawnA','command':'Two'}}])
        self.responses.extend([{'ok':True,'executed':True}]*3)
        before=len(self.calls)
        with patch('tools.rimworld.cli.Control',return_value=self.control):
            run(parser().parse_args(argv+['call','order_pawn','--args','{"id":"PawnA","command":"Go here"}','--token',self.token]))
            run(parser().parse_args(argv+['batch','--file',str(steps),'--token',self.token]))
        self.assertEqual(len(self.calls)-before,3)
        self.assertFalse(self.camp._actions())

    def test_cli_simple_default_and_explicit_tracking(self):
        self.assertFalse(parser().parse_args(['call','order_pawn','--token','t']).track)
        self.assertTrue(parser().parse_args(['call','order_pawn','--token','t','--track']).track)


class HealthChangeClassification(unittest.TestCase):
    def severity(self,rows):
        o=normalize('wait_for_event',{}, {'pausedAfter':True,'cause':'timeout','_delta':{'pawnDamage':rows}},'c','s','fixture')
        r=next(r for r in signals(o) if r['kind']=='delta:pawnDamage')
        self.assertEqual(r['value'],rows)
        return r['severity']

    def test_healing_and_new_effects_are_not_automatically_damage(self):
        self.assertEqual(self.severity([{'name':'p','hpBefore':96,'hpAfter':100}]),'info')
        self.assertEqual(self.severity([{'name':'p','hpBefore':100,'hpAfter':100,'newInjuries':['New condition']}]),'review')

    def test_damage_and_unknown_types_still_require_attention(self):
        self.assertEqual(self.severity([{'name':'p','hpBefore':80,'hpAfter':60}]),'critical')
        for row in ({'hpBefore':False,'hpAfter':0},{'hpBefore':80,'hpAfter':90,'novelDanger':True},{'hpBefore':80,'hpAfter':90,'newInjuries':{'unexpected':1}}):
            self.assertEqual(self.severity([row]),'unknown')
