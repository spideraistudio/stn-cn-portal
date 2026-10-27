import unittest,copy,tempfile
from pathlib import Path
from test_calculator import configured,D
from engine import compute,validate_scheme,effective_settings
from importer import extract_party_details
from store import Store

def fixed_example(scheme_unit='packet',cn_unit='packet',returned='0'):
 s=configured();sc=s['schemes'][0];pid=sc['products'][0];sc.update(benefits=['Net'],unit=scheme_unit,billing='150',billing_unit='packet',net_mode='fixed',net_cn_rate='20',net_cn_unit=cn_unit,net=[])
 qty='100';entries=[{'id':'sale-fixed','date':'2026-05-01','kind':'sale','debit':'15000','credit':'0','reviewed':True,'items':[{'name':'Test product','product':pid,'qty':qty,'unit':'packet','rate':'150','amount':'15000'}]}]
 if D(returned):entries.append({'id':'return-fixed','date':'2026-06-01','kind':'return','debit':'0','credit':str(D(returned)*150),'reviewed':True,'items':[{'name':'Test product','product':pid,'qty':returned,'unit':'packet','rate':'150','amount':str(D(returned)*150)}]})
 r={'party':'Synthetic fixed CN','state':'Gujarat','season':s['seasons'][0]['name'],'opening':'0','closing':str(D('15000')-D(returned)*150),'old_dues':'0','ledger_confirmed':True,'entries':entries,'allocations':[],'cash_splits':[],'opening_sources':[]}
 return r,s,pid

class FlexibleImportTests(unittest.TestCase):
 def test_redgram_example_fixed_twenty_per_packet(self):
  r,s,pid=fixed_example();s['schemes'][0]['crop']='Redgram';s['products'][0].update(crop='Redgram',name='27D27');o=compute(r,s)
  self.assertEqual(o['issues'],[]);self.assertEqual(o['new_CN_total'],D(2000));self.assertEqual(o['final_balance'],D(13000));self.assertEqual(o['CNs'][0]['working']['net_quantity'],D(100))
 def test_fixed_net_sold_returns_and_zero(self):
  r,s,_=fixed_example(returned='20');self.assertEqual(compute(r,s)['new_CN_total'],D(1600))
  r,s,_=fixed_example(returned='100');self.assertEqual(compute(r,s)['new_CN_total'],D(0))
 def test_fixed_packet_cn_with_scheme_in_kg(self):
  r,s,_=fixed_example(scheme_unit='kg');o=compute(r,s);self.assertEqual(o['issues'],[]);self.assertEqual(o['new_CN_total'],D(2000))
  s['schemes'][0]['net_cn_unit']='kg';self.assertEqual(compute(r,s)['new_CN_total'],D(950))
 def test_fixed_zero_negative_missing_validation(self):
  r,s,_=fixed_example();sc=s['schemes'][0];self.assertEqual(validate_scheme(sc,True),[])
  sc['net_cn_rate']='0';self.assertEqual(compute(r,s)['new_CN_total'],D(0))
  for rate in (None,'-1'):
   sc['net_cn_rate']=rate;self.assertTrue(validate_scheme(sc,True));self.assertFalse(compute(r,s)['can_finalise'])
 def test_existing_net_price_still_uses_slabs(self):
  r,s,_=fixed_example();s['schemes'][0].pop('net_mode');s['schemes'][0]['net']=[{'above':'0','upto':None,'rate':'130'}];self.assertEqual(compute(r,s)['new_CN_total'],D(2000))
 def test_record_only_group_assignment_preserves_catalogue(self):
  r,s,pid=fixed_example();target=s['schemes'][1];target.update(benefits=['Net'],net_mode='fixed',net_cn_rate='20',net_cn_unit='packet',net=[],billing='150');r['product_assignments']={pid:target['id']};before=copy.deepcopy(s);o=compute(r,s)
  self.assertEqual(o['issues'],[]);self.assertEqual(o['groups'][0]['scheme'],target['id']);self.assertEqual(o['new_CN_total'],D(2000));self.assertEqual(s,before);self.assertEqual(s['products'][0]['scheme'],'scheme-1')
 def test_assignment_crop_or_packing_mismatch_rejected(self):
  r,s,pid=fixed_example();r['product_assignments']={pid:'scheme-3'}
  with self.assertRaisesRegex(ValueError,'crop and packing'):effective_settings(r,s)
  self.assertFalse(compute(r,s)['can_finalise']);self.assertEqual(compute(r,s)['new_CN_total'],D(0))
 def test_pending_product_requires_scheme(self):
  r,s,pid=fixed_example();s['products'][0]['needs_assignment']=True;o=compute(r,s);self.assertEqual(o['new_CN_total'],D(0));self.assertTrue(any('Choose a scheme/group' in x for x in o['issues']));r['product_assignments']={pid:'scheme-1'};self.assertEqual(compute(r,s)['issues'],[])
 def test_assignment_save_freeze_and_reopen(self):
  r,s,pid=fixed_example();target=s['schemes'][1];target.update(benefits=['Net'],net_mode='fixed',net_cn_rate='20',net_cn_unit='packet',net=[],billing='150');r['product_assignments']={pid:target['id']}
  with tempfile.TemporaryDirectory() as td:
   st=Store(Path(td)/'calc.sqlite');s['version']=st.settings()['version'];st.save_settings(s);saved=st.save(r);f=st.finalise(saved['id'],saved['revision']);self.assertEqual(st.get(f['id'])['product_assignments'],r['product_assignments']);self.assertEqual(D(st.calculate(st.get(f['id']))['new_CN_total']),D(2000))
 def test_group_change_does_not_reuse_old_abs_destination(self):
  from test_calculator import example
  r,s=example('scheme-2','100','0','25000',[('2026-06-01','1000')]);pid=s['schemes'][1]['products'][0];r['product_assignments']={pid:'scheme-1'};o=compute(r,s)
  self.assertTrue(any('payment destination' in i for i in o['issues']));self.assertFalse(o['can_finalise']);self.assertEqual(r['allocations'][0]['scheme'],'scheme-2');self.assertEqual(r['allocations'][0]['amount'],'25000')
 def test_party_address_uses_recipient_not_issuer(self):
  text='DHANLAXMI Gujarat\nLedger Statement\nFor 01-Apr-26 to 13-Oct-26\nOther Dealer, Jaipur\nMarket Road, Jaipur, Rajasthan, 302001\nPhone: 123\nDate Particulars\n'
  p=extract_party_details(text);self.assertEqual(p['party'],'Other Dealer, Jaipur');self.assertEqual(p['location'],'Jaipur');self.assertEqual(p['state'],'Rajasthan')
 def test_unknown_or_ambiguous_recipient_state_left_blank(self):
  prefix='Issuer Gujarat\nLedger Statement\nFor 01-Apr-26 to 13-Oct-26\nDealer\n'
  self.assertEqual(extract_party_details(prefix+'Unknown Road\nPhone: 123')['state'],'')
  self.assertEqual(extract_party_details(prefix+'Gujarat Rajasthan\nPhone: 123')['state'],'')
