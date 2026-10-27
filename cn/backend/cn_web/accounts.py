"""Transactional accounts and opaque server-side sessions for the web service.

All API mutations reauthorize the session within the transaction. No client
user ID, role header or existing offline local token is an identity source.
"""
from contextlib import contextmanager, closing
import json
import os
import re
import secrets
import sqlite3
import time
import uuid

from .security import (AuthError, PERMISSIONS, checked_permissions, hash_password,
                       verify_password, session_hash, require_permission)
from .workspaces import WorkspaceRegistry, WorkspaceDenied
from . import storage_ops, account_roles as roles


class Accounts:
    SESSION_SECONDS = 8 * 60 * 60
    IDLE_SECONDS = 30 * 60
    ATTEMPT_WINDOW = 15 * 60
    USER_ATTEMPTS = 5
    IP_ATTEMPTS = 30

    def __init__(self, root, *, clock=time.time):
        self.registry = WorkspaceRegistry(root)
        if os.name == "posix":
            os.chmod(self.registry.root, 0o700)
            os.chmod(self.registry.path, 0o600)
        self.clock = clock
        with self._tx() as db:
            db.executescript("""
                CREATE TABLE IF NOT EXISTS users (
                    id TEXT PRIMARY KEY, username TEXT NOT NULL UNIQUE,
                    password_hash TEXT NOT NULL, is_admin INTEGER NOT NULL,
                    must_change INTEGER NOT NULL, permissions TEXT NOT NULL,
                    created_at REAL NOT NULL);
                CREATE TABLE IF NOT EXISTS sessions (
                    token_hash TEXT PRIMARY KEY, user_id TEXT NOT NULL,
                    created_at REAL NOT NULL, last_seen REAL NOT NULL,
                    expires_at REAL NOT NULL);
                CREATE INDEX IF NOT EXISTS session_users ON sessions(user_id);
                CREATE TABLE IF NOT EXISTS auth_audit (
                    id INTEGER PRIMARY KEY, at REAL NOT NULL, actor TEXT,
                    action TEXT NOT NULL, target TEXT, details TEXT NOT NULL);
                CREATE TABLE IF NOT EXISTS login_attempts (
                    at REAL NOT NULL, username TEXT NOT NULL, ip TEXT NOT NULL);
                CREATE INDEX IF NOT EXISTS attempt_time ON login_attempts(at);
            """)
        with self._tx() as db:
            storage_ops.initialize(db)
            roles.initialize(db)
            if "appearance" not in {r[1] for r in db.execute("PRAGMA table_info(sessions)")}:
                db.execute("ALTER TABLE sessions ADD COLUMN appearance TEXT NOT NULL DEFAULT 'studio'")
        # Equal-cost dummy verification for unknown usernames; never a login.
        self._dummy_hash = hash_password(secrets.token_urlsafe(32))

    @contextmanager
    def _tx(self):
        with closing(sqlite3.connect(self.registry.path, timeout=15)) as db:
            db.row_factory = sqlite3.Row
            db.execute("BEGIN IMMEDIATE")
            with db:
                before = storage_ops.usage(db)
                yield db
                storage_ops.enforce(db, before)

    @staticmethod
    def username(value):
        if not isinstance(value, str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.@+-]{2,79}", value):
            raise AuthError("Username must be 3–80 letters, digits or . _ @ + -", 400)
        return value.lower()

    @staticmethod
    def quota(value):
        if type(value) is not int or not 1 <= value <= 2**53 - 1:
            raise AuthError("Choose a positive storage allowance in bytes", 400)
        return value

    def audit(self, db, actor, action, target=None, **details):
        # Callers supply only named, non-secret fields. No request-body logging.
        db.execute("INSERT INTO auth_audit(at,actor,action,target,details) VALUES(?,?,?,?,?)",
                   (self.clock(), actor, action, target, json.dumps(details, sort_keys=True)))

    def _insert_user(self, db, username, password_hash, quota, permissions, *, admin=False):
        uid = uuid.uuid4().hex
        key = uuid.uuid4().hex
        try:
            db.execute("INSERT INTO users VALUES(?,?,?,?,?,?,?)",
                       (uid, username, password_hash, int(admin), int(not admin), json.dumps(permissions), self.clock()))
            db.execute("INSERT INTO workspaces VALUES(?,?,1,?)", (uid, key, quota))
        except sqlite3.IntegrityError:
            raise AuthError("That username is unavailable", 409) from None
        return uid

    def bootstrap(self, username, password, *, quota_bytes):
        """Operator-only CLI: one initial admin, never an HTTP route."""
        name, quota = self.username(username), self.quota(quota_bytes)
        hashed = hash_password(password)
        with self._tx() as db:
            if db.execute("SELECT 1 FROM users LIMIT 1").fetchone():
                raise AuthError("Administrator has already been set up", 409)
            uid = self._insert_user(db, name, hashed, quota, sorted(PERMISSIONS), admin=True)
            db.execute("INSERT INTO account_roles(user_id,role) VALUES(?,'superadmin')", (uid,))
            self.audit(db, uid, "admin_bootstrapped", uid)
        return uid

    def _public_user(self, row):
        return {"id": row["id"], "username": row["username"],
                "is_admin": bool(row["is_admin"]), "enabled": bool(row["enabled"]),
                "must_change_password": bool(row["must_change"]),
                "permissions": json.loads(row["permissions"]), "quota_bytes": row["quota_bytes"]}

    def _user(self, db, uid):
        return db.execute("SELECT u.*,w.enabled,w.quota_bytes FROM users u JOIN workspaces w ON w.user_id=u.id WHERE u.id=?", (uid,)).fetchone()

    def _session(self, db, token, *, allow_change=False, admin=False, permission=None):
        if not isinstance(token, str) or not re.fullmatch(r"[A-Za-z0-9_-]{43}", token):
            raise AuthError("Sign in to continue", 401)
        row = db.execute("SELECT * FROM sessions WHERE token_hash=?", (session_hash(token),)).fetchone()
        now = self.clock()
        if not row or row["expires_at"] <= now or row["last_seen"] + self.IDLE_SECONDS <= now:
            raise AuthError("Sign in to continue", 401)
        account = self._user(db, row["user_id"])
        if not account or not account["enabled"]:
            raise AuthError("Sign in to continue", 401)
        user = roles.public(db, self._public_user(account))
        if user.get('parent_admin') and user['role']=='user':
            parent=self._user(db,user['parent_admin'])
            if not parent or not parent['enabled']:
                raise AuthError("Sign in to continue",401)
            user['permissions']=sorted(set(user['permissions']) & set(json.loads(parent['permissions'])))
        if user["must_change_password"] and not allow_change:
            raise AuthError("Change your temporary password before continuing", 403)
        if admin and (not user["is_admin"] or not user.get("manage_users")):
            raise AuthError("Administrator access required", 403)
        if permission:
            require_permission(user, permission)
        db.execute("UPDATE sessions SET last_seen=? WHERE token_hash=?", (now, session_hash(token)))
        return user

    def login(self, username, password, ip, previous_token=""):
        # Invalid, disabled and unknown accounts return the same credential error.
        try:
            name = self.username(username)
        except AuthError:
            name = "!invalid-name!"  # Not a legal account name; cannot alias a real user.
        try:
            valid_input = isinstance(password, str) and len(password.encode()) <= 512
        except UnicodeError:
            valid_input = False
        if not valid_input:
            raise AuthError("Invalid username or password", 401)
        now = self.clock()
        failure = None
        token = None
        with self._tx() as db:
            db.execute("DELETE FROM login_attempts WHERE at<?", (now - 86400,))
            counts = db.execute("SELECT SUM(username=?),SUM(ip=?) FROM login_attempts WHERE at>?",
                                (name, ip, now - self.ATTEMPT_WINDOW)).fetchone()
            if (counts[0] or 0) >= self.USER_ATTEMPTS or (counts[1] or 0) >= self.IP_ATTEMPTS:
                failure = AuthError("Too many login attempts. Try again later", 429)
            else:
                row = db.execute("SELECT u.*,w.enabled,w.quota_bytes FROM users u JOIN workspaces w ON w.user_id=u.id WHERE username=?", (name,)).fetchone()
                valid = verify_password(password, row["password_hash"] if row else self._dummy_hash)
                parent_available=True
                if row:
                    meta=db.execute('SELECT role,parent_admin FROM account_roles WHERE user_id=?',(row['id'],)).fetchone()
                    if meta and meta['role']=='user' and meta['parent_admin']:
                        parent=self._user(db,meta['parent_admin'])
                        parent_available=bool(parent and parent['enabled'])
                if not row or not valid or not row["enabled"] or not parent_available:
                    db.execute("INSERT INTO login_attempts VALUES(?,?,?)", (now, name, ip))
                    self.audit(db, None, "login_failed", None)
                    failure = AuthError("Invalid username or password", 401)
                else:
                    if previous_token:
                        db.execute("DELETE FROM sessions WHERE token_hash=?", (session_hash(previous_token),))
                    token = secrets.token_urlsafe(32)
                    db.execute("DELETE FROM sessions WHERE expires_at<=? OR last_seen<=?", (now, now-self.IDLE_SECONDS))
                    db.execute("INSERT INTO sessions(token_hash,user_id,created_at,last_seen,expires_at) VALUES(?,?,?,?,?)", (session_hash(token), row["id"], now, now, now+self.SESSION_SECONDS))
                    db.execute("DELETE FROM login_attempts WHERE username=?", (name,))
                    self.audit(db, row["id"], "login", row["id"])
        if failure:
            raise failure
        return token

    def me(self, token):
        with self._tx() as db:
            return self._session(db, token, allow_change=True)

    def authorize(self, token, permission):
        """Read-only API boundary; financial writes must recheck in their txn."""
        with self._tx() as db:
            return self._session(db, token, permission=permission)

    def workspace(self, token):
        with self._tx() as db:
            user = self._session(db, token, permission="view_workspace")
            try:
                workspace = self.registry.resolve(user["id"])
            except WorkspaceDenied:
                raise AuthError("Workspace is unavailable", 403) from None
            return {"workspace_id": workspace.workspace_id, "quota_bytes": workspace.quota_bytes,
                    **storage_ops.status(db, user["id"]), "stage": "Phase 7 storage operations"}

    def cleanup_temporary(self, token):
        with self._tx() as db:
            user = self._session(db, token, permission="delete_records")
            return storage_ops.cleanup(db, self, user['id'])

    def list_users(self, token):
        with self._tx() as db:
            actor=self._session(db, token, admin=True)
            rows=db.execute("SELECT u.*,w.enabled,w.quota_bytes FROM users u JOIN workspaces w ON w.user_id=u.id ORDER BY username").fetchall()
            result=[]
            for row in rows:
                value=roles.public(db,self._public_user(row))
                if actor['role']=='superadmin' or value.get('parent_admin')==actor['id']:
                    result.append(value | storage_ops.status(db,row['id']))
            return result

    def create_user(self, token, *, username, temporary_password, permissions,
                    quota_bytes=None, role='user', parent_admin=None, max_users=5,
                    user_quota_bytes=roles.USER_QUOTA, manage_users=True):
        name=self.username(username)
        if parent_admin is not None and (not isinstance(parent_admin,str) or len(parent_admin)!=32):raise AuthError("Invalid parent administrator",400)
        perms,hashed=checked_permissions(permissions),hash_password(temporary_password)
        if not isinstance(role,str) or role not in {'user','admin'}:raise AuthError('Choose User or Admin',400)
        self._management_values(max_users,user_quota_bytes,manage_users)
        with self._tx() as db:
            actor=self._session(db,token,admin=True)
            if actor['role']!='superadmin':
                if role!='user' or parent_admin not in (None,actor['id']):raise AuthError('Administrator scope exceeded',403)
                parent_admin=actor['id']
            elif role=='admin':
                if parent_admin is not None:raise AuthError('Admins are managed by superadmin',400)
                parent_admin=actor['id']
            parent=None
            if role=='user' and parent_admin:
                parent=roles.capacity(db,parent_admin)
            quota=self.quota(quota_bytes if quota_bytes is not None else roles.ADMIN_QUOTA if role=='admin' else parent['user_quota_bytes'] if parent else roles.USER_QUOTA)
            roles.delegation(actor,perms,quota)
            uid=self._insert_user(db,name,hashed,quota,perms,admin=role=='admin')
            db.execute('INSERT INTO account_roles VALUES(?,?,?,?,?,?)',(uid,role,parent_admin,max_users,user_quota_bytes,int(manage_users)))
            hook = getattr(self, '_created_account', None)
            if hook:
                hook(db, uid, parent_admin)
            self.audit(db,actor['id'],'user_created',uid,role=role,parent_admin=parent_admin,quota_bytes=quota,permissions=perms)
            return roles.public(db,self._public_user(self._user(db,uid)))

    @staticmethod
    def _management_values(max_users,user_quota_bytes,manage_users):
        if type(max_users) is not int or not 0<=max_users<=10000 or type(manage_users) is not bool:
            raise AuthError('Invalid delegated management limits',400)
        Accounts.quota(user_quota_bytes)

    def update_user(self, token, uid, changes):
        allowed={'enabled','permissions','quota_bytes','parent_admin','max_users','user_quota_bytes','manage_users'}
        if not changes or set(changes)-allowed:raise AuthError('Unsupported account change',400)
        if 'enabled' in changes and type(changes['enabled']) is not bool:raise AuthError('Enabled must be true or false',400)
        changes=dict(changes)
        if 'permissions' in changes:changes['permissions']=checked_permissions(changes['permissions'])
        if 'quota_bytes' in changes:self.quota(changes['quota_bytes'])
        with self._tx() as db:
            actor=self._session(db,token,admin=True)
            meta=roles.target(db,actor,uid);target=self._user(db,uid)
            if meta['role']=='superadmin' and changes.get('enabled') is False:raise AuthError('The superadmin cannot be disabled',409)
            special={'parent_admin','max_users','user_quota_bytes','manage_users'} & set(changes)
            if special and actor['role']!='superadmin':raise AuthError('Superadmin access required',403)
            if 'parent_admin' in changes:
                if meta['role']!='user':raise AuthError('Only users can be assigned to admins',400)
                parent=changes['parent_admin']
                if parent is not None and (not isinstance(parent,str) or len(parent)!=32):raise AuthError('Invalid parent administrator',400)
                if parent is not None and parent!=meta['parent_admin']:roles.capacity(db,parent,exclude=uid)
                hook = getattr(self, '_reassign_account', None)
                if hook:
                    hook(db, uid, parent)
            if special-{'parent_admin'}:
                if meta['role']!='admin':raise AuthError('Delegation limits apply to admins',400)
                self._management_values(changes.get('max_users',meta['max_users']),changes.get('user_quota_bytes',meta['user_quota_bytes']),changes.get('manage_users',bool(meta['manage_users'])))
            if 'permissions' in changes:roles.delegation(actor,changes['permissions'],0)
            if 'quota_bytes' in changes and changes['quota_bytes']>target['quota_bytes']:roles.delegation(actor,[],changes['quota_bytes'])
            if 'permissions' in changes:db.execute('UPDATE users SET permissions=? WHERE id=?',(json.dumps(changes['permissions']),uid))
            if 'enabled' in changes:db.execute('UPDATE workspaces SET enabled=? WHERE user_id=?',(int(changes['enabled']),uid))
            if 'quota_bytes' in changes:db.execute('UPDATE workspaces SET quota_bytes=? WHERE user_id=?',(changes['quota_bytes'],uid))
            for field in special:db.execute('UPDATE account_roles SET '+field+'=? WHERE user_id=?',(changes[field],uid))
            if changes.get('enabled') is False or 'parent_admin' in changes:
                db.execute('DELETE FROM sessions WHERE user_id=?',(uid,))
                if meta['role']=='admin':db.execute('DELETE FROM sessions WHERE user_id IN (SELECT user_id FROM account_roles WHERE parent_admin=?)',(uid,))
            self.audit(db,actor['id'],'user_updated',uid,changes=changes)
            return roles.public(db,self._public_user(self._user(db,uid)))

    def reset_password(self, token, uid, temporary_password):
        hashed=hash_password(temporary_password)
        with self._tx() as db:
            actor=self._session(db,token,admin=True)
            roles.target(db,actor,uid)
            db.execute('UPDATE users SET password_hash=?,must_change=1 WHERE id=?',(hashed,uid))
            db.execute('DELETE FROM sessions WHERE user_id=?',(uid,))
            target=self._user(db,uid)
            db.execute('DELETE FROM login_attempts WHERE username=?',(target['username'],))
            self.audit(db,actor['id'],'password_reset',uid)

    def change_password(self, token, current_password, new_password):
        if current_password == new_password:
            raise AuthError("Choose a different new password", 400)
        hashed = hash_password(new_password)
        with self._tx() as db:
            user = self._session(db, token, allow_change=True)
            row = self._user(db, user["id"])
            if not verify_password(current_password, row["password_hash"]):
                raise AuthError("Current password is incorrect", 403)
            db.execute("UPDATE users SET password_hash=?,must_change=0 WHERE id=?", (hashed, user["id"]))
            db.execute("DELETE FROM sessions WHERE user_id=?", (user["id"],))
            self.audit(db, user["id"], "password_changed", user["id"])

    def logout(self, token, *, all_sessions=False):
        with self._tx() as db:
            user = self._session(db, token, allow_change=True)
            if all_sessions:
                db.execute("DELETE FROM sessions WHERE user_id=?", (user["id"],))
            else:
                db.execute("DELETE FROM sessions WHERE token_hash=?", (session_hash(token),))
            self.audit(db, user["id"], "logout_all" if all_sessions else "logout", user["id"])

    def audit_log(self, token):
        with self._tx() as db:
            actor=self._session(db,token,admin=True)
            if actor['role']=='superadmin':
                rows=db.execute('SELECT * FROM auth_audit ORDER BY id DESC LIMIT 200')
            else:
                rows=db.execute("SELECT * FROM auth_audit WHERE actor=? OR target IN (SELECT user_id FROM account_roles WHERE parent_admin=? AND role='user') ORDER BY id DESC LIMIT 200",(actor['id'],actor['id']))
            return [dict(r) for r in rows]
