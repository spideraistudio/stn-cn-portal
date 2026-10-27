"""Owned Phase 3 documents. No financial execution or offline-server routing.

Workspace writes and live session checks share the account SQLite transaction.
Composite owner keys and scoped parent lookups never accept browser identities.
"""
import base64
import binascii
import json
import math
import uuid
from .security import AuthError, require_permission

KINDS = {'projects': 'edit_ledger', 'workbooks': 'edit_ledger',
         'schemes': 'edit_schemes', 'settings': 'edit_schemes',
         'parties': 'edit_ledger', 'files': 'import_statements', 'layouts': 'view_workspace'}
FIELDS = {
    'projects': {'name', 'description'},
    'workbooks': {'name', 'state', 'financial_year', 'season'},
    'schemes': {'name', 'configuration'},
    'settings': {'name', 'configuration'},
    'parties': {'name', 'state', 'hq', 'reference'},
    'files': {'name', 'content_base64'},
    'layouts': {'name', 'theme', 'record_id', 'positions', 'locked'},
}


def fields(value, required, optional=()):
    if not isinstance(value, dict) or set(value)-set(required)-set(optional) or set(required)-set(value):
        raise AuthError('Request fields are missing or unsupported', 400)


def identifier(value):
    if not isinstance(value, str) or len(value) != 32 or any(c not in '0123456789abcdef' for c in value):
        raise AuthError('Object not found', 404)
    return value


def validate(kind, value):
    fields(value, {'name'}, FIELDS[kind]-{'name'})
    if any(not isinstance(value[k], str) or len(value[k]) > 500 or '\x00' in value[k]
           for k in set(value)-{'configuration', 'content_base64', 'positions', 'locked'}):
        raise AuthError('Invalid text field', 400)
    if not value['name'].strip():
        raise AuthError('Enter a name', 400)
    if 'configuration' in value and not isinstance(value['configuration'], dict):
        raise AuthError('Configuration must be an object', 400)
    if kind == 'files':
        try:
            raw = base64.b64decode(value['content_base64'], validate=True)
            if base64.b64encode(raw).decode() != value['content_base64']:
                raise ValueError()
        except (KeyError, ValueError, TypeError, binascii.Error):
            raise AuthError('File must contain canonical base64 bytes', 400) from None
    if kind == 'layouts':
        if value.get('theme', 'classic') not in {'classic', 'studio'} or type(value.get('locked', False)) is not bool:
            raise AuthError('Invalid appearance', 400)
        positions = value.get('positions', [])
        if not isinstance(positions, list) or len(positions) > 1000:
            raise AuthError('Invalid positions', 400)
        seen = set()
        for p in positions:
            fields(p, {'key', 'x', 'y'})
            if not isinstance(p['key'], str) or not 1 <= len(p['key']) <= 600 or p['key'] in seen:
                raise AuthError('Invalid card identity', 400)
            seen.add(p['key'])
            if any(type(p[k]) not in (float, int) or not math.isfinite(p[k]) or abs(p[k]) > 100000 for k in ('x', 'y')):
                raise AuthError('Invalid coordinate', 400)
    try:
        encoded = json.dumps(value, allow_nan=False)
    except (ValueError, TypeError, RecursionError):
        raise AuthError('Invalid document', 400) from None
    return encoded


class DataStore:
    def __init__(self, accounts):
        self.accounts = accounts
        with accounts._tx() as db:
            db.execute('''CREATE TABLE IF NOT EXISTS workspace_documents (
                owner TEXT NOT NULL, id TEXT NOT NULL, kind TEXT NOT NULL,
                project TEXT, workbook TEXT, revision INTEGER NOT NULL,
                deleted INTEGER NOT NULL DEFAULT 0, payload TEXT NOT NULL,
                PRIMARY KEY(owner,id))''')
            db.execute('CREATE INDEX IF NOT EXISTS document_scope ON workspace_documents(owner,project,workbook,kind)')

    def user(self, db, token, permission='view_workspace'):
        user = self.accounts._session(db, token, permission='view_workspace')
        require_permission(user, permission)
        return user

    def row(self, db, owner, oid, *, kind=None):
        row = db.execute('SELECT * FROM workspace_documents WHERE owner=? AND id=?', (owner, identifier(oid))).fetchone()
        if not row or row['deleted'] or kind and row['kind'] != kind:
            raise AuthError('Object not found', 404)
        if row['project']:
            self.row(db, owner, row['project'], kind='projects')
        if row['workbook']:
            self.row(db, owner, row['workbook'], kind='workbooks')
        return row

    @staticmethod
    def public(row):
        return {k: row[k] for k in ('id', 'kind', 'project', 'workbook', 'revision')} | {'data': json.loads(row['payload'])}

    def scope(self, db, owner, kind, project, workbook):
        if kind == 'projects':
            if project is not None or workbook is not None:
                raise AuthError('Projects have no parent', 400)
        else:
            self.row(db, owner, project, kind='projects')
            if kind == 'workbooks' and workbook is not None:
                raise AuthError('Workbooks belong directly to projects', 400)
            if workbook is not None:
                row = self.row(db, owner, workbook, kind='workbooks')
                if row['project'] != project:
                    raise AuthError('Object not found', 404)
            if kind in {'parties', 'layouts'} and workbook is None:
                raise AuthError('Choose a workbook', 400)

    def request(self, token, method, kind, oid=None, data=None):
        if kind not in KINDS:
            raise AuthError('Not found', 404)
        with self.accounts._tx() as db:
            permission = KINDS[kind] if method in {'POST', 'PATCH'} else 'delete_records' if method == 'DELETE' else 'view_workspace'
            user = self.user(db, token, permission)
            owner = user['id']
            if method == 'DELETE' and kind in {'schemes', 'settings'}:
                require_permission(user, 'edit_schemes')
            if oid:
                row = self.row(db, owner, oid, kind=kind)
                if method == 'GET':
                    return self.public(row)
                if method not in {'PATCH', 'DELETE'}:
                    raise AuthError('Not found', 404)
                fields(data, {'revision', 'data'} if method == 'PATCH' else {'revision'})
                if type(data['revision']) is not int or data['revision'] != row['revision']:
                    raise AuthError('This item changed. Reload before saving.', 409)
                if method == 'DELETE' and hasattr(self, 'calculator'):
                    self.calculator.protect(db, owner, row)
                if method in {'PATCH','DELETE'} and hasattr(self, 'ledger'):
                    self.ledger.protect(db, owner, row, method, data)
                if method == 'PATCH':
                    payload = validate(kind, data['data'])
                    db.execute('UPDATE workspace_documents SET payload=?,revision=revision+1 WHERE owner=? AND id=?', (payload, owner, oid))
                else:
                    # No cascading purge and no financial/frozen record route.
                    if db.execute('SELECT 1 FROM workspace_documents WHERE owner=? AND deleted=0 AND (project=? OR workbook=?)', (owner, oid, oid)).fetchone():
                        raise AuthError('Archive child items first', 409)
                    db.execute('UPDATE workspace_documents SET deleted=1,revision=revision+1 WHERE owner=? AND id=?', (owner, oid))
                self.accounts.audit(db, owner, 'workspace_'+method.lower(), oid, kind=kind)
                return {'deleted': True} if method == 'DELETE' else self.public(self.row(db, owner, oid))
            if method == 'POST':
                fields(data, {'data'}, {'project', 'workbook'})
                project, workbook = data.get('project'), data.get('workbook')
                self.scope(db, owner, kind, project, workbook)
                payload = validate(kind, data['data'])
                oid = uuid.uuid4().hex
                db.execute('INSERT INTO workspace_documents VALUES(?,?,?,?,?,1,0,?)', (owner, oid, kind, project, workbook, payload))
                self.accounts.audit(db, owner, 'workspace_created', oid, kind=kind)
                return self.public(self.row(db, owner, oid))
            if method == 'GET':
                rows = db.execute('SELECT * FROM workspace_documents WHERE owner=? AND kind=? AND deleted=0 ORDER BY rowid', (owner, kind)).fetchall()
                return {'items': [self.public(r) for r in rows]}
            raise AuthError('Not found', 404)

    def download(self, token, oid):
        with self.accounts._tx() as db:
            user = self.user(db, token, 'export_print')
            return self.public(self.row(db, user['id'], oid, kind='files'))

    def export(self, token, project):
        with self.accounts._tx() as db:
            user = self.user(db, token, 'export_print')
            root = self.row(db, user['id'], project, kind='projects')
            rows = db.execute('SELECT * FROM workspace_documents WHERE owner=? AND project=? AND deleted=0 ORDER BY rowid', (user['id'], project)).fetchall()
            result = {'format': 'cn-web-project', 'version': 1, 'documents': [self.public(root)]+[self.public(r) for r in rows]}
            if hasattr(self, 'ledger'):
                bundle = self.ledger.export_bundle(db, user['id'], project)
                if bundle: result.update(version=2, ledger_bundle=bundle)
            if hasattr(self, 'calculator'):
                calc = self.calculator.export_bundle(db, user['id'], project)
                if calc: result.update(version=3, calculator_bundle=calc, ledger_bundle=result.get('ledger_bundle', []))
            return result

    def import_project(self, token, data):
        fields(data, {'backup'})
        backup = data['backup']
        fields(backup, {'format', 'version', 'documents'}, {'ledger_bundle','calculator_bundle'})
        if backup['format'] != 'cn-web-project' or type(backup['version']) is not int or backup['version'] not in (1, 2, 3) or not isinstance(backup['documents'], list) or not 1 <= len(backup['documents']) <= 10000:
            raise AuthError('Unsupported project backup', 400)
        docs, seen = backup['documents'], set()
        # Validate the entire graph before creating anything. Never merge by ID.
        by_id = {}
        for d in docs:
            fields(d, {'id', 'kind', 'project', 'workbook', 'revision', 'data'})
            identifier(d['id'])
            if d['id'] in seen or not isinstance(d['kind'], str) or d['kind'] not in KINDS or type(d['revision']) is not int or d['revision'] < 1:
                raise AuthError('Invalid backup object', 400)
            seen.add(d['id']); by_id[d['id']] = d
            validate(d['kind'], d['data'])
        roots = [d for d in docs if d['kind'] == 'projects']
        if len(roots) != 1:
            raise AuthError('Backup must contain one project', 400)
        root = roots[0]
        for d in docs:
            if d is root:
                valid = d['project'] is None and d['workbook'] is None
            else:
                valid = d['project'] == root['id']
                w = by_id.get(d['workbook']) if isinstance(d['workbook'], str) else None
                valid = valid and (d['workbook'] is None or w is not None and w['kind'] == 'workbooks')
                valid = valid and (d['kind'] != 'workbooks' or d['workbook'] is None)
                valid = valid and (d['kind'] not in {'parties', 'layouts'} or w is not None)
            if not valid:
                raise AuthError('Invalid backup relationships', 400)
        bundle = []
        if backup['version'] in (2, 3):
            if not hasattr(self, 'ledger') or 'ledger_bundle' not in backup:
                raise AuthError('Ledger-aware backup reader is required', 400)
            bundle = self.ledger.validate_bundle(backup['ledger_bundle'], by_id)
        elif 'ledger_bundle' in backup:
            raise AuthError('Ledger backup requires format version 2', 400)
        calculator_bundle = []
        if backup['version'] == 3:
            if not hasattr(self, 'calculator') or 'calculator_bundle' not in backup:
                raise AuthError('Calculator-aware backup reader is required',400)
            calculator_bundle = self.calculator.validate_bundle(backup['calculator_bundle'], by_id, bundle)
        elif 'calculator_bundle' in backup:
            raise AuthError('Calculator backup requires version 3',400)
        mapping = {d['id']: uuid.uuid4().hex for d in docs}
        for part in bundle:
            mapping.update({r['id']: uuid.uuid4().hex for r in part['state']['ledgers']})
        with self.accounts._tx() as db:
            user = self.user(db, token, 'import_statements')
            require_permission(user, 'edit_ledger')
            for d in docs:
                require_permission(user, KINDS[d['kind']])
            for d in docs:
                payload = dict(d['data'])
                if d['kind'] == 'layouts' and payload.get('record_id') in mapping:
                    payload['record_id'] = mapping[payload['record_id']]
                db.execute('INSERT INTO workspace_documents VALUES(?,?,?,?,?,1,0,?)',
                           (user['id'], mapping[d['id']], d['kind'], mapping.get(d['project']), mapping.get(d['workbook']), validate(d['kind'], payload)))
            if bundle:
                self.ledger.import_bundle(db, user, mapping, bundle)
            if calculator_bundle:
                self.calculator.import_bundle(db, user, mapping, calculator_bundle)
            self.accounts.audit(db, user['id'], 'project_imported', mapping[root['id']], count=len(docs))
            return {'project_id': mapping[root['id']], 'imported': len(docs)}
