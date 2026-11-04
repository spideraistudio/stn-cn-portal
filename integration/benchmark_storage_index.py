"""Synthetic in-memory quota hot-path benchmark. No user data is read/changed."""
import sys,sqlite3,time,json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'cn/backend'))
from cn_web.storage_ops import usage
con=sqlite3.connect(':memory:')
con.execute('CREATE TABLE workspace_documents(owner TEXT,id TEXT,payload TEXT,PRIMARY KEY(owner,id))')
blob='x'*(16*1024*1024)
for i in range(10):con.execute('INSERT INTO workspace_documents VALUES(?,?,?)',('synthetic',str(i),blob))
def scan():return dict(con.execute('SELECT owner,SUM(length(CAST(payload AS BLOB))) FROM workspace_documents GROUP BY owner'))
start=time.perf_counter();assert usage(con)==scan();bootstrap=time.perf_counter()-start
results={}
for name,fn in [('previous_full_payload_scan',scan),('maintained_byte_index',lambda:usage(con))]:
 begin=time.perf_counter()
 for _ in range(10):assert fn()=={'synthetic':160*1024*1024}
 results[name+'_mean_ms']=(time.perf_counter()-begin)*100
print(json.dumps({'synthetic_payload_mib':160,'repetitions':10,'bootstrap_and_comparison_ms':bootstrap*1000,**results,'scope':'quota byte-count operation only; not whole-app or Windows response time'},indent=2))
