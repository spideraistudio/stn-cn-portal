"""Storage contention, rollback, existing-data and retention boundaries."""
import concurrent.futures
import json
from pathlib import Path
import sys
import tempfile
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'backend'))
from cn_web.accounts import Accounts
from cn_web.data_store import DataStore
from cn_web import storage_ops as storage
from cn_web.security import AuthError

class StorageTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.now=1800000000
        self.a=Accounts(self.temp.name,clock=lambda:self.now)
        self.owner=self.a.bootstrap('admin','Storage test password 2026!',quota_bytes=100000)
        self.store=DataStore(self.a)
        self.token=self.a.login('admin','Storage test password 2026!','local')
    def write(self, oid, size):
        try:
            with self.a._tx() as db:
                db.execute('INSERT INTO workspace_documents VALUES(?,?,?,NULL,NULL,1,0,?)',(self.owner,oid,'projects','x'*size))
            return True
        except AuthError as e:
            self.assertEqual(e.status,413)
            return False
    def test_concurrent_uploads_and_exact_boundary(self):
        with self.a._tx() as db:db.execute('UPDATE workspaces SET quota_bytes=100 WHERE user_id=?',(self.owner,))
        with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
            result=list(pool.map(lambda n:self.write(str(n),60),range(8)))
        self.assertEqual(sum(result),1)
        self.assertEqual(self.a.workspace(self.token)['used_bytes'],60)
        self.assertTrue(self.write('exact',40));self.assertFalse(self.write('over',1))
    def test_all_tables_archives_growth_and_atomic_rollback(self):
        with self.a._tx() as db:
            db.execute('CREATE TABLE calculator_workspaces(owner TEXT,workbook TEXT,revision INTEGER,payload TEXT)')
            db.execute('INSERT INTO calculator_workspaces VALUES(?,?,1,?)',(self.owner,'wb','é'*10))
            db.execute('UPDATE workspaces SET quota_bytes=30 WHERE user_id=?',(self.owner,))
        self.assertEqual(self.a.workspace(self.token)['used_bytes'],20)
        with self.assertRaises(AuthError):
            with self.a._tx() as db:
                db.execute('INSERT INTO workspace_documents VALUES(?,?,?,NULL,NULL,1,1,?)',(self.owner,'a','files','a'*11))
                db.execute('UPDATE calculator_workspaces SET revision=2')
        with self.a._tx() as db:self.assertEqual(db.execute('SELECT revision FROM calculator_workspaces').fetchone()[0],1)
    def test_lowered_quota_preserves_saved_work_and_allows_reduction(self):
        self.assertTrue(self.write('old',100))
        with self.a._tx() as db:db.execute('UPDATE workspaces SET quota_bytes=10 WHERE user_id=?',(self.owner,))
        self.assertTrue(self.a.workspace(self.token)['over_quota']);self.assertFalse(self.write('new',1))
        with self.a._tx() as db:db.execute("UPDATE workspace_documents SET payload='retained'")
        self.assertEqual(self.a.workspace(self.token)['used_bytes'],8)
    def test_maintenance_failure_keeps_service_available_for_retry(self):
        from unittest.mock import patch
        from cn_web.cli import maintain_temporary
        from contextlib import redirect_stderr
        import io
        with patch('cn_web.storage_ops.cleanup',side_effect=RuntimeError('failure')), redirect_stderr(io.StringIO()):
            self.assertFalse(maintain_temporary(self.a))
        self.assertTrue(maintain_temporary(self.a))

    def test_corrupt_or_unknown_registry_metadata_is_retained(self):
        old=self.now-61*86400
        with self.a._tx() as db:
            one=storage.put_temporary(db,self.owner,'cache',b'keep',old)
            two=storage.put_temporary(db,self.owner,'cache',b'keep',old)
            db.execute("UPDATE storage_temporary SET links='invalid' WHERE id=?",(one,))
            db.execute("UPDATE storage_temporary SET category='recovery' WHERE id=?",(two,))
        self.assertEqual(self.a.cleanup_temporary(self.token)['removed'],0)

    def test_restore_over_quota_is_atomic_and_retry_preserves_identity_isolation(self):
        project=self.store.request(self.token,'POST','projects',data={'data':{'name':'source'}})
        backup=self.store.export(self.token,project['id'])
        used=self.a.workspace(self.token)['used_bytes']
        with self.a._tx() as db:db.execute('UPDATE workspaces SET quota_bytes=? WHERE user_id=?',(used,self.owner))
        with self.assertRaises(AuthError):self.store.import_project(self.token,{'backup':backup})
        self.assertEqual(len(self.store.request(self.token,'GET','projects')['items']),1)
        with self.a._tx() as db:db.execute('UPDATE workspaces SET quota_bytes=100000 WHERE user_id=?',(self.owner,))
        restored=self.store.import_project(self.token,{'backup':backup})
        self.assertNotEqual(restored['project_id'],project['id'])
        self.assertEqual(len(self.store.request(self.token,'GET','projects')['items']),2)

    def test_retention_protection_cutoff_owner_retry_and_failure(self):
        self.a.registry.provision("other",quota_bytes=100000)
        old=self.now-61*86400
        with self.a._tx() as db:
            for kw in ({},{'active':True},{'protected':True},{'links':['saved_pdf']}):
                storage.put_temporary(db,self.owner,'cache',b'abc',old,**kw)
            fresh=storage.put_temporary(db,self.owner,'abandoned_upload',b'abc',old)
            db.execute('UPDATE storage_temporary SET last_used_at=? WHERE id=?',(self.now,fresh))
            storage.put_temporary(db,self.owner,'temporary_preview',b'abc',self.now-60*86400)
            storage.put_temporary(db,'other','cache',b'abc',old)
        self.assertTrue(self.write('saved_pdf',12))
        with self.assertRaises(RuntimeError):
            with self.a._tx() as db:
                self.assertEqual(storage.cleanup(db,self.a,self.owner)['removed'],1)
                raise RuntimeError('simulate failed commit')
        self.assertEqual(self.a.cleanup_temporary(self.token)['removed'],1)
        self.assertEqual(self.a.cleanup_temporary(self.token)['removed'],0)
        with self.a._tx() as db:
            self.assertEqual(db.execute('SELECT COUNT(*) FROM storage_temporary').fetchone()[0],6)
            self.assertEqual(db.execute('SELECT COUNT(*) FROM workspace_documents').fetchone()[0],1)
            self.assertEqual(db.execute("SELECT COUNT(*) FROM auth_audit WHERE action='temporary_cleaned'").fetchone()[0],1)

if __name__=='__main__':unittest.main()
