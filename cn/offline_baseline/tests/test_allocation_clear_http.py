import unittest,urllib.request,urllib.error
import test_http as shared
from test_regular_cash import scenario
class AllocationClearHTTPTests(unittest.TestCase):
 setUpClass=classmethod(shared.LocalHTTPTests.setUpClass.__func__)
 tearDownClass=classmethod(shared.LocalHTTPTests.tearDownClass.__func__)
 get=classmethod(shared.LocalHTTPTests.get.__func__)
 post=shared.LocalHTTPTests.post
 def test_auth_scope_preview_apply(self):
  r,s,pid=scenario();self.post('/api/settings',s);r=self.post('/api/save',r);b={'id':r['id'],'revision':r['revision'],'scope':'all'}
  with self.assertRaises(urllib.error.HTTPError) as err:self.post('/api/allocation-clear-preview',b,token=False)
  self.assertEqual(err.exception.code,403)
  with self.assertRaises(urllib.error.HTTPError):self.post('/api/allocation-clear-preview',{**b,'workbook_id':'other'})
  plan=self.post('/api/allocation-clear-preview',b);self.assertEqual(plan['released_total'],'600000');self.assertEqual(next(x for x in self.get('/api/state')['records'] if x['id']==r['id']),r)
  saved=self.post('/api/allocation-clear-apply',{**b,'expected':plan['expected']});self.assertEqual(saved['entries'],r['entries']);self.assertEqual(saved['allocations'],[])
  with self.assertRaises(urllib.error.HTTPError):self.post('/api/allocation-clear-apply',{**b,'expected':plan['expected']})
  with urllib.request.urlopen('http://127.0.0.1:18765/payment-workbench.js') as response:self.assertIn('javascript',response.headers['Content-Type']);self.assertIn(b'Clear all party allocations',response.read())
