"""Generate fresh-server config without exposing secrets or overwriting settings."""
import argparse
from getpass import getpass
import ipaddress
import os
from pathlib import Path
import re
import secrets
from urllib.parse import urlsplit


def create_config(path, *, origin, mongo_uri, admin_email):
    url = urlsplit(origin)
    if (url.scheme != 'https' or not url.hostname or url.port not in (None, 443)
            or url.path or url.query or url.fragment or url.username or url.password
            or not re.fullmatch(r'[a-z0-9](?:[a-z0-9.-]*[a-z0-9])?', url.hostname)
            or '.' not in url.hostname or url.hostname.endswith('.localhost')):
        raise ValueError('Use an exact HTTPS hostname with no port or path')
    try:
        ipaddress.ip_address(url.hostname)
    except ValueError:
        pass
    else:
        raise ValueError('Use the approved DNS hostname, not a numeric IP address')
    parsed = urlsplit(mongo_uri)
    if (parsed.scheme != 'mongodb' or parsed.hostname != '127.0.0.1'
            or not parsed.username or not parsed.password or parsed.port not in (None, 27017)
            or not re.fullmatch(r'/[A-Za-z][A-Za-z0-9_-]{0,62}', parsed.path)):
        raise ValueError('Use an authenticated loopback MongoDB URI with a database name')
    if not re.fullmatch(r'[^\s@]+@[^\s@]+\.[^\s@]+', admin_email):
        raise ValueError('Enter the platform administrator email')
    # Values are consumed by systemd EnvironmentFile, not evaluated as shell.
    for value in (origin, mongo_uri, admin_email):
        if any(ch in value for ch in '\r\n\x00"\\'):
            raise ValueError('Unsupported configuration characters; percent-encode URI credentials')
    values = {
        'PORTAL_ORIGIN': origin, 'CN_WEB_DATA': '/var/lib/stn-cn/cn',
        'PORTAL_MODE': 'combined', 'NEXT_PUBLIC_COMMON_PORTAL': '1',
        'PORTAL_COOKIE_NAME': '__Host-cn_session',
        'PORTAL_IDENTITY_URL': 'http://127.0.0.1:8788/internal/portal/introspect',
        'PORTAL_BRIDGE_KEY': secrets.token_urlsafe(48),
        'IDENTIFIER_LOOKUP_KEY': secrets.token_urlsafe(48),
        'MONGODB_URI': mongo_uri, 'STN_MONGO_TLS': '0',
        'ADMIN_EMAILS': admin_email, 'NODE_ENV': 'production',
    }
    path = Path(path)
    # Exclusive create is deliberate: existing lookup keys must never be rotated
    # by setup, otherwise stored GST lookup identities would stop matching.
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, 'w') as file:
        file.write(''.join(f'{key}="{value}"\n' for key, value in values.items()))
    return values


def main():
    if os.geteuid() != 0:
        raise SystemExit('Run as root on the fresh staging VPS')
    parser = argparse.ArgumentParser()
    parser.add_argument('--origin', required=True)
    parser.add_argument('--admin-email', required=True)
    args = parser.parse_args()
    directory = Path('/etc/stn-cn')
    directory.mkdir(mode=0o700, exist_ok=True)
    create_config(directory / 'app.env', origin=args.origin,
                  mongo_uri=getpass('Authenticated loopback MongoDB URI (hidden): '),
                  admin_email=args.admin_email)
    print('Private configuration created; values were not printed. Existing configurations are never replaced.')


if __name__ == '__main__':
    main()
