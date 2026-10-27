import unittest,urllib.error
import test_http as shared
from test_calculator import example
class WorkbookPrintHTTPTests(unittest.TestCase):
 setUpClass=classmethod(shared.LocalHTTPTests.setUpClass.__func__)
 tearDownClass=classmethod(shared.LocalHTTPTests.tearDownClass.__func__)
 get=classmethod(shared.LocalHTTPTests.get.__func__)
 post=shared.LocalHTTPTests.post
 def test_token_workbook_scope_and_readonly(self):
  r,s=example();self.post('/api/settings',s);r=self.post('/api/save',r)
  with self.assertRaises(urllib.error.HTTPError) as e:self.post('/api/workbook-print',{},token=False)
  self.assertEqual(e.exception.code,403)
  p=self.post('/api/workbook-print',{});before=self.get('/api/backup');out=self.post('/api/workbook-print',{'expected':p['expected'],'record_ids':[r['id']]});self.assertEqual(out['items'][0]['record'],r);self.assertEqual(self.get('/api/backup')['legacy']['records'],before['legacy']['records'])
  meta=self.post('/api/workbooks',{'name':'Other print book','state':'Gujarat','period':'2026 season 1','start':'2026-04-01','end':'2026-08-31','cutoff':'2026-10-19'})
  other=self.post('/api/workbook-print',{},workbook=meta['id']);self.assertEqual(other['groups'],[])
  with self.assertRaises(urllib.error.HTTPError):self.post('/api/workbook-print',{'expected':other['expected'],'record_ids':[r['id']]},workbook=meta['id'])
