"""Real HTTP ownership, backup, permission and revision regressions."""
import concurrent.futures
import copy
import sqlite3
import unittest
import test_accounts_http as helpers


class WorkspaceHTTPTests(unittest.TestCase):
    setUp = helpers.AccountHTTPTests.setUp
    stop = helpers.AccountHTTPTests.stop
    create = helpers.AccountHTTPTests.create
    user_browser = helpers.AccountHTTPTests.user_browser
    def setup_pair(self):
        ua, a = self.user_browser('owner-a')
        ub, b = self.user_browser('owner-b')
        return a, ua, b, ub

    def make(self, browser, kind, name='Test', **scope):
        code, d, _ = browser.request('/api/data/'+kind, {'data': {'name': name}, **scope})
        self.assertEqual(code, 201, d)
        return d

    def test_owned_graph_and_export_import(self):
        a, ua, b, ub = self.setup_pair()
        p = self.make(a, 'projects')
        w = self.make(a, 'workbooks', project=p['id'])
        party = self.make(a, 'parties', project=p['id'], workbook=w['id'])
        scheme = self.make(a, 'schemes', project=p['id'])
        for kind, r in [('projects', p), ('workbooks', w), ('parties', party), ('schemes', scheme)]:
            for method, body in [('GET', None), ('PATCH', {'revision': 1, 'data': {'name':'Intruder'}}), ('DELETE', {'revision':1})]:
                self.assertEqual(b.request('/api/data/'+kind+'/'+r['id'],body,method)[0],404)
            self.assertEqual(b.request('/api/data/'+kind)[1]['items'],[])
            self.assertEqual(self.admin.request('/api/data/'+kind+'/'+r['id'])[0],404)
        self.assertEqual(b.request('/api/projects/'+p['id']+'/export')[0],404)
        self.assertEqual(b.request('/api/data/parties',{'project':p['id'],'workbook':w['id'],'data':{'name':'x'}})[0],404)
        code, backup, _ = a.request('/api/projects/'+p['id']+'/export')
        self.assertEqual(code,200)
        text=str(backup)
        for secret in ['password_hash','csrf_token','permissions','token_hash',ua['id']]:
            self.assertNotIn(secret,text)
        code, imported, _=b.request('/api/projects/import',{'backup':backup})
        self.assertEqual(code,201,imported)
        self.assertNotEqual(imported['project_id'],p['id'])
        self.assertEqual(len(b.request('/api/data/parties')[1]['items']),1)
        self.assertEqual(a.request('/api/data/parties/'+party['id'])[1]['revision'],1)
        bad=copy.deepcopy(backup);bad['documents'][-1]['project']='f'*32
        before=b.request('/api/data/projects')[1]
        self.assertEqual(b.request('/api/projects/import',{'backup':bad})[0],400)
        self.assertEqual(before,b.request('/api/data/projects')[1])
        # Import must not bypass edit_schemes, even via project backup.
        self.admin.request('/api/admin/users/'+ub['id'],{'permissions':['view_workspace','import_statements','edit_ledger']},'PATCH')
        self.assertEqual(b.request('/api/projects/import',{'backup':backup})[0],403)
        self.assertEqual(before,b.request('/api/data/projects')[1])

    def test_revision_atomicity_files_layouts_and_revocation(self):
        a, ua, b, ub=self.setup_pair()
        p=self.make(a,'projects');w=self.make(a,'workbooks',project=p['id'])
        url='/api/data/workbooks/'+w['id']
        with concurrent.futures.ThreadPoolExecutor(2) as pool:
            result=list(pool.map(lambda n:a.request(url,{'revision':1,'data':{'name':str(n)}},'PATCH')[0],[1,2]))
        self.assertEqual(sorted(result),[200,409])
        for kind, data in [('files',{'name':'../../source.pdf','content_base64':'AAEC/w=='}),('layouts',{'name':'Studio','theme':'studio','record_id':'party-1','positions':[{'key':'cash','x':-34,'y':100}],'locked':True})]:
            status,r,_=a.request('/api/data/'+kind,{'project':p['id'],'workbook':w['id'],'data':data})
            self.assertEqual(status,201,r)
            self.assertEqual(a.request('/api/data/'+kind+'/'+r['id'])[1]['data'],data)
            self.assertEqual(b.request('/api/data/'+kind+'/'+r['id'])[0],404)
        # Same internal ID in distinct owners remains independent.
        with self.accounts._tx() as db:
            db.execute('INSERT INTO workspace_documents VALUES(?,?,?,?,?,1,0,?)',(ub['id'],p['id'],'projects',None,None,'{"name":"Other"}'))
        self.assertEqual(b.request('/api/data/projects/'+p['id'])[1]['data']['name'],'Other')
        self.assertEqual(a.request('/api/data/projects/'+p['id'])[1]['data']['name'],'Test')
        self.assertEqual(a.request('/api/data/projects/'+p['id'],{'revision':1},'DELETE')[0],409)
        self.admin.request('/api/admin/users/'+ua['id'],{'permissions':['view_workspace']},'PATCH')
        self.assertEqual(a.request(url,{'revision':2,'data':{'name':'blocked'}},'PATCH')[0],403)
        self.admin.request('/api/admin/users/'+ua['id'],{'enabled':False},'PATCH')
        self.assertEqual(a.request(url)[0],401)

    def test_strict_mutation_boundaries(self):
        ua, a=self.user_browser()
        p=self.make(a,'projects')
        for kind in ['projects','workbooks','schemes','settings','parties','files','layouts']:
            payload={'data':{'name':'Bad','issued':True}}
            if kind!='projects':payload['project']=p['id']
            self.assertIn(a.request('/api/data/'+kind,payload)[0],[400,404])
        self.assertEqual(a.request('/api/data/projects',{'data':{'name':'x'},'owner':ua['id']})[0],400)
        self.assertEqual(a.request('/api/data/projects',{'data':{'name':'x'}},headers={'X-CSRF-Token':''})[0],403)
        self.assertEqual(a.request('/api/data/projects?owner='+ua['id'])[0],400)
        self.assertEqual(a.request('/api/data/files',{'project':p['id'],'data':{'name':'file','content_base64':'invalid!'}})[0],400)
        self.assertEqual(a.request('/api/data/layouts',{'project':p['id'],'data':{'name':'Bad','theme':'unknown'}})[0],400)

    def test_parallel_store_writes_and_restart(self):
        ua, a = self.user_browser()
        p=self.make(a,'projects')
        store=self.app.store
        def save(n):
            try:
                return store.request(a.token,'PATCH','projects',p['id'],{'revision':1,'data':{'name':str(n)}})['revision']
            except helpers.AuthError as e:
                return e.status
        with concurrent.futures.ThreadPoolExecutor(2) as pool:
            self.assertEqual(sorted(pool.map(save,[1,2])),[2,409])
        from cn_web.data_store import DataStore
        from cn_web.accounts import Accounts
        restarted=DataStore(Accounts(self.tmp.name,clock=lambda:self.now[0]))
        self.assertEqual(restarted.request(a.token,'GET','projects',p['id'])['revision'],2)
        self.accounts.logout(a.token,all_sessions=True)
        with self.assertRaises(helpers.AuthError):
            restarted.request(a.token,'POST','projects',data={'data':{'name':'Blocked'}})

    def test_download_and_all_new_permission_boundaries(self):
        ua, a=self.user_browser()
        ub, b=self.user_browser('owner-b')
        p=self.make(a,'projects');w=self.make(a,'workbooks',project=p['id'])
        status, f, _=a.request('/api/data/files',{'project':p['id'],'data':{'name':'sample.pdf','content_base64':'UERG'}})
        self.assertEqual(status,201)
        self.assertEqual(a.request('/api/files/'+f['id']+'/download')[0],200)
        self.assertEqual(b.request('/api/files/'+f['id']+'/download')[0],404)
        self.admin.request('/api/admin/users/'+ua['id'],{'permissions':['view_workspace']},'PATCH')
        self.assertEqual(a.request('/api/files/'+f['id']+'/download')[0],403)
        self.assertEqual(a.request('/api/projects/'+p['id']+'/export')[0],403)
        for kind in ['projects','workbooks','schemes','settings','parties','files']:
            payload={'data':{'name':'Denied'}}
            if kind!='projects':payload.update(project=p['id'],workbook=w['id'])
            self.assertEqual(a.request('/api/data/'+kind,payload)[0],403)
        self.admin.request('/api/admin/users/'+ua['id'],{'permissions':[]},'PATCH')
        for kind in ['projects','workbooks','schemes','settings','parties','files','layouts']:
            self.assertEqual(a.request('/api/data/'+kind)[0],403)
