"""HTTPS-only combined application, supervised independently from Next.js.

All listeners bind loopback. Only the edge listener trusts Caddy's replaced
forwarding headers. The identity listener never trusts browser identity headers.
"""
import hmac
import http.client
import ipaddress
import json
import os
from pathlib import Path
import re
import sys
from urllib.parse import urlencode, urlsplit

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'cn' / 'backend'))
from cn_web.portal import PortalAccounts
from cn_web.portal_http import PortalApp
from cn_web.security import AuthError
from integration.gateway import Gateway, InternalOnly


def settings(environ=None):
    env = os.environ if environ is None else environ
    origin = env.get('PORTAL_ORIGIN', '')
    url = urlsplit(origin)
    if (url.scheme != 'https' or not url.hostname or url.path or url.query
            or url.fragment or url.username or url.password or url.port == 0
            or url.hostname in {'localhost', '127.0.0.1', '::1'}):
        raise ValueError('Set PORTAL_ORIGIN to the exact HTTPS site origin')
    data = Path(env.get('CN_WEB_DATA', ''))
    if (not data.is_absolute() or len(data.parts) < 4
            or data.resolve().is_relative_to(ROOT)):
        raise ValueError('CN_WEB_DATA must be an absolute private directory outside the source checkout')
    for key in ('PORTAL_BRIDGE_KEY', 'IDENTIFIER_LOOKUP_KEY'):
        if not re.fullmatch(r'[A-Za-z0-9_-]{43,}', env.get(key, '')):
            raise ValueError('Set a generated production secret for ' + key)
    if env['PORTAL_BRIDGE_KEY'] == env['IDENTIFIER_LOOKUP_KEY']:
        raise ValueError('Bridge and lookup keys must differ')
    if env.get('PORTAL_COOKIE_NAME', '__Host-cn_session') != '__Host-cn_session':
        raise ValueError('Production requires the secure host-only cookie')
    return origin, data, env['PORTAL_BRIDGE_KEY']


def response(start, code, body):
    raw = json.dumps(body).encode()
    start(code, [('Content-Type', 'application/json'), ('Content-Length', str(len(raw))),
                 ('Cache-Control', 'no-store'), ('X-Content-Type-Options', 'nosniff')])
    return [raw]


def loopback(value):
    try:
        return ipaddress.ip_address(value).is_loopback
    except ValueError:
        return False


def make_portal():
    origin, data, secret = settings()
    accounts = PortalAccounts(data)

    def validate_link(token, member_id):
        conn = http.client.HTTPConnection('127.0.0.1', 3000, timeout=8)
        try:
            conn.request('GET', '/api/portal-stn/link-check?' + urlencode({'id': member_id}),
                         headers={'Host': urlsplit(origin).netloc,
                                  'Cookie': '__Host-cn_session=' + token,
                                  'X-Forwarded-Proto': 'https'})
            result = conn.getresponse()
            if result.status != 200:
                raise AuthError('STN member verification failed; nothing was linked', 503)
            return json.loads(result.read())
        except (OSError, ValueError, http.client.HTTPException):
            raise AuthError('STN unavailable; nothing was linked', 503) from None
        finally:
            conn.close()

    return PortalApp(accounts, origin=origin, development=False,
                     bridge_key=secret, stn_link_validator=validate_link)


class PrivateIdentity:
    def __init__(self, app):
        self.app = app
        self.dispatch = InternalOnly(app)

    def __call__(self, env, start):
        if not loopback(env.get('REMOTE_ADDR', '')):
            return response(start, '403 Forbidden', {'error': 'Private listener'})
        if env.get('PATH_INFO') == '/internal/portal/health':
            if (env.get('REQUEST_METHOD') != 'GET' or
                    not hmac.compare_digest(env.get('HTTP_X_PORTAL_KEY', ''), self.app.bridge_key)):
                return response(start, '404 Not Found', {'error': 'Not found'})
            try:
                with self.app.accounts._tx() as db:
                    db.execute('SELECT 1').fetchone()
                return response(start, '200 OK', {'status': 'ok'})
            except Exception:
                return response(start, '503 Service Unavailable', {'status': 'unavailable'})
        return self.dispatch(dict(env, **{'wsgi.url_scheme': 'https'}), start)


class ProductionEdge:
    def __init__(self, app):
        self.app = app
        self.gateway = Gateway(app, 3000)

    def ready(self):
        for port, path in [(8788, '/internal/portal/health'), (3000, '/api/production-health')]:
            conn = http.client.HTTPConnection('127.0.0.1', port, timeout=5)
            try:
                conn.request('GET', path, headers={'Host': self.app.authority,
                             'X-Portal-Key': self.app.bridge_key})
                result = conn.getresponse()
                payload = result.read(4096)
                if result.status != 200 or json.loads(payload).get('status') != 'ok':
                    return False
            except (OSError, ValueError, http.client.HTTPException):
                return False
            finally:
                conn.close()
        return True

    def __call__(self, env, start):
        # Gunicorn binds 127.0.0.1; Caddy is the only public-facing listener.
        if (not loopback(env.get('REMOTE_ADDR', '')) or
                env.get('HTTP_HOST') != self.app.authority or
                env.get('HTTP_X_FORWARDED_HOST') != self.app.authority or
                env.get('HTTP_X_FORWARDED_PROTO') != 'https' or
                env.get('wsgi.url_scheme') != 'https'):
            return response(start, '400 Bad Request', {'error': 'Trusted HTTPS proxy required'})
        try:
            client = str(ipaddress.ip_address(env.get('HTTP_X_FORWARDED_FOR', '')))
        except ValueError:
            return response(start, '400 Bad Request', {'error': 'Invalid client address'})
        env = dict(env, REMOTE_ADDR=client, HTTP_CF_CONNECTING_IP=client)
        # Never forward browser-supplied private/proxy credentials downstream.
        for name in ('HTTP_X_PORTAL_KEY', 'HTTP_FORWARDED', 'HTTP_X_REAL_IP'):
            env.pop(name, None)
        path = env.get('PATH_INFO', '/')
        if path.rstrip('/') == '/api/production-health':
            return response(start, '404 Not Found', {'error': 'Not found'})
        if path == '/ready':
            if env.get('REQUEST_METHOD') not in {'GET', 'HEAD'}:
                return response(start, '405 Method Not Allowed', {'error': 'Method not allowed'})
            ok = self.ready()
            return response(start, '200 OK' if ok else '503 Service Unavailable',
                            {'status': 'ok' if ok else 'unavailable'})
        return self.gateway(env, start)


def create_gateway():
    return ProductionEdge(make_portal())


def create_identity():
    return PrivateIdentity(make_portal())
