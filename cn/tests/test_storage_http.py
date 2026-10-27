"""Concurrent real HTTP uploads against the same persistent capacity."""
import test_accounts_http as fixtures
Browser=fixtures.Browser
from socketserver import ThreadingMixIn
from wsgiref.simple_server import WSGIServer, make_server
from cn_web.cli import QuietHandler
from cn_web.security import PERMISSIONS
import concurrent.futures
import threading
import base64
import unittest

class ThreadedServer(ThreadingMixIn, WSGIServer):
    daemon_threads=True

class StorageHTTPTests(unittest.TestCase):
    setUp=fixtures.AccountHTTPTests.setUp
    stop=fixtures.AccountHTTPTests.stop
    def test_concurrent_files_quota_and_cleanup_permissions(self):
        self.server.shutdown();self.thread.join();self.server.server_close()
        self.server=make_server('127.0.0.1',0,self.app,server_class=ThreadedServer,handler_class=QuietHandler)
        self.origin='http://127.0.0.1:'+str(self.server.server_port)
        self.app.origin=self.origin;self.app.authority='127.0.0.1:'+str(self.server.server_port)
        self.thread=threading.Thread(target=self.server.serve_forever,kwargs={'poll_interval':.01},daemon=True);self.thread.start()
        self.admin=Browser(self.origin);self.admin.login('admin','Admin test passphrase 2026!')
        status,p,_=self.admin.request('/api/data/projects',{'data':{'name':'Quota test'}})
        self.assertEqual(status,201);project=p['id']
        before=self.admin.request('/api/workspace')[1]['used_bytes']
        with self.accounts._tx() as db:db.execute('UPDATE workspaces SET quota_bytes=? WHERE user_id=?',(before+2100,self.admin_id))
        def upload(n):
            client=Browser(self.origin);client.token=self.admin.token;client.csrf=self.admin.csrf
            return client.request('/api/data/files',{'project':project,'data':{'name':str(n),'content_base64':base64.b64encode(b'x'*1400).decode()}})[0]
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:outcomes=list(pool.map(upload,range(4)))
        self.assertEqual(outcomes.count(201),1);self.assertEqual(outcomes.count(413),3)
        usage=self.admin.request('/api/workspace')[1];self.assertLessEqual(usage['used_bytes'],usage['quota_bytes'])
        self.assertEqual(len(self.admin.request('/api/data/files')[1]['items']),1)
        self.assertEqual(self.admin.request('/api/storage/cleanup',{})[0],200)
        with self.accounts._tx() as db:
            import json
            db.execute('UPDATE users SET permissions=? WHERE id=?',(json.dumps(sorted(PERMISSIONS-{'delete_records'})),self.admin_id))
        self.assertEqual(self.admin.request('/api/storage/cleanup',{})[0],403)
        self.assertEqual(self.admin.request('/api/storage/cleanup',{},headers={'X-CSRF-Token':'bad'})[0],403)

if __name__=='__main__':unittest.main()
