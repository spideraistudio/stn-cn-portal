from functools import partial
from pathlib import Path
import os
import subprocess
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'cn'/'backend'),str(ROOT/'cn'/'tests')]
from cn_web.portal import PortalAccounts
from cn_web.portal_http import PortalApp
import test_accounts_http as h
import run_phase6_browser_flow as run
h.Accounts=run.Accounts=PortalAccounts
h.AccountApp=run.AccountApp=partial(PortalApp,bridge_key='synthetic-browser-key-'*3)
if sys.platform.startswith('linux'):
    exe=os.environ.get('CN_BROWSER_EXECUTABLE') or subprocess.check_output(['node','-e',"import('@sparticuz/chromium').then(m=>m.default.executablePath()).then(console.log)"],cwd=ROOT,text=True).strip()
    os.environ['CN_BROWSER_EXECUTABLE']=exe
    os.environ['CN_CHROMIUM_PACKAGE']=str(ROOT/'node_modules/@sparticuz/chromium/build/cjs/index.cjs') if (ROOT/'node_modules/@sparticuz/chromium/build/cjs/index.cjs').exists() else str(ROOT/'node_modules/@sparticuz/chromium/build/esm/index.js')
    # Read package entry through Node's resolver, without changing application code.
    os.environ['CN_CHROMIUM_PACKAGE']=subprocess.check_output(['node','-p',"require.resolve('@sparticuz/chromium')"],cwd=ROOT,text=True).strip()
    os.environ['NODE_PATH']=str(ROOT/'node_modules')
os.environ.setdefault('CN_BROWSER_REDUCED_MOTION','1')
run.main()
