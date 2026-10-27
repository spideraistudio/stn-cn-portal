import sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'integration'),str(ROOT/'cn/tests'),str(ROOT/'cn/backend')]
from test_portal import PortalTests
class UXPhase1(PortalTests):
 def test_first_workbook_atomic_owned_and_validated(self):
  payload={'name':'Gujarat Kharif 2026','state':'Gujarat','period':'Kharif 2026','start':'2026-04-01','end':'2026-08-31','cutoff':'2026-10-31'}
  user,b=self.user_browser()
  code,out,_=b.request('/api/portal/start-workbook',{**payload,'end':'2025-01-01'})
  self.assertIn(code,(400,409),out)
  self.assertEqual(b.request('/api/data/projects')[1]['items'],[])
  code,out,_=b.request('/api/portal/start-workbook',payload)
  self.assertEqual(code,201,out)
  headers={'X-CN-Project':out['project'],'X-CN-Workbook':out['workbook']}
  code,state,_=b.request('/api/calculator/native-state',headers=headers)
  self.assertEqual(code,200,state);self.assertEqual(state['workbook']['name'],payload['name'])
  self.assertEqual(state['settings']['seasons'][0]['start'],payload['start'])
  _,other=self.user_browser('other-user')
  self.assertEqual(other.request('/api/calculator/native-state',headers=headers)[0],404)
  self.assertEqual(other.request('/api/portal/start-workbook',{**payload,'project':out['project']})[0],404)
  self.assertEqual(other.request('/api/data/projects')[1]['items'],[])
  _,reader=self.user_browser('reader-user',permissions=['view_workspace'])
  self.assertEqual(reader.request('/api/portal/start-workbook',payload)[0],403)
  self.assertEqual(reader.request('/api/data/projects')[1]['items'],[])
 def test_settings_navigation_and_legacy_workspace_redirect(self):
  code,html,_=self.admin.request('/account');self.assertEqual(code,200)
  for name in ['Account &amp; Settings','/settings/users','/settings/issues','/privacy','/terms','/disclaimer','/calculator']:self.assertIn(name,html)
  self.assertNotIn('href="/workspace"',html)
  code,html,_=self.admin.request('/workspace');self.assertEqual(code,200);self.assertIn('web-bridge.js',html)
if __name__=='__main__':
 result=unittest.TextTestRunner(verbosity=2).run(unittest.TestSuite(UXPhase1(n) for n in UXPhase1.__dict__ if n.startswith('test_')))
 raise SystemExit(not result.wasSuccessful())
