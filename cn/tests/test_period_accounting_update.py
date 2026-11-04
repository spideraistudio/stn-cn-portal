import copy,unittest
from decimal import Decimal
from cn_web import ledger_service
from period_accounting import view
from prior_payments import conflicts
from engine import payment_work,validate_input_limits
import test_native_interface_http as native

PERIOD={'name':'Oct-Nov','start':'2026-10-01','end':'2026-11-30','cutoff':'2026-11-30'}
def e(id,dt,kind,debit='0',credit='0',**kw):return dict(id=id,reference=id,date=dt,kind=kind,debit=debit,credit=credit,items=[],**kw)
def r(entries,opening='0'):return dict(id='a',party='Seller',address='Address',source={'issuer':'Company'},opening=opening,entries=entries,allocations=[],opening_sources=[],old_dues=opening,cash_splits=[])
class PeriodModelTests(unittest.TestCase):
    def test_opening_closing_all_activity_and_cutoff(self):
        x=r([e('sale','2026-05-01','sale','100'),e('r','2026-09-01','receipt',credit='40'),e('s2','2026-10-02','sale','50'),e('return','2026-10-03','return',credit='10'),e('ipt','2026-10-04','ipt_in','5'),e('cn','2026-10-05','posted_cn',credit='7'),e('adj','2026-10-06','adjustment','2'),e('future','2026-12-01','receipt',credit='100')], '20')
        p=view(x,PERIOD);self.assertEqual(p['opening'],'80');self.assertEqual(p['closing'],'120');self.assertEqual(set(p['totals']),{'sale','return','ipt_in','posted_cn','adjustment'});self.assertNotIn('future',p['entry_ids'])
    def test_cn_before_vs_after_receipt(self):
        for cn_date,expected in [('2026-10-01','50'),('2026-10-03','0')]:
            x=r([e('cn',cn_date,'posted_cn',credit='50'),e('r','2026-10-02','receipt',credit='100')],'100');p=view(x,PERIOD)
            self.assertEqual(p['sources'][0]['available'],expected)
    def test_preperiod_advance_original_date_remaining(self):
        x=r([e('advance','2026-03-01','receipt',credit='200'),e('old','2026-05-01','sale','70')]);p=view(x,PERIOD)
        self.assertEqual(p['opening'],'-130');self.assertEqual(p['sources'][0]['date'],'2026-03-01');self.assertEqual(p['sources'][0]['available'],'130')
        x['period_accounting']=p;self.assertEqual(payment_work(x)[0][0]['available'],Decimal(130))
    def test_explicit_current_bill_reference_and_fallback(self):
        base=[e('new','2026-10-01','sale','100'),e('receipt','2026-10-02','receipt',credit='100',settlement_reference='new')]
        p=view(r(base,'100'),PERIOD);self.assertEqual(p['sources'][0]['available'],'100');self.assertEqual(p['old_dues_remaining'],'100')
        base[-1].pop('settlement_reference');p=view(r(base,'100'),PERIOD);self.assertEqual(p['old_dues_remaining'],'0')
    def test_ordinary_receipt_reuse_without_reservation(self):
        a=r([e('receipt','2026-10-01','receipt',credit='100')]);a['allocations']=[dict(id='split',source='receipt',amount='60',type='Settlement')]
        b=copy.deepcopy(a);b['id']='b';b['workbook_id']='other'
        with self.assertRaisesRegex(ValueError,'already reserved/allocated'):conflicts(a,[b])
        b['allocations'][0]['amount']='40';conflicts(a,[b])
    def test_deleted_finalised_receipt_budget_stays_locked(self):
        a=r([e('receipt','2026-10-01','receipt',credit='100')]);a['allocations']=[dict(id='split',source='receipt',amount='100',type='Settlement')]
        frozen=copy.deepcopy(a);frozen.update(id='frozen',status='finalised',deleted_at='2026-11-02')
        with self.assertRaisesRegex(ValueError,'already reserved/allocated'):conflicts(a,[frozen])
    def test_opening_credit_is_consumed_before_later_receipts(self):
        x=r([e('old','2026-05-01','sale','150'),e('r','2026-10-01','receipt',credit='100')],'-100');x['old_dues']='0'
        p=view(x,PERIOD);self.assertEqual(p['opening'],'50');self.assertEqual(p['sources'][0]['available'],'50')
        self.assertEqual(p['untraced_opening_remaining'],'0')
    def test_selected_period_credit_cap_uses_earlier_credit_postings(self):
        from engine import validate_input_limits
        x=r([e('cn','2026-09-01','posted_cn',credit='100')])
        x['period_accounting']=view(x,PERIOD)
        x['opening_sources']=[dict(id='credit',amount='100',date=None)]
        from settings import initial_settings
        validate_input_limits(x,initial_settings())
        x['opening_sources'][0]['amount']='101'
        with self.assertRaisesRegex(ValueError,'Opening-credit sources exceed'):validate_input_limits(x,initial_settings())

    def test_carried_credit_pool_cannot_be_reused_in_another_period(self):
        x=r([e('cn','2026-09-01','posted_cn',credit='100')]);x['period_accounting']=view(x,PERIOD)
        x['opening_sources']=[dict(id='credit',amount='100',date=None)]
        x['allocations']=[dict(id='a',source='credit',amount='70',type='Settlement')]
        other=copy.deepcopy(x);other.update(id='other',season='Another period',workbook_id='other')
        with self.assertRaisesRegex(ValueError,'already reserved/allocated'):conflicts(x,[other])

    def test_overlapping_views_preserve_existing_dates(self):
        annual={'name':'Annual','start':'2026-04-01','end':'2026-11-30','cutoff':'2026-11-30'}
        ledger_service.validate_config([], [annual,PERIOD])

class GivenCNTests(unittest.TestCase):
    def example(self):
        import importlib.util
        from pathlib import Path
        spec=importlib.util.spec_from_file_location('preserved_examples',Path(__file__).resolve().parents[1]/'offline_baseline/tests/test_calculator.py')
        module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
        return module.example()
    def test_crop_season_deduction_once_and_floor(self):
        from engine import compute
        a,cfg=self.example();before=compute(a,cfg)['new_CN_total'];crop=cfg['schemes'][2]['crop']
        a['entries'].append(e('given','2026-08-30','posted_cn',credit='1000'));a['closing']=str(Decimal(a['closing'])-1000)
        a['posted_cn_assignments']={'given':dict(crop=crop,season=a['season'],amount='1000')}
        self.assertEqual(compute(a,cfg)['new_CN_total'],before-1000)
        self.assertEqual(compute(a,cfg)['new_CN_total'],before-1000)
        a['posted_cn_assignments']['given']['season']='Other season';self.assertEqual(compute(a,cfg)['new_CN_total'],before)
        a['entries'][-1]['credit']='1000000';a['closing']=str(Decimal(a['closing'])-999000)
        a['posted_cn_assignments']['given'].update(season=a['season'],amount='1000000')
        self.assertEqual(compute(a,cfg)['new_CN_total'],0)
    def test_already_issued_history_is_not_deducted_twice(self):
        from engine import compute
        a,cfg=self.example();base=compute(a,cfg);crop=cfg['schemes'][2]['crop']
        cn=next(c for c in base['CNs'] if c['rounded']>=1000)
        a['prior_issued']={cn['key']:'1000'}
        a['entries'].append(e('posted','2026-08-30','posted_cn',credit='1000'));a['closing']=str(Decimal(a['closing'])-1000)
        a['posted_cn_assignments']={'posted':dict(crop=crop,season=a['season'],amount='1000')}
        self.assertEqual(compute(a,cfg)['new_CN_total'],base['new_CN_total']-1000)
    def test_material_return_cannot_be_benefit_cn(self):
        from engine import compute
        a,cfg=self.example();a['posted_cn_assignments']={'return':dict(crop=cfg['schemes'][2]['crop'],season=a['season'],amount='1')}
        self.assertFalse(compute(a,cfg)['can_finalise'])

class PeriodHTTPTests(unittest.TestCase):
    setUp=native.NativeInterfaceTests.setUp
    stop=native.NativeInterfaceTests.stop
    create=native.NativeInterfaceTests.create
    user_browser=native.NativeInterfaceTests.user_browser
    setup_book=native.NativeInterfaceTests.setup_book
    config=native.NativeInterfaceTests.config
    state=native.NativeInterfaceTests.state
    url=native.NativeInterfaceTests.url
    file=native.NativeInterfaceTests.file
    calc=native.NativeInterfaceTests.calc
    imported=native.NativeInterfaceTests.imported
    def test_workbook_creation_without_dates_and_selected_period_reopen(self):
        u,b=self.user_browser();_,w=self.setup_book(b)
        code,new,_=self.calc(b,w,'workbooks',{'name':'No dates','state':'Gujarat','mode':'blank'})
        self.assertEqual(code,200,new)
        self.config(b,w);record=self.imported(b,w)
        cfg=self.calc(b,w,'state')[1]['settings'];cfg['seasons'].append({**PERIOD,'confirmed':True})
        code,out,_=self.calc(b,w,'settings',cfg);self.assertEqual(code,200,out)
        code,out,_=self.calc(b,w,'native-workbook-period',{'season':'Oct-Nov'});self.assertEqual(code,200,out)
        code,out,_=self.calc(b,w,'native-state');self.assertEqual(out['selected_period'],'Oct-Nov')
        code,opened,_=self.calc(b,w,'native-open',{'ledger_id':record['web_source']['ledger_id'],'season':'Oct-Nov'});self.assertEqual(code,200,opened)
        backup=b.request('/api/projects/'+w['project']+'/export')[1]
        code,clone,_=b.request('/api/projects/import',{'backup':backup});self.assertEqual(code,201,clone)
        cloned=next(x for x in b.request('/api/data/workbooks')[1]['items'] if x['project']==clone['project_id'])
        self.assertEqual(self.calc(b,cloned,'native-state')[1]['selected_period'],'Oct-Nov')
        self.assertIn('period_accounting',opened)
        code,saved,_=self.calc(b,w,'save',opened);self.assertEqual(code,200,saved)
        code,reopened,_=self.calc(b,w,'record',{'id':saved['id']});self.assertEqual(code,200,reopened);self.assertEqual(reopened['result']['period_accounting']['start'],'2026-10-01')
    def test_shared_posted_cn_and_reference_permissions_reopen(self):
        u,b=self.user_browser();_,w=self.setup_book(b);self.config(b,w);record=self.imported(b,w)
        cn=next(e for e in record['entries'] if e['kind']=='posted_cn')
        value=dict(crop='Paddy',season='Kharif',amount='100',history_relation='separate')
        code,saved,_=self.calc(b,w,'native-given-cn',dict(id=record['id'],revision=record['revision'],entry=cn['id'],value=value));self.assertEqual(code,200,saved)
        code,rabi,_=self.calc(b,w,'native-open',dict(ledger_id=saved['web_source']['ledger_id'],season='Rabi'));self.assertEqual(code,200,rabi)
        self.assertEqual(rabi['posted_cn_assignments'][cn['id']],value)
        code,out,_=self.calc(b,w,'native-given-cn',dict(id=rabi['id'],revision=rabi['revision'],entry=cn['id'],value={**value,'amount':'101'}));self.assertEqual(code,400,out)
        receipt=next(e for e in rabi['entries'] if e['kind']=='receipt' and e['date']>'2026-10-01');sale=next(e for e in rabi['entries'] if e['kind']=='sale' and e['date']>'2026-10-01')
        code,out,_=self.calc(b,w,'native-settlement-reference',dict(id=rabi['id'],revision=rabi['revision'],entry=receipt['id'],value=sale['reference']));self.assertEqual(code,200,out)
        self.assertEqual(next(e for e in out['entries'] if e['id']==receipt['id'])['settlement_reference'],sale['reference'])
        backup=b.request('/api/projects/'+w['project']+'/export')[1]
        code,imported,_=b.request('/api/projects/import',{'backup':backup});self.assertEqual(code,201,imported)
        imported_book=next(x for x in b.request('/api/data/workbooks')[1]['items'] if x['project']==imported['project_id'])
        state=self.state(b,imported_book)
        code,details,_=b.request(self.url(imported_book,'ledgers/'+state['ledgers'][0]['id']));self.assertEqual(code,200,details)
        self.assertTrue(details['ledger']['posted_cn_assignments'])
        _,other=self.user_browser('other-account');self.assertEqual(self.calc(other,w,'native-given-cn',dict(id=out['id'],revision=out['revision'],entry=cn['id'],value=value))[0],404)
