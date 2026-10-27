import unittest,urllib.request,urllib.error
import test_http as shared
from test_regular_cash import scenario

class CashRemovalHTTPTests(unittest.TestCase):
 setUpClass=classmethod(shared.LocalHTTPTests.setUpClass.__func__)
 tearDownClass=classmethod(shared.LocalHTTPTests.tearDownClass.__func__)
 get=classmethod(shared.LocalHTTPTests.get.__func__)
 post=shared.LocalHTTPTests.post
 def test_preview_apply_auth_scope_and_asset(self):
  r,s,pid=scenario();self.post('/api/settings',s);r=self.post('/api/save',r);payload={'record':r,'scheme':'scheme-5','product':pid}
  with self.assertRaises(urllib.error.HTTPError) as err:self.post('/api/cash-remove-apply',payload,token=False)
  self.assertEqual(err.exception.code,403)
  bad={**payload,'record':{**r,'workbook_id':'another'}}
  with self.assertRaises(urllib.error.HTTPError):self.post('/api/cash-remove-preview',bad)
  plan=self.post('/api/cash-remove-preview',payload);self.assertEqual(plan['released_total'],'300000')
  current=next(x for x in self.get('/api/state')['records'] if x['id']==r['id']);self.assertEqual(current,r)
  saved=self.post('/api/cash-remove-apply',{**payload,'settings_version':plan['settings_version']});self.assertEqual(saved['cash_splits'],[]);self.assertEqual(saved['entries'],r['entries']);self.assertEqual(len(saved['allocations']),2)
  with urllib.request.urlopen('http://127.0.0.1:18765/scheme-options.js') as response:self.assertIn('javascript',response.headers['Content-Type']);self.assertIn(b'Add Cash Scheme',response.read())
