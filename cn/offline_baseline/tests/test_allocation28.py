import copy,tempfile,unittest
from pathlib import Path
from test_calculator import example,D
from cash_quantity import preview
from engine import compute
from store import Store

def cash_case():
 r,s=example('scheme-5','1500','0','0',[]);r['entries']=[e for e in r['entries'] if e['kind']!='receipt'];r['allocations']=[];r['entries'].append({'id':'paid','kind':'receipt','date':'2026-03-20','credit':'100000','debit':'0','reviewed':True});r['closing']='110000'
 return r,s,{'scheme':'scheme-5','product':s['schemes'][4]['products'][0],'source':'paid','amount':'100000','supplied':'1000','returned':'0'}
class Allocation28Tests(unittest.TestCase):
 def test_cash_reference_no_double_benefits(self):
  r,s,a=cash_case();before=copy.deepcopy(r);p=preview(r,s,**a);self.assertEqual(r,before);self.assertEqual(p['cash_net'],D(1000));self.assertEqual(p['regular_net'],D(500));self.assertEqual(p['Cash_CN'],D(40000));o=compute(p['candidate'],s);self.assertEqual(o['issues'],[]);self.assertEqual(o['groups'][0]['net'],D(500));self.assertEqual(next(c['rounded'] for c in o['CNs'] if c['benefit']=='Quantity'),D(5000));self.assertEqual(o['new_CN_total'],D(45000));self.assertEqual(o['final_balance'],D(65000));self.assertEqual(o['unallocated'],D(0));self.assertEqual(p['candidate']['entries'],r['entries'])
 def test_old_dues_reduce_funding(self):
  r,s,a=cash_case();r.update(opening='20000',old_dues='20000',closing='130000')
  with self.assertRaisesRegex(ValueError,'availability'):preview(r,s,**a)
  a['amount']='80000'
  with self.assertRaisesRegex(ValueError,'cover'):preview(r,s,**a)
  a['supplied']='800';p=preview(r,s,**a);self.assertEqual(p['regular_net'],D(700));self.assertEqual(compute(p['candidate'],s)['sources'][0]['old_dues_cleared'],D(20000))
 def test_original_dates_and_membership(self):
  r,s,a=cash_case();r['entries'][-1]['date']='2026-07-01'
  with self.assertRaisesRegex(ValueError,'original payment date'):preview(r,s,**a)
  r['entries'][-1]['original']={**r['entries'][-1],'date':'2026-03-20'};self.assertEqual(preview(r,s,**a)['original_date'],'2026-03-20');a['product']=s['schemes'][3]['products'][0]
  with self.assertRaisesRegex(ValueError,'eligible'):preview(r,s,**a)
 def test_cash_returns_need_review(self):
  r,s,a=cash_case();r['entries'].append({'id':'ret','kind':'return','date':'2026-06-20','credit':'14000','debit':'0','reviewed':True,'items':[{'name':'32D55','product':a['product'],'qty':'100','unit':'kg','rate':'140','amount':'14000'}]});r['closing']='96000';a['returned']='100'
  with self.assertRaisesRegex(ValueError,'deduction rate'):preview(r,s,**a)
  a.update(deduction_rate='0',remark='Reviewed Cash return');p=preview(r,s,**a);self.assertEqual(p['cash_net'],D(900));self.assertEqual(p['Cash_CN'],D(36000));self.assertEqual(p['regular_net'],D(500));a['returned']='101'
  with self.assertRaisesRegex(ValueError,'conservation'):preview(r,s,**a)
 def test_two_sources_edit_preserves_total(self):
  r,s,a=cash_case();a.update(amount='60000',supplied='600');r=preview(r,s,**a)['candidate'];r['entries'].append({'id':'paid2','kind':'receipt','date':'2026-03-25','credit':'40000','debit':'0'});r['closing']='70000';a.update(source='paid2',amount='40000',supplied='1000');p=preview(r,s,**a);self.assertEqual(p['funding'],D(100000));self.assertEqual(p['Cash_CN'],D(40000));self.assertEqual(len(p['candidate']['cash_splits']),1);a['replace_id']=p['allocation']['id'];p2=preview(p['candidate'],s,**a);self.assertEqual(p2['funding'],D(100000));self.assertEqual(len(p2['candidate']['allocations']),2)
 def test_net_assignment_no_extra_payment_cn(self):
  r,s=example('scheme-1','400','0','0',[]);r['entries']=[e for e in r['entries'] if e['kind']!='receipt'];r['entries'].append({'id':'net-paid','kind':'receipt','date':'2026-06-01','debit':'0','credit':'50000','reviewed':True});r['allocations']=[{'id':'net-row','source':'net-paid','scheme':'scheme-1','product':s['schemes'][0]['products'][0],'type':'Net','amount':'50000'}];r['closing']='310400';o=compute(r,s);self.assertEqual(o['issues'],[]);self.assertEqual(o['unallocated'],D(0));self.assertEqual([c['benefit'] for c in o['CNs']],['Net rate']);self.assertEqual(o['new_CN_total'],D(90400));self.assertEqual(o['final_balance'],D(220000));r['allocations'][0]['scheme']='scheme-5';self.assertTrue(any('Net Rate' in i or 'destination' in i for i in compute(r,s)['issues']))
 def test_dues_review_binds_amounts(self):
  r,s,a=cash_case();r.update(opening='20000',old_dues='20000',closing='130000',opening_dues_review_required=True);self.assertTrue(any('Confirm opening' in i for i in compute(r,s)['issues']));r['opening_dues_review']={'opening':'20000','old_dues':'20000','reason':''};self.assertFalse(any('Confirm opening' in i for i in compute(r,s)['issues']));r['old_dues']='0';self.assertTrue(any('Confirm opening' in i for i in compute(r,s)['issues']));r['opening_dues_review']['old_dues']='0';self.assertTrue(any('Explain the opening' in i for i in compute(r,s)['issues']));r['opening_dues_review']['reason']='Separately reconciled';self.assertFalse(any('opening' in i.lower() for i in compute(r,s)['issues']))
 def test_store_preview_apply_and_guards(self):
  with tempfile.TemporaryDirectory() as d:
   r,s,a=cash_case();st=Store(Path(d)/'test.sqlite');cfg=st.save_settings(s);r=st.save(r);payload={'record':r,**a};before=st.backup();st.preview_cash_quantity(payload);self.assertEqual(st.backup()['records'],before['records']);self.assertEqual(st.get(r['id'])['cash_splits'],[])
   with self.assertRaisesRegex(ValueError,'settings changed'):st.preview_cash_quantity({**payload,'settings_version':-1},apply=True)
   saved=st.preview_cash_quantity({**payload,'settings_version':cfg['version']},apply=True);self.assertEqual(st.calculate(saved)['new_CN_total'],D(45000))
   with self.assertRaisesRegex(ValueError,'Record changed'):st.preview_cash_quantity(payload)
   forged=copy.deepcopy(saved);forged['entries'][-1]['date']='2026-07-01';forged['entries'][-1]['original']['date']='2026-07-01';a['replace_id']=saved['allocations'][0]['id'];self.assertEqual(st.preview_cash_quantity({'record':forged,**a})['original_date'],'2026-03-20');frozen=st.finalise(saved['id'],saved['revision']);frozen['status']='draft'
   with self.assertRaisesRegex(ValueError,'draft revision'):st.preview_cash_quantity({'record':frozen,**a})
