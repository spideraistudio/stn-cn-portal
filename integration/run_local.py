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
sys.path.insert(0,str(ROOT/'cn'/'backend'))
from cn_web.portal import PortalAccounts
from cn_web.portal_http import PortalApp

class ThreadedServer(ThreadingMixIn, WSGIServer):
    daemon_threads=True

class Quiet(WSGIRequestHandler):
    def log_message(self,*args): pass

class Gateway:
    STATIC={'/','/portal','/portal/manage','/portal.js','/portal.css','/account','/account.js','/account.css','/calculator','/workspace','/workspace.js','/ledger','/ledger.js','/health','/app.js','/polish.js','/ui-theme.js','/studio.js','/payment-workbench.js','/scheme-options.js','/cd-card-display.js','/studio.css','/style.css','/cd-card-display.css','/studio-art.svg','/app.ico','/fonts/Manrope.ttf','/web-session.js','/web-bridge.js','/billing-audit.js','/audit-product-mapping.js','/audit-categories.js','/audit-categories.css','/suite-theme.js','/suite-theme.css','/ledger-panel.js'}
    API=('/api/auth/','/api/admin/users','/api/admin/audit','/api/me','/api/workspace','/api/data/','/api/calculator/','/api/ledger/','/api/projects/','/api/files/','/api/storage/','/api/portal/')
    def __init__(self,app,node_port=3000): self.app,self.node_port=app,node_port
    def __call__(self,env,start):
        path=env.get('PATH_INFO','/')
        def error(code,message):
            data=json.dumps({'error':message}).encode();start(code,[('Content-Type','application/json'),('Content-Length',str(len(data))),('Cache-Control','no-store')]);return [data]
        if env.get('HTTP_HOST')!=self.app.authority:return error('400 Bad Request','Unrecognised host')
        if path.startswith('/internal/'):return error('404 Not Found','Not found')
        if env['REQUEST_METHOD'] not in {'GET','HEAD','OPTIONS'} and env.get('HTTP_ORIGIN')!=self.app.origin:return error('403 Forbidden','Request origin is not allowed')
        moved={'/member/users':'/settings/users','/member/account':'/account','/member/issues':'/settings/issues','/member/about':'/about','/member/contact':'/contact'}
        if env['REQUEST_METHOD']=='GET' and path in moved:
            start('302 Found',[('Location',moved[path]),('Cache-Control','no-store')]);return [b'']
        if path in self.STATIC or any(path==p or path.startswith(p if p.endswith("/") else p+"/") for p in self.API):return self.app(env,start)
        if path in {'/login','/admin-login','/forgot-password','/member/password','/admin/security'}:
            start('302 Found',[('Location','/account' if path in {'/member/password','/admin/security'} else '/portal'),('Cache-Control','no-store')]);return [b'']
        if path in {'/logout','/admin-logout'}:
            start('302 Found',[('Location','/portal/logout'),('Cache-Control','no-store')]);return [b'']
        try:
            length=int(env.get('CONTENT_LENGTH') or 0)
            if length<0 or length>16*1024*1024:return error('413 Payload Too Large','Request too large')
            headers={k[5:].replace('_','-'):v for k,v in env.items() if k.startswith('HTTP_') and k not in {'HTTP_CONNECTION','HTTP_X_PORTAL_KEY'} and not k.startswith('HTTP_X_FORWARDED')}
            headers['Host']=self.app.authority
            headers['X-Forwarded-Host']=self.app.authority
            headers['X-Forwarded-Proto']='http'
            if env.get('CONTENT_TYPE'):headers['Content-Type']=env['CONTENT_TYPE']
            if length:headers['Content-Length']=str(length)
            target='/' if path=='/stn' else path
            if env.get('QUERY_STRING'):target+='?'+env['QUERY_STRING']
            connection=http.client.HTTPConnection('127.0.0.1',self.node_port,timeout=90)
            try:
                connection.request(env['REQUEST_METHOD'],target,env['wsgi.input'].read(length) if length else None,headers)
                response=connection.getresponse();data=response.read()
                outgoing=[(k,v) for k,v in response.getheaders() if k.lower() not in {'connection','transfer-encoding','content-length','keep-alive'}]
                outgoing.append(('Content-Length',str(len(data))))
                start(f'{response.status} {response.reason}',outgoing);return [data]
            finally:connection.close()
        except (OSError,http.client.HTTPException):return error('503 Service Unavailable','STN is starting or unavailable. Retry shortly.')

class InternalOnly:
    def __init__(self,app):self.app=app
    def __call__(self,env,start):
        if env.get('PATH_INFO') not in {'/internal/portal/introspect','/internal/portal/verify-password'}:
            start('404 Not Found',[('Content-Type','text/plain')]);return [b'Not found']
        # The private listener has its own port. Identity is established by the
        # bridge secret, never by a browser Host/user/role header.
        return self.app(dict(env,HTTP_HOST=self.app.authority),start)

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
