"""Exercise bundle path/port behavior without claiming a native Windows build."""
import json,os,runpy,subprocess,sys,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class PackagedRuntimeTests(unittest.TestCase):
 def test_frozen_assets_separate_from_data_and_override(self):
  for override in (False,True):
   with tempfile.TemporaryDirectory() as d:
    exe=Path(d)/'AllCropCN.exe';chosen=Path(d)/'explicit'/'db.sqlite3'
    script="import sys,runpy,json;sys.frozen=True;sys.executable=sys.argv[1];m=runpy.run_path(sys.argv[2]);print(json.dumps([str(m['ROOT']),m['store'].path]))"
    env=dict(os.environ);env.pop('CN_DATA_PATH',None)
    if override:env['CN_DATA_PATH']=str(chosen)
    proc=subprocess.run([sys.executable,'-c',script,str(exe),str(ROOT/'app.py')],cwd=ROOT,env=env,capture_output=True,text=True,check=True)
    assets,data=json.loads(proc.stdout)
    self.assertEqual(Path(assets),ROOT)
    self.assertEqual(Path(data),chosen if override else Path(d)/'data'/'calculator.sqlite3')
    self.assertTrue(Path(data).is_file())
 def test_frozen_auto_port_and_static_pdf_dependency(self):
  with tempfile.TemporaryDirectory() as d:
   script="import sys,runpy;sys.frozen=True;sys.executable=sys.argv[1];sys.argv=[sys.argv[2],'--no-browser'];runpy.run_path(sys.argv[0],run_name='__main__')"
   env=dict(os.environ);env.pop('CN_PORT',None);env.pop('CN_DATA_PATH',None)
   p=subprocess.Popen([sys.executable,'-u','-c',script,str(Path(d)/'AllCropCN.exe'),str(ROOT/'app.py')],cwd=ROOT,env=env,stdout=subprocess.PIPE,text=True)
   try:
    import urllib.request,re
    line=p.stdout.readline();url=re.search(r'http://127.0.0.1:(\d+)',line).group(0)
    self.assertNotEqual(url.rsplit(':',1)[1],'0')
    self.assertIn(b'Offline workspace',urllib.request.urlopen(url).read())
    self.assertIn(b'body',urllib.request.urlopen(url+'/style.css').read())
    self.assertEqual(json.load(urllib.request.urlopen(url+'/api/health'))['status'],'ok')
   finally:p.terminate();p.wait();p.stdout.close()
