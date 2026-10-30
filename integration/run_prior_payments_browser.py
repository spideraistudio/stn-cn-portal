import sys,subprocess,json,os
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'cn/backend'),str(ROOT/'cn/tests')]
from functools import partial
from cn_web.portal import PortalAccounts
from cn_web.portal_http import PortalApp
import test_accounts_http as helpers
helpers.Accounts=PortalAccounts;helpers.AccountApp=partial(PortalApp,bridge_key='browser-test-bridge-'*4)
from test_prior_payments_http import PriorPaymentHTTPTests,statement
x=PriorPaymentHTTPTests();x.setUp()
try:
 u,b,w,r,refs,m=x.prepare()
 prior=Path(x.tmp.name)/'prior-browser-input.pdf';prior.write_bytes(statement())
 wrong=Path(x.tmp.name)/'prior-browser-wrong.pdf';wrong.write_bytes(statement(wrong=True))
 info={'token':b.token,'origin':x.origin,'project':w['project'],'workbook':w['id'],'record':r['id'],'prior':str(prior),'wrong':str(wrong)}
 subprocess.run(['node',str(ROOT/'integration/browser_prior_payments.cjs')],check=True,env={**os.environ,'PRIOR_BROWSER_INFO':json.dumps(info)})
finally:x.doCleanups()
