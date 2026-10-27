"""Logical retained-byte quotas, enforced under the account SQLite write lock.

The lock is the upload reservation: no second writer can spend capacity until
this transaction commits or rolls back. No leases can be orphaned by a crash.
Only this module's registered ephemeral blobs are ever age-cleaned.
"""
import json
import uuid
from .security import AuthError

TABLES = ('workspace_documents', 'ledger_workspaces', 'calculator_workspaces')
TEMP_CATEGORIES = {'temporary_preview', 'cache', 'abandoned_upload'}


def initialize(db):
    db.execute('''CREATE TABLE IF NOT EXISTS storage_temporary (
        owner TEXT NOT NULL, id TEXT NOT NULL, category TEXT NOT NULL,
        created_at REAL NOT NULL, last_used_at REAL NOT NULL,
        active INTEGER NOT NULL, protected INTEGER NOT NULL,
        links TEXT NOT NULL, payload BLOB NOT NULL, PRIMARY KEY(owner,id))''')


def usage(db):
    """UTF-8 payload bytes, including base64 and archived/deleted documents.

    Shared SQLite page/index/WAL overhead and security audit are operator costs,
    not attributed arbitrarily to one user. Temporary bytes are included once.
    """
    result = {}
    tables = {r[0] for r in db.execute("SELECT name FROM sqlite_master WHERE type='table'")}
    for table in TABLES:
        if table in tables:
            for r in db.execute('SELECT owner, SUM(length(CAST(payload AS BLOB))) FROM '+table+' GROUP BY owner'):
                result[r[0]] = result.get(r[0], 0) + r[1]
    if 'storage_temporary' in tables:
        for r in db.execute('SELECT owner, SUM(length(payload)+length(CAST(links AS BLOB))) FROM storage_temporary GROUP BY owner'):
            result[r[0]] = result.get(r[0], 0) + r[1]
    return result


def enforce(db, before):
    after = usage(db)
    quotas = dict(db.execute('SELECT user_id,quota_bytes FROM workspaces'))
    for owner, size in after.items():
        # Existing over-limit work remains readable/exportable and can shrink.
        if size > quotas[owner] and size > before.get(owner, 0):
            raise AuthError('Storage allowance exceeded. No changes saved. Ask your administrator to increase your allowance.', 413)


def status(db, owner):
    used = usage(db).get(owner, 0)
    quota = db.execute('SELECT quota_bytes FROM workspaces WHERE user_id=?', (owner,)).fetchone()[0]
    return dict(used_bytes=used, quota_bytes=quota, available_bytes=max(0, quota-used),
                over_quota=used>quota, quota_enforcement_active=True,
                accounting='UTF-8 saved payloads (including base64 PDFs), archived data and registered temporary bytes; excludes shared database overhead and security audit')


def put_temporary(db, owner, category, payload, now, *, active=False, protected=False, links=()):
    """Trusted server-only registration. Never accepts filesystem paths."""
    if category not in TEMP_CATEGORIES or not isinstance(payload, bytes):
        raise ValueError('Invalid temporary object')
    oid = uuid.uuid4().hex
    db.execute('INSERT INTO storage_temporary VALUES(?,?,?,?,?,?,?,?,?)',
               (owner, oid, category, now, now, int(active), int(protected), json.dumps(list(links)), payload))
    return oid


def cleanup(db, accounts, owner=None):
    cutoff = accounts.clock() - 60*86400
    rows = db.execute('SELECT * FROM storage_temporary WHERE created_at<? AND last_used_at<? AND active=0 AND protected=0', (cutoff, cutoff)).fetchall()
    deleted = 0
    for row in rows:
        if owner is not None and row['owner'] != owner:
            continue
        try:
            unlinked = json.loads(row['links']) == []
        except (ValueError, TypeError):
            unlinked = False
        if row['category'] not in TEMP_CATEGORIES or not unlinked:
            continue
        db.execute('DELETE FROM storage_temporary WHERE owner=? AND id=?', (row['owner'], row['id']))
        accounts.audit(db, row['owner'], 'temporary_cleaned', row['id'], category=row['category'])
        deleted += 1
    return {'removed': deleted, 'retention_days': 60}
