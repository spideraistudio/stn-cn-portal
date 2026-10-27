"""Production WSGI factory. TLS termination/trusted proxy setup belongs to Phase 8."""
import os
from .accounts import Accounts
from .http_app import AccountApp


def create_app():
    # Explicit settings only; development cookie mode cannot be enabled here.
    return AccountApp(Accounts(os.environ['CN_WEB_DATA']), origin=os.environ['CN_WEB_ORIGIN'])
