from pathlib import Path
import subprocess,zipfile,hashlib,json,tempfile,os,socket,time,urllib.request
root=Path(__file__).resolve().parents[1];out=root.parent/'STN_CN_Offline_Prior_Receipts_Update.zip';prefix='STN_CN_Offline_Prior_Receipts_Update'
names=set(subprocess.check_output(['git','ls-files'],cwd=root,text=True).splitlines())|set(subprocess.check_output(['git','ls-files','--others','--exclude-standard'],cwd=root,text=True).splitlines())
items={}
for name in sorted(names):
 p=root/name
 if not p.is_file() or any(x in p.parts for x in ('__pycache__','node_modules','.git','.next','integration-data')) or p.suffix in ('.pyc','.pyo','.sqlite','.sqlite3','.db','.zip'):continue
 b=p.read_bytes()
 if p.suffix.lower()=='.bat' and not name.startswith('cn/offline_baseline/'):b=b.replace(b'\r\n',b'\n').replace(b'\n',b'\r\n')
 items[name]=b
manifest={n:hashlib.sha256(b).hexdigest() for n,b in items.items()}
items['PRIOR_RECEIPTS_PACKAGE_SHA256.json']=json.dumps({'base_commit':'aa4e8937c6d826e6567ef37c8d5b2c23878ef9eb','files':manifest},indent=2).encode()
with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
 for n,b in items.items():z.writestr(prefix+'/'+n,b)
with zipfile.ZipFile(out) as z:
 assert z.testzip() is None
 with tempfile.TemporaryDirectory() as temp:
  z.extractall(temp);program=Path(temp)/prefix
  for n,h in manifest.items():assert hashlib.sha256((program/n).read_bytes()).hexdigest()==h,n
  subprocess.run(['python','cn/verify_baseline.py','--allow-private-fixtures'],cwd=program,check=True)
  subprocess.run(['python','-m','compileall','-q','cn/backend'],cwd=program,check=True)
  for n in ('cn/backend/cn_web/calculator_static/app.js','cn/backend/cn_web/calculator_static/web-bridge.js','integration/browser_prior_payments.cjs'):
   subprocess.run(['node','--check',str(program/n)],check=True)
  def port():
   with socket.socket() as s:s.bind(('127.0.0.1',0));return s.getsockname()[1]
  public,private=port(),port()
  p=subprocess.Popen(['python','integration/run_local.py','--no-node','--port',str(public),'--identity-port',str(private),'--data',str(Path(temp)/'test-data/cn')],cwd=program,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE)
  try:
   for i in range(100):
    try:
     with urllib.request.urlopen('http://127.0.0.1:'+str(public)+'/health',timeout=1) as r:assert r.status==200
     break
    except OSError:
     if p.poll() is not None:raise RuntimeError(p.stderr.read().decode())
     time.sleep(.1)
   else:raise RuntimeError('Extracted gateway startup failed')
   for path in ['/portal','/portal.js','/suite-theme.css']:
    with urllib.request.urlopen('http://127.0.0.1:'+str(public)+path,timeout=3) as r:assert r.status==200
  finally:p.terminate();p.communicate(timeout=10)
print(json.dumps({'zip':str(out),'files':len(items),'bytes':out.stat().st_size,'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'checks':'ZIP CRC, all content hashes, extracted baseline, Python compilation, changed JavaScript syntax and isolated extracted combined gateway/portal startup passed. Node/Mongo full stack and native Windows installation not rerun.'}))
