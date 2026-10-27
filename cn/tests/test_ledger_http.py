"""Real owned HTTP adapters with fixed synthetic PDFs and preserved real fixtures."""
import base64
import copy
from decimal import Decimal
from pathlib import Path
import unittest
from unittest.mock import patch
import test_accounts_http as helpers
from cn_web.accounts import Accounts
from cn_web.http_app import AccountApp

FIXTURES=Path(__file__).parent/'fixtures'
CATALOGUE=[{'id':'dawat1','name':'DAWAT 1 kg','crop':'Paddy','segment':'Hybrid 1 kg','packing_kg':'1','aliases':[]},
           {'id':'dawat3','name':'DAWAT 3 kg','crop':'Paddy','segment':'Hybrid 3 kg','packing_kg':'3','aliases':[]}]
PERIODS=[{'name':'Kharif','start':'2026-04-01','end':'2026-08-31','cutoff':'2026-11-15'},
         {'name':'Rabi','start':'2026-10-01','end':'2027-02-28','cutoff':'2027-03-31'}]

class LedgerHTTPTests(unittest.TestCase):
    setUp=helpers.AccountHTTPTests.setUp
    stop=helpers.AccountHTTPTests.stop
    create=helpers.AccountHTTPTests.create
    user_browser=helpers.AccountHTTPTests.user_browser

    def setup_book(self,browser):
        code,p,_=browser.request('/api/data/projects',{'data':{'name':'Project'}});self.assertEqual(code,201,p)
        code,w,_=browser.request('/api/data/workbooks',{'data':{'name':'Gujarat'},'project':p['id']});self.assertEqual(code,201,w)
        return p,w

    def url(self,w,action=''):
        return '/api/ledger/workbooks/'+w['id']+('/'+action if action else '')

    def state(self,b,w):
        code,r,_=b.request(self.url(w));self.assertEqual(code,200,r);return r

    def config(self,b,w):
        code,r,_=b.request(self.url(w,'config'),{'revision':self.state(b,w)['revision'],'catalogue':CATALOGUE,'periods':PERIODS},'PUT')
        self.assertEqual(code,200,r)

    def file(self,name):
        return {'name':name,'content_base64':base64.b64encode((FIXTURES/name).read_bytes()).decode()}

    def imported(self,b,w,name='two_seasons.pdf',apply=True):
        payload={'revision':self.state(b,w)['revision'],'files':[self.file(name)]}
        code,p,_=b.request(self.url(w,'preview-import'),payload);self.assertEqual(code,200,p)
        if not apply:return p,payload
        code,result,_=b.request(self.url(w,'apply-import'),{**payload,'preview_digest':p['preview_digest']});self.assertEqual(code,200,result)
        return result['results'][0]['id']

    def detail(self,b,w,lid):
        status,r,_=b.request(self.url(w,'ledgers/'+lid));self.assertEqual(status,200,r);return r

    def review(self,b,w,lid,ei,review):
        return b.request(self.url(w,'review'),{'revision':self.state(b,w)['revision'],'ledger_id':lid,'entry_index':ei,'review':review})

    def test_late_kharif_cn_return_ipt_and_original_receipts(self):
        ua,a=self.user_browser();p,w=self.setup_book(a);self.config(a,w);lid=self.imported(a,w)
        original=self.detail(a,w,lid)['ledger']['document']
        for i,e in enumerate(original['entries']):
            for j,item in enumerate(e.get('items',[])):
                pid='dawat3' if '3 kg' in item['name'] else 'dawat1'
                code,r,_=a.request(self.url(w,'mapping'),{'revision':self.state(a,w)['revision'],'ledger_id':lid,'entry_index':i,'item_index':j,'product_id':pid})
                self.assertEqual(code,200,r)
        ids={e['reference']:i for i,e in enumerate(original['entries'])}
        for ref,r in [('CNK1',{'kind':'posted_cn','season':'Kharif','cn_class':'scheme','crop':'Paddy','reason':'Late Kharif benefit CN'}),
                      ('JF1',{'kind':'posted_cn','season':'Rabi','cn_class':'freight','reason':'Journal freight'}),
                      ('RT2',{'kind':'return','season':'Kharif','reason':'Return belongs to Kharif supply'}),
                      ('IPT1',{'kind':'ipt_out','season':'Kharif','reason':'Late IPT matched to Kharif stock'})]:
            code,r,_=self.review(a,w,lid,ids[ref],r);self.assertEqual(code,200,r)
        results={}
        for season in ['Kharif','Rabi']:
            code,out,_=a.request(self.url(w,'summary'),{'ledger_id':lid,'season':season});self.assertEqual(code,200,out)
            results[season]=out
        kh={r['product_id']:r for r in results['Kharif']['products']};ra=results['Rabi']['products']
        self.assertEqual(Decimal(kh['dawat1']['net_sold']),Decimal(4)) # 10 - 2 - 1 - 3
        self.assertEqual(Decimal(kh['dawat3']['net_sold']),Decimal(5))
        self.assertEqual(Decimal(ra[0]['net_sold']),Decimal(7))
        self.assertEqual(sum(Decimal(r['ipt_out']) for r in ra),0)
        cn=next(c for c in results['Rabi']['posted_CNs'] if c['entry_index']==ids['CNK1'])
        self.assertFalse(cn['included_in_selected_season']);self.assertEqual(cn['date'],'2026-11-05')
        self.assertEqual(results['Rabi']['closing'],'950.00')
        self.assertEqual([r['original_date'] for r in results['Rabi']['receipts']],['2026-06-01','2026-11-09'])
        self.assertEqual(self.detail(a,w,lid)['ledger']['document'],original)
        code,_,_=self.review(a,w,lid,ids['R1'],{'season':'Kharif','reason':'Cannot move receipt'})
        self.assertEqual(code,400)
        # Moving cutoff earlier is a conflicting saved-period change.
        changed=copy.deepcopy(PERIODS);changed[0]['cutoff']='2026-10-01'
        self.assertEqual(a.request(self.url(w,'config'),{'revision':self.state(a,w)['revision'],'periods':changed},'PUT')[0],409)

    def test_preview_cancel_repeat_failed_batch_and_changed_source(self):
        ua,a=self.user_browser();p,w=self.setup_book(a);self.config(a,w)
        preview,payload=self.imported(a,w,apply=False)
        self.assertFalse(self.state(a,w)['ledgers']);self.assertEqual(a.request('/api/data/files')[1]['items'],[])
        broken={**payload,'files':payload['files']+[{'name':'broken.pdf','content_base64':base64.b64encode(b'%PDF-broken').decode()}]}
        self.assertEqual(a.request(self.url(w,'preview-import'),broken)[0],400)
        self.assertFalse(self.state(a,w)['ledgers'])
        lid=self.imported(a,w)
        again=self.imported(a,w);self.assertEqual(again,lid);self.assertEqual(len(self.state(a,w)['ledgers']),1)
        preview,payload=self.imported(a,w,'two_seasons_changed.pdf',False)
        self.assertEqual(preview['results'][0]['status'],'Review replacement')
        code,r,_=a.request(self.url(w,'apply-import'),{**payload,'preview_digest':preview['preview_digest']});self.assertEqual(code,409,r)
        code,r,_=a.request(self.url(w,'apply-import'),{**payload,'preview_digest':preview['preview_digest'],'replacements':{'0:0':lid},'reason':'Reviewed changed statement'})
        self.assertEqual(code,200,r);self.assertEqual(len(self.state(a,w)['ledgers']),2)
        self.assertIsNotNone(self.detail(a,w,lid)['ledger']['superseded_by'])
        stale=a.request(self.url(w,'apply-import'),{**payload,'preview_digest':preview['preview_digest'],'replacements':{'0:0':lid},'reason':'stale'})
        self.assertEqual(stale[0],409)

    def test_year_link_credit_cap_and_dates(self):
        ua,a=self.user_browser();p,w=self.setup_book(a)
        old=self.imported(a,w,'prior_year.pdf');current=self.imported(a,w,'current_year.pdf')
        payload={'revision':self.state(a,w)['revision'],'previous_id':old,'current_id':current}
        code,result,_=a.request(self.url(w,'year-preview'),payload);self.assertEqual(code,200,result)
        receipt=result['review']['receipts'][0]
        self.assertEqual(receipt['date'],'2026-01-15')
        self.assertEqual(Decimal(result['review']['maximum_opening_credit']),10000)
        self.assertEqual(a.request(self.url(w,'year-apply'),{**payload,'confirmed':{receipt['id']:'10001'},'reason':'reviewed'})[0],400)
        code,r,_=a.request(self.url(w,'year-apply'),{**payload,'confirmed':{receipt['id']:'6000'},'reason':'Original remaining credit verified'})
        self.assertEqual(code,200,r);self.assertEqual(r['opening_sources'][0]['date'],'2026-01-15');self.assertEqual(r['opening_sources'][0]['amount'],'6000')
        self.assertFalse(self.state(a,w)['year_links'][current]['stale'])

    def test_ownership_permissions_reauthorization_and_file_protection(self):
        ua,a=self.user_browser();ub,b=self.user_browser('other-user');p,w=self.setup_book(a);self.config(a,w);lid=self.imported(a,w)
        self.assertEqual(b.request(self.url(w))[0],404)
        self.assertEqual(self.admin.request(self.url(w,'ledgers/'+lid))[0],404)
        for action,body in [('audit',{'start':'2026-04-01','end':'2027-03-31'}),('summary',{'ledger_id':lid,'season':'Rabi'}),('year-preview',{'revision':2,'previous_id':lid,'current_id':lid}),('reread',{'revision':2,'ledger_id':lid}),('mapping',{'revision':2,'ledger_id':lid,'entry_index':0,'item_index':0,'product_id':'dawat1'})]:
            self.assertEqual(b.request(self.url(w,action),body)[0],404)
        row=self.detail(a,w,lid)['ledger']
        f=a.request('/api/data/files/'+row['file_id'])[1]
        self.assertEqual(a.request('/api/data/files/'+row['file_id'],{'revision':f['revision'],'data':{'name':'changed','content_base64':'AA=='}},'PATCH')[0],409)
        self.assertEqual(a.request('/api/data/parties/'+row['party_id'],{'revision':1},'DELETE')[0],409)
        self.admin.request('/api/admin/users/'+ua['id'],{'permissions':['view_workspace','edit_ledger','import_statements']},'PATCH')
        self.assertEqual(a.request(self.url(w,'config'),{'revision':self.state(a,w)['revision'],'catalogue':CATALOGUE},'PUT')[0],403)
        payload={'revision':self.state(a,w)['revision'],'files':[self.file('prior_year.pdf')]}
        preview=a.request(self.url(w,'preview-import'),payload)[1]
        # Revocation during parsing is checked again inside the commit boundary.
        actual=self.app.ledger.parse
        def revoked(raw,state):
            parsed=actual(raw,state)
            self.accounts.update_user(self.admin.token,ua['id'],{'enabled':False})
            return parsed
        with patch.object(self.app.ledger,'parse',side_effect=revoked):
            self.assertEqual(a.request(self.url(w,'apply-import'),{**payload,'preview_digest':preview['preview_digest']})[0],401)

    def test_audit_category_review_and_backup_roundtrip(self):
        ua,a=self.user_browser();ub,b=self.user_browser('receiver');p,w=self.setup_book(a);self.config(a,w);lid=self.imported(a,w,'duplicate_receipts.pdf')
        query={'start':'2026-04-01','end':'2027-03-31'}
        code,audit,_=a.request(self.url(w,'audit'),query);self.assertEqual(code,200,audit)
        finding=audit['findings'][0];self.assertEqual(finding['type'],'Duplicate payment reference')
        code,r,_=a.request(self.url(w,'audit-review'),{**query,'revision':audit['revision'],'review_id':finding['review_id'],'reason':'Bank reviewed independently'});self.assertEqual(code,200,r)
        self.assertEqual(a.request(self.url(w,'audit'),query)[1]['findings'][0]['review']['status'],'not_applicable')
        backup=a.request('/api/projects/'+p['id']+'/export')[1];self.assertEqual(backup['version'],2)
        code,r,_=b.request('/api/projects/import',{'backup':backup});self.assertEqual(code,201,r)
        nw=next(wr for wr in b.request('/api/data/workbooks')[1]['items'] if wr['project']==r['project_id'])
        state=self.state(b,nw);self.assertEqual(len(state['ledgers']),1);self.assertNotEqual(state['ledgers'][0]['id'],lid)
        detail=self.detail(b,nw,state['ledgers'][0]['id']);self.assertEqual(detail['ledger']['document']['entries'][0]['original']['date'],'2026-05-01')
        bad=copy.deepcopy(backup);bad['ledger_bundle'][0]['state']['ledgers'][0]['document']['entries'][0]['date']='2020-01-01'
        before=b.request('/api/data/projects')[1];self.assertEqual(b.request('/api/projects/import',{'backup':bad})[0],400);self.assertEqual(before,b.request('/api/data/projects')[1])
        self.admin.request('/api/admin/users/'+ub['id'],{'permissions':['view_workspace','import_statements','edit_ledger']},'PATCH')
        self.assertEqual(b.request('/api/projects/import',{'backup':backup})[0],403)

    def test_combined_pdf_all_49_parties(self):
        ua,a=self.user_browser();p,w=self.setup_book(a)
        raw=(Path(__file__).resolve().parents[1]/'offline_baseline/fixtures/surendranagar_combined.pdf').read_bytes()
        payload={'revision':0,'files':[{'name':'combined.pdf','content_base64':base64.b64encode(raw).decode()}]}
        code,preview,_=a.request(self.url(w,'preview-import'),payload);self.assertEqual(code,200,preview)
        self.assertEqual(len(preview['results']),49)
        code,r,_=a.request(self.url(w,'apply-import'),{**payload,'preview_digest':preview['preview_digest']});self.assertEqual(code,200,r)
        self.assertEqual(len(r['results']),49)
        self.assertEqual(sum(x['entries'] for x in self.state(a,w)['ledgers']),329)

    def test_strict_boundaries_packing_and_concurrent_apply(self):
        ua,a=self.user_browser();p,w=self.setup_book(a);self.config(a,w)
        preview,payload=self.imported(a,w,apply=False)
        # Two independent requests previewed against the same revision cannot both commit.
        first=a.request(self.url(w,'apply-import'),{**payload,'preview_digest':preview['preview_digest']})
        self.assertEqual(first[0],200)
        self.assertEqual(a.request(self.url(w,'apply-import'),{**payload,'preview_digest':preview['preview_digest']})[0],409)
        lid=first[1]['results'][0]['id'];doc=self.detail(a,w,lid)['ledger']['document']
        three=next(i for i,e in enumerate(doc['entries']) if any('3 kg' in it['name'] for it in e.get('items',[])))
        self.assertEqual(a.request(self.url(w,'mapping'),{'revision':self.state(a,w)['revision'],'ledger_id':lid,'entry_index':three,'item_index':0,'product_id':'dawat1'})[0],400)
        self.assertEqual(self.review(a,w,lid,0,{'reason':'tamper','date':'2020-01-01'})[0],400)
        self.assertEqual(a.request(self.url(w,'summary'),{'ledger_id':lid,'season':'Rabi','user_id':ua['id']})[0],400)
        self.assertEqual(a.request(self.url(w,'audit'),{'start':'2027-01-01','end':'2026-01-01'})[0],400)
        self.assertEqual(a.request(self.url(w,'config'),{'revision':self.state(a,w)['revision'],'catalogue':CATALOGUE},'PUT',headers={'X-CSRF-Token':''})[0],403)
        row=self.detail(a,w,lid)['ledger'];party=a.request('/api/data/parties/'+row['party_id'])[1]
        self.assertEqual(a.request('/api/data/parties/'+row['party_id'],{'revision':party['revision'],'data':{**party['data'],'hq':'Town HQ'}},'PATCH')[0],200)
        original_file=a.request('/api/data/files/'+row['file_id'])[1]
        self.assertEqual(a.request('/api/data/files/'+row['file_id'],{'revision':original_file['revision'],'data':{**original_file['data'],'name':'renamed.pdf'}},'PATCH')[0],200)
        journal=next(i for i,e in enumerate(doc['entries']) if e['reference']=='JF1')
        self.assertEqual(self.review(a,w,lid,journal,{'kind':'posted_cn','cn_class':'scheme','season':'Rabi','crop':'Paddy','reason':'Must be excluded'})[0],400)

    def test_year_link_layout_and_mapping_backup_preserved(self):
        ua,a=self.user_browser();ub,b=self.user_browser('receiver');p,w=self.setup_book(a);self.config(a,w)
        previous=self.imported(a,w,'prior_year.pdf');current=self.imported(a,w,'current_year.pdf')
        query={'revision':self.state(a,w)['revision'],'previous_id':previous,'current_id':current}
        review=a.request(self.url(w,'year-preview'),query)[1]['review'];rid=review['receipts'][0]['id']
        self.assertEqual(a.request(self.url(w,'year-apply'),{**query,'confirmed':{rid:'4500'},'reason':'Verified original advance'})[0],200)
        self.assertEqual(a.request(self.url(w,'mapping'),{'revision':self.state(a,w)['revision'],'ledger_id':current,'entry_index':0,'item_index':0,'product_id':'dawat1'})[0],200)
        layout={'name':'Saved Studio','record_id':current,'theme':'studio','positions':[{'key':'money','x':55,'y':-88}],'locked':True}
        self.assertEqual(a.request('/api/data/layouts',{'project':p['id'],'workbook':w['id'],'data':layout})[0],201)
        backup=a.request('/api/projects/'+p['id']+'/export')[1]
        code,result,_=b.request('/api/projects/import',{'backup':backup});self.assertEqual(code,201,result)
        nw=next(r for r in b.request('/api/data/workbooks')[1]['items'] if r['project']==result['project_id'])
        s=self.state(b,nw);self.assertEqual(len(s['year_links']),1)
        new_current=next(iter(s['year_links']))
        self.assertEqual(s['year_links'][new_current]['opening_sources'][0]['date'],'2026-01-15')
        self.assertEqual(s['year_links'][new_current]['opening_sources'][0]['amount'],'4500')
        nl=b.request('/api/data/layouts')[1]['items'][0]['data']
        self.assertEqual(nl['record_id'],new_current);self.assertEqual(nl['positions'],layout['positions'])
        self.assertEqual(self.detail(b,nw,new_current)['ledger']['mappings'],{'0:0':'dawat1'})
        # Startup against the same account database preserves owned Phase 4 state.
        restarted=AccountApp(Accounts(self.tmp.name,clock=lambda:self.now[0]),origin=self.origin,development=True)
        self.assertEqual(restarted.ledger.state(b.token,nw['id'])['ledgers'],s['ledgers'])
