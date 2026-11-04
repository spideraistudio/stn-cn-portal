"""Synthetic local HTTP + Chromium acceptance; no user or live-server data."""
import json,os,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'cn/backend'),str(ROOT/'cn/tests'),str(ROOT/'integration')]
from test_portal import PortalTests
from test_calculator_http import CalculatorHTTPTests
from test_ledger_http import LedgerHTTPTests
case=PortalTests();case.setUp()
try:
    _,b=case.user_browser()
    # Reuse existing synthetic statement and source review helpers.
    for name in ['setup_book','url','state','config','file','imported','detail','review']:
        setattr(case,name,getattr(LedgerHTTPTests,name).__get__(case))
    case.calc=CalculatorHTTPTests.calc.__get__(case)
    case.saved=CalculatorHTTPTests.saved.__get__(case)
    project,book=case.setup_book(b)
    lid,_=CalculatorHTTPTests.mapped_source(case,b,book)
    code,k,_=case.calc(b,book,'native-open',{'ledger_id':lid,'season':'Kharif'});assert code==200,k
    info={'origin':case.origin,'token':b.token,'admin':case.admin.token,'project':project['id'],'workbook':book['id'],'kharif':k['id']}
    result=subprocess.run(['node',str(ROOT/'integration/browser_offline_scope_update.cjs')],env={**os.environ,'CN_FLOW_INFO':json.dumps(info)},cwd=ROOT,timeout=180)
    raise SystemExit(result.returncode)
finally:case.doCleanups()
