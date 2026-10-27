"""Delegated limits via real HTTP, including requests bypassing the form."""
import sys, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'integration'),str(ROOT/'cn/tests'),str(ROOT/'cn/backend')]
from test_unified_accounts import UnifiedTests
from test_accounts_http import Browser,TEMP_PASSWORD,USER_PASSWORD

class StorageCeilingTests(UnifiedTests):
 def test_delegated_ceiling_create_edit_and_platform_override(self):
  p=self.payload();p['stn']=False
  created=self.accounts.provision(self.admin.token,p,self.member())
  self.accounts.activate_provision(self.admin.token,self.member('cn_only'))
  token=self.accounts.login(p['username'],TEMP_PASSWORD,'local')
  self.accounts.change_password(token,TEMP_PASSWORD,USER_PASSWORD)
  b=Browser(self.origin);b.login(p['username'],USER_PASSWORD)
  state=b.request('/api/portal/state')[1]
  self.assertEqual(state['user']['user_quota_bytes'],250*1048576)
  self.assertEqual(state['user']['quota_bytes'],1024*1048576)
  staff={'username':'ceiling-staff','temporary_password':TEMP_PASSWORD,'permissions':[],'cn':True,'stn':False,'quota_bytes':250*1048576}
  for size in (251,2560):
   code,out,_=b.request('/api/portal/provision',{**staff,'quota_bytes':size*1048576})
   self.assertEqual(code,403,out)
   self.assertEqual(self.accounts.list_users(b.token),[])
  code,u,_=b.request('/api/portal/provision',staff);self.assertEqual(code,201,u)
  for size in (251,2560):
   code,out,_=b.request('/api/portal/update-user',{'user_id':u['user_id'],'cn':True,'stn':False,'changes':{'quota_bytes':size*1048576}})
   self.assertEqual(code,403,out)
   self.assertEqual(self.accounts.list_users(b.token)[0]['quota_bytes'],250*1048576)
  code,out,_=b.request('/api/admin/users/'+created['user_id'],{'user_quota_bytes':500*1048576},'PATCH')
  self.assertEqual(code,404,out)
  self.accounts.update_user(self.admin.token,created['user_id'],{'user_quota_bytes':500*1048576})
  code,out,_=b.request('/api/portal/update-user',{'user_id':u['user_id'],'cn':True,'stn':False,'changes':{'quota_bytes':500*1048576}})
  self.assertEqual(code,200,out)
  self.assertEqual(self.accounts.list_users(b.token)[0]['quota_bytes'],500*1048576)

if __name__=='__main__':
 result=unittest.TextTestRunner(verbosity=2).run(unittest.TestSuite([StorageCeilingTests('test_delegated_ceiling_create_edit_and_platform_override')]))
 raise SystemExit(not result.wasSuccessful())
