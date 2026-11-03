import base64,copy,io,unittest
from decimal import Decimal as D
from cn_web import ledger_service
from cn_web.security import PERMISSIONS
from period_accounting import view
from prior_payments import conflicts
from engine import compute
import test_period_accounting_update as period_tests
import test_split_settlement_update as split_tests
import test_native_interface_http as native
PERIOD=period_tests.PERIOD

def review(record,orders=None):
    p=record['period_accounting']
    record['accounting_review']={'evidence':p['review_evidence'],'reason':'Verified against original source vouchers','same_day_order':orders or {i['date']:'source' for i in p['review_items'] if i['kind']=='same_day_order'}}
    record['period_accounting']=view(record,PERIOD)

class PaymentGuardTests(unittest.TestCase):
    def example(self):
        r,cfg=split_tests.GramExampleTests().setup_example(opening='80000',cn='0',payment='100000',sale='200000');r['id']='a';return r,cfg
    def test_remaining_20000_not_gross_100000_is_shared(self):
        a,cfg=self.example();self.assertEqual(compute(a,cfg)['new_CN_total'],1600)
        b=copy.deepcopy(a);b.update(id='b',workbook_id='different')
        with self.assertRaisesRegex(ValueError,'already reserved/allocated'):conflicts(a,[b])
        a['allocations'][0]['amount']='10000';b['allocations'][0]['amount']='10000';conflicts(a,[b])
        b['allocations'][0]['amount']='10000.01'
        with self.assertRaises(ValueError):conflicts(a,[b])
    def test_numeric_format_and_frozen_history_do_not_bypass(self):
        a,cfg=self.example();b=copy.deepcopy(a);b.update(id='frozen',status='issued',deleted_at='2026-11-03')
        b['entries'][-1]['credit']='100000.00'
        with self.assertRaises(ValueError):conflicts(a,[b])
    def test_same_day_needs_review_and_order_changes_only_same_day(self):
        r,cfg=split_tests.GramExampleTests().setup_example('2026-10-10','2026-10-10')
        self.assertTrue(r['period_accounting']['review_required']);self.assertFalse(compute(r,cfg)['can_finalise'])
        original=copy.deepcopy(r['entries']);review(r,{'2026-10-10':'receipt_first'})
        self.assertFalse(r['period_accounting']['review_required']);self.assertEqual(r['period_accounting']['sources'][0]['available'],'0')
        self.assertEqual(r['entries'],original)
        r['accounting_review']['same_day_order']['2026-10-10']='cn_first';r['period_accounting']=view(r,PERIOD)
        self.assertEqual(r['period_accounting']['sources'][0]['available'],'20000')
    def test_unsupported_split_blocks_until_review_and_reopens_after_change(self):
        r,cfg=self.example();receipt=r['entries'][-1];receipt['source_lines']=[{'text':'Agst Ref OLD 30.00 Cr'}];r['period_accounting']=view(r,PERIOD)
        self.assertFalse(compute(r,cfg)['can_finalise']);review(r);self.assertTrue(compute(r,cfg)['can_finalise'])
        receipt['source_lines'][0]['text']='Agst Ref OLD 31.00 Cr';r['period_accounting']=view(r,PERIOD)
        self.assertTrue(r['period_accounting']['review_required']);self.assertFalse(compute(r,cfg)['can_finalise'])
    def test_pending_legacy_frozen_issue_requires_review_without_mutating_history(self):
        from unittest.mock import patch,Mock
        from cn_web.finish_service import FinishService
        from cn_web.security import AuthError
        frozen={'id':'frozen','revision':2,'status':'finalised','web_source':{'ledger_id':'source'},'result':{'unchanged':'proof'}}
        before=copy.deepcopy(frozen);store=Mock();store.project.return_value={'period_accounting':{'review_required':True}}
        with patch('cn_web.finish_service.Store.get',return_value=frozen):
            with self.assertRaisesRegex(AuthError,'draft revision'):FinishService(None).issue(None,{},'book',store,{'id':'frozen','revision':2})
        self.assertEqual(frozen,before)

    def test_payment_based_8_percent_and_cap_preserved(self):
        r,cfg=split_tests.GramExampleTests().setup_example(payment='100000',opening='0',cn='0',sale='108000')
        o=compute(r,cfg);self.assertTrue(o['can_finalise']);self.assertEqual(o['new_CN_total'],8000)
        self.assertEqual(o['final_balance'],0)

def statement():
    from reportlab.pdfgen import canvas
    lines=['Ledger Statement','For 01-Apr-26 to 31-Mar-27','Test Seeds, Town','Town, Gujarat','Date Particulars Amount Balance',
           '01-Apr-26 Opening Balance 80000.00','01-Oct-26 Sales Invoice S1 200000.00 280000.00','DAWAT 1 kg 2000.00 pkt @ 100.00 200000.00',
           '10-Oct-26 Credit Note CN1 20000.00 260000.00','Kharif benefit','10-Oct-26 Receipt R1 100000.00 160000.00','NEFT-ORIGINAL','Closing Balance 160000.00']
    data=io.BytesIO();c=canvas.Canvas(data);y=800
    for line in lines:c.drawString(40,y,line);y-=20
    c.save();return base64.b64encode(data.getvalue()).decode()

class AccountingReviewHTTPTests(unittest.TestCase):
    for name in ['setUp','stop','create','user_browser','setup_book','config','state','url','file','detail','calc','saved']:
        locals()[name]=getattr(native.NativeInterfaceTests,name)
    def prepare(self):
        u,b=self.user_browser();_,w=self.setup_book(b);self.config(b,w)
        code,out,_=self.calc(b,w,'native-import',{'data':statement(),'filename':'same-day.pdf','season':'Rabi'});self.assertEqual(code,200,out)
        r=out['native_record'];return u,b,w,r
    def body(self,r):
        return dict(id=r['id'],revision=r['revision'],evidence=r['period_accounting']['review_evidence'],reason='Verified original Tally voucher sequence',same_day_order={'2026-10-10':'cn_first'})
    def test_review_permission_atomicity_save_reopen_backup(self):
        u,b,w,r=self.prepare();self.assertTrue(r['period_accounting']['review_required'])
        self.assertNotEqual(self.calc(b,w,'finalise',{'id':r['id'],'revision':r['revision']})[0],200)
        body=self.body(r)
        self.admin.request('/api/admin/users/'+u['id'],{'permissions':list(PERMISSIONS-{'allocate_payments'})},'PATCH')
        self.assertEqual(self.calc(b,w,'native-accounting-review',body)[0],403)
        self.admin.request('/api/admin/users/'+u['id'],{'permissions':list(PERMISSIONS)},'PATCH')
        self.assertEqual(self.calc(b,w,'native-accounting-review',{**body,'evidence':'0'*64})[0],409)
        code,saved,_=self.calc(b,w,'native-accounting-review',body);self.assertEqual(code,200,saved)
        self.assertFalse(saved['period_accounting']['review_required']);self.assertEqual(saved['accounting_review']['reason'],body['reason'])
        code,reopened,_=self.calc(b,w,'record',{'id':saved['id']});self.assertEqual(code,200,reopened);self.assertFalse(reopened['record']['period_accounting']['review_required'])
        backup=b.request('/api/projects/'+w['project']+'/export')[1]
        code,clone,_=b.request('/api/projects/import',{'backup':backup});self.assertEqual(code,201,clone)
        cloned=next(x for x in b.request('/api/data/workbooks')[1]['items'] if x['project']==clone['project_id'])
        imported=self.saved(b,cloned)['records'][0];self.assertFalse(imported['period_accounting']['review_required'])
        _,other=self.user_browser('other');self.assertEqual(self.calc(other,w,'native-accounting-review',self.body(saved))[0],404)
    def test_remaining_budget_is_shared_across_owned_workbooks(self):
        u,b,w,r=self.prepare();_,w2=self.setup_book(b);self.config(b,w2)
        code,out,_=self.calc(b,w2,'native-import',{'data':statement(),'filename':'same-day.pdf','season':'Rabi'});self.assertEqual(code,200,out)
        second=out['native_record']
        for record in (r,second):
            receipt=next(e for e in record['entries'] if e['kind']=='receipt')
            record['allocations']=[dict(id='cash',source=receipt['id'],type='Settlement',amount='25000',scheme='',product='')]
        code,r,_=self.calc(b,w,'save',r);self.assertEqual(code,200,r)
        code,error,_=self.calc(b,w2,'save',second);self.assertNotEqual(code,200,error)
        self.assertIn('already reserved/allocated',error['error'])
        r['allocations'][0]['amount']='15000';self.assertEqual(self.calc(b,w,'save',r)[0],200)
        self.assertEqual(self.calc(b,w2,'save',second)[0],200)
    def test_save_cannot_forge_review(self):
        u,b,w,r=self.prepare()
        r['accounting_review']={'evidence':r['period_accounting']['review_evidence'],'reason':'Forged review via generic save','same_day_order':{'2026-10-10':'cn_first'},'actor':u['id'],'reviewed_at':'2026-11-03'}
        r['period_accounting']['review_required']=False
        code,saved,_=self.calc(b,w,'save',r);self.assertEqual(code,200,saved)
        self.assertTrue(saved['period_accounting']['review_required']);self.assertIsNone(saved['accounting_review'])

    def test_changed_order_cannot_silently_shrink_saved_allocation(self):
        u,b,w,r=self.prepare();receipt=next(e for e in r['entries'] if e['kind']=='receipt')
        r['allocations']=[dict(id='keep',source=receipt['id'],type='Settlement',amount='30000',scheme='',product='')]
        code,r,_=self.calc(b,w,'save',r);self.assertEqual(code,200,r)
        before=self.saved(b,w)
        body={**self.body(r),'same_day_order':{'2026-10-10':'receipt_first'}}
        code,out,_=self.calc(b,w,'native-accounting-review',body);self.assertNotEqual(code,200,out)
        self.assertEqual(self.saved(b,w),before)
