import copy,tempfile,unittest
from pathlib import Path
from ledger_audit import audit_documents,finding_id,save_audit_review
from store import Store
from workbooks import Workbooks
from test_ledger_audit import doc,entry

class AuditReviewTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.st=Store(Path(self.tmp.name)/'db.sqlite3')
  self.docs=[doc([entry('r1','receipt',text='NEFT-ABC123456-PARTY'),entry('r2','receipt',text='NEFT-ABC123456-PARTY')])]
 def tearDown(self):self.tmp.cleanup()
 def report(self,settings=None):return audit_documents(self.docs,'2026-04-01','2026-08-31',settings or self.st.settings())
 def payload(self):
  f=self.report()['findings'][0]
  return dict(finding=f,review_id=f['review_id'],start='2026-04-01',end='2026-08-31',reason='Bank record checked: separate intended postings',version=self.st.settings()['version'])
 def test_review_reopen_and_source_unchanged(self):
  before=copy.deepcopy(self.docs);p=self.payload();s=save_audit_review(self.st,p);f=self.report()['findings'][0]
  self.assertEqual(f['review']['status'],'not_applicable');self.assertEqual(self.docs,before)
  save_audit_review(self.st,{**p,'version':s['version'],'reset':True});self.assertIsNone(self.report()['findings'][0]['review'])
 def test_reason_fingerprint_stale_validation(self):
  p=self.payload()
  for update in ({'reason':''},{'review_id':'wrong'},{'version':-1}):
   with self.assertRaises(ValueError):save_audit_review(self.st,{**p,**update})
 def test_review_bound_to_exact_evidence_and_period_not_filename(self):
  p=self.payload();save_audit_review(self.st,p)
  self.docs[0]['audit_filename']='renamed.pdf';self.assertIsNotNone(self.report()['findings'][0]['review'])
  self.docs[0]['entries'][0]['credit']='101';self.assertIsNone(self.report()['findings'][0]['review'])
  f=p['finding'];self.assertNotEqual(finding_id(f,p['start'],p['end']),finding_id(f,'2026-04-02',p['end']))
 def test_review_survives_backup_restore(self):
  p=self.payload();save_audit_review(self.st,p);other=Store(Path(self.tmp.name)/'restored.sqlite3');other.restore(self.st.backup(),True)
  self.assertEqual(other.settings()['audit_finding_reviews'],self.st.settings()['audit_finding_reviews'])
 def test_workbook_scoping(self):
  books=Workbooks(self.st);w=books.create(dict(name='Review workbook',state='Gujarat',period='Test',start='2026-04-01',end='2026-08-31',cutoff='2026-10-01',mode='blank'),'legacy');p=self.payload();save_audit_review(self.st,p)
  self.assertNotIn(p['review_id'],books.get(w['id']).settings().get('audit_finding_reviews',{}))
 def test_new_workbook_never_copies_review_dispositions(self):
  p=self.payload();save_audit_review(self.st,p);books=Workbooks(self.st);w=books.create(dict(name='Fresh reviews',state='Gujarat',period='Test',start='2026-04-01',end='2026-08-31',cutoff='2026-10-01',mode='copy'),'legacy')
  self.assertNotIn('audit_finding_reviews',books.get(w['id']).settings())
 def test_freight_journal_not_crop_and_generic_journal_not_guessed(self):
  docs=[doc([entry('cn','posted_cn',text='FREIGHT CREDIT COTTON TRANSPORT 123'),entry('other','posted_cn',text='JOURNAL ADJUSTMENT 987')])];r=audit_documents(docs,'2026-04-01','2026-08-31',self.st.settings())
  self.assertEqual(r['posted_CNs'][0]['cn_classification'],'freight');self.assertIn('no crop mapping',r['posted_CNs'][0]['crop']);self.assertEqual(r['posted_CNs'][1]['cn_classification'],'unclassified')
  cfg=self.st.settings();cfg['audit_cn_classifications']={'FREIGHT CREDIT COTTON TRANSPORT 123':'scheme'};cfg['audit_crop_mappings']={'FREIGHT CREDIT COTTON TRANSPORT 123':'Cotton'}
  r=audit_documents(docs,'2026-04-01','2026-08-31',cfg);self.assertEqual(r['posted_CNs'][0]['crop'],'Cotton')
 def test_other_classification_no_crop(self):
  cfg=self.st.settings();cfg['audit_cn_classifications']={'OTHER JOURNAL':'other'}
  r=audit_documents([doc([entry('cn','posted_cn',text='OTHER JOURNAL')])],'2026-04-01','2026-08-31',cfg)
  self.assertEqual(r['posted_CNs'][0]['cn_classification'],'other');self.assertIn('no crop mapping',r['posted_CNs'][0]['crop'])
