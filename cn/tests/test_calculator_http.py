"""Real HTTP checks for the authenticated Update35.2 interface adapter."""
import copy,json,unittest
import test_accounts_http as helpers
from test_ledger_http import LedgerHTTPTests
from cn_web.security import PERMISSIONS
from cn_web.http_app import AccountApp
from engine import compute

class CalculatorHTTPTests(unittest.TestCase):
    setUp=helpers.AccountHTTPTests.setUp
    stop=helpers.AccountHTTPTests.stop
    create=helpers.AccountHTTPTests.create
    user_browser=helpers.AccountHTTPTests.user_browser
    setup_book=LedgerHTTPTests.setup_book
    url=LedgerHTTPTests.url
    state=LedgerHTTPTests.state
    config=LedgerHTTPTests.config
    file=LedgerHTTPTests.file
    imported=LedgerHTTPTests.imported
    detail=LedgerHTTPTests.detail
    review=LedgerHTTPTests.review
    def calc(self,b,w,action,data=None):
        return b.request('/api/calculator/'+action,data,headers={'X-CN-Project':w['project'],'X-CN-Workbook':w['id']})
    def saved(self,b,w):
        code,r,_=self.calc(b,w,'state');self.assertEqual(code,200,r);return r
    def blank(self,w):
        return {'party':'Synthetic','location':'Town','state':'Gujarat','season':'2026 season 1','opening':'0','closing':'-50000','old_dues':'0','entries':[{'id':'receipt1','date':'2026-05-01','kind':'receipt','credit':'50000','debit':'0','items':[]}],'allocations':[],'cash_splits':[],'opening_sources':[],'status':'draft','revision':0,'ledger_confirmed':True,'workbook_id':w['id'],'annual_ledger':True,'manual_order':False}
    def save(self,b,w,r):
        code,out,_=self.calc(b,w,'save',r);self.assertEqual(code,200,out);return out
    def test_created_workbook_registers_owned_source_period(self):
        u,b=self.user_browser();p,w=self.setup_book(b)
        body={'name':'Rabi workbook','state':'Gujarat','period':'Rabi 2026',
              'start':'2026-10-01','end':'2027-02-28','cutoff':'2027-03-31','mode':'blank','source':w['id']}
        code,new,_=self.calc(b,w,'workbooks',body);self.assertEqual(code,200,new)
        new['project']=p['id']
        periods=self.state(b,new)['periods']
        self.assertEqual(periods,[{'name':body['period'],**{k:body[k] for k in ('start','end','cutoff')}}])
        self.assertEqual(self.state(b,w)['periods'],[])
        self.assertEqual(self.saved(b,new)['settings']['seasons'][0]['name'],body['period'])
        _,other=self.user_browser('other-user')
        self.assertEqual(other.request(self.url(new))[0],404)
        self.admin.request('/api/admin/users/'+u['id'],{'permissions':list(PERMISSIONS-{'edit_schemes'})},'PATCH')
        self.assertEqual(self.calc(b,w,'workbooks',body)[0],403)

    def test_assets_and_engine_parity(self):
        u,b=self.user_browser();p,w=self.setup_book(b)
        for path in ['/calculator','/app.js','/studio.js','/style.css','/studio.css','/web-session.js','/web-bridge.js','/ledger-panel.js','/cd-card-display.js','/cd-card-display.css']:
            self.assertEqual(b.request(path)[0],200,path)
        source=helpers.ROOT/'offline_baseline/static';target=helpers.ROOT/'backend/cn_web/calculator_static'
        for name in ['studio.css','style.css','payment-workbench.js','scheme-options.js','polish.js']:
            self.assertEqual((source/name).read_bytes(),(target/name).read_bytes(),name)
        # studio.js camera pan and ui-theme.js login default are intentional UI-only changes.
        r=self.save(b,w,self.blank(w));cfg=self.saved(b,w)['settings'];code,result,_=self.calc(b,w,'calculate',r);self.assertEqual(code,200,result)
        self.assertEqual(json.loads(json.dumps(compute(r,cfg),default=str)),result)
        self.assertEqual(self.calc(b,w,'calculate',dict(r,status='issued',result={'new_CN_total':'999'}))[0],400)
    def test_ownership_revocation_and_save_bypasses(self):
        u,a=self.user_browser();p,w=self.setup_book(a);r=self.save(a,w,self.blank(w));v,b=self.user_browser('user-b');p2,w2=self.setup_book(b)
        self.assertEqual(self.calc(b,w,'state')[0],404);self.assertEqual(self.calc(self.admin,w,'state')[0],404);self.assertEqual(self.calc(b,w2,'save',r)[0],404)
        self.assertEqual(a.request('/api/calculator/save',r,headers={'X-CN-Project':p['id'],'X-CN-Workbook':w['id'],'X-CSRF-Token':''})[0],403)
        self.admin.request('/api/admin/users/'+u['id'],{'permissions':list(PERMISSIONS-{'allocate_payments','edit_schemes'})},'PATCH')
        changed=copy.deepcopy(r);changed['allocations']=[{'id':'a','source':'receipt1','type':'Settlement','amount':'1','scheme':'','product':''}]
        self.assertEqual(self.calc(a,w,'save',changed)[0],403)
        for action,body in [('settings',self.saved(a,w)['settings']),('restore',{}),('project-import',{}),('cash-quantity-apply',{'record':r,'deduction_rate':'5'})]:self.assertEqual(self.calc(a,w,action,body)[0],403,action)
        changed=copy.deepcopy(r);changed['entries'][0]['date']='2026-01-15';self.assertEqual(self.calc(a,w,'save',changed)[0],400)
        self.assertEqual(self.saved(a,w)['records'][0],r)
        a.request('/api/auth/logout-all',{});self.assertEqual(self.calc(a,w,'state')[0],401)
    def test_preview_cancel_clear_and_stale_apply(self):
        u,b=self.user_browser();p,w=self.setup_book(b);r=self.blank(w);r['allocations']=[{'id':'a','type':'Settlement','source':'receipt1','scheme':'','product':'','amount':'100'}];r=self.save(b,w,r);before=self.saved(b,w)
        payload={'id':r['id'],'revision':r['revision'],'scope':'all'};code,plan,_=self.calc(b,w,'allocation-clear-preview',payload);self.assertEqual(code,200,plan);self.assertEqual(self.saved(b,w),before)
        self.assertEqual(self.calc(b,w,'allocation-clear-apply',{**payload,'expected':'wrong'})[0],400)
        code,out,_=self.calc(b,w,'allocation-clear-apply',{**payload,'expected':plan['expected']});self.assertEqual(code,200,out);self.assertEqual(out['allocations'],[]);self.assertEqual(out['entries'],r['entries'])
        self.assertEqual(self.calc(b,w,'allocation-clear-apply',{**payload,'expected':plan['expected']})[0],400)
        self.assertEqual(self.calc(b,w,'save',r)[0],400)
    def test_layout_restart_and_user_isolation(self):
        u,b=self.user_browser();p,w=self.setup_book(b);r=self.save(b,w,self.blank(w));layout={'positions':[{'key':'crop:Maize','x':32,'y':-49}],'locked':True}
        for suffix in ['','::classic']:
            code,out,_=self.calc(b,w,'ui-preferences',{'record_id':r['id']+suffix,'theme':'studio' if not suffix else 'classic','layout':layout});self.assertEqual(code,200,out)
        self.server.set_app(AccountApp(self.accounts,origin=self.origin,development=True))
        for suffix in ['','::classic']:
            code,out,_=b.request('/api/calculator/ui-preferences',headers={'X-CN-Project':p['id'],'X-CN-Workbook':w['id'],'X-CN-Record':r['id']+suffix});self.assertEqual(code,200,out);self.assertEqual(out['layout'],layout)
        v,c=self.user_browser('user-b');p2,w2=self.setup_book(c);self.assertEqual(self.calc(c,w2,'ui-preferences',{'record_id':r['id'],'layout':layout})[0],400)
        bad=copy.deepcopy(layout);bad['positions'][0]['x']=True;self.assertEqual(self.calc(b,w,'ui-preferences',{'record_id':r['id'],'layout':bad})[0],400)
    def mapped_source(self,b,w):
        self.config(b,w);lid=self.imported(b,w);original=self.detail(b,w,lid)['ledger']['document']
        for i,e in enumerate(original['entries']):
            for j,item in enumerate(e.get('items',[])):
                pid='dawat3' if '3 kg' in item['name'] else 'dawat1';code,r,_=b.request(self.url(w,'mapping'),{'revision':self.state(b,w)['revision'],'ledger_id':lid,'entry_index':i,'item_index':j,'product_id':pid});self.assertEqual(code,200,r)
        ids={e['reference']:i for i,e in enumerate(original['entries'])}
        for ref,review in [('CNK1',{'kind':'posted_cn','season':'Kharif','cn_class':'scheme','crop':'Paddy','reason':'Late Kharif CN'}),('JF1',{'kind':'posted_cn','cn_class':'freight','reason':'Freight journal'}),('RT2',{'kind':'return','season':'Kharif','reason':'Kharif return'}),('IPT1',{'kind':'ipt_out','season':'Kharif','reason':'Kharif transfer'})]:self.assertEqual(self.review(b,w,lid,ids[ref],review)[0],200)
        return lid,original
    def test_phase4_season_projection_dates_and_staleness(self):
        u,b=self.user_browser();p,w=self.setup_book(b);lid,original=self.mapped_source(b,w);dates=[e['date'] for e in original['entries']];records={}
        for season in ['Kharif','Rabi']:
            code,r,_=self.calc(b,w,'open-source',{'ledger_id':lid,'season':season,'revision':self.state(b,w)['revision']});self.assertEqual(code,200,r);records[season]=r;self.assertEqual([e['date'] for e in r['entries']],dates)
            code,result,_=self.calc(b,w,'calculate',r);self.assertEqual(code,200,result);summary=b.request(self.url(w,'summary'),{'ledger_id':lid,'season':season})[1]
            self.assertEqual({x['product_id']:float(x['net_sold']) for x in result['product_CNs']},{x['product_id']:float(x['net_sold_kg']) for x in summary['products']});self.assertEqual(result['ledger_closing'],'950.00')
        self.assertEqual(self.detail(b,w,lid)['ledger']['document'],original)
        r=copy.deepcopy(records['Rabi']);r['entries'][0]['date']='2001-01-01';self.assertEqual(self.calc(b,w,'save',r)[0],400)
        ei=next(i for i,e in enumerate(original['entries']) if e['reference']=='CNK1');self.assertEqual(self.review(b,w,lid,ei,{'kind':'posted_cn','season':'Kharif','cn_class':'scheme','crop':'Paddy','reason':'New review note'})[0],200)
        self.assertEqual(self.calc(b,w,'calculate',records['Kharif'])[0],409)
    def test_backup_independent_copy_and_scheme_permission(self):
        u,b=self.user_browser();p,w=self.setup_book(b);r=self.save(b,w,self.blank(w));self.calc(b,w,'ui-preferences',{'record_id':r['id']+'::classic','layout':{'positions':[{'key':'x','x':1,'y':2}],'locked':False}})
        code,backup,_=b.request('/api/projects/'+p['id']+'/export');self.assertEqual(code,200,backup);self.assertEqual(backup['version'],3)
        code,result,_=b.request('/api/projects/import',{'backup':backup});self.assertEqual(code,201,result);w2=next(x for x in b.request('/api/data/workbooks')[1]['items'] if x['project']==result['project_id']);r2=self.saved(b,w2)['records'][0];self.assertNotEqual(r2['id'],r['id']);self.assertEqual(r2['entries'],r['entries'])
        malicious=copy.deepcopy(backup);row=malicious['calculator_bundle'][0]['payload']['records'][0];obj=json.loads(row[2]);obj['status']='issued';row[2]=json.dumps(obj);count=len(b.request('/api/data/projects')[1]['items']);self.assertEqual(b.request('/api/projects/import',{'backup':malicious})[0],400);self.assertEqual(len(b.request('/api/data/projects')[1]['items']),count)
        self.admin.request('/api/admin/users/'+u['id'],{'permissions':list(PERMISSIONS-{'edit_schemes'})},'PATCH');self.assertEqual(b.request('/api/projects/import',{'backup':backup})[0],403)
    def test_source_backup_rebinds_provenance(self):
        u,b=self.user_browser();p,w=self.setup_book(b);lid,original=self.mapped_source(b,w);code,r,_=self.calc(b,w,'open-source',{'ledger_id':lid,'season':'Kharif','revision':self.state(b,w)['revision']});self.assertEqual(code,200,r)
        backup=b.request('/api/projects/'+p['id']+'/export')[1];code,result,_=b.request('/api/projects/import',{'backup':backup});self.assertEqual(code,201,result);w2=next(x for x in b.request('/api/data/workbooks')[1]['items'] if x['project']==result['project_id']);r2=self.saved(b,w2)['records'][0];code,result,_=self.calc(b,w2,'calculate',r2);self.assertEqual(code,200,result);self.assertNotEqual(r['web_source']['ledger_id'],r2['web_source']['ledger_id'])


    def configured_case(self,b,w,kind='cd'):
        import sys
        sys.path.append(str(helpers.ROOT/'offline_baseline/tests'))
        from test_allocation_review import maize
        from test_calculator import example
        if kind=='cd':r,cfg=maize(('4',),'50000')
        elif kind=='abs':r,cfg=example('scheme-4','100','0','30000',[]);r['allocations']=[]
        else:
            r,cfg=example('scheme-5','100','0','0',[])
            r['entries']=[e for e in r['entries'] if e['kind']!='receipt'];r['allocations']=[]
            r['entries'].append({'id':'cashreceipt','kind':'receipt','date':'2026-03-20','debit':'0','credit':'10000','reviewed':True})
            r['closing']='4000'
        code,out,_=self.calc(b,w,'settings',cfg);self.assertEqual(code,200,out)
        r.update(workbook_id=w['id'],annual_ledger=True,status='draft',revision=0)
        return self.save(b,w,r),out

    def test_cd_unused_release_and_nonzero_parity(self):
        u,b=self.user_browser();p,w=self.setup_book(b);r,cfg=self.configured_case(b,w)
        before=self.saved(b,w);payload={'id':r['id'],'revision':r['revision'],'operation':'cd-group','scheme':'scheme-4','source':'receipt0','amount':'50000'}
        code,plan,_=self.calc(b,w,'allocation-review-preview',payload);self.assertEqual(code,200,plan);self.assertGreater(float(plan['released']),48000);self.assertEqual(self.saved(b,w),before)
        code,saved,_=self.calc(b,w,'allocation-review-apply',{**payload,'expected':plan['expected']});self.assertEqual(code,200,saved);self.assertEqual(saved['entries'],r['entries'])
        code,result,_=self.calc(b,w,'calculate',saved);self.assertEqual(code,200,result);self.assertGreater(float(result['new_CN_total']),0);self.assertEqual(json.loads(json.dumps(compute(saved,cfg),default=str)),result)
        self.assertEqual(self.calc(b,w,'allocation-review-apply',{**payload,'expected':plan['expected']})[0],400)

    def test_abs_excess_and_july_rejection(self):
        u,b=self.user_browser();p,w=self.setup_book(b);r,cfg=self.configured_case(b,w,'abs')
        payload={'record':r,'crop':'Maize','scheme':'scheme-4','source':'advance','amount':'30000'}
        before=self.saved(b,w);code,plan,_=self.calc(b,w,'abs-distribution-preview',payload);self.assertEqual(code,200,plan);self.assertGreater(float(plan['ABS_CN']),0);self.assertGreater(float(plan['excess_ABS']),0);self.assertEqual(self.saved(b,w),before)
        code,out,_=self.calc(b,w,'abs-distribution-apply',{**payload,'settings_version':plan['settings_version']});self.assertEqual(code,200,out);self.assertEqual(out['entries'],r['entries'])
        code,result,_=self.calc(b,w,'calculate',out);self.assertEqual(code,200,result);self.assertEqual(json.loads(json.dumps(compute(out,cfg),default=str)),result)
        r2=copy.deepcopy(r);r2.pop('id');next(e for e in r2['entries'] if e['id']=='advance')['date']='2026-07-01';r2=self.save(b,w,r2)
        self.assertEqual(self.calc(b,w,'abs-distribution-preview',{**payload,'record':r2})[0],400)

    def test_cash_preview_apply_and_removal(self):
        u,b=self.user_browser();p,w=self.setup_book(b);r,cfg=self.configured_case(b,w,'cash')
        payload={'record':r,'scheme':'scheme-5','product':cfg['schemes'][4]['products'][0],'source':'cashreceipt','amount':'10000','supplied':'100','returned':'0'}
        before=self.saved(b,w);code,plan,_=self.calc(b,w,'cash-quantity-preview',payload);self.assertEqual(code,200,plan);self.assertEqual(self.saved(b,w),before)
        code,out,_=self.calc(b,w,'cash-quantity-apply',{**payload,'settings_version':plan['settings_version']});self.assertEqual(code,200,out);self.assertEqual(out['entries'],r['entries'])
        code,result,_=self.calc(b,w,'calculate',out);self.assertEqual(code,200,result);self.assertEqual(json.loads(json.dumps(compute(out,cfg),default=str)),result)
        removal={'record':out,'scheme':payload['scheme'],'product':payload['product']};code,plan,_=self.calc(b,w,'cash-remove-preview',removal);self.assertEqual(code,200,plan)
        code,out,_=self.calc(b,w,'cash-remove-apply',{**removal,'settings_version':plan['settings_version']});self.assertEqual(code,200,out);self.assertEqual(out['cash_splits'],[]);self.assertEqual(out['allocations'],[])


    def test_phase5_year_link_keeps_opening_cap_and_receipt_dates(self):
        u,b=self.user_browser();p,w=self.setup_book(b);self.config(b,w)
        old=self.imported(b,w,'prior_year.pdf');current=self.imported(b,w,'current_year.pdf')
        payload={'revision':self.state(b,w)['revision'],'previous_id':old,'current_id':current}
        code,preview,_=b.request(self.url(w,'year-preview'),payload);self.assertEqual(code,200,preview)
        receipt=preview['review']['receipts'][0]
        code,link,_=b.request(self.url(w,'year-apply'),{**payload,'confirmed':{receipt['id']:'10000'},'reason':'Original unspent receipt reviewed'});self.assertEqual(code,200,link)
        code,r,_=self.calc(b,w,'open-source',{'ledger_id':current,'season':'Kharif','revision':self.state(b,w)['revision']});self.assertEqual(code,200,r)
        self.assertEqual(sum(float(x['amount']) for x in r['opening_sources']),10000)
        self.assertEqual(r['opening_sources'][0]['date'],'2026-01-15')
        self.assertFalse(r['allocations'])
        code,out,_=self.calc(b,w,'calculate',r);self.assertEqual(code,200,out)
        opening=[x for x in out['sources'] if x['opening']];self.assertEqual(len(opening),1);self.assertEqual(opening[0]['date'],'2026-01-15')
        altered=copy.deepcopy(r);altered['opening_sources'][0]['amount']='20000';self.assertEqual(self.calc(b,w,'save',altered)[0],409)

del LedgerHTTPTests
