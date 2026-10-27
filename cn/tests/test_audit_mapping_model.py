import copy
import unittest
from cn_web.audit_mapping import nrv_for_audit
from ledger_audit import audit_documents
class AuditMappingModel(unittest.TestCase):
    def test_exact_mapping_wins_over_broad_name_without_rewriting_evidence(self):
        products=[{'id':'seed','name':'Seed','crop':'Maize','packing_kg':'4','aliases':[], 'segment':''},{'id':'gold','name':'Seed Gold','crop':'Cotton','packing_kg':'1','aliases':[], 'segment':''}]
        doc={'party':'Dealer','location':'Town','entries':[{'id':'s','date':'2026-04-01','reference':'S1','kind':'sale','debit':'100','credit':'0','items':[{'name':'Seed Gold','qty':'1','unit':'packet','amount':'100','rate':'100','product':'gold','mapping_confirmed':True}]}]}
        cfg={'products':products,'crops':['Maize','Cotton']};state={'catalogue':products,'ledgers':[]};before=copy.deepcopy((doc,cfg,state))
        out=nrv_for_audit([doc,doc],state,cfg,'2026-04-01','2026-04-30');self.assertEqual(len(out['product_rows']),1);self.assertEqual(out['product_rows'][0]['product_id'],'gold');self.assertEqual(out['product_rows'][0]['crop'],'Cotton');self.assertEqual(out['product_rows'][0]['net_packets'],1);self.assertEqual(before,(doc,cfg,state))
    def test_without_new_mapping_matches_original_audit_and_preserves_return_evidence(self):
        p={'id':'seed','name':'Seed','crop':'Maize','packing_kg':'4','aliases':[], 'segment':''};cfg={'products':[p],'crops':['Maize']};state={'catalogue':[p],'ledgers':[]}
        def entry(kind,ref,date,qty):return {'id':ref,'reference':ref,'date':date,'kind':kind,'debit':str(qty*100) if kind=='sale' else '0','credit':str(qty*100) if kind=='return' else '0','items':[{'name':'Seed','qty':str(qty),'rate':'100','amount':str(qty*100),'unit':'packet'}]}
        doc={'party':'Dealer','location':'Town','entries':[entry('sale','S1','2026-04-01',3),entry('return','R1','2026-04-02',1)]}
        baseline=audit_documents([doc],'2026-04-01','2026-04-30',cfg)['posted_CN_NRV'];out=nrv_for_audit([doc],state,cfg,'2026-04-01','2026-04-30')
        self.assertEqual(out['product_rows'],baseline['product_rows']);self.assertEqual(out['confirmed_CN_total'],baseline['confirmed_CN_total']);self.assertEqual(out['excluded_credits'][0]['items'][0]['name'],'Seed');self.assertNotIn('__CN_AUDIT_',str(out))
