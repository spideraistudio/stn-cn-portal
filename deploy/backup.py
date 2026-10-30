"""Coherent off-server encrypted backups with a short write pause.

No deletion/pruning or live restore. Keep app services stopped until Mongo,
SQLite, files and secrets are captured together, then resume their prior state.
"""
from contextlib import contextmanager
from datetime import datetime, timezone
import fcntl
import json
import os
from pathlib import Path
import shutil
import signal
import subprocess
import tarfile
import tempfile

SERVICES = ['stn-cn-maintenance.timer', 'stn-cn-maintenance.service',
            'stn-cn-python@gateway.service', 'stn-cn-node.service',
            'stn-cn-python@identity.service']


def run(command, **kwargs):
    return subprocess.run(command, check=True, **kwargs)


@contextmanager
def pause_services():
    active = [name for name in SERVICES if subprocess.run(
        ['systemctl', 'is-active', '--quiet', name], check=False).returncode == 0]
    stopped = []
    try:
        for name in SERVICES:
            # Record before stopping so a timed-out/partially stopped unit is
            # also restored by the finally block.
            stopped.append(name)
            run(['systemctl', 'stop', name])
        yield
    finally:
        failures = []
        for name in reversed(stopped):
            if name not in active:
                continue
            if name == 'stn-cn-maintenance.service':
                continue  # One-shot cleanup must not be executed a second time.
            if subprocess.run(['systemctl', 'start', name], check=False).returncode:
                failures.append(name)
        if failures:
            raise RuntimeError('Service restart failed: ' + ', '.join(failures))


def main():
    if os.geteuid() != 0:
        raise SystemExit('Backup requires root on the target VPS')
    for name in ('RESTIC_REPOSITORY', 'RESTIC_PASSWORD_FILE', 'MONGO_DUMP_CONFIG'):
        if not os.environ.get(name):
            raise SystemExit('Configure backup setting: ' + name)
    if not os.environ['RESTIC_REPOSITORY'].startswith(('s3:', 'sftp:', 'rest:', 'azure:', 'gs:', 'b2:')):
        raise SystemExit('Use an off-server restic repository')
    for key in ('RESTIC_PASSWORD_FILE', 'MONGO_DUMP_CONFIG'):
        path = Path(os.environ[key])
        if not path.is_file() or path.stat().st_mode & 0o077:
            raise SystemExit(key + ' must be a private 0600/0400 file')
    root = Path('/var/backups/stn-cn')
    root.mkdir(mode=0o700, parents=True, exist_ok=True)
    os.umask(0o077)
    # Shared with activation to prevent concurrent backup/deploy snapshots.
    with open('/run/lock/stn-cn-operation.lock', 'w') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        run(['restic', 'snapshots', '--json'], stdout=subprocess.DEVNULL)
        with tempfile.TemporaryDirectory(prefix='snapshot-', dir=root) as temporary:
            snapshot = Path(temporary)
            with pause_services():
                run(['mongodump', '--config', os.environ['MONGO_DUMP_CONFIG'],
                     '--archive=' + str(snapshot / 'mongo.archive.gz'), '--gzip'],
                    stdout=subprocess.DEVNULL)
                with tarfile.open(snapshot / 'private-state.tar.gz', 'w:gz') as archive:
                    archive.add('/var/lib/stn-cn/cn', arcname='cn')
                    archive.add('/etc/stn-cn', arcname='settings')
                release = Path('/srv/stn-cn/current/RELEASE_COMMIT').read_text().strip()
                metadata = {'commit': release,
                            'captured_at': datetime.now(timezone.utc).isoformat(),
                            'consistent_write_pause': True}
                (snapshot / 'snapshot.json').write_text(json.dumps(metadata))
            # Resume availability before the remote upload; snapshot bytes are
            # immutable and restic encrypts them before transfer.
            run(['restic', 'backup', str(snapshot), '--tag', 'stn-cn', '--tag', release])
            run(['restic', 'check'], stdout=subprocess.DEVNULL)
            (root / 'last-success.json').write_text(json.dumps(metadata))
            print('Encrypted backup and repository check completed; no snapshots were pruned.')


if __name__ == '__main__':
    def interrupt(signum, frame):
        raise KeyboardInterrupt
    signal.signal(signal.SIGTERM, interrupt)
    signal.signal(signal.SIGINT, interrupt)
    main()
