"""Same-origin portal and private server-to-server session introspection."""
import hmac
from pathlib import Path
from .http_app import AccountApp
from .security import AuthError, csrf_token, verify_password


class PortalApp(AccountApp):
    def __init__(self, *args, bridge_key, stn_link_validator=None, **kwargs):
        if len(bridge_key)<43: raise ValueError('Use a random bridge secret of at least 43 characters')
        self.bridge_key=bridge_key
        self.stn_link_validator=stn_link_validator
        super().__init__(*args, **kwargs)

    def dispatch(self, env):
        path,method=env.get('PATH_INFO','/'),env['REQUEST_METHOD']
        if env.get('HTTP_HOST')!=self.authority: raise AuthError('Unrecognised host',400)
        if path in {'/internal/portal/introspect','/internal/portal/verify-password'}:
            key=env.get('HTTP_X_PORTAL_KEY','')
            if method!='POST' or not hmac.compare_digest(key,self.bridge_key): raise AuthError('Not found',404)
            token=self.token(env)
            if path.endswith('/verify-password'):
                data=self.body(env)
                self.fields(data,{'password'})
                with self.accounts._tx() as db:
                    user=self.accounts._session(db,token)
                    row=self.accounts._user(db,user['id'])
                    return 200,{'valid':verify_password(data['password'],row['password_hash'])},[]
            return 200,self.accounts.introspect(token),[]
        static={'/':'portal.html','/portal':'portal.html','/portal/manage':'portal.html',
                '/portal.js':'portal.js','/portal.css':'portal.css'}
        if method=='GET' and path in static:
            name=static[path]
            kind='text/javascript' if name.endswith('.js') else 'text/css' if name.endswith('.css') else 'text/html'
            return 200,(Path(__file__).parent/'portal_static'/name).read_bytes(),[('Content-Type',kind+'; charset=utf-8')]
        if method=='GET' and path=='/workspace':
            return 302,b'',[('Location','/calculator')]
        if method=='GET' and path=='/account':
            return super().dispatch(dict(env,PATH_INFO='/'))
        if path.startswith('/api/portal/'):
            if env.get('QUERY_STRING'): raise AuthError('Query parameters not accepted',400)
            token=self.token(env)
            self.accounts.me(token)
            if method=='GET' and path=='/api/portal/state': return 200,self.accounts.overview(token),[]
            if method!='POST': raise AuthError('Not found',404)
            if env.get('HTTP_ORIGIN')!=self.origin or not hmac.compare_digest(env.get('HTTP_X_CSRF_TOKEN',''),csrf_token(token)): raise AuthError('Security token is missing or expired',403)
            body=self.body(env)
            if path=='/api/portal/start-workbook':
                self.fields(body,{'name','state','period','start','end','cutoff'},{'project'})
                # Atomic first-workbook setup with the existing ownership/quota checks.
                with self.accounts._tx() as db:
                    user=self.store.user(db,token,'edit_ledger')
                    from .security import require_permission
                    require_permission(user,'edit_schemes')
                    for key in ('name','state','period'):
                        if not isinstance(body[key],str) or not body[key].strip() or len(body[key])>100:
                            raise AuthError('Enter a valid '+key,400)
                    project=body.get('project')
                    if project:self.store.row(db,user['id'],project,kind='projects')
                    else:project=self.store.request(token,'POST','projects',data={'data':{'name':'My CN Work'}})['id']
                    book=self.store.request(token,'POST','workbooks',data={'project':project,'data':{'name':body['name'].strip(),'state':body['state'].strip(),'season':body['period'].strip()}})
                    _,revision,_=self.ledger.load(db,user['id'],book['id'])
                    self.ledger.config(token,book['id'],{'revision':revision,'periods':[{'name':body['period'].strip(),'start':body['start'],'end':body['end'],'cutoff':body['cutoff']}]})
                    return 201,{'project':project,'workbook':book['id']},[]
            if path=='/api/portal/update-user':
                self.fields(body,{'user_id','cn','stn','changes'},{'temporary_password'})
                with self.accounts._tx() as db:
                    self.accounts.update_user(token,body['user_id'],body['changes'])
                    changes={k:body[k] for k in ('user_id','cn','stn')}
                    target=self.accounts._user(db,body['user_id'])
                    from . import account_roles as roles
                    meta=roles.public(db,self.accounts._public_user(target))
                    if body['stn'] and not self.accounts._policy(db,meta)['stn_member_id']:
                        parent=self.accounts._user(db,meta.get('parent_admin'))
                        policy=self.accounts._policy(db,roles.public(db,self.accounts._public_user(parent))) if parent else None
                        if not policy or not policy['stn'] or not policy['stn_member_id']:raise AuthError('Company needs an approved STN link before enabling access',409)
                        changes['stn_member_id']=policy['stn_member_id']
                    self.accounts.access(token,changes)
                    if body.get('temporary_password'):self.accounts.reset_password(token,body['user_id'],body['temporary_password'])
                return 200,{'saved':True},[]
            if path in {'/api/portal/provision','/api/portal/activate'}:
                member=None
                if body.get('member_id'):
                    if not self.stn_link_validator:raise AuthError('STN verification unavailable',503)
                    member=self.stn_link_validator(token,str(body['member_id']))
                    if not member.get('exists'):raise AuthError('Signup member not found',404)
                if path.endswith('/activate'):
                    if not member:raise AuthError('Member required',400)
                    return 200,self.accounts.activate_provision(token,member),[]
                return 201,self.accounts.provision(token,body,member),[]
            if path=='/api/portal/company': return 200,self.accounts.company(token,body),[]
            if path=='/api/portal/access':
                linked=None
                if body.get('stn_member_id') is not None:
                    actor=self.accounts.me(token)
                    if actor['role'] not in {'superadmin','admin'}:raise AuthError('Administrator required',403)
                    if not isinstance(body['stn_member_id'],str):raise AuthError('Invalid STN member ID',400)
                    if self.stn_link_validator:
                        linked=self.stn_link_validator(token,body['stn_member_id'])
                        if not linked.get('exists'):raise AuthError('STN member ID was not found; nothing was linked',400)
                return 200,self.accounts.access(token,body) | ({'linked_member':linked} if linked else {}),[]
            if path=='/api/portal/revoke':
                self.fields(body,{'user_id'})
                return 200,self.accounts.revoke(token,body['user_id']),[]
            raise AuthError('Not found',404)
        return super().dispatch(env)
