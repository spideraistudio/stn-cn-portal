"""Runs both real services on disposable local data. Start integration:mongo first."""
import copy
from datetime import datetime,timedelta,timezone
import json
import os
from pathlib import Path
import socket
import subprocess
import sys
import tempfile
import time
import uuid
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'cn'/'backend'),str(ROOT/'cn'/'tests')]
from cn_web.portal import PortalAccounts
from cn_web.security import PERMISSIONS
from test_accounts_http import Browser
from test_finish_http import FinishHTTPTests
from case_number_checks import exercise_case_numbers

PASSWORD='Synthetic integration password 2026!'
def port():
    with socket.socket() as s:s.bind(('127.0.0.1',0));return s.getsockname()[1]
def check(code,expected,body):
    assert code==expected,(code,expected,body)
def main():
    dbname='integration_e2e_'+uuid.uuid4().hex
    env={**os.environ,'MONGODB_URI':'mongodb://127.0.0.1:27017/'+dbname,'STN_MONGO_TLS':'0','NEXT_TELEMETRY_DISABLED':'1'}
    subprocess.run(['node',str(ROOT/'integration/seed_fixture.mjs')],env=env,cwd=ROOT,check=True)
    with tempfile.TemporaryDirectory(prefix='stn-cn-e2e-') as temp:
        data=Path(temp)/'cn';a=PortalAccounts(data);a.bootstrap('platform',PASSWORD,quota_bytes=1024**3)
        root=a.login('platform',PASSWORD,'synthetic')
        people=[]
        for i,name in enumerate(['buyer-admin','supplier-admin','third-admin'],1):
            c=a.company(root,{'name':'Synthetic company '+str(i),'cn':True,'stn':True})
            u=a.create_user(root,username=name,temporary_password=PASSWORD,permissions=sorted(PERMISSIONS),role='admin')
            a.access(root,{'user_id':u['id'],'company_id':c['id'],'cn':True,'stn':True,'stn_member_id':str(i).zfill(24)})
            people.append((u,c))
        public_port,identity_port,node_port=port(),port(),port();origin=f'http://127.0.0.1:{public_port}'
        log=open(ROOT/'verification'/os.environ.get('INTEGRATION_SERVER_LOG','full_stack_server.txt'),'w')
        command=[sys.executable,str(ROOT/'integration/run_local.py'),'--data',str(data),'--port',str(public_port),'--identity-port',str(identity_port),'--node-port',str(node_port),'--node-mode','start']
        server=subprocess.Popen(command,env=env,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT)
        def start_ready():
            for _ in range(90):
                try:
                    if Browser(origin).request('/api/health')[0]==200:return
                except Exception:pass
                if server.poll() is not None:raise RuntimeError('Gateway exited; inspect full_stack_server.txt')
                time.sleep(1)
            raise RuntimeError('STN startup timed out')
        try:
            start_ready()
            subprocess.run(['node',str(ROOT/'integration/browser_public.mjs')],cwd=ROOT,env={**env,'PUBLIC_BROWSER_INFO':json.dumps({'origin':origin,'admin_username':'platform','admin_password':PASSWORD})},check=True)
            admin=Browser(origin);admin.login('platform',PASSWORD)
            signup={'member_id':str(4).zfill(24),'username':'signup-company-admin','temporary_password':PASSWORD,'permissions':sorted(PERMISSIONS),'cn':True,'stn':True,'max_users':5,'quota_bytes':1024**3,'user_quota_bytes':250*1024**2}
            code,created,_=admin.request('/api/portal-stn/approve',signup);check(code,200,created)
            again=admin.request('/api/portal-stn/approve',signup);check(again[0],200,again[1]);assert again[1]['user_id']==created['user_id']
            sb=Browser(origin);sb.login(signup['username'],PASSWORD);assert sb.request('/api/me')[1]['user']['must_change_password']
            sb.request('/api/auth/password',{'current_password':PASSWORD,'new_password':PASSWORD+' signup'})
            sb.login(signup['username'],PASSWORD+' signup');assert sb.request('/api/portal/state')[1]['user']['modules']=={'cn':True,'stn':True}
            assert sb.request('/api/member/seed-browse')[0]==200
            print('PASS unified real signup approval creates one company/admin identity, modules and permissions; retry is idempotent; temporary password enforced',flush=True)
            clients=[]
            for name in ['buyer-admin','supplier-admin','third-admin']:
                b=Browser(origin);b.login(name,PASSWORD)
                check(b.request('/api/auth/password',{'current_password':PASSWORD,'new_password':PASSWORD+' changed'})[0],200,'password')
                b.login(name,PASSWORD+' changed');clients.append(b)
            buyer,supplier,third=clients
            check(admin.request('/api/portal-stn/link-check?id='+str(1).zfill(24))[0],200,'link lookup')
            code,bad,_=admin.request('/api/portal/access',{'user_id':people[0][0]['id'],'stn_member_id':'f'*24});check(code,400,bad)
            code,linked,_=admin.request('/api/portal/access',{'user_id':people[0][0]['id'],'stn_member_id':str(1).zfill(24)});check(code,200,linked)
            assert linked['linked_member']['company_name']=='Synthetic Company 1'
            buyer.login('buyer-admin',PASSWORD+' changed')
            assert buyer.request('/api/portal/state')[1]['user']['role']=='admin'
            assert buyer.request('/api/admin/cleanup',{})[0]==403
            assert buyer.request('/api/admin/credentials',{'memberId':str(1).zfill(24)})[0]==403
            assert buyer.request('/internal/portal/introspect',{})[0]==404
            assert buyer.request('/api/member-auth',{'loginId':'forged','password':PASSWORD})[0]==409
            assert buyer.request('/api/member/seed-browse',headers={'Cookie':'stn_member_session=forged'})[0]==403
            print('PASS shared login, forced password change, legacy-session bypass denial and company admin / platform separation',flush=True)
            code,staff,_=buyer.request('/api/admin/users',{'username':'buyer-staff','temporary_password':PASSWORD,'permissions':sorted(PERMISSIONS)});check(code,201,staff)
            staff_id=staff['user']['id']
            code,grant,_=buyer.request('/api/portal/access',{'user_id':staff_id,'cn':True,'stn':True,'stn_member_id':str(1).zfill(24)});check(code,200,grant)
            staff_browser=Browser(origin);staff_browser.login('buyer-staff',PASSWORD)
            staff_browser.request('/api/auth/password',{'current_password':PASSWORD,'new_password':PASSWORD+' staff'})
            staff_browser.login('buyer-staff',PASSWORD+' staff')
            check(staff_browser.request('/api/member/seed-requests')[0],200,'explicit staff STN grant')
            code,conflict,_=admin.request('/api/portal/access',{'user_id':people[2][0]['id'],'stn_member_id':str(1).zfill(24)});check(code,409,conflict)
            print('PASS individual staff login, explicit delegated company STN grant, preserved company boundaries and no automatic account merge',flush=True)
            now=datetime.now(timezone.utc);delivery=(now+timedelta(days=15)).date().isoformat();deadline=(now+timedelta(days=5)).strftime('%Y-%m-%dT%H:%M')
            payload={'crop':'Maize','segment':'Hybrid','description':'Synthetic maize seed requirement','varietyType':'hybrid','productMatch':'equivalent','quantity':100,'quantityUnit':'kg','partialAllowed':True,'cleaning':'either','treatment':'either','germinationRequired':True,'gotRequired':False,'deliveryState':'Gujarat','deliveryDistrict':'Ahmadabad','destination':'Synthetic warehouse','deliveryBy':delivery,'transport':'included','paymentTerms':'Cash','quotationDeadline':deadline,'anonymous':True,'panIndia':False,'supplierStates':['Gujarat']}
            code,r,_=buyer.request('/api/member/seed-requests',payload);check(code,201,r);rid=r['request']['id']
            listing=supplier.request('/api/member/seed-browse')[1]['requests'];req=next(x for x in listing if x['id']==rid)
            assert 'ownerId' not in req and req['ownerCompany']=='Anonymous buyer'
            assert not any(x['id']==rid for x in third.request('/api/member/seed-browse')[1]['requests'])
            quote={'offeredProduct':'Synthetic maize','crop':'Maize','segment':'Hybrid','varietyType':'hybrid','quantity':80,'quantityUnit':'kg','price':100,'priceUnit':'kg','cleaning':'clean','treatment':'treated','earliestDelivery':delivery,'transportIncluded':True,'pricingBasis':'Delivered Ahmedabad','paymentType':'cash','germinationAvailable':True,'gotAvailable':False,'validUntil':(now+timedelta(days=4)).date().isoformat()}
            assert buyer.request('/api/member/seed-quotes/'+rid,quote)[0]==403
            code,q,_=supplier.request('/api/member/seed-quotes/'+rid,quote);check(code,201,q);qid=q['quotation']['id']
            code,out,_=buyer.request('/api/member/seed-quotes/'+rid+'/buyer',{'quotationId':qid,'type':'status','value':'selected'},'PATCH');check(code,200,out)
            assert out['quotation'].get('supplierContact')
            own=supplier.request('/api/member/seed-quotes/'+rid)[1]['quotation'];assert own.get('buyerContact')
            code,out,_=buyer.request('/api/member/seed-requests/'+rid,{'action':'closed'},'PATCH');check(code,200,out)
            assert supplier.request('/api/member/seed-quote-history')[0]==200
            print('PASS STN real MongoDB seed request, state scope, anonymous buyer, self-quote denial, quotation, approval/contact exchange and history',flush=True)
            # Seller reports use the original form and review pipeline.
            report={'requestId':str(uuid.uuid4()),'gstin':'24ABCDE1234F1Z5','firmName':'Synthetic Seller','taluka':'Ahmedabad','district':'Ahmadabad','state':'Gujarat','pincode':'380001','rating':8,'dispute':False,'amount':'','disputeType':'payment_default','disputeOther':'','disputeStartMonth':'','disputeEndMonth':'','disputeOngoing':False,'legal':False,'caseNumber':'','summary':'Synthetic business experience for integration regression only.'}
            case_report_id=exercise_case_numbers(buyer,supplier,third,admin,report)
            case=FinishHTTPTests();source_project,source_book=case.setup_book(buyer)
            lid,original=case.mapped_source(buyer,source_book)
            source_cfg=case.saved(buyer,source_book)['settings']
            for scheme in source_cfg['schemes']:
                scheme.update(confirmed=True,states=['Gujarat'],unit='kg',billing='100',billing_unit='kg',benefits=['Quantity'],quantity=[{'above':'0','upto':None,'rate':'1','name':'Test quantity'}])
            check(case.calc(buyer,source_book,'settings',source_cfg)[0],200,'source schemes')
            code,sr,_=case.calc(buyer,source_book,'open-source',{'ledger_id':lid,'season':'Kharif','revision':case.state(buyer,source_book)['revision']});check(code,200,sr)
            sr.update(state='Gujarat',ledger_confirmed=True)
            sr['allocations']=[{'id':'settlement-'+e['id'],'source':e['id'],'type':'Settlement','scheme':source_cfg['schemes'][0]['id'],'product':'','amount':e['credit']} for e in sr['entries'] if e['kind']=='receipt']
            code,sr,_=case.calc(buyer,source_book,'save',sr);check(code,200,sr)
            sf=case.finish(buyer,source_book,sr)
            assert [e['date'] for e in sf['entries']]==[e['date'] for e in original['entries']]
            assert case.calc(buyer,source_book,'report',{})[0]==200
            print('PASS complete source-PDF import → mapping → scheme assignment → receipt settlement → finalisation → reporting, with original dates and late Kharif classification',flush=True)
            p,w=case.setup_book(buyer);r,cfg,result=case.case(buyer,w);frozen=case.finish(buyer,w,r,True)
            assert result['new_CN_total']=='38561',result['new_CN_total']
            assert case.calc(staff_browser,w,'record',{'id':frozen['id']})[0]==404
            assert case.calc(supplier,w,'record',{'id':frozen['id']})[0]==404
            assert case.calc(admin,w,'record',{'id':frozen['id']})[0]==404
            assert case.calc(buyer,w,'report',{})[0]==200
            assert case.calc(buyer,w,'product-csv',{'record':frozen})[0]==200
            backup=buyer.request('/api/projects/'+p['id']+'/export')[1]
            code,imported,_=supplier.request('/api/projects/import',{'backup':backup});check(code,201,imported);assert imported['project_id']!=p['id'],imported
            changed=copy.deepcopy(cfg);changed['schemes'][2]['extra'][1]['rate']='26000';assert case.calc(buyer,w,'settings',changed)[0]==200
            assert case.calc(buyer,w,'record',{'id':frozen['id']})[1]['result']==result
            cn_before=buyer.request('/api/workspace')[1]['used_bytes']
            storage=buyer.request('/api/portal-stn/storage')[1];assert storage['cn_allowance_deducted']==0 and storage['logical_bson_bytes']>0,storage
            assert buyer.request('/api/workspace')[1]['used_bytes']==cn_before
            print('PASS CN PDF import, original evidence, exact ₹38,561 result, finalise/issue, reports/CSV, frozen history, individual isolation including platform admin, independent export/import and separate STN accounting',flush=True)
            # Browser checks use the same gateway and actual STN/CN services.
            info={'origin':origin,'username':'buyer-admin','password':PASSWORD+' changed','project':p['id'],'workbook':w['id'],'admin_username':'platform','admin_password':PASSWORD,'case_report_id':case_report_id}
            subprocess.run(['node',str(ROOT/'integration/browser_case_numbers.cjs')],cwd=ROOT,env={**env,'INTEGRATION_BROWSER_INFO':json.dumps(info)},check=True)
            subprocess.run(['node',str(ROOT/'integration/browser_combined.cjs')],cwd=ROOT,env={**env,'INTEGRATION_BROWSER_INFO':json.dumps(info)},check=True)
            code,out,_=admin.request('/api/portal/access',{'user_id':people[0][0]['id'],'stn':False});check(code,200,out)
            assert buyer.request('/api/member/seed-browse')[0]==403
            for path in ['/api/member/seed-requests','/api/member/seed-quote-history','/api/notifications','/api/portal-stn/storage']:
                assert buyer.request(path)[0] in (401,403),path
            for path in ['/api/reports','/api/seller-search','/api/profile-change','/api/account-deletion','/api/pilot-issues']:
                assert buyer.request(path,{})[0] in (401,403),path
            buyer.login('buyer-admin',PASSWORD+' changed');assert buyer.request('/api/workspace')[0]==200 and buyer.request('/api/member/seed-browse')[0]==403
            admin.request('/api/portal/access',{'user_id':people[0][0]['id'],'stn':True,'cn':False})
            buyer.login('buyer-admin',PASSWORD+' changed');assert buyer.request('/api/workspace')[0]==403 and buyer.request('/api/member/seed-browse')[0]==200
            admin.request('/api/portal/access',{'user_id':people[0][0]['id'],'cn':True})
            buyer.login('buyer-admin',PASSWORD+' changed')
            # Real gateway and Node restart, same files and sessions.
            server.terminate();server.wait(timeout=25);server=subprocess.Popen(command,env=env,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT);start_ready()
            assert case.calc(buyer,w,'record',{'id':frozen['id']})[1]['result']==result
            assert supplier.request('/api/member/seed-quote-history')[0]==200
            admin.request('/api/admin/users/'+people[0][0]['id']+'/reset-password',{'temporary_password':PASSWORD+' reset'})
            assert buyer.request('/api/workspace')[0]==401 and buyer.request('/api/member/seed-browse')[0]==403
            buyer.login('buyer-admin',PASSWORD+' reset');assert buyer.request('/api/member/seed-browse')[0]==403
            check(buyer.request('/api/auth/password',{'current_password':PASSWORD+' reset','new_password':PASSWORD+' final'})[0],200,'change')
            buyer.login('buyer-admin',PASSWORD+' final');assert buyer.request('/api/member/seed-browse')[0]==200
            buyer.request('/api/auth/logout',{});assert buyer.request('/api/workspace')[0]==401 and buyer.request('/api/member/seed-browse')[0]==403
            print('PASS independent module disable/immediate revocation, full service restart/reopening, scoped reset/forced change and shared logout',flush=True)
        finally:
            server.terminate()
            try:server.wait(timeout=25)
            except subprocess.TimeoutExpired:server.kill()
            log.close()
    print('PASS full stack integration journey (Linux; Windows acceptance pending)',flush=True)
if __name__=='__main__':
    mongo=subprocess.Popen(['node',str(ROOT/'integration/mongo_local.mjs')],cwd=ROOT,env={**os.environ,'STN_DISPOSABLE_MONGO':'1'},stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True)
    try:
        for line in mongo.stdout:
            print(line,end='',flush=True)
            if 'MongoDB ready' in line:break
        if mongo.poll() is not None:raise RuntimeError('Disposable MongoDB failed')
        main()
    finally:
        mongo.terminate()
        try:mongo.wait(timeout=20)
        except subprocess.TimeoutExpired:mongo.kill()

