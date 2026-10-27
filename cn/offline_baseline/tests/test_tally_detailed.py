import base64,copy,tempfile,unittest
from unittest.mock import patch
from collections import Counter
from pathlib import Path
from test_calculator import ROOT,configured,D
from importer import import_pdf,import_pdf_documents,compare_import,parse_saved_source
from workbooks import Workbooks,bulk_history
from store import Store
from engine import compute

class DetailedTallyTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.settings=configured();cls.raw=(ROOT/'fixtures/surendranagar_combined.pdf').read_bytes();cls.docs=import_pdf_documents(cls.raw,cls.settings);cls.by_party={d['party']:d for d in cls.docs}
 def doc(self,prefix):return next(d for d in self.docs if d['party'].startswith(prefix))
 def cotton(self,doc):
  q={kind:sum((D(i['qty']) for e in doc['entries'] if e['kind']==kind for i in e['items'] if i['name'].startswith('Cotton')),D(0)) for kind in ('sale','return','ipt_in','ipt_out')}
  return q['sale'],q['ipt_in'],q['ipt_out'],q['sale']+q['ipt_in']-q['ipt_out'],q['return'],q['sale']+q['ipt_in']-q['ipt_out']-q['return']
 def test_all_parties_pages_and_footer_totals_reconcile(self):
  self.assertEqual(len(self.docs),49);self.assertEqual(len(self.by_party),49);self.assertFalse(any(d.get('import_error') for d in self.docs));self.assertEqual(sum(len(d['entries']) for d in self.docs),329);self.assertEqual(sum(len(e['items']) for d in self.docs for e in d['entries']),341)
  for d in self.docs:
   self.assertTrue(d['reconciled'],d['party']);self.assertFalse(any(not w.startswith('Map product/packing:') for w in d['warnings']),(d['party'],d['warnings']));self.assertEqual(len({e['id'] for e in d['entries']}),len(d['entries']))
  self.assertEqual(sorted(n for d in self.docs for n in d['source']['page_numbers']),list(range(1,70)))
  self.assertEqual(len({d['source']['sha256'] for d in self.docs}),49);self.assertEqual(len({d['source']['file_sha256'] for d in self.docs}),1)
  for d in self.docs:self.assertTrue(all(p['party']==d['party'] for p in d['source']['structured_pages']))
 def test_actual_balances_credits_zero_and_inactive_parties(self):
  expected={'Ashapura Seeds, Chuda':('89909','1591149'),'Krishna Trading':('171898','1683058'),'Umiya Seeds':('-215700','18280'),'Chandrakant Dodiya':('222299','0'),'Giriraj Seeds':('-1579400','-645172.22'),'Ganesh Seeds':('-75001','-3191.89')}
  for prefix,(opening,closing) in expected.items():d=self.doc(prefix);self.assertEqual(D(d['opening']),D(opening));self.assertEqual(D(d['closing']),D(closing))
  d=self.doc('Shree Shakti Sale Agency');self.assertEqual(d['entries'],[]);self.assertEqual(D(d['opening']),D(23475));self.assertEqual(D(d['closing']),D(23475))
  for d in self.docs:
   if d['source']['opening_omitted_zero']:self.assertEqual(D(d['opening']),D(0))
 def test_repeated_dates_wrapped_ipt_and_no_supply_double_count(self):
  a=self.doc('Ashapura');k=self.doc('Krishna Trading');self.assertEqual(self.cotton(a),tuple(D(x) for x in (4650,0,125,4525,2110,2415)));self.assertEqual(self.cotton(k),tuple(D(x) for x in (3250,175,10,3415,1505,1910)))
  e=next(e for e in a['entries'] if e['reference']=='GJ/SRN/26-27/0259');self.assertTrue(e['date_inherited']);self.assertEqual(e['date'],'2026-08-14');self.assertEqual(e['kind'],'return');ipt=next(e for e in a['entries'] if e['kind']=='ipt_out');self.assertEqual(ipt['transfer_party'],'KRISHNA TRADING CO, WADHVAN')
  self.assertEqual(sum(1 for d in self.docs for e in d['entries'] if e['kind'].startswith('ipt_')),16)
 def test_receipts_once_not_bill_references_cheques_or_carry_totals(self):
  a=self.doc('Ashapura');payments=[e for e in a['entries'] if e['kind']=='receipt'];self.assertEqual(len(payments),1);self.assertEqual(D(payments[0]['credit']),D(200000));self.assertEqual(payments[0]['date'],'2026-04-08')
  agri=self.doc('Agri Business');payments=[e for e in agri['entries'] if e['kind']=='receipt'];self.assertEqual(len(payments),4);self.assertEqual(sum(D(e['credit']) for e in payments),D(200000))
  self.assertTrue(all(e['reference'] not in ('Carried','Forward') for d in self.docs for e in d['entries']))
  journal=next(e for e in self.doc('Chandrakant')['entries'] if e['voucher_family']=='Journal');self.assertEqual(journal['kind'],'posted_cn');self.assertEqual(D(journal['credit']),D(17299))
 def test_engine_keeps_each_full_ledger_and_original_dates(self):
  for d in self.docs:
   r={**copy.deepcopy(d),'state':d['state'] or 'Gujarat','season':'2026 season 1','annual_ledger':True,'old_dues':'0','allocations':[],'opening_sources':[],'cash_splits':[],'ledger_confirmed':False};out=compute(r,self.settings);self.assertEqual(out['ledger_computed'],D(d['closing']),d['party']);self.assertEqual(len(out['sources']),sum(e['kind']=='receipt' for e in d['entries']))
   for src in out['sources']:self.assertEqual(src['date'],next(e['original']['date'] for e in d['entries'] if e['id']==src['id']))
 def test_cross_version_duplicate_comparison_numeric_format_and_day_order(self):
  old=import_pdf((ROOT/'fixtures/krishna_ipt.pdf').read_bytes(),self.settings);new=self.doc('Krishna Trading');self.assertTrue(all(c['status']=='Already imported' for c in compare_import(old['entries'],new['entries'])))
  old=import_pdf((ROOT/'fixtures/ashapura_ipt.pdf').read_bytes(),self.settings);new=self.doc('Ashapura');counts=Counter(c['status'] for c in compare_import(old['entries'],new['entries']));self.assertEqual(counts,{'Already imported':13,'New':2})
  changed=copy.deepcopy(new['entries']);changed[0]['original']['credit']='199999';self.assertEqual(compare_import(new['entries'],changed)[0]['status'],'Changed')
 def test_saved_structured_source_reread_is_idempotent(self):
  for d in self.docs:
   reread=parse_saved_source(d['source'],self.settings);self.assertEqual(reread['source'],d['source']);self.assertEqual(reread['opening'],d['opening']);self.assertEqual(reread['closing'],d['closing']);self.assertTrue(all(c['status']=='Already imported' for c in compare_import(d['entries'],reread['entries'])))
 def test_missing_items_wrong_column_and_broken_carry_are_not_silent(self):
  d=self.doc('Ashapura');pages=copy.deepcopy(d['source']['structured_pages']);page=pages[0];row=next(r for r in page['rows'] if 'GJ/26-27/0052' in r['text'] and r['text'].startswith('21-Apr'))
  row['right']=400
  from tally_detailed import parse_ledger
  with self.assertRaisesRegex(ValueError,'Ambiguous debit/credit'):parse_ledger(pages,self.settings)
  pages=copy.deepcopy(d['source']['structured_pages']);row=next(r for p in pages for r in p['rows'] if r['text'].startswith('Brought Forward'));row['text']='Brought Forward 1.00 2.00';parsed=parse_ledger(pages,self.settings);self.assertTrue(any('carry totals' in w for w in parsed['warnings']))
 def test_bulk_combined_pdf_creates_49_then_skips_same_file(self):
  with tempfile.TemporaryDirectory() as td:
   books=Workbooks(Store(Path(td)/'calculator.sqlite3'));meta=books.create({'name':'Surendranagar','state':'Gujarat','period':'2026 season 1','start':'2026-04-01','end':'2026-08-31','cutoff':'2026-10-15'});b={'filename':'Surendranagar.pdf','season':'2026 season 1','data':base64.b64encode(self.raw).decode()};first=books.bulk_import(meta['id'],b);self.assertEqual(first['ledger_count'],49);self.assertTrue(all(r['status']=='Imported' for r in first['results']));self.assertEqual(len(books.get(meta['id']).all()),49);self.assertEqual(len(bulk_history(books.get(meta['id']))),49)
   second=books.bulk_import(meta['id'],b);self.assertTrue(all(r['status']=='Already imported' for r in second['results']));self.assertEqual(len(books.get(meta['id']).all()),49)
 def test_single_party_compatibility_and_clear_combined_single_import_message(self):
  # Single-document PDF API retains its original contract; mixed files use the batch API.
  with self.assertRaisesRegex(ValueError,'49 party ledgers'):import_pdf(self.raw,self.settings)
 def test_one_failed_ledger_does_not_stop_other_parties(self):
  with tempfile.TemporaryDirectory() as td:
   books=Workbooks(Store(Path(td)/'calculator.sqlite3'));id=books.create({'name':'Partial import','state':'Gujarat','period':'2026 season 1','start':'2026-04-01','end':'2026-08-31','cutoff':'2026-10-15'})['id']
   documents=[self.doc('Ashapura'),{'party':'Unreadable ledger','import_error':'Ambiguous amount column'},self.doc('Krishna Trading')]
   with patch('workbooks.import_pdf_documents',return_value=documents):out=books.bulk_import(id,{'filename':'Mixed.pdf','season':'2026 season 1','data':base64.b64encode(b'mixed source').decode()})
   self.assertEqual([x['status'] for x in out['results']],['Imported','Failed','Imported']);self.assertEqual(len(books.get(id).all()),2);self.assertEqual(len(bulk_history(books.get(id))),3)
