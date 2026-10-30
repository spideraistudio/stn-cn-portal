"""Explicit initial/staging activation; never called by prepare-release.sh.

Requires owner approval before any live activation. Database migrations and
data copying are deliberately absent. Code rollback cannot undo data changes.
"""
import argparse
import fcntl
import os
from pathlib import Path
import re
import subprocess
import time
import urllib.request
from urllib.parse import urlsplit
from .backup import pause_services

SERVICES = ['stn-cn-python@identity.service', 'stn-cn-node.service', 'stn-cn-python@gateway.service']


def ready(origin):
    # Real certificate and hostname validation, never --insecure.
    with urllib.request.urlopen(origin + '/ready', timeout=15) as result:
        return result.status == 200


def activate(release, origin, *, base=Path('/srv/stn-cn')):
    release = Path(release)
    if (not re.fullmatch(r'[0-9a-f]{40}', release.name)
            or release.parent != base / 'releases' or release.is_symlink()
            or not (release / 'RELEASE_COMMIT').is_file()
            or (release / 'RELEASE_COMMIT').read_text().strip() != release.name):
        raise ValueError('Use an immutable prepared release with matching commit')
    current = base / 'current'
    if current.exists() and not current.is_symlink():
        raise ValueError('Current path must be a release symlink')
    previous = current.resolve() if current.is_symlink() else None

    def point(target):
        temporary = current.with_name('.next-release')
        if temporary.exists() or temporary.is_symlink():
            raise ValueError('Another release operation needs review')
        temporary.symlink_to(target)
        os.replace(temporary, current)

    with pause_services():
        # Pause cleanup as well as app workers; prevent mixed-release writes.
        try:
            point(release)
            for service in SERVICES:
                subprocess.run(['systemctl', 'start', service], check=True)
            for attempt in range(12):
                try:
                    if ready(origin):
                        print('Activated commit ' + release.name + '; HTTPS readiness passed.')
                        return
                except (OSError, ValueError):
                    pass
                time.sleep(5)
            raise RuntimeError('HTTPS readiness failed')
        except BaseException:
            for service in reversed(SERVICES):
                subprocess.run(['systemctl', 'stop', service], check=False)
            if previous:
                point(previous)
                for service in SERVICES:
                    subprocess.run(['systemctl', 'start', service], check=False)
                print('Previous code release restored; verify its readiness and data before use.')
            else:
                print('Initial activation failed; services are stopped for investigation.')
            raise


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('commit')
    parser.add_argument('--origin', required=True)
    parser.add_argument('--approved-activation', action='store_true', required=True)
    args = parser.parse_args()
    if os.geteuid() != 0:
        raise SystemExit('Run as root on the target VPS')
    if urlsplit(args.origin).scheme != 'https':
        raise SystemExit('An approved HTTPS origin is required')
    with open('/run/lock/stn-cn-operation.lock', 'w') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        activate('/srv/stn-cn/releases/' + args.commit, args.origin)


if __name__ == '__main__':
    main()
