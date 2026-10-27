"""Run UI/API smoke against an isolated temporary database."""
from pathlib import Path
import subprocess,os,time,urllib.request,tempfile,sys
ROOT=Path(__file__).resolve().parents[1]
with tempfile.TemporaryDirectory() as d:
 p=subprocess.Popen([sys.executable,str(ROOT/'app.py'),'--no-browser'],env=dict(os.environ,CN_PORT='8765',CN_DATA_PATH=str(Path(d)/'ui.sqlite')),stdout=subprocess.DEVNULL)
 try:
  for n in range(100):
   try:urllib.request.urlopen('http://127.0.0.1:8765/api/health',timeout=1);break
   except Exception:time.sleep(.03)
  else:raise RuntimeError('UI test server did not start')
  for script in (sys.argv[1:] or ['tests/ui_logic_smoke.cjs','tests/payment_studio_smoke.cjs','tests/complete_ui_smoke.cjs','tests/polish_smoke.cjs','tests/abs_assignment_smoke.cjs','tests/abs_distribution_smoke.cjs','tests/ledger_nrv_smoke.cjs','tests/shared_projects_smoke.cjs']):
   subprocess.run(['node',script],cwd=ROOT,check=True)
 finally:p.terminate();p.wait()
