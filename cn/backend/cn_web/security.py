"""Password hashing and explicit business permissions; no financial changes."""
import hashlib
import hmac
import secrets

# OWASP-supported scrypt tradeoff: 16 MiB, five passes (N=2^14,r=8,p=5).
N, R, P = 16384, 8, 5
PERMISSIONS = frozenset({
    "view_workspace", "edit_schemes", "import_statements", "edit_ledger",
    "allocate_payments", "finalise", "issue_cn", "export_print",
    "delete_records", "permanent_delete",
})


class AuthError(Exception):
    def __init__(self, message, status=403):
        super().__init__(message)
        self.status = status


def check_password_policy(password):
    try:
        valid = isinstance(password, str) and 12 <= len(password) <= 128 and len(password.encode("utf-8")) <= 512
    except UnicodeError:
        valid = False
    if not valid:
        raise AuthError("Use a password between 12 and 128 characters", 400)


def hash_password(password):
    check_password_policy(password)
    salt = secrets.token_bytes(16)
    value = hashlib.scrypt(password.encode(), salt=salt, n=N, r=R, p=P, dklen=32)
    return f"scrypt${N}${R}${P}${salt.hex()}${value.hex()}"


def verify_password(password, encoded):
    try:
        if not isinstance(password, str) or len(password.encode()) > 512:
            return False
        kind, n, r, p, salt, expected = encoded.split("$")
        if (kind, int(n), int(r), int(p)) != ("scrypt", N, R, P):
            return False
        value = hashlib.scrypt(password.encode(), salt=bytes.fromhex(salt), n=N, r=R, p=P, dklen=32)
        return hmac.compare_digest(value.hex(), expected)
    except (ValueError, TypeError, UnicodeError):
        return False


def checked_permissions(values):
    if (not isinstance(values, list) or any(not isinstance(v, str) for v in values)
            or len(set(values)) != len(values) or set(values) - PERMISSIONS):
        raise AuthError("Invalid permission selection", 400)
    return sorted(values)


def require_permission(user, permission):
    # Admin is an account-management role, never an implicit financial bypass.
    if permission not in PERMISSIONS or permission not in user["permissions"]:
        raise AuthError("This action is not permitted")


def session_hash(token):
    return hashlib.sha256(token.encode()).hexdigest()


def csrf_token(token):
    return hashlib.sha256(("csrf:" + token).encode()).hexdigest()
