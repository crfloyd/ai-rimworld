import copy
import unittest
from tools.rimworld.presentation import present


class PresentationReferences(unittest.TestCase):
    def observation(self, body, risk, **extra):
        return dict(id='obs-example', completeness='known', data=body,
                    risks=[dict(kind='novel_warning', severity='unknown', value=risk)], **extra)

    def resolve(self, output, pointer):
        value = output
        for part in pointer.removeprefix('#/').split('/'):
            name = part.replace('~1','/').replace('~0','~')
            value = value[int(name)] if isinstance(value,list) else value[name]
        return value

    def test_exact_visible_risk_is_referenced_without_mutation(self):
        warning = {'enemies':[{'id':'p','newMechanic':'x'*200,'value':False}]}
        source = self.observation({'a/b~c':warning}, warning, counts={'p':1})
        before = copy.deepcopy(source)
        output = present(source)
        self.assertEqual(source,before)
        self.assertEqual(self.resolve(output,output['risks'][0]['value_ref']),warning)
        self.assertEqual(output['risks'][0]['severity'],'unknown')

    def test_missing_risk_values_survive_unchanged_partial_and_full_views(self):
        for extra in ({}, {'unchanged':True}, {'delta':{'changed_fields':['x']}}, {'completeness':'partial'}):
            source = self.observation({'x':1}, {'newMechanic':'danger'})
            source.update(extra)
            self.assertEqual(present(source)['risks'][0]['value'],{'newMechanic':'danger'})

    def test_nested_false_is_not_referenced_to_zero(self):
        risk = {'items':[False], 'description':'x'*200}
        body = {'items':[0], 'description':'x'*200}
        output = present(self.observation({'warning':body},risk))
        self.assertEqual(output['risks'][0]['value'],risk)
        self.assertNotIn('value_ref',output['risks'][0])

    def test_different_warning_with_same_name_is_not_hidden(self):
        source = self.observation({'warning':{'value':0}}, None, warnings={'warning':{'value':False}})
        self.assertIs(present(source)['warnings']['warning']['value'],False)

    def test_references_do_not_depend_on_previous_present_calls(self):
        risk = {'text':'x'*200}
        present(self.observation({'warning':risk},risk))
        self.assertEqual(present(self.observation({},risk))['risks'][0]['value'],risk)
