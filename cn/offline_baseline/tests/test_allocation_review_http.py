import unittest,urllib.error
import test_http as shared
from test_allocation_review import maize
class AllocationReviewHTTPTests(unittest.TestCase):
 setUpClass=classmethod(shared.LocalHTTPTests.setUpClass.__func__)
 tearDownClass=classmethod(shared.LocalHTTPTests.tearDownClass.__func__)
 get=classmethod(shared.LocalHTTPTests.get.__func__)
 post=shared.LocalHTTPTests.post
 def test_auth_scope_preview_apply_and_stale(self):
  r,s=maize(('4',),'50000');self.post('/api/settings',s);r=self.post('/api/save',r);b={'id':r['id'],'revision':r['revision'],'operation':'cd-group','scheme':'scheme-4','source':'receipt0','amount':'50000'}
  with self.assertRaises(urllib.error.HTTPError) as error:self.post('/api/allocation-review-preview',b,token=False)
  self.assertEqual(error.exception.code,403)
  with self.assertRaises(urllib.error.HTTPError):self.post('/api/allocation-review-preview',{**b,'workbook_id':'other'})
  p=self.post('/api/allocation-review-preview',b);self.assertEqual(next(x for x in self.get('/api/state')['records'] if x['id']==r['id']),r);self.assertGreater(float(p['released']),48000)
  saved=self.post('/api/allocation-review-apply',{**b,'expected':p['expected']});self.assertEqual(saved['entries'],r['entries'])
  with self.assertRaises(urllib.error.HTTPError):self.post('/api/allocation-review-apply',{**b,'expected':p['expected']})
