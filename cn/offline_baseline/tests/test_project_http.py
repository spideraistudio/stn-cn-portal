import base64,json,os,subprocess,sys,tempfile,time,unittest,urllib.error,urllib.request
from pathlib import Path
from test_calculator import example
ROOT=Path(__file__).resolve().parents[1]
class ProjectHTTPTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.tmp=tempfile.TemporaryDirectory();cls.url='http://127.0.0.1:18771';cls.proc=subprocess.Popen([sys.executable,str(ROOT/'app.py'),'--no-browser'],env=dict(os.environ,CN_PORT='18771',CN_DATA_PATH=str(Path(cls.tmp.name)/'owner.sqlite3')),stdout=subprocess.DEVNULL,stderr=subprocess.PIPE)
  for _ in range(100):
   try:cls.token=cls.call('/api/state')['token'];break
   except Exception:time.sleep(.03)
  else:raise RuntimeError('Project test server did not start')
 @classmethod
 def tearDownClass(cls):cls.proc.terminate();cls.proc.communicate(timeout=5);cls.tmp.cleanup()
 @classmethod
 def call(cls,path,b=None,project=None,token=True):
  headers={'Content-Type':'application/json'}
  if project:headers['X-CN-Project']=project
  if b is not None and token:headers['X-CN-Token']=cls.token
  req=urllib.request.Request(cls.url+path,data=json.dumps(b).encode() if b is not None else None,headers=headers)
  return json.load(urllib.request.urlopen(req))
 def test_received_edit_reports_and_backups_cannot_mix_with_own_project(self):
  r,cfg=example();cfg['version']=self.call('/api/state')['settings']['version'];self.call('/api/settings',cfg);r['party']='Original owner';r=self.call('/api/save',r);frozen=self.call('/api/finalise',{'id':r['id'],'revision':r['revision']});main=self.call('/api/backup')
  p=self.call('/api/project-export',{});file=self.call('/api/project-export',{'confirm':True,'expected':p['sha256'],'name':'HTTP received','sender':'Sender'});preview=self.call('/api/project-import',{'data':file['data']});received=self.call('/api/project-import',{'data':file['data'],'confirm':True,'expected':preview['expected']})['project']['id']
  state=self.call('/api/state',project=received);self.assertEqual(state['records'],[frozen]);self.assertEqual(state['project']['kind'],'received')
  rev=self.call('/api/revise',{'id':frozen['id']},received);rev.update(party='Receiver only',ledger_confirmed=True,revision_ledger_confirmed=True);rev=self.call('/api/save',rev,received);self.call('/api/finalise',{'id':rev['id'],'revision':rev['revision']},received)
  main_report=self.call('/api/report',{});received_report=self.call('/api/report',{},received);self.assertNotIn('Receiver only',json.dumps(main_report));self.assertIn('Receiver only',json.dumps(received_report));self.assertNotIn('Receiver only',json.dumps(self.call('/api/territory-report',{})))
  for key in ('records','settings','issued','audit','bulk_imports'):self.assertEqual(self.call('/api/backup')['legacy'][key],main['legacy'][key])
  self.assertEqual(self.call('/api/state')['project']['id'],'main');self.assertEqual(self.call('/api/state')['records'],[frozen])
  self.assertEqual(len(self.call('/api/backup',project=received)['legacy']['records']),2)
 def test_bad_project_invalid_file_and_unauthenticated_mutation_rejected(self):
  with self.assertRaises(urllib.error.HTTPError) as err:self.call('/api/state',project='../escape')
  self.assertEqual(err.exception.code,400)
  count=len(self.call('/api/state')['projects'])
  for b in ({'data':'not-a-file'},{'data':base64.b64encode(b'not a zip').decode()}):
   with self.assertRaises(urllib.error.HTTPError):self.call('/api/project-import',b)
  self.assertEqual(len(self.call('/api/state')['projects']),count)
  with self.assertRaises(urllib.error.HTTPError) as err:self.call('/api/project-import',{'data':'anything'},token=False)
  self.assertEqual(err.exception.code,403)
