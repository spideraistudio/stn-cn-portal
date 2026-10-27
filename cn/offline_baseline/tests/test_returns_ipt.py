import unittest,copy,tempfile
from pathlib import Path
from decimal import Decimal
from test_calculator import ROOT,configured,D
from importer import import_pdf,parse_statement_pages,compare_import
from engine import compute
from store import Store

class StatementReturnTests(unittest.TestCase):
 def setUp(self):self.s=configured();self.i=import_pdf((ROOT/'fixtures/maharashtra.pdf').read_bytes(),self.s)
 def test_real_statement_returns_journals_and_balance(self):
  self.assertTrue(self.i['reconciled']);self.assertEqual(len(self.i['entries']),12);self.assertEqual(self.i['opening'],'-552875.00');self.assertEqual(self.i['closing'],'602385.00');self.assertEqual(self.i['state'],'Maharashtra')
  returns=[e for e in self.i['entries'] if e['kind']=='return'];self.assertEqual(len(returns),1);self.assertEqual(returns[0]['date'],'2026-09-01');self.assertEqual(len(returns[0]['items']),6);self.assertEqual(returns[0]['credit'],'820840.00')
  journals=[e for e in self.i['entries'] if e.get('posting_label')];self.assertEqual(sum(D(e['credit']) for e in journals),D(11900));self.assertTrue(all(e['kind']=='posted_cn' and not e['classification_required'] for e in journals))
 def test_real_product_packet_nets(self):
  expected={'Ranbanka':(120,60,60),'32D12':(500,416,84),'32D55':(1700,0,1700),'14D88':(100,14,86),'27D27':(300,186,114),'Janki Ratna':(300,38,262),'Mandhata':(300,289,11)}
  for name,(supply,ret,net) in expected.items():
   totals=[sum(D(i['qty']) for e in self.i['entries'] if e['kind']==kind for i in e.get('items',[]) if name in i['name']) for kind in ('sale','return')];self.assertEqual(totals,[D(supply),D(ret)]);self.assertEqual(totals[0]-totals[1],D(net))
 def test_reparse_same_saved_text_not_double_import(self):
  fresh=parse_statement_pages([self.i['source']['text']],self.s,self.i['source']);self.assertTrue(all(x['status']=='Already imported' for x in compare_import(self.i['entries'],fresh['entries'])));self.assertEqual(fresh['source'],self.i['source'])
 def test_old_missing_return_classification_matches_same_id_for_repair(self):
  old=copy.deepcopy(self.i['entries']);ret=next(e for e in old if e['kind']=='return');ret['kind']='posted_cn';ret['items']=[];ret['original']=copy.deepcopy({k:v for k,v in ret.items() if k!='original'});out=compare_import(old,self.i['entries']);entry=next(x for x in out if x['incoming']['id']==ret['id']);self.assertEqual(entry['status'],'Changed');self.assertEqual(len(entry['incoming']['items']),6)
 def test_accepted_parser_correction_keeps_first_original_and_new_baseline(self):
  old=copy.deepcopy(self.i['entries']);ret=next(e for e in old if e['kind']=='return');first=copy.deepcopy(ret['original']);first['kind']='posted_cn';first['items']=[];ret['original']=first;ret['latest_import_source']=copy.deepcopy(next(e for e in self.i['entries'] if e['id']==ret['id'])['original']);ret['kind']='ipt_out'
  self.assertTrue(all(x['status']=='Already imported' for x in compare_import(old,self.i['entries'])));self.assertEqual(ret['original']['items'],[])
 def test_zero_start_balance_does_not_replace_reference_with_amount(self):
  text='Ledger Statement\nFor 01-Apr-26 to 30-Sep-26\nTest Party\nMarket, Gujarat\nDate Particulars\n01-Apr-26 Opening Balance 0.00\n01-Apr-26 Sales Invoice Gujarat-Invoice INV-01 100.00 100.00\nTest 1kg 1.00 pkt @ 100.00 100.00\nClosing Balance Rs. 100.00'
  x=parse_statement_pages([text],self.s);self.assertEqual(x['entries'][0]['reference'],'INV-01');self.assertTrue(x['entries'][0]['legacy_ids'])
 def test_september_return_not_silently_dropped_from_august_season(self):
  r={**self.i,'season':'2026 season 1','old_dues':'0','allocations':[],'cash_splits':[],'opening_sources':[]};o=compute(r,self.s);self.assertEqual(o['ledger_computed'],D(602385));self.assertTrue(any('outside selected season' in x for x in o['issues']));self.assertFalse(o['can_finalise'])

def ipt_example(incoming='0',outgoing='0',returned='20'):
 s=configured();sc=s['schemes'][0];sc.update(billing='100',benefits=['Quantity'],quantity=[{'above':'0','upto':'100','rate':'1'},{'above':'100','upto':None,'rate':'2'}]);pid=sc['products'][0]
 def entry(id,kind,qty,debit,credit):return {'id':id,'reference':id,'date':'2026-05-01','kind':kind,'debit':str(debit),'credit':str(credit),'reviewed':True,'items':[{'name':'Stock','product':pid,'qty':str(qty),'unit':'packet','rate':'100','amount':str(abs(D(debit)-D(credit)))}]}
 entries=[entry('sale','sale','100','10000','0')]
 if D(incoming):entries.append(entry('in','ipt_in',incoming,str(D(incoming)*100),'0'))
 if D(outgoing):entries.append(entry('out','ipt_out',outgoing,'0',str(D(outgoing)*100)))
 if D(returned):entries.append(entry('ret','return',returned,'0',str(D(returned)*100)))
 closing=sum(D(e['debit'])-D(e['credit']) for e in entries)
 r={'party':'Synthetic IPT','state':'Gujarat','season':'2026 season 1','opening':'0','closing':str(closing),'old_dues':'0','ledger_confirmed':True,'entries':entries,'allocations':[],'cash_splits':[],'opening_sources':[]}
 return r,s

class IPTTests(unittest.TestCase):
 def test_received_adds_supply_and_qualifying_tier(self):
  r,s=ipt_example(incoming='50',returned='20');o=compute(r,s);self.assertEqual(o['issues'],[]);g=o['groups'][0];self.assertEqual(g['supplied'],D(150));self.assertEqual(g['returned'],D(20));self.assertEqual(g['net'],D(130));self.assertEqual(g['ipt_received'],D(50));self.assertEqual(o['new_CN_total'],D(260))
 def test_given_deducts_supply_not_counted_as_return(self):
  r,s=ipt_example(outgoing='30',returned='20');o=compute(r,s);self.assertEqual(o['issues'],[]);g=o['groups'][0];self.assertEqual(g['supplied'],D(70));self.assertEqual(g['returned'],D(20));self.assertEqual(g['net'],D(50));self.assertEqual(g['ipt_given'],D(30));self.assertEqual(o['new_CN_total'],D(50));self.assertEqual(o['ledger_computed'],D(5000))
 def test_both_directions_return_bonus_uses_adjusted_supply(self):
  r,s=ipt_example(incoming='50',outgoing='30',returned='12');sc=s['schemes'][0];sc.update(benefits=['Quantity','Return'],return_threshold='10',return_rate='1',return_unit='packet');o=compute(r,s);self.assertEqual(o['issues'],[]);self.assertEqual(o['groups'][0]['supplied'],D(120));self.assertEqual(o['groups'][0]['net'],D(108));self.assertEqual(next(c['rounded'] for c in o['CNs'] if c['benefit']=='Return'),D(108))
 def test_excess_transfer_out_or_returns_block_finish(self):
  for incoming,outgoing,ret in [('0','110','0'),('0','30','80')]:
   r,s=ipt_example(incoming,outgoing,ret);self.assertFalse(compute(r,s)['can_finalise'])
 def test_stock_transfer_does_not_become_receipt(self):
  r,s=ipt_example(incoming='50',outgoing='30');o=compute(r,s);self.assertEqual(o['sources'],[]);self.assertEqual(o['unallocated'],D(0))
 def test_manual_delete_preserves_original_snapshot_and_amounts(self):
  r,s=ipt_example();e=r['entries'][0];e['original']=copy.deepcopy(e);e['source_lines']=[{'text':'Imported invoice'}];e['items'].append({'manual':True,'name':'Manual item','product':None,'qty':'0','unit':'kg','rate':'0','amount':'0'})
  with tempfile.TemporaryDirectory() as td:
   st=Store(Path(td)/'x.sqlite');st.save_settings(s);saved=st.save(r);original=copy.deepcopy(saved['entries'][0]['original']);saved['entries'][0]['items'].pop();saved['entries'][0]['correction_reason']='Removed manual row';updated=st.save(saved);self.assertEqual(updated['entries'][0]['original'],original);self.assertEqual(updated['entries'][0]['debit'],'10000')

 def test_incomplete_scheme_still_reports_unallocated_receipt(self):
  r,s=ipt_example(returned='0');s['schemes'][0]['quantity'][0]['rate']='unfinished'
  r['entries'].append({'id':'payment','date':'2026-07-13','kind':'receipt','debit':'0','credit':'100000','reviewed':True,'items':[]});r['closing']='-90000'
  o=compute(r,s);self.assertFalse(o['can_finalise']);self.assertEqual(o['unallocated'],D(100000));self.assertEqual(o['sources'][0]['date'],'2026-07-13');self.assertEqual(o['ledger_computed'],D(-90000));self.assertEqual(o['new_CN_total'],D(0))
