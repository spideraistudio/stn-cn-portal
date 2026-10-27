import copy
import unittest
from cn_web import billing_audit as a
from cn_web.security import AuthError

class BillingTests(unittest.TestCase):
    def setUp(self):
        self.s={'ledgers':[], 'catalogue':[{'id':'p','name':'Seed','crop':'Maize','segment':'','packing_kg':'4','aliases':[]}], 'billing_audit':a.empty()}
        self.s['billing_audit']['rates']=[{'state':'Gujarat','product':'p','start':'2026-04-01','end':'2026-08-31','unit':'packet','rate':'901'}, {'state':'Gujarat','product':'p','start':'2026-09-01','end':'2027-03-31','unit':'packet','rate':'950'}]
        self.doc={'party':'Dealer','location':'Town','state':'Gujarat','entries':[]}
    def add(self,kind,ref,date,qty,rate,unit='packet'):
        self.doc['entries'].append({'kind':kind,'reference':ref,'date':date,'items':[{'name':'Seed','product':'p','mapping_confirmed':True,'qty':str(qty),'rate':str(rate),'amount':str(qty*rate),'unit':unit}]})
    def run_audit(self,**kw):return a.run([self.doc],self.s,'2026-04-01','2027-03-31',**kw)
    def test_seasons_original_wrong_sale_return_and_no_mutation(self):
        self.add('sale','S1','2026-05-01',10,890);self.add('return','R1','2026-10-01',2,890)
        before=copy.deepcopy((self.s,self.doc));r=self.run_audit()['rows'];self.assertEqual(r[0]['status'],'Billing rate mismatch');self.assertEqual(r[1]['status'],'Return rate matches earlier supply')
        m={r[1]['id']:[{'sale':r[0]['id'],'qty':'2'}]};r=self.run_audit(matches=m)['rows'];self.assertEqual(r[1]['status'],'Return rate matches original bill');self.assertEqual(a.decimal(r[1]['expected_rate']),a.decimal('890'));self.assertEqual(before,(self.s,self.doc))
    def test_split_no_offset_and_overreturn(self):
        self.add('sale','S1','2026-05-01',2,900);self.add('sale','S2','2026-06-01',2,1000);self.add('return','R1','2026-10-01',2,950)
        rows=self.run_audit()['rows'];m={rows[2]['id']:[{'sale':rows[0]['id'],'qty':'1'},{'sale':rows[1]['id'],'qty':'1'}]}
        r=self.run_audit(matches=m)['rows'][2];self.assertEqual(r['status'],'Return rate mismatch');self.assertEqual(r['difference'],'0')
        m[rows[2]['id']]=[{'sale':rows[0]['id'],'qty':'3'}]
        with self.assertRaises(AuthError):self.run_audit(matches=m,strict=True)
    def test_units_prior_returns_and_dedup(self):
        self.add('sale','S','2026-05-01',2,901);self.add('return','R','2026-06-01',4,225.25,'kg');self.add('return','R2','2026-10-01',5,225.25,'kg')
        rows=self.run_audit()['rows'];m={r['id']:[{'sale':rows[0]['id'],'qty':r['qty']}] for r in rows[1:]}
        result=self.run_audit(matches=m)['rows'];self.assertEqual(result[1]['status'],'Return rate matches original bill');self.assertEqual(result[2]['status'],'Return exceeds remaining billed quantity')
        self.assertEqual(len(a.run([self.doc,self.doc],self.s,'2026-04-01','2027-03-31')['rows']),3)
    def test_missing_sale_overlap_and_stale_review(self):
        self.add('return','R','2026-05-01',2,901);r=self.run_audit()['rows'][0];self.assertIn('Original sale required',r['status'])
        self.s['billing_audit']['reviews']={r['id']:{'status':'not_applicable','reason':'Review note','evidence':r['review_evidence']}}
        self.assertIsNotNone(self.run_audit()['rows'][0]['review'])
        self.s['billing_audit']['rates'][0]['rate']='902';self.assertIsNone(self.run_audit()['rows'][0]['review'])
        self.s['billing_audit']['rates'].append(copy.deepcopy(self.s['billing_audit']['rates'][0]))
        with self.assertRaises(AuthError):self.run_audit()
