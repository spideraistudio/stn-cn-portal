import unittest,urllib.request,urllib.error
import test_http as shared
from test_calculator import example

class TerritoryHTTPTests(unittest.TestCase):
 setUpClass=classmethod(shared.LocalHTTPTests.setUpClass.__func__)
 tearDownClass=classmethod(shared.LocalHTTPTests.tearDownClass.__func__)
 get=classmethod(shared.LocalHTTPTests.get.__func__)
 post=shared.LocalHTTPTests.post
 def test_territory_auth_frozen_source_and_assets(self):
  r,s=example();r['source']={'text':'Group: Sample HQ\nDate Particulars\n'};self.post('/api/settings',s);saved=self.post('/api/save',r);self.post('/api/finalise',{'id':saved['id'],'revision':saved['revision']});before=self.get('/api/state')['records']
  data=self.post('/api/territory-report',{'filters':{'hq':'Sample HQ'}});self.assertTrue(data['hierarchy']);self.assertEqual(data['hierarchy'][0]['hqs'][0]['hq'],'Sample HQ');self.assertEqual(before,self.get('/api/state')['records'])
  with self.assertRaises(urllib.error.HTTPError):self.post('/api/territory-report',{},token=False)
  for path,prefix in [('/fonts/Manrope.ttf',b'\x00\x01\x00\x00'),('/polish.js',b"'use strict';"),('/app.ico',b'\x00\x00\x01\x00')]:
   with urllib.request.urlopen('http://127.0.0.1:18765'+path) as response:self.assertTrue(response.read().startswith(prefix))
