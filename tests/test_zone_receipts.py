import unittest
from tools.rimworld.control import receipt_status


class ZoneReceipts(unittest.TestCase):
    def test_exact_zone_setting_receipts_are_accepted_not_completed(self):
        cases=[('rename_zone',{'id':13,'name':'Clothes'},{'id':13,'label':'Clothes'}),
               ('set_stockpile_priority',{'id':13,'priority':'Critical'},{'id':13,'kind':'stockpile','priority':'Critical'}),
               ('set_stockpile_filter',{'id':13,'disallowAll':True,'allow':'Apparel_TribalA','hpMin':51},
                {'id':13,'kind':'stockpile','applied':['disallowAll','+Apparel_TribalA','hpRange'],'filter':{'hpPercentRange':[50,100]}})]
        for tool,args,data in cases:
            self.assertEqual(receipt_status(tool,args,data,'known'),'accepted')
            self.assertEqual(receipt_status(tool,args,dict(data,error='failed'),'known'),'blocked')
            self.assertEqual(receipt_status(tool,args,data,'partial'),'unknown')
            self.assertEqual(receipt_status(tool,args,dict(data,id=14),'known'),'unknown')

    def test_type_mismatch_does_not_identify_the_requested_zone(self):
        self.assertEqual(receipt_status('rename_zone',{'id':0,'name':'A'},{'id':False,'label':'A'},'known'),'unknown')

    def test_filter_unknown_or_partially_applied_requests_need_review(self):
        args={'id':13,'disallowAll':True,'allow':'Unrecognized'}
        base={'id':13,'kind':'stockpile','filter':{}}
        self.assertEqual(receipt_status('set_stockpile_filter',args,dict(base,applied=['disallowAll','unknown:Unrecognized']),'known'),'blocked')
        for applied in ([],['disallowAll'],['disallowAll','mystery'],None):
            self.assertEqual(receipt_status('set_stockpile_filter',args,dict(base,applied=applied),'known'),'unknown')

    def test_wrong_name_priority_or_read_only_filter_does_not_certify_setting(self):
        self.assertEqual(receipt_status('rename_zone',{'id':13,'name':'A'},{'id':13,'label':'B'},'known'),'unknown')
        self.assertEqual(receipt_status('set_stockpile_priority',{'id':13,'priority':'Critical'},{'id':13,'kind':'stockpile','priority':'Normal'},'known'),'unknown')
        self.assertEqual(receipt_status('set_stockpile_filter',{'id':13},{'id':13,'kind':'stockpile','mode':'read','filter':{}},'known'),'unknown')
