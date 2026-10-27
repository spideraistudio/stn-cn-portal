"""Portable offline projects. Imports always create a new, isolated database root."""
import base64,copy,functools,hashlib,io,json,os,re,shutil,tempfile,threading,uuid,zipfile
from pathlib import Path
from store import Store,dump,now
from workbooks import Workbooks

FORMAT='all-crop-cn-project'
LIMIT=128*1024*1024

def encoded(value):return dump(value).encode('utf-8')
def digest(value):return hashlib.sha256(encoded(value)).hexdigest()
def loads(raw):
    def bad(value):raise ValueError('Non-finite number in shared file')
    return json.loads(raw,parse_constant=bad)

def summary(backup):
    stores=[backup['legacy']]+[b['backup'] for b in backup['workbooks']]
    records=[loads(row['data']) for b in stores for row in b['records']]
    return {'workbooks':len(backup['workbooks'])+1,'records':len(records),
            'parties':len({(r.get('party','').strip().casefold(),r.get('location','').strip().casefold()) for r in records}),
            'drafts':sum(r.get('status')=='draft' for r in records),
            'completed':sum(r.get('status') in ('finalised','issued') for r in records),
            'deleted_records':sum(bool(r.get('deleted_at')) for r in records),
            'schemes':sum(len(loads(max(b['settings'],key=lambda s:s['version'])['data'])['schemes']) for b in stores)}

class Projects:
    def __init__(self,main):
        self.main=main;self.directory=Path(main.legacy.path).parent/'shared-projects'
        self.lock=threading.RLock();self.cache={'main':main}
    def serialized(self,fn):
        @functools.wraps(fn)
        def run(*args,**kwargs):
            with self.lock:return fn(*args,**kwargs)
        return run
    def _registry(self):
        path=self.directory/'index.json'
        return loads(path.read_bytes()) if path.exists() else []
    def _write(self,items):
        self.directory.mkdir(parents=True,exist_ok=True)
        tmp=self.directory/'index.tmp';tmp.write_bytes(encoded(items));os.replace(tmp,self.directory/'index.json')
    def list(self):return [{'id':'main','name':'My Work','kind':'own'}]+self._registry()
    def metadata(self,id):
        if id!='main' and not re.fullmatch('[a-f0-9]{32}',id):raise ValueError('Invalid project')
        found=next((m for m in self.list() if m['id']==id),None)
        if not found:raise ValueError('Project not found. Return to My Work.')
        return copy.deepcopy(found)
    def context(self,id='main'):
        self.metadata(id)
        if id not in self.cache:
            path=self.directory/id/'calculator.sqlite3'
            if not path.is_file():raise ValueError('Project data is missing; import the original shared file again')
            self.cache[id]=Workbooks(Store(path))
        books=self.cache[id];return books.legacy,books
    def export(self,id,b):
        _,books=self.context(id);backup=books.backup();backup.pop('created_at',None)
        for item in [backup['legacy']]+[w['backup'] for w in backup['workbooks']]:item.pop('created_at',None)
        info=summary(backup)
        meta=self.metadata(id);name=str(b.get('name') or meta['name']).strip()[:160]
        sender=str(b.get('sender') or '').strip()[:160]
        identity=Path(self.main.legacy.path).parent/'project-identity.json'
        if id=='main' and not identity.exists():identity.write_bytes(encoded({'origin':uuid.uuid4().hex}))
        origin=meta.get('origin') or (loads(identity.read_bytes())['origin'] if id=='main' else id)
        manifest={'format':FORMAT,'version':1,'name':name,'sender':sender,'exported_at':now(),
                  'transfer_id':uuid.uuid4().hex,'origin':origin,'preferred_workbook':b.get('selected_workbook','legacy'),
                  'parent_transfer':meta.get('transfer_id'),'sha256':hashlib.sha256(encoded(backup)).hexdigest()}
        if manifest['preferred_workbook'] not in ['legacy']+[m['metadata']['id'] for m in backup['workbooks'] if not m['metadata'].get('deleted_at')]:raise ValueError('Select an active workbook')
        if len(encoded(backup))>LIMIT:raise ValueError('Project exceeds the 128 MB portable-file limit')
        preview={**manifest,**info,'scope':'Entire selected project, including deleted records, all workbooks and history. Other projects are excluded.'}
        if not b.get('confirm'):return preview
        if b.get('expected')!=manifest['sha256']:raise ValueError('Project changed. Preview the export again.')
        out=io.BytesIO()
        with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED) as z:
            z.writestr('manifest.json',encoded(manifest));z.writestr('work.json',encoded(backup))
        return {'filename':re.sub(r'[^a-zA-Z0-9_-]+','_',name)[:80]+'.cnwork','data':base64.b64encode(out.getvalue()).decode(),'summary':preview}
    def _read(self,data):
        try:
            if len(data)>96*1024*1024:raise ValueError('Shared file exceeds compressed size limit')
            raw=base64.b64decode(data,validate=True)
            with zipfile.ZipFile(io.BytesIO(raw)) as z:
                if sorted(z.namelist())!=['manifest.json','work.json']:raise ValueError('Shared file must contain only manifest.json and work.json')
                if z.getinfo('manifest.json').file_size>65536 or sum(i.file_size for i in z.infolist())>LIMIT:raise ValueError('Shared file exceeds expanded size limit')
                manifest=loads(z.read('manifest.json'));content=z.read('work.json');backup=loads(content)
            if manifest.get('format')!=FORMAT or manifest.get('version')!=1:raise ValueError('Unsupported shared-file version; use a compatible calculator')
            if not isinstance(manifest.get('name'),str) or not manifest['name'].strip() or len(manifest['name'])>160:raise ValueError('Shared file has no valid project name')
            if not isinstance(manifest.get('sender',''),str) or len(manifest.get('sender',''))>160:raise ValueError('Invalid sender')
            if hashlib.sha256(content).hexdigest()!=manifest.get('sha256'):raise ValueError('Shared file integrity check failed')
            if backup.get('format')!='all-crop-cn-workbooks-backup' or backup.get('version')!=1:raise ValueError('Invalid project backup')
            info=summary(backup)
            return manifest,backup,info
        except (ValueError,KeyError,TypeError,AttributeError,RuntimeError,zipfile.BadZipFile,UnicodeError) as e:
            raise ValueError('Cannot open shared file: '+str(e)) from e
    def receive(self,b):
        manifest,backup,info=self._read(b['data']);fingerprint=digest({'manifest':manifest,'backup':backup})
        # Real temporary restore catches duplicate keys and malformed rows before registration.
        self.directory.mkdir(parents=True,exist_ok=True)
        with tempfile.TemporaryDirectory(prefix='.incoming-',dir=self.directory) as td:
            st=Store(Path(td)/'calculator.sqlite3');books=Workbooks(st)
            books.restore(backup,False);books._restore_validated(backup)
            selected=manifest.get('preferred_workbook','legacy')
            books.get(selected)
            preview={**info,'name':manifest['name'],'sender':manifest.get('sender',''),'exported_at':manifest.get('exported_at',''),
                     'expected':fingerprint,'warning':'Opens a new isolated local copy. Existing projects are not changed.'}
            if not b.get('confirm'):return preview
            if b.get('expected')!=fingerprint:raise ValueError('Shared file changed; preview again')
            id=uuid.uuid4().hex
            meta={'id':id,'kind':'received','name':manifest['name'],'sender':manifest.get('sender',''),'received_at':now(),
                  'exported_at':manifest.get('exported_at',''),'transfer_id':manifest.get('transfer_id'),
                  'origin':manifest.get('origin') or manifest.get('transfer_id'),'preferred_workbook':selected}
            dest=self.directory/id
            # These are empty-seed restore backups created during validation, never source work.
            for p in Path(td).rglob('*.before-restore.json'):p.unlink()
            shutil.copytree(td,dest)
            try:self._write(self._registry()+[meta])
            except BaseException:shutil.rmtree(dest);raise
            return {'imported':True,'project':meta,'summary':preview}
