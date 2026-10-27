import copy,tempfile,json,unittest
from pathlib import Path
from decimal import Decimal as D
from settings import initial_settings
from ledger_audit import audit_documents,voucher_view,cn_product_key
from ledger_nrv import saved_bulk_report
from store import Store,dump

def item(name='32D55',q='1000',value='140000',unit='kg'):
 return {'name':name,'qty':q,'unit':unit,'rate':'140','amount':value}
def voucher(id,kind='sale',value='140000',items=None,text='',family=None):
 return {'id':id,'kind':kind,'date':'2026-05-01','reference':id,'debit':value if kind=='sale' else '0','credit':'0' if kind=='sale' else value,'remarks':text,'items':items or [],'source_lines':[{'page':1,'line':1,'text':id+' '+(family or ('Sales Invoice' if kind=='sale' else 'Credit Note'))},{'page':1,'line':2,'text':text}],**({'voucher_family':family} if family else {})}
def doc(es,party='A'):return {'party':party,'location':'Town','entries':es,'warnings':[]}
def report(ds,s=None):return audit_documents(ds,'2026-04-01','2026-08-31',s or initial_settings())['posted_CN_NRV']
def base():return doc([voucher('s',items=[item()]),voucher('r','return','14000',[item(q='100',value='14000')]),voucher('c','posted_cn','18000',text='32D55 scheme benefit')])

class LedgerNRVTests(unittest.TestCase):
 def test_actual_invoice_return_and_posted_cn(self):
  d=base();before=copy.deepcopy(d);r=report([d]);c=r['crop_rows'][0];self.assertEqual(c['net_kg'],D(900));self.assertEqual(c['scheme_CN'],D(18000));self.assertEqual(c['NRV_per_kg'],D(120));self.assertEqual(c['NRV_per_packet'],D(480));self.assertEqual(c['CN_status'],'CN given');self.assertEqual(r['product_rows'][0]['NRV_per_kg'],D(120));self.assertEqual(d,before)
 def test_journal_freight_and_return_cn_never_deduct_twice(self):
  d=base();d['entries'] += [voucher('j','posted_cn','9999',text='32D55 scheme benefit',family='Journal'),voucher('f','posted_cn','8888',text='Freight 32D55 scheme CN'),voucher('h','posted_cn','1000',family='Credit Note Freight')];s=initial_settings();s['audit_cn_classifications']={'32D55 SCHEME BENEFIT':'scheme'};s['audit_crop_mappings']={'32D55 SCHEME BENEFIT':'Maize'};r=report([d],s);self.assertEqual(r['confirmed_CN_total'],D(18000));self.assertEqual(r['crop_rows'][0]['NRV_per_kg'],D(120));self.assertEqual(len(r['excluded_credits']),4)
 def test_weighted_average_never_mean_of_party_rates(self):
  a=doc([voucher('s',value='10000',items=[item(q='100',value='10000')]),voucher('c','posted_cn','1000',text='32D55 ABS benefit')]);b=doc([voucher('s',value='200000',items=[item(q='1000',value='200000')]),voucher('c','posted_cn','20000',text='32D55 CD discount')],'B');r=report([a,b]);c=r['crop_rows'][0];self.assertLess(abs(c['NRV_per_kg']-D(189000)/D(1100)),D('1e-24'));self.assertEqual(r['product_average_rows'][0]['NRV_per_kg'],c['NRV_per_kg']);self.assertNotEqual(c['NRV_per_kg'],D(135));self.assertEqual(c['party_count'],2)
 def test_crop_only_cn_no_product_apportionment(self):
  d=base();d['entries'][-1]['remarks']='Maize scheme benefit';d['entries'][-1]['source_lines'][1]['text']='Maize scheme benefit';r=report([d]);self.assertEqual(r['crop_rows'][0]['NRV_per_kg'],D(120));self.assertIsNone(r['product_rows'][0]['NRV_per_kg']);self.assertEqual(r['party_rows'][0]['crop_CN_pool'],D(18000))
 def test_unknown_cn_suppresses_affected_nrv_not_zero(self):
  d=base();d['entries'].append(voucher('u','posted_cn','500',text='Unidentified adjustment ABC'));r=report([d]);self.assertIsNone(r['crop_rows'][0]['NRV_per_kg']);self.assertEqual(r['crop_rows'][0]['CN_status'],'Needs review');self.assertEqual(r['confirmed_CN_total'],D(18000));self.assertEqual(len(r['pending_CNs']),1)
 def test_no_cn_status_is_period_scoped(self):
  d=doc([voucher('s',items=[item()]),voucher('out','posted_cn','999',text='32D55 scheme benefit')]);d['entries'][1]['date']='2026-09-01';r=report([d]);self.assertEqual(r['crop_rows'][0]['CN_status'],'No scheme CN found');self.assertEqual(r['crop_rows'][0]['NRV_per_kg'],D(140))
 def test_dawat_packing_separation_and_no_mixed_packet_average(self):
  d=doc([voucher('s1',value='3000',items=[item('DAWAT 1 kg','10','3000','packet')]),voucher('s3',value='9000',items=[item('DAWAT 3 kg','10','9000','packet')]),voucher('cn','posted_cn','300',text='DAWAT 3 kg scheme benefit')]);r=report([d]);self.assertEqual(len(r['product_rows']),2);self.assertEqual(r['crop_rows'][0]['NRV_per_kg'],D(11700)/40);self.assertIsNone(r['crop_rows'][0]['NRV_per_packet']);self.assertEqual(next(x for x in r['product_rows'] if x['packing_kg']==3)['NRV_per_packet'],D(870))
 def test_ambiguous_dawat_cn_falls_back_to_crop(self):
  d=doc([voucher('s',value='3000',items=[item('DAWAT 1 kg','10','3000','packet')]),voucher('cn','posted_cn','300',text='DAWAT scheme benefit')]);r=report([d]);self.assertIsNone(r['included_CNs'][0]['product_id']);self.assertEqual(r['crop_rows'][0]['NRV_per_kg'],D(270));self.assertIsNone(r['product_rows'][0]['NRV_per_kg'])
 def test_explicit_product_mapping_and_quantified_financial_cn(self):
  d=base();cn=d['entries'][-1];cn['remarks']='Agreed benefit';cn['source_lines'][1]['text']='Agreed benefit';cn['items']=[item(q='900',value='18000')];s=initial_settings();pid=next(p['id'] for p in s['products'] if p['name']=='32D55');r=report([d],s);self.assertIsNone(r['crop_rows'][0]['NRV_per_kg']);s.update(audit_cn_classifications={'AGREED BENEFIT':'scheme'},audit_crop_mappings={'AGREED BENEFIT':'Maize'},audit_product_mappings={cn_product_key(voucher_view(d,cn)):pid});r=report([d],s);self.assertEqual(r['product_rows'][0]['NRV_per_kg'],D(120));self.assertEqual(r['crop_rows'][0]['net_kg'],D(900))
 def test_material_classification_reduces_sales_not_scheme_cn(self):
  d=doc([voucher('s',items=[item()]),voucher('r','posted_cn','14000',[item(q='100',value='14000')],text='Material adjustment')]);s=initial_settings();s['audit_cn_classifications']={'MATERIAL ADJUSTMENT':'material_return'};r=report([d],s);self.assertEqual(r['confirmed_CN_total'],0);self.assertEqual(r['crop_rows'][0]['net_kg'],900);self.assertEqual(r['crop_rows'][0]['NRV_per_kg'],140)
 def test_voucher_value_mismatch_returns_missing_coverage_and_unknown_packing(self):
  d=base();d['entries'][0]['debit']='140100';self.assertIsNone(report([d])['crop_rows'][0]['NRV_per_kg']);d=base();d['entries'][1]['items'][0]['qty']='1001';self.assertIsNone(report([d])['crop_rows'][0]['NRV_per_kg']);d=doc([voucher('s',value='1000',items=[item('Maize unidentified','10','1000','packet')])]);r=report([d]);self.assertIsNone(r['crop_rows'][0]['NRV_per_kg']);self.assertEqual(r['crop_rows'][0]['NRV_per_packet'],100)
 def test_overlapping_uploads_dedup_but_repeated_printed_postings_retained(self):
  d=base();self.assertEqual(report([d]),report([d,copy.deepcopy(d)]));d['entries'].append(copy.deepcopy(d['entries'][-1]));self.assertEqual(report([d,d])['confirmed_CN_total'],36000)
 def test_unmatched_cn_and_failed_party_do_not_create_false_average(self):
  d=base();d['entries'].append(voucher('x','posted_cn','100',text='Legend scheme benefit'));r=report([d]);self.assertIsNone(r['crop_rows'][0]['NRV_per_kg']);r=report([base(),{'party':'Bad','import_error':'Cannot read PDF'}]);self.assertFalse(r['coverage_complete']);self.assertIsNone(r['crop_rows'][0]['NRV_per_kg']);self.assertEqual(r['party_rows'][0]['NRV_per_kg'],120)
 def test_saved_bulk_source_only_readonly_and_no_double_records(self):
  with tempfile.TemporaryDirectory() as td:
   st=Store(Path(td)/'a.sqlite');d=base();r={**d,'state':'Gujarat','season':'2026 season 1','opening':'0','closing':'108000','old_dues':'0','allocations':[],'cash_splits':[],'opening_sources':[],'ledger_confirmed':False};r=st.save(r)
   with st.db() as c:
    for i in range(2):c.execute('INSERT INTO bulk_imports VALUES(?,?)',(str(i),dump({'id':str(i),'status':'Imported','record_id':r['id'],'party':'A','filename':'test.pdf'})))
   before=st.backup();out=saved_bulk_report(st,'2026-04-01','2026-08-31');after=st.backup();before.pop('created_at');after.pop('created_at');self.assertEqual(after,before);self.assertEqual(out['posted_CN_NRV']['confirmed_CN_total'],18000);self.assertEqual(out['posted_CN_NRV']['crop_rows'][0]['NRV_per_kg'],120)

 def test_manual_product_mapping_is_voucher_scoped(self):
  a=base();a['entries'][-1]['remarks']='Maize scheme benefit';a['entries'][-1]['source_lines'][1]['text']='Maize scheme benefit';b=copy.deepcopy(a);b['party']='Other party';s=initial_settings();pid=next(p['id'] for p in s['products'] if p['name']=='32D55');s['audit_product_mappings']={cn_product_key(voucher_view(a,a['entries'][-1])):pid};r=report([a,b],s);self.assertEqual(next(x for x in r['product_rows'] if x['party']=='A')['NRV_per_kg'],120);self.assertIsNone(next(x for x in r['product_rows'] if x['party']=='Other party')['NRV_per_kg']);self.assertEqual(r['crop_rows'][0]['NRV_per_kg'],120)

 def test_conflicting_overlap_not_summed_and_decimal_formats_not_conflicts(self):
  a=base();b=copy.deepcopy(a);b['entries'][0]['debit']='140001';b['entries'][0]['items'][0]['amount']='140001';r=report([a,b]);self.assertTrue(any('Conflicting' in x['reason'] for x in r['pending_CNs']));self.assertIsNone(r['crop_rows'][0]['NRV_per_kg'])
  b=copy.deepcopy(a)
  for e in b['entries']:
   e['debit']=str(D(e['debit']).quantize(D('.01')));e['credit']=str(D(e['credit']).quantize(D('.01')))
  self.assertEqual(report([a,b])['crop_rows'][0]['NRV_per_kg'],120)

 def test_credit_only_party_cannot_silently_disappear_from_bulk_average(self):
  a=doc([voucher('s',items=[item()])]);b=doc([voucher('cn','posted_cn','500',text='Unidentified credit ABC')],'Credit only party');r=report([a,b]);self.assertIsNone(r['crop_rows'][0]['NRV_per_kg']);self.assertEqual(r['party_rows'][0]['NRV_per_kg'],140)
  b['entries'][0]['remarks']='Maize unidentified credit';b['entries'][0]['source_lines'][1]['text']='Maize unidentified credit';r=report([a,b]);self.assertIsNone(r['crop_rows'][0]['NRV_per_kg']);self.assertIsNone(r['product_average_rows'][0]['NRV_per_kg'])
