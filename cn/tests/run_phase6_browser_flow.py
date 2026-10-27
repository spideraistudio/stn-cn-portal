"""Native Chromium import/reopen regression on temporary, synthetic owned data.

Requires Node Playwright and a Chromium executable (CN_BROWSER_EXECUTABLE), or
Playwright's installed browser. No real WEB/offline user data is opened.
"""
import json
import os
from pathlib import Path
import subprocess
import sys
import threading
from wsgiref.simple_server import make_server

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tests'))
from test_finish_http import FinishHTTPTests
from cn_web.accounts import Accounts
from cn_web.http_app import AccountApp
from cn_web.cli import QuietHandler


def main():
    case = FinishHTTPTests()
    case.setUp()
    try:
        _, browser = case.user_browser()
        project, workbook = case.setup_book(browser)
        info = {'origin': case.origin, 'token': browser.token,
                'project': project['id'], 'workbook': workbook['id']}
        if os.environ.get('CN_BROWSER_CASE')=='cd-cards':
            sys.path.append(str(ROOT/'offline_baseline/tests'))
            from test_allocation_review import maize
            for label,quantities,amount in [('multiple',('800','32','60'),'100000'),('capped',('4',),'50000')]:
                record,cfg=maize(quantities,amount)
                if label=='multiple':
                    code,out,_=case.calc(browser,workbook,'settings',cfg);assert code==200,out
                record.update(workbook_id=workbook['id'],annual_ledger=True,status='draft',revision=0,party='CD cards '+label)
                code,out,_=case.calc(browser,workbook,'save',record);assert code==200,out
                info[label]=out['id']
        else:
            case.config(browser, workbook)
        child = subprocess.Popen(
            ['node', str(ROOT / 'tests' / os.environ.get('CN_BROWSER_TEST','browser_phase63_offline.cjs'))],
            env={**os.environ, 'CN_FLOW_INFO': json.dumps(info)},
            cwd=ROOT, text=True, stdin=subprocess.PIPE,
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        try:
            for line in child.stdout:
                if line.strip() == 'CN_TEST_RESTART_SERVER':
                    port = case.server.server_port
                    case.stop()
                    case.accounts = Accounts(case.tmp.name, clock=lambda: case.now[0])
                    case.app = AccountApp(case.accounts, origin=case.origin, development=True)
                    case.server = make_server('127.0.0.1', port, case.app, handler_class=QuietHandler)
                    case.thread = threading.Thread(target=case.server.serve_forever,
                                                   kwargs={'poll_interval': .01}, daemon=True)
                    case.thread.start()
                    child.stdin.write('server restarted\n')
                    child.stdin.flush()
                else:
                    print(line, end='', flush=True)
            if child.wait(timeout=10):
                raise RuntimeError('Native browser regression failed')
        finally:
            if child.poll() is None:
                child.terminate()
                child.wait(timeout=10)
    finally:
        case.doCleanups()


if __name__ == '__main__':
    main()
