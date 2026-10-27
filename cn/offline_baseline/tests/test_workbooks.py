import copy,tempfile,unittest,base64,hashlib,json
from pathlib import Path
from unittest.mock import patch
from test_calculator import ROOT,example,configured,D
from store import Store,dump
from workbooks import Workbooks,bulk_history,bulk_document,resolve_bulk
from engine import compute

class WorkbookTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.root=Store(Path(self.tmp.name)/'calculator.sqlite3');self.root.save_settings(configured());self.books=Workbooks(self.root)
 def tearDown(self):self.tmp.cleanup()
 def create(self,name='Gujarat workbook',**kw):return self.books.create({'name':name,'state':'Gujarat','period':'2026 season 1','start':'2026-04-01','end':'2026-08-31','cutoff':'2026-10-13',**kw})
 def payload(self,filename='ashapura_ipt.pdf',**kw):return {'filename':filename,'data':base64.b64encode((ROOT/'fixtures'/filename).read_bytes()).decode(),'season':'2026 season 1',**kw}
 def test_independent_scheme_and_record_stores_without_changing_legacy(self):
  before=self.root.settings();a=self.create();b=self.create('Rajasthan workbook',state='Rajasthan');sa=self.books.get(a['id']);sb=self.books.get(b['id']);cfg=sa.settings();cfg['schemes'][1]['abs_rate']='99';sa.save_settings(cfg)
  self.assertEqual(self.root.settings(),before);self.assertNotEqual(sb.settings()['schemes'][1]['abs_rate'],'99');self.assertFalse(any(s['confirmed'] for s in sa.settings()['schemes']))
  r,_=example();r['workbook_id']=a['id'];saved=sa.save(r);self.assertEqual(len(sa.all()),1);self.assertEqual(sb.all(),[]);self.assertEqual(self.root.all(),[])
  with self.assertRaises(ValueError):sb.get(saved['id'])
 def test_blank_setup_and_date_validation(self):
  m=self.create(mode='blank');s=self.books.get(m['id']).settings();self.assertTrue(all(not sc['benefits'] and sc['billing'] is None for sc in s['schemes']));self.assertTrue(s['products'])
  with self.assertRaises(ValueError):self.create('Bad dates',end='2026-03-01')
  with self.assertRaises(ValueError):self.books.get('../calculator.sqlite3')
  with self.assertRaises(ValueError):self.create()
 def test_bulk_actual_pdfs_save_and_skip_duplicate_then_survive_restart(self):
  m=self.create();id=m['id'];a=self.books.bulk_import(id,self.payload());k=self.books.bulk_import(id,self.payload('krishna_ipt.pdf'));self.assertEqual((a['status'],k['status']),('Imported','Imported'))
  self.assertEqual(self.books.bulk_import(id,self.payload())['status'],'Already imported');reopened=Workbooks(Store(self.root.path));st=reopened.get(id);self.assertEqual(len(st.all()),2);self.assertEqual(len(bulk_history(st)),2)
  r=st.get(a['record_id']);self.assertTrue(r['annual_ledger']);self.assertEqual(r['workbook_id'],id);self.assertEqual(r['allocations'],[]);self.assertFalse(r['ledger_confirmed']);self.assertEqual(next(e['date'] for e in r['entries'] if e['kind']=='receipt'),'2026-04-08')
 def test_bulk_reimport_deleted_party_creates_fresh_record_keeps_archive(self):
  id=self.create()['id'];first=self.books.bulk_import(id,self.payload());st=self.books.get(id);old=st.get(first['record_id']);preview=st.party_action(old['id']);st.party_action(old['id'],confirm=True,expected=preview['expected']);archived=st.get(old['id'])
  new=self.books.bulk_import(id,self.payload());self.assertEqual(new['status'],'Imported');self.assertNotEqual(new['record_id'],old['id']);self.assertEqual(st.get(old['id']),archived);self.assertFalse(st.get(new['record_id']).get('deleted_at'));self.assertIn('ledger_audit',new)
 def test_bulk_failed_pdf_and_border_state_allowed_with_workbook_schemes(self):
  id=self.create()['id'];bad=self.books.bulk_import(id,{'filename':'broken.pdf','data':base64.b64encode(b'not pdf').decode(),'season':'2026 season 1'});self.assertEqual(bad['status'],'Failed');self.assertEqual(self.books.bulk_import(id,self.payload())['status'],'Imported');self.assertEqual(len(self.books.get(id).all()),1)
  wrong=self.create('Rajasthan',state='Rajasthan')['id'];out=self.books.bulk_import(wrong,self.payload());self.assertEqual(out['status'],'Imported');self.assertIn('address state',out['address_warning']);border=self.books.get(wrong).get(out['record_id']);self.assertEqual(border['state'],'Gujarat');self.assertEqual(border['workbook_scheme_state'],'Rajasthan');self.assertEqual(border['entries'],self.books.get(id).all()[0]['entries'])
 def test_changed_bulk_statement_retained_for_review_without_overwriting(self):
  id=self.create()['id'];first=self.books.bulk_import(id,self.payload());st=self.books.get(id);before=st.get(first['record_id']);data=copy.deepcopy(before);doc={k:v for k,v in data.items() if k not in ('id','status','revision')};doc['source']['sha256']='changed';doc['closing']='2184525.00';doc['entries'][0]['credit']='199999.00';doc['entries'][0]['original']['credit']='199999.00'
  with patch('workbooks.import_pdf_documents',return_value=[doc]):out=self.books.bulk_import(id,self.payload(data=base64.b64encode(b'changed pdf').decode()))
  self.assertEqual(out['status'],'Needs review');self.assertEqual(st.get(first['record_id']),before);self.assertEqual(bulk_document(st,out['id'])['document']['closing'],'2184525.00')
  backup=self.books.backup();self.books.restore(backup,True);self.assertEqual(bulk_document(st,out['id'])['document']['closing'],'2184525.00')
  self.assertFalse(resolve_bulk(st,out['id'],before['id'])['resolved']);updated=copy.deepcopy(before);updated['closing']=doc['closing'];updated['entries'][0]={**copy.deepcopy(doc['entries'][0]),'latest_import_source':copy.deepcopy(doc['entries'][0]['original']),'original':before['entries'][0]['original'],'correction_reason':'Accepted updated statement'};saved=st.save(updated);self.assertTrue(resolve_bulk(st,out['id'],saved['id'])['resolved']);self.assertEqual(next(x['status'] for x in bulk_history(st) if x['id']==out['id']),'Reviewed')
 def test_same_pdf_hash_with_old_parser_classification_requires_review(self):
  from importer import import_pdf
  id=self.create()['id'];doc=import_pdf((ROOT/'fixtures'/'ashapura_ipt.pdf').read_bytes(),self.books.get(id).settings());old=copy.deepcopy(doc)
  for e in old['entries']:
   if e['kind']=='ipt_out':e['kind']='return';e['original']['kind']='return'
  saved=self.books.get(id).save({**old,'season':'2026 season 1','annual_ledger':True,'allocations':[],'opening_sources':[],'cash_splits':[],'old_dues':'0','ledger_confirmed':False,'workbook_id':id})
  out=self.books.bulk_import(id,self.payload());self.assertEqual(out['status'],'Needs review');self.assertEqual(out['record_id'],saved['id']);self.assertEqual(len(self.books.get(id).all()),1)
 def test_two_hundred_parties_are_independent_and_resume_skips_all(self):
  id=self.create()['id'];sample=self.books.bulk_import(id,self.payload());base=self.books.get(id).get(sample['record_id']);self.assertEqual(sample['status'],'Imported')
  def parse(raw,settings):
   d=copy.deepcopy(base);d['party']='Synthetic Party '+raw.decode();d['location']='Town '+raw.decode();d['source']['sha256']=hashlib.sha256(raw).hexdigest();return {k:v for k,v in d.items() if k not in ('id','revision','status')}
  with patch('workbooks.import_pdf_documents',side_effect=lambda raw,settings:[parse(raw,settings)]):
   for i in range(200):self.assertEqual(self.books.bulk_import(id,self.payload(data=base64.b64encode(str(i).encode()).decode()))['status'],'Imported')
   for i in range(200):self.assertEqual(self.books.bulk_import(id,self.payload(data=base64.b64encode(str(i).encode()).decode()))['status'],'Already imported')
  self.assertEqual(len(self.books.get(id).all()),201);self.assertEqual(self.root.all(),[])
 def test_backup_restore_includes_all_workbooks_legacy_and_bulk_queue(self):
  id=self.create()['id'];self.books.bulk_import(id,self.payload());self.root.save(example()[0]);backup=self.books.backup();out=self.books.restore(backup,False);self.assertEqual(out['records'],2)
  self.create('Extra workbook');self.books.restore(backup,True);self.assertEqual(len(self.books.list()),1);self.assertEqual(len(self.books.get(id).all()),1);self.assertEqual(len(bulk_history(self.books.get(id))),1);self.assertEqual(len(self.root.all()),1)
  legacy=self.root.backup();self.books.restore(legacy,True);self.assertEqual(len(self.books.list()),1)
 def test_issue_duplicate_blocked_across_overlapping_workbooks(self):
  a=self.create();b=self.create('Another');r,s=example();r.update(annual_ledger=True)
  for m in (a,b):
   st=self.books.get(m['id']);cfg=copy.deepcopy(s);cfg['version']=st.settings()['version'];st.save_settings(cfg);saved=st.save({**r,'workbook_id':m['id']});f=st.finalise(saved['id'],saved['revision'])
   if m==a:self.books.issue(m['id'],f['id'],f['revision'])
   else:
    with self.assertRaisesRegex(ValueError,'overlaps'):self.books.issue(m['id'],f['id'],f['revision'])

class AnnualPeriodAndProductTests(unittest.TestCase):
 def test_annual_stock_outside_period_not_counted_but_ledger_retained(self):
  r,s=example();before=compute(r,s);r['entries'].append({'id':'next-season','date':'2026-11-01','kind':'sale','debit':'999','credit':'0','items':[{'name':'Outside product needs no mapping','product':None,'qty':'100','unit':'packet','amount':'999','rate':'9.99'}]});r['closing']=str(D(r['closing'])+999);r['annual_ledger']=True;out=compute(r,s)
  self.assertEqual(out['groups'],before['groups']);self.assertEqual(out['new_CN_total'],before['new_CN_total']);self.assertEqual(out['ledger_computed'],before['ledger_computed']+999);self.assertFalse(any('outside selected season' in i or 'Outside product needs' in i for i in out['issues']));self.assertEqual(out['sources'],before['sources'])
 def test_cutoff_blocks_later_payment_benefits_but_settlement_allowed(self):
  r,s=example();r['annual_ledger']=True;s['seasons'][0]['cutoff']='2026-06-30';s['seasons'][0]['end']='2026-06-30';out=compute(r,s);self.assertTrue(any('Payment after selected' in i for i in out['issues']));r['allocations'][-1]['type']='Settlement';self.assertFalse(any('Payment after selected' in i for i in compute(r,s)['issues']))
 def product_example(self):
  r,s=example('scheme-2',sup='10',ret='0',abs_amount='0');sc=s['schemes'][1];sc.update(benefits=['Quantity','Extra','ABS'],quantity=[{'above':'0','upto':None,'rate':'0.5'}],extra=[{'above':'0','upto':None,'rate':'100.5'}],token='10',abs_rate='2');p1,p2=sc['products'];sale=r['entries'][0];sale['debit']='27030';sale['items'][0].update(qty='10',amount='9010');sale['items'].append({**copy.deepcopy(sale['items'][0]),'product':p2,'qty':'20','amount':'18020'});r['entries']=[sale,{'id':'advance','kind':'receipt','date':'2026-03-20','credit':'50','debit':'0','items':[]}];r['closing']='26980';r['allocations']=[{'id':'a','type':'ABS','source':'advance','scheme':sc['id'],'product':p1,'amount':'50'}];return r,s
 def test_product_shares_reconcile_each_rounded_benefit_abs_direct(self):
  r,s=self.product_example();out=compute(r,s);self.assertEqual(out['issues'],[]);rows=out['product_CNs'];self.assertEqual(sum(x['total_CN'] for x in rows),sum(c['rounded'] for c in out['CNs']));self.assertEqual(out['new_CN_total'],D(126))
  for c in out['CNs']:self.assertEqual(sum(b['CN'] for x in rows for b in x['benefits'] if b['benefit']==c['benefit']),c['rounded'])
  p1=s['schemes'][1]['products'][0]
  for row in rows:self.assertEqual(next(b['CN'] for b in row['benefits'] if b['benefit']=='ABS'),D(10) if row['product_id']==p1 else D(0));self.assertEqual(row['CN_per_packet']*row['net_packets'],row['total_CN'])
 def test_requests_never_change_entitlement_outstanding_or_issue(self):
  r,s=self.product_example();before=compute(r,s);row=before['product_CNs'][0];r['cn_requests']={row['key']:{'direction':'decrease','unit':'kg','rate':'1000','remark':'Request only'}};after=compute(r,s)
  for field in ('CNs','proposals','new_CN_total','final_balance','party_owes','excess_credit'):self.assertEqual(after[field],before[field])
  self.assertLess(after['product_CNs'][0]['request']['requested_total'],0)
  with tempfile.TemporaryDirectory() as td:
   st=Store(Path(td)/'p.sqlite3');st.save_settings(s);saved=st.save(r);f=st.finalise(saved['id'],saved['revision']);issued=st.issue(f['id'],f['revision']);self.assertEqual(D(issued['result']['new_CN_total']),before['new_CN_total']);self.assertEqual(st.get(saved['id'])['cn_requests'],r['cn_requests'])
 def test_cash_product_direct_and_independent_dawat_breakdowns(self):
  for sid in ('scheme-7','scheme-8'):
   r,s=example(sid,sup='100',ret='0',abs_amount='10000');o=compute(r,s);self.assertEqual(len(o['product_CNs']),1);self.assertEqual(o['product_CNs'][0]['scheme'],sid);self.assertEqual(sum(x['total_CN'] for x in o['product_CNs']),sum(c['rounded'] for c in o['CNs']))
