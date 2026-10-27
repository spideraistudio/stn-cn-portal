import unittest,copy,tempfile
from pathlib import Path
from decimal import Decimal
from engine import compute,D
from abs_distribution import preview
from store import Store
from test_calculator import example

class ABSDistributionTests(unittest.TestCase):
 def case(self,amount='30000'):
  r,s=example('scheme-4',sup='100',ret='0',abs_amount=amount,payments=[]);r['status']='draft'
  r['entries']=[e for e in r['entries'] if e['id'] in ('sale','advance')];r['allocations']=[a for a in r['allocations'] if a['type']=='ABS'];r['allocations'][0]['product']=''
  sc=s['schemes'][3];first=r['entries'][0];first['items'].append(dict(name='Second',product=sc['products'][1],qty='200',unit='kg',amount='70000'));first['debit']='105000';r['closing']=str(D(105000)-D(amount));return r,s,sc
 def plan(self,r,s,sc,**kw):return preview(r,s,crop=sc['crop'],source='advance',amount=r['allocations'][0]['amount'],replace_id='aa',**kw)
 def test_crop_auto_select_split_cap_and_excess_first_cd(self):
  r,s,sc=self.case();before=copy.deepcopy((r,s));p=self.plan(r,s,sc)
  self.assertEqual(p['scheme'],sc['id']);self.assertEqual([D(a['amount']) for a in p['allocations']],[20000,10000]);self.assertEqual(p['ABS_CN'],3000);self.assertEqual(p['excess_ABS'],15000);self.assertGreater(p['CD_CN'],0);self.assertEqual((r,s),before)
  self.assertTrue(all(a['type']=='ABS' and a['source']=='advance' for a in p['allocations']))
 def test_short_booking_is_proportional_and_exact(self):
  r,s,sc=self.case('1500.01');p=self.plan(r,s,sc);self.assertEqual(sum(D(a['amount']) for a in p['allocations']),D('1500.01'))
  amounts=[D(a['amount']) for a in p['allocations']];self.assertLess(abs(amounts[1]-2*amounts[0]),D('0.02'));self.assertEqual(p['excess_ABS'],0)
 def test_existing_manual_abs_capacity_is_not_booked_twice(self):
  r,s,sc=self.case();r['entries'].append(dict(id='manual',kind='receipt',date='2026-03-21',credit='5000',debit='0'));r['allocations'].append(dict(id='manual',source='manual',scheme=sc['id'],product=sc['products'][0],amount='5000',type='ABS'));r['closing']=str(D(r['closing'])-5000)
  p=self.plan(r,s,sc);self.assertEqual(p['ABS_CN'],3000);self.assertEqual(p['excess_ABS'],20000)
 def test_already_covered_products_receive_only_excess(self):
  r,s,sc=self.case();r['entries'].append(dict(id='manual',kind='receipt',date='2026-03-21',credit='15000',debit='0'));r['allocations'] += [dict(id='m'+str(i),source='manual',scheme=sc['id'],product=pid,amount=str(a),type='ABS') for i,(pid,a) in enumerate(zip(sc['products'],[5000,10000]))];r['closing']=str(D(r['closing'])-15000)
  p=self.plan(r,s,sc);self.assertEqual(p['ABS_CN'],3000);self.assertEqual(p['excess_ABS'],30000);self.assertEqual(sum(D(a['amount']) for a in p['allocations']),30000)
 def test_date_caps_extension_and_original_date_enforced(self):
  for dt in ['2026-07-01',None]:
   r,s,sc=self.case();r['entries'][1]['date']=dt
   with self.assertRaisesRegex(ValueError,'original payment date'):self.plan(r,s,sc)
  r,s,sc=self.case();r['entries'][1]['original']={**r['entries'][1],'date':'2026-07-01'}
  with self.assertRaises(ValueError):self.plan(r,s,sc)
  r,s,sc=self.case();sc['extended_end']='2026-04-15';r['entries'][1]['date']='2026-04-10'
  with self.assertRaisesRegex(ValueError,'approval'):self.plan(r,s,sc)
  p=self.plan(r,s,sc,approved=True,remark='Reviewed extension');self.assertEqual(p['ABS_CN'],3000)
  with self.assertRaisesRegex(ValueError,'availability'):preview(r,s,scheme=sc['id'],source='advance',amount='30000.01',replace_id='aa',approved=True,remark='Reviewed')
 def test_undated_opening_credit_and_no_second_receipt(self):
  r,s,sc=self.case();r['entries']=[e for e in r['entries'] if e['kind']!='receipt'];r.update(opening='-30000',opening_sources=[dict(id='opening',amount='30000',date=None)]);r['allocations'][0]['source']='opening';p=preview(r,s,crop='Maize',source='opening',amount='30000',replace_id='aa');self.assertEqual(p['ABS_CN'],3000);self.assertIsNone(p['original_date'])
 def test_multiple_segments_and_no_eligible_sales_require_choice(self):
  r,s,sc=self.case();second=copy.deepcopy(sc);second.update(id='another',segment_id='another',segment='Different',products=['new']);s['schemes'].append(second);p=copy.deepcopy(next(p for p in s['products'] if p['id']==sc['products'][0]));p.update(id='new',scheme='another',segment_id='another',segment='Different');s['products'].append(p);r['entries'][0]['items'].append(dict(name='Other',product='new',qty='10',unit='kg',amount='3500'));r['entries'][0]['debit']=str(D(r['entries'][0]['debit'])+3500);r['closing']=str(D(r['closing'])+3500)
  with self.assertRaisesRegex(ValueError,'multiple'):self.plan(r,s,sc)
  self.assertEqual(self.plan(r,s,sc,scheme=sc['id'])['scheme'],sc['id'])
  r['entries'][0]['items']=[]
  with self.assertRaises(ValueError):self.plan(r,s,sc)
 def test_frozen_negative_zero_and_overallocated_rows_rejected(self):
  for amount in ['0','-1','NaN']:
   r,s,sc=self.case()
   with self.assertRaises((ValueError,ArithmeticError)):preview(r,s,crop='Maize',source='advance',amount=amount,replace_id='aa')
  r,s,sc=self.case();r['status']='issued'
  with self.assertRaisesRegex(ValueError,'revision'):self.plan(r,s,sc)
 def test_review_issues_stay_visible_and_zero_net_products_not_allocated(self):
  r,s,sc=self.case();zero=sc['products'][2];r['entries'].append(dict(id='unmatched',kind='return',date='2026-05-01',debit='0',credit='1750',items=[dict(product=zero,name='Zero product',qty='5',unit='kg',amount='1750')]));r['closing']=str(D(r['closing'])-1750)
  p=self.plan(r,s,sc);self.assertTrue(any('Returns without' in e for e in p['issues']));self.assertNotIn(zero,[a['product'] for a in p['allocations']])
 def test_preview_read_only_apply_atomic_stale_and_manual_edit(self):
  r,s,sc=self.case()
  with tempfile.TemporaryDirectory() as td:
   st=Store(Path(td)/'a.sqlite3');st.save_settings(s);r=st.save(r);before=st.backup();payload=dict(record=r,crop='Maize',source='advance',amount='30000',replace_id='aa');p=st.preview_abs_distribution(payload);after=st.backup();self.assertEqual(before['records'],after['records']);self.assertEqual(before['audit'],after['audit'])
   with self.assertRaisesRegex(ValueError,'settings changed'):st.preview_abs_distribution({**payload,'settings_version':0},apply=True)
   saved=st.preview_abs_distribution({**payload,'settings_version':p['settings_version']},apply=True);self.assertEqual(sum(D(a['amount']) for a in saved['allocations']),30000);self.assertEqual(st.calculate(saved)['new_CN_total'],compute({**r,'allocations':p['allocations']},s)['new_CN_total']);self.assertEqual(saved['entries'],r['entries'])
   with self.assertRaisesRegex(ValueError,'Record changed'):st.preview_abs_distribution({**payload,'settings_version':p['settings_version']},apply=True)
   saved['allocations'][0]['amount']=str(D(saved['allocations'][0]['amount'])-1);saved['allocations'][1]['amount']=str(D(saved['allocations'][1]['amount'])+1);st.save(saved)
