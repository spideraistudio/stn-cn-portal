"""Independent numerical oracles and adversarial boundaries for the core-rule audit."""
import copy,random,tempfile,unittest
from decimal import Decimal,localcontext,ROUND_HALF_UP
from pathlib import Path
from engine import compute,D,validate_scheme,validate_input_limits,unit_qty,slab_cn
from reporting import product_rows
from store import Store
from unittest.mock import patch
from test_calculator import example

class CoreRulesAuditTests(unittest.TestCase):
 def net_case(self,unit,billing_unit,pack,billing,net_rate,qty):
  r,s=example('scheme-4',sup=str(qty),ret='0',abs_amount='0',payments=[])
  r['entries']=[e for e in r['entries'] if e['kind']=='sale'];r['allocations']=[]
  sc=s['schemes'][3];sc.update(unit=unit,packing_kg=str(pack),billing=str(billing),billing_unit=billing_unit,benefits=['Net'],net=[dict(above='0',upto=None,rate=str(net_rate))])
  for p in s['products']:
   if p['scheme']==sc['id']:p['packing_kg']=str(pack)
  item=r['entries'][0]['items'][0];item.update(qty=str(qty),unit=unit)
  factor=(D(pack) if unit=='packet' else D(1))/(D(pack) if billing_unit=='packet' else D(1))
  invoice=D(qty)*D(billing)*factor;item['amount']=str(invoice);r['entries'][0]['debit']=str(invoice);r['closing']=str(invoice)
  return r,s,invoice-D(qty)*D(net_rate)
 def test_net_price_rate_units_both_directions(self):
  for args in [('kg','packet',4,400,80,40),('packet','kg',4,100,320,10),('packet','kg','0.475',1000,400,10),('kg','kg',4,100,80,40),('packet','packet',4,400,320,10)]:
   with self.subTest(args=args):
    r,s,expected=self.net_case(*args);before=copy.deepcopy((r,s));o=compute(r,s)
    self.assertEqual(o['issues'],[]);self.assertEqual(o['new_CN_total'],expected.quantize(D(1),rounding=ROUND_HALF_UP));self.assertEqual((r,s),before)
    row=product_rows(r,o,s,{})[0];self.assertEqual(row['net_realisation'],D(r['closing'])-o['new_CN_total'])
 def test_net_fixed_cn_stays_in_its_own_rate_unit(self):
  r,s,_=self.net_case('kg','packet',4,400,80,40);s['schemes'][3].update(net_mode='fixed',net_cn_rate='10',net_cn_unit='packet')
  o=compute(r,s);self.assertEqual(o['issues'],[]);self.assertEqual(o['new_CN_total'],100)
 def test_open_ended_overlap_is_rejected_for_every_slab_type(self):
  for key,benefit in [('quantity','Quantity'),('extra','Extra'),('net','Net')]:
   r,s=example();sc=s['schemes'][2];sc.update(benefits=[benefit]);sc[key]=[dict(above='0',upto=None,rate='10'),dict(above='20',upto='40',rate='20')]
   self.assertTrue(any('must be last' in e for e in validate_scheme(sc,True)))
   self.assertFalse(compute(r,s)['can_finalise'])
 def test_inclusive_extra_order_and_progressive_mode_validation(self):
  r,s=example();sc=s['schemes'][2];sc.update(benefits=['Extra'],extra=[dict(above='100',upto='300',rate='1000',inclusive=True),dict(above='100',upto=None,rate='2000',inclusive=True)])
  self.assertTrue(any('must increase' in e for e in validate_scheme(sc,True)))
  sc['extra'][1].update(above='301',inclusive=False);self.assertTrue(any('consistent' in e for e in validate_scheme(sc,True)))
  sc.update(benefits=['Quantity'],quantity_mode='typo');self.assertTrue(any('whole or progressive' in e for e in validate_scheme(sc,True)))
 def test_valid_progressive_and_highest_slab_continuation(self):
  rows=[dict(above='0',upto='100',rate='2'),dict(above='100',upto='200',rate='4')]
  for qty,expected in [(0,0),(100,200),(150,400),(200,600),(250,800)]:self.assertEqual(slab_cn(D(qty),rows,'progressive'),expected)
 def test_cash_configuration_and_save_rejection(self):
  for field,value in [('advance','0'),('advance','-100'),('cn_rate','-1'),('unit','box'),('end','2026-01-01'),('start',None),('products',[])]:
   with self.subTest(field=field):
    r,s=example('scheme-5',sup='100',ret='0',abs_amount='0',payments=[]);sc=s['schemes'][4];sc['cash'][field]=value
    self.assertTrue(validate_scheme(sc,True));self.assertFalse(compute(r,s)['can_finalise'])
    with tempfile.TemporaryDirectory() as td:
     st=Store(Path(td)/'test.sqlite3');before=st.settings()
     with self.assertRaises(ValueError):st.save_settings(s)
     self.assertEqual(st.settings(),before)
 def test_cash_packet_split_integrality_and_fractional_kg(self):
  r,s=example('scheme-5',sup='10',ret='0',abs_amount='0',payments=[]);sc=s['schemes'][4];sc['unit']='packet';r['entries'][0]['items'][0].update(unit='packet',qty='10')
  r['cash_splits']=[dict(scheme=sc['id'],product=sc['products'][0],supplied='0.5',returned='0',deduction_rate='0')]
  with self.assertRaisesRegex(ValueError,'whole packets'):validate_input_limits(r,s)
  self.assertEqual(compute(r,s)['CNs'],[])
  sc['unit']='kg';r['entries'][0]['items'][0].update(unit='kg',qty='10');validate_input_limits(r,s)
 def test_reporting_state_follows_calculation_precedence(self):
  r,s=example();r.update(state='Rajasthan',workbook_scheme_state='Rajasthan',scheme_state='Gujarat',override_reason='Explicit reviewed override')
  out=compute(r,s);self.assertEqual(out['issues'],[]);self.assertEqual(product_rows(r,out,s,{'state':'Rajasthan'})[0]['state'],'Gujarat')
 def test_randomized_cd_cap_against_independent_closed_form(self):
  rng=random.Random(251016)
  with localcontext() as ctx:
   ctx.prec=40
   for n in range(180):
    qty=D(rng.randint(1,5000));bill=D(rng.randint(50,500));pct=D(rng.randint(0,100));amount=D(rng.randint(0,2000000))/100
    r,s=example('scheme-4',sup=str(qty),ret='0',abs_amount='0',payments=[('2026-06-20',str(amount))]);sc=s['schemes'][3];sc.update(benefits=['CD'],billing=str(bill),billing_unit='kg',cd=[dict(start='2026-04-01',end='2026-12-31',percent=str(pct))])
    r['entries'][0]['items'][0]['amount']=r['entries'][0]['debit']=str(qty*bill);r['closing']=str(qty*bill-amount)
    expected=min(amount,qty*bill/(1+pct/100))*pct/100;out=compute(r,s)
    self.assertEqual(out['issues'],[]);self.assertEqual(out['new_CN_total'],expected.quantize(D(1),rounding=ROUND_HALF_UP));g=out['groups'][0];w=g['CD_work'][0]
    self.assertGreaterEqual(g['segment_balance'],0);self.assertLessEqual(w['eligible_payment']+w['CD'],g['pre_CD']);self.assertEqual(w['eligible_payment']+w['unused'],amount)
    self.assertEqual(out['final_balance'],D(r['closing'])-out['new_CN_total'])
 def test_randomized_abs_principal_excess_and_cn_conservation(self):
  rng=random.Random(251017)
  for n in range(180):
   sup=D(rng.randint(1,5000));ret=D(rng.randint(0,int(sup)));paid=D(rng.randint(1,400000))
   r,s=example('scheme-3',sup=str(sup),ret=str(ret),abs_amount=str(paid),payments=[]);r['entries']=[e for e in r['entries'] if not e['id'].startswith('receipt')];r['allocations']=[a for a in r['allocations'] if a['type']=='ABS'];r['closing']=str(sum((D(e['debit'])-D(e['credit']) for e in r['entries']),D(0)))
   out=compute(r,s);self.assertEqual(out['issues'],[]);g=out['groups'][0];w=next(c for c in out['CNs'] if c['benefit']=='ABS')['working'][0]
   self.assertEqual(w['principal']+w['excess'],paid);self.assertEqual(w['eligible'],min(sup-ret,paid/50));self.assertEqual(w['CN'],w['eligible']*10)
   self.assertEqual(sum(p['total_CN'] for p in out['product_CNs']),sum(c['rounded'] for c in out['CNs']))
   self.assertEqual(out['new_CN_total'],sum(c['precise'].quantize(D(1),rounding=ROUND_HALF_UP) for c in out['CNs']))
 def test_saved_frozen_results_are_preserved_after_settings_change(self):
  r,s=example()
  with tempfile.TemporaryDirectory() as td:
   st=Store(Path(td)/'test.sqlite3');st.save_settings(s);saved=st.save(r);frozen=st.finalise(saved['id'],saved['revision']);cfg=st.settings();cfg['schemes'][2]['quantity'][0]['rate']='123';st.save_settings(cfg)
   self.assertEqual(st.get(saved['id']),frozen);self.assertEqual(st.calculate(frozen),frozen['result'])

 def test_frozen_snapshot_is_authoritative_even_if_client_or_engine_changes(self):
  r,s=example()
  with tempfile.TemporaryDirectory() as td:
   st=Store(Path(td)/'test.sqlite3');st.save_settings(s);saved=st.save(r);frozen=st.finalise(saved['id'],saved['revision']);tampered=copy.deepcopy(frozen);tampered['result']['new_CN_total']='999999';tampered['entries']=[]
   with patch('store.compute',side_effect=AssertionError('Frozen record must not be recomputed')):
    self.assertEqual(st.calculate(tampered),frozen['result'])
   issued=st.issue(frozen['id'],frozen['revision'])
   with patch('store.compute',side_effect=AssertionError('Issued record must not be recomputed')):
    self.assertEqual(st.calculate(issued),issued['result'])
   revision=st.revise(issued['id'])
   with patch('store.compute',return_value={'revision_recomputed':True}) as engine:
    self.assertTrue(st.calculate(revision)['revision_recomputed']);engine.assert_called_once()
