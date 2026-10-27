import unittest,tempfile,copy,csv,io
from pathlib import Path
from decimal import Decimal as D
from reporting import product_rows,csv_text,report,BENEFITS
from store import Store
from workbooks import Workbooks
from test_calculator import example

class ReportingTests(unittest.TestCase):
 def sample(self):
  r,s=example();p=s['products'][0];sc=next(x for x in s['schemes'] if x['id']==p['scheme']);sc['billing']='901';sc['billing_unit']='packet'
  r.update(party='Example',season=sc['season'],status='finalised',entries=[{'id':'sale','kind':'sale','items':[{'product':p['id'],'qty':'120','unit':'packet'}]},{'id':'ret','kind':'return','items':[{'product':p['id'],'qty':'20','unit':'packet'}]}])
  row=dict(key=sc['id']+'|'+p['id'],scheme=sc['id'],scheme_name=sc['name'],product_id=p['id'],product=p['name'],crop=p['crop'],segment=sc['segment'],packing_kg='0.475',unit='packet',net_sold='100',net_packets='100',net_kg='47.5',total_CN='11500',CN_per_packet='115',CN_per_kg=str(D(11500)/D('47.5')),benefits=[dict(benefit=k,CN=str(v*100)) for k,v in zip(('ABS','Quantity','CD','Extra','Return'),(25,50,15,15,10))])
  return r,s,dict(issues=[],product_CNs=[row],stock_scope={'sale':True,'ret':True})
 def test_user_nrv_example_and_quantities(self):
  r,s,res=self.sample();rows=product_rows(r,res,s,{'id':'a','name':'Gujarat','state':'Gujarat'});x=rows[0]
  self.assertEqual(x['NRV_per_packet'],786);self.assertEqual(x['net_realisation'],78600);self.assertEqual(x['invoice_supply'],120);self.assertEqual(x['returns'],20);self.assertEqual(sum(x[b+' CN'] for b in BENEFITS),11500)
 def test_freight_and_requested_changes_not_deducted(self):
  r,s,res=self.sample();r['entries'].append({'id':'freight','kind':'posted_cn','credit':'5000','items':[]});res['product_CNs'][0]['request']={'delta':'999','requested_total':'12499'}
  before=copy.deepcopy((r,s,res));row=product_rows(r,res,s,{'name':'A'})[0]
  self.assertEqual(row['NRV_per_packet'],786);self.assertEqual(row['requested_delta_display_only'],999);self.assertEqual((r,s,res),before)
 def test_separate_units_and_zero_sales(self):
  r,s,res=self.sample();p=res['product_CNs'][0];p.update(net_sold='0',net_packets='0',net_kg='0',total_CN='0',CN_per_packet='0',CN_per_kg='0');row=product_rows(r,res,s,{'name':'A'})[0];self.assertIsNone(row['NRV_per_packet'])
 def test_missing_breakdown_and_unresolved_calculation_block(self):
  r,s,res=self.sample()
  with self.assertRaises(ValueError):product_rows(r,{},s,{})
  res['issues']=['Unmapped product']
  with self.assertRaises(ValueError):product_rows(r,res,s,{})
 def test_csv_bom_escaping_formula_and_full_precision(self):
  r,s,res=self.sample();r['party']='=HYPERLINK("bad")';r['location']='ગુજરાત, India';rows=product_rows(r,res,s,{'name':'Test'});text=csv_text(rows)
  self.assertTrue(text.startswith('\ufeff'));parsed=list(csv.DictReader(io.StringIO(text.lstrip('\ufeff'))));self.assertTrue(parsed[0]['party'].startswith("'="));self.assertEqual(parsed[0]['location'],'ગુજરાત, India');self.assertEqual(D(parsed[0]['NRV_per_packet']),786)
 def make_store(self):
  self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);st=Store(Path(self.tmp.name)/'a.sqlite3');r,s=example();st.save_settings(s);r=st.save(r);f=st.finalise(r['id'],r['revision']);return st,r,s,f
 def test_latest_completed_and_draft_revision_not_double_counted(self):
  st,r,s,f=self.make_store();books=Workbooks(st);before=books.backup();base=report(books);st.revise(f['id']);after=report(books);self.assertEqual(base['rows'],after['rows']);self.assertTrue(base['rows']);self.assertEqual(report(books,{'party':'No match'})['rows'],[])
  cfg=st.settings();cfg['schemes'][2]['billing']='999';st.save_settings(cfg);self.assertEqual(report(books)['rows'],base['rows'])
 def test_overlapping_lineages_excluded_and_no_mutation(self):
  st,r,s,f=self.make_store();second=copy.deepcopy(r);second.pop('id');second.pop('revision');second=st.save(second);st.finalise(second['id'],second['revision']);books=Workbooks(st);before=books.backup();out=report(books);self.assertFalse(out['rows']);self.assertTrue(any('Overlapping' in n for n in out['notes']));after=books.backup()
  before.pop('created_at',None);after.pop('created_at',None);before['legacy'].pop('created_at',None);after['legacy'].pop('created_at',None);self.assertEqual(before,after)
 def test_deleted_party_not_in_report(self):
  st,r,s,f=self.make_store();preview=st.party_action(f['id']);st.party_action(f['id'],confirm=True,expected=preview['expected']);self.assertFalse(report(Workbooks(st))['rows'])
 def test_weighted_nrv_uses_realisation_over_quantity(self):
  st,r,s,f=self.make_store();second=copy.deepcopy(r);second.pop('id');second.pop('revision');second['party']='Different Party';second=st.save(second);st.finalise(second['id'],second['revision']);out=report(Workbooks(st))
  for total in out['totals']:
   members=[x for x in out['rows'] if x['product']==total['product'] and x['crop']==total['crop']]
   self.assertEqual(total['NRV_per_packet'],sum(x['net_realisation'] for x in members)/sum(x['net_packets'] for x in members))

 def test_single_workbook_filter_resolves_cross_workbook_overlap(self):
  st,r,s,f=self.make_store();books=Workbooks(st);meta=books.create(dict(name='Other workbook',state='Gujarat',period=r['season'],start='2026-04-01',end='2026-08-31',cutoff='2026-10-13',mode='copy'),'legacy');other=books.get(meta['id']);other.save_settings(s);clone=copy.deepcopy(r);clone.pop('id');clone.pop('revision');saved=other.save(clone);other.finalise(saved['id'],saved['revision'])
  self.assertFalse(report(books)['rows']);self.assertTrue(report(books,{'workbook':'Other workbook'})['rows'])
