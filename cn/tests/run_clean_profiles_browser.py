import json,os,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/'integration'),str(ROOT/'cn/tests'),str(ROOT/'cn/backend')]
from test_portal import PortalTests
case=PortalTests()
case.setUp()
try:
    _,browser=case.user_browser()
    info={'origin':case.origin,'token':browser.token}
    subprocess.run(['node',str(ROOT/'cn/tests/browser_clean_profiles.cjs')],cwd=ROOT,env={**os.environ,'CN_FLOW_INFO':json.dumps(info)},check=True)
finally:case.doCleanups()
