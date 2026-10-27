import copy,unittest
from test_ledger_audit import entry,doc,check

class CrossPartyReturnTests(unittest.TestCase):
 def item(self,**kw):return dict(name='DAWAT 1 KG',unit='packet',qty='20',amount='2000',rate='100',source_page=2,source_line=8,**kw)
 def documents(self):
  i=self.item()
  return [doc([entry('R1','return','2000',items=[i])],'Shree Seeds'),doc([entry('R2','return','2000',items=[copy.deepcopy(i)])],'Shri Seeds')]
 def matches(self,docs):return [f for f in check(docs)['findings'] if f['type']=='Possible duplicate sales return']
 def test_strict_cross_party_and_complete_voucher(self):
  docs=self.documents();before=copy.deepcopy(docs);r=self.matches(docs)
  self.assertEqual(len(r),1);self.assertTrue(r[0]['full_voucher_match']);self.assertEqual(len(r[0]['vouchers']),2)
  self.assertEqual(r[0]['vouchers'][0]['item']['source_page'],2);self.assertEqual(docs,before)
 def test_unrelated_names_also_compare(self):
  docs=self.documents();docs[1]['party']='Entirely Different Traders';self.assertEqual(len(self.matches(docs)),1)
 def test_no_weaker_matches(self):
  for field,value in [('date','2026-05-02'),('name','DAWAT 3 KG'),('unit','kg'),('qty','21'),('amount','1999')]:
   with self.subTest(field=field):
    docs=self.documents();e=docs[1]['entries'][0]
    (e if field=='date' else e['items'][0])[field]=value
    self.assertFalse(self.matches(docs))
 def test_same_party_and_same_pdf_do_not_manufacture_cross_party_matches(self):
  docs=self.documents();docs[1]['party']=docs[0]['party'];self.assertFalse(self.matches(docs))
  docs=self.documents();r=self.matches(docs);self.assertEqual(r,self.matches(docs+copy.deepcopy(docs)))
 def test_source_precision_order_and_whitespace(self):
  docs=self.documents();i=docs[1]['entries'][0]['items'][0];i.update(name=' dawat  1 kg ',qty='20.000',amount='2000.00');self.assertEqual(len(self.matches(docs)),1)
 def test_partial_voucher_match_is_still_strict_item_match(self):
  docs=self.documents();docs[1]['entries'][0]['items'].append(dict(name='OTHER',unit='packet',qty='1',amount='10',rate='10'));docs[1]['entries'][0]['credit']='2010'
  r=self.matches(docs);self.assertEqual(len(r),1);self.assertFalse(r[0]['full_voucher_match'])
 def test_missing_zero_or_negative_values_never_match(self):
  for field,value in [('qty',None),('amount',None),('amount','0'),('qty','-1'),('unit',''),('name','')]:
   docs=self.documents()
   for d in docs:d['entries'][0]['items'][0][field]=value
   self.assertFalse(self.matches(docs))
 def test_ipt_not_return_and_period_scope(self):
  docs=self.documents();docs[1]['entries'][0]['kind']='ipt_in';self.assertFalse(self.matches(docs))
  docs=self.documents()
  for d in docs:d['entries'][0]['date']='2026-09-01'
  self.assertFalse(self.matches(docs))
 def test_pack_metadata_and_multiline_complete_signature(self):
  docs=self.documents();docs[0]['entries'][0]['items'][0]['packing_kg']='1';docs[1]['entries'][0]['items'][0]['packing_kg']='3';self.assertFalse(self.matches(docs))
  docs=self.documents()
  for d in docs:d['entries'][0]['items'].append(dict(name='OTHER',unit='kg',qty='5',amount='50',rate='10'))
  docs[1]['entries'][0]['items'].reverse();r=self.matches(docs);self.assertEqual(len(r),2);self.assertTrue(all(f['full_voucher_match'] for f in r))
 def test_multiple_equal_lines_stay_one_voucher_per_comparison(self):
  docs=self.documents();docs[0]['entries'][0]['items']*=2;r=self.matches(docs)
  self.assertEqual(len(r),1);self.assertEqual(len(r[0]['vouchers']),2);self.assertFalse(r[0]['full_voucher_match'])
