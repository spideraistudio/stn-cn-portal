import copy,tempfile,unittest
from pathlib import Path
from test_calculator import example,D
from engine import compute,validate_input_limits
from store import Store

class InputLimitTests(unittest.TestCase):
 def test_one_lakh_cannot_be_ten_lakh_any_allocation_type(self):
  for kind in ('ABS','CD','Cash','Settlement'):
   r,s=example(abs_amount='100000');r['allocations'][0].update(amount='1000000',type=kind)
   with self.assertRaisesRegex(ValueError,'availability'):validate_input_limits(r,s)
   out=compute(r,s);self.assertFalse(out['can_finalise']);self.assertEqual(out['new_CN_total'],D(0));self.assertEqual(out['CNs'],[]);self.assertTrue(out['sources'])
 def test_sum_all_rows_across_destinations(self):
  r,s=example(abs_amount='100000');r['allocations'][0]['amount']='50000';r['allocations'].append({**r['allocations'][0],'id':'another','amount':'50000','type':'Settlement','scheme':'scheme-2'})
  validate_input_limits(r,s);r['allocations'][-1]['amount']='50000.01'
  with self.assertRaisesRegex(ValueError,'availability'):validate_input_limits(r,s)
 def test_old_dues_reduce_cap_and_source_change(self):
  r,s=example(abs_amount='0',payments=[('2026-05-01','100000'),('2026-05-02','50000')]);r.update(opening='20000',old_dues='20000');r['allocations'][0]['amount']='80000';validate_input_limits(r,s)
  r['allocations'][0]['amount']='80000.01'
  with self.assertRaises(ValueError):validate_input_limits(r,s)
  r['allocations'][0].update(source='receipt1',amount='1')
  with self.assertRaises(ValueError):validate_input_limits(r,s)
 def test_negative_nonfinite_duplicates_and_opening_credit(self):
  for value in ('-1','NaN','Infinity'):
   r,s=example();r['allocations'][0]['amount']=value
   with self.assertRaises((ValueError,ArithmeticError)):validate_input_limits(r,s)
  r,s=example();r['opening_sources']=[{'id':'o','amount':'1'}]
  with self.assertRaisesRegex(ValueError,'Opening-credit'):validate_input_limits(r,s)
  r,s=example();r['allocations'].append(copy.deepcopy(r['allocations'][0]))
  with self.assertRaisesRegex(ValueError,'identity'):validate_input_limits(r,s)
 def test_save_rejects_without_changing_saved_data(self):
  r,s=example()
  with tempfile.TemporaryDirectory() as d:
   st=Store(Path(d)/'test.sqlite');s['version']=st.settings()['version'];st.save_settings(s);saved=st.save(r);backup=st.backup();bad=copy.deepcopy(saved);bad['allocations'][0]['amount']='1000000'
   with self.assertRaisesRegex(ValueError,'availability'):st.save(bad)
   self.assertEqual(st.get(saved['id']),saved);self.assertEqual(st.backup()['records'],backup['records'])
 def test_oversized_cash_quantity_and_values(self):
  for field,value in [('supplied','10001'),('returned','501'),('cash_sales_value','1400001'),('cash_returns_value','70001'),('deduction_rate','-1')]:
   r,s=example('scheme-5','10000','500','0');r['cash_splits']=[{'scheme':'scheme-5','product':s['schemes'][4]['products'][0],'supplied':'3000','returned':'100','deduction_rate':'0','remark':'test',field:value}]
   with self.assertRaises(ValueError):validate_input_limits(r,s)
   self.assertEqual(compute(r,s)['CNs'],[])
 def test_product_name_edit_add_and_identity_protection(self):
  with tempfile.TemporaryDirectory() as d:
   st=Store(Path(d)/'test.sqlite');s=st.settings();old=copy.deepcopy(s['products'][0]);s['products'][0]['name']='New name';s=st.save_settings(s);self.assertEqual(s['products'][0]['id'],old['id'])
   bad=copy.deepcopy(s);bad['products'][0]['packing_kg']='1'
   with self.assertRaisesRegex(ValueError,'identity'):st.save_settings(bad)
   sc=s['schemes'][0];new={**old,'id':'new-id','name':'New product'};s['products'].append(new);sc['products'].append(new['id']);s=st.save_settings(s);self.assertEqual(s['products'][-1],new)
