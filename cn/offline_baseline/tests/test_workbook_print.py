import copy,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
from store import Store
from workbook_print import workbook_print
from test_calculator import example,D

class WorkbookPrintTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.st=Store(Path(self.tmp.name)/'book.sqlite3');r,s=example();self.st.save_settings(s);r['party']='Print party';self.r=self.st.save(r);self.meta={'id':'legacy','name':'Print workbook'}
 def preview(self):return workbook_print(self.st,self.meta,{})
 def build(self,ids,p=None):return workbook_print(self.st,self.meta,{'record_ids':ids,'expected':(p or self.preview())['expected']})
 def test_snapshot_reports_are_readonly_and_keep_requests_display_only(self):
  before=self.st.backup();before.pop('created_at',None);out=self.build([self.r['id']]);after=self.st.backup();after.pop('created_at',None);self.assertEqual(after,before);self.assertEqual(out['items'][0]['record'],self.r);self.assertEqual(out['items'][0]['result']['new_CN_total'],self.st.calculate(self.r)['new_CN_total'])
 def test_one_version_per_party_period_frozen_never_recomputed(self):
  f=self.st.finalise(self.r['id'],self.r['revision']);rev=self.st.revise(f['id']);p=self.preview();self.assertEqual(len(p['groups']),1);self.assertEqual(len(p['groups'][0]['versions']),2);self.assertEqual(p['groups'][0]['selected_id'],rev['id'])
  with self.assertRaisesRegex(ValueError,'one version'):self.build([f['id'],rev['id']],p)
  with patch('workbook_print.compute',side_effect=AssertionError('Frozen result recomputed')):out=self.build([f['id']],p)
  self.assertEqual(out['items'][0]['result'],f['result'])
 def test_deleted_scope_and_empty_duplicate_ids_rejected(self):
  for ids in [[],[self.r['id'],self.r['id']],['other-book-record']]:
   with self.assertRaises(ValueError):self.build(ids)
  p=self.st.party_action(self.r['id']);self.st.party_action(self.r['id'],confirm=True,expected=p['expected']);self.assertEqual(self.preview()['groups'],[])
 def test_snapshot_change_rejected(self):
  p=self.preview();r=copy.deepcopy(self.r);r['party']='Changed';self.st.save(r)
  with self.assertRaisesRegex(ValueError,'Workbook changed'):self.build([r['id']],p)
 def test_latest_empty_draft_does_not_hide_ledger(self):
  empty=copy.deepcopy(self.r);empty.pop('id');empty['entries']=[];empty.pop('source',None);empty['allocations']=[];empty['opening_sources']=[];empty['closing']=empty['opening'];self.st.save(empty)
  self.assertEqual(self.preview()['groups'][0]['selected_id'],self.r['id'])
 def test_missing_frozen_result_reported_not_zero(self):
  # Model an old/damaged completed snapshot without recalculating its history.
  f=self.st.finalise(self.r['id'],self.r['revision'])
  from store import dump
  f.pop('result')
  with self.st.db() as c:c.execute('UPDATE records SET data=? WHERE id=?',(dump(f),f['id']))
  out=self.build([f['id']]);self.assertIn('error',out['items'][0]);self.assertNotIn('result',out['items'][0])
