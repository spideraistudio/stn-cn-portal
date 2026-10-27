"""Read-only automatic rate evidence, trace and legacy-rule parity."""
import copy
from test_billing_audit import BillingTests
from cn_web import billing_audit as a
from ledger_audit import audit_documents

class BillingRateFix(BillingTests):
    def test_automatic_return_rules_match_existing_ledger_audit(self):
        for supplies,returned,category in [([900],950,'Return rate above supply'),([900,1000],950,'Mixed supply rates — review return'),([900,1000],1100,'Return rate above supply'),([900,1000],900,None),([900],900,None)]:
            with self.subTest(supplies=supplies,returned=returned):
                self.doc['entries']=[]
                for i,rate in enumerate(supplies):self.add('sale','S'+str(i),'2026-05-01',10,rate)
                self.add('return','R','2026-10-01',2,returned)
                before=copy.deepcopy((self.doc,self.s));r=self.run_audit()['rows'][-1]
                legacy=copy.deepcopy(self.doc);legacy.update(opening='0',closing='0',warnings=[])
                for entry in legacy['entries']:entry.update(debit='0',credit='0',narration=entry['reference'])
                findings=audit_documents([legacy],'2026-04-01','2027-03-31',{'products':self.s['catalogue']})['findings']
                rate_findings=[f['type'] for f in findings if f['type'] in ('Return rate above supply','Mixed supply rates — review return')]
                self.assertEqual(rate_findings,[category] if category else [])
                if category:self.assertEqual(r['status'],category)
                else:self.assertFalse(r['attention'])
                self.assertFalse(r['invoice_match_confirmed']);self.assertEqual(r['allocations'],[])
                self.assertEqual(before,(self.doc,self.s))

    def test_saved_all_state_rate_reproduces_and_corrects_missing_comparison(self):
        self.add('sale','S','2026-05-01',10,900)
        self.s['billing_audit']['rates']=[{**self.s['billing_audit']['rates'][0],'state':'ALL','rate':'800'}]
        r=self.run_audit()['rows'][0]
        self.assertEqual(r['status'],'Billing rate mismatch');self.assertEqual(r['difference'],'1000')
        self.s['billing_audit']['rates'][0]['rate']='900'
        self.assertEqual(self.run_audit()['rows'][0]['status'],'Rate matches')
        self.s['billing_audit']['rates'].append({**self.s['billing_audit']['rates'][0],'state':'Gujarat','rate':'850'})
        self.assertEqual(a.decimal(self.run_audit()['rows'][0]['expected_rate']),a.decimal('850'))

    def test_clear_unchecked_reasons(self):
        self.add('sale','S','2026-05-01',10,900)
        for state,period,reason in [('',False,'state is missing'),('Rajasthan',False,'No approved rate for statement state'),('Gujarat',True,'No approved rate effective')]:
            with self.subTest(state=state):
                self.doc['state']=state
                self.doc['entries'][0]['date']='2027-04-01' if period else '2026-05-01'
                end='2027-04-02' if period else '2027-03-31'
                r=a.run([self.doc],self.s,'2026-04-01',end)['rows'][0]
                self.assertFalse(r['comparison_checked']);self.assertIsNone(r['difference']);self.assertIn(reason,r['unchecked_reason']);self.assertIn('Not compared',r['comparison_basis'])
        self.doc['state']='Gujarat';self.doc['entries'][0]['date']='2026-05-01'
        self.s['billing_audit']['rates']=[]
        self.assertIn('No approved rate saved for mapped product',self.run_audit()['rows'][0]['unchecked_reason'])
        self.doc['entries'][0]['items'][0].update(name='Unknown seed',product=None,mapping_confirmed=False)
        self.assertIn('Product mapping required',self.run_audit()['rows'][0]['unchecked_reason'])

    def test_units_cross_year_and_return_rate_not_current_approved(self):
        self.add('sale','S','2026-03-01',10,1200)
        self.add('return','R','2026-10-01',2,350,'kg')
        r=self.run_audit()['rows'][0]
        self.assertEqual(r['status'],'Return rate above supply');self.assertEqual(a.decimal(r['expected_rate']),a.decimal(300));self.assertEqual(a.decimal(r['difference']),a.decimal(100))
        self.s['billing_audit']['rates'][1]['rate']='999999'
        self.assertEqual(self.run_audit()['rows'][0]['expected_rate'],r['expected_rate'])

    def test_many_matches_and_one_difference_counts(self):
        for i in range(500):self.add('sale','S'+str(i),'2026-05-01',1,901 if i else 900)
        r=self.run_audit();self.assertEqual(r['counts']['attention'],1);self.assertEqual(r['counts']['unchecked'],0);self.assertEqual(r['counts']['compared'],500)

import test_billing_http as http
class BillingRateFixHTTP(http.BillingHTTP):
    def test_all_rate_save_rerun_reclassifies_owned_pdf_and_invalidates_review(self):
        _,b=self.user_browser();_,w=self.setup_book(b);self.config(b,w)
        code,out,_=self.calc(b,w,'native-audit-import',{'data':self.file('two_seasons.pdf')['content_base64']});self.assertEqual(code,200,out)
        req={'documents':out['documents'],'start':'2026-04-01','end':'2027-03-31','include_saved':False}
        initial=self.calc(b,w,'native-billing-run',req)[1]
        sale=next(r for r in initial['rows'] if r['kind']=='sale' and r['product'])
        cfg=self.calc(b,w,'native-billing-config',{})[1]
        rate={'state':'ALL','product':sale['product'],'start':req['start'],'end':req['end'],'unit':sale['unit'],'rate':str(a.decimal(sale['rate'])+1)}
        code,saved,_=self.calc(b,w,'native-billing-rates',{'revision':cfg['revision'],'rates':[rate]});self.assertEqual(code,200,saved)
        code,changed,_=self.calc(b,w,'native-billing-run',req);self.assertEqual(code,200,changed)
        target=next(r for r in changed['rows'] if r['id']==sale['id']);self.assertEqual(target['status'],'Billing rate mismatch');self.assertTrue(target['attention'])
        code,reviewed,_=self.calc(b,w,'native-billing-review',{**req,'revision':changed['revision'],'evidence':changed['evidence'],'row_id':sale['id'],'review':{'status':'mistake','reason':'Review source invoice'}});self.assertEqual(code,200,reviewed);self.assertIn('mapping_targets',reviewed)
        rate['rate']=sale['rate']
        code,saved,_=self.calc(b,w,'native-billing-rates',{'revision':reviewed['revision'],'rates':[rate]});self.assertEqual(code,200,saved)
        checked=self.calc(b,w,'native-billing-run',req)[1];target=next(r for r in checked['rows'] if r['id']==sale['id'])
        self.assertEqual(target['status'],'Rate matches');self.assertFalse(target['attention']);self.assertIsNone(target['review'])
        self.assertEqual([(r['id'],r['rate'],r['date'],r['amount']) for r in initial['rows']],[(r['id'],r['rate'],r['date'],r['amount']) for r in checked['rows']])
        self.assertEqual(self.calc(b,w,'native-billing-config',{})[1]['configuration']['rates'],[rate])
