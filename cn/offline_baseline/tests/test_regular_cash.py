"""Regular + Cash stock/payment conservation and transactional removal."""
import copy,tempfile,unittest
from pathlib import Path
from test_calculator import example,D
from cash_quantity import preview
from engine import compute
from store import Store

def scenario():
 r,s=example('scheme-5','10000','0','0',[])
 r['entries']=[e for e in r['entries'] if e['kind']!='receipt']
 r['entries'] += [{'id':'march','kind':'receipt','date':'2026-03-20','credit':'580000','debit':'0','reviewed':True},{'id':'may','kind':'receipt','date':'2026-05-10','credit':'20000','debit':'0','reviewed':True}]
 r['closing']='800000';pid=s['schemes'][4]['products'][0]
 r['allocations']=[{'id':'regular-abs','source':'march','type':'ABS','scheme':'scheme-5','product':pid,'amount':'280000'},{'id':'regular-cd','source':'may','type':'CD','scheme':'scheme-5','product':'','amount':'20000'}]
 plan=preview(r,s,scheme='scheme-5',product=pid,source='march',amount='300000',supplied='3000')
 return plan['candidate'],s,pid

class RegularCashTests(unittest.TestCase):
 def test_ten_thousand_kg_six_lakh_split(self):
  r,s,pid=scenario();o=compute(r,s)
  self.assertEqual(o['issues'],[])
  cn={c['benefit']:c['rounded'] for c in o['CNs']}
  self.assertEqual(cn,{'Cash 32D55':D(120000),'Quantity':D(140000),'ABS':D(70000),'CD':D(2400)})
  self.assertEqual(o['new_CN_total'],D(332400));self.assertEqual(o['final_balance'],D(467600));self.assertEqual(o['unallocated'],D(0))
  row=o['product_CNs'][0];self.assertEqual(row['net_sold'],D(10000));self.assertEqual(row['regular_net'],D(7000))
 def test_cash_only_payment_does_not_create_regular_abs(self):
  r,s,pid=scenario();r['allocations']=[a for a in r['allocations'] if a['type']=='Cash'];r['entries']=[e for e in r['entries'] if e['id']!='may'];r['entries'][-1]['credit']='300000';r['closing']='1100000'
  o=compute(r,s);self.assertEqual(o['issues'],[])
  self.assertEqual(next(c['rounded'] for c in o['CNs'] if c['benefit']=='ABS'),D(0));self.assertEqual(o['product_CNs'][0]['regular_net'],D(7000));self.assertEqual(o['new_CN_total'],D(260000))
 def test_remove_preview_cancel_apply_and_stale_guards(self):
  with tempfile.TemporaryDirectory() as d:
   r,s,pid=scenario();st=Store(Path(d)/'test.sqlite');cfg=st.save_settings(s);r=st.save(r);payload={'record':r,'scheme':'scheme-5','product':pid}
   before=copy.deepcopy(st.get(r['id']));plan=st.preview_cash_removal(payload)
   self.assertEqual(st.get(r['id']),before);self.assertEqual(plan['released_total'],D(300000));self.assertEqual(plan['regular_net'],D(10000));self.assertEqual(plan['new_CN'],D(272400))
   with self.assertRaisesRegex(ValueError,'settings changed'):st.preview_cash_removal({**payload,'settings_version':-1},True)
   saved=st.preview_cash_removal({**payload,'settings_version':cfg['version']},True)
   self.assertEqual(saved['entries'],before['entries']);self.assertEqual(saved['cash_splits'],[])
   self.assertEqual(saved['allocations'],[a for a in before['allocations'] if a['type']!='Cash'])
   self.assertEqual(st.calculate(saved)['unallocated'],D(300000))
   with self.assertRaisesRegex(ValueError,'Record changed'):st.preview_cash_removal({**payload,'settings_version':cfg['version']},True)
 def test_remove_multiple_funding_rows(self):
  with tempfile.TemporaryDirectory() as d:
   r,s,pid=scenario();cash=next(a for a in r['allocations'] if a['type']=='Cash');cash['amount']='200000';r['allocations'].append({**cash,'id':'cash-second','amount':'100000'})
   st=Store(Path(d)/'x.sqlite');st.save_settings(s);r=st.save(r);p=st.preview_cash_removal({'record':r,'scheme':'scheme-5','product':pid});self.assertEqual(p['removed_rows'],2);self.assertEqual(p['released_total'],D(300000))
 def test_frozen_cannot_remove_even_with_forged_status(self):
  with tempfile.TemporaryDirectory() as d:
   r,s,pid=scenario();st=Store(Path(d)/'x.sqlite');cfg=st.save_settings(s);r=st.save(r);f=st.finalise(r['id'],r['revision']);f['status']='draft'
   with self.assertRaisesRegex(ValueError,'draft revision'):st.preview_cash_removal({'record':f,'scheme':'scheme-5','product':pid,'settings_version':cfg['version']},True)
