"""Real Caddy TLS + Gunicorn + Next + authenticated disposable Mongo smoke.

Requires the production Next build and STAGE2_MONGO_URI pointing ONLY to an
authenticated loopback integration_ database. The caller owns that disposable
Mongo instance. No VPS, real certificates, live data or system services touched.
"""
import http.client
from http.cookies import SimpleCookie
import json
import os
from pathlib import Path
import secrets
import signal
import socket
import ssl
import subprocess
import sys
import tempfile
import time
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from deploy.production import make_portal
from cn_web.security import PERMISSIONS

HOST = 'portal.example.test'
PASSWORD = 'Synthetic production smoke password 2026!'


def free_port():
    with socket.socket() as sock:
        sock.bind(('127.0.0.1', 0))
        return sock.getsockname()[1]


class Client:
    def __init__(self, port, context):
        self.port, self.context = port, context
        self.cookie, self.csrf = '', ''

    def request(self, path, data=None, method=None, headers=None):
        method = method or ('POST' if data is not None else 'GET')
        conn = http.client.HTTPSConnection(HOST, self.port, context=self.context, timeout=40)
        # Test-only DNS mapping preserves real SNI and certificate validation.
        conn._create_connection = lambda address, timeout, source_address=None: socket.create_connection(
            ('127.0.0.1', address[1]), timeout, source_address)
        values = {'Cookie': self.cookie}
        if method not in {'GET', 'HEAD'}:
            values.update({'Origin': f'https://{HOST}:{self.port}', 'Content-Type': 'application/json',
                           'X-CSRF-Token': self.csrf})
        values.update(headers or {})
        try:
            conn.request(method, path, None if data is None else json.dumps(data), values)
            result = conn.getresponse()
            raw = result.read()
            response_headers = dict(result.getheaders())
            cookie = result.getheader('Set-Cookie')
            if cookie:
                parsed = SimpleCookie(cookie)
                if '__Host-cn_session' in parsed:
                    self.cookie = '__Host-cn_session=' + parsed['__Host-cn_session'].value
            try:
                body = json.loads(raw)
            except ValueError:
                body = raw.decode(errors='replace')
            return result.status, body, response_headers
        finally:
            conn.close()

    def login(self, name, password):
        result = self.request('/api/auth/login', {'username': name, 'password': password})
        assert result[0] == 200, (result[0], result[1])
        assert 'Secure' in result[2]['Set-Cookie'] and 'HttpOnly' in result[2]['Set-Cookie']
        result = self.request('/api/me')
        assert result[0] == 200
        self.csrf = result[1]['csrf_token']
        return result[1]


def main():
    uri = os.environ['STAGE2_MONGO_URI']
    parsed = urlsplit(uri)
    if parsed.hostname != '127.0.0.1' or not parsed.username or not parsed.password or not parsed.path.startswith('/integration_'):
        raise SystemExit('An authenticated disposable loopback integration_ database is required')
    caddy = os.environ['STAGE2_CADDY']
    for port in (3000, 8787, 8788):
        with socket.socket() as sock:
            sock.bind(('127.0.0.1', port))  # Refuse to interfere with existing apps.
    with tempfile.TemporaryDirectory(prefix='stage2-production-') as temporary:
        temp = Path(temporary)
        tls_port = free_port()
        origin = f'https://{HOST}:{tls_port}'
        env = {**os.environ, 'PORTAL_ORIGIN': origin, 'CN_WEB_DATA': str(temp / 'cn'),
               'PORTAL_BRIDGE_KEY': secrets.token_urlsafe(48), 'IDENTIFIER_LOOKUP_KEY': secrets.token_urlsafe(48),
               'PORTAL_MODE': 'combined', 'NEXT_PUBLIC_COMMON_PORTAL': '1', 'NODE_ENV': 'production',
               'NODE_USE_ENV_PROXY': '0',
               'PORTAL_COOKIE_NAME': '__Host-cn_session', 'MONGODB_URI': uri, 'STN_MONGO_TLS': '0',
               'PORTAL_IDENTITY_URL': 'http://127.0.0.1:8788/internal/portal/introspect',
               'ADMIN_EMAILS': 'synthetic-platform@example.test', 'NEXT_TELEMETRY_DISABLED': '1',
               'PYTHONPATH': os.environ.get('STAGE2_PYTHONPATH', '') + os.pathsep + str(ROOT),
               'XDG_DATA_HOME': str(temp / 'caddy-data'), 'XDG_CONFIG_HOME': str(temp / 'caddy-config')}
        original = dict(os.environ)
        os.environ.update(env)
        try:
            app = make_portal()
            app.accounts.bootstrap('platform', PASSWORD, quota_bytes=1024**3)
        finally:
            os.environ.clear()
            os.environ.update(original)
        config = (ROOT / 'deploy/Caddyfile.example').read_text()
        config = config.replace('app-staging.example.com {', f'https://{HOST}:{tls_port} {{\n    bind 127.0.0.1\n    tls internal')
        config = '{\n    admin off\n    auto_https disable_redirects\n    skip_install_trust\n}\n' + config
        (temp / 'Caddyfile').write_text(config)
        # Node's test-only DNS mapping allows its approval callback through the
        # same TLS origin; it does not replace certificate verification.
        resolver = temp / 'resolver.cjs'
        resolver.write_text("const dns=require('node:dns');const lookup=dns.lookup;dns.lookup=function(host,opts,cb){if(host!=='portal.example.test')return lookup.apply(this,arguments);if(typeof opts==='function'){cb=opts;opts={}};process.nextTick(()=>opts&&opts.all?cb(null,[{address:'127.0.0.1',family:4}]):cb(null,'127.0.0.1',4))};")
        processes, logs = [], []
        def start(command, name, extra=None):
            log = open(temp / (name + '.log'), 'w')
            logs.append(log)
            process = subprocess.Popen(command, cwd=ROOT, env={**env, **(extra or {})},
                                       stdout=log, stderr=subprocess.STDOUT, start_new_session=True)
            processes.append(process)
            return process
        def gunicorn(role):
            return start([sys.executable, '-m', 'gunicorn', '--config', 'deploy/gunicorn.conf.py',
                          f'deploy.production:create_{role}()'], role,
                         {'PORTAL_PROCESS': role, 'GUNICORN_CMD_ARGS': '--graceful-timeout=5'})
        try:
            start([caddy, 'run', '--config', str(temp / 'Caddyfile'), '--adapter', 'caddyfile'], 'caddy')
            ca = temp / 'caddy-data/caddy/pki/authorities/local/root.crt'
            for attempt in range(40):
                if ca.exists():
                    break
                time.sleep(.25)
            context = ssl.create_default_context(cafile=str(ca))
            node_extra = {'NODE_EXTRA_CA_CERTS': str(ca), 'NODE_OPTIONS': '--require=' + str(resolver)}
            def node():
                return start(['node', 'node_modules/next/dist/bin/next', 'start', '--hostname', '127.0.0.1', '--port', '3000'], 'node', node_extra)
            identity = gunicorn('identity')
            frontend = node()
            gateway = gunicorn('gateway')
            admin = Client(tls_port, context)
            def wait_ready():
                for attempt in range(80):
                    try:
                        if admin.request('/ready')[0] == 200:
                            return
                    except OSError:
                        pass
                    time.sleep(.5)
                raise RuntimeError('Production readiness timed out')
            wait_ready()
            # Verify Node's server-side callback DNS and CA trust independently
            # before exercising the unified approval callback.
            probe = "try{const r=await fetch(process.env.PORTAL_ORIGIN+'/health');if(r.status!==200)throw Error('Unexpected status '+r.status)}catch(e){console.error('Node TLS callback:',e.message,e.cause?.code,e.cause?.message);process.exitCode=1}"
            subprocess.run(['node', '-e', probe], cwd=ROOT, env={**env, **node_extra}, check=True)
            for path in ('/portal', '/stn', '/about', '/join'):
                assert admin.request(path)[0] == 200, path
            for path in ('/internal/portal/introspect', '/internal/portal/health', '/api/production-health'):
                assert admin.request(path)[0] == 404, path
            print('PASS real Caddy TLS validation, Gunicorn listeners, Next pages, authenticated Mongo readiness and private-route denial.', flush=True)
            admin.login('platform', PASSWORD)
            signup = {'companyName': 'Synthetic Production Company', 'gstin': '24PQRST6789L1Z5',
                      'responsiblePersonName': 'Synthetic Contact', 'mobileNumber': '9876543210',
                      'email': 'production@example.test', 'taluka': 'Synthetic Taluka',
                      'address': 'Synthetic registered address', 'state': 'Gujarat', 'district': 'Ahmadabad',
                      'pincode': '380001', 'category': 'agriculture'}
            public = Client(tls_port, context)
            result = public.request('/api/register', signup)
            assert result[0] == 200, result
            duplicate = public.request('/api/register', signup)
            assert duplicate[0] == 409, duplicate
            # Read synthetic pending ID via the dedicated disposable app DB.
            code = "import {MongoClient} from 'mongodb';const c=await MongoClient.connect(process.env.MONGODB_URI);const m=await c.db().collection('members').findOne({gstin:'24PQRST6789L1Z5'});console.log(JSON.stringify({id:String(m._id),status:m.status}));await c.close();"
            result = subprocess.run(['node', '--input-type=module', '-e', code], cwd=ROOT, env=env,
                                    text=True, stdout=subprocess.PIPE, check=True)
            member = json.loads(result.stdout)
            assert member['status'] == 'pending'
            approve = {'member_id': member['id'], 'username': 'production-company-admin',
                       'temporary_password': PASSWORD, 'permissions': sorted(PERMISSIONS),
                       'cn': True, 'stn': True, 'max_users': 5, 'quota_bytes': 1024**3,
                       'user_quota_bytes': 250 * 1024**2}
            result = admin.request('/api/portal-stn/approve', approve)
            assert result[0] == 200, result
            user = Client(tls_port, context)
            identity = user.login(approve['username'], PASSWORD)
            assert identity['user']['must_change_password']
            result = user.request('/api/auth/password', {'current_password': PASSWORD, 'new_password': PASSWORD + ' changed'})
            assert result[0] == 200, result
            user.login(approve['username'], PASSWORD + ' changed')
            state = user.request('/api/portal/state')
            assert state[0] == 200 and state[1]['user']['modules'] == {'cn': True, 'stn': True}, state
            assert user.request('/api/member/seed-browse')[0] == 200
            assert user.request('/api/workspace')[0] == 200
            print('PASS HTTPS registration, duplicate rejection, real unified approval callback, secure login, forced password change and permitted STN/CN access.', flush=True)
            # Caddy must discard forged client/proxy credentials.
            assert user.request('/api/me', headers={'X-Forwarded-For': 'spoofed', 'X-Forwarded-Proto': 'http',
                                                   'CF-Connecting-IP': 'spoofed', 'X-Portal-Key': 'spoofed'})[0] == 200
            frontend.terminate()
            frontend.wait(timeout=20)
            assert admin.request('/ready')[0] == 503
            frontend = node()
            wait_ready()
            gateway.terminate()
            gateway.wait(timeout=25)
            gateway = gunicorn('gateway')
            wait_ready()
            assert user.request('/api/workspace')[0] == 200
            assert user.request('/api/auth/logout', {})[0] == 200
            assert user.request('/api/me')[0] == 401
            print('PASS edge-header replacement, dependency outage/recovery, gateway restart with saved account/session and shared sign-out.', flush=True)
        except BaseException:
            # Test logs contain synthetic data only; never run against real data.
            for name in ('caddy', 'gateway', 'identity', 'node'):
                path = temp / (name + '.log')
                if path.exists():
                    print(name + ' log tail:\n' + '\n'.join(path.read_text(errors='replace').splitlines()[-14:]))
            raise
        finally:
            for process in reversed(processes):
                if process.poll() is None:
                    os.killpg(process.pid, signal.SIGTERM)
                    try:
                        process.wait(timeout=25)
                    except subprocess.TimeoutExpired:
                        os.killpg(process.pid, signal.SIGKILL)
                        process.wait()
            for log in logs:
                log.close()


if __name__ == '__main__':
    main()
