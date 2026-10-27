"""Real HTTP checks on isolated temporary data, without weakening password KDF."""
import concurrent.futures
from html.parser import HTMLParser
import http.cookies
import json
from pathlib import Path
import sqlite3
import sys
import tempfile
import threading
import unittest
import urllib.error
import urllib.request
from wsgiref.simple_server import make_server

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))
from cn_web.accounts import Accounts
from cn_web.http_app import AccountApp
from cn_web.cli import QuietHandler
from cn_web.security import AuthError, PERMISSIONS, hash_password, verify_password, session_hash

ADMIN_PASSWORD = "Admin test passphrase 2026!"
TEMP_PASSWORD = "Temporary test passphrase!"
USER_PASSWORD = "Changed test passphrase 2026!"


class Browser:
    def __init__(self, origin):
        self.origin, self.token, self.csrf = origin, "", ""

    def request(self, path, data=None, method=None, headers=None, raw=None):
        method = method or ("POST" if data is not None or raw is not None else "GET")
        h = {"Cookie": "cn_dev_session=" + self.token}
        if method not in {"GET", "HEAD"}:
            h.update({"Origin": self.origin, "Content-Type": "application/json", "X-CSRF-Token": self.csrf})
        for k, v in (headers or {}).items():
            if v is None:
                h.pop(k, None)
            else:
                h[k] = v
        payload = raw if raw is not None else json.dumps(data).encode() if data is not None else None
        request = urllib.request.Request(self.origin + path, payload, h, method=method)
        try:
            response = urllib.request.urlopen(request, timeout=20)
        except urllib.error.HTTPError as error:
            response = error
        with response:
            content = response.read()
            content_type = response.headers.get("Content-Type", "")
            body = json.loads(content) if "application/json" in content_type else content.decode()
            cookie = response.headers.get("Set-Cookie")
            if cookie:
                self.token = http.cookies.SimpleCookie(cookie)["cn_dev_session"].value
            if isinstance(body, dict) and body.get("csrf_token"):
                self.csrf = body["csrf_token"]
            return response.status, body, dict(response.headers)

    def login(self, username, password):
        status, body, _ = self.request("/api/auth/login", {"username": username, "password": password})
        if status != 200:
            raise AssertionError((status, body))
        self.request("/api/me")


class AccountHTTPTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.now = [1800000000.0]
        self.accounts = Accounts(self.tmp.name, clock=lambda: self.now[0])
        self.admin_id = self.accounts.bootstrap("admin", ADMIN_PASSWORD, quota_bytes=104857600)
        self.server = make_server("127.0.0.1", 0, lambda e, s: [], handler_class=QuietHandler)
        self.origin = "http://127.0.0.1:" + str(self.server.server_port)
        self.app = AccountApp(self.accounts, origin=self.origin, development=True)
        self.server.set_app(self.app)
        self.thread = threading.Thread(target=self.server.serve_forever, kwargs={"poll_interval": .01}, daemon=True)
        self.thread.start()
        self.addCleanup(self.stop)
        self.admin = Browser(self.origin)
        self.admin.login("admin", ADMIN_PASSWORD)

    def stop(self):
        self.server.shutdown()
        self.thread.join(timeout=2)
        self.server.server_close()

    def create(self, name="user-a", permissions=None):
        status, body, _ = self.admin.request("/api/admin/users", {
            "username": name, "temporary_password": TEMP_PASSWORD,
            "quota_bytes": 52428800,
            "permissions": list(PERMISSIONS) if permissions is None else permissions})
        self.assertEqual(status, 201, body)
        return body["user"]

    def user_browser(self, name="user-a", permissions=None):
        user = self.create(name, permissions)
        browser = Browser(self.origin)
        browser.login(name, TEMP_PASSWORD)
        status, body, _ = browser.request("/api/auth/password", {"current_password": TEMP_PASSWORD, "new_password": USER_PASSWORD})
        self.assertEqual(status, 200, body)
        browser.login(name, USER_PASSWORD)
        return user, browser

    def test_health_and_pc_console_have_no_credentials(self):
        guest = Browser(self.origin)
        self.assertEqual(guest.request("/health")[1], {"status": "ok", "phase": 7})
        status, html, headers = guest.request("/")
        self.assertEqual(status, 200)
        self.assertIn("Users &amp; access".replace("&amp;", "&"), html)
        self.assertNotIn(ADMIN_PASSWORD, html)
        self.assertEqual(headers["Cache-Control"], "no-store")
        self.assertIn("frame-ancestors 'none'", headers["Content-Security-Policy"])

    def test_bootstrap_is_operator_only_and_one_time(self):
        with self.assertRaises(AuthError):
            self.accounts.bootstrap("second", ADMIN_PASSWORD, quota_bytes=1048576)
        self.assertEqual(self.admin.request("/api/bootstrap", {})[0], 404)
        self.assertEqual(Browser(self.origin).request("/api/register", {})[0], 401)

    def test_guest_and_forged_identity_headers_denied(self):
        b = Browser(self.origin)
        for path in ("/api/me", "/api/workspace", "/api/admin/users", "/api/admin/audit", "/api/state"):
            with self.subTest(path=path):
                status, _, _ = b.request(path, headers={"X-CN-User":self.admin_id, "X-CN-Role":"admin", "Authorization":"Bearer pretend", "X-CN-Project":"main"})
                self.assertEqual(status, 401)
        b.token = "forged"
        self.assertEqual(b.request("/api/me")[0], 401)

    def test_new_user_must_change_password_and_old_session_is_revoked(self):
        self.create()
        b = Browser(self.origin)
        b.login("user-a", TEMP_PASSWORD)
        old = b.token
        self.assertTrue(b.request("/api/me")[1]["user"]["must_change_password"])
        self.assertEqual(b.request("/api/workspace")[0], 403)
        self.assertEqual(b.request("/api/auth/password", {"current_password":"wrong", "new_password":USER_PASSWORD})[0], 403)
        self.assertEqual(b.request("/api/auth/password", {"current_password":TEMP_PASSWORD, "new_password":USER_PASSWORD})[0], 200)
        b.token = old
        self.assertEqual(b.request("/api/me")[0], 401)
        self.assertEqual(b.request("/api/auth/login", {"username":"user-a", "password":TEMP_PASSWORD})[0], 401)
        b.login("user-a", USER_PASSWORD)
        self.assertEqual(b.request("/api/workspace")[0], 200)

    def test_independent_workspaces_even_with_forged_selection_headers(self):
        a, ba = self.user_browser()
        b, bb = self.user_browser("user-b")
        wa = ba.request("/api/workspace")[1]
        wb = bb.request("/api/workspace")[1]
        self.assertNotEqual(wa["workspace_id"], wb["workspace_id"])
        self.assertNotIn("directory", wa)
        status, same, _ = ba.request("/api/workspace", headers={"X-CN-User":b["id"], "X-CN-Project":wb["workspace_id"], "X-CN-Workbook":"other"})
        self.assertEqual(status, 200)
        self.assertEqual(same["workspace_id"], wa["workspace_id"])
        self.assertEqual(ba.request("/api/workspace?user_id="+b["id"])[0], 400)

    def test_regular_user_cannot_manage_users_or_read_audit(self):
        user, b = self.user_browser()
        self.assertEqual(b.request("/api/admin/users")[0], 403)
        self.assertEqual(b.request("/api/admin/audit")[0], 403)
        self.assertEqual(b.request("/api/admin/users/"+user["id"], {"permissions":list(PERMISSIONS)}, method="PATCH")[0], 403)
        self.assertEqual(b.request("/api/admin/users/"+user["id"]+"/reset-password", {"temporary_password":TEMP_PASSWORD})[0], 403)
        self.assertEqual(b.request("/api/admin/users", {"username":"hacker", "temporary_password":TEMP_PASSWORD, "quota_bytes":1000, "permissions":[]})[0], 403)

    def test_permissions_enforced_without_session_reissue(self):
        user, b = self.user_browser()
        original_token = b.token
        self.assertEqual(b.request("/api/workspace")[0], 200)
        for permission in sorted(PERMISSIONS):
            self.accounts.authorize(b.token, permission)
        self.assertEqual(self.admin.request("/api/admin/users/"+user["id"], {"permissions":[]}, method="PATCH")[0], 200)
        self.assertEqual(b.token, original_token)
        self.assertEqual(b.request("/api/workspace")[0], 403)
        for permission in sorted(PERMISSIONS):
            with self.subTest(permission=permission), self.assertRaises(AuthError):
                self.accounts.authorize(b.token, permission)
        self.assertEqual(self.admin.request("/api/admin/users/"+user["id"], {"permissions":["view_workspace"]}, method="PATCH")[0], 200)
        self.assertEqual(b.request("/api/workspace")[0], 200)

    def test_disable_revokes_every_session_and_reenable_does_not_restore(self):
        user, b = self.user_browser()
        c = Browser(self.origin)
        c.login("user-a", USER_PASSWORD)
        old = (b.token, c.token)
        self.assertEqual(self.admin.request("/api/admin/users/"+user["id"], {"enabled":False}, method="PATCH")[0], 200)
        self.assertEqual(b.request("/api/me")[0], 401)
        self.assertEqual(c.request("/api/me")[0], 401)
        self.assertEqual(c.request("/api/auth/login", {"username":"user-a", "password":USER_PASSWORD})[0], 401)
        self.admin.request("/api/admin/users/"+user["id"], {"enabled":True}, method="PATCH")
        for token in old:
            with self.assertRaises(AuthError):
                self.accounts.me(token)
        b.login("user-a", USER_PASSWORD)

    def test_reset_revokes_sessions_and_forces_new_password(self):
        user, b = self.user_browser()
        old = b.token
        self.assertEqual(self.admin.request("/api/admin/users/"+user["id"]+"/reset-password", {"temporary_password":TEMP_PASSWORD})[0], 200)
        self.assertEqual(b.request("/api/me")[0], 401)
        self.assertEqual(b.request("/api/auth/login", {"username":"user-a", "password":USER_PASSWORD})[0], 401)
        b.login("user-a", TEMP_PASSWORD)
        self.assertNotEqual(b.token, old)
        self.assertEqual(b.request("/api/workspace")[0], 403)

    def test_logout_one_and_logout_all(self):
        _, b = self.user_browser()
        c = Browser(self.origin)
        c.login("user-a", USER_PASSWORD)
        old = b.token
        status, _, h = b.request("/api/auth/logout", {})
        self.assertEqual(status, 200)
        self.assertIn("Max-Age=0", h["Set-Cookie"])
        with self.assertRaises(AuthError):
            self.accounts.me(old)
        self.assertEqual(c.request("/api/me")[0], 200)
        b.login("user-a", USER_PASSWORD)
        self.assertEqual(c.request("/api/auth/logout-all", {})[0], 200)
        self.assertEqual(b.request("/api/me")[0], 401)

    def test_idle_and_absolute_expiry(self):
        token = self.admin.token
        self.now[0] += self.accounts.IDLE_SECONDS
        self.assertEqual(self.admin.request("/api/me")[0], 401)
        self.admin.login("admin", ADMIN_PASSWORD)
        self.now[0] += self.accounts.SESSION_SECONDS
        with self.accounts._tx() as db:
            db.execute("UPDATE sessions SET last_seen=?", (self.now[0],))
        self.assertEqual(self.admin.request("/api/me")[0], 401)

    def test_session_cookie_and_hash_storage_and_rotation(self):
        old = self.admin.token
        status, _, headers = self.admin.request("/api/auth/login", {"username":"admin", "password":ADMIN_PASSWORD})
        self.assertEqual(status, 200)
        cookie = headers["Set-Cookie"]
        self.assertIn("HttpOnly", cookie)
        self.assertIn("SameSite=Strict", cookie)
        self.assertIn("Path=/", cookie)
        self.assertNotEqual(self.admin.token, old)
        with self.assertRaises(AuthError):
            self.accounts.me(old)
        with sqlite3.connect(self.accounts.registry.path) as db:
            encoded = db.execute("SELECT password_hash FROM users WHERE id=?", (self.admin_id,)).fetchone()[0]
            tokens = [r[0] for r in db.execute("SELECT token_hash FROM sessions")]
        self.assertNotEqual(encoded, ADMIN_PASSWORD)
        self.assertIn(session_hash(self.admin.token), tokens)
        self.assertNotIn(self.admin.token, tokens)

    def test_origin_csrf_content_type_and_mass_assignment_guards(self):
        user = self.create()
        path = "/api/admin/users/" + user["id"]
        for headers in ({"Origin":"https://evil.example"}, {"Origin":None}, {"X-CSRF-Token":None}, {"X-CSRF-Token":"wrong"}, {"X-CSRF-Token":"é"}):
            with self.subTest(headers=headers):
                self.assertEqual(self.admin.request(path, {"enabled":False}, method="PATCH", headers=headers)[0], 403)
        self.assertEqual(self.admin.request(path, {"enabled":False}, method="PATCH", headers={"Content-Type":"text/plain"})[0], 415)
        self.assertEqual(self.admin.request(path, {"is_admin":True}, method="PATCH")[0], 400)
        self.assertEqual(self.admin.request(path, {"permissions":["manage_users"]}, method="PATCH")[0], 400)
        self.assertEqual(self.admin.request(path, {"enabled":"false"}, method="PATCH")[0], 400)
        self.assertEqual(self.admin.request(path, {"quota_bytes":True}, method="PATCH")[0], 400)
        self.assertTrue(self.accounts.list_users(self.admin.token)[1]["enabled"])

    def test_unknown_credentials_generic_and_rate_limited_persistently(self):
        b = Browser(self.origin)
        errors = []
        for name in ("admin", "missing-user"):
            errors.append(b.request("/api/auth/login", {"username":name, "password":"incorrect"})[:2])
        self.assertEqual(errors[0], errors[1])
        for _ in range(self.accounts.USER_ATTEMPTS - 1):
            self.assertEqual(b.request("/api/auth/login", {"username":"missing-user", "password":"incorrect"})[0], 401)
        self.assertEqual(b.request("/api/auth/login", {"username":"missing-user", "password":"incorrect"})[0], 429)
        restarted = Accounts(self.tmp.name, clock=lambda:self.now[0])
        with self.assertRaises(AuthError) as error:
            restarted.login("missing-user", "incorrect", "127.0.0.1")
        self.assertEqual(error.exception.status, 429)
        self.now[0] += self.accounts.ATTEMPT_WINDOW + 1
        self.assertEqual(b.request("/api/auth/login", {"username":"missing-user", "password":"incorrect"})[0], 401)

    def test_malformed_json_oversize_host_and_missing_routes(self):
        self.assertEqual(self.admin.request("/api/auth/logout", raw=b"{")[0], 400)
        self.assertEqual(self.admin.request("/api/auth/logout", raw=b"[1]")[0], 400)
        self.assertEqual(self.admin.request("/api/auth/logout", raw=b" "*17000)[0], 413)
        self.assertEqual(self.admin.request("/api/me", headers={"Host":"evil.example"})[0], 400)
        self.assertEqual(self.admin.request("/api/state")[0], 404)
        self.assertEqual(self.admin.request("/offline_baseline/data/calculator.sqlite3")[0], 404)

    def test_password_policy_invalid_names_and_duplicate_accounts(self):
        for password in ("short", "x"*129, 1234, "x"*12+"\ud800"):
            self.assertEqual(self.admin.request("/api/admin/users", {"username":"new-user", "temporary_password":password, "quota_bytes":1000, "permissions":[]})[0], 400)
        self.create()
        self.assertEqual(self.admin.request("/api/admin/users", {"username":"USER-A", "temporary_password":TEMP_PASSWORD, "quota_bytes":1000, "permissions":[]})[0], 409)
        b = Browser(self.origin)
        for name in ("../../admin", "admin' OR 1=1 --", "!invalid-name!"):
            self.assertEqual(b.request("/api/auth/login", {"username":name, "password":ADMIN_PASSWORD})[0], 401)
        self.create("invalid-name")
        self.assertEqual(b.request("/api/auth/login", {"username":"<bad>", "password":TEMP_PASSWORD})[0], 401)
        self.assertEqual(b.request("/api/auth/login", {"username":"admin", "password":"\ud800"})[0], 401)

    def test_admin_protection_and_audit_contains_no_secrets(self):
        self.assertEqual(self.admin.request("/api/admin/users/"+self.admin_id, {"enabled":False}, method="PATCH")[0], 409)
        self.create()
        events = self.admin.request("/api/admin/audit")[1]["events"]
        blob = json.dumps(events)
        for secret in (self.admin.token, self.admin.csrf, ADMIN_PASSWORD, TEMP_PASSWORD):
            self.assertNotIn(secret, blob)
        self.assertIn("user_created", blob)

    def test_concurrent_duplicate_user_creation_is_atomic(self):
        def attempt(_):
            try:
                return self.accounts.create_user(self.admin.token, username="race-user", temporary_password=TEMP_PASSWORD, quota_bytes=1000, permissions=[])["id"]
            except AuthError as exc:
                return exc.status
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
            result = list(pool.map(attempt, range(2)))
        self.assertEqual(sum(x==409 for x in result), 1)
        with sqlite3.connect(self.accounts.registry.path) as db:
            self.assertEqual(db.execute("SELECT COUNT(*) FROM users").fetchone()[0], 2)
            self.assertEqual(db.execute("SELECT COUNT(*) FROM workspaces").fetchone()[0], 2)


class PasswordAndConfigurationTests(unittest.TestCase):
    def test_salted_hashes_and_wrong_password(self):
        a, b = hash_password(ADMIN_PASSWORD), hash_password(ADMIN_PASSWORD)
        self.assertNotEqual(a,b)
        self.assertTrue(verify_password(ADMIN_PASSWORD,a))
        self.assertFalse(verify_password("wrong",a))
        self.assertFalse(verify_password(ADMIN_PASSWORD,"broken"))

    def test_production_requires_https_and_uses_secure_host_cookie(self):
        with tempfile.TemporaryDirectory() as d:
            accounts = Accounts(d)
            with self.assertRaises(ValueError):
                AccountApp(accounts, origin="http://example.com")
            with self.assertRaises(ValueError):
                AccountApp(accounts, origin="http://example.com", development=True)
            app = AccountApp(accounts, origin="https://cn.example.com")
            cookie = app.cookie("x"*43)
            for fragment in ("__Host-cn_session", "Secure", "HttpOnly", "SameSite=Strict", "Path=/"):
                self.assertIn(fragment,cookie)
            self.assertNotIn("Domain=",cookie)

    def test_production_rejects_plain_http_even_with_forged_forwarded_headers(self):
        with tempfile.TemporaryDirectory() as d:
            app = AccountApp(Accounts(d), origin="https://cn.example.com")
            status = []
            env = {"REQUEST_METHOD":"GET", "PATH_INFO":"/health", "HTTP_HOST":"cn.example.com",
                   "wsgi.url_scheme":"http", "HTTP_X_FORWARDED_PROTO":"https"}
            response = b"".join(app(env, lambda s,h:status.append(s)))
            self.assertTrue(status[0].startswith("400"))
            self.assertIn(b"HTTPS is required", response)

    def test_pc_console_form_bindings_and_no_inline_execution(self):
        class Inventory(HTMLParser):
            def __init__(self):
                super().__init__()
                self.ids, self.forms, self.form = set(), {}, None
                self.inline = False
            def handle_starttag(self, tag, attrs):
                attrs = dict(attrs)
                if attrs.get("id"):
                    if attrs["id"] in self.ids:
                        raise AssertionError("Duplicate HTML ID")
                    self.ids.add(attrs["id"])
                if any(k.startswith("on") for k in attrs):
                    self.inline = True
                if tag=="script" and not attrs.get("src"):
                    self.inline = True
                if tag=="form":
                    self.form=attrs["id"]
                    self.forms[self.form]=set()
                if self.form and attrs.get("name"):
                    self.forms[self.form].add(attrs["name"])
            def handle_endtag(self, tag):
                if tag=="form": self.form=None
        inv=Inventory()
        inv.feed((ROOT/"backend/cn_web/static/index.html").read_text())
        expected={"login-form":{"username","password"},"password-form":{"current_password","new_password"},
                  "create-user":{"username","temporary_password","quota_mib","role","parent_admin","max_users","user_quota_mib","manage_users","cn_access","stn_access"},
                  "edit-form":{"enabled","quota_mib","parent_admin","max_users","user_quota_mib","manage_users"},"reset-form":{"temporary_password"}}
        self.assertEqual(inv.forms,expected)
        self.assertFalse(inv.inline)
        script=(ROOT/"backend/cn_web/static/account.js").read_text()
        import re
        for selector in re.findall(r"\$\(['\"]#([^'\"]+)['\"]\)",script):
            self.assertIn(selector,inv.ids)
        self.assertNotIn("innerHTML",script)
        self.assertNotIn("localStorage",script)
        self.assertNotIn("sessionStorage",script)


if __name__ == "__main__":
    unittest.main()
