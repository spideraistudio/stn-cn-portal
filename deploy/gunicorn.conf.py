"""Private loopback listeners only; one worker avoids in-process state divergence."""
import os

role = os.environ['PORTAL_PROCESS']
if role not in {'gateway', 'identity'}:
    raise ValueError('Unknown portal process')
bind = '127.0.0.1:' + ('8787' if role == 'gateway' else '8788')
workers = 1
worker_class = 'gthread'
threads = 8
timeout = 180
graceful_timeout = 180
keepalive = 2
limit_request_line = 8190
limit_request_fields = 100
limit_request_field_size = 8190
forwarded_allow_ips = '127.0.0.1'
secure_scheme_headers = {'X-FORWARDED-PROTO': 'https'}
accesslog = None  # No query strings, private identifiers or tokens in request logs.
errorlog = '-'
capture_output = True
umask = 0o077
preload_app = False
control_socket_disable = True  # No operator control socket exposed by app users.
