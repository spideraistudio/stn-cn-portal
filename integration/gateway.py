"""Shared route dispatcher; launch/security policies belong to each entry point."""
import http.client
import json
from urllib.parse import urlsplit

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
            headers['X-Forwarded-Proto']=urlsplit(self.app.origin).scheme
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
