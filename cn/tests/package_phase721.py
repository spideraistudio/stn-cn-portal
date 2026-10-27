from pathlib import Path
import zipfile,hashlib,tempfile,subprocess,sys,os,socket,time,urllib.request
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT.parents[1]/'CN_Web_Phase7_2_1_Audit_Mapping.zip'
for name,marker in [('audit_mapping_cumulative.txt','\nOK\n'),('audit_mapping_targeted.txt','\nOK\n'),('audit_mapping_browser.txt','No page errors'),('audit_mapping_billing_regression.txt','No page errors'),('audit_mapping_offline_browser.txt','PASS: no page errors/failed API calls.')]:
    assert marker in (ROOT/'verification'/name).read_text(),name

def pack():
    with zipfile.ZipFile(OUT,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for p in sorted(ROOT.rglob('*')):
            if p.is_file() and '__pycache__' not in p.parts and p.suffix not in ('.pyc','.pyo'):
                z.write(p,ROOT.name+'/'+str(p.relative_to(ROOT)))
pack()
with zipfile.ZipFile(OUT) as z,zipfile.ZipFile(ROOT.parents[1]/'CN_Web_Phase7_2_Billing_Audit.zip') as prior:
    assert z.testzip() is None
    assert set(prior.namelist())<=set(z.namelist())
    for n in prior.namelist():
        if '/offline_baseline/' in n:assert prior.read(n)==z.read(n),n
    with tempfile.TemporaryDirectory() as tmp:
        z.extractall(tmp);program=Path(tmp)/ROOT.name
        subprocess.run([sys.executable,'verify_baseline.py'],cwd=program,check=True)
        subprocess.run([sys.executable,'-m','compileall','-q',str(program/'backend')],check=True)
        for js in (program/'backend/cn_web').rglob('*.js'):subprocess.run(['node','--check',str(js)],check=True)
        with socket.socket() as sock:sock.bind(('127.0.0.1',0));port=sock.getsockname()[1]
        proc=subprocess.Popen([sys.executable,'-m','cn_web.cli','--data',str(Path(tmp)/'data'),'serve-local','--port',str(port)],cwd=program,env={**os.environ,'PYTHONPATH':str(program/'backend')},stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        try:
            for _ in range(80):
                try:
                    with urllib.request.urlopen(f'http://127.0.0.1:{port}/health',timeout=1) as r:assert r.status==200
                    break
                except OSError:time.sleep(.1)
            else:raise RuntimeError('Startup failed')
            for url in ['/calculator','/billing-audit.js','/audit-product-mapping.js','/web-bridge.js']:
                with urllib.request.urlopen(f'http://127.0.0.1:{port}'+url,timeout=3) as r:assert r.status==200
        finally:proc.terminate();proc.communicate(timeout=5)
        bat=(program/'Start_Web_Phase7_2_1_Windows.bat').read_bytes();assert b'cd /d "%~dp0"\r\n' in bat and b'python manage_web.py start-local\r\n' in bat
(ROOT/'verification/audit_mapping_package.txt').write_text('PASS: cumulative archive membership, unchanged offline baseline, ZIP CRC and extraction, all JS syntax, Python compilation, extracted-server startup and billing assets; Windows launcher CRLF. 104 cumulative tests and five targeted mapping/model checks passed. Three Linux Chromium runs passed: audit mapping, billing regression and original workflow. New Windows acceptance pending.\n')
pack()
with zipfile.ZipFile(OUT) as z:assert z.testzip() is None
print(OUT,OUT.stat().st_size,hashlib.sha256(OUT.read_bytes()).hexdigest())
