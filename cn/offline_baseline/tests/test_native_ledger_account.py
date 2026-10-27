import copy,tempfile,unittest
from pathlib import Path
from collections import Counter
from decimal import Decimal
from importer import import_pdf_documents,parse_saved_source,compare_import
from settings import initial_settings
from year_link import analyse_pair,match_years,attach_link
from store import Store
from workbooks import Workbooks

ROOT=Path(__file__).resolve().parents[1]
D=Decimal
class NativeLedgerAccountTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.settings=initial_settings();cls.previous=import_pdf_documents((ROOT/'fixtures/khammam_previous_fy.pdf').read_bytes(),cls.settings)[0];cls.current=import_pdf_documents((ROOT/'fixtures/khammam_current_fy.pdf').read_bytes(),cls.settings)[0]
 def test_actual_party_location_state_and_period(self):
  for doc in (self.previous,self.current):
   self.assertEqual(doc['party'],'Sri Lakshmi Ganapathi Traders, Khammam');self.assertEqual(doc['location'],'Khammam');self.assertEqual(doc['state'],'Telangana');self.assertTrue(doc['reconciled']);self.assertEqual(doc['source']['format'],'tally-detailed-ledger');self.assertFalse([w for w in doc['warnings'] if not w.startswith('Map product/packing')])
  self.assertEqual((self.previous['source']['report_start'],self.previous['source']['report_end']),('2025-04-01','2026-03-31'));self.assertEqual((self.current['source']['report_start'],self.current['source']['report_end']),('2026-04-01','2026-10-15'))
 def test_previous_zero_opening_carried_pages_money_and_stock(self):
  p=self.previous;self.assertEqual(D(p['opening']),0);self.assertTrue(p['source']['opening_omitted_zero']);self.assertEqual(D(p['closing']),D('269180'));self.assertEqual(len(p['entries']),22);self.assertEqual(sum(len(e['items']) for e in p['entries']),15);self.assertEqual(Counter(e['kind'] for e in p['entries']),{'receipt':7,'sale':6,'return':2,'posted_cn':6,'ipt_in':1});self.assertEqual([x['first'] for x in p['source']['structured_pages']],[True,False,False]);self.assertEqual(sum(D(e['credit']) for e in p['entries'] if e['kind']=='receipt'),D('275000'))
  transfer=next(e for e in p['entries'] if e['kind']=='ipt_in');self.assertEqual(transfer['date'],'2026-01-30');self.assertEqual(transfer['items'][0]['qty'],'70.000');self.assertIn('VISHNU SEEDS',transfer['transfer_party']);self.assertIn('MEDRU',transfer['transfer_party']);self.assertEqual(len([e for e in p['entries'] if e['reference']=='DCSL/2025-26/803']),1)
 def test_original_date_inheritance_not_cheque_or_reference_date(self):
  invoice=next(e for e in self.previous['entries'] if e['reference']=='DCSL/2025-26/734');self.assertEqual(invoice['date'],'2025-12-02');self.assertTrue(invoice['date_inherited']);receipt=next(e for e in self.previous['entries'] if e['reference']=='2814');self.assertEqual(receipt['date'],'2025-12-02');self.assertTrue(any('1-12-2025' in l['text'] for l in receipt['source_lines']))
 def test_current_opening_debit_despite_cr_label_and_debit_correction(self):
  c=self.current;self.assertEqual(D(c['opening']),D('269180'));self.assertEqual(D(c['closing']),D('120031'));self.assertEqual(len(c['entries']),5);self.assertEqual(Counter(e['kind'] for e in c['entries']),{'receipt':3,'return':1,'adjustment':1});self.assertEqual(sum(D(e['credit']) for e in c['entries'] if e['kind']=='receipt'),D('130000'));self.assertEqual(sum(D(e['credit']) for e in c['entries'] if e['kind']=='return'),D('44149'))
  correction=next(e for e in c['entries'] if e['reference']=='DCSL/26-27/0156');self.assertEqual(correction['kind'],'adjustment');self.assertEqual(correction['date'],'2026-09-28');self.assertEqual(D(correction['debit']),D('25000'));self.assertTrue(correction['classification_required']);self.assertEqual(correction['items'],[])
 def test_actual_year_pair_links_without_fabricating_advance(self):
  m=match_years([self.previous],[self.current]);self.assertEqual(m['matches'][0]['previous_index'],0);self.assertEqual(m['matches'][0]['status'],'Exact party/location match');r=analyse_pair(self.previous,self.current);self.assertEqual(r['previous_close'],r['current_opening']);self.assertEqual(r['maximum_opening_credit'],0)
  current={**copy.deepcopy(self.current),'status':'draft','opening_sources':[],'allocations':[]};linked=attach_link(current,self.previous,self.current,{},'Actual FY ledgers reconciled; opening is outstanding');self.assertEqual(linked['opening_sources'],[]);self.assertEqual(linked['entries'],self.current['entries'])
  with self.assertRaisesRegex(ValueError,'opening credit'):attach_link(current,self.previous,self.current,{self.previous['entries'][0]['id']:'1'},'Must not turn prior receipts into new money')
 def test_reparse_and_repeat_import_preserve_original_vouchers(self):
  for doc in (self.previous,self.current):
   again=parse_saved_source(doc['source'],self.settings);self.assertEqual(again['entries'],doc['entries']);self.assertTrue(all(c['status']=='Already imported' for c in compare_import(doc['entries'],again['entries'])));self.assertEqual(again['closing'],doc['closing'])
 def test_real_pair_save_link_uses_existing_bulk_import_review_and_backup(self):
  with tempfile.TemporaryDirectory() as td:
   st=Store(Path(td)/'calculator.sqlite3');books=Workbooks(st);w=books.create({'name':'Real historical pair','state':'Telangana','period':'Kharif 2026','start':'2026-04-01','end':'2026-10-15','cutoff':'2026-10-15'})
   record=books.link_year(w['id'],{'previous':self.previous,'current':self.current,'season':'Kharif 2026','confirmed':{},'reason':'Previous closing reconciles with current opening; no opening credit'});self.assertEqual(record['opening_sources'],[]);self.assertEqual(len(record['entries']),5);self.assertEqual(D(record['closing']),D('120031'));sources=copy.deepcopy(record['entries']);books.restore(books.backup(),True);self.assertEqual(books.get(w['id']).get(record['id'])['entries'],sources);self.assertEqual(len(books.get(w['id']).all()),1)
