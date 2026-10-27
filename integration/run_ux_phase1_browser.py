"""Real gateway/identity/Next/Chromium with isolated CN-only synthetic accounts.
No Mongo data is needed or modified; approved-member report/closure routes keep
existing STN policy and are not re-certified by this targeted check.
"""
import os,sys,tempfile,subprocess,time,socket,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'cn/backend'),str(ROOT/'cn/tests'),str(ROOT/'integration')]
from cn_web.portal import PortalAccounts
from cn_web.security import PERMISSIONS
from test_accounts_http import Browser
from run_local import frontend_fingerprint
PASSWORD='Synthetic UX phase one password!'
def port():
 with socket.socket() as s:s.bind(('127.0.0.1',0));return s.getsockname()[1]
with tempfile.TemporaryDirectory(prefix='cn-ux-phase1-') as temp:
 a=PortalAccounts(Path(temp)/'cn');a.bootstrap('platform',PASSWORD,quota_bytes=1024**3);root=a.login('platform',PASSWORD,'test')
 co=a.company(root,{'name':'UX synthetic company','cn':True,'stn':False})
 admin=a.create_user(root,username='fresh-admin',temporary_password=PASSWORD,permissions=sorted(PERMISSIONS),role='admin')
 a.access(root,{'user_id':admin['id'],'company_id':co['id'],'cn':True,'stn':False})
 token=a.login('fresh-admin',PASSWORD,'test');a.change_password(token,PASSWORD,PASSWORD+' changed')
 public,identity,node=port(),port(),port();origin=f'http://127.0.0.1:{public}'
 (ROOT/'.next/portal-source-fingerprint').write_text(frontend_fingerprint())
 with open(ROOT/'verification/ux_phase1_browser_server.txt','w') as log:
  process=subprocess.Popen([sys.executable,'integration/run_local.py','--data',str(Path(temp)/'cn'),'--port',str(public),'--identity-port',str(identity),'--node-port',str(node)],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,env={**os.environ,'MONGODB_URI':'mongodb://127.0.0.1:27017/integration_ux_phase1','NEXT_TELEMETRY_DISABLED':'1'})
  try:
   for _ in range(90):
    if process.poll() is not None:raise RuntimeError('Local gateway exited')
    try:
     if Browser(origin).request('/health')[0]==200:break
    except Exception:pass
    time.sleep(1)
   else:raise RuntimeError('Startup timed out')
   subprocess.run(['node','integration/browser_ux_phase1.mjs',json.dumps({'origin':origin,'password':PASSWORD+' changed'})],cwd=ROOT,env=os.environ,check=True)
  finally:
   process.terminate()
   try:process.wait(timeout=10)
   except subprocess.TimeoutExpired:process.kill();process.wait()
