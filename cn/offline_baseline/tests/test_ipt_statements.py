import copy,tempfile,unittest
from pathlib import Path
from test_calculator import ROOT,configured,example,D
from importer import import_pdf,compare_import,parse_statement_pages
from engine import compute
from store import Store

class ActualIPTStatements(unittest.TestCase):
 def setUp(self):
  self.s=configured();self.docs={name:import_pdf((ROOT/'fixtures'/name).read_bytes(),self.s) for name in ('ashapura_ipt.pdf','krishna_ipt.pdf')}
 def cotton(self,doc,kind):return sum((D(i['qty']) for e in doc['entries'] if e['kind']==kind for i in e['items'] if i['name'].startswith('Cotton')),D(0))
 def test_actual_directions_parties_and_125_packet_pair(self):
  a=self.docs['ashapura_ipt.pdf'];k=self.docs['krishna_ipt.pdf']
  out=next(e for e in a['entries'] if e['reference']=='GJ/SRN/26-27/0223');inc=next(e for e in k['entries'] if e['reference']=='GJ/26-27/1049')
  self.assertEqual((out['kind'],inc['kind']),('ipt_out','ipt_in'));self.assertEqual(out['transfer_party'],'KRISHNA TRADING CO, WADHVAN');self.assertEqual(inc['transfer_party'],'ASHAPURA SEEDS, CHUDA')
  self.assertEqual(out['items'][0]['qty'],inc['items'][0]['qty']);self.assertEqual(out['credit'],inc['debit']);self.assertEqual(inc['items'][0]['qty'],'125.00');self.assertFalse(out['classification_required']);self.assertFalse(inc['classification_required'])
 def test_stock_columns_no_double_count_and_real_returns_separate(self):
  for name,expected in [('ashapura_ipt.pdf',(4650,0,125,4525,2110,2415)),('krishna_ipt.pdf',(3250,175,10,3415,1505,1910))]:
   doc=self.docs[name];supply,inc,out,ret=[self.cotton(doc,k) for k in ('sale','ipt_in','ipt_out','return')];self.assertEqual((supply,inc,out,supply+inc-out,ret,supply+inc-out-ret),tuple(D(v) for v in expected))
   self.assertEqual(len({e['id'] for e in doc['entries']}),len(doc['entries']));self.assertEqual(sum(1 for e in doc['entries'] if e['date']=='2026-08-14' and e['kind']=='ipt_in'),2 if name.startswith('krishna') else 0)
 def test_ledgers_receipts_and_parser_money_stay_original(self):
  for name,closing in [('ashapura_ipt.pdf',2184524),('krishna_ipt.pdf',1683058)]:
   d=self.docs[name];self.assertTrue(d['reconciled']);self.assertEqual(D(d['closing']),D(closing));self.assertFalse(any('Incomplete' in w or 'balance mismatch' in w for w in d['warnings']))
   r={**d,'state':'Gujarat','season':'2026 season 1','allocations':[],'old_dues':'0','opening_sources':[],'cash_splits':[],'ledger_confirmed':True};o=compute(r,self.s);self.assertEqual(o['ledger_computed'],D(closing))
   self.assertEqual(len(o['sources']),0 if name.startswith('krishna') else 1)
   if o['sources']:self.assertEqual(o['sources'][0]['date'],'2026-04-08');self.assertEqual(o['sources'][0]['amount'],D(200000))
 def test_re_read_old_classifications_replaces_same_ids_and_preserves_snapshot(self):
  for doc in self.docs.values():
   old=copy.deepcopy(doc['entries'])
   for e in old:
    if e['kind'].startswith('ipt_'):e['kind']=e['original']['kind']='sale' if e['kind']=='ipt_in' else 'return'
   first={e['id']:copy.deepcopy(e['original']) for e in old};comp=compare_import(old,doc['entries']);changed=[c for c in comp if c['status']=='Changed'];self.assertEqual(len(changed),3 if doc['party'].startswith('Krishna') else 1);self.assertFalse(any(c['status']=='New' for c in comp))
   for c in changed:
    pos=next(i for i,e in enumerate(old) if e['id']==c['incoming']['id']);old[pos]={**copy.deepcopy(c['incoming']),'original':first[c['incoming']['id']],'latest_import_source':copy.deepcopy(c['incoming']['original']),'correction_reason':'Accepted IPT narration detection'}
   self.assertEqual(len(old),len(doc['entries']));self.assertTrue(all(c['status']=='Already imported' for c in compare_import(old,doc['entries'])));self.assertTrue(all(e['original']==first[e['id']] for e in old))
 def test_engine_totals_match_columns_and_no_review_tick_blockers(self):
  for name in self.docs:
   d=self.docs[name];r={**copy.deepcopy(d),'state':'Gujarat','season':'2026 season 1','allocations':[],'old_dues':'0','opening_sources':[],'cash_splits':[],'ledger_confirmed':True};o=compute(r,self.s);cotton=[g for g in o['groups'] if g['crop']=='Cotton'];self.assertEqual(sum(g['invoice_supplied'] for g in cotton),self.cotton(d,'sale'));self.assertEqual(sum(g['ipt_received'] for g in cotton),self.cotton(d,'ipt_in'));self.assertEqual(sum(g['ipt_given'] for g in cotton),self.cotton(d,'ipt_out'));self.assertEqual(sum(g['returned'] for g in cotton),self.cotton(d,'return'));self.assertFalse(any('Review ledger voucher' in i or 'Confirm suggested' in i for i in o['issues']))
 def test_routine_ticks_unnecessary_but_exceptions_still_block(self):
  r,s=example()
  for e in r['entries']:
   e['reviewed']=False
   for i in e.get('items',[]):i['mapping_confirmed']=False
  self.assertTrue(compute(r,s)['can_finalise']);r['entries'][0]['classification_required']=True;self.assertFalse(compute(r,s)['can_finalise']);r['entries'][0]['classification_required']=False;r['entries'][0]['items'][0]['product']=None;self.assertFalse(compute(r,s)['can_finalise'])
 def test_manual_snapshot_is_captured_on_single_summary_confirmation(self):
  r,s=example();r['entries'][0]['reviewed']=False
  with tempfile.TemporaryDirectory() as td:
   st=Store(Path(td)/'x.sqlite');st.save_settings(s);saved=st.save(r);self.assertEqual(saved['entries'][0]['original']['date'],r['entries'][0]['date']);original=copy.deepcopy(saved['entries'][0]['original']);saved['entries'][0]['items'][0]['qty']='401';saved['entries'][0]['correction_reason']='Documented quantity correction';saved=st.save(saved);self.assertEqual(saved['entries'][0]['original'],original)
 def test_received_spelling_and_ambiguous_direction(self):
  for wording in ['GOODS RECEIVED FROM A','GOODS RECIVED FROM A','IPT Received FROM A']:
   text='Ledger Statement\nFor 01-Apr-26 to 31-Aug-26\nParty\n01-Apr-26 Opening Balance 0.00\n14-Aug-26 Sales Invoice Gujarat-Invoice V1 100.00 100.00\n'+wording+'\nStock 1.00 pkt @ 100.00 100.00\nClosing Balance Rs. 100.00';e=parse_statement_pages([text],self.s)['entries'][0];self.assertEqual(e['kind'],'ipt_in')
  ambiguous=text.replace(wording,'GOODS RECEIVED FROM A\nGOODS DISPATCH TO B');e=parse_statement_pages([ambiguous],self.s)['entries'][0];self.assertEqual(e['kind'],'unknown');self.assertTrue(e['classification_required'])
