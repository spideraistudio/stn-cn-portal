"""Same-origin WSGI account API; separate from the offline loopback server."""
from http.cookies import SimpleCookie, CookieError
import hmac
import json
from pathlib import Path
import re
from urllib.parse import urlsplit

from .accounts import Accounts
from .data_store import DataStore
from .ledger_service import LedgerService, encode
from .security import AuthError, PERMISSIONS, csrf_token
from .calculator_service import CalculatorService


class AccountApp:
    MAX_BODY = 16 * 1024 * 1024

    def __init__(self, accounts: Accounts, *, origin, development=False):
        url = urlsplit(origin)
        if url.path or url.query or url.fragment or url.username or url.password or not url.netloc:
            raise ValueError("Set an exact origin without a path")
        if development:
            if url.scheme != "http" or url.hostname not in {"127.0.0.1", "localhost"}:
                raise ValueError("Development mode is restricted to local HTTP")
        elif url.scheme != "https":
            raise ValueError("Production requires an HTTPS origin")
        self.accounts, self.origin = accounts, origin
        self.store = DataStore(accounts)
        self.ledger = LedgerService(self.store)
        self.store.ledger = self.ledger
        self.calculator = CalculatorService(self.store, self.ledger)
        self.store.calculator = self.calculator
        self.authority, self.development = url.netloc, development
        self.cookie_name = "cn_dev_session" if development else "__Host-cn_session"

    def cookie(self, token, *, clear=False):
        value = SimpleCookie()
        value[self.cookie_name] = "" if clear else token
        c = value[self.cookie_name]
        c["path"] = "/"
        c["httponly"] = True
        c["samesite"] = "Strict"
        c["max-age"] = 0 if clear else self.accounts.SESSION_SECONDS
        if not self.development:
            c["secure"] = True
        return c.OutputString()

    def token(self, environ):
        try:
            cookies = SimpleCookie(environ.get("HTTP_COOKIE", ""))
            cookie = cookies.get(self.cookie_name)
            return cookie.value if cookie else ""
        except CookieError:
            return ""

    def body(self, environ):
        if environ.get("CONTENT_TYPE", "").split(";")[0].lower() != "application/json":
            raise AuthError("Send JSON data", 415)
        try:
            length = int(environ.get("CONTENT_LENGTH", "0"))
            limit = self.MAX_BODY if environ.get("PATH_INFO", "").startswith(("/api/data/", "/api/projects/", "/api/ledger/", "/api/calculator/")) else 16384
            if not 0 < length <= limit:
                raise AuthError("Request body is missing or too large", 413)
            data = json.loads(environ["wsgi.input"].read(length))
            if not isinstance(data, dict):
                raise ValueError()
            return data
        except (ValueError, UnicodeError):
            raise AuthError("Invalid JSON object", 400) from None

    @staticmethod
    def fields(body, required, optional=()):
        if set(body) - set(required) - set(optional) or set(required) - set(body):
            raise AuthError("Request fields are missing or unsupported", 400)

    def dispatch(self, env):
        method, path = env["REQUEST_METHOD"], env.get("PATH_INFO", "/")
        if env.get("HTTP_HOST") != self.authority:
            raise AuthError("Unrecognised host", 400)
        if not self.development and env.get("wsgi.url_scheme") != "https":
            raise AuthError("HTTPS is required", 400)
        static = {"/": ("index.html", "text/html; charset=utf-8"),
                  "/account.js": ("account.js", "text/javascript; charset=utf-8"),
                  "/account.css": ("account.css", "text/css; charset=utf-8"),
                  "/workspace": ("workspace.html", "text/html; charset=utf-8"),
                  "/workspace.js": ("workspace.js", "text/javascript; charset=utf-8"),
                  "/ledger": ("ledger.html", "text/html; charset=utf-8"),
                  "/ledger.js": ("ledger.js", "text/javascript; charset=utf-8")}
        if method == "GET" and path in static:
            name, kind = static[path]
            return 200, (Path(__file__).parent / "static" / name).read_bytes(), [("Content-Type", kind)]
        calculator_assets = {"/calculator": "index.html", **{"/"+name: name for name in
            ("app.js", "polish.js", "ui-theme.js", "studio.js", "payment-workbench.js", "scheme-options.js", "cd-card-display.js",
             "studio.css", "style.css", "cd-card-display.css", "studio-art.svg", "app.ico", "fonts/Manrope.ttf", "web-session.js", "web-bridge.js", "billing-audit.js", "audit-product-mapping.js", "audit-categories.js", "audit-categories.css", "suite-theme.js", "suite-theme.css", "ledger-panel.js")}}
        if method == "GET" and path in calculator_assets:
            import mimetypes
            name = calculator_assets[path]
            kind = mimetypes.guess_type(name)[0] or "application/octet-stream"
            return 200, (Path(__file__).parent / "calculator_static" / name).read_bytes(), [("Content-Type", kind)]
        if method == "GET" and path == "/health":
            return 200, {"status": "ok", "phase": 7}, []
        if not path.startswith("/api/"):
            raise AuthError("Not found", 404)
        if env.get("QUERY_STRING"):
            raise AuthError("This endpoint does not accept query parameters", 400)
        token = self.token(env)
        unsafe = method not in {"GET", "HEAD", "OPTIONS"}
        if unsafe and env.get("HTTP_ORIGIN") != self.origin:
            raise AuthError("Request origin is not allowed", 403)
        if method == "POST" and path == "/api/auth/login":
            data = self.body(env)
            self.fields(data, {"username", "password"})
            token = self.accounts.login(data["username"], data["password"], env.get("REMOTE_ADDR", "unknown"), token)
            return 200, {"signed_in": True}, [("Set-Cookie", self.cookie(token))]
        # No open registration, browser bootstrap or offline API fallback.
        user = self.accounts.me(token)
        if unsafe:
            supplied = env.get("HTTP_X_CSRF_TOKEN", "")
            if not hmac.compare_digest(supplied.encode(), csrf_token(token).encode()):
                raise AuthError("Security token is missing or expired", 403)
        if path == "/api/storage/cleanup" and method == "POST":
            self.fields(self.body(env), set())
            return 200, self.accounts.cleanup_temporary(token), []
        calc_match = re.fullmatch(r"/api/calculator/([a-z-]+)", path)
        if calc_match:
            action = calc_match.group(1)
            if method not in ({"GET"} if action in {"state", "native-state"} else {"GET", "POST"} if action == "ui-preferences" else {"POST"}):
                raise AuthError("Not found", 404)
            return 200, self.calculator.request(token, action, self.body(env) if unsafe else None,
                env.get("HTTP_X_CN_PROJECT", "main"), env.get("HTTP_X_CN_WORKBOOK", "legacy"),
                env.get("HTTP_X_CN_RECORD", "")), []
        ledger_match = re.fullmatch(r"/api/ledger/workbooks/([a-f0-9]{32})(?:/(config|preview-import|apply-import|mapping|resolve-mappings|review|reread|summary|audit|audit-review|year-preview|year-apply|ledgers/([a-f0-9]{32})))?", path)
        if ledger_match:
            workbook, action, lid = ledger_match.groups()
            if method == "GET" and (action is None or lid):
                return 200, self.ledger.state(token, workbook, lid), []
            if action == "config" and method == "PUT":
                return 200, self.ledger.config(token, workbook, self.body(env)), []
            if method == "POST":
                data = self.body(env)
                if action in {"preview-import", "apply-import"}:
                    return 200, self.ledger.import_files(token, workbook, data, action == "apply-import"), []
                if action in {"year-preview", "year-apply"}:
                    return 200, self.ledger.year_link(token, workbook, data, action == "year-apply"), []
                handlers = {"mapping": self.ledger.mapping, "resolve-mappings": self.ledger.resolve_mappings, "review": self.ledger.review,
                            "reread": self.ledger.reread, "summary": self.ledger.summary,
                            "audit": self.ledger.audit, "audit-review": self.ledger.audit_review}
                if action in handlers:
                    return 200, handlers[action](token, workbook, data), []
            raise AuthError("Not found", 404)
        file_match = re.fullmatch(r"/api/files/([a-f0-9]{32})/download", path)
        if file_match and method == "GET":
            document = self.store.download(token, file_match.group(1))
            import base64
            return 200, base64.b64decode(document['data']['content_base64']), [
                ("Content-Type", "application/octet-stream"),
                ("Content-Disposition", 'attachment; filename="source-file.bin"')]
        if path == "/api/projects/import" and method == "POST":
            return 201, self.store.import_project(token, self.body(env)), []
        match = re.fullmatch(r"/api/projects/([a-f0-9]{32})/export", path)
        if match and method == "GET":
            return 200, self.store.export(token, match.group(1)), []
        match = re.fullmatch(r"/api/data/([a-z]+)(?:/([a-f0-9]{32}))?", path)
        if match:
            kind, oid = match.groups()
            result = self.store.request(token, method, kind, oid,
                                        self.body(env) if unsafe else None)
            return (201 if method == "POST" else 200), result, []
        if method == "GET" and path == "/api/me":
            return 200, {"user": user, "csrf_token": csrf_token(token), "permission_options": sorted(PERMISSIONS)}, []
        if method == "GET" and path == "/api/workspace":
            return 200, self.accounts.workspace(token), []
        if method == "GET" and path == "/api/admin/users":
            return 200, {"users": self.accounts.list_users(token)}, []
        if method == "GET" and path == "/api/admin/audit":
            return 200, {"events": self.accounts.audit_log(token)}, []
        if unsafe:
            data = self.body(env)
            if method == "POST" and path in {"/api/auth/logout", "/api/auth/logout-all"}:
                self.fields(data, set())
                self.accounts.logout(token, all_sessions=path.endswith("logout-all"))
                return 200, {"signed_out": True}, [("Set-Cookie", self.cookie("", clear=True))]
            if method == "POST" and path == "/api/auth/password":
                self.fields(data, {"current_password", "new_password"})
                self.accounts.change_password(token, data["current_password"], data["new_password"])
                return 200, {"signed_out": True}, [("Set-Cookie", self.cookie("", clear=True))]
            if method == "POST" and path == "/api/admin/users":
                self.fields(data, {"username", "temporary_password", "permissions"}, {"quota_bytes","role","parent_admin","max_users","user_quota_bytes","manage_users"})
                return 201, {"user": self.accounts.create_user(token, **data)}, []
            match = re.fullmatch(r"/api/admin/users/([a-f0-9]{32})(/reset-password)?", path)
            if match:
                uid, reset = match.groups()
                if method == "POST" and reset:
                    self.fields(data, {"temporary_password"})
                    self.accounts.reset_password(token, uid, data["temporary_password"])
                    return 200, {"reset": True}, []
                if method == "PATCH" and not reset:
                    return 200, {"user": self.accounts.update_user(token, uid, data)}, []
        raise AuthError("Not found", 404)

    def __call__(self, env, start_response):
        try:
            status, body, headers = self.dispatch(env)
        except AuthError as exc:
            status, body, headers = exc.status, {"error": str(exc)}, []
        except Exception:
            # Neither exception text nor credentials/SQL are returned to browsers.
            status, body, headers = 500, {"error": "Request could not be completed"}, []
        if not isinstance(body, bytes):
            body = encode(body).encode()
            headers.append(("Content-Type", "application/json; charset=utf-8"))
        style_policy = "'self' 'unsafe-inline'" if env.get("PATH_INFO") == "/calculator" else "'self'"
        headers += [("Content-Length", str(len(body))), ("Cache-Control", "no-store"),
                    ("X-Content-Type-Options", "nosniff"), ("X-Frame-Options", "DENY"),
                    ("Referrer-Policy", "no-referrer"),
                    ("Content-Security-Policy", f"default-src 'self'; script-src 'self'; style-src {style_policy}; img-src 'self' data:; font-src 'self'; connect-src 'self'; frame-ancestors 'none'; base-uri 'none'; form-action 'self'"),
                    ("Permissions-Policy", "camera=(), microphone=(), geolocation=()")]
        if not self.development:
            headers.append(("Strict-Transport-Security", "max-age=31536000"))
        labels = {302:"Found",200:"OK",201:"Created",400:"Bad Request",401:"Unauthorized",403:"Forbidden",404:"Not Found",409:"Conflict",413:"Payload Too Large",415:"Unsupported Media Type",429:"Too Many Requests",500:"Internal Server Error"}
        start_response(f"{status} {labels.get(status, 'Error')}", headers)
        return [body]
