"""Password-only reset contract through real HTTP; synthetic isolated accounts."""
import sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'integration'),str(ROOT/'cn/tests'),str(ROOT/'cn/backend')]
from test_portal import PortalTests
from test_accounts_http import Browser,TEMP_PASSWORD,USER_PASSWORD
from cn_web.security import PERMISSIONS

class Phase2Tests(PortalTests):
 def test_scoped_password_only_reset(self):
  def person(name,role='user',parent=None):
   u=self.accounts.create_user(self.admin.token,username=name,temporary_password=TEMP_PASSWORD,permissions=sorted(PERMISSIONS),role=role,parent_admin=parent)
   t=self.accounts.login(name,TEMP_PASSWORD,'local');self.accounts.change_password(t,TEMP_PASSWORD,USER_PASSWORD)
   b=Browser(self.origin);b.login(name,USER_PASSWORD);return u,b
  owner,ob=person('owner','admin');other,xb=person('other','admin')
  own,ub=person('own-staff',parent=owner['id']);foreign,fb=person('foreign-staff',parent=other['id'])
  endpoint=lambda u:'/api/admin/users/'+u['id']+'/reset-password'
  payload={'temporary_password':TEMP_PASSWORD}
  for target in (other,foreign,owner):self.assertEqual(ob.request(endpoint(target),payload)[0],404)
  self.assertEqual(ub.request(endpoint(own),payload)[0],403)
  self.assertEqual(ob.request(endpoint(own),payload,headers={'X-CSRF-Token':'bad'})[0],403)
  before=next(u for u in self.accounts.overview(ob.token)['users'] if u['id']==own['id'])
  self.assertEqual(ob.request(endpoint(own),{'temporary_password':'short'})[0],400)
  self.assertEqual(ub.request('/api/me')[0],200)
  self.assertEqual(ob.request(endpoint(own),payload)[0],200)
  self.assertEqual(ub.request('/api/me')[0],401)
  after=next(u for u in self.accounts.overview(ob.token)['users'] if u['id']==own['id'])
  for field in ('permissions','quota_bytes','enabled','requested_cn','requested_stn','parent_admin'):self.assertEqual(before[field],after[field])
  ub.login('own-staff',TEMP_PASSWORD)
  self.assertTrue(ub.request('/api/me')[1]['user']['must_change_password'])
  self.assertEqual(ub.request('/api/workspace')[0],403)
  self.assertEqual(ub.request('/api/auth/password',{'current_password':TEMP_PASSWORD,'new_password':USER_PASSWORD})[0],200)
  ub.login('own-staff',USER_PASSWORD)
  self.assertEqual(ub.request('/api/workspace')[0],200)
  self.assertEqual(self.admin.request(endpoint(other),payload)[0],200)
  self.assertEqual(xb.request('/api/me')[0],401)
  self.assertEqual(fb.request('/api/me')[0],200)
  self.accounts.update_user(self.admin.token,owner['id'],{'manage_users':False})
  self.assertEqual(ob.request(endpoint(own),payload)[0],403)

if __name__=='__main__':
 result=unittest.TextTestRunner(verbosity=2).run(unittest.TestSuite([Phase2Tests('test_scoped_password_only_reset')]))
 raise SystemExit(not result.wasSuccessful())
