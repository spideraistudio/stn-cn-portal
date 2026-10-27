"""Cumulative Phase 7.1 Windows ZIP; verification is Linux, not Windows acceptance."""
from pathlib import Path
import hashlib
import os
import socket
import subprocess
import sys
import tempfile
import time
import urllib.request
import zipfile
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT.parents[1]/'CN_Web_Phase7_1_Cumulative.zip'
PRIOR=ROOT.parents[1]/'CN_Web_Phase7_Cumulative.zip'
LOG=ROOT/'verification/hierarchy_package.txt'

def main():
    for name,marker in [('hierarchy_cumulative_http.txt','\nOK\n'),('hierarchy_http.txt','\nOK\n'),
                        ('hierarchy_storage.txt','\nOK\n'),('hierarchy_pan_browser.txt','No page errors.'),
                        ('hierarchy_cd_browser.txt','PASS: no browser/API errors.'),
                        ('hierarchy_offline_browser.txt','PASS: no page errors/failed API calls.'),
                        ('hierarchy_opening_browser.txt','Only the deliberate forgery failed')]:
        assert marker in (ROOT/'verification'/name).read_text(),name
    def pack():
        with zipfile.ZipFile(OUT,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
            for p in sorted(ROOT.rglob('*')):
                if p.is_file() and '__pycache__' not in p.parts and '.git' not in p.parts and p.suffix not in ('.pyc','.pyo'):
                    z.write(p,ROOT.name+'/'+str(p.relative_to(ROOT)))
    pack();reports=[]
    with zipfile.ZipFile(PRIOR) as old,zipfile.ZipFile(OUT) as z:
        assert z.testzip() is None
        original={n for n in old.namelist() if not n.endswith('/')}
        assert original<=set(z.namelist()),original-set(z.namelist())
        changed={str(Path(n).relative_to(ROOT.name)) for n in original if old.read(n)!=z.read(n)}
        allowed={'PHASE_HANDOFF.md','PHASE_PLAN.md','README.md','Recover_Admin.py','manage_web.py',
                 'backend/cn_web/accounts.py','backend/cn_web/http_app.py','backend/cn_web/cli.py',
                 'backend/cn_web/calculator_service.py','backend/cn_web/static/account.js','backend/cn_web/static/index.html',
                 'backend/cn_web/calculator_static/web-bridge.js','backend/cn_web/calculator_static/index.html',
                 'backend/cn_web/calculator_static/studio.js','backend/cn_web/calculator_static/ui-theme.js',
                 'docs/ADMIN_LOGIN_RECOVERY.txt','tests/test_accounts_http.py','tests/test_calculator_http.py','tests/browser_phase7_storage.cjs'}
        assert changed<=allowed,changed-allowed
        reports.append('PASS: all Phase 7 ZIP members retained. Changed files limited to hierarchy/recovery, session appearance, camera pan, user-facing release docs and related tests. Original app.js/payment renderers, financial engine and baseline assets untouched.')
        with tempfile.TemporaryDirectory() as tmp:
            z.extractall(tmp);program=Path(tmp)/ROOT.name
            subprocess.run([sys.executable,'verify_baseline.py'],cwd=program,check=True,capture_output=True)
            for folder in ['calculator_static','static']:
                for js in (program/'backend/cn_web'/folder).glob('*.js'):
                    subprocess.run(['node','--check',str(js)],check=True,capture_output=True)
            subprocess.run([sys.executable,'-m','compileall','-q',str(program/'backend'),str(program/'Recover_Admin.py'),str(program/'manage_web.py')],check=True,capture_output=True)
            bat=(program/'Start_Web_Phase7_1_Windows.bat').read_bytes()
            assert b'cd /d "%~dp0"\r\n' in bat and b'python manage_web.py start-local\r\n' in bat
            with socket.socket() as sock:sock.bind(('127.0.0.1',0));port=sock.getsockname()[1]
            proc=subprocess.Popen([sys.executable,'-m','cn_web.cli','--data',str(Path(tmp)/'isolated-data'),'serve-local','--port',str(port)],cwd=program,env={**os.environ,'PYTHONPATH':str(program/'backend')},stdout=subprocess.PIPE,stderr=subprocess.PIPE)
            try:
                for _ in range(80):
                    try:
                        with urllib.request.urlopen(f'http://127.0.0.1:{port}/health',timeout=1) as r:assert b'7' in r.read()
                        break
                    except OSError:time.sleep(.1)
                else:raise RuntimeError('Extracted server did not start')
                for path in ['/','/calculator','/web-bridge.js','/account.js','/studio.js','/ui-theme.js']:
                    with urllib.request.urlopen(f'http://127.0.0.1:{port}'+path,timeout=3) as r:assert r.status==200
            finally:proc.terminate();proc.communicate(timeout=5)
    reports.append('PASS: ZIP CRC/extraction; all 140 preserved baseline hashes; JS syntax/Python compilation; quoted CRLF Windows launcher; extracted-server startup/health/assets on isolated Linux data.')
    reports.append('PASS: cumulative HTTP/security suite, latest targeted hierarchy/reset/migration/recovery and storage tests; fresh Linux Chromium camera pan/card drag/Navy login/account UI, CD cards/both appearances, original offline workflow and opening-credit Save/navigation/restart. See exact individual reports. Financial regressions run through calculator/finish HTTP suite; Phase 7 full offline regression is prior evidence, not claimed as a new run.')
    reports.append('Prior Phases 2–7 have user-reported Windows acceptance. New Phase 7.1 additions require targeted Windows acceptance. No public hosting/deployment; mobile deferred.')
    LOG.write_text('\n'.join(reports)+'\n');pack()
    with zipfile.ZipFile(OUT) as z:assert z.testzip() is None
    print(LOG.read_text());print(OUT);print('Bytes:',OUT.stat().st_size);print('SHA256:',hashlib.sha256(OUT.read_bytes()).hexdigest())
if __name__=='__main__':main()
