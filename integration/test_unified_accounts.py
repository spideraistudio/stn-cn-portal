import copy,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT/'cn/backend'),str(ROOT/'cn/tests'),str(ROOT/'integration')]
from test_portal import PortalTests
from cn_web.security import PERMISSIONS,AuthError
from test_accounts_http import TEMP_PASSWORD,USER_PASSWORD
class UnifiedTests(PortalTests):
 setUp=PortalTests.setUp
 stop=PortalTests.stop
 def payload(self):return {'member_id':'1'*24,'username':'company-admin','temporary_password':TEMP_PASSWORD,'permissions':sorted(PERMISSIONS),'cn':True,'stn':True}
 def member(self,status='pending'):return {'exists':True,'member_id':'1'*24,'company_name':'Requested company','status':status}
 def test_prepare_retry_activation_and_private_identity(self):
  p=self.payload();r=self.accounts.provision(self.admin.token,p,self.member());uid=r['user_id']
  with self.assertRaises(AuthError):self.accounts.login(p['username'],TEMP_PASSWORD,'local')
  self.assertEqual(self.accounts.provision(self.admin.token,p,self.member())['user_id'],uid)
  with self.assertRaises(AuthError):self.accounts.activate_provision(self.admin.token,self.member())
  self.accounts.activate_provision(self.admin.token,self.member('approved'))
  t=self.accounts.login(p['username'],TEMP_PASSWORD,'local');self.assertTrue(self.accounts.me(t)['must_change_password'])
  with self.assertRaises(AuthError):self.accounts.workspace(t)
  self.accounts.change_password(t,TEMP_PASSWORD,USER_PASSWORD)
  t=self.accounts.login(p['username'],USER_PASSWORD,'local');self.assertEqual(self.accounts.me(t)['quota_bytes'],1024**3)
  self.assertEqual(self.accounts.me(t)['modules'],{'cn':True,'stn':True})
 def test_failed_terms_rollback_all_rows(self):
  p=self.payload();p['quota_bytes']=0
  with self.assertRaises(AuthError):self.accounts.provision(self.admin.token,p,self.member())
  with self.accounts._tx() as db:
   self.assertEqual(db.execute('SELECT count(*) FROM portal_companies').fetchone()[0],0)
   self.assertEqual(db.execute('SELECT count(*) FROM portal_provisioning').fetchone()[0],0)
   self.assertIsNone(db.execute('SELECT 1 FROM users WHERE username=?',(p['username'],)).fetchone())
 def test_retry_cannot_change_grants_or_create_duplicate(self):
  p=self.payload();self.accounts.provision(self.admin.token,p,self.member());p['stn']=False
  with self.assertRaises(AuthError):self.accounts.provision(self.admin.token,p,self.member())
 def test_cn_only_and_staff_delegation_failure_atomic(self):
  p=self.payload();p['stn']=False;r=self.accounts.provision(self.admin.token,p,self.member());self.accounts.activate_provision(self.admin.token,self.member('cn_only'))
  t=self.accounts.login(p['username'],TEMP_PASSWORD,'local');self.accounts.change_password(t,TEMP_PASSWORD,USER_PASSWORD);t=self.accounts.login(p['username'],USER_PASSWORD,'local')
  staff={'username':'staff-user','temporary_password':TEMP_PASSWORD,'permissions':[],'cn':True,'stn':True}
  with self.assertRaises(AuthError):self.accounts.provision(t,staff)
  self.assertEqual(self.accounts.list_users(t),[])
  staff['stn']=False;u=self.accounts.provision(t,staff);self.assertTrue(u['user_id'])
  self.assertEqual(self.accounts.list_users(t)[0]['quota_bytes'],250*1024**2)
  from test_accounts_http import Browser
  b=Browser(self.origin);b.token=t;b.request('/api/me')
  code,out,_=b.request('/api/portal/update-user',{'user_id':u['user_id'],'cn':True,'stn':True,'changes':{'quota_bytes':100*1024**2}})
  self.assertEqual(code,409,out)
  self.assertEqual(self.accounts.list_users(t)[0]['quota_bytes'],250*1024**2)

if __name__=='__main__':
 suite=unittest.TestSuite(UnifiedTests(n) for n in UnifiedTests.__dict__ if n.startswith('test_'))
 result=unittest.TextTestRunner(verbosity=2).run(suite)
 raise SystemExit(not result.wasSuccessful())
