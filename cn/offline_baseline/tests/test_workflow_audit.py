import copy,tempfile,unittest
from pathlib import Path
from engine import compute,D,validate_scheme,validate_input_limits
from store import Store
from test_calculator import example

class WorkflowAuditTests(unittest.TestCase):
 def cash_case(self):
  r,s=example('scheme-5',sup='100',ret='0',abs_amount='0',payments=[('2026-03-12','10000')])
  r['allocations'][0].update(type='Cash',product=s['schemes'][4]['products'][0])
  return r,s
 def test_cash_payment_requires_explicit_quantity_selection(self):
  r,s=self.cash_case();out=compute(r,s)
  self.assertFalse(out['can_finalise']);self.assertTrue(any('Cash supplied/returned split' in x for x in out['issues']))
  self.assertTrue(any(d.get('step')==2 for d in out['issue_details']))
 def test_cash_zero_placeholder_does_not_resolve_missing_selection(self):
  r,s=self.cash_case();a=r['allocations'][0]
  r['cash_splits']=[dict(scheme=a['scheme'],product=a['product'],supplied='0',returned='0')]
  self.assertFalse(compute(r,s)['can_finalise'])
 def test_cash_valid_split_keeps_arithmetic_and_data(self):
  r,s=self.cash_case();a=r['allocations'][0];r['cash_splits']=[dict(scheme=a['scheme'],product=a['product'],supplied='100',returned='0')]
  before=copy.deepcopy((r,s));out=compute(r,s)
  self.assertEqual(out['issues'],[]);self.assertEqual(next(c['rounded'] for c in out['CNs'] if c['benefit'].startswith('Cash ')),4000);self.assertEqual((r,s),before)
 def test_manual_order_blank_defaults_to_zero(self):
  r,s=example();r['manual_order']=True;r['allocations'][1]['order']='';a=compute(r,s);r['allocations'][1]['order']='0';b=compute(r,s)
  self.assertEqual(a,b);self.assertTrue(a['can_finalise'])
 def test_manual_order_invalid_is_rejected_before_save(self):
  for value in ['-1','1.5','NaN','oops']:
   with self.subTest(value=value):
    r,s=example();r['manual_order']=True;r['allocations'][1]['order']=value
    with self.assertRaisesRegex(ValueError,'CD processing order'):validate_input_limits(r,s)
 def test_rate_units_checked_at_scheme_validation(self):
  for field in ['billing_unit','abs_unit','return_unit','extra_unit']:
   r,s=example();sc=s['schemes'][2];sc[field]='box'
   self.assertTrue(validate_scheme(sc,True),field)
 def test_duplicate_scheme_and_season_identities_rejected_atomically(self):
  for key in ['schemes','seasons']:
   with tempfile.TemporaryDirectory() as td:
    st=Store(Path(td)/'db');s=st.settings();before=copy.deepcopy(s);s[key].append(copy.deepcopy(s[key][0]))
    with self.assertRaisesRegex(ValueError,'Duplicate'):st.save_settings(s)
    self.assertEqual(st.settings(),before)
 def test_frozen_saved_status_is_authoritative(self):
  with tempfile.TemporaryDirectory() as td:
   st=Store(Path(td)/'db');r,s=example();st.save_settings(s);r=st.save(r);r=st.finalise(r['id'],r['revision']);fake=copy.deepcopy(r);fake.update(status='draft',entries=[])
   self.assertEqual(st.calculate(fake),r['result'])
 def test_draft_uses_current_workbook_settings_not_client_snapshot(self):
  with tempfile.TemporaryDirectory() as td:
   st=Store(Path(td)/'db');r,s=example();st.save_settings(s);r=st.save(r);fake=copy.deepcopy(r);fake['frozen_settings']=copy.deepcopy(s);fake['frozen_settings']['schemes'][2]['quantity'][0]['rate']='999';fake['result']={'new_CN_total':'999'}
   self.assertEqual(st.calculate(fake),st.calculate(r));saved=st.save(fake);self.assertNotIn('frozen_settings',saved);self.assertNotIn('result',saved)
 def test_extended_abs_whitespace_note_is_not_approval(self):
  r,s=example();s['schemes'][2]['extended_end']='2026-04-15';r['entries'][2]['date']='2026-04-01';r['allocations'][0].update(approved=True,remark='   ')
  self.assertFalse(compute(r,s)['can_finalise'])

 def test_scheme_override_cannot_silently_leave_money_in_old_scheme(self):
  r,s=example();sc=copy.deepcopy(s['schemes'][2]);sc.update(id='alternate',name='Alternate scheme');s['schemes'].append(sc);r['scheme_overrides']={'scheme-3':'alternate'}
  out=compute(r,s);self.assertFalse(out['can_finalise']);self.assertTrue(any('payment destination' in e for e in out['issues']))
  for a in r['allocations']:a['scheme']='alternate'
  self.assertEqual(compute(r,s)['issues'],[])
 def test_abs_unknown_product_cannot_turn_silently_into_excess(self):
  r,s=example();r['allocations'][0]['product']='missing';s['schemes'][2]['products'].append('missing')
  self.assertFalse(compute(r,s)['can_finalise'])
