"""Operator-only commands; never exposed as HTTP APIs."""
import argparse
from getpass import getpass
from .production import make_portal


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('action', choices=['bootstrap-admin', 'cleanup'])
    args = parser.parse_args()
    app = make_portal()
    if args.action == 'bootstrap-admin':
        name = input('Platform administrator username: ').strip()
        password = getpass('New password (12–128 characters): ')
        if password != getpass('Repeat password: '):
            raise SystemExit('Passwords do not match')
        app.accounts.bootstrap(name, password, quota_bytes=1024**3)
        print('Administrator created. No default credentials exist.')
    else:
        from cn_web import storage_ops
        with app.accounts._tx() as db:
            storage_ops.cleanup(db, app.accounts)
        print('Temporary-file cleanup completed; saved sources/history are retained.')


if __name__ == '__main__':
    main()
