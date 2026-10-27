"""Operator setup and local account-console preview. No financial server changes."""
import argparse
import time
import sys
from getpass import getpass
from wsgiref.simple_server import make_server, WSGIRequestHandler

from .accounts import Accounts
from .http_app import AccountApp
from . import storage_ops


class QuietHandler(WSGIRequestHandler):
    def log_message(self, *_):
        pass


def maintain_temporary(accounts):
    try:
        with accounts._tx() as db:
            storage_ops.cleanup(db, accounts)
        return True
    except Exception:
        # The transaction rolls back; maintenance must not take down the app.
        print("Temporary cleanup deferred after an error; saved work is retained. Retrying shortly.", file=sys.stderr, flush=True)
        return False


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", required=True, help="New WEB data directory; do not use offline data")
    sub = parser.add_subparsers(dest="command", required=True)
    setup = sub.add_parser("bootstrap-admin")
    setup.add_argument("--username", required=True)
    setup.add_argument("--quota-mib", required=True, type=int)
    dev = sub.add_parser("serve-local")
    dev.add_argument("--port", type=int, default=8787)
    args = parser.parse_args()
    accounts = Accounts(args.data)
    if args.command == "bootstrap-admin":
        password = getpass("Administrator password (12–128 characters): ")
        if password != getpass("Confirm password: "):
            parser.error("Passwords do not match")
        try:
            accounts.bootstrap(args.username, password, quota_bytes=args.quota_mib * 1024 * 1024)
        except Exception as exc:
            parser.error(str(exc))
        print("Administrator created. No password was saved in a setup file.")
    else:
        origin = f"http://127.0.0.1:{args.port}"
        app = AccountApp(accounts, origin=origin, development=True)
        cleanup_ok = maintain_temporary(accounts)
        print("Local Phase 7.1 CN workspace: " + origin, flush=True)
        with make_server("127.0.0.1", args.port, app, handler_class=QuietHandler) as server:
            server.timeout = 30
            next_cleanup = time.monotonic() + (86400 if cleanup_ok else 60)
            while True:
                server.handle_request()
                if time.monotonic() >= next_cleanup:
                    cleanup_ok = maintain_temporary(accounts)
                    next_cleanup = time.monotonic() + (86400 if cleanup_ok else 60)


if __name__ == "__main__":
    main()
