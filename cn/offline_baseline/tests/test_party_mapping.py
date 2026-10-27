import unittest,tempfile,copy,json
from pathlib import Path
from test_calculator import example,configured,ROOT,D
from store import Store
from engine import compute
from importer import import_pdf,product_suggestion,compare_import

class PartyLifecycleTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.store=Store(Path(self.tmp.name)/'test.sqlite');s=configured();s['version']=self.store.settings()['version'];self.store.save_settings(s)
 def tearDown(self):self.tmp.cleanup()
 def save_example(self,**overrides):
  r,_=example();r.update(overrides);return self.store.save(r)
 def action(self,r,restore=False):
  p=self.store.party_action(r['id'],restore);return self.store.party_action(r['id'],restore,True,p['expected'])
 def test_delete_party_all_seasons_restore_other_party_unchanged(self):
  a=self.save_example(party='Party A');b=self.save_example(party=' party a ',season='Other season');other=self.save_example(party='Party B');before={r['id']:r for r in self.store.all()};self.action(a)
  for item in (a,b):
   deleted=self.store.get(item['id']);self.assertTrue(deleted['deleted_at']);self.assertEqual(deleted['entries'],item['entries']);self.assertEqual(deleted['allocations'],item['allocations'])
  self.assertEqual(self.store.get(other['id']),before[other['id']]);self.action(a,True)
  self.assertFalse(self.store.get(a['id']).get('deleted_at'));self.assertEqual(self.store.get(b['id'])['entries'],b['entries'])
 def test_delete_requires_current_preview_fingerprint(self):
  r=self.save_example();p=self.store.party_action(r['id']);r['location']='new location';self.store.save(r)
  with self.assertRaisesRegex(ValueError,'changed'):self.store.party_action(r['id'],confirm=True,expected=p['expected'])
  self.assertFalse(self.store.get(r['id']).get('deleted_at'))
 def test_deleted_record_stays_protected_but_fresh_party_allowed(self):
  r=self.save_example();self.action(r)
  with self.assertRaisesRegex(ValueError,'deleted'):self.store.save(r)
  fresh,_=example()
  created=self.store.save(fresh)
  self.assertNotEqual(created['id'],r['id']);self.assertTrue(self.store.get(r['id'])['deleted_at'])
  with self.assertRaisesRegex(ValueError,'deleted'):self.store.finalise(r['id'],self.store.get(r['id'])['revision'])
 def test_deleting_issued_party_keeps_snapshot_and_duplicate_controls(self):
  r=self.save_example();f=self.store.finalise(r['id'],r['revision']);issued=self.store.issue(f['id'],f['revision']);snapshot=copy.deepcopy(issued['result']);ledger=self.store.backup()['issued'];self.action(issued)
  archived=self.store.get(issued['id']);self.assertEqual(archived['result'],snapshot);self.assertEqual(archived['frozen_settings'],issued['frozen_settings']);self.assertEqual(self.store.backup()['issued'],ledger)
  with self.assertRaisesRegex(ValueError,'deleted'):self.store.revise(issued['id'])
  fresh=self.save_example();f=self.store.finalise(fresh['id'],fresh['revision'])
  with self.assertRaisesRegex(ValueError,'Duplicate'):self.store.issue(f['id'],f['revision'])
 def test_deleted_scheme_hidden_metadata_restore_and_frozen_result(self):
  r=self.save_example();f=self.store.finalise(r['id'],r['revision']);before=f['result'];s=self.store.settings();s=self.store.scheme_action('scheme-3',s['version']);self.assertTrue(next(x for x in s['schemes'] if x['id']=='scheme-3')['deleted_at'])
  trial,_=example();o=self.store.calculate(trial);self.assertTrue(any('scheme is deleted' in i for i in o['issues']));self.assertEqual(self.store.get(f['id'])['result'],before);self.assertEqual(self.store.calculate(self.store.get(f['id'])),before)
  s=self.store.scheme_action('scheme-3',s['version'],True);self.assertEqual(self.store.calculate(trial)['issues'],[])
 def test_scheme_stale_delete_and_hard_removal_rejected(self):
  s=self.store.settings();self.store.save_settings(s)
  with self.assertRaisesRegex(ValueError,'changed'):self.store.scheme_action('scheme-3',s['version'])
  s=self.store.settings();s['schemes']=[x for x in s['schemes'] if x['id']!='scheme-3']
  with self.assertRaisesRegex(ValueError,'Delete Scheme'):self.store.save_settings(s)
 def test_backup_restore_retains_deletion_state(self):
  r=self.save_example();self.action(r);s=self.store.settings();self.store.scheme_action('scheme-3',s['version']);backup=self.store.backup();new=Store(Path(self.tmp.name)/'restore.sqlite');new.restore(backup,True)
  self.assertTrue(new.get(r['id']).get('deleted_at'));self.assertTrue(next(x for x in new.settings()['schemes'] if x['id']=='scheme-3').get('deleted_at'));p=new.party_action(r['id'],True);new.party_action(r['id'],True,True,p['expected']);self.assertFalse(new.get(r['id']).get('deleted_at'))

class ImportSuggestionTests(unittest.TestCase):
 def test_unique_packing_suggestion_and_ambiguous_dawat(self):
  s=configured();one=product_suggestion('DAWAT 1 kg',s);three=product_suggestion('DAWAT 3 kg',s);self.assertNotEqual(one['product'],three['product']);self.assertEqual(one['packing_kg'],'1');self.assertEqual(three['packing_kg'],'3');self.assertIsNone(product_suggestion('DAWAT',s)['product']);self.assertEqual(len(product_suggestion('DAWAT',s)['candidates']),2)
 def test_wrong_packing_unknown_and_alias(self):
  s=configured();self.assertIsNone(product_suggestion('DAWAT 2 kg',s)['product']);self.assertIsNone(product_suggestion('UNKNOWN',s)['product']);s['products'][0]['aliases']=['Friendly Name'];x=product_suggestion('Friendly Name 475 gm',s);self.assertEqual(x['product'],s['products'][0]['id']);self.assertEqual(x['detected_packing_kg'],'0.475')
 def test_import_suggestions_leave_source_money_dates_and_review_pending(self):
  data=import_pdf((ROOT/'fixtures/ashapura.pdf').read_bytes(),configured());items=[i for e in data['entries'] for i in e.get('items',[])];self.assertTrue(items);self.assertTrue(all(i['mapping_confirmed'] is False for i in items));self.assertTrue(all('mapping_suggestion' in i for i in items));self.assertEqual(data['closing'],'2184524.00');self.assertEqual(next(e for e in data['entries'] if e['kind']=='receipt')['date'],'2026-04-08')
 def test_duplicate_import_ignores_changed_catalogue_suggestions(self):
  s=configured();a=import_pdf((ROOT/'fixtures/ashapura.pdf').read_bytes(),s);b=copy.deepcopy(a)
  for e in b['entries']:
   for i in e.get('items',[]):i['product']=None;i['mapping_suggestion']={'reason':'Changed catalogue'};i['mapping_confirmed']=True
   e['original']=copy.deepcopy({k:v for k,v in e.items() if k!='original'})
  self.assertTrue(all(x['status']=='Already imported' for x in compare_import(a['entries'],b['entries'])))
  b['entries'][0]['original']['debit']='1';self.assertEqual(compare_import(a['entries'],b['entries'])[0]['status'],'Changed')
 def test_confirm_mapping_is_not_a_physical_source_correction(self):
  r,s=example();item=r['entries'][0]['items'][0];item['mapping_confirmed']=False;r['entries'][0]['original']=copy.deepcopy(r['entries'][0]);o=compute(r,s);self.assertFalse(any('Confirm suggested' in i for i in o['issues']));item['mapping_confirmed']=True;item['mapping_reason']='Checked';o=compute(r,s);self.assertFalse(any('Source correction' in i or 'Confirm suggested' in i for i in o['issues']))
  item['qty']='401';self.assertTrue(any('Source correction' in i for i in compute(r,s)['issues']))
