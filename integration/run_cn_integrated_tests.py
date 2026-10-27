"""Original financial/API regression tests through the combined account authority."""
from functools import partial
from pathlib import Path
import sys
import unittest
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'cn'/'backend'),str(ROOT/'cn'/'tests')]
from cn_web.portal import PortalAccounts
from cn_web.portal_http import PortalApp
import test_accounts_http as helpers
helpers.Accounts=PortalAccounts
helpers.AccountApp=partial(PortalApp,bridge_key='integration-test-secret-'*3)
suite=unittest.TestSuite()
for name in ['test_workspaces_http','test_ledger_http','test_product_mapping_http','test_calculator_http','test_native_interface_http','test_finish_http','test_storage_http','test_billing_http','test_audit_mapping_http','test_hierarchy_http']:
    module=__import__(name)
    module.Accounts=PortalAccounts
    module.AccountApp=helpers.AccountApp
    suite.addTests(unittest.defaultTestLoader.loadTestsFromModule(module))
result=unittest.TextTestRunner(verbosity=1).run(suite)
raise SystemExit(not result.wasSuccessful())
