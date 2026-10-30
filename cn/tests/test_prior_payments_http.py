"""Owned-file, permissions, persistence and anti-tamper checks over real HTTP."""
import base64,copy,io,unittest
import test_accounts_http as helpers
import test_ledger_http as ledger_tests
CATALOGUE=ledger_tests.CATALOGUE;PERIODS=ledger_tests.PERIODS
import test_calculator_http as calculator_tests
from cn_web.security import PERMISSIONS

def statement(previous=True,wrong=False):
    from reportlab.pdfgen import canvas
    lines=['Ledger Statement','For 01-Apr-25 to 31-Mar-26' if previous else 'For 01-Apr-26 to 31-Mar-27','Other Seller, Town' if wrong else 'Test Seeds, Town','Town, Gujarat','Date Particulars Amount Balance']
    lines += ['01-Apr-25 Opening Balance 200000.00','15-Jan-26 Receipt JAN300 300000.00 -100000.00','NEFT-JAN-ORIGINAL-REFERENCE','10-Feb-26 Credit Note CN90 90000.00 -190000.00','Earlier sales benefit','10-Mar-26 Sales Invoice PADDY300 300000.00 110000.00','DAWAT 1 kg 3000.00 pkt @ 100.00 300000.00','Closing Balance 110000.00'] if previous else ['01-Apr-26 Opening Balance 110000.00','10-May-26 Receipt PADDYPAY 300000.00 -190000.00','NEFT-PADDY-MAY-PAYMENT','Closing Balance -190000.00']
    b=io.BytesIO();c=canvas.Canvas(b);y=800
    for t in lines:c.drawString(40,y,t);y-=20
    c.save();return b.getvalue()
class PriorPaymentHTTPTests(unittest.TestCase):
    setUp=helpers.AccountHTTPTests.setUp;stop=helpers.AccountHTTPTests.stop;create=helpers.AccountHTTPTests.create;user_browser=helpers.AccountHTTPTests.user_browser
    setup_book=ledger_tests.LedgerHTTPTests.setup_book;url=ledger_tests.LedgerHTTPTests.url;state=ledger_tests.LedgerHTTPTests.state
    calc=calculator_tests.CalculatorHTTPTests.calc;saved=calculator_tests.CalculatorHTTPTests.saved
    def prepare(self):
        u,b=self.user_browser();_,w=self.setup_book(b)
        cat=CATALOGUE+[{'id':'cotton','name':'Cotton','crop':'Cotton','segment':'Cotton','packing_kg':'0.475','aliases':[]}]
        self.assertEqual(b.request(self.url(w,'config'),{'revision':self.state(b,w)['revision'],'catalogue':cat,'periods':PERIODS},'PUT')[0],200)
        code,out,_=self.calc(b,w,'native-import',{'data':base64.b64encode(statement(False)).decode(),'filename':'Current.pdf','season':'Kharif'});self.assertEqual(code,200,out);r=out['native_record']
        code,out,_=self.calc(b,w,'native-audit-import',{'data':base64.b64encode(statement()).decode(),'filename':'Prior.pdf'});self.assertEqual(code,200,out)
        refs=out['documents'];code,matched,_=self.calc(b,w,'native-payment-history-match',{'id':r['id'],'revision':r['revision'],'documents':refs});self.assertEqual(code,200,matched)
        return u,b,w,r,refs,matched
    def body(self,r,m):
        plan=m['plan'];return {'id':r['id'],'revision':r['revision'],'previous':m['previous'],'start':plan['start'],'end':plan['end'],'approvals':[{'cn':plan['cn_candidates'][0]['id'],'receipt':plan['rows'][0]['id'],'earned':'2025-12-31','reason':'Verified earlier sales benefit'}],'selections':[{'receipt':plan['rows'][0]['id'],'crop':'Cotton','amount':'190000'}]}
    def test_unlink_preserves_statement_and_opening(self):
        u,b,w,r,refs,m=self.prepare()
        code,r,_=self.calc(b,w,'native-payment-history-save',self.body(r,m));self.assertEqual(code,200,r)
        opening=r['opening'];entries=copy.deepcopy(r['entries'])
        code,out,_=self.calc(b,w,'native-payment-history-unlink',{'id':r['id'],'revision':r['revision']})
        self.assertEqual(code,200,out);self.assertFalse(out.get('payment_history'));self.assertEqual(out['reserved_sources'],[])
        self.assertEqual(out['opening'],opening);self.assertEqual(out['entries'],entries)

    def test_real_pdf_match_cn_reservation_save_reopen_tamper_and_backup(self):
        u,b,w,r,refs,m=self.prepare();self.assertTrue(m['match']['matched']);self.assertEqual(m['plan']['rows'][0]['available'],'100000.00')
        body=self.body(r,m);code,plan,_=self.calc(b,w,'native-payment-history-preview',body);self.assertEqual(code,200,plan);self.assertEqual(float(plan['rows'][0]['available']),190000)
        code,r,_=self.calc(b,w,'native-payment-history-save',body);self.assertEqual(code,200,r);self.assertEqual(float(r['old_dues']),300000)
        code,calc,_=self.calc(b,w,'calculate',r);self.assertEqual(code,200,calc);self.assertEqual(float(calc['mismatch']),0)
        self.assertEqual(float(calc['sources'][0]['available']),190000);self.assertEqual(float(calc['sources'][1]['available']),0);self.assertEqual(float(calc['old_dues_remaining']),0)
        self.assertTrue(self.calc(b,w,'record',{'id':r['id']})[1]['record']['payment_history'])
        for field in ('reserved_sources','payment_history'):
            bad=copy.deepcopy(r);bad[field]=[] if field=='reserved_sources' else {}
            self.assertEqual(self.calc(b,w,'save',bad)[0],409)
        # No duplicate registration on retry; same source IDs, budget and record.
        body['revision']=r['revision'];code,r2,_=self.calc(b,w,'native-payment-history-save',body);self.assertEqual(code,200,r2);self.assertEqual(r2['reserved_sources'],r['reserved_sources'])
        backup=b.request('/api/projects/'+w['project']+'/export')[1];code,out,_=b.request('/api/projects/import',{'backup':backup});self.assertEqual(code,201,out)
        w2=next(x for x in b.request('/api/data/workbooks')[1]['items'] if x['project']==out['project_id']);restored=self.saved(b,w2)['records'][0];self.assertEqual(restored['reserved_sources'],r['reserved_sources'])
        # A copied project cannot finalise a second use of the protected receipt.
        code,blocked,_=self.calc(b,w2,'finalise',{'id':restored['id'],'revision':restored['revision']});self.assertNotEqual(code,200);self.assertIn('already reserved',blocked.get('error',''))
    def test_wrong_party_ambiguous_and_cross_owner_files_blocked(self):
        _,b,w,r,refs,m=self.prepare();_,other=self.user_browser('other');_,w2=self.setup_book(other)
        # Owned source references cannot be used by another account/workbook.
        self.assertNotEqual(self.calc(other,w2,'native-payment-history-match',{'id':r['id'],'revision':r['revision'],'documents':refs})[0],200)
        code,out,_=self.calc(b,w,'native-audit-import',{'data':base64.b64encode(statement(wrong=True)).decode(),'filename':'Wrong.pdf'});self.assertEqual(code,200,out)
        self.assertEqual(self.calc(b,w,'native-payment-history-match',{'id':r['id'],'revision':r['revision'],'documents':out['documents']})[0],400)
        self.assertEqual(self.calc(b,w,'native-payment-history-match',{'id':r['id'],'revision':r['revision'],'documents':refs*2})[0],400)
    def test_permissions_and_stale_requests(self):
        u,b,w,r,refs,m=self.prepare();body=self.body(r,m)
        self.admin.request('/api/admin/users/'+u['id'],{'permissions':list(PERMISSIONS-{'allocate_payments'})},'PATCH');self.assertEqual(self.calc(b,w,'native-payment-history-save',body)[0],403)
        self.admin.request('/api/admin/users/'+u['id'],{'permissions':list(PERMISSIONS)},'PATCH');body['revision']+=1;self.assertEqual(self.calc(b,w,'native-payment-history-save',body)[0],409)
if __name__=='__main__':unittest.main(verbosity=2)
