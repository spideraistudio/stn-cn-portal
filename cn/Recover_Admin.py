"""PC operator recovery only. Copy beside manage_web.py; never mounted over HTTP."""
import argparse
from contextlib import closing
from datetime import datetime
from getpass import getpass
import json
import os
from pathlib import Path
import sqlite3
import sys
import time
import uuid

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / 'backend'))


def connect_existing(path):
    if not path.is_file():
        raise ValueError('No existing web accounts found at '+str(path)+'. If you use a custom data folder, run Recover_Admin_Windows.bat --data "YOUR WEB DATA FOLDER".')
    return sqlite3.connect(path.resolve().as_uri()+'?mode=rw', uri=True, timeout=15)


def admins(path):
    with closing(connect_existing(path)) as db:
        return db.execute("SELECT username FROM users WHERE is_admin=1 AND id IN (SELECT user_id FROM account_roles WHERE role='superadmin') ORDER BY username").fetchall()


def recover(path, username, password):
    from cn_web.security import hash_password
    hashed = hash_password(password)
    with closing(connect_existing(path)) as db:
        db.execute('BEGIN IMMEDIATE')
        try:
            user = db.execute("SELECT id,username FROM users WHERE username=? AND is_admin=1 AND id IN (SELECT user_id FROM account_roles WHERE role='superadmin')", (username,)).fetchone()
            if not user:
                raise ValueError('Choose the existing superadmin. No account was changed.')
            backups = path.parent / 'recovery_backups'
            backups.mkdir(exist_ok=True)
            if os.name == 'posix':
                backups.chmod(0o700)
            backup = backups / ('before-admin-reset-'+datetime.now().strftime('%Y%m%d-%H%M%S')+'-'+uuid.uuid4().hex[:8]+'.sqlite3')
            # Read from a second connection while this transaction prevents writers.
            # sqlite backup includes all saved web tables in one consistent snapshot.
            with closing(sqlite3.connect(path.resolve().as_uri()+'?mode=ro', uri=True)) as source:
                with closing(sqlite3.connect(backup)) as target:
                    source.backup(target)
                    if target.execute('PRAGMA integrity_check').fetchone()[0] != 'ok':
                        raise ValueError('Backup verification failed. No password was changed.')
            if os.name == 'posix':
                backup.chmod(0o600)
            db.execute('UPDATE users SET password_hash=?,must_change=0 WHERE id=?', (hashed,user[0]))
            db.execute('DELETE FROM sessions WHERE user_id=?', (user[0],))
            db.execute('DELETE FROM login_attempts WHERE username=?', (user[1],))
            db.execute('INSERT INTO auth_audit(at,actor,action,target,details) VALUES(?,NULL,?,?,?)',
                       (time.time(),'local_admin_password_recovered',user[0],json.dumps({'method':'local_pc_operator'})))
            db.commit()
            return backup
        except Exception:
            db.rollback()
            raise


def main():
    parser=argparse.ArgumentParser(description='Recover an existing All Crop CN WEB administrator on this PC')
    parser.add_argument('--data',type=Path)
    args=parser.parse_args()
    base=Path(os.environ.get('LOCALAPPDATA',str(Path.home()/'.local'/'share')))
    path=(args.data or base/'AllCropCNWeb')/'accounts.sqlite3'
    if not (ROOT/'backend'/'cn_web'/'security.py').is_file():
        raise ValueError('Extract these recovery files into your calculator program folder, beside manage_web.py, then run again.')
    print('All Crop CN - local superadmin recovery')
    print('Stop the calculator server before continuing.\nWeb data: '+str(path))
    from cn_web.accounts import Accounts
    Accounts(path.parent)
    rows=admins(path)
    if not rows:
        raise ValueError('No administrator exists in this data folder. No new account was created.')
    print('\nExisting superadmin login ID:')
    for i,row in enumerate(rows,1):
        print(str(i)+'. '+row[0])
    choice=input('\nChoose number [1]: ').strip() or '1'
    if not choice.isdigit() or not 1<=int(choice)<=len(rows):
        raise ValueError('Invalid selection. No account was changed.')
    username=rows[int(choice)-1][0]
    print('\nSet a NEW password, 12-128 characters. Typed characters are hidden.')
    password=getpass('New password: ')
    if password!=getpass('Confirm new password: '):
        raise ValueError('Passwords do not match. No account was changed.')
    backup=recover(path,username,password)
    print('\nPassword reset successfully. Login ID: '+username)
    print('Start the calculator normally and sign in using your new password.')
    print('Workbooks, users and permissions are retained. Old admin sessions are signed out.')
    print('Automatic database backup: '+str(backup))


if __name__=='__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('\nCancelled.')
        sys.exit(1)
    except Exception as exc:
        print('\nRecovery stopped: '+str(exc))
        sys.exit(1)
