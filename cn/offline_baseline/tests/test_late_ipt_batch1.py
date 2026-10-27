import copy,tempfile,unittest
from pathlib import Path
from test_calculator import example,configured,D
from engine import compute,validate_input_limits,late_ipt_issue_conflict
from store import Store
from ledger_audit import audit_documents

class LateIPTTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.store=Store(Path(self.tmp.name)/'late.sqlite3')
  self.r,self.s=example(sup='400',ret='40',abs_amount='0',payments=[])
  # The example factory's empty-list default creates payments; remove them explicitly.
  self.r['entries']=[e for e in self.r['entries'] if e['kind']!='receipt'];self.r['allocations']=[]
  self.r['entries'][0].update(kind='ipt_in',date='2026-09-05',reference='Late transfer')
  self.r.update(annual_ledger=True,closing=str(sum((D(e['debit'])-D(e['credit']) for e in self.r['entries']),D(0))))
  for sc in self.s['schemes']:
   if sc['id']=='scheme-3':sc['benefits']=['Quantity']
  self.s['version']=self.store.settings()['version'];self.store.save_settings(self.s)
 def tearDown(self):self.tmp.cleanup()
 def approve(self):
  record=self.store.save(self.r);return self.store.review_late_ipt(record['id'],record['revision'],'sale','Details received after season; transfer belongs to this season')
 def test_later_within_period_ipt_resolves_return_independent_of_order(self):
  self.r['entries'][0]['date']='2026-08-25';o=compute(self.r,self.s);self.assertFalse(any('Returns without' in x for x in o['issues']));self.assertEqual(o['groups'][0]['net'],D(360))
  self.r['entries'].reverse();again=compute(self.r,self.s);self.assertEqual(again['new_CN_total'],o['new_CN_total'])
 def test_outside_requires_explicit_review_preserves_ledger_dates_and_sources(self):
  before=self.store.save(self.r);initial=self.store.calculate(before);self.assertTrue(any('Returns without' in x for x in initial['issues']))
  reviewed=self.store.review_late_ipt(before['id'],before['revision'],'sale','Late details for this period');o=self.store.calculate(reviewed)
  self.assertFalse(any('Returns without' in x for x in o['issues']));self.assertEqual(o['groups'][0]['ipt_received'],D(400));self.assertEqual(o['groups'][0]['returned'],D(40));self.assertEqual(o['groups'][0]['net'],D(360));self.assertEqual(o['mismatch'],0);self.assertEqual(o['ledger_closing'],initial['ledger_closing']);self.assertEqual(reviewed['entries'],before['entries']);self.assertEqual(o['sources'],[]);self.assertFalse(reviewed['ledger_confirmed']);self.assertTrue(o['stock_scope']['sale'])
  reopened=self.store.get(reviewed['id']);self.assertEqual(reopened['late_ipt_reviews'],reviewed['late_ipt_reviews'])
  removed=self.store.review_late_ipt(reviewed['id'],reviewed['revision'],'sale',remove=True);self.assertTrue(any('Returns without' in x for x in self.store.calculate(removed)['issues']))
 def test_no_automatic_inclusion_or_cutoff_bypass_or_blank_reason(self):
  before=self.store.save(self.r)
  for reason in ('','   '):
   with self.assertRaisesRegex(ValueError,'reason'):self.store.review_late_ipt(before['id'],before['revision'],'sale',reason)
  with self.assertRaisesRegex(ValueError,'only available'):self.store.review_late_ipt(before['id'],before['revision'],'return','Not a transfer')
  self.r['entries'][0]['date']='2026-11-01';record=self.store.save(self.r)
  with self.assertRaisesRegex(ValueError,'cutoff'):self.store.review_late_ipt(record['id'],record['revision'],'sale','Late')
 def test_changed_physical_voucher_or_period_invalidates_review(self):
  reviewed=self.approve();bad=copy.deepcopy(reviewed);bad['entries'][0]['items'][0]['qty']='401';o=self.store.calculate(bad);self.assertTrue(any('voucher changed' in x for x in o['issues']));self.assertFalse(o['stock_scope']['sale'])
  cfg=self.store.settings();cfg['seasons'][0]['end']='2026-08-30';self.store.save_settings(cfg);self.assertTrue(any('different period dates' in x for x in self.store.calculate(reviewed)['issues']))
 def test_frozen_backup_restore_and_cash_limits_use_same_stock_scope(self):
  reviewed=self.approve();reviewed['ledger_confirmed']=True;reviewed=self.store.save(reviewed);f=self.store.finalise(reviewed['id'],reviewed['revision']);self.assertEqual(f['result']['groups'][0]['net'],'360');before=copy.deepcopy(f);new=Store(Path(self.tmp.name)/'restore.sqlite3');new.restore(self.store.backup(),True);self.assertEqual(new.get(f['id']),before)
  with self.assertRaisesRegex(ValueError,'active draft'):self.store.review_late_ipt(f['id'],f['revision'],'sale',remove=True)
 def test_stale_write_refused(self):
  record=self.store.save(self.r);saved=self.store.save(record)
  with self.assertRaisesRegex(ValueError,'changed'):self.store.review_late_ipt(record['id'],record['revision'],'sale','Late')
 def test_cross_period_issue_of_same_late_transfer_blocked_even_if_old_party_deleted(self):
  reviewed=self.approve();reviewed['ledger_confirmed']=True;reviewed=self.store.save(reviewed);f=self.store.finalise(reviewed['id'],reviewed['revision']);old=self.store.issue(f['id'],f['revision']);preview=self.store.party_action(old['id']);self.store.party_action(old['id'],confirm=True,expected=preview['expected'])
  cfg=self.store.settings();cfg['seasons'].append({'name':'next','start':'2026-09-01','end':'2026-11-30','cutoff':'2026-12-31','confirmed':True})
  for sc in cfg['schemes']:sc['season']='next'
  self.store.save_settings(cfg);next_record=copy.deepcopy(self.r);next_record['season']='next';next_record['ledger_confirmed']=True;next_record=self.store.save(next_record);next_f=self.store.finalise(next_record['id'],next_record['revision']);self.assertTrue(late_ipt_issue_conflict(next_f,old))
  with self.assertRaisesRegex(ValueError,'IPT is already included'):self.store.issue(next_f['id'],next_f['revision'])
 def test_audit_later_ipt_covers_earlier_return_without_becoming_invoice_rate(self):
  entries=copy.deepcopy(self.r['entries']);entries[0]['date']='2026-08-25';doc={'party':'Late party','entries':entries};report=audit_documents([doc],'2026-04-01','2026-08-31');self.assertEqual(report['findings'],[]);self.assertTrue(report['stock_timing']);entries[0]['items'][0]['qty']='20';report=audit_documents([doc],'2026-04-01','2026-08-31');self.assertTrue(any(f['type']=='Return supply needs review' for f in report['findings']))
 def test_border_party_uses_workbook_state_without_changing_address(self):
  r,s=example(abs_amount='0');r['state']='Madhya Pradesh';r['workbook_scheme_state']='Gujarat';o=compute(r,s);self.assertFalse(any('No explicit state' in x or 'State override requires' in x for x in o['issues']));self.assertEqual(r['state'],'Madhya Pradesh');self.assertTrue(any('differs from workbook' in x for x in o['information']));r['scheme_state']='Rajasthan';self.assertTrue(any('State override requires' in x for x in compute(r,s)['issues']))
