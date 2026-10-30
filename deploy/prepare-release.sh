#!/usr/bin/env bash
# Prepare only. Never change the current symlink or restart the live app here.
set -euo pipefail
umask 077
[[ $EUID -eq 0 ]] || { echo 'Run as root on the target VPS'; exit 1; }
release_sha=${1:?Pass the exact reviewed 40-character commit SHA}
[[ $release_sha =~ ^[0-9a-f]{40}$ ]] || { echo 'Full commit SHA required'; exit 1; }
source_repo=/srv/stn-cn/repository
release_dir=/srv/stn-cn/releases/$release_sha
[[ ! -e $release_dir ]] || { echo 'Release already exists; refusing overwrite'; exit 1; }
git -C "$source_repo" fetch origin fix/combined-portal-production
git -C "$source_repo" merge-base --is-ancestor "$release_sha" origin/fix/combined-portal-production
install -d -m 0755 -o stnnode -g stnnode "$release_dir"
git -C "$source_repo" archive "$release_sha" | tar -x -C "$release_dir"
chown -R stnnode:stnnode "$release_dir"
cd "$release_dir"
runuser -u stnnode -- npm ci --include=dev
runuser -u stnnode -- python3 -m venv .venv
runuser -u stnnode -- .venv/bin/pip install -r deploy/requirements.txt
# Build needs combined-mode public flag, never production database credentials.
runuser -u stnnode -- env NODE_ENV=production NEXT_PUBLIC_COMMON_PORTAL=1 NEXT_TELEMETRY_DISABLED=1 npm run build
printf '%s\n' "$release_sha" > RELEASE_COMMIT
install -d -m 0700 -o stnnode -g stnnode /var/cache/stn-cn/next
rm -rf .next/cache
ln -s /var/cache/stn-cn/next .next/cache
chown -R root:root "$release_dir"
chmod -R a+rX "$release_dir"
echo "Prepared $release_sha. No service or live symlink was changed."
