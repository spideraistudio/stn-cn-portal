"""Phase 4 static delivery plus real owned audit/review/reopen regressions."""
import copy
import unittest
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'integration'))
from run_local import Gateway
import test_native_interface_http as native

class Phase4HTTP(unittest.TestCase):
    setUp=native.NativeInterfaceTests.setUp
    stop=native.NativeInterfaceTests.stop
    create=native.NativeInterfaceTests.create
    user_browser=native.NativeInterfaceTests.user_browser
    setup_book=native.NativeInterfaceTests.setup_book
    config=native.NativeInterfaceTests.config
    state=native.NativeInterfaceTests.state
    url=native.NativeInterfaceTests.url
    file=native.NativeInterfaceTests.file
    calc=native.NativeInterfaceTests.calc

    def test_assets_and_owned_review_reopen_preserve_evidence(self):
        self.server.set_app(Gateway(self.app,node_port=1)) # Assets must never fall through to STN.
        _,browser=self.user_browser();_,w=self.setup_book(browser);self.config(browser,w)
        code,html,_=browser.request('/calculator');self.assertEqual(code,200)
        self.assertLess(html.index('/audit-product-mapping.js'),html.index('/audit-categories.js'))
        self.assertLess(html.index('/audit-categories.js'),html.index('/billing-audit.js'))
        for asset,mime in [('audit-categories.js','javascript'),('audit-categories.css','text/css')]:
            code,body,headers=browser.request('/'+asset);self.assertEqual(code,200)
            self.assertIn(mime,headers['Content-Type']);self.assertTrue(body)
        code,imported,_=self.calc(browser,w,'native-audit-import',{'data':self.file('duplicate_receipts.pdf')['content_base64']});self.assertEqual(code,200,imported)
        args={'documents':imported['documents'],'start':'2026-04-01','end':'2027-03-31'}
        code,report,_=self.calc(browser,w,'native-audit-check',args);self.assertEqual(code,200,report)
        finding=report['findings'][0];evidence=copy.deepcopy(finding['vouchers'])
        code,current,_=self.calc(browser,w,'state');self.assertEqual(code,200,current)
        settings=current['settings']
        save={**args,'finding':finding,'review_id':finding['review_id'],'reason':'Bank evidence checked','version':settings['version']}
        _,foreign=self.user_browser('phase4-foreign');_,fw=self.setup_book(foreign);self.config(foreign,fw)
        self.assertEqual(self.calc(foreign,fw,'native-audit-check',args)[0],404)
        self.assertEqual(self.calc(foreign,w,'native-audit-review',save)[0],404)
        code,saved,_=self.calc(browser,w,'native-audit-review',save);self.assertEqual(code,200,saved)
        fresh=self.calc(browser,w,'native-audit-check',args)[1]['findings'][0]
        self.assertEqual(fresh['review']['status'],'not_applicable');self.assertEqual(fresh['vouchers'],evidence)
        self.assertEqual(self.calc(browser,w,'native-audit-review',{**save,'version':saved['version'],'review_id':'wrong'})[0],409)
        code,reopened,_=self.calc(browser,w,'native-audit-review',{**save,'version':saved['version'],'reset':True});self.assertEqual(code,200,reopened)
        fresh=self.calc(browser,w,'native-audit-check',args)[1]['findings'][0]
        self.assertIsNone(fresh['review']);self.assertEqual(fresh['vouchers'],evidence)
        self.assertEqual(self.calc(browser,w,'native-audit-review',save)[0],400)

if __name__=='__main__':unittest.main()
