import os,sys,json,tempfile,subprocess,time,urllib.request
from pathlib import Path
root=Path(__file__).resolve().parents[1];sys.path.insert(0,str(root))
from store import Store
from workbooks import Workbooks
backup=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else None
if backup is None:raise SystemExit('Usage: python tests/run_backup_navigation.py PATH_TO_BACKUP.json')
with tempfile.TemporaryDirectory() as tmp:
 st=Store(Path(tmp)/'calculator.sqlite3');books=Workbooks(st);books.restore(json.loads(backup.read_text()),True)
 before=books.backup();proc=subprocess.Popen([sys.executable,str(root/'app.py'),'--no-browser'],env=dict(os.environ,CN_DATA_PATH=st.path,CN_PORT='18766'),stdout=subprocess.DEVNULL)
 try:
  for _ in range(100):
   try:urllib.request.urlopen('http://127.0.0.1:18766/api/health',timeout=1);break
   except Exception:time.sleep(.05)
  state=json.load(urllib.request.urlopen('http://127.0.0.1:18766/api/state'));payload=json.dumps({'backup':json.loads(backup.read_text())}).encode();request=urllib.request.Request('http://127.0.0.1:18766/api/restore',data=payload,headers={'Content-Type':'application/json','X-CN-Token':state['token']});preview=json.load(urllib.request.urlopen(request,timeout=60));assert preview['records']==sum(len(w['backup']['records']) for w in before['workbooks'])+len(before['legacy']['records']);print('Actual 34.8 MiB backup HTTP restore preview accepted:',preview['records'],'records; no restore confirmation sent.')
  subprocess.run(['node',str(root/'tests/party_navigation_backup.cjs')],env=dict(os.environ,CN_ACCEPTANCE_BACKUP=str(backup)),check=True)
  # Navigation may save drafts. All original imported monetary/physical entries must remain exact.
  after=Workbooks(Store(st.path)).backup();count=0
  for old_book in before['workbooks']:
   new_book=next(b for b in after['workbooks'] if b['metadata']['id']==old_book['metadata']['id']);now={r['id']:json.loads(r['data']) for r in new_book['backup']['records']}
   for row in old_book['backup']['records']:
    old=json.loads(row['data']);new=now[row['id']]
    assert old.get('entries')==new.get('entries')
    assert old.get('allocations')==new.get('allocations')
    assert old.get('opening')==new.get('opening') and old.get('closing')==new.get('closing')
    count+=1
  print('Preserved imported entries/allocations/opening/closing in',count,'workbook records from actual backup.')
 finally:proc.terminate();proc.wait()
