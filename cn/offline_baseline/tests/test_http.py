import unittest,subprocess,sys,tempfile,os,json,time,urllib.request,urllib.error
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class LocalHTTPTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.tmp=tempfile.TemporaryDirectory();env=dict(os.environ,CN_PORT='18765',CN_DATA_PATH=str(Path(cls.tmp.name)/'api.sqlite'))
  cls.proc=subprocess.Popen([sys.executable,str(ROOT/'app.py'),'--no-browser'],env=env,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
  for i in range(100):
   try:cls.state=cls.get('/api/state');break
   except Exception:time.sleep(.03)
  else:raise RuntimeError('Local server did not start')
 @classmethod
 def tearDownClass(cls):cls.proc.terminate();cls.proc.communicate(timeout=5);cls.tmp.cleanup()
 @classmethod
 def get(cls,path):return json.load(urllib.request.urlopen('http://127.0.0.1:18765'+path))
 def post(self,path,payload,token=True,workbook=None):
  req=urllib.request.Request('http://127.0.0.1:18765'+path,data=json.dumps(payload).encode(),headers={'Content-Type':'application/json',**({'X-CN-Workbook':workbook} if workbook else {}),**({'X-CN-Token':self.state['token']} if token else {})});return json.load(urllib.request.urlopen(req))
 def test_remaining_batch_endpoints_and_crossyear_credit_registration(self):
  from test_remaining_batches import pair
  previous,current,cfg=pair();make={'name':'Year-link HTTP workbook','state':'Gujarat','period':'2026 season 1','start':'2026-04-01','end':'2026-08-31','cutoff':'2026-10-13'};w=self.post('/api/workbooks',make)['id']
  saved=self.post('/api/year-link-save',{'previous':previous,'current':current,'season':'2026 season 1','confirmed':{'old-r':'4000'},'reason':'Jan receipt less Feb purchases, reviewed'},workbook=w);self.assertEqual(saved['opening_sources'][0]['date'],'2026-01-15');self.assertEqual(saved['opening_sources'][0]['amount'],'4000');self.assertEqual([{k:v for k,v in e.items() if k!='original'} for e in saved['entries']],current['entries']);self.assertEqual(self.post('/api/year-match',{'previous':[previous],'current':[current]},workbook=w)['matches'][0]['previous_index'],0)
  state_req=urllib.request.Request('http://127.0.0.1:18765/api/state',headers={'X-CN-Workbook':w});ws=json.load(urllib.request.urlopen(state_req));prod=ws['settings']['products'][0]
  mapped=self.post('/api/audit-map',{'narration':'Unknown CN test','crop':'Cotton','version':ws['settings']['version']},workbook=w);self.assertEqual(mapped['audit_crop_mappings']['UNKNOWN CN TEST'],'Cotton');archived=self.post('/api/product-delete',{'id':prod['id'],'version':mapped['version']},workbook=w);self.assertTrue(archived['products'][0]['deleted_at']);self.post('/api/product-delete',{'id':prod['id'],'version':archived['version'],'restore':True},workbook=w)
  preview=self.post('/api/workbook-delete',{'id':w});self.post('/api/workbook-delete',{'id':w,'confirm':True,'expected':preview['expected']});self.assertNotIn(w,[x['id'] for x in self.get('/api/state')['workbooks']]);preview=self.post('/api/workbook-delete',{'id':w,'restore':True});self.post('/api/workbook-delete',{'id':w,'restore':True,'confirm':True,'expected':preview['expected']})
 def test_health_and_static_assets(self):
  self.assertTrue(self.get('/api/health')['offline'])
  with urllib.request.urlopen('http://127.0.0.1:18765/') as r:self.assertIn(b'All-crop CN calculator',r.read());self.assertIn("default-src 'self'",r.headers['Content-Security-Policy'])
 def test_standalone_audit_without_cn_setup_or_record_writes(self):
  import base64
  before=self.get('/api/state')['records'];raw=base64.b64encode((ROOT/'fixtures/ashapura.pdf').read_bytes()).decode();documents=self.post('/api/audit-import',{'data':raw})['documents'];out=self.post('/api/audit-check',{'documents':documents,'start':'2026-04-01','end':'2026-08-31'});self.assertEqual(out['party_count'],1);self.assertIn('posted_CNs',out);self.assertEqual(self.get('/api/state')['records'],before)
 def test_import_save_reopen_calculate(self):
  data=self.get('/api/fixture/ashapura');data.update(season='2026 season 1',old_dues='89909',allocations=[],cash_splits=[],opening_sources=[],ledger_confirmed=False)
  saved=self.post('/api/save',data);reopened=next(r for r in self.get('/api/state')['records'] if r['id']==saved['id']);self.assertEqual(reopened['entries'],data['entries']);o=self.post('/api/calculate',saved);self.assertEqual(o['ledger_computed'],'2184524.00');self.assertFalse(o['can_finalise'])
  with self.assertRaises(urllib.error.HTTPError):self.post('/api/finalise',{'id':saved['id'],'revision':saved['revision']})
 def test_excessive_split_rejected_http(self):
  data=self.get('/api/fixture/ashapura');data.update(season='2026 season 1',old_dues='89909',cash_splits=[],opening_sources=[],ledger_confirmed=False)
  src=next(e['id'] for e in data['entries'] if e['kind']=='receipt')
  data['allocations']=[{'id':'overflow','source':src,'scheme':'scheme-2','type':'CD','amount':'1000000'}]
  for endpoint in ('/api/save','/api/validate-limits'):
   with self.assertRaises(urllib.error.HTTPError) as ctx:self.post(endpoint,data)
   self.assertEqual(ctx.exception.code,400)
  out=self.post('/api/calculate',data);self.assertEqual(out['new_CN_total'],'0');self.assertFalse(out['can_finalise']);self.assertTrue(out['sources'])
 def test_party_and_scheme_delete_restore_http(self):
  data=self.get('/api/fixture/ashapura');data.update(party='HTTP Lifecycle Test',season='2026 season 1',old_dues='0',allocations=[],cash_splits=[],opening_sources=[],ledger_confirmed=False)
  saved=self.post('/api/save',data);preview=self.post('/api/party-delete',{'id':saved['id']});out=self.post('/api/party-delete',{'id':saved['id'],'confirm':True,'expected':preview['expected']});self.assertTrue(out['deleted'])
  with self.assertRaises(urllib.error.HTTPError):self.post('/api/save',saved)
  preview=self.post('/api/party-delete',{'id':saved['id'],'restore':True});out=self.post('/api/party-delete',{'id':saved['id'],'restore':True,'confirm':True,'expected':preview['expected']});self.assertTrue(out['restored'])
  settings=self.get('/api/state')['settings'];settings=self.post('/api/scheme-delete',{'id':'scheme-1','version':settings['version']});self.assertTrue(settings['schemes'][0].get('deleted_at'));settings=self.post('/api/scheme-delete',{'id':'scheme-1','version':settings['version'],'restore':True});self.assertFalse(settings['schemes'][0].get('deleted_at'))
 def test_scheme_preview_validation(self):
  scheme=self.state['settings']['schemes'][1];out=self.post('/api/validate-scheme',{'scheme':scheme,'production':False});self.assertEqual(out['errors'],[])
  scheme['cd'][1]['start']=scheme['cd'][0]['end'];out=self.post('/api/validate-scheme',{'scheme':scheme,'production':False});self.assertTrue(any('Overlapping' in e for e in out['errors']))
 def test_no_token_mutation_rejected(self):
  with self.assertRaises(urllib.error.HTTPError) as ctx:self.post('/api/save',{},False)
  self.assertEqual(ctx.exception.code,403)
 def test_foreign_host_rejected(self):
  req=urllib.request.Request('http://127.0.0.1:18765/api/state',headers={'Host':'untrusted.example'})
  with self.assertRaises(urllib.error.HTTPError) as ctx:urllib.request.urlopen(req)
  self.assertEqual(ctx.exception.code,403)
 def test_workbook_scope_and_bulk_endpoints(self):
  import base64
  def state(id):
   req=urllib.request.Request('http://127.0.0.1:18765/api/state',headers={'X-CN-Workbook':id});return json.load(urllib.request.urlopen(req))
  make={'name':'HTTP independent workbook','state':'Gujarat','period':'HTTP season','start':'2026-04-01','end':'2026-08-31','cutoff':'2026-10-13','mode':'copy'}
  a=self.post('/api/workbooks',make);b=self.post('/api/workbooks',{**make,'name':'HTTP other workbook'});sa=state(a['id']);sb=state(b['id']);sa['settings']['schemes'][1]['abs_rate']='77';self.post('/api/settings',sa['settings'],workbook=a['id']);self.assertNotEqual(state(b['id'])['settings']['schemes'][1]['abs_rate'],'77')
  pdf=base64.b64encode((ROOT/'fixtures/ashapura_ipt.pdf').read_bytes()).decode();payload={'filename':'Ashapura.pdf','data':pdf,'season':'HTTP season'};out=self.post('/api/bulk-import',payload,workbook=a['id']);self.assertEqual(out['status'],'Imported');self.assertEqual(self.post('/api/bulk-import',payload,workbook=a['id'])['status'],'Already imported');self.assertEqual(state(b['id'])['records'],[])
  r=state(a['id'])['records'][0]
  with self.assertRaises(urllib.error.HTTPError):self.post('/api/save',r,workbook=b['id'])
  with self.assertRaises(urllib.error.HTTPError):self.post('/api/finalise',{'id':r['id'],'revision':r['revision']},workbook=b['id'])
  backup=self.get('/api/backup');self.assertEqual(backup['format'],'all-crop-cn-workbooks-backup');self.assertGreaterEqual(len(backup['workbooks']),2);preview=self.post('/api/restore',{'backup':backup});self.assertIn('all workbook',preview['warning'])

 def test_frozen_status_and_draft_settings_are_server_owned(self):
  from test_calculator import example
  r,cfg=example();cfg['version']=self.get('/api/state')['settings']['version'];cfg=self.post('/api/settings',cfg)
  r['party']='Workflow HTTP frozen';saved=self.post('/api/save',r);frozen=self.post('/api/finalise',{'id':saved['id'],'revision':saved['revision']})
  fake=dict(frozen,status='draft',entries=[],party='Wrong display')
  self.assertEqual(self.post('/api/calculate',fake),frozen['result'])
  csv=self.post('/api/product-csv',{'record':fake})['csv'];self.assertIn('Workflow HTTP frozen',csv);self.assertNotIn('Wrong display',csv)
  draft=dict(r,party='Workflow HTTP draft',frozen_settings=cfg,result={'new_CN_total':'999'})
  draft['frozen_settings']['schemes'][2]['quantity'][0]['rate']='999'
  self.assertEqual(self.post('/api/calculate',draft),self.post('/api/calculate',dict(r,party='Workflow HTTP draft')))
  stored=self.post('/api/save',draft);self.assertNotIn('frozen_settings',stored);self.assertNotIn('result',stored)
 def test_cash_quantity_scoped_preview_apply_and_auth(self):
  from test_allocation28 import cash_case
  r,s,a=cash_case();w=self.post('/api/workbooks',{'name':'Quantity booking HTTP','state':'Rajasthan','period':'2026 season 1','start':'2026-04-01','end':'2026-08-31','cutoff':'2026-10-13'})['id']
  req=urllib.request.Request('http://127.0.0.1:18765/api/state',headers={'X-CN-Workbook':w});ws=json.load(urllib.request.urlopen(req));s['version']=ws['settings']['version'];cfg=self.post('/api/settings',s,workbook=w);r=self.post('/api/save',r,workbook=w);payload={'record':r,**a}
  with self.assertRaises(urllib.error.HTTPError) as error:self.post('/api/cash-quantity-preview',payload,token=False,workbook=w)
  self.assertEqual(error.exception.code,403)
  with self.assertRaises(urllib.error.HTTPError):self.post('/api/cash-quantity-preview',payload)
  plan=self.post('/api/cash-quantity-preview',payload,workbook=w);self.assertEqual(plan['Cash_CN'],'40000');self.assertEqual(plan['regular_net'],'500');self.assertNotIn('candidate',plan)
  saved=self.post('/api/cash-quantity-apply',{**payload,'settings_version':plan['settings_version']},workbook=w);self.assertEqual(saved['workbook_id'],w);self.assertEqual(saved['cash_splits'][0]['supplied'],'1000');self.assertEqual(saved['entries'],r['entries']);self.assertEqual(self.post('/api/calculate',saved,workbook=w)['new_CN_total'],'45000')
  with self.assertRaises(urllib.error.HTTPError):self.post('/api/cash-quantity-apply',{**payload,'settings_version':plan['settings_version']},workbook=w)
 def test_ledger_nrv_mapping_and_saved_bulk_readonly(self):
  import copy,base64
  from test_ledger_nrv import base
  from ledger_audit import voucher_view,cn_product_key
  w=self.post('/api/workbooks',{'name':'Posted CN NRV HTTP','state':'Gujarat','period':'NRV period','start':'2026-04-01','end':'2026-08-31','cutoff':'2026-10-13'})['id']
  def state():
   req=urllib.request.Request('http://127.0.0.1:18765/api/state',headers={'X-CN-Workbook':w});return json.load(urllib.request.urlopen(req))
  d=base();d['entries'][-1]['remarks']='AGREED NRV HTTP BENEFIT';d['entries'][-1]['source_lines'][1]['text']='AGREED NRV HTTP BENEFIT';payload={'documents':[d],'start':'2026-04-01','end':'2026-08-31'};before=copy.deepcopy(d)
  out=self.post('/api/audit-check',payload,workbook=w);self.assertIsNone(out['posted_CN_NRV']['crop_rows'][0]['NRV_per_kg']);ws=state();pid=next(p['id'] for p in ws['settings']['products'] if p['name']=='32D55')
  with self.assertRaises(urllib.error.HTTPError):self.post('/api/audit-map',{'narration':'AGREED NRV HTTP BENEFIT','crop':'Cotton','product':pid,'classification':'scheme','version':ws['settings']['version']},workbook=w)
  self.post('/api/audit-map',{'narration':'AGREED NRV HTTP BENEFIT','crop':'Maize','product':pid,'classification':'scheme','product_mapping_key':cn_product_key(voucher_view(d,d['entries'][-1])),'voucher':voucher_view(d,d['entries'][-1]),'version':ws['settings']['version']},workbook=w);out=self.post('/api/audit-check',payload,workbook=w);self.assertEqual(out['posted_CN_NRV']['product_rows'][0]['NRV_per_kg'],'120');self.assertEqual(d,before);self.assertEqual(state()['records'],ws['records'])
  self.assertIsNone(self.post('/api/audit-check',payload)['posted_CN_NRV']['crop_rows'][0]['NRV_per_kg'])
  pdf=base64.b64encode((ROOT/'fixtures/ashapura.pdf').read_bytes()).decode();self.post('/api/bulk-import',{'filename':'NRV source.pdf','data':pdf,'season':'NRV period'},workbook=w);before=state()['records'];out=self.post('/api/audit-bulk-nrv',{'start':'2026-04-01','end':'2026-08-31'},workbook=w);self.assertEqual(out['source'],'saved_bulk_source_entries');self.assertTrue(out['posted_CN_NRV']['crop_rows']);self.assertEqual(state()['records'],before)
