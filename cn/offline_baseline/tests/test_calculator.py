import unittest,sys,tempfile,copy,json
from pathlib import Path
from decimal import Decimal
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from engine import D,compute,rounded,tier,slab_cn,validate_scheme
from settings import initial_settings
from importer import import_pdf,compare_import
from store import Store
ROOT=Path(__file__).resolve().parents[1]

def configured():
 s=initial_settings();s['seasons'][0].update(start='2026-04-01',end='2026-08-31',cutoff='2026-10-13',confirmed=True)
 for sc in s['schemes']:sc.update(states=['Gujarat','Rajasthan'],confirmed=True,abs_start='2026-01-01',abs_end='2026-03-31')
 return s

def example(sid='scheme-3',sup='400',ret='40',abs_amount='30000',payments=None):
 s=configured();sc=next(x for x in s['schemes'] if x['id']==sid);pid=sc['products'][0]
 bill=D(sc['billing'])/(D(sc['packing_kg']) if sc['billing_unit']=='packet' and sc['unit']=='kg' else 1)
 entries=[{'id':'sale','date':'2026-04-20','kind':'sale','debit':str((D(sup)*bill).quantize(D('0.01'))),'credit':'0','reference':'S1','reviewed':True,'items':[{'name':'Test','product':pid,'qty':sup,'unit':sc['unit'],'rate':str(bill),'amount':str((D(sup)*bill).quantize(D('0.01')))}]}]
 if D(ret):entries.append({'id':'return','date':'2026-08-20','kind':'return','debit':'0','credit':str((D(ret)*bill).quantize(D('0.01'))),'reviewed':True,'items':[{'name':'Test','product':pid,'qty':ret,'unit':sc['unit'],'rate':str(bill),'amount':str((D(ret)*bill).quantize(D('0.01')))}]})
 allocations=[]
 if D(abs_amount):
  entries.append({'id':'advance','date':'2026-03-20','kind':'receipt','debit':'0','credit':abs_amount,'reviewed':True});allocations.append({'id':'aa','source':'advance','scheme':sid,'product':pid,'type':'ABS','amount':abs_amount})
 for i,(dt,amt) in enumerate(payments or [('2026-06-20','30000'),('2026-07-10','30000')]):
  eid='receipt'+str(i);entries.append({'id':eid,'date':dt,'kind':'receipt','debit':'0','credit':amt,'reviewed':True});allocations.append({'id':'allocation'+str(i),'source':eid,'scheme':sid,'type':'CD','amount':amt})
 closing=sum((D(e['debit'])-D(e['credit']) for e in entries),Decimal(0))
 r={'party':'Test Party','state':'Rajasthan','location':'Town','season':'2026 season 1','opening':'0','closing':str(closing),'old_dues':'0','ledger_confirmed':True,'entries':entries,'allocations':allocations,'opening_sources':[],'cash_splits':[]}
 return r,s

class ArithmeticTests(unittest.TestCase):
 def test_corrected_bajra_cap(self):
  r,s=example();o=compute(r,s)
  self.assertEqual(o['issues'],[]);self.assertEqual(o['new_CN_total'],D(38561));self.assertEqual(o['excess_credit'],D(32561));self.assertEqual(o['groups'][0]['pre_CD'],D(42200))
  cn={c['benefit']:c for c in o['CNs']};self.assertEqual(cn['Extra']['rounded'],D(25000));self.assertEqual(cn['CD']['rounded'],D(2761))
 def test_saini_regression_synthetic_dates(self):
  # Dates here are representative test dates within confirmed windows, NOT claimed Saini receipt dates.
  r,s=example(sup='2951.25',ret='1038.75',abs_amount='0',payments=[('2026-06-10','100000'),('2026-06-20','100000'),('2026-08-10','60000'),('2026-09-10','30000')])
  r.update(party='Saini reference arithmetic',opening='49565',old_dues='49565',closing='279265')
  r['entries'].append({'id':'other','date':'2026-05-20','kind':'adjustment','debit':'9700','credit':'0','reviewed':True,'remarks':'Other crops net control'})
  r['allocations'][0]['amount']='50435';r['allocations'][-1]['type']='Settlement'
  o=compute(r,s);self.assertEqual(o['issues'],[]);self.assertEqual(o['ledger_computed'],D(279265));self.assertEqual(o['new_CN_total'],D(136730));self.assertEqual(o['party_owes'],D(142535));self.assertEqual(next(c['precise'] for c in o['CNs'] if c['benefit']=='CD'),D('10530.45'))
 def test_deluxe_inclusive_returns_and_rounding(self):
  r,s=example('scheme-2','1000','100','200000',[('2026-06-10','200000'),('2026-07-01','100000')]);o=compute(r,s)
  # All ABS belongs to same product here: eligible 800, no excess.
  self.assertEqual(o['issues'],[]);self.assertEqual(next(c['rounded'] for c in o['CNs'] if c['benefit']=='Return'),D(9000))
  self.assertEqual(rounded(D('100.5')),D(101));self.assertEqual(sum(rounded(D(x)) for x in ['10.4','10.4','10.4']),D(30))
 def test_zero_sales_no_extra(self):
  r,s=example('scheme-2','0','0','0',[]);r['entries']=[];r['allocations']=[];r['closing']='0';o=compute(r,s);self.assertEqual(o['new_CN_total'],D(0))
 def test_product_wise_no_automatic_abs(self):
  r,s=example('scheme-4','1000','0','75000',[('2026-06-10','200000'),('2026-06-20','300000')]);pid=s['schemes'][3]['products'][1]
  r['entries'][0]['debit']='525000';r['entries'][0]['items'].append({'name':'Legend','product':pid,'qty':'500','unit':'kg','amount':'175000'});r['closing']='-50000'
  o=compute(r,s);self.assertEqual(o['issues'],[]);self.assertEqual(o['new_CN_total'],D(93287));self.assertEqual(o['excess_credit'],D(143287));self.assertEqual(o['groups'][0]['used_token_principal'],D(50000))
 def test_doublecross(self):
  r,s=example('scheme-5','2000','100','100000',[('2026-06-20','50000')]);o=compute(r,s);self.assertEqual(o['issues'],[]);self.assertEqual(o['new_CN_total'],D(63880));self.assertEqual(o['party_owes'],D(52120))
 def test_purnima(self):
  r,s=example('scheme-6','2000','100','100000',[('2026-06-20','50000')]);o=compute(r,s);self.assertEqual(o['issues'],[]);self.assertEqual(o['new_CN_total'],D(63880));self.assertEqual(o['party_owes'],D(90120))
 def test_dawat_separate(self):
  for sid in ['scheme-7','scheme-8']:
   r,s=example(sid,'700','70','70000',[('2026-06-10','50000'),('2026-07-01','40000')]);o=compute(r,s);self.assertEqual(o['issues'],[]);self.assertEqual(o['excess_credit'],D(5298));self.assertNotIn('Extra',[c['benefit'] for c in o['CNs']])
  self.assertNotEqual(s['schemes'][6]['products'],s['schemes'][7]['products'])
 def test_quantity_boundary_and_highest_continuation(self):
  rows=initial_settings()['schemes'][2]['quantity']
  for qty,rate in [('330','16'),('330.001','20'),('630','20'),('630.01','25'),('1650','27'),('1650.1','32'),('100000','32')]:self.assertEqual(slab_cn(D(qty),rows,'whole'),D(qty)*D(rate))
  self.assertEqual(slab_cn(D(0),rows,'whole'),D(0))
 def test_cash_split_and_deduction(self):
  r,s=example('scheme-5','10000','500','0',[]);r['entries']=[e for e in r['entries'] if e['kind']!='receipt'];r['allocations']=[]
  r['entries'].append({'id':'cashreceipt','date':'2026-03-20','kind':'receipt','debit':'0','credit':'300000','reviewed':True});r['allocations']=[{'id':'cashallocation','source':'cashreceipt','scheme':'scheme-5','product':s['schemes'][4]['products'][0],'type':'Cash','amount':'300000'}]
  r['cash_splits']=[{'scheme':'scheme-5','product':s['schemes'][4]['products'][0],'supplied':'3000','returned':'100','deduction_rate':'30','remark':'Agreed additional return deduction'}];r['closing']='1030000';o=compute(r,s)
  self.assertEqual(o['issues'],[]);self.assertEqual(next(c['rounded'] for c in o['CNs'] if c['benefit'].startswith('Cash')),D(113000));self.assertEqual(o['groups'][0]['net'],D(6600));self.assertEqual(o['product_CNs'][0]['net_sold'],D(9500));self.assertEqual(next(b['CN'] for b in o['product_CNs'][0]['benefits'] if b['benefit'].startswith('Cash')),D(113000));self.assertEqual(o['product_CNs'][0]['total_CN'],o['new_CN_total'])
  r['cash_splits'][0]['deduction_rate']=None;self.assertTrue(any('Resolve cash' in x for x in compute(r,s)['issues']))
 def test_payment_overallocation(self):
  r,s=example();r['allocations'][0]['amount']='30001';self.assertTrue(any('availability' in x for x in compute(r,s)['issues']))
 def test_original_dates_not_changed_by_allocation(self):
  r,s=example();r['allocations'][1]['date']='2026-01-01';a=compute(r,s);self.assertEqual(a['groups'][0]['CD_work'][1]['original_date'],'2026-06-20')
  e=next(e for e in r['entries'] if e['id']=='receipt0');e['original']=copy.deepcopy(e);e['date']='2026-01-01';e['correction_reason']='Edited';self.assertTrue(any('eligibility remains original' in x for x in compute(r,s)['issues']))
 def test_opening_credit_never_second_receipt(self):
  r,s=example(abs_amount='0',payments=[]);r['entries']=[e for e in r['entries'] if e['kind']!='receipt'];r['allocations']=[];r.update(opening='-30000',closing='66000',opening_sources=[{'id':'opening-credit','amount':'30000','date':None}]);r['allocations']=[{'id':'openingABS','source':'opening-credit','scheme':'scheme-3','product':s['schemes'][2]['products'][0],'type':'ABS','amount':'30000'}]
  o=compute(r,s);self.assertEqual(o['issues'],[]);self.assertEqual(o['ledger_computed'],D(66000));self.assertEqual(o['groups'][0]['excess_ABS'],D(12000))
 def test_missing_settings_blocks(self):
  r,s=example();s['schemes'][2]['abs_end']=None;self.assertFalse(compute(r,s)['can_finalise']);s['schemes'][2]['token']=None;self.assertFalse(compute(r,s)['can_finalise'])
 def test_unassigned_payment_blocks(self):
  r,s=example();r['allocations'].pop();self.assertTrue(any('Assign ordinary' in x for x in compute(r,s)['issues']))
 def test_fractional_packet_blocks(self):
  r,s=example('scheme-2','10.1','0','0',[]);self.assertTrue(any('Fractional packet' in x for x in compute(r,s)['issues']))
 def test_builder_compatibility_and_overlaps(self):
  s=configured()['schemes'][2];s['benefits'].append('Net');self.assertTrue(any('cannot combine' in x for x in validate_scheme(s)))
  s['benefits'].remove('Net');s['cd'][1]['start']=s['cd'][0]['end'];self.assertTrue(any('Overlapping' in x for x in validate_scheme(s)))
 def test_singlecross_decimal_extra_boundary(self):
  rows=initial_settings()['schemes'][3]['extra']
  self.assertEqual(tier(D('2999.99'),rows)['rate'],'25000')
  self.assertEqual(tier(D('3000'),rows)['rate'],'50000')
 def test_cd_date_boundaries(self):
  for sid,dates in [('scheme-2',[('2026-06-15',8),('2026-06-16',4),('2026-07-15',4),('2026-07-16',2),('2026-07-30',2),('2026-07-31',0)]),('scheme-5',[('2026-06-15',12),('2026-06-16',8),('2026-06-30',8),('2026-07-01',5),('2026-07-15',5),('2026-07-16',2),('2026-07-31',0)]),('scheme-3',[('2026-06-30',7),('2026-07-01',5),('2026-07-15',5),('2026-07-16',3),('2026-07-31',3),('2026-08-01',0)])]:
   for dt,pct in dates:
    r,s=example(sid,'2000','0','0',[(dt,'100')]);o=compute(r,s)
    self.assertEqual(o['issues'],[])
    self.assertEqual(next(c['precise'] for c in o['CNs'] if c['benefit']=='CD'),D(pct))
 def test_manual_order_preserved(self):
  r,s=example();r['manual_order']=True;r['allocations'][1]['order']=2;r['allocations'][2]['order']=1
  o=compute(r,s);self.assertEqual(o['groups'][0]['CD_work'][1]['original_date'],'2026-07-10')
 def test_cash_supply_requirement_and_zero_floor(self):
  r,s=example('scheme-5','3000','100','0',[]);r['entries']=[e for e in r['entries'] if e['kind']!='receipt'];pid=s['schemes'][4]['products'][0]
  r['entries'].append({'id':'cashreceipt','date':'2026-03-20','kind':'receipt','debit':'0','credit':'290000','reviewed':True})
  r['allocations']=[{'id':'cash','source':'cashreceipt','scheme':'scheme-5','product':pid,'type':'Cash','amount':'290000'}]
  r['cash_splits']=[{'scheme':'scheme-5','product':pid,'supplied':'3000','returned':'100','deduction_rate':'2000','remark':'Review excess'}];r['closing']='116000'
  o=compute(r,s);self.assertTrue(any('supplied quantity' in x for x in o['issues']));self.assertTrue(any('exceeds CN' in x for x in o['issues']));self.assertEqual(next(c['rounded'] for c in o['CNs'] if c['benefit'].startswith('Cash')),D(0))
 def test_selected_custom_scheme_receives_same_original_sources(self):
  r,s=example();sc=copy.deepcopy(s['schemes'][2]);sc['id']='custom-bajra';sc['name']='My Saved Test Scheme';s['schemes'].append(sc)
  source_before=copy.deepcopy(r['entries']);r['scheme_overrides']={'scheme-3':'custom-bajra'}
  for a in r['allocations']:a['scheme']='custom-bajra'
  o=compute(r,s);self.assertEqual(o['issues'],[]);self.assertEqual(o['new_CN_total'],D(38561));self.assertEqual(o['groups'][0]['scheme'],'custom-bajra');self.assertEqual(r['entries'],source_before)
 def test_progressive_custom_scheme(self):
  self.assertEqual(slab_cn(D(250),[{'above':'0','upto':'100','rate':'2'},{'above':'100','upto':'200','rate':'3'}],'progressive'),D(650))

class ImportTests(unittest.TestCase):
 def setUp(self):self.s=initial_settings();self.i=import_pdf((ROOT/'fixtures/ashapura.pdf').read_bytes(),self.s)
 def test_reconciliation(self):
  self.assertTrue(self.i['reconciled']);self.assertEqual(self.i['opening'],'89909.00');self.assertEqual(self.i['closing'],'2184524.00');self.assertEqual(len(self.i['entries']),13)
  es=self.i['entries'];self.assertEqual(sum(D(e['debit']) for e in es),D(4332150));self.assertEqual(sum(D(e['credit']) for e in es if e['kind']=='return'),D(1922910));self.assertEqual(sum(D(e['credit']) for e in es if e['kind']=='posted_cn'),D(2000));self.assertEqual(next(e['date'] for e in es if e['kind']=='receipt'),'2026-04-08')
 def test_cotton_totals_and_original_lines(self):
  expect={'Advance':(1500,1313),'Agniveer':(2525,555),'D551':(375,53),'Dhanvarsha':(250,189)};products={p['id']:p for p in self.s['products']}
  for name,(sup,ret) in expect.items():
   actual=[sum(D(i['qty']) for e in self.i['entries'] if e['kind']==kind for i in e['items'] if i['product'] and products[i['product']]['name']==name) for kind in ['sale','return']]
   self.assertEqual(actual,[D(sup),D(ret)])
  self.assertEqual(len({i['name'] for e in self.i['entries'] for i in e['items']}),8)
  self.assertTrue(all('original' in e and e['source_lines'] for e in self.i['entries']))
 def test_duplicate_and_changed_import(self):
  compare=compare_import(self.i['entries'],self.i['entries']);self.assertTrue(all(c['status']=='Already imported' for c in compare))
  inc=copy.deepcopy(self.i['entries']);inc[0]['original']['credit']='199999';self.assertEqual(compare_import(self.i['entries'],inc)[0]['status'],'Changed')
 def test_malformed_pdf_rejected(self):
  with self.assertRaises(ValueError):import_pdf(b'not a PDF',self.s)
 def test_import_draft_blocks_until_review(self):
  r={**self.i,'season':'2026 season 1','old_dues':'89909','allocations':[],'cash_splits':[],'opening_sources':[],'ledger_confirmed':False};o=compute(r,self.s);self.assertFalse(o['can_finalise']);self.assertEqual(o['ledger_computed'],D(2184524))

class PersistenceTests(unittest.TestCase):
 def setUp(self):self.tmp=tempfile.TemporaryDirectory();self.store=Store(Path(self.tmp.name)/'test.sqlite');self.r,self.s=example();self.store.save_settings(self.s)
 def tearDown(self):self.tmp.cleanup()
 def test_save_reopen_and_stale_write(self):
  r=self.store.save(self.r);other=Store(self.store.path);self.assertEqual(other.get(r['id']),r)
  new=self.store.save(r)
  with self.assertRaises(ValueError):self.store.save(r)
  self.assertEqual(new['revision'],2)
 def test_finalise_freeze_issue_duplicate_revision(self):
  r=self.store.save(self.r);f=self.store.finalise(r['id'],r['revision']);self.assertEqual(f['status'],'finalised')
  changed=self.store.settings();changed['schemes'][2]['extra'][1]['rate']='26000';self.store.save_settings(changed);self.assertEqual(D(self.store.calculate(f)['new_CN_total']),D(38561))
  with self.assertRaises(ValueError):self.store.save(f)
  issued=self.store.issue(f['id'],f['revision']);self.assertEqual(issued['status'],'issued')
  with self.assertRaises(ValueError):self.store.issue(f['id'],f['revision'])
  duplicate=self.store.save(self.r);df=self.store.finalise(duplicate['id'],duplicate['revision'])
  with self.assertRaises(ValueError):self.store.issue(df['id'],df['revision'])
  rev=self.store.revise(issued['id']);result=self.store.calculate(rev);self.assertEqual(result['new_CN_total'],D(934));self.assertTrue(any('Revision requires' in x for x in result['issues']))
 def test_guarded_finalise(self):
  r=copy.deepcopy(self.r);r['ledger_confirmed']=False;r=self.store.save(r)
  with self.assertRaises(ValueError):self.store.finalise(r['id'],r['revision'])
 def test_source_original_immutable(self):
  r=copy.deepcopy(self.r);r['entries'][0]['original']=copy.deepcopy(r['entries'][0]);r=self.store.save(r);orig=copy.deepcopy(r['entries'][0]['original']);r['entries'][0]['original']['debit']='1';r=self.store.save(r);self.assertEqual(r['entries'][0]['original'],orig)
  r['entries'].pop(0)
  with self.assertRaises(ValueError):self.store.save(r)
 def test_backup_restore_with_safety_copy(self):
  saved=self.store.save(self.r);b=self.store.backup();self.assertEqual(self.store.restore(b)['records'],1);self.store.restore(b,True);self.assertEqual(self.store.get(saved['id']),saved);self.assertTrue(Path(self.store.path+'.before-restore.json').exists())
 def test_revision_negative_adjustment_blocks(self):
  r=self.store.save(self.r);f=self.store.finalise(r['id'],r['revision']);i=self.store.issue(f['id'],f['revision']);rev=self.store.revise(i['id']);s=self.store.settings();s['schemes'][2]['extra'][1]['rate']='20000';self.store.save_settings(s);self.assertTrue(any('Negative revised' in x for x in self.store.calculate(rev)['issues']))

if __name__=='__main__':unittest.main(verbosity=2)
