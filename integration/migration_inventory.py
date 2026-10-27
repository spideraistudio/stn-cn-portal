"""Read-only inventory of an explicitly supplied stopped CN data copy."""
import argparse,json,sqlite3
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--cn-copy',type=Path,required=True);args=p.parse_args()
path=(args.cn_copy/'accounts.sqlite3').resolve()
with sqlite3.connect(path.as_uri()+'?mode=ro',uri=True) as db:
    db.row_factory=sqlite3.Row
    rows=db.execute('SELECT u.id,u.username,r.role,r.parent_admin,w.quota_bytes,w.enabled FROM users u JOIN workspaces w ON w.user_id=u.id JOIN account_roles r ON r.user_id=u.id ORDER BY u.username').fetchall()
    print(json.dumps({'source_copy':str(path),'accounts':[dict(r) for r in rows],'migration':'No changes. Assign companies and exact STN member IDs explicitly in the portal; never match by name, GST or email.'},indent=2))
