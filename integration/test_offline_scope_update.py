"""Username uniqueness and season/product separation on synthetic HTTP data."""
import concurrent.futures
import copy
import sys
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'cn/backend'),str(ROOT/'cn/tests'),str(ROOT/'integration')]
from test_portal import PortalTests
from test_accounts_http import Browser,TEMP_PASSWORD
from test_calculator_http import CalculatorHTTPTests
from cn_web.security import AuthError

class UsernameUpdateTests(PortalTests):
    def test_check_is_scoped_case_insensitive_and_does_not_create_accounts(self):
        url='/api/portal/username-availability'
        self.assertEqual(Browser(self.origin).request(url,{'username':'new-login'})[0],401)
        _,regular=self.user_browser()
        self.assertEqual(regular.request(url,{'username':'new-login'})[0],403)
        self.assertEqual(self.admin.request(url,{'username':'new-login'},headers={'X-CSRF-Token':'wrong'})[0],403)
        before=len(self.accounts.list_users(self.admin.token))
        self.assertEqual(self.admin.request(url,{'username':'NEW-LOGIN'})[1]['available'],True)
        user=self.accounts.create_user(self.admin.token,username='new-login',temporary_password=TEMP_PASSWORD,permissions=[])
        code,result,_=self.admin.request(url,{'username':'NEW-LOGIN'})
        self.assertEqual(code,200,result);self.assertFalse(result['available'])
        self.assertEqual(set(result),{'username','available','prepared_retry'})
        self.assertEqual(len(self.accounts.list_users(self.admin.token)),before+1)
        self.assertEqual(self.admin.request('/api/admin/users',{'username':'NEW-LOGIN','temporary_password':TEMP_PASSWORD,'permissions':[],'quota_bytes':1048576})[0],409)
        self.assertEqual(next(u for u in self.accounts.list_users(self.admin.token) if u['username']=='new-login')['id'],user['id'])
        self.accounts.update_user(self.admin.token,user['id'],{'enabled':False})
        self.assertFalse(self.admin.request(url,{'username':'NEW-LOGIN'})[1]['available'])

    def test_simultaneous_creations_allow_exactly_one_account(self):
        def create(_):
            try:return self.accounts.create_user(self.admin.token,username='race-login',temporary_password=TEMP_PASSWORD,permissions=[])['id']
            except AuthError as e:return e.status
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:results=list(pool.map(create,range(2)))
        self.assertEqual(sum(isinstance(r,str) for r in results),1,results)
        self.assertEqual(sum(r==409 for r in results),1,results)

    def test_prepared_signup_retry_is_not_a_different_users_duplicate(self):
        from test_unified_accounts import UnifiedTests
        p=UnifiedTests.payload(self);member=UnifiedTests.member(self)
        created=self.accounts.provision(self.admin.token,p,member)
        result=self.accounts.username_availability(self.admin.token,p['username'].upper(),p['member_id'])
        self.assertTrue(result['available']);self.assertTrue(result['prepared_retry'])
        self.assertFalse(self.accounts.username_availability(self.admin.token,p['username'],'2'*24)['available'])
        self.assertEqual(self.accounts.provision(self.admin.token,p,member)['user_id'],created['user_id'])

class ProductScopeTests(CalculatorHTTPTests):
    def test_same_product_seasons_and_exclusions_preserve_full_ledger(self):
        _,b=self.user_browser();_,w=self.setup_book(b);lid,original=self.mapped_source(b,w)
        rows={};results={}
        for season in ['Kharif','Rabi']:
            code,r,_=self.calc(b,w,'native-open',{'ledger_id':lid,'season':season});self.assertEqual(code,200,r);rows[season]=r
            code,result,_=self.calc(b,w,'calculate',r);self.assertEqual(code,200,result);results[season]=result
        self.assertNotEqual(rows['Kharif']['id'],rows['Rabi']['id'])
        kh={x['product_id']:x['net_sold'] for x in results['Kharif']['product_CNs']}
        ra={x['product_id']:x['net_sold'] for x in results['Rabi']['product_CNs']}
        self.assertNotEqual(kh,ra)
        r=copy.deepcopy(rows['Kharif']);target=next(iter(kh))
        raw_dates=[e['date'] for e in r['entries']]
        raw_amounts=[(e['debit'],e['credit']) for e in r['entries']]
        for e in r['entries']:
            for item in e.get('items',[]):
                if item.get('product')==target and not item.get('exclude'):
                    item.update(exclude=True,review_reason='Working-period product selection: Kharif')
        blocked=copy.deepcopy(r)
        blocked['allocations']=[{'id':'existing-split','source':next(e['id'] for e in r['entries'] if e['kind']=='receipt'),'type':'CD','scheme':'existing-group','product':'','amount':'10'}]
        self.assertEqual(self.calc(b,w,'save',blocked)[0],409)
        self.assertEqual(self.calc(b,w,'record',{'id':r['id']})[1]['record']['allocations'],[])
        code,r,_=self.calc(b,w,'save',r);self.assertEqual(code,200,r)
        code,result,_=self.calc(b,w,'calculate',r);self.assertEqual(code,200,result)
        self.assertNotIn(target,{x['product_id'] for x in result['product_CNs']})
        self.assertEqual(result['ledger_closing'],results['Kharif']['ledger_closing'])
        self.assertEqual(result['sources'],results['Kharif']['sources'])
        reopened=self.calc(b,w,'record',{'id':r['id']})[1]['record']
        self.assertEqual([e['date'] for e in reopened['entries']],raw_dates)
        self.assertEqual([(e['debit'],e['credit']) for e in reopened['entries']],raw_amounts)
        self.assertEqual(self.calc(b,w,'record',{'id':rows['Rabi']['id']})[1]['result'],results['Rabi'])
        self.assertEqual(self.detail(b,w,lid)['ledger']['document'],original)
        for e in reopened['entries']:
            for item in e.get('items',[]):
                if str(item.get('review_reason','')).startswith('Working-period product selection: '):
                    item['exclude']=False;item.pop('review_reason',None)
        code,restored,_=self.calc(b,w,'save',reopened);self.assertEqual(code,200,restored)
        result=self.calc(b,w,'calculate',restored)[1]
        self.assertEqual({x['product_id']:x['net_sold'] for x in result['product_CNs']},kh)

if __name__=='__main__':
    suite=unittest.TestSuite()
    for cls in [UsernameUpdateTests,ProductScopeTests]:
        suite.addTests(cls(n) for n in cls.__dict__ if n.startswith('test_'))
    result=unittest.TextTestRunner(verbosity=2).run(suite)
    raise SystemExit(not result.wasSuccessful())
