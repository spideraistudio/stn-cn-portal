"""Delegated management only; never grants access to another owner's data."""
from .security import AuthError
ADMIN_QUOTA = 1024**3
USER_QUOTA = 250*1024**2


def initialize(db):
    db.execute('''CREATE TABLE IF NOT EXISTS account_roles (
        user_id TEXT PRIMARY KEY, role TEXT NOT NULL, parent_admin TEXT,
        max_users INTEGER NOT NULL DEFAULT 5, user_quota_bytes INTEGER NOT NULL DEFAULT 262144000,
        manage_users INTEGER NOT NULL DEFAULT 1)''')
    # Old installation's original bootstrap operator becomes superadmin once.
    root = db.execute("SELECT user_id FROM account_roles WHERE role='superadmin'").fetchone()
    if root is None:
        first = db.execute("SELECT id FROM users WHERE is_admin=1 ORDER BY created_at,rowid LIMIT 1").fetchone()
        root_id = first[0] if first else None
    else:
        root_id = root[0]
    for row in db.execute('SELECT id,is_admin FROM users').fetchall():
        role = 'superadmin' if row['id']==root_id else 'admin' if row['is_admin'] else 'user'
        # Legacy users remain directly managed by the superadmin, never guessed
        # into an admin group. Their quotas, credentials and work are unchanged.
        db.execute('INSERT OR IGNORE INTO account_roles(user_id,role,parent_admin) VALUES(?,?,?)',
                   (row['id'],role,root_id if role=='admin' else None))


def public(db, user):
    row=db.execute('SELECT * FROM account_roles WHERE user_id=?',(user['id'],)).fetchone()
    if row:
        user.update({k:row[k] for k in ('role','parent_admin','max_users','user_quota_bytes')})
        user['manage_users']=bool(row['manage_users'])
    return user


def target(db, actor, uid):
    row=db.execute('SELECT * FROM account_roles WHERE user_id=?',(uid,)).fetchone()
    if not row or (actor['role']!='superadmin' and (row['role']!='user' or row['parent_admin']!=actor['id'])):
        raise AuthError('Account not found',404)
    return row


def capacity(db, parent, *, exclude=None):
    admin=db.execute('SELECT r.*,w.enabled FROM account_roles r JOIN workspaces w ON w.user_id=r.user_id WHERE r.user_id=?',(parent,)).fetchone()
    if not admin or admin['role']!='admin':raise AuthError('Choose an administrator',400)
    count=db.execute("SELECT COUNT(*) FROM account_roles WHERE parent_admin=? AND role='user' AND user_id!=?",(parent,exclude or '')).fetchone()[0]
    if count>=admin['max_users']:raise AuthError('This administrator has reached the user limit',409)
    return admin


def delegation(actor, permissions, quota):
    if actor['role']=='admin':
        if not set(permissions)<=set(actor['permissions']):raise AuthError('You can grant only permissions assigned to you',403)
        if quota>actor['user_quota_bytes']:raise AuthError('User allowance exceeds the limit granted by superadmin',403)
