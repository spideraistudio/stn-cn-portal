"""Hierarchy boundaries and resets through authenticated HTTP; synthetic data."""
import concurrent.futures
import importlib.util
import json
from pathlib import Path
import threading
import unittest
import test_accounts_http as fixtures
from cn_web.accounts import Accounts
from cn_web.security import PERMISSIONS
P=fixtures.TEMP_PASSWORD

class HierarchyTests(unittest.TestCase):
    setUp=fixtures.AccountHTTPTests.setUp
    stop=fixtures.AccountHTTPTests.stop
    def create(self, browser, name, **extra):
        status,out,_=browser.request('/api/admin/users',dict(username=name,temporary_password=P,permissions=sorted(PERMISSIONS),**extra))
        self.assertEqual(status,201,out);return out['user']
    def login_new(self,name):
        b=fixtures.Browser(self.origin);b.login(name,P)
        code,_,_=b.request('/api/auth/password',{'current_password':P,'new_password':fixtures.USER_PASSWORD});self.assertEqual(code,200)
        b.login(name,fixtures.USER_PASSWORD);return b
    def admin_account(self,name):
        row=self.create(self.admin,name,role='admin');return row,self.login_new(name)
    def test_defaults_own_scope_no_peer_root_or_ledger_access(self):
        self.assertEqual(self.admin.request('/api/me')[1]['user']['role'],'superadmin')
        a,ab=self.admin_account('admin-a');b,bb=self.admin_account('admin-b')
        self.assertEqual(a['quota_bytes'],1024**3);self.assertEqual(a['max_users'],5)
        u=self.create(ab,'child-a');self.assertEqual(u['parent_admin'],a['id']);self.assertEqual(u['quota_bytes'],250*1024**2)
        self.assertEqual([x['id'] for x in bb.request('/api/admin/users')[1]['users']],[])
        self.assertEqual([x['id'] for x in ab.request('/api/admin/users')[1]['users']],[u['id']])
        for target in [b['id'],self.admin_id,u['id']]:
            if target==u['id']:continue
            self.assertEqual(ab.request('/api/admin/users/'+target+'/reset-password',{'temporary_password':P})[0],404)
        self.assertEqual(bb.request('/api/admin/users/'+u['id'],{'enabled':False},method='PATCH')[0],404)
        self.assertEqual(ab.request('/api/admin/users',{'username':'escalate','temporary_password':P,'permissions':[],'role':'admin'})[0],403)
        self.assertEqual(ab.request('/api/admin/users',{'username':'foreign','temporary_password':P,'permissions':[],'parent_admin':b['id']})[0],403)
        userb=self.login_new('child-a');_,project,_=userb.request('/api/data/projects',{'data':{'name':'private'}})
        self.assertEqual(ab.request('/api/data/projects/'+project['id'])[0],404)
    def test_five_user_limit_concurrent_admin_changes(self):
        a,ab=self.admin_account('admin-a')
        for n in range(4):self.create(ab,'child-'+str(n))
        def create(n):
            try:
                self.accounts.create_user(ab.token,username='race-'+str(n),temporary_password=P,permissions=[])
                return 201
            except fixtures.AuthError as e:return e.status
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:out=list(pool.map(create,range(4)))
        self.assertEqual(out.count(201),1);self.assertEqual(out.count(409),3)
        children=ab.request('/api/admin/users')[1]['users'];self.assertEqual(len(children),5)
        ab.request('/api/admin/users/'+children[0]['id'],{'enabled':False},method='PATCH')
        self.assertEqual(ab.request('/api/admin/users',{'username':'sixth','temporary_password':P,'permissions':[]})[0],409)
    def test_delegated_rights_limits_and_live_revocation(self):
        a,ab=self.admin_account('admin-a')
        self.admin.request('/api/admin/users/'+a['id'],{'permissions':['view_workspace','edit_ledger']},method='PATCH')
        self.assertEqual(ab.request('/api/admin/users',{'username':'too-many-rights','temporary_password':P,'permissions':['edit_schemes']})[0],403)
        self.assertEqual(ab.request('/api/admin/users',{'username':'too-large','temporary_password':P,'permissions':[],'quota_bytes':251*1024**2})[0],403)
        code,out,_=ab.request('/api/admin/users',{'username':'child','temporary_password':P,'permissions':['view_workspace','edit_ledger']});self.assertEqual(code,201,out)
        ub=self.login_new('child');self.assertEqual(ub.request('/api/data/projects',{'data':{'name':'allowed'}})[0],201)
        self.admin.request('/api/admin/users/'+a['id'],{'permissions':['view_workspace']},method='PATCH')
        self.assertEqual(ub.request('/api/data/projects',{'data':{'name':'denied'}})[0],403)
        self.assertEqual(ab.request('/api/admin/users/'+out['user']['id'],{'enabled':False},method='PATCH')[0],200)
        self.assertEqual(ab.request('/api/admin/users/'+out['user']['id'],{'enabled':True},method='PATCH')[0],200)
        self.assertEqual(ab.request('/api/admin/users/'+out['user']['id'],{'max_users':100},method='PATCH')[0],403)
        self.admin.request('/api/admin/users/'+a['id'],{'manage_users':False},method='PATCH')
        self.assertEqual(ab.request('/api/admin/users')[0],403)
    def test_reset_user_admin_sessions_and_data_retained(self):
        a,ab=self.admin_account('admin-a');u=self.create(ab,'child');ub=self.login_new('child')
        _,project,_=ub.request('/api/data/projects',{'data':{'name':'retained'}})
        self.assertEqual(ab.request('/api/admin/users/'+u['id']+'/reset-password',{'temporary_password':P})[0],200)
        self.assertEqual(ub.request('/api/me')[0],401)
        reset=fixtures.Browser(self.origin);reset.login('child',P)
        self.assertTrue(reset.request('/api/me')[1]['user']['must_change_password'])
        self.assertEqual(reset.request('/api/workspace')[0],403)
        reset.request('/api/auth/password',{'current_password':P,'new_password':fixtures.USER_PASSWORD});reset.login('child',fixtures.USER_PASSWORD)
        self.assertEqual(reset.request('/api/data/projects/'+project['id'])[0],200)
        self.assertEqual(self.admin.request('/api/admin/users/'+a['id']+'/reset-password',{'temporary_password':P})[0],200)
        self.assertEqual(ab.request('/api/me')[0],401)
        events=self.admin.request('/api/admin/audit')[1]['events'];self.assertNotIn(P,json.dumps(events))
    def test_disabled_admin_children_revoked_and_reassignment_superadmin_only(self):
        a,ab=self.admin_account('admin-a');b,bb=self.admin_account('admin-b');u=self.create(ab,'child');ub=self.login_new('child')
        self.assertEqual(self.admin.request('/api/admin/users/'+a['id'],{'enabled':False},method='PATCH')[0],200)
        self.assertEqual(ub.request('/api/me')[0],401)
        self.assertEqual(ub.request('/api/auth/login',{'username':'child','password':fixtures.USER_PASSWORD})[0],401)
        self.admin.request('/api/admin/users/'+a['id'],{'enabled':True},method='PATCH')
        self.assertEqual(ub.request('/api/me')[0],401)
        self.assertEqual(self.admin.request('/api/admin/users/'+u['id'],{'parent_admin':b['id']},method='PATCH')[0],200)
        self.assertEqual(len(bb.request('/api/admin/users')[1]['users']),1)
    def test_legacy_migration_and_recovery_backup(self):
        import tempfile,sqlite3
        with tempfile.TemporaryDirectory() as directory:
            old=Accounts(directory);root=old.bootstrap('legacy-root',fixtures.ADMIN_PASSWORD,quota_bytes=987654)
            token=old.login('legacy-root',fixtures.ADMIN_PASSWORD,'legacy')
            u=old.create_user(token,username='legacy-user',temporary_password=P,permissions=[])
            with old._tx() as db:db.execute('DROP TABLE account_roles')
            upgraded=Accounts(directory)
            self.assertEqual(upgraded.me(token)['role'],'superadmin')
            rows=upgraded.list_users(token);self.assertEqual(rows[0]['quota_bytes'],987654)
            self.assertIsNone(next(r for r in rows if r['id']==u['id'])['parent_admin'])
            spec=importlib.util.spec_from_file_location('recovery',Path(__file__).resolve().parents[1]/'Recover_Admin.py');mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
            backup=mod.recover(Path(directory)/'accounts.sqlite3','legacy-root','Recovered root password 2026!')
            self.assertTrue(backup.is_file());self.assertEqual(mod.admins(Path(directory)/'accounts.sqlite3'),[('legacy-root',)])
            with sqlite3.connect(backup) as db:self.assertEqual(db.execute('PRAGMA integrity_check').fetchone()[0],'ok')
            with self.assertRaises(fixtures.AuthError):upgraded.me(token)
    def test_navy_default_per_login_preserves_classic_selection_within_session(self):
        # Existing calculator fixtures exercise saved appearance/layout APIs.
        from test_finish_http import FinishHTTPTests
        case=FinishHTTPTests();case.setUp()
        try:
            _,b=case.user_browser();_,wb=case.setup_book(b)
            code,out,_=case.calc(b,wb,'ui-preferences',None);self.assertEqual(code,200,out);self.assertEqual(out['theme'],'studio')
            code,out,_=case.calc(b,wb,'ui-preferences',{'theme':'classic'});self.assertEqual(code,200,out)
            self.assertEqual(case.calc(b,wb,'ui-preferences',None)[1]['theme'],'classic')
            b.login('user-a',fixtures.USER_PASSWORD)
            self.assertEqual(case.calc(b,wb,'ui-preferences',None)[1]['theme'],'studio')
        finally:case.doCleanups()

if __name__=='__main__':unittest.main()
