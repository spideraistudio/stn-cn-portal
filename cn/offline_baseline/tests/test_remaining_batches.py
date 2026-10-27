import unittest,tempfile,copy,json
from pathlib import Path
from test_calculator import example,configured,D
from store import Store
from workbooks import Workbooks
from importer import product_suggestion
from engine import compute,validate_input_limits
from year_link import match_years,analyse_pair,attach_link,validate_link_sources,traced_credit_conflict
from ledger_audit import audit_documents


def pair():
 previous={'party':'P','location':'Town','opening':'0','closing':'-4000','entries':[{'id':'old-r','date':'2026-01-15','kind':'receipt','reference':'NEFT1','debit':'0','credit':'10000','items':[]},{'id':'old-s','date':'2026-02-15','kind':'sale','reference':'Feb other crop','debit':'6000','credit':'0','items':[{'name':'Other crop','qty':'60','unit':'kg','rate':'100','amount':'6000'}]}],'source':{'sha256':'previous','text':'For 01-Apr-25 to 31-Mar-26'},'warnings':[]}
 r,s=example(sup='100',ret='0',abs_amount='0');r['entries']=[e for e in r['entries'] if e['kind']!='receipt'];r.update(status='draft',party='P',location='Town',opening='-4000',closing=str(sum((D(e['debit'])-D(e['credit']) for e in r['entries']),D(-4000))),allocations=[],source={'sha256':'current','text':'For 01-Apr-26 to 15-Oct-26'},warnings=[])
 return previous,r,s

class RemainingBatchesTests(unittest.TestCase):
 def setUp(self):self.tmp=tempfile.TemporaryDirectory();self.store=Store(Path(self.tmp.name)/'calculator.sqlite3');self.books=Workbooks(self.store)
 def tearDown(self):self.tmp.cleanup()
 def create(self):return self.books.create({'name':'Workbook','state':'Gujarat','period':'2026 season 1','start':'2026-04-01','end':'2026-08-31','cutoff':'2026-10-13'})
 def test_workbook_delete_restore_backup_and_stale_guard(self):
  w=self.create();preview=self.books.delete(w['id']);cfg=self.books.get(w['id']).settings();cfg['schemes'][0]['name']='Changed';self.books.get(w['id']).save_settings(cfg)
  with self.assertRaisesRegex(ValueError,'changed'):self.books.delete(w['id'],confirm=True,expected=preview['expected'])
  preview=self.books.delete(w['id']);self.books.delete(w['id'],confirm=True,expected=preview['expected']);self.assertFalse(self.books.list());self.assertEqual(len(self.books.list(True)),1)
  with self.assertRaisesRegex(ValueError,'deleted'):self.books.get(w['id'])
  backup=self.books.backup();self.assertTrue(backup['workbooks'][0]['metadata']['deleted_at']);self.books.restore(backup,True);preview=self.books.delete(w['id'],True);self.books.delete(w['id'],True,True,preview['expected']);self.assertEqual(len(self.books.list()),1);self.assertTrue(list((Path(self.tmp.name)/'workbook-safety').glob('*.json')))
 def test_product_archive_keeps_identity_and_import_suggestion_excludes_it(self):
  cfg=self.store.settings();p=cfg['products'][0];before=copy.deepcopy(p);saved=self.store.product_action(p['id'],cfg['version']);self.assertEqual(saved['products'][0]['id'],before['id']);self.assertIsNone(product_suggestion(before['name'],saved)['product']);self.assertTrue(saved['products'][0]['deleted_at']);restored=self.store.product_action(p['id'],saved['version'],True);self.assertFalse(restored['products'][0].get('deleted_at'))
 def test_deleting_all_schemes_does_not_remove_engine_rules(self):
  r,cfg=example();self.store.save_settings(cfg)
  for sc in list(self.store.settings()['schemes']):self.store.scheme_action(sc['id'],self.store.settings()['version'])
  self.assertTrue(compute(r,self.store.settings())['issues']);cfg=self.store.settings()
  for sc in cfg['schemes']:sc.pop('deleted_at',None)
  self.store.save_settings(cfg);self.assertEqual(compute(r,self.store.settings())['new_CN_total'],D(38561))
 def test_crop_mapping_is_workbook_scoped_and_backup_preserved(self):
  w=self.create();st=self.books.get(w['id']);cfg=st.settings();cfg['audit_crop_mappings']={'CN GIVEN SPECIAL BENEFIT':'Cotton'};st.save_settings(cfg);doc={'party':'P','entries':[{'id':'cn','kind':'posted_cn','date':'2026-05-01','debit':'0','credit':'100','source_lines':[{'text':'voucher'},{'text':'CN GIVEN SPECIAL BENEFIT'}]}]};r=audit_documents([doc],'2026-04-01','2026-08-31',st.settings());self.assertEqual(r['posted_CNs'][0]['crop'],'Cotton');self.assertNotIn('audit_crop_mappings',self.store.settings());self.books.restore(self.books.backup(),True);self.assertEqual(self.books.get(w['id']).settings()['audit_crop_mappings'],cfg['audit_crop_mappings'])
 def test_crossyear_matches_order_independent_ambiguous_no_guess(self):
  a,b,_=pair();other=copy.deepcopy(a);other['party']='Other';current_other=copy.deepcopy(b);current_other['party']='Other';r=match_years([other,a],[b,current_other]);self.assertEqual([m['previous_index'] for m in r['matches']],[1,0]);r=match_years([a,a],[b]);self.assertIsNone(r['matches'][0]['previous_index'])
 def test_reconciliation_and_adjacent_financial_years_required(self):
  a,b,_=pair();r=analyse_pair(a,b);self.assertEqual(r['maximum_opening_credit'],D(4000));self.assertEqual(len(r['jan_march_activity']),2)
  bad=copy.deepcopy(b);bad['opening']='-3999';bad['closing']=str(D(bad['closing'])+1)
  with self.assertRaisesRegex(ValueError,'closing does not match'):analyse_pair(a,bad)
  bad=copy.deepcopy(a);bad['source']['text']='For 01-Jan-25 to 31-Dec-25'
  with self.assertRaisesRegex(ValueError,'full April'):analyse_pair(bad,b)
  bad=copy.deepcopy(b);bad['location']='Different'
  with self.assertRaisesRegex(ValueError,'reason'):analyse_pair(a,bad)
  self.assertEqual(analyse_pair(a,bad,'Same firm confirmed')['maximum_opening_credit'],D(4000))
 def test_only_confirmed_unspent_carry_is_registered_and_never_second_receipt(self):
  a,b,s=pair();before=copy.deepcopy(b['entries']);linked=attach_link(b,a,b,{'old-r':'4000'},'Jan receipt less Feb purchases, remainder confirmed');self.assertEqual(linked['entries'],before);self.assertEqual(linked['opening_sources'][0]['date'],'2026-01-15');self.assertEqual(linked['opening_sources'][0]['amount'],'4000');self.assertEqual(len(linked['opening_sources']),1);validate_link_sources(linked)
  linked['allocations']=[{'id':'a','source':linked['opening_sources'][0]['id'],'type':'ABS','scheme':'scheme-3','product':s['schemes'][2]['products'][0],'amount':'4000'}];o=compute(linked,s);self.assertFalse(any('outside approved' in x for x in o['issues']));self.assertEqual(o['mismatch'],0);self.assertEqual(o['ledger_closing'],D(b['closing']))
 def test_caps_original_date_tampering_and_existing_sources(self):
  a,b,s=pair()
  with self.assertRaisesRegex(ValueError,'opening credit'):attach_link(b,a,b,{'old-r':'5000'},'Review')
  with self.assertRaisesRegex(ValueError,'original receipt'):attach_link(b,a,b,{'old-r':'10001'},'Review')
  b['opening_sources']=[{'id':'generic','amount':'4000','date':None}]
  with self.assertRaisesRegex(ValueError,'opening credit'):attach_link(b,a,b,{'old-r':'4000'},'Review')
  linked=attach_link(b,a,b,{'old-r':'4000'},'Review',replace_unused=True);linked['opening_sources'][0]['date']='2026-03-01'
  with self.assertRaisesRegex(ValueError,'date changed'):validate_input_limits(linked,s)
 def test_traced_receipt_issue_reservation_across_lineages_and_revisions(self):
  a,b,s=pair();linked=attach_link(b,a,b,{'old-r':'4000'},'Review');linked.update(id='new',lineage='new');linked['allocations']=[{'id':'a','source':linked['opening_sources'][0]['id'],'amount':'2000','type':'ABS'}];old=copy.deepcopy(linked);old.update(id='old',lineage='old',status='issued');self.assertFalse(traced_credit_conflict(linked,[old]));linked['allocations'][0]['amount']='2001';self.assertTrue(traced_credit_conflict(linked,[old]));linked.update(lineage='old');self.assertFalse(traced_credit_conflict(linked,[old]))
 def test_prior_proof_date_and_amount_changes_are_detected(self):
  a,b,s=pair();linked=attach_link(b,a,b,{'old-r':'4000'},'Review');linked['prior_year_link']['previous_document']['entries'][0]['date']='2026-02-15';linked['opening_sources'][0]['date']='2026-02-15'
  with self.assertRaisesRegex(ValueError,'proof/opening changed'):validate_input_limits(linked,s)
  bad=copy.deepcopy(b);bad['entries'][0]['date']='2026-01-01'
  with self.assertRaisesRegex(ValueError,'outside its reported'):analyse_pair(a,bad)
 def test_link_backup_reopen_and_allocated_source_change_rejected(self):
  a,b,s=pair();self.store.save_settings(s);saved=self.store.save(attach_link(b,a,b,{'old-r':'2000'},'Review'));new=Store(Path(self.tmp.name)/'restored.sqlite3');new.restore(self.store.backup(),True);self.assertEqual(new.get(saved['id'])['prior_year_link'],json.loads(json.dumps(saved['prior_year_link'],default=str)));saved['allocations']=[{'id':'a','source':saved['opening_sources'][0]['id'],'type':'Settlement','amount':'1000','scheme':'scheme-3','remark':'Review'}]
  with self.assertRaisesRegex(ValueError,'allocations'):attach_link(saved,a,b,{'old-r':'1000'},'Changed')
