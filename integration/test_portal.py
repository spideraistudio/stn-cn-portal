import concurrent.futures
import json
from pathlib import Path
import sys
import unittest
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'cn'/'tests'),str(ROOT/'cn'/'backend')]
import test_accounts_http as h
from cn_web.portal import PortalAccounts
from cn_web.portal_http import PortalApp
from cn_web.security import PERMISSIONS,AuthError,csrf_token

class PortalTests(h.AccountHTTPTests):
    def setUp(self):
        old_a,old_app=h.Accounts,h.AccountApp
        h.Accounts=PortalAccounts
        h.AccountApp=lambda *a,**k:PortalApp(*a,bridge_key='b'*64,**k)
        try:super().setUp()
        finally:h.Accounts,h.AccountApp=old_a,old_app

    def test_health_and_pc_console_have_no_credentials(self):
        self.assertEqual(self.admin.request("/health")[0],200)
        code,html,_=self.admin.request("/");self.assertEqual(code,200)
        self.assertIn("/portal.js",html);self.assertNotIn(h.ADMIN_PASSWORD,html)

    def company(self,name='Company A',cn=True,stn=True):
        code,data,_=self.admin.request('/api/portal/company',{'name':name,'cn':cn,'stn':stn,'enabled':True})
        self.assertEqual(code,200,data);return data

    def test_company_admin_private_ownership_limits_linking(self):
        c=self.company()
        admin=self.accounts.create_user(self.admin.token,username='company-admin',temporary_password=h.TEMP_PASSWORD,permissions=sorted(PERMISSIONS),role='admin')
        self.assertEqual(admin['quota_bytes'],1024**3)
        self.accounts.access(self.admin.token,{'user_id':admin['id'],'company_id':c['id'],'cn':True,'stn':True})
        t=self.accounts.login('company-admin',h.TEMP_PASSWORD,'local')
        self.accounts.change_password(t,h.TEMP_PASSWORD,h.USER_PASSWORD)
        t=self.accounts.login('company-admin',h.USER_PASSWORD,'local')
        users=[]
        for i in range(5):
            u=self.accounts.create_user(t,username=f'staff-{i}',temporary_password=h.TEMP_PASSWORD,permissions=sorted(PERMISSIONS));users.append(u)
            self.assertEqual(u['quota_bytes'],250*1024**2)
        with self.assertRaises(AuthError):self.accounts.create_user(t,username='sixth',temporary_password=h.TEMP_PASSWORD,permissions=[])
        own=self.accounts.overview(t)
        self.assertEqual(len(own['users']),5)
        self.assertTrue(all(u['company']['id']==c['id'] for u in own['users']))
        with self.assertRaises(AuthError):self.accounts.company(t,{'name':'Escalate'})
        with self.assertRaises(AuthError):self.accounts.access(t,{'user_id':users[0]['id'],'company_id':c['id']})
        with self.assertRaises(AuthError):self.accounts.access(t,{'user_id':self.admin_id,'cn':False})
        self.accounts.access(self.admin.token,{'user_id':users[0]['id'],'stn_member_id':'000000000000000000000001','stn':True})
        self.accounts.access(self.admin.token,{'user_id':users[1]['id'],'stn_member_id':'000000000000000000000001'})
        outsider=self.accounts.create_user(self.admin.token,username='outsider',temporary_password=h.TEMP_PASSWORD,permissions=[])
        with self.assertRaises(AuthError):self.accounts.access(self.admin.token,{'user_id':outsider['id'],'stn_member_id':'000000000000000000000001'})
        linked=self.accounts.overview(self.admin.token)['users']
        self.assertEqual(next(u for u in linked if u['id']==users[0]['id'])['stn_member_id'],'000000000000000000000001')

    def test_revocation_entitlements_expiry_and_no_revival(self):
        c=self.company();u,b=self.user_browser();uid=u['id']
        self.accounts.access(self.admin.token,{'user_id':uid,'company_id':c['id'],'cn':True,'stn':True})
        self.assertEqual(b.request('/api/me')[0],401)
        b.login('user-a',h.USER_PASSWORD)
        self.assertTrue(self.accounts.introspect(b.token)['modules']['stn'])
        c=self.accounts.company(self.admin.token,{'id':c['id'],'revision':c['revision'],'cn':False})
        self.assertEqual(b.request('/api/workspace')[0],401)
        b.login('user-a',h.USER_PASSWORD)
        self.assertEqual(b.request('/api/workspace')[0],403)
        self.assertTrue(self.accounts.introspect(b.token)['modules']['stn'])
        self.assertFalse(self.accounts.introspect(b.token)['modules']['cn'])
        self.accounts.company(self.admin.token,{'id':c['id'],'revision':c['revision'],'cn':True,'ends_at':self.now[0]-1})
        b.login('user-a',h.USER_PASSWORD)
        self.assertEqual(self.accounts.introspect(b.token)['modules'],{'cn':False,'stn':False})

    def test_private_introspection_and_csrf(self):
        self.assertEqual(self.admin.request('/internal/portal/introspect',{})[0],404)
        code,data,_=self.admin.request('/internal/portal/introspect',{},headers={'X-Portal-Key':'b'*64})
        self.assertEqual(code,200,data);self.assertEqual(data['role'],'superadmin')
        self.assertNotIn('permissions',data);self.assertNotIn('password_hash',data)
        self.assertEqual(self.admin.request('/api/portal/company',{'name':'bad'},headers={'X-CSRF-Token':'bad'})[0],403)
        self.assertEqual(self.admin.request('/api/portal/company',{'name':'bad','cn':'yes'})[0],400)
        self.assertEqual(self.admin.request('/internal/portal/verify-password',{'password':h.ADMIN_PASSWORD},headers={'X-Portal-Key':'b'*64})[1],{'valid':True})

    def test_explicit_reassignment_clears_previous_company_stn_link(self):
        c1=self.company('First');c2=self.company('Second')
        a1=self.accounts.create_user(self.admin.token,username='first-admin',temporary_password=h.TEMP_PASSWORD,permissions=sorted(PERMISSIONS),role='admin')
        a2=self.accounts.create_user(self.admin.token,username='second-admin',temporary_password=h.TEMP_PASSWORD,permissions=sorted(PERMISSIONS),role='admin')
        for admin,c in [(a1,c1),(a2,c2)]:self.accounts.access(self.admin.token,{'user_id':admin['id'],'company_id':c['id']})
        u=self.accounts.create_user(self.admin.token,username='moving-user',temporary_password=h.TEMP_PASSWORD,permissions=[],parent_admin=a1['id'])
        self.accounts.access(self.admin.token,{'user_id':u['id'],'stn':True,'stn_member_id':'000000000000000000000001'})
        self.accounts.update_user(self.admin.token,u['id'],{'parent_admin':a2['id']})
        moved=next(v for v in self.accounts.overview(self.admin.token)['users'] if v['id']==u['id'])
        self.assertEqual(moved['company']['id'],c2['id']);self.assertIsNone(moved['stn_member_id']);self.assertFalse(moved['stn'])

    def test_previous_local_link_schema_preserves_identity_on_upgrade(self):
        u=self.accounts.create_user(self.admin.token,username='legacy-portal-user',temporary_password=h.TEMP_PASSWORD,permissions=[])
        with self.accounts._tx() as db:
            db.execute('ALTER TABLE portal_memberships RENAME TO saved_links')
            db.execute('CREATE TABLE portal_memberships(user_id TEXT PRIMARY KEY,company_id TEXT,cn INTEGER NOT NULL DEFAULT 1,stn INTEGER NOT NULL DEFAULT 0,stn_member_id TEXT UNIQUE)')
            db.execute('INSERT INTO portal_memberships SELECT * FROM saved_links')
            db.execute('DROP TABLE saved_links')
        upgraded=PortalAccounts(self.tmp.name,clock=lambda:self.now[0])
        token=upgraded.login('legacy-portal-user',h.TEMP_PASSWORD,'local')
        self.assertEqual(upgraded.me(token)['id'],u['id'])
        self.assertEqual(upgraded.me(token)['quota_bytes'],u['quota_bytes'])

    def test_company_revision_and_scoped_session_revocation(self):
        c=self.company()
        self.accounts.company(self.admin.token,{'id':c['id'],'revision':c['revision'],'name':'Renamed'})
        with self.assertRaises(AuthError):self.accounts.company(self.admin.token,{'id':c['id'],'revision':c['revision'],'name':'Stale'})
        u,b=self.user_browser();uid=u['id']
        self.accounts.revoke(self.admin.token,uid)
        self.assertEqual(b.request('/api/me')[0],401)
        self.assertEqual(self.admin.request('/api/me')[0],200)

if __name__=='__main__':unittest.main(verbosity=2)
