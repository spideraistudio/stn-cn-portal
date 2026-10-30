"""Production trust, secure sessions, private bridge and operator safeguards."""
import copy
import io
import json
from pathlib import Path
import secrets
import tempfile
import unittest
from unittest.mock import patch, Mock

from deploy.configure import create_config
from deploy.production import (PrivateIdentity, ProductionEdge, make_portal,
                               settings, ROOT)
from deploy.backup import pause_services
from deploy.activate_release import activate

PASSWORD = 'Synthetic production regression password 2026!'
ORIGIN = 'https://portal.example.test'


def environ(path='/', method='GET', body=None, **overrides):
    raw = json.dumps(body).encode() if body is not None else b''
    value = {'PATH_INFO': path, 'REQUEST_METHOD': method, 'QUERY_STRING': '',
             'HTTP_HOST': 'portal.example.test', 'REMOTE_ADDR': '127.0.0.1',
             'HTTP_X_FORWARDED_HOST': 'portal.example.test',
             'HTTP_X_FORWARDED_PROTO': 'https', 'HTTP_X_FORWARDED_FOR': '198.51.100.24',
             'wsgi.url_scheme': 'https', 'wsgi.input': io.BytesIO(raw),
             'CONTENT_LENGTH': str(len(raw)), 'CONTENT_TYPE': 'application/json'}
    value.update(overrides)
    return value


def request(app, env):
    captured = {}
    def start(status, headers):
        captured.update(status=int(status.split()[0]), headers=dict(headers))
    captured['body'] = b''.join(app(env, start))
    return captured


class ProductionTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.env = {'PORTAL_ORIGIN': ORIGIN,
                    'CN_WEB_DATA': str(Path(self.temporary.name) / 'private'),
                    'PORTAL_BRIDGE_KEY': secrets.token_urlsafe(48),
                    'IDENTIFIER_LOOKUP_KEY': secrets.token_urlsafe(48)}
        self.environment = patch.dict('os.environ', self.env)
        self.environment.start()
        self.addCleanup(self.environment.stop)
        self.app = make_portal()
        self.edge = ProductionEdge(self.app)
        self.internal = PrivateIdentity(self.app)

    def test_secure_cookie_and_real_login(self):
        self.app.accounts.bootstrap('platform', PASSWORD, quota_bytes=1024**3)
        result = request(self.edge, environ('/api/auth/login', 'POST',
                         {'username': 'platform', 'password': PASSWORD}, HTTP_ORIGIN=ORIGIN))
        self.assertEqual(result['status'], 200, result)
        cookie = result['headers']['Set-Cookie']
        for part in ['__Host-cn_session=', 'Secure', 'HttpOnly', 'SameSite=Strict', 'Path=/']:
            self.assertIn(part, cookie)
        self.assertNotIn('Domain=', cookie)
        me = request(self.edge, environ('/api/me', HTTP_COOKIE=cookie.split(';')[0]))
        self.assertEqual(me['status'], 200)
        self.assertEqual(json.loads(me['body'])['user']['username'], 'platform')
        failed = request(self.edge, environ('/api/auth/login', 'POST',
                         {'username': 'platform', 'password': PASSWORD + ' wrong'}, HTTP_ORIGIN=ORIGIN))
        self.assertEqual(failed['status'], 401)
        with self.app.accounts._tx() as db:
            self.assertEqual(db.execute('SELECT ip FROM login_attempts LIMIT 1').fetchone()['ip'], '198.51.100.24')

    def test_proxy_cannot_be_forged_by_remote_client(self):
        self.assertEqual(request(self.edge, environ(REMOTE_ADDR='198.51.100.24'))['status'], 400)

    def test_wrong_host_proto_or_untrusted_chain_rejected(self):
        for override in [{'HTTP_HOST': 'wrong.test'}, {'HTTP_X_FORWARDED_HOST': 'wrong.test'},
                         {'HTTP_X_FORWARDED_PROTO': 'http'}, {'wsgi.url_scheme': 'http'},
                         {'HTTP_X_FORWARDED_FOR': '198.51.100.1, 127.0.0.1'},
                         {'HTTP_X_FORWARDED_FOR': 'invalid'}]:
            self.assertEqual(request(self.edge, environ(**override))['status'], 400)

    def test_cross_origin_login_rejected(self):
        result = request(self.edge, environ('/api/auth/login', 'POST',
                         {'username': 'platform', 'password': PASSWORD}, HTTP_ORIGIN='https://evil.test'))
        self.assertEqual(result['status'], 403)

    def test_private_health_and_bridge_never_public(self):
        for path in ['/internal/portal/health', '/internal/portal/introspect', '/api/production-health']:
            self.assertEqual(request(self.edge, environ(path, HTTP_X_PORTAL_KEY=self.app.bridge_key))['status'], 404)

    def test_private_health_requires_loopback_and_secret(self):
        path = '/internal/portal/health'
        self.assertEqual(request(self.internal, environ(path))['status'], 404)
        self.assertEqual(request(self.internal, environ(path, HTTP_X_PORTAL_KEY=self.app.bridge_key))['status'], 200)
        self.assertEqual(request(self.internal, environ(path, REMOTE_ADDR='198.51.100.24',
                         HTTP_X_PORTAL_KEY=self.app.bridge_key))['status'], 403)
        self.assertEqual(request(self.internal, environ('/portal'))['status'], 404)

    def test_bridge_introspection_accepts_secure_cookie_only(self):
        self.app.accounts.bootstrap('platform', PASSWORD, quota_bytes=1024**3)
        token = self.app.accounts.login('platform', PASSWORD, 'test')
        for cookie, status in [('cn_dev_session=' + token, 401), ('__Host-cn_session=' + token, 200)]:
            result = request(self.internal, environ('/internal/portal/introspect', 'POST', {},
                             HTTP_X_PORTAL_KEY=self.app.bridge_key, HTTP_COOKIE=cookie))
            self.assertEqual(result['status'], status)

    def test_gateway_removes_browser_private_headers_and_corrects_ip(self):
        self.edge.gateway = Mock(return_value=[b'ok'])
        request(self.edge, environ(HTTP_X_PORTAL_KEY='forged', HTTP_CF_CONNECTING_IP='forged', HTTP_FORWARDED='forged'))
        env = self.edge.gateway.call_args.args[0]
        self.assertNotIn('HTTP_X_PORTAL_KEY', env)
        self.assertNotIn('HTTP_FORWARDED', env)
        self.assertEqual(env['HTTP_CF_CONNECTING_IP'], '198.51.100.24')

    def test_liveness_and_dependency_readiness_differ(self):
        self.assertEqual(request(self.edge, environ('/health'))['status'], 200)
        with patch.object(self.edge, 'ready', return_value=False):
            self.assertEqual(request(self.edge, environ('/ready'))['status'], 503)
        with patch.object(self.edge, 'ready', return_value=True):
            self.assertEqual(request(self.edge, environ('/ready'))['status'], 200)

    def test_https_only_and_no_checkout_data_or_dev_cookie(self):
        for change in [{'PORTAL_ORIGIN': 'http://portal.example.test'},
                       {'CN_WEB_DATA': str(ROOT / 'integration-data')},
                       {'CN_WEB_DATA': 'relative'}, {'PORTAL_COOKIE_NAME': 'cn_dev_session'},
                       {'PORTAL_BRIDGE_KEY': 'short'},
                       {'PORTAL_BRIDGE_KEY': self.env['IDENTIFIER_LOOKUP_KEY']}]:
            with self.assertRaises(ValueError):
                settings({**self.env, **change})

    def test_config_is_private_exclusive_and_never_rotates_existing_keys(self):
        path = Path(self.temporary.name) / 'app.env'
        kwargs = {'origin': ORIGIN, 'mongo_uri': 'mongodb://app:encoded@127.0.0.1:27017/stn_staging',
                  'admin_email': 'owner@example.test'}
        values = create_config(path, **kwargs)
        before = path.read_bytes()
        self.assertEqual(path.stat().st_mode & 0o777, 0o600)
        self.assertNotEqual(values['PORTAL_BRIDGE_KEY'], values['IDENTIFIER_LOOKUP_KEY'])
        with self.assertRaises(FileExistsError):
            create_config(path, **kwargs)
        self.assertEqual(path.read_bytes(), before)
        with self.assertRaises(ValueError):
            create_config(path, **{**kwargs, 'mongo_uri': 'mongodb://external.test/stn'})
        with self.assertRaises(ValueError):
            create_config(path, **{**kwargs, 'origin': 'https://127.0.0.1'})


class OperatorTests(unittest.TestCase):
    def releases(self, directory):
        root = Path(directory)
        previous = root / 'releases' / ('a' * 40)
        incoming = root / 'releases' / ('b' * 40)
        for path in (previous, incoming):
            path.mkdir(parents=True)
            (path / 'RELEASE_COMMIT').write_text(path.name)
        (root / 'current').symlink_to(previous)
        return root, previous, incoming

    @patch('deploy.activate_release.subprocess.run')
    @patch('deploy.activate_release.ready', return_value=True)
    def test_activation_switches_only_to_prepared_release(self, ready, run):
        with tempfile.TemporaryDirectory() as directory:
            root, previous, incoming = self.releases(directory)
            activate(incoming, ORIGIN, base=root)
            self.assertEqual((root / 'current').resolve(), incoming)
            with self.assertRaises(ValueError):
                activate(root / 'releases' / 'not-a-commit', ORIGIN, base=root)

    @patch('deploy.activate_release.time.sleep')
    @patch('deploy.activate_release.subprocess.run')
    @patch('deploy.activate_release.ready', return_value=False)
    def test_readiness_failure_restores_previous_code(self, ready, run, sleep):
        with tempfile.TemporaryDirectory() as directory:
            root, previous, incoming = self.releases(directory)
            with self.assertRaisesRegex(RuntimeError, 'readiness failed'):
                activate(incoming, ORIGIN, base=root)
            self.assertEqual((root / 'current').resolve(), previous)
            self.assertTrue((previous / 'RELEASE_COMMIT').is_file())

    @patch('deploy.backup.subprocess.run')
    def test_backup_always_restores_only_previous_service_state(self, run):
        run.return_value.returncode = 0
        with self.assertRaisesRegex(RuntimeError, 'capture failed'):
            with pause_services():
                raise RuntimeError('capture failed')
        calls = [call.args[0] for call in run.call_args_list]
        self.assertIn(['systemctl', 'start', 'stn-cn-python@gateway.service'], calls)
        self.assertIn(['systemctl', 'start', 'stn-cn-node.service'], calls)
        self.assertNotIn(['systemctl', 'start', 'stn-cn-maintenance.service'], calls)

    @patch('deploy.backup.subprocess.run')
    def test_inactive_services_are_not_started_by_backup(self, run):
        run.return_value.returncode = 3
        with pause_services():
            pass
        self.assertFalse(any(call.args[0][1] == 'start' for call in run.call_args_list))


if __name__ == '__main__':
    unittest.main(verbosity=2)
