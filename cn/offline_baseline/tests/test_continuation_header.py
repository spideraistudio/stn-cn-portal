"""Ledger: name : period Page N is a continuation, not another party."""
import copy,os,unittest
from pathlib import Path
from decimal import Decimal
from collections import Counter,defaultdict
from tally_detailed import get_party,group_pages
from importer import import_pdf,import_pdf_documents,parse_saved_source,compare_import
from settings import initial_settings

class ContinuationHeaderTests(unittest.TestCase):
 def test_explicit_continuation_suffix_removed(self):
  for suffix in [' Page 32','',' Page 100']:
   self.assertEqual(get_party('Issuer\nLedger: Sample Trading, Satara : 1-Apr-26 to 31-Mar-27'+suffix+'\nDate Particulars'),('Sample Trading, Satara',False))
 def test_first_headers_and_distinct_ledgers_keep_boundaries(self):
  self.assertEqual(get_party('Issuer\nLedger: Sample Trading, Satara\nAddress'),('Sample Trading, Satara',True))
  headers=['Ledger: Sample Trading, Satara','Ledger: Sample Trading, Satara : 1-Apr-26 to 31-Mar-27 Page 32','Ledger: Other Trading : 1-Apr-26 to 31-Mar-27 Page 33','Ledger: Sample Trading, Satara']
  pages=[dict(zip(('party','first'),get_party(x))) for x in headers]
  self.assertEqual([len(g) for g in group_pages(pages)],[2,1,1])
 def test_original_group_and_account_continuations_preserved(self):
  for h in ['Group: Dealers Ledger: Sample Trading : 1-Apr-26 to 31-Mar-27 Page 2','Sample Trading Ledger Account : 1-Apr-26 to 31-Mar-27 Page 2']:
   self.assertEqual(get_party(h),('Sample Trading',False))

@unittest.skipUnless(os.environ.get('CN_REGRESSION_PDF'),'Set CN_REGRESSION_PDF to the supplied two-page ledger for local verification.')
class SuppliedLedgerTests(unittest.TestCase):
 def test_whole_pdf_vouchers_stock_money_and_saved_reparse(self):
  data=Path(os.environ['CN_REGRESSION_PDF']).read_bytes();settings=initial_settings();docs=import_pdf_documents(data,settings);self.assertEqual(len(docs),1);r=import_pdf(data,settings)
  self.assertEqual(r['source']['page_numbers'],[1,2]);self.assertEqual(r['opening'],'-552875.00');self.assertEqual(r['closing'],'602385.00');self.assertTrue(r['reconciled'])
  self.assertEqual(Counter(e['kind'] for e in r['entries']),{'sale':6,'return':1,'posted_cn':4,'receipt':1})
  self.assertEqual(sum((Decimal(e['debit']) for e in r['entries']),Decimal(0)),Decimal('2088000'))
  self.assertEqual(sum((Decimal(e['credit']) for e in r['entries']),Decimal(0)),Decimal('932740'))
  self.assertEqual(sum((Decimal(e['credit']) for e in r['entries'] if e['kind']=='posted_cn'),Decimal(0)),Decimal('11900'))
  self.assertEqual(next(e['date'] for e in r['entries'] if e['kind']=='receipt'),'2026-07-13')
  self.assertEqual(sum((Decimal(e['credit']) for e in r['entries'] if e['kind']=='return'),Decimal(0)),Decimal('820840'))
  expected={'32D55':Decimal(1700),'32D12':Decimal(84),'Ranbanka':Decimal(60),'14D88':Decimal(86),'27D27':Decimal(114),'Janki Ratna':Decimal(262),'Mandhata':Decimal(11)}
  for token,net in expected.items():
   q=sum((Decimal(i['qty'])*(1 if e['kind']=='sale' else -1) for e in r['entries'] if e['kind'] in ('sale','return') for i in e['items'] if token in i['name']),Decimal(0));self.assertEqual(q,net,token)
  again=parse_saved_source(r['source'],settings);self.assertEqual(again['entries'],r['entries']);self.assertEqual(len(set(e['id'] for e in r['entries'])),12)
  self.assertFalse(any('balance' in w.lower() or 'Incomplete item' in w for w in r['warnings']))
