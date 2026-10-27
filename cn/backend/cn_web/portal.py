"""Common identity and company policy. Financial ownership remains individual."""
import uuid
import threading
from contextlib import contextmanager
from .unified_accounts import UnifiedAccounts
from .accounts import Accounts
from . import account_roles as roles, storage_ops
from .security import AuthError


class PortalAccounts(UnifiedAccounts, Accounts):
    def __init__(self, *args, **kwargs):
        self._nested_tx=threading.local()
        super().__init__(*args, **kwargs)
        with self._tx() as db:
            db.executescript('''
              CREATE TABLE IF NOT EXISTS portal_provisioning(member_id TEXT PRIMARY KEY,user_id TEXT NOT NULL,completed INTEGER NOT NULL,config_digest TEXT NOT NULL);
              CREATE TABLE IF NOT EXISTS portal_companies (
                id TEXT PRIMARY KEY, name TEXT NOT NULL, enabled INTEGER NOT NULL,
                cn INTEGER NOT NULL, stn INTEGER NOT NULL, starts_at REAL, ends_at REAL,
                plan TEXT NOT NULL, revision INTEGER NOT NULL DEFAULT 1);
              CREATE TABLE IF NOT EXISTS portal_memberships (
                user_id TEXT PRIMARY KEY, company_id TEXT,
                cn INTEGER NOT NULL DEFAULT 1, stn INTEGER NOT NULL DEFAULT 0,
                stn_member_id TEXT);
            ''')
            if not db.in_transaction:
                db.execute('BEGIN IMMEDIATE')
            # Earlier local candidates used a one-to-one link. Keep their IDs
            # while allowing explicitly granted staff access to one company member.
            if any(r['unique'] for r in db.execute('PRAGMA index_list(portal_memberships)') if r['origin']=='u'):
                db.execute('ALTER TABLE portal_memberships RENAME TO portal_memberships_old')
                db.execute('CREATE TABLE portal_memberships(user_id TEXT PRIMARY KEY,company_id TEXT,cn INTEGER NOT NULL DEFAULT 1,stn INTEGER NOT NULL DEFAULT 0,stn_member_id TEXT)')
                db.execute('INSERT INTO portal_memberships SELECT * FROM portal_memberships_old')
                db.execute('DROP TABLE portal_memberships_old')

    @contextmanager
    def _tx(self):
        active=getattr(self._nested_tx,'db',None)
        if active is not None:
            yield active
            return
        with super()._tx() as db:
            self._nested_tx.db=db
            try:yield db
            finally:self._nested_tx.db=None

    def _policy(self, db, user):
        m = db.execute('SELECT * FROM portal_memberships WHERE user_id=?', (user['id'],)).fetchone()
        # Legacy CN accounts remain independent until explicitly assigned.
        cn, stn, company = True, user['role'] == 'superadmin', None
        if m:
            cn, stn = bool(m['cn']), bool(m['stn'])
            if m['company_id']:
                c = db.execute('SELECT * FROM portal_companies WHERE id=?', (m['company_id'],)).fetchone()
                company = dict(c) if c else None
                active = bool(c and c['enabled'] and (c['starts_at'] is None or c['starts_at'] <= self.clock())
                              and (c['ends_at'] is None or self.clock() < c['ends_at']))
                cn = bool(cn and active and c['cn'])
                stn = bool(stn and active and c['stn'])
        if user['role'] == 'user' and user.get('parent_admin'):
            parent = db.execute('SELECT * FROM portal_memberships WHERE user_id=?', (user['parent_admin'],)).fetchone()
            if parent:
                cn, stn = cn and bool(parent['cn']), stn and bool(parent['stn'])
        return {'company': company, 'cn': cn, 'stn': stn,
                'stn_member_id': m['stn_member_id'] if m else None,
                'requested_cn': bool(m['cn']) if m else True,
                'requested_stn': bool(m['stn']) if m else user['role'] == 'superadmin'}

    def _session(self, db, token, **kwargs):
        user = super()._session(db, token, **kwargs)
        policy = self._policy(db, user)
        if kwargs.get('permission') and not policy['cn']:
            raise AuthError('CN Calculator access is disabled', 403)
        user['modules'] = {'cn': policy['cn'], 'stn': policy['stn']}
        user['company_id'] = policy['company']['id'] if policy['company'] else None
        return user

    def _created_account(self, db, uid, parent_admin):
        parent = db.execute('SELECT company_id FROM portal_memberships WHERE user_id=?', (parent_admin,)).fetchone()
        db.execute('INSERT INTO portal_memberships(user_id,company_id) VALUES(?,?)', (uid, parent[0] if parent else None))

    def _reassign_account(self, db, uid, parent_admin):
        # Reassignment is explicit superadmin work; retain identity and all CN data.
        parent=db.execute('SELECT company_id FROM portal_memberships WHERE user_id=?',(parent_admin,)).fetchone()
        cid=parent[0] if parent else None
        old=db.execute('SELECT company_id FROM portal_memberships WHERE user_id=?',(uid,)).fetchone()
        if old and old[0]!=cid:
            db.execute('UPDATE portal_memberships SET stn=0,stn_member_id=NULL WHERE user_id=?',(uid,))
        db.execute('INSERT INTO portal_memberships(user_id,company_id) VALUES(?,?) ON CONFLICT(user_id) DO UPDATE SET company_id=excluded.company_id',(uid,cid))

    def overview(self, token):
        with self._tx() as db:
            actor = self._session(db, token)
            p = self._policy(db, actor)
            users, companies = [], []
            if actor['is_admin'] and actor['manage_users']:
                for r in db.execute('SELECT u.*,w.enabled,w.quota_bytes FROM users u JOIN workspaces w ON w.user_id=u.id').fetchall():
                    user = roles.public(db, self._public_user(r))
                    if actor['role'] == 'superadmin' or user.get('parent_admin') == actor['id']:
                        policy = self._policy(db, user)
                        users.append(user | policy | storage_ops.status(db, user['id']))
                if actor['role'] == 'superadmin':
                    companies = [dict(r) for r in db.execute('SELECT * FROM portal_companies ORDER BY name')]
            return {'user': actor, 'policy': p, 'users': users, 'companies': companies,
                    'stn_storage': {'accounting': 'separate', 'source': '/api/portal-stn/storage'}}

    def company(self, token, body):
        allowed = {'id','name','enabled','cn','stn','starts_at','ends_at','plan','revision'}
        if set(body) - allowed: raise AuthError('Unsupported company field',400)
        if body.get('id') is not None and (not isinstance(body['id'],str) or not __import__('re').fullmatch(r'[a-f0-9]{32}',body['id'])): raise AuthError('Invalid company ID',400)
        with self._tx() as db:
            actor = self._session(db, token, admin=True)
            if actor['role'] != 'superadmin': raise AuthError('Platform superadmin required',403)
            cid = body.get('id') or uuid.uuid4().hex
            old = db.execute('SELECT * FROM portal_companies WHERE id=?',(cid,)).fetchone()
            if body.get('id') and not old: raise AuthError('Company not found',404)
            if old and body.get('revision') != old['revision']: raise AuthError('Reload company before saving',409)
            data = dict(old) if old else {'id':cid,'enabled':True,'cn':True,'stn':False,'starts_at':None,'ends_at':None,'plan':'CN-only','revision':0}
            data.update(body)
            if not isinstance(data.get('name'),str) or not 1<=len(data['name'].strip())<=160: raise AuthError('Company name required',400)
            for k in ('cn','stn','enabled'):
                if k in body and type(body[k]) is not bool: raise AuthError('Module switches must be boolean',400)
            for k in ('starts_at','ends_at'):
                if data[k] is not None and (type(data[k]) not in (int,float) or not 0<=data[k]<=253402300799): raise AuthError('Invalid subscription date',400)
            if data['starts_at'] is not None and data['ends_at'] is not None and data['starts_at']>=data['ends_at']: raise AuthError('End must follow start',400)
            if not isinstance(data['plan'],str) or len(data['plan'])>160: raise AuthError('Invalid plan',400)
            data['revision'] = (old['revision'] if old else 0)+1
            db.execute('INSERT OR REPLACE INTO portal_companies VALUES(?,?,?,?,?,?,?,?,?)',tuple(data[k] for k in ('id','name','enabled','cn','stn','starts_at','ends_at','plan','revision')))
            # Terminate sessions on entitlement changes; no session restoration on re-enable.
            db.execute('DELETE FROM sessions WHERE user_id IN (SELECT user_id FROM portal_memberships WHERE company_id=?)',(cid,))
            self.audit(db,actor['id'],'portal_company_saved',cid,revision=data['revision'])
            return data

    def access(self, token, body):
        if set(body)-{'user_id','company_id','cn','stn','stn_member_id'} or 'user_id' not in body: raise AuthError('Invalid access fields',400)
        if not isinstance(body['user_id'],str) or not __import__('re').fullmatch(r'[a-f0-9]{32}',body['user_id']): raise AuthError('Invalid user ID',400)
        if body.get('company_id') is not None and (not isinstance(body['company_id'],str) or not __import__('re').fullmatch(r'[a-f0-9]{32}',body['company_id'])): raise AuthError('Invalid company ID',400)
        with self._tx() as db:
            actor = self._session(db,token,admin=True)
            meta = roles.target(db,actor,body['user_id'])
            target = self._user(db,body['user_id'])
            if not target: raise AuthError('Account not found',404)
            if 'company_id' in body and actor['role']!='superadmin': raise AuthError('Only superadmin may assign companies',403)
            if 'stn_member_id' in body and actor['role']!='superadmin':
                own=self._policy(db,actor)
                if not actor['modules']['stn'] or not own['stn_member_id'] or body['stn_member_id']!=own['stn_member_id']:
                    raise AuthError('You may grant only your explicitly linked company STN membership',403)
            old = db.execute('SELECT * FROM portal_memberships WHERE user_id=?',(target['id'],)).fetchone()
            data = dict(old) if old else {'user_id':target['id'],'company_id':None,'cn':1,'stn':int(meta['role']=='superadmin'),'stn_member_id':None}
            data.update(body)
            if old and old['stn_member_id'] is not None and data['company_id']!=old['company_id'] and 'stn_member_id' not in body:
                data['stn_member_id']=None
                data['stn']=0
            for k in ('cn','stn'):
                if k in body and type(body[k]) is not bool: raise AuthError('Module switch must be boolean',400)
                if actor['role']!='superadmin' and data[k] and not actor['modules'][k]: raise AuthError('Module exceeds delegated access',403)
            cid = data['company_id']
            if cid and not db.execute('SELECT 1 FROM portal_companies WHERE id=?',(cid,)).fetchone(): raise AuthError('Company not found',404)
            if meta['role']=='superadmin' and cid: raise AuthError('Platform operator stays outside customer companies',400)
            if meta['role']=='user' and meta['parent_admin']:
                parent=db.execute('SELECT company_id FROM portal_memberships WHERE user_id=?',(meta['parent_admin'],)).fetchone()
                if cid != (parent[0] if parent else None): raise AuthError('User and managing admin must belong to the same company',409)
            if meta['role']=='admin' and cid != (old['company_id'] if old else None):
                if db.execute("SELECT 1 FROM account_roles WHERE parent_admin=? AND role='user'",(target['id'],)).fetchone(): raise AuthError('Assign admin company before adding users; reassign children explicitly first',409)
            link=data['stn_member_id']
            if link is not None and (not isinstance(link,str) or not __import__('re').fullmatch(r'[a-fA-F0-9]{24}|[0-9]+',link)): raise AuthError('Use an exact existing STN member ID',400)
            if link is not None:
                other=db.execute('SELECT user_id,company_id FROM portal_memberships WHERE stn_member_id=? AND user_id!=?',(link,target['id'])).fetchall()
                if any(not cid or r['company_id']!=cid for r in other):raise AuthError('This STN membership belongs to another company assignment',409)
                if cid and db.execute('SELECT 1 FROM portal_memberships WHERE company_id=? AND stn_member_id IS NOT NULL AND stn_member_id!=? AND user_id!=?',(cid,link,target['id'])).fetchone():raise AuthError('Company already has another STN membership; explicitly unlink it before changing',409)
            try:
                db.execute('INSERT INTO portal_memberships VALUES(?,?,?,?,?) ON CONFLICT(user_id) DO UPDATE SET company_id=excluded.company_id,cn=excluded.cn,stn=excluded.stn,stn_member_id=excluded.stn_member_id',tuple(data[k] for k in ('user_id','company_id','cn','stn','stn_member_id')))
            except __import__('sqlite3').IntegrityError: raise AuthError('Account link conflict',409) from None
            db.execute('DELETE FROM sessions WHERE user_id=?',(target['id'],))
            if meta['role']=='admin': db.execute('DELETE FROM sessions WHERE user_id IN (SELECT user_id FROM account_roles WHERE parent_admin=?)',(target['id'],))
            self.audit(db,actor['id'],'portal_access_saved',target['id'],company_id=cid,cn=bool(data['cn']),stn=bool(data['stn']),stn_member_id=link)
            return {'saved':True}

    def revoke(self,token,uid):
        if not isinstance(uid,str) or not __import__('re').fullmatch(r'[a-f0-9]{32}',uid): raise AuthError('Invalid user ID',400)
        with self._tx() as db:
            actor=self._session(db,token,admin=True)
            roles.target(db,actor,uid)
            db.execute('DELETE FROM sessions WHERE user_id=?',(uid,))
            self.audit(db,actor['id'],'portal_sessions_revoked',uid)
        return {'revoked':True}

    def introspect(self, token):
        with self._tx() as db:
            user=self._session(db,token)
            return {'id':user['id'],'username':user['username'],'role':user['role'],
                    'modules':user['modules'],'manage_users':bool(user['manage_users']),'stn_member_id':self._policy(db,user)['stn_member_id']}
