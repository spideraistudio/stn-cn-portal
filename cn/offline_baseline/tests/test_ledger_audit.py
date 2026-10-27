import unittest, copy, tempfile, base64
from pathlib import Path
from ledger_audit import audit_documents
from importer import import_pdf_documents
from settings import initial_settings


def entry(ref,kind,amount='100',text='',day='2026-05-01',items=None):
 return {'id':ref,'reference':ref,'date':day,'kind':kind,'debit':amount if kind=='sale' else '0','credit':amount if kind!='sale' else '0','items':items or [],'source_lines':[{'page':1,'line':1,'text':ref},{'page':1,'line':2,'text':text}]}
def doc(entries,party='Party A'):
 return {'party':party,'entries':entries,'warnings':[]}
def check(documents):return audit_documents(documents,'2026-04-01','2026-08-31')

class LedgerAuditTests(unittest.TestCase):
 def test_equal_amounts_never_sufficient(self):
  r=check([doc([entry('1','receipt'),entry('2','receipt'),entry('3','posted_cn'),entry('4','posted_cn')])]);self.assertEqual(r['findings'],[]);self.assertEqual(len(r['posted_CNs']),2)
 def test_exact_bank_reference_across_parties_dates_and_different_amounts(self):
  r=check([doc([entry('1','receipt',text='NEFT-BARBL26098828135-AASHAPURA SEEDS--78041976916-BARB0BGGBXX')]),doc([entry('2','receipt','200',text='NEFT-BARBL26098828135-AASHAPURA SEEDS--78041976916-BARB0BGGBXX',day='2026-05-02')],'Party B')]);self.assertEqual(len(r['findings']),1);self.assertEqual(len(r['findings'][0]['vouchers']),2)
 def test_same_amount_distinct_references_not_flagged(self):
  r=check([doc([entry('1','receipt',text='NEFT-ABC123456-PARTY'),entry('2','receipt',text='NEFT-XYZ987654-PARTY')])]);self.assertFalse(r['findings'])
 def test_repeated_import_not_duplicate_but_identical_printed_entries_retained(self):
  a=doc([entry('1','receipt',text='NEFT-ABC123456-PARTY')]);self.assertFalse(check([a,copy.deepcopy(a)])['findings']);a['entries'].append(copy.deepcopy(a['entries'][0]));self.assertEqual(len(check([a,a])['findings']),1)
 def test_cross_layout_precision_and_family_not_false_duplicate(self):
  a=doc([entry('1','receipt',text='NEFT-ABC123456-PARTY')]);b=copy.deepcopy(a);b['entries'][0].update(credit='100.00',voucher_family='Receipt');self.assertFalse(check([a,b])['findings']);self.assertEqual(check([a,b])['voucher_count'],1)
 def test_cn_same_narration_amount_only_and_crop_list(self):
  a=doc([entry('1','posted_cn',text='CN GIVEN COTTON QUANTITY BENEFIT 125 PKTS'),entry('2','posted_cn',text='CN GIVEN COTTON QUANTITY BENEFIT 125 PKTS'),entry('3','posted_cn',text='CN GIVEN MAIZE BENEFIT')]);r=check([a]);self.assertEqual(len(r['findings']),1);self.assertEqual(len(r['posted_CNs']),3)
 def test_period_and_no_mutation(self):
  a=doc([entry('1','receipt',text='NEFT-ABC123456-PARTY'),entry('2','receipt',text='NEFT-ABC123456-PARTY',day='2026-09-01')]);before=copy.deepcopy(a);self.assertFalse(check([a])['findings']);self.assertEqual(a,before)
 def test_invalid_period(self):
  with self.assertRaises(ValueError):audit_documents([],'2026-08-01','2026-04-01')
 def test_rate_excess_and_mixed_rate_uncertainty(self):
  def item(rate,qty='20'):return {'name':'PRODUCT 1 KG','unit':'packet','qty':qty,'rate':rate,'amount':str(int(rate)*int(qty))}
  a=doc([entry('s','sale','10000',items=[item('100','100')]),entry('r','return','2500',day='2026-06-01',items=[item('125')])]);r=check([a]);self.assertEqual(r['findings'][0]['possible_excess_min'],500)
  a['entries'].insert(1,entry('s2','sale','12500',day='2026-05-03',items=[item('125','100')]))
  r=check([a]);self.assertEqual(r['findings'][0]['type'],'Mixed supply rates — review return');self.assertEqual(r['findings'][0]['possible_excess_min'],0)
 def test_ipt_and_separate_packing_never_used_as_sale(self):
  a=doc([entry('s','ipt_in',items=[{'name':'DAWAT 3 kg','qty':'20','unit':'packet','rate':'100'}]),entry('r','return',items=[{'name':'DAWAT 1 kg','qty':'2','unit':'packet','rate':'125'}])]);self.assertEqual(check([a])['findings'][0]['type'],'Return supply needs review')
 def test_actual_combined_all_parties_and_repeat_no_added_findings(self):
  documents=import_pdf_documents((Path(__file__).resolve().parents[1]/'fixtures/surendranagar_combined.pdf').read_bytes(),initial_settings());before=copy.deepcopy(documents);r=check(documents);again=check(documents+documents);self.assertEqual(r,again);self.assertEqual(documents,before);self.assertEqual(r['party_count'],49)
