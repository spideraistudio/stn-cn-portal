"""New layout adapters: synthetic evidence and optional private PDF acceptance.
Set CN_MULTI_STATEMENT_DIR to the local sample directory; private PDFs are never bundled.
"""
import base64
import copy
import os
from pathlib import Path
import unittest
import test_accounts_http as helpers
import test_native_interface_http as native_tests
from cn_web.statement_import import import_pdf_documents, monetary_cells
from cn_web.statement_review import project_reviews, same_issuer, analyse_pair, PREFIX
from cn_web.product_mapping import packing
from settings import initial_settings
from cn_web.security import PERMISSIONS


class ReviewTests(unittest.TestCase):
    def document(self):
        return {'source':{'format':'account-compact-v1','opening_omitted_zero':True},'entries':[{'id':'a','reference':'B1','items':[{'name':'Seed','unit':'unknown','amount_basis':'calculated_qty_times_rate'}]}]}
    def test_canonical_review_gates_cannot_be_removed_by_browser_metadata(self):
        d=self.document();r=copy.deepcopy(d);r['import_warnings']=[]
        project_reviews(r,d);self.assertEqual(len(r['import_warnings']),3)
        r['source']={};r['entries'][0]['items'][0].update(unit='packet',unit_review_reason='Invoice confirms packets')
        r['entries'][0]['amount_review_reason']='Verified invoice amounts';r['opening_review_reason']='Confirmed no prior balance'
        project_reviews(r,d);self.assertEqual(r['import_warnings'],[])
        r['entries']=[];project_reviews(r,d);self.assertTrue(any('missing' in w for w in r['import_warnings']))
    def test_malformed_pdf_is_a_validation_error(self):
        with self.assertRaises(ValueError):import_pdf_documents(b'%PDF-broken',initial_settings())

    def test_column_geometry_and_ambiguity(self):
        row={'page':1,'words':[{'text':'50.00','x1':399},{'text':'100.00','x1':543}]}
        cells,found=monetary_cells(row,{'credit':381,'debit':461},20)
        self.assertEqual(found,{'credit'});self.assertEqual(cells['credit'],50)
        with self.assertRaises(ValueError):monetary_cells(row,{'credit':390,'debit':400},20)
    def test_packing_and_issuer_separation(self):
        self.assertEqual(packing({'name':'SEED 500grms'}),'0.5')
        a={'source':{'issuer':'One'}};b={'source':{'issuer':'Two'}}
        self.assertFalse(same_issuer(a,b))
        with self.assertRaisesRegex(ValueError,'issuing company'):analyse_pair(a,b)


@unittest.skipUnless(os.environ.get('CN_MULTI_STATEMENT_DIR'),'Private acceptance PDFs supplied separately')
class PrivateStatementTests(unittest.TestCase):
    setUp=helpers.AccountHTTPTests.setUp
    stop=helpers.AccountHTTPTests.stop
    create=helpers.AccountHTTPTests.create
    user_browser=helpers.AccountHTTPTests.user_browser
    setup_book=native_tests.NativeInterfaceTests.setup_book
    state=native_tests.NativeInterfaceTests.state
    url=native_tests.NativeInterfaceTests.url
    calc=native_tests.NativeInterfaceTests.calc
    saved=native_tests.NativeInterfaceTests.saved

    def test_three_actual_pdfs_owned_import_repeat_review_and_finalisation_block(self):
        user,b=self.user_browser();_,other=self.user_browser('other-user')
        files=list(Path(os.environ['CN_MULTI_STATEMENT_DIR']).glob('*'))
        expected={'tally-balance-columns-v1':(35,'-35053.00'),'account-compact-v1':(31,'1243450.00'),'account-item-detail-v1':(6,'42000.00')}
        count=0
        for p in files:
            if p.suffix.lower()!='.pdf':continue
            doc=import_pdf_documents(p.read_bytes(),initial_settings())[0];fmt=doc['source']['format'];count+=1
            self.assertEqual((len(doc['entries']),doc['closing']),expected[fmt])
            self.assertEqual(len({e['id'] for e in doc['entries']}),len(doc['entries']))
            self.assertEqual(doc,import_pdf_documents(p.read_bytes(),initial_settings())[0])
            import io, pdfplumber
            from cn_web.statement_import import page_rows, parse_tally_balance, parse_account_statement
            with pdfplumber.open(p) as pdf: pages=[page_rows(page,n) for n,page in enumerate(pdf.pages,1)]
            if fmt=='account-compact-v1':
                with self.assertRaises(ValueError):parse_account_statement(pages[:1]+pages[2:],initial_settings(),'test',True)
            if fmt=='tally-balance-columns-v1':
                with self.assertRaises(ValueError):parse_tally_balance(pages[:2],initial_settings(),'test')

            _,w=self.setup_book(b)
            body={'data':base64.b64encode(p.read_bytes()).decode(),'filename':p.name}
            code,out,_=self.calc(b,w,'native-import',body);self.assertEqual(code,200,out)
            r=out['native_record'];original=copy.deepcopy(r['source'])
            code,repeat,_=self.calc(b,w,'native-import',body);self.assertEqual(code,200,repeat);self.assertEqual(repeat['native_record']['id'],r['id'])
            self.assertEqual(self.calc(other,w,'record',{'id':r['id']})[0],404)
            code,result,_=self.calc(b,w,'calculate',r);self.assertEqual(code,200,result);self.assertFalse(result['can_finalise'])
            self.assertNotEqual(self.calc(b,w,'finalise',{'id':r['id'],'revision':r['revision']})[0],200)
            if fmt=='account-item-detail-v1':
                self.assertTrue(all(i['unit']=='packet' for e in r['entries'] for i in e['items']))
                self.assertTrue(all(i['mapping_suggestion']['detected_packing_kg']=='3' for e in r['entries'] for i in e['items']))
                r['opening_review_reason']='Confirmed by reviewing earlier ledger'
                self.admin.request('/api/admin/users/'+user['id'],{'permissions':list(PERMISSIONS-{'edit_ledger'})},'PATCH')
                self.assertEqual(self.calc(b,w,'save',r)[0],403)
                self.admin.request('/api/admin/users/'+user['id'],{'permissions':list(PERMISSIONS)},'PATCH')
            if fmt=='account-compact-v1':
                kds=next(i for e in r['entries'] for i in e['items'] if 'KDS-726' in i['name']);self.assertEqual(kds['unit'],'packet');self.assertEqual(kds['qty'],'250.000');self.assertEqual(kds['rate'],'2400.00')
                self.assertTrue(any(i['unit']=='unknown' for e in r['entries'] for i in e['items']))
                self.assertTrue(any(e.get('item_total_difference') for e in r['entries']))
            code,r,_=self.calc(b,w,'save',r);self.assertEqual(code,200,r);self.assertEqual(r['source'],original)
            code,reloaded,_=self.calc(b,w,'record',{'id':r['id']});self.assertEqual(code,200,reloaded);self.assertEqual(reloaded['record']['source'],original)
            if fmt=='account-compact-v1':
                backup=b.request('/api/projects/'+w['project']+'/export')[1]
                code,restored,_=b.request('/api/projects/import',{'backup':backup});self.assertEqual(code,201,restored)
                book=next(x for x in b.request('/api/data/workbooks')[1]['items'] if x['project']==restored['project_id'])
                self.assertEqual(self.saved(b,book)['records'][0]['source'],original)
            print('PASS actual PDF:',fmt,'vouchers',len(doc['entries']),'closing',doc['closing'])
        self.assertEqual(count,3)

if __name__=='__main__':unittest.main()
