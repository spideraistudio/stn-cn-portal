"""Fresh settings are empty; existing payloads, mappings and frozen history survive."""
import copy
import sys
import unittest
from pathlib import Path
sys.path[:0]=[str(Path(__file__).resolve().parents[2]/'integration')]
import test_portal as portal_tests
from cn_web.calculator_service import Runtime
from settings import initial_settings


class CleanRuntimeTests(unittest.TestCase):
    def test_empty_workbook_never_inherits_reference_catalogue(self):
        st=Runtime(None,{'catalogue':[],'periods':[]},None)
        try:
            cfg=st.settings()
            self.assertEqual(cfg['products'],[]);self.assertEqual(cfg['schemes'],[])
            self.assertEqual(cfg['seasons'],[{'name':'Working season','start':None,'end':None,'cutoff':None,'confirmed':False}])
            self.assertEqual(st.all(),[])
            self.assertTrue(all(not st.payload()[t] for t in ('records','bulk_imports','issued','audit')))
        finally:st.connection.close()
    def test_existing_payload_preserves_all_settings_and_history(self):
        st=Runtime(None,{'catalogue':[],'periods':[]},None)
        try:
            cfg=initial_settings();cfg['version']=1
            st.save_settings(cfg)
            st.connection.execute("INSERT INTO issued VALUES('test','123','{}')");st.connection.commit()
            saved=st.payload()
            other=Runtime(saved,{'catalogue':[],'periods':[]},None)
            try:self.assertEqual(other.payload(),saved)
            finally:other.connection.close()
        finally:st.connection.close()
    def test_own_catalogue_only_gets_unconfigured_placeholders(self):
        p={'id':'own','crop':'Soybean','name':'Custom seed','segment':'Own segment','packing_kg':'20','aliases':[]}
        cfg=Runtime.seed({'catalogue':[p],'periods':[{'name':'Own season','start':'2026-04-01','end':'2026-08-31','cutoff':'2026-11-30'}]})
        self.assertEqual([x['id'] for x in cfg['products']],['own']);self.assertEqual(len(cfg['schemes']),1)
        sc=cfg['schemes'][0]
        self.assertFalse(sc['confirmed']);self.assertEqual(sc['benefits'],[]);self.assertIsNone(sc['billing']);self.assertEqual(sc['cd'],[])


class CleanProfileHTTPTests(unittest.TestCase):
    def setUp(self):
        h=portal_tests.h
        old_accounts,old_app=h.Accounts,h.AccountApp
        h.Accounts=portal_tests.PortalAccounts
        h.AccountApp=lambda *a,**k:portal_tests.PortalApp(*a,bridge_key='b'*64,**k)
        try:h.AccountHTTPTests.setUp(self)
        finally:h.Accounts,h.AccountApp=old_accounts,old_app
    stop=portal_tests.PortalTests.stop
    create=portal_tests.PortalTests.create
    user_browser=portal_tests.PortalTests.user_browser
    def start(self,b,name='Fresh workbook'):
        code,data,_=b.request('/api/portal/start-workbook',{'name':name,'state':'Gujarat','period':'Own season','start':'2026-04-01','end':'2026-08-31','cutoff':'2026-11-30'})
        self.assertEqual(code,201,data);return {'X-CN-Project':data['project'],'X-CN-Workbook':data['workbook']}
    def test_two_fresh_users_start_empty_and_cannot_read_each_other(self):
        _,a=self.user_browser();_,b=self.user_browser('second-user')
        for browser in (a,b):
            for kind in ('projects','workbooks','parties','files','schemes','layouts'):
                code,data,_=browser.request('/api/data/'+kind);self.assertEqual(code,200,data);self.assertEqual(data['items'],[])
        headers=self.start(a)
        code,data,_=a.request('/api/calculator/native-state',headers=headers);self.assertEqual(code,200,data)
        for key in ('products','schemes'):self.assertEqual(data['settings'][key],[])
        self.assertEqual(data['settings']['seasons'][0]['name'],'Own season');self.assertEqual(data['records'],[]);self.assertEqual(data['bulk_history'],[])
        self.assertEqual(b.request('/api/calculator/native-state',headers=headers)[0],404)
        own=self.start(b);self.assertEqual(b.request('/api/calculator/native-state',headers=own)[1]['settings']['products'],[])
    def test_blank_workbook_does_not_copy_own_saved_catalogue(self):
        _,b=self.user_browser();headers=self.start(b)
        old=initial_settings();old['seasons']=b.request('/api/calculator/native-state',headers=headers)[1]['settings']['seasons']
        for scheme in old['schemes']:scheme['season']='Own season'
        code,saved,_=b.request('/api/calculator/settings',old,headers=headers);self.assertEqual(code,200,saved)
        before=copy.deepcopy(saved)
        code,new,_=b.request('/api/calculator/workbooks',{'name':'Empty workbook','state':'Gujarat','period':'New season','start':'2026-10-01','end':'2027-02-28','cutoff':'2027-03-31','mode':'blank','source':headers['X-CN-Workbook']},headers=headers);self.assertEqual(code,200,new)
        h={**headers,'X-CN-Workbook':new['id']}
        fresh=b.request('/api/calculator/native-state',headers=h)[1]
        self.assertEqual(fresh['settings']['products'],[]);self.assertEqual(fresh['settings']['schemes'],[])
        original=b.request('/api/calculator/native-state',headers=headers)[1]['settings'];self.assertEqual(original,before)

if __name__=='__main__':unittest.main()
