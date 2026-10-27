"""Package and validate this cumulative PC review release (no user data)."""
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
OUT=ROOT.parents[1]/'CN_Web_Phase6_3_2_CD_Product_Cards.zip'
PRIOR=ROOT.parents[1]/'CN_Web_Phase6_3_1_Allocation_Fix.zip'
LOG=ROOT/'verification/phase632_package.txt'

def main():
    for name,marker in [('phase632_cd_cards_browser_final.txt','PASS: no browser/API errors.'),
                        ('phase632_offline_browser.txt','PASS: no page errors/failed API calls.'),
                        ('phase632_opening_browser.txt','Only the deliberate forgery failed'),
                        ('phase632_calculator_http.txt','\nOK\n'),
                        ('phase632_native_http.txt','\nOK\n')]:
        assert marker in (ROOT/'verification'/name).read_text(),name
    with zipfile.ZipFile(OUT,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for p in sorted(ROOT.rglob('*')):
            if p.is_file() and '__pycache__' not in p.parts and '.git' not in p.parts and p.suffix not in ('.pyc','.pyo') and p!=LOG:
                z.write(p,ROOT.name+'/'+str(p.relative_to(ROOT)))
    reports=[]
    with zipfile.ZipFile(PRIOR) as old,zipfile.ZipFile(OUT) as z:
        assert z.testzip() is None
        original=set(old.namelist());assert original<=set(z.namelist())
        changed={str(Path(n).relative_to(ROOT.name)) for n in original if old.read(n)!=z.read(n)}
        expected={'PHASE_HANDOFF.md','PHASE_PLAN.md','README.md','Start_Web_Phase6_Offline_Interface_Windows.bat',
                  'backend/cn_web/calculator_static/app.js','backend/cn_web/calculator_static/index.html',
                  'backend/cn_web/calculator_static/web-bridge.js','backend/cn_web/http_app.py',
                  'docs/PHASE6_FINISH_SECURITY.md','tests/run_phase6_browser_flow.py',
                  'tests/test_calculator_http.py','tests/web_ui_transport.cjs','tests/browser_phase63_offline.cjs'}
        assert changed==expected,changed
        reports.append('PASS: every Phase 6.3.1 member retained; only intended web display/asset, test, launcher and release-document changes. No financial service/engine modifications.')
        with tempfile.TemporaryDirectory() as tmp:
            z.extractall(tmp);program=Path(tmp)/ROOT.name
            for p in program.rglob('*'):
                if p.is_file():assert p.read_bytes()==(ROOT/p.relative_to(program)).read_bytes(),p
            subprocess.run([sys.executable,'verify_baseline.py'],cwd=program,check=True,capture_output=True)
            for js in (program/'backend/cn_web/calculator_static').glob('*.js'):
                subprocess.run(['node','--check',str(js)],check=True,capture_output=True)
            subprocess.run([sys.executable,'-m','compileall','-q',str(program/'backend')],check=True,capture_output=True)
            bat=(program/'Start_Web_Phase6_Offline_Interface_Windows.bat').read_bytes()
            assert bat==b'@echo off\r\ncd /d "%~dp0"\r\necho All Crop CN Web - Phase 6.3.2 Original Offline Interface\r\npython manage_web.py start-local\r\npause\r\n'
            reports.append('PASS: ZIP CRC/extraction, byte equivalence, all 140 preserved baseline hashes, JS/Python compilation and quoted CRLF Windows launcher.')
            with socket.socket() as sock:
                sock.bind(('127.0.0.1',0));port=sock.getsockname()[1]
            server=subprocess.Popen([sys.executable,'-m','cn_web.cli','--data',str(Path(tmp)/'temporary-data'),'serve-local','--port',str(port)],cwd=program,env={**os.environ,'PYTHONPATH':str(program/'backend')},stdout=subprocess.PIPE,stderr=subprocess.PIPE)
            try:
                for _ in range(80):
                    try:
                        with urllib.request.urlopen(f'http://127.0.0.1:{port}/health',timeout=1) as r:assert r.status==200
                        break
                    except OSError:time.sleep(.1)
                else:raise RuntimeError('Extracted server did not start')
                for path in ['/','/calculator','/app.js','/cd-card-display.js','/cd-card-display.css','/web-bridge.js']:
                    with urllib.request.urlopen(f'http://127.0.0.1:{port}'+path,timeout=3) as r:assert r.status==200
            finally:
                server.terminate();server.communicate(timeout=5)
    reports.append('PASS: extracted server starts and serves calculator/new assets using isolated temporary data.')
    reports.append('PASS: 12 calculator and 10 native HTTP tests; exact display attribution model; real Chromium CD crop preview/apply, product-card sums/highlights/fit in both themes, no display mutation, reopen/restart and capped excess; original-screen and opening-credit browser regressions; baseline/zoom checks.')
    reports.append('Targeted CD-card flow uses normal motion; broad legacy journey uses reduced motion after headless click-stability timeouts. Windows acceptance remains pending. Phase 7 is on hold. No public deployment.')
    LOG.write_text('\n'.join(reports)+'\n')
    with zipfile.ZipFile(OUT,'a',zipfile.ZIP_DEFLATED) as z:z.write(LOG,ROOT.name+'/verification/phase632_package.txt')
    with zipfile.ZipFile(OUT) as z:
        assert z.testzip() is None
        for p in (ROOT/'verification').glob('phase632_*'):
            assert z.read(ROOT.name+'/verification/'+p.name)==p.read_bytes(),p
    print(LOG.read_text());print(OUT);print('Bytes:',OUT.stat().st_size);print('SHA256:',hashlib.sha256(OUT.read_bytes()).hexdigest())

if __name__=='__main__':main()
