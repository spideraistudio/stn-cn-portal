"""Build and smoke-check a complete cumulative Windows review package."""
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
OUT=ROOT.parents[1]/'CN_Web_Phase7_Cumulative.zip'
PRIOR=ROOT.parents[1]/'upload/phase 11.zip'
LOG=ROOT/'verification/phase7_package.txt'

def main():
    for name,marker in [('phase7_http.txt','\nOK\n'),('phase7_storage.txt','\nOK\n'),
                        ('phase7_engine.txt','OK (skipped=1)'),('phase7_concurrent_uploads_final.txt','\nOK\n'),
                        ('phase7_cd_browser.txt','PASS: no browser/API errors.'),
                        ('phase7_offline_browser.txt','PASS: no page errors/failed API calls.'),
                        ('phase7_opening_browser.txt','Only the deliberate forgery failed'),
                        ('phase7_storage_browser.txt','no page errors.')]:
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
        allowed={'PHASE_HANDOFF.md','PHASE_PLAN.md','README.md','docs/PHASE6_FINISH_SECURITY.md',
                 'backend/cn_web/accounts.py','backend/cn_web/http_app.py','backend/cn_web/cli.py',
                 'backend/cn_web/static/account.js','backend/cn_web/calculator_static/web-bridge.js',
                 'tests/test_accounts_http.py'}
        assert changed<=allowed,changed-allowed
        reports.append('PASS: every supplied Phase 6.3.2 file retained; changes restricted to storage/account integration, release markers, release docs and the health-marker test. All engine and original UI renderer/assets unchanged.')
        with tempfile.TemporaryDirectory() as tmp:
            z.extractall(tmp);program=Path(tmp)/ROOT.name
            subprocess.run([sys.executable,'verify_baseline.py'],cwd=program,check=True,capture_output=True)
            for folder in ['calculator_static','static']:
                for js in (program/'backend/cn_web'/folder).glob('*.js'):
                    subprocess.run(['node','--check',str(js)],check=True,capture_output=True)
            subprocess.run([sys.executable,'-m','compileall','-q',str(program/'backend')],check=True,capture_output=True)
            bat=(program/'Start_Web_Phase7_Windows.bat').read_bytes()
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
                for path in ['/','/calculator','/web-bridge.js','/account.js','/cd-card-display.js']:
                    with urllib.request.urlopen(f'http://127.0.0.1:{port}'+path,timeout=3) as r:assert r.status==200
            finally:proc.terminate();proc.communicate(timeout=5)
    reports.append('PASS: ZIP CRC/extraction, all 140 baseline hashes, JS syntax, Python compilation, quoted CRLF Windows launcher and extracted-server startup/health/assets on isolated Linux data.')
    reports.append('PASS: storage boundary/atomic restore and contention tests; threaded concurrent HTTP uploads; permissions/CSRF; cumulative HTTP/security and 332 offline regressions (one skip); fresh Linux Chromium CD, opening-credit, original-screen and storage UI flows. See individual reports for exact results.')
    reports.append('Windows executable/batch execution and user workflow acceptance remain pending. Only Phase 2 has overall Windows acceptance; mapping and latest CD-card checks passed specifically. No hosting/mobile/deployment.')
    LOG.write_text('\n'.join(reports)+'\n');pack()
    with zipfile.ZipFile(OUT) as z:assert z.testzip() is None
    print(LOG.read_text());print(OUT);print('Bytes:',OUT.stat().st_size);print('SHA256:',hashlib.sha256(OUT.read_bytes()).hexdigest())
if __name__=='__main__':main()
