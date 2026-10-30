import sys,unittest
from pathlib import Path
root=Path(__file__).resolve().parents[1]/'cn'
sys.path[:0]=[str(root/'backend'),str(root/'offline_baseline'),str(root/'offline_baseline/tests')]
from cn_web import ledger_service
import engine
print('Engine under test:',engine.__file__,flush=True)
private={'ashapura.pdf','ashapura_ipt.pdf','khammam_current_fy.pdf','khammam_previous_fy.pdf','krishna_ipt.pdf','maharashtra.pdf','surendranagar_combined.pdf'}
class Results(unittest.TextTestResult):
 def addError(self,test,err):
  e=err[1]
  if isinstance(e,FileNotFoundError) and Path(e.filename or '').name in private:self.addSkip(test,'Private fixture absent: '+Path(e.filename).name)
  else:super().addError(test,err)
suite=unittest.defaultTestLoader.discover(str(root/'offline_baseline/tests'),pattern='test_*.py')
if not (root/'offline_baseline/fixtures/ashapura.pdf').exists():
 import test_http
 for name in ('test_excessive_split_rejected_http','test_import_save_reopen_calculate','test_party_and_scheme_delete_restore_http'):
  setattr(test_http.LocalHTTPTests,name,unittest.skip('Private ashapura.pdf is not included in repository')(getattr(test_http.LocalHTTPTests,name)))
r=unittest.TextTestRunner(verbosity=1,resultclass=Results).run(suite)
raise SystemExit(not r.wasSuccessful())
