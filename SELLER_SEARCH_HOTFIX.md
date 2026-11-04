# Approved seller visibility fix — 4 November 2026

Normal registration now persists is_pilot=0 explicitly. Seller search, identity lookup and established seller lookup treat a missing/null pilot flag as zero, consistent with the member projection. Explicit pilot=1 records remain isolated; category, approval status, GST matching and search permissions still apply. No automatic database migration or changes to existing reports are included.

Verification: 20 focused tests passed, using disposable MongoDB 8.0.17 and the real SQL adapter, registration persistence and search/identity route code. Authentication context and notification side effects are stubbed; this is not hosted browser acceptance. Tests cover new, missing-flag and null-flag accounts, pilot separation, pending report/category exclusion and blocked search permissions. Production Next build and TypeScript passed. The new checks are included in release CI.

Release preparation accepts STN_BUILD_PYTHON to select the existing service-accessible Python interpreter instead of the server's default Python. On this VPS use /opt/stn-cn/python/cpython-3.12.16-linux-x86_64-gnu/bin/python3.12; do not use the /root shortcut.

Deployment remains an operator action: prepare a new full-commit release with its own venv/build, preserve /etc/stn-cn/app.env and /var/lib/stn-cn data, then activate through deploy.activate_release. Existing issued CN history and financial calculations are outside this fix. The earlier database repair only normalized missing account flags; this code fix protects future registrations and historical missing/null flags.
