"""Phase 3 synthetic rate/unit reproduction and scoped saved-state regression."""
import copy
import unittest
from cn_web import billing_audit as audit
from test_billing_audit import BillingTests
from test_billing_http import BillingHTTP

class RateTrace(BillingTests):
    def test_kg_rate_entered_as_default_packet_reproduces_false_mismatch(self):
        self.s['billing_audit']['rates'][0].update(rate='300',unit='packet')
        self.add('sale','S1','2026-05-01',10,1200)
        self.add('return','R1','2026-10-01',1,1200)
        original=copy.deepcopy(self.doc)
        rows=self.run_audit()['rows']
        self.assertEqual(rows[0]['status'],'Billing rate mismatch')
        self.assertEqual(audit.decimal(rows[0]['difference']),audit.decimal('9000'))
        matches={rows[1]['id']:[{'sale':rows[0]['id'],'qty':'1'}]}
        self.s['billing_audit']['rates'][0]['unit']='kg'
        rows=self.run_audit(matches=matches)['rows']
        self.assertEqual(rows[0]['status'],'Rate matches')
        self.assertIn('300 / kg',rows[0]['comparison_basis'])
        self.assertEqual(rows[0]['packing_kg'],'4')
        self.assertEqual(rows[1]['status'],'Return rate matches original bill')
        self.assertEqual(self.doc,original)
        self.s['billing_audit']['rates'][1]['rate']='999'
        self.assertEqual(self.run_audit(matches=matches)['rows'][1]['status'],'Return rate matches original bill')

    def test_state_choices_preserve_existing_and_reuse_case_spacing(self):
        cfg=audit.empty();old={'state':' GUJARAT ','product':'p','start':'2026-01-01','end':'2026-03-31','unit':'kg','rate':'10'}
        cfg['rates']=[old]
        states=audit.recorded_states(cfg,[{'state':'Gujarat'},{'state':'Madhya   Pradesh'}],{'state':'gujarat'},{'schemes':[{'states':['Rajasthan']}]},[])
        self.assertEqual(states,['GUJARAT','Madhya Pradesh','Rajasthan'])
        new={**old,'state':' gujarat ','start':'2026-04-01','end':'2026-08-31'}
        out=audit.canonical_rates([old,new],cfg['rates'],states)
        self.assertEqual(out[0]['state'],' GUJARAT ')
        self.assertEqual(out[1]['state'],'GUJARAT')
        self.assertEqual(cfg['rates'],[old])

class ScopedStates(BillingHTTP):
    def test_scoped_config_states_and_saved_correction(self):
        _,b=self.user_browser();_,w=self.setup_book(b);self.config(b,w)
        _,out,_=self.calc(b,w,'native-audit-import',{'data':self.file('two_seasons.pdf')['content_base64']})
        docs=out['documents'];request={'documents':docs,'start':'2026-04-01','end':'2027-03-31','include_saved':False}
        code,cfg,_=self.calc(b,w,'native-billing-config',{'documents':docs});self.assertEqual(code,200,cfg)
        self.assertIn('Gujarat',cfg['states'])
        _,other=self.user_browser('other-phase3');_,foreign=self.setup_book(other);self.config(other,foreign)
        self.assertEqual(self.calc(other,foreign,'native-billing-config',{'documents':docs})[0],404)
        before=self.calc(b,w,'native-billing-run',request)[1]
        rates=[{'state':'Gujarat','product':'dawat1','start':'2026-04-01','end':'2027-03-31','unit':'','rate':'100'}]
        self.assertEqual(self.calc(b,w,'native-billing-rates',{'revision':cfg['revision'],'rates':rates})[0],400)
        rates[0]['unit']='kg'
        code,saved,_=self.calc(b,w,'native-billing-rates',{'revision':cfg['revision'],'rates':rates});self.assertEqual(code,200,saved)
        self.assertEqual(self.calc(b,w,'native-billing-rates',{'revision':cfg['revision'],'rates':rates})[0],409)
        after=self.calc(b,w,'native-billing-run',request)[1]
        self.assertEqual([(r['id'],r['rate'],r['amount'],r['date']) for r in before['rows']],[(r['id'],r['rate'],r['amount'],r['date']) for r in after['rows']])
        self.assertTrue(any(r['status']=='Rate matches' for r in after['rows']))
        self.assertEqual(self.calc(b,w,'native-billing-config',{})[1]['configuration']['rates'],rates)

if __name__=='__main__':unittest.main()
