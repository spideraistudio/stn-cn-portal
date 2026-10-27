import copy,tempfile,unittest
from pathlib import Path
from engine import compute,D
from allocation_review import review_allocation
from abs_distribution import preview as abs_preview
from store import Store
from test_calculator import example

def maize(quantities=('800','32','60'),payment='100000',date='2026-05-10'):
 r,s=example('scheme-4','0','0','0',[(date,payment)]);sc=s['schemes'][3];r['allocations']=[];r['entries'][0]['items']=[]
 for pid,q in zip(sc['products'],quantities):
  p=next(p for p in s['products'] if p['id']==pid);r['entries'][0]['items'].append({'name':p['name'],'product':pid,'qty':q,'unit':'kg','rate':'350','amount':str(D(q)*350)})
 total=sum((D(q) for q in quantities),D(0))*350;r['entries'][0]['debit']=str(total);r['closing']=str(total-D(payment));return r,s

class AllocationReviewTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.st=Store(Path(self.tmp.name)/'test.sqlite')
 def save(self,r,s):self.st.save_settings(s);self.r=self.st.save(r)
 def body(self,**kw):return {'id':self.r['id'],'revision':self.r['revision'],'operation':'cd-group','scheme':'scheme-4','source':'receipt0','amount':'100000',**kw}
 def test_three_products_one_pool_readonly(self):
  r,s=maize();self.save(r,s);b=self.body();prior=self.st.backup();p=review_allocation(self.st,b);after=self.st.backup();prior.pop('created_at');after.pop('created_at');self.assertEqual(prior,after)
  self.assertEqual(p['retained'],D(100000));self.assertEqual(p['released'],D(0));self.assertEqual(p['percent'],D(12));self.assertEqual(len(p['products']),3);self.assertEqual(p['CD'],D(12000));saved=review_allocation(self.st,{**b,'expected':p['expected']},True)
  self.assertEqual(len(saved['allocations']),1);self.assertEqual(saved['allocations'][0]['product'],'');self.assertEqual(saved['entries'],self.r['entries']);self.assertEqual(self.st.calculate(saved)['issues'],[]);self.assertEqual(sum((x['CD_CN'] for x in p['products']),D(0)),D(12000))
 def test_one_packet_caps_leaves_excess(self):
  r,s=maize(('4',),'50000');self.save(r,s);b=self.body(amount='50000');p=review_allocation(self.st,b);self.assertGreater(p['released'],D(48000));self.assertEqual(p['retained']+p['released'],D(50000));self.assertLess(p['retained']-p['used'],D('.01'))
  full=copy.deepcopy(self.r);full['allocations']=[{'id':'full','source':'receipt0','scheme':'scheme-4','product':'','type':'CD','amount':'50000'}];saved=review_allocation(self.st,{**b,'expected':p['expected']},True);actual=self.st.calculate(saved);self.assertEqual(actual['new_CN_total'],compute(full,s)['new_CN_total']);self.assertEqual(actual['unallocated'],p['released']);self.assertEqual(saved['entries'],self.r['entries'])
 def test_release_preserves_ledger_and_entitlement(self):
  r,s=maize(('4',),'50000');r['allocations']=[{'id':'large','source':'receipt0','scheme':'scheme-4','product':s['schemes'][3]['products'][0],'type':'CD','amount':'50000'}];self.save(r,s);b=self.body(operation='cd-release',target='large');p=review_allocation(self.st,b);saved=review_allocation(self.st,{**b,'expected':p['expected']},True);self.assertEqual(self.st.calculate(saved)['new_CN_total'],p['previous_CN']);self.assertEqual(p['new_CN'],p['previous_CN']);self.assertGreater(p['released'],D(48000))
  for k in self.r:
   if k not in ('allocations','revision','saved_at'):self.assertEqual(saved[k],self.r[k],k)
  with self.assertRaisesRegex(ValueError,'No releasable'):review_allocation(self.st,{**b,'revision':saved['revision']})
 def test_zero_used_release_removes_only_target(self):
  r,s=maize(('4',),'50000');r['allocations']=[{'id':'first','source':'receipt0','scheme':'scheme-4','type':'CD','amount':'5000'},{'id':'second','source':'receipt0','scheme':'scheme-4','type':'CD','amount':'45000'}];self.save(r,s);b=self.body(operation='cd-release',target='second');p=review_allocation(self.st,b);self.assertEqual(p['retained'],D(0));saved=review_allocation(self.st,{**b,'expected':p['expected']},True);self.assertEqual([a['id'] for a in saved['allocations']],['first'])
 def test_date_and_zero_rate_not_upgraded(self):
  r,s=maize(('4',),'50000','2026-09-10');self.save(r,s);b=self.body(amount='50000');p=review_allocation(self.st,b);self.assertEqual(p['percent'],D(0));self.assertEqual(p['CD'],D(0));self.assertEqual(p['original_date'],'2026-09-10');saved=review_allocation(self.st,{**b,'expected':p['expected']},True);self.assertEqual(saved['entries'],self.r['entries'])
 def test_stale_settings_revision_selection_frozen(self):
  r,s=maize();self.save(r,s);b=self.body();p=review_allocation(self.st,b)
  with self.assertRaisesRegex(ValueError,'changed'):review_allocation(self.st,{**b,'amount':'10','expected':p['expected']},True)
  self.st.save_settings(self.st.settings())
  with self.assertRaisesRegex(ValueError,'changed'):review_allocation(self.st,{**b,'expected':p['expected']},True)
  saved=self.st.save(self.r)
  with self.assertRaisesRegex(ValueError,'changed'):review_allocation(self.st,b)
  saved['allocations']=[{'id':'settle','type':'Settlement','scheme':'scheme-4','source':'receipt0','amount':'100000'}];saved=self.st.save(saved);self.st.finalise(saved['id'],saved['revision'])
  with self.assertRaisesRegex(ValueError,'draft revision'):review_allocation(self.st,{**b,'revision':saved['revision']})
 def test_limits_old_dues_options_segment(self):
  r,s=maize();r['opening']='10000';r['old_dues']='10000';r['closing']=str(D(r['closing'])+10000);self.save(r,s);p=review_allocation(self.st,self.body(options=True,crop='Maize'));self.assertEqual([x['id'] for x in p['schemes']],['scheme-4']);self.assertEqual(p['sources'][0]['remaining'],D(90000))
  for kw in ({'amount':'100000'},{'amount':'-1'},{'amount':'NaN'},{'scheme':'scheme-5'},{'source':'bad'},{'crop':'Cotton'}):
   with self.assertRaises(ValueError):review_allocation(self.st,self.body(**kw))
 def test_earlier_receipt_displaces_later_funding(self):
  r,s=maize(('4',),'50000');r['entries'].append({'id':'later','date':'2026-06-10','kind':'receipt','debit':'0','credit':'10000','reviewed':True});r['closing']=str(D(r['closing'])-10000);r['allocations']=[{'id':'later-cd','type':'CD','source':'later','scheme':'scheme-4','amount':'10000'}];self.save(r,s);p=review_allocation(self.st,self.body(amount='50000'));self.assertEqual(p['affected'][0]['source'],'later');self.assertEqual(p['affected'][0]['unused'],D(10000))
 def test_abs_product_capacity_and_existing_excess(self):
  r,s=maize(date='2026-03-20');p=abs_preview(r,s,scheme='scheme-4',source='receipt0',amount='100000');self.assertEqual(sum((x['token_applied'] for x in p['products']),D(0)),D(44600));self.assertEqual(sum((x['excess'] for x in p['products']),D(0)),D(55400));self.assertEqual(p['excess_ABS'],D(55400))
 def test_invalid_release_and_operation(self):
  r,s=maize();self.save(r,s)
  for kw in ({'operation':'cd-release','target':'bad'},{'operation':'bad'}):
   with self.assertRaises(ValueError):review_allocation(self.st,self.body(**kw))

 def test_existing_receipt_cannot_fund_same_capacity_twice(self):
  r,s=maize(('4',),'50000');r['allocations']=[{'id':'existing','source':'receipt0','scheme':'scheme-4','type':'CD','amount':'2000'}];self.save(r,s)
  p=review_allocation(self.st,self.body(amount='10000'));self.assertEqual(p['retained'],D(0));self.assertEqual(p['released'],D(10000))
  with self.assertRaisesRegex(ValueError,'no additional'):review_allocation(self.st,{**self.body(amount='10000'),'expected':p['expected']},True)
 def test_top_up_existing_split_preserves_identity(self):
  r,s=maize();r['allocations']=[{'id':'existing','source':'receipt0','scheme':'scheme-4','type':'CD','amount':'10000'}];self.save(r,s)
  b=self.body(amount='20000');p=review_allocation(self.st,b);saved=review_allocation(self.st,{**b,'expected':p['expected']},True)
  self.assertEqual(len(saved['allocations']),1);self.assertEqual(saved['allocations'][0]['id'],'existing');self.assertEqual(saved['allocations'][0]['amount'],'30000');self.assertEqual(p['CD'],D(2400))
