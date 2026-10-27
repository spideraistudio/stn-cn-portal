import unittest,copy,urllib.error
import test_http as shared
from test_calculator import example

class ReportingHTTPTests(unittest.TestCase):
 setUpClass=classmethod(shared.LocalHTTPTests.setUpClass.__func__)
 tearDownClass=classmethod(shared.LocalHTTPTests.tearDownClass.__func__)
 get=classmethod(shared.LocalHTTPTests.get.__func__)
 post=shared.LocalHTTPTests.post
 def test_csv_routes_frozen_snapshot_filters_and_no_writes(self):
  r,s=example();self.post('/api/settings',s);saved=self.post('/api/save',r)
  draft=self.post('/api/product-csv',{'record':saved});self.assertTrue(draft['csv'].startswith('\ufeff'));self.assertGreater(draft['rows'],0)
  frozen=self.post('/api/finalise',{'id':saved['id'],'revision':saved['revision']});before=self.get('/api/state')['records']
  tampered=copy.deepcopy(frozen);tampered['result']['product_CNs'][0]['total_CN']='999999999';exported=self.post('/api/product-csv',{'record':tampered})
  self.assertEqual(draft['csv'].replace(',draft,',',finalised,'),exported['csv']);rows=self.post('/api/report',{'filters':{}});self.assertEqual(rows['summary']['products'],draft['rows'])
  csv=self.post('/api/report',{'filters':{'party':r['party']},'csv':True});self.assertEqual(csv['rows'],draft['rows']);self.assertIn('NRV_per_packet',csv['csv'])
  self.assertEqual(self.post('/api/report',{'filters':{'party':'NO SUCH PARTY'}})['rows'],[]);self.assertEqual(before,self.get('/api/state')['records'])
  with self.assertRaises(urllib.error.HTTPError):self.post('/api/report',{},token=False)
