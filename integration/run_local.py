"""Local integration gateway. Never opens a non-loopback database or interface."""
import argparse
from getpass import getpass
import http.client
import json
import hashlib
import os
from pathlib import Path
import secrets
import signal
import subprocess
import sys
import threading
from urllib.parse import urlsplit
from wsgiref.simple_server import make_server, WSGIServer, WSGIRequestHandler
from socketserver import ThreadingMixIn

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
sys.path.insert(0,str(ROOT/'cn'/'backend'))
from cn_web.portal import PortalAccounts
from cn_web.portal_http import PortalApp

class ThreadedServer(ThreadingMixIn, WSGIServer):
    daemon_threads=True

class Quiet(WSGIRequestHandler):
    def log_message(self,*args): pass

from integration.gateway import Gateway, InternalOnly

def frontend_fingerprint():
    digest=hashlib.sha256()
    files=[]
    for folder in ('app','components','lib','hooks','db','public','vendor'):
        files.extend(p for p in (ROOT/folder).rglob('*') if p.is_file())
    files.extend(ROOT/name for name in ('package.json','package-lock.json','next.config.ts','proxy.ts','tsconfig.json','postcss.config.mjs','components.json'))
    for p in sorted(files):
        digest.update(str(p.relative_to(ROOT)).encode());digest.update(p.read_bytes())
    return digest.hexdigest()

def ensure_frontend_build(env):
    stamp=ROOT/'.next/portal-source-fingerprint'
    fingerprint=frontend_fingerprint()
    if (ROOT/'.next/BUILD_ID').exists() and stamp.exists() and stamp.read_text()==fingerprint:return
    print('Preparing STN frontend for local use. First start/update can take a few minutes; keep this window open.',flush=True)
    subprocess.run(['node',str(ROOT/'node_modules/next/dist/bin/next'),'build'],cwd=ROOT,env={**env,'NODE_ENV':'production','NEXT_TELEMETRY_DISABLED':'1'},check=True)
    stamp.write_text(fingerprint)

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--data',type=Path,default=ROOT/'integration-data'/'cn')
    parser.add_argument('--port',type=int,default=8787)
    parser.add_argument('--identity-port',type=int,default=8788)
    parser.add_argument('--node-port',type=int,default=3000)
    parser.add_argument('--setup-admin',action='store_true')
    parser.add_argument('--no-node',action='store_true')
    parser.add_argument('--node-mode',choices=['dev','start'],default='start')
    args=parser.parse_args()
    def terminate(signum, frame):raise KeyboardInterrupt
    signal.signal(signal.SIGTERM,terminate)
    accounts=PortalAccounts(args.data)
    if args.setup_admin:
        name=input('Platform superadmin username: ').strip()
        password=getpass('New password (12–128 characters): ')
        if password!=getpass('Repeat password: '):raise SystemExit('Passwords do not match')
        accounts.bootstrap(name,password,quota_bytes=1024**3)
        print('Platform account created. Start the combined application next.');return
    mongo=os.environ.get('MONGODB_URI','mongodb://127.0.0.1:27017/integration_stn')
    parsed=urlsplit(mongo)
    if parsed.hostname not in {'127.0.0.1','localhost'} or not parsed.path.startswith('/integration_'):
        raise SystemExit('Local testing requires a loopback MongoDB and an integration_ database. Live databases are deliberately refused.')
    args.data.mkdir(parents=True,exist_ok=True)
    secret_file=args.data.parent/'portal-secrets.json'
    if not secret_file.exists():
        fd=os.open(secret_file,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
        with os.fdopen(fd,'w') as f:json.dump({'bridge':secrets.token_urlsafe(48),'lookup':secrets.token_urlsafe(48)},f)
    config=json.loads(secret_file.read_text())
    origin=f'http://127.0.0.1:{args.port}'
    def validate_stn_link(token,member_id):
        from urllib.parse import urlencode
        from cn_web.security import AuthError
        connection=http.client.HTTPConnection('127.0.0.1',args.node_port,timeout=8)
        try:
            connection.request('GET','/api/portal-stn/link-check?'+urlencode({'id':member_id}),headers={'Host':urlsplit(origin).netloc,'Cookie':'cn_dev_session='+token})
            response=connection.getresponse();body=json.loads(response.read())
            if response.status!=200:raise AuthError('STN member verification failed; link was not saved',503)
            return body
        except (OSError,ValueError,http.client.HTTPException):
            raise AuthError('STN unavailable; link was not saved',503) from None
        finally:connection.close()
    app=PortalApp(accounts,origin=origin,development=True,bridge_key=config['bridge'],stn_link_validator=validate_stn_link)
    from cn_web import storage_ops
    with accounts._tx() as db:storage_ops.cleanup(db,accounts)
    stop_cleanup=threading.Event()
    def maintenance():
        while not stop_cleanup.wait(86400):
            with accounts._tx() as db:storage_ops.cleanup(db,accounts)
    threading.Thread(target=maintenance,daemon=True).start()
    internal=make_server('127.0.0.1',args.identity_port,InternalOnly(app),server_class=ThreadedServer,handler_class=Quiet)
    threading.Thread(target=internal.serve_forever,daemon=True).start()
    child=None
    if not args.no_node:
        env={**os.environ,'PORTAL_MODE':'combined','PORTAL_COOKIE_NAME':'cn_dev_session','NEXT_PUBLIC_COMMON_PORTAL':'1','PORTAL_BRIDGE_KEY':config['bridge'],'PORTAL_ORIGIN':origin,'PORTAL_IDENTITY_URL':f'http://127.0.0.1:{args.identity_port}/internal/portal/introspect','MONGODB_URI':mongo,'STN_MONGO_TLS':'0','ADMIN_EMAILS':os.environ.get('ADMIN_EMAILS','platform@integration.local'),'IDENTIFIER_LOOKUP_KEY':config['lookup']}
        if args.node_mode=='start':
            env['NODE_ENV']='production'
            ensure_frontend_build(env)
        child=subprocess.Popen(['node',str(ROOT/'node_modules/next/dist/bin/next'),args.node_mode,'--hostname','127.0.0.1','--port',str(args.node_port)],cwd=ROOT,env=env)
    print(f'Combined local application: {origin}/portal',flush=True)
    print('Independent test data only. No live migration or deployment.',flush=True)
    try:
        with make_server('127.0.0.1',args.port,Gateway(app,args.node_port),server_class=ThreadedServer,handler_class=Quiet) as server:server.serve_forever()
    except KeyboardInterrupt:pass
    finally:
        stop_cleanup.set();internal.shutdown();internal.server_close()
        if child:child.terminate();child.wait(timeout=15)

if __name__=='__main__':main()
