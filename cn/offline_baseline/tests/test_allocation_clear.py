import copy,tempfile,unittest
from pathlib import Path
from store import Store
from allocation_clear import clear_allocations
from test_regular_cash import scenario
from engine import D
class AllocationClearTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.st=Store(Path(self.tmp.name)/'test.sqlite');r,s,self.pid=scenario();self.cfg=self.st.save_settings(s);self.r=self.st.save(r)
 def body(self,scope='all',target=''):return {'id':self.r['id'],'revision':self.r['revision'],'scope':scope,'target':target}
 def test_readonly_preview_all_preserves_ledger(self):
  b=self.body();before=self.st.backup();plan=clear_allocations(self.st,b);after=self.st.backup();before.pop('created_at');after.pop('created_at');self.assertEqual(before,after);self.assertEqual(plan['released_total'],D(600000));self.assertEqual(len(plan['cash_splits']),1)
  saved=clear_allocations(self.st,{**b,'expected':plan['expected']},True);self.assertEqual(saved['allocations'],[]);self.assertEqual(saved['cash_splits'],[])
  for key in self.r:
   if key not in ('allocations','cash_splits','revision','saved_at'):self.assertEqual(saved[key],self.r[key],key)
  self.assertEqual(self.st.calculate(saved)['unallocated'],D(600000))
 def test_single_payment_keeps_other_rows(self):
  b=self.body('source','may');plan=clear_allocations(self.st,b);self.assertEqual(plan['released_total'],D(20000));self.assertEqual(plan['cash_splits'],[]);saved=clear_allocations(self.st,{**b,'expected':plan['expected']},True);self.assertEqual(saved['cash_splits'],self.r['cash_splits']);self.assertEqual(saved['allocations'],[a for a in self.r['allocations'] if a['source']!='may'])
 def test_cross_receipt_cash_group_explicit(self):
  r=copy.deepcopy(self.r);cash=next(a for a in r['allocations'] if a['type']=='Cash');cash['amount']='200000';r['entries'].append({'id':'march2','kind':'receipt','date':'2026-03-22','credit':'100000','debit':'0','reviewed':True});r['closing']='700000';r['allocations'].append({**cash,'id':'cash2','source':'march2','amount':'100000'});self.r=self.st.save(r);b=self.body('source','march2');plan=clear_allocations(self.st,b);self.assertEqual(plan['extra_rows'],1);self.assertEqual(plan['released_by_source'],{'march':D(200000),'march2':D(100000)});saved=clear_allocations(self.st,{**b,'expected':plan['expected']},True);self.assertEqual(saved['cash_splits'],[]);self.assertEqual(saved['allocations'],[a for a in self.r['allocations'] if a['type']!='Cash']);self.assertEqual(saved['entries'],self.r['entries'])
 def test_stale_guards_and_selection_binding(self):
  b=self.body('row','regular-cd');plan=clear_allocations(self.st,b)
  with self.assertRaisesRegex(ValueError,'changed'):clear_allocations(self.st,{**b,'scope':'all','expected':plan['expected']},True)
  self.st.save_settings(self.st.settings())
  with self.assertRaisesRegex(ValueError,'changed'):clear_allocations(self.st,{**b,'expected':plan['expected']},True)
  self.st.save(self.r)
  with self.assertRaisesRegex(ValueError,'changed'):clear_allocations(self.st,b)
 def test_frozen_unknown_targets(self):
  for scope,target in [('row','bad'),('source','bad'),('bad','')]:
   with self.assertRaises(ValueError):clear_allocations(self.st,self.body(scope,target))
  self.st.finalise(self.r['id'],self.r['revision'])
  with self.assertRaisesRegex(ValueError,'draft revision'):clear_allocations(self.st,self.body())
 def test_orphan_split_can_be_cleared(self):
  r=copy.deepcopy(self.r);r['allocations']=[];self.r=self.st.save(r);b=self.body();plan=clear_allocations(self.st,b);self.assertEqual(plan['removed'],[]);self.assertEqual(len(plan['cash_splits']),1);saved=clear_allocations(self.st,{**b,'expected':plan['expected']},True);self.assertEqual(saved['cash_splits'],[])
