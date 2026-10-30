"""Receipt provenance, old-dues, retroactive CN and protected-crop regressions."""
import copy,unittest
from decimal import Decimal
from cn_web import ledger_service
from prior_payments import analyse,attach,party_match,validate,conflicts
from engine import payment_work,validate_input_limits,compute,validate_abs_assignment_changes

def doc(opening,entries,start='2025-04-01',end='2026-03-31'):
    closing=Decimal(opening)+sum((Decimal(e['debit'])-Decimal(e['credit']) for e in entries),Decimal(0))
    return {'party':'Exact Seller, Town','address':'Road 1, Town, Gujarat','location':'Town','state':'Gujarat','opening':opening,'closing':str(closing),'entries':entries,'source':{'report_start':start,'report_end':end,'issuer':'Company'}}
def entry(id,date,kind,debit='0',credit='0'):
    return {'id':id,'date':date,'reference':id,'kind':kind,'debit':debit,'credit':credit,'items':[]}
def pair(amount='300000',paddy='75000'):
    prior=doc('200000',[entry('r1','2026-01-15','receipt',credit=amount),entry('cn1','2026-02-10','posted_cn',credit='90000'),entry('paddy','2026-03-10','sale',debit=paddy)])
    current=doc(prior['closing'],[],start='2026-04-01',end='2027-03-31')
    return prior,current
def approve():return [{'cn':'cn1','receipt':'r1','earned':'2025-12-31','reason':'Earlier sales benefit approved before January'}]
def cfg():return {'products':[],'schemes':[],'seasons':[]}
def record(current):return {**copy.deepcopy(current),'status':'draft','old_dues':str(max(Decimal(current['opening']),0)),'opening_sources':[],'allocations':[],'cash_splits':[]}
class PriorPaymentTests(unittest.TestCase):
    def test_existing_credit_reconciled_without_changing_allocations(self):
        a=doc('-491466',[entry('r1','2026-03-14','receipt',credit='508534')]);b=doc(a['closing'],[],start='2026-04-01',end='2027-03-31')
        r=record(b);r['opening_sources']=[{'id':'old','date':None,'amount':'1000000'}]
        r['allocations']=[{'id':'a','source':'old','type':'Settlement','amount':'100000','remark':'Existing settlement'}]
        args=(a,b,'2026-01-01','2026-03-31',[],[{'receipt':'r1','crop':'Cotton','amount':'508534'}])
        linked=attach(r,*args);self.assertEqual(linked['opening_sources'][0]['amount'],'491466');self.assertEqual(linked['allocations'],r['allocations']);validate_input_limits(linked,cfg())
        self.assertEqual(r['opening_sources'][0]['amount'],'1000000')
        r['allocations'][0]['amount']='600000'
        with self.assertRaisesRegex(ValueError,'already allocated overlaps'):attach(r,*args)
        self.assertEqual(r['allocations'][0]['amount'],'600000')

    def test_carried_credit_conversion_date_scheme_and_limit(self):
        from cn_web.calculator_service import validate_opening_sources
        r=record(doc('-100000',[],start='2026-04-01',end='2027-03-31'))
        r['opening_sources']=[{'id':'credit','amount':'100000','date':'2026-01-15','conversion':True,'crop':'Cotton','scheme':'cotton','original_date':None}]
        settings=cfg();settings['schemes']=[{'id':'cotton','crop':'Cotton','benefits':['ABS'],'abs_start':'2026-01-01','abs_end':'2026-03-31'}]
        validate_opening_sources(r,[]);validate_input_limits(r,settings)
        r['opening_sources'][0]['date']='2026-04-01'
        with self.assertRaisesRegex(ValueError,'booking period'):validate_input_limits(r,settings)
        r['opening_sources'][0]['date']='2026-01-15';r['opening_sources'][0]['amount']='100001'
        with self.assertRaisesRegex(ValueError,'exceed'):validate_input_limits(r,settings)
        r['opening_sources'][0]['amount']='100000';r['allocations']=[{'id':'a','source':'credit','scheme':'other','type':'ABS','amount':'1'}]
        with self.assertRaisesRegex(ValueError,'selected scheme'):validate_input_limits(r,settings)

    def test_reserved_abs_uses_original_date(self):
        r=self.reserved();sid=r['reserved_sources'][0]['id']
        r['allocations']=[{'id':'abs','source':sid,'type':'ABS','scheme':'cotton','amount':'100'}]
        settings=cfg();settings['schemes']=[{'id':'cotton','benefits':['ABS'],'abs_start':'2026-01-01','abs_end':'2026-03-31'}]
        validate_abs_assignment_changes(r,settings)
        settings['schemes'][0]['abs_end']='2026-01-14'
        with self.assertRaisesRegex(ValueError,'2026-01-15'):
            validate_abs_assignment_changes(r,settings)

    def test_three_lakh_late_cn_and_paddy_reserve(self):
        a,b=pair();p=analyse(a,b,'2026-01-01','2026-03-31',approve());r=p['rows'][0]
        self.assertEqual(r['available'],'190000');self.assertEqual(r['cleared'],'110000')
        r=attach(record(b),a,b,p['start'],p['end'],approve(),[{'receipt':'r1','crop':'Cotton','amount':'190000'}])
        self.assertEqual(r['opening'],b['opening']);self.assertEqual(r['old_dues'],'75000')
        sources,remaining,due=payment_work(r);self.assertEqual(sources[0]['available'],Decimal('190000'));self.assertEqual(due,Decimal('75000'))
        self.assertEqual(sources[0]['old_dues_cleared'],0);validate_input_limits(r,cfg())
    def test_one_lakh_fully_consumed(self):
        a,b=pair('100000');self.assertEqual(analyse(a,b,'2026-01-01','2026-03-31',approve())['rows'][0]['available'],'0')
    def test_unapproved_cn_not_retrospective(self):
        a,b=pair();self.assertEqual(analyse(a,b,'2026-01-01','2026-03-31')['rows'][0]['available'],'100000')
    def test_later_paddy_invoice_never_consumes_reserve(self):
        for n in ('0','75000','300000','900000'):
            a,b=pair(paddy=n);self.assertEqual(analyse(a,b,'2026-01-01','2026-03-31',approve())['rows'][0]['available'],'190000')
    def test_exact_identity_and_missing_address(self):
        a,b=pair();self.assertTrue(party_match(a,b)['matched'])
        for key in ('party','address','location'):
            bad=copy.deepcopy(b);bad[key]+=' other';self.assertFalse(party_match(a,bad)['matched'])
        b['address']='';self.assertFalse(party_match(a,b)['matched'])
    def test_boundary_mismatch(self):
        a,b=pair();b['opening']='1'
        with self.assertRaises(ValueError):analyse(a,b,'2026-01-01','2026-03-31')
    def test_cn_duplicate_date_missing_reason(self):
        a,b=pair()
        for approvals in [approve()*2,[{**approve()[0],'earned':'2026-01-16'}],[{**approve()[0],'reason':''}]]:
            with self.assertRaises(ValueError):analyse(a,b,'2026-01-01','2026-03-31',approvals)
    def test_cn_not_counted_twice_at_posting_for_later_receipt(self):
        a,b=pair();a['entries'].append(entry('r2','2026-03-20','receipt',credit='100000'));a['closing']=str(Decimal(a['closing'])-100000);b=doc(a['closing'],[],start='2026-04-01',end='2027-03-31')
        rows=analyse(a,b,'2026-01-01','2026-03-31',approve())['rows'];self.assertEqual(rows[1]['cleared'],'75000');self.assertEqual(rows[1]['available'],'25000')
    def reserved(self):
        a,b=pair();return attach(record(b),a,b,'2026-01-01','2026-03-31',approve(),[{'receipt':'r1','crop':'Cotton','amount':'190000'}])
    def test_tamper_proof_and_overspend(self):
        for key,value in [('amount','190001'),('date','2026-04-01'),('crop','Paddy')]:
            r=self.reserved();r['reserved_sources'][0][key]=value
            with self.assertRaises(ValueError):validate(r)
        r=self.reserved();r['allocations']=[{'id':'a','source':r['reserved_sources'][0]['id'],'type':'Settlement','remark':'Explicit old settlement','amount':'190001'}]
        with self.assertRaises(ValueError):validate_input_limits(r,cfg())
    def test_cross_crop_rejected(self):
        r=self.reserved();r['allocations']=[{'id':'a','source':r['reserved_sources'][0]['id'],'type':'CD','scheme':'paddy','amount':'100'}]
        c=cfg();c['schemes']=[{'id':'paddy','crop':'Paddy'}]
        with self.assertRaisesRegex(ValueError,'reserved for Cotton'):validate_input_limits(r,c)
    def test_current_receipt_clears_gross_dues_not_reserve(self):
        r=self.reserved();r['entries'].append(entry('new','2026-05-01','receipt',credit='100000'));r['closing']=str(Decimal(r['closing'])-100000)
        src,_,due=payment_work(r);self.assertEqual(src[0]['available'],Decimal('190000'));self.assertEqual(src[1]['available'],Decimal('25000'));self.assertEqual(due,0)
    def test_reuse_across_records_and_revisions(self):
        r=self.reserved();r.update(id='one',lineage='one');other=copy.deepcopy(r);other.update(id='two',lineage='two')
        with self.assertRaises(ValueError):conflicts(r,[other])
        other['lineage']='one';conflicts(r,[other])
    def test_issued_budget_not_released_by_unissued_revision(self):
        original=self.reserved();original.update(id='issued',lineage='old',status='issued',issued_at='2026-10-01',saved_at='2026-10-01')
        draft=copy.deepcopy(original);draft.update(id='draft',status='draft',saved_at='2026-10-02');draft['reserved_sources']=[]
        target=self.reserved();target.update(id='new',lineage='new')
        with self.assertRaises(ValueError):conflicts(target,[original,draft])
    def test_same_late_cn_cannot_release_different_receipts(self):
        a,b=pair();a['entries'].insert(1,entry('r2','2026-01-20','receipt',credit='100000'));a['closing']=str(Decimal(a['closing'])-100000);b=doc(a['closing'],[],start='2026-04-01',end='2027-03-31')
        first=attach(record(b),a,b,'2026-01-01','2026-03-31',approve(),[{'receipt':'r1','crop':'Cotton','amount':'10000'}]);first.update(id='first',lineage='first')
        second_approval=[{**approve()[0],'receipt':'r2'}]
        second=attach(record(b),a,b,'2026-01-01','2026-03-31',second_approval,[{'receipt':'r2','crop':'Cotton','amount':'10000'}]);second.update(id='second',lineage='second')
        with self.assertRaisesRegex(ValueError,'duplicate CN'):conflicts(first,[second])
    def test_overlapping_opening_credit_blocked(self):
        a=doc('0',[entry('r1','2026-01-15','receipt',credit='10000')]);b=doc('-10000',[],start='2026-04-01',end='2027-03-31')
        r=attach(record(b),a,b,'2026-01-01','2026-03-31',[],[{'receipt':'r1','crop':'Cotton','amount':'10000'}]);r['opening_sources']=[{'id':'double','date':None,'amount':'1'}]
        with self.assertRaises(ValueError):validate_input_limits(r,cfg())
    def test_frozen_record_cannot_change(self):
        a,b=pair();r=record(b);r['status']='issued'
        with self.assertRaises(ValueError):attach(r,a,b,'2026-01-01','2026-03-31',[],[])
if __name__=='__main__':unittest.main(verbosity=2)
