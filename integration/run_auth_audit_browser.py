"""Run browser auth checks against disposable, isolated account data."""
import json, os, subprocess, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'integration'),str(ROOT/'cn/tests'),str(ROOT/'cn/backend')]
from test_portal import PortalTests
from test_accounts_http import USER_PASSWORD
case=PortalTests()
case.setUp()
try:
    _, browser=case.user_browser()
    info={'origin':case.origin,'token':browser.token,'username':'user-a','password':USER_PASSWORD}
    subprocess.run(['node',str(ROOT/'integration/browser_auth_audit.cjs')],cwd=ROOT,env={**os.environ,'AUTH_AUDIT_INFO':json.dumps(info)},check=True)
finally:case.doCleanups()
