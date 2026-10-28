"""Source-package verification without touching user data."""
import hashlib,json
from pathlib import Path
import subprocess,sys,zipfile
ROOT=Path(__file__).resolve().parents[1]
subprocess.run([sys.executable,str(ROOT/'cn/verify_baseline.py'),'--allow-private-fixtures'],check=True,cwd=ROOT)
required=['INTEGRATION_README.md','PHASE_HANDOFF.md','PHASE_PLAN.md','TEST_RESULTS.md','WINDOWS_ACCEPTANCE.md','package.json','package-lock.json','Setup_Combined_Windows.bat','Setup_Combined_Admin_Windows.bat','Start_Local_Mongo_Windows.bat','Start_Combined_Windows.bat','integration/run_local.py','cn/backend/cn_web/portal.py']
assert all((ROOT/p).is_file() for p in required)
for p in ['verification/full_stack.txt','verification/portal_http.txt','verification/cn_cumulative.txt','verification/cn_integrated_http.txt']:
    text=(ROOT/p).read_text();assert 'Traceback' not in text and 'FAILED' not in text,p
print('PASS package source, Windows launchers, preserved baseline, archived test records and required handoff files. This check does not rerun workflows or certify deployment.')
