import base64,copy,io,json,sqlite3,tempfile,unittest,zipfile,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from store import Store,dump
from workbooks import Workbooks
from projects import Projects,encoded
from maintenance import purge,Cleanup
from test_calculator import example

class ProjectSharingTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name);self.st=Store(self.root/'owner'/'calculator.sqlite3');self.books=Workbooks(self.st);self.projects=Projects(self.books)
  r,cfg=example();self.st.save_settings(cfg);self.r=self.st.save(r)
 def tearDown(self):self.tmp.cleanup()
 def export(self,manager=None,id='main'):
  manager=manager or self.projects;p=manager.export(id,{});return manager.export(id,{'confirm':True,'expected':p['sha256'],'name':'Season review','sender':'Person A'})
 def receive(self,file):
  p=self.projects.receive({'data':file['data']});return self.projects.receive({'data':file['data'],'confirm':True,'expected':p['expected']})
 def test_transfer_frozen_snapshots_then_continue_without_touching_owner(self):
  frozen=self.st.finalise(self.r['id'],self.r['revision']);before=self.st.backup();file=self.export();p=self.projects.receive({'data':file['data']});self.assertEqual(p['completed'],1)
  imported=self.receive(file);id=imported['project']['id'];received,_=self.projects.context(id);self.assertNotEqual(received.path,self.st.path);self.assertEqual(received.get(frozen['id']),frozen)
  draft=received.revise(frozen['id']);draft['party']='Person B working copy';received.save(draft);self.assertEqual(self.st.get(frozen['id']),frozen);self.assertEqual(len(self.st.all()),1)
  cfg=received.settings();cfg['products'][0]['name']='Receiver-only product';received.save_settings(cfg);self.assertNotEqual(self.st.settings()['products'][0]['name'],'Receiver-only product')
  returned=self.export(self.projects,id);p=self.projects.receive({'data':returned['data']});self.assertEqual(p['records'],2)
  restarted=Projects(self.books);self.assertEqual(restarted.context(id)[0].get(frozen['id']),frozen)
 def test_reimport_same_file_creates_two_separate_roots(self):
  file=self.export();a=self.receive(file)['project']['id'];b=self.receive(file)['project']['id'];self.assertNotEqual(a,b)
  st,_=self.projects.context(a);r=st.get(self.r['id']);r['location']='Changed';st.save(r)
  self.assertEqual(self.projects.context(b)[0].get(r['id'])['location'],'Town');self.assertEqual(self.st.get(r['id'])['location'],'Town')
 def test_preview_does_not_register_project_and_stale_export_rejected(self):
  file=self.export();before=self.st.backup();self.projects.receive({'data':file['data']});self.assertEqual(len(self.projects.list()),1)
  for k in ('records','settings','audit','issued'):self.assertEqual(before[k],self.st.backup()[k])
  p=self.projects.export('main',{});r=self.st.get(self.r['id']);r['party']='Changed';self.st.save(r)
  with self.assertRaisesRegex(ValueError,'changed'):self.projects.export('main',{'confirm':True,'expected':p['sha256']})
 def test_integrity_paths_duplicate_members_invalid_rows_and_versions_rejected(self):
  file=self.export();raw=base64.b64decode(file['data'])
  with zipfile.ZipFile(io.BytesIO(raw)) as z:members={n:z.read(n) for n in z.namelist()}
  def pack(changes,extra=None):
   o=io.BytesIO()
   with zipfile.ZipFile(o,'w') as z:
    for n,data in {**members,**changes}.items():z.writestr(n,data)
    if extra:z.writestr(*extra)
   return base64.b64encode(o.getvalue()).decode()
  with self.assertRaisesRegex(ValueError,'integrity'):self.projects.receive({'data':pack({'work.json':members['work.json']+b' '})})
  with self.assertRaisesRegex(ValueError,'only manifest'):self.projects.receive({'data':pack({},('../escape.py',b'bad'))})
  manifest=json.loads(members['manifest.json']);manifest['version']=999
  with self.assertRaisesRegex(ValueError,'version'):self.projects.receive({'data':pack({'manifest.json':encoded(manifest)})})
  import hashlib
  data=json.loads(members['work.json']);data['legacy']['records'].append(copy.deepcopy(data['legacy']['records'][0]));content=encoded(data);manifest['version']=1;manifest['sha256']=hashlib.sha256(content).hexdigest()
  with self.assertRaises(sqlite3.IntegrityError):self.projects.receive({'data':pack({'manifest.json':encoded(manifest),'work.json':content})})
  self.assertEqual(len(self.projects.list()),1)
 def test_workbook_private_schemes_bulk_history_and_issue_guards_travel(self):
  make={'name':'North season','state':'Gujarat','period':'2026 season 1','start':'2026-04-01','end':'2026-08-31','cutoff':'2026-10-13'};w=self.books.create(make);st=self.books.get(w['id']);r,cfg=example();st.save_settings(cfg);r['workbook_id']=w['id'];r=st.save(r);r=st.finalise(r['id'],r['revision']);r=st.issue(r['id'],r['revision'])
  with st.db() as c:c.execute('INSERT INTO bulk_imports VALUES(?,?)',('sample',dump({'id':'sample','record_id':r['id'],'status':'Imported'})))
  p=self.projects.export('main',{'selected_workbook':w['id']});file=self.projects.export('main',{'selected_workbook':w['id'],'confirm':True,'expected':p['sha256']});incoming=self.receive(file);_,b=self.projects.context(incoming['project']['id']);self.assertEqual(b.get(w['id']).get(r['id']),r);self.assertEqual(b.get(w['id']).backup()['issued'],st.backup()['issued']);self.assertEqual(b.get(w['id']).backup()['bulk_imports'],st.backup()['bulk_imports'])
  with self.assertRaisesRegex(ValueError,'current finalised'):b.issue(w['id'],r['id'],r['revision'])

class StorageMaintenanceTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name);self.st=Store(self.root/'data'/'calculator.sqlite3');self.books=Workbooks(self.st);self.code=self.root/'code';(self.code/'__pycache__').mkdir(parents=True)
 def tearDown(self):self.tmp.cleanup()
 def save(self,name='To Remove'):
  r,cfg=example();r['party']=name;cfg['version']=self.st.settings()['version'];self.st.save_settings(cfg);return self.st.save(r)
 def archive(self,r):
  p=self.st.party_action(r['id']);self.st.party_action(r['id'],confirm=True,expected=p['expected'])
 def perform(self,b):
  p=purge(self.books,'legacy',b);return purge(self.books,'legacy',{**b,'confirm':True,'expected':p['expected'],'typed_name':p['name']})
 def test_party_purge_removes_rows_audit_and_import_but_keeps_other_party(self):
  a=self.save();b=self.save('Keep me')
  with self.st.db() as c:c.execute('INSERT INTO bulk_imports VALUES(?,?)',('test',dump({'record_id':a['id']})))
  self.archive(a);p=purge(self.books,'legacy',{'kind':'party','id':a['id']});self.assertEqual(p['blockers'],[])
  with self.assertRaisesRegex(ValueError,'exact name'):purge(self.books,'legacy',{'kind':'party','id':a['id'],'confirm':True,'expected':p['expected'],'typed_name':'wrong'})
  self.perform({'kind':'party','id':a['id']});self.assertEqual(self.st.all(),[b]);self.assertEqual(self.st.backup()['bulk_imports'],[]);self.assertFalse(any(x['target']==a['id'] and x['action']!='purge_party' for x in self.st.backup()['audit']))
 def test_active_party_issued_and_referenced_history_are_blocked(self):
  r=self.save()
  with self.assertRaisesRegex(ValueError,'Deleted Parties'):purge(self.books,'legacy',{'kind':'party','id':r['id']})
  frozen=self.st.finalise(r['id'],r['revision']);issued=self.st.issue(frozen['id'],frozen['revision']);self.archive(issued)
  p=purge(self.books,'legacy',{'kind':'party','id':issued['id']});self.assertTrue(p['blockers'])
  with self.assertRaisesRegex(ValueError,'Issued'):self.perform({'kind':'party','id':issued['id']})
 def test_stale_purge_preview_is_rejected(self):
  a=self.save();self.archive(a);p=purge(self.books,'legacy',{'kind':'party','id':a['id']});self.save('Another edit')
  with self.assertRaisesRegex(ValueError,'changed'):purge(self.books,'legacy',{'kind':'party','id':a['id'],'confirm':True,'expected':p['expected'],'typed_name':p['name']})
 def test_unused_scheme_purge_and_used_scheme_block(self):
  cfg=self.st.settings();sid=cfg['schemes'][0]['id'];self.st.scheme_action(sid,cfg['version']);p=purge(self.books,'legacy',{'kind':'scheme','id':sid});self.assertEqual(p['blockers'],[]);self.perform({'kind':'scheme','id':sid});self.assertNotIn(sid,[s['id'] for s in self.st.settings()['schemes']]);self.assertTrue(self.st.settings()['products']);self.assertGreater(self.st.settings()['version'],cfg['version'])
  r=self.save();sid='scheme-3';self.st.scheme_action(sid,self.st.settings()['version']);self.assertTrue(purge(self.books,'legacy',{'kind':'scheme','id':sid})['blockers'])
 def test_deleted_workbook_purge_reclaims_file_and_safety_copies(self):
  w=self.books.create({'name':'Disposable','state':'Gujarat','period':'Test','start':'2026-04-01','end':'2026-08-31','cutoff':'2026-10-13'});st=self.books.get(w['id']);path=Path(st.path);p=self.books.delete(w['id']);self.books.delete(w['id'],confirm=True,expected=p['expected']);self.assertTrue(path.exists());self.perform({'kind':'workbook','id':w['id']});self.assertFalse(path.exists());self.assertNotIn(w['id'],[m['id'] for m in self.books.list(True)]);self.assertEqual(list((self.root/'data'/'workbook-safety').glob(w['id']+'-*')),[])
 def test_cleanup_only_regenerable_cache_by_default_explicit_backups_and_symlink_safe(self):
  cache=self.code/'__pycache__'/'app.pyc';cache.write_bytes(b'cache');evidence=self.root/'data'/'source.pdf';evidence.write_bytes(b'original');backup=Path(self.st.path+'.before-restore.json');backup.write_bytes(b'recovery');foreign=self.root/'foreign.pyc';foreign.write_bytes(b'keep');(self.code/'__pycache__'/'foreign.pyc').symlink_to(foreign)
  clean=Cleanup(self.books,self.code);p=clean.run({});self.assertEqual(p['cache_bytes'],5);clean.run({'confirm':True,'expected':p['expected']});self.assertFalse(cache.exists());self.assertTrue(backup.exists());self.assertEqual(evidence.read_bytes(),b'original');self.assertTrue(foreign.exists())
  p=clean.run({});ids=[f['id'] for f in p['files'] if f['kind']=='backup'];p=clean.run({'backup_ids':ids})
  with self.assertRaisesRegex(ValueError,'DELETE BACKUPS'):clean.run({'confirm':True,'expected':p['expected'],'backup_ids':ids})
  clean.run({'confirm':True,'expected':p['expected'],'backup_ids':ids,'typed_confirmation':'DELETE BACKUPS'});self.assertFalse(backup.exists());self.assertTrue(evidence.exists())
 def test_cleanup_stale_file_list_rejected_and_compaction_preserves_data(self):
  self.save();cache=self.code/'__pycache__'/'app.pyc';cache.write_bytes(b'first');clean=Cleanup(self.books,self.code);p=clean.run({});cache.write_bytes(b'changed')
  with self.assertRaisesRegex(ValueError,'changed'):clean.run({'confirm':True,'expected':p['expected']})
  rows=self.st.all();settings=self.st.settings();p=clean.run({});clean.run({'confirm':True,'expected':p['expected']});self.assertEqual(self.st.all(),rows);self.assertEqual(self.st.settings(),settings)

 def test_unused_scheme_purge_preserves_other_completed_snapshot_exactly(self):
  r=self.save();frozen=self.st.finalise(r['id'],r['revision']);sid='scheme-1';self.st.scheme_action(sid,self.st.settings()['version']);p=purge(self.books,'legacy',{'kind':'scheme','id':sid});self.assertEqual(p['blockers'],[]);self.perform({'kind':'scheme','id':sid});self.assertEqual(self.st.get(frozen['id']),frozen)
 def test_issued_workbook_cannot_lose_duplicate_issue_protections(self):
  w=self.books.create({'name':'Issued history','state':'Gujarat','period':'2026 season 1','start':'2026-04-01','end':'2026-08-31','cutoff':'2026-10-13'});st=self.books.get(w['id']);r,cfg=example();st.save_settings(cfg);r=st.save(r);r=st.finalise(r['id'],r['revision']);st.issue(r['id'],r['revision']);p=self.books.delete(w['id']);self.books.delete(w['id'],confirm=True,expected=p['expected']);p=purge(self.books,'legacy',{'kind':'workbook','id':w['id']});self.assertTrue(p['blockers'])
  with self.assertRaisesRegex(ValueError,'issued'):self.perform({'kind':'workbook','id':w['id']})
  self.assertTrue(Path(st.path).exists());self.assertTrue(st.backup()['issued'])
 def test_party_purge_transaction_rolls_back_on_sql_failure(self):
  r=self.save();self.archive(r);before=self.st.backup()
  with self.st.db() as c:c.execute("CREATE TRIGGER test_protect BEFORE DELETE ON records BEGIN SELECT RAISE(ABORT, 'simulated failure'); END")
  with self.assertRaisesRegex(sqlite3.IntegrityError,'simulated failure'):self.perform({'kind':'party','id':r['id']})
  after=self.st.backup()
  for key in ('records','audit','bulk_imports','settings'):self.assertEqual(after[key],before[key])
