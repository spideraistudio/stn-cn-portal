import unittest,copy
from test_calculator import example,configured,D
from engine import compute,validate_input_limits
from importer import parse_statement_pages,compare_import

def journal_text(lines):
 return 'Ledger Statement\nFor 01-Apr-26 to 30-Sep-26\nTest Party\nMarket, Gujarat\n01-Apr-26 Opening Balance 1000.00\n'+lines+'\nClosing Balance Rs. 900.00'

class PaymentClarityTests(unittest.TestCase):
 def test_journal_is_posted_expense_not_receipt_or_return(self):
  i=parse_statement_pages([journal_text('01-May-26 Journal J1 100.00 900.00\nFreight charges')],configured());e=i['entries'][0]
  self.assertEqual(e['kind'],'posted_cn');self.assertFalse(e['classification_required']);self.assertEqual(e['credit'],'100.00');self.assertEqual(e['original']['kind'],'posted_cn');self.assertTrue(i['reconciled'])
  r={**i,'state':'Gujarat','season':'2026 season 1','allocations':[],'old_dues':'0','opening_sources':[],'ledger_confirmed':True};r['entries'][0]['reviewed']=True;o=compute(r,configured());self.assertEqual(o['sources'],[]);self.assertEqual(o['new_CN_total'],D(0));self.assertEqual(o['final_balance'],D(900))
 def test_old_journal_reread_keeps_id_and_detects_change(self):
  i=parse_statement_pages([journal_text('01-May-26 Journal J1 100.00 900.00')],configured());old=copy.deepcopy(i['entries']);old[0]['kind']='adjustment';old[0]['original']['kind']='adjustment';out=compare_import(old,i['entries']);self.assertEqual(out[0]['status'],'Changed');self.assertEqual(out[0]['incoming']['id'],old[0]['id']);self.assertEqual(compare_import(i['entries'],i['entries'])[0]['status'],'Already imported')
 def test_stock_or_debit_journal_remains_reviewable(self):
  for line in ['01-May-26 Journal J1 100.00 900.00\nStock 1.00 pkt @ 100.00 100.00','01-May-26 Journal J1 100.00 1100.00']:
   e=parse_statement_pages([journal_text(line)],configured())['entries'][0];self.assertTrue(e['classification_required']);self.assertNotEqual(e['kind'],'posted_cn')
 def test_cd_work_reports_actual_slab_and_unchanged_date(self):
  r,s=example();o=compute(r,s);sc=next(sc for sc in s['schemes'] if sc['id']=='scheme-3')
  for w in o['groups'][0]['CD_work']:
   self.assertEqual(w['period'],sc['cd'][w['slab']-1]);self.assertEqual(w['percent'],D(w['period']['percent']));self.assertLess(abs(w['eligible_payment']*w['percent']/100-w['CD']),D('0.000000000000000000000001'))
   if w['source']:self.assertEqual(w['original_date'],next(e['date'] for e in r['entries'] if e['id']==w['source']))
  self.assertEqual(o['new_CN_total'],D(38561))
 def test_abs_work_explains_net_limit_and_token_conservation(self):
  r,s=example();o=compute(r,s);w=next(c for c in o['CNs'] if c['benefit']=='ABS')['working'][0];self.assertEqual(w['allocated'],w['principal']+w['excess']);self.assertLessEqual(w['eligible'],w['net_sold']);self.assertEqual(w['CN'],w['eligible']*w['CN_rate']);self.assertEqual(w['principal'],w['eligible']*w['token_rate'])
 def test_opening_credit_mixed_splits_exact_cap_and_no_second_receipt(self):
  r,s=example(abs_amount='0',payments=[]);r['entries']=[e for e in r['entries'] if e['kind']!='receipt'];r['closing']=str(sum(D(e['debit'])-D(e['credit']) for e in r['entries']));r.update(opening='-1000.25',closing=str(D(r['closing'])-D('1000.25')),opening_sources=[{'id':'credit','amount':'1000.25','date':None}]);sc=next(sc for sc in s['schemes'] if sc['id']=='scheme-3');r['allocations']=[{'id':'abs','source':'credit','type':'ABS','scheme':sc['id'],'product':sc['products'][0],'amount':'500.10'},{'id':'cd','source':'credit','type':'CD','scheme':sc['id'],'amount':'500.15'}]
  before=copy.deepcopy(r);validate_input_limits(r,s);o=compute(r,s);self.assertEqual(o['unallocated'],D(0));self.assertEqual(o['ledger_computed'],D(r['closing']));self.assertEqual(r,before);self.assertEqual(next(w for w in o['groups'][0]['CD_work'] if w['source']=='credit')['percent'],D(0));r['allocations'][1]['amount']='500.16'
  with self.assertRaises(ValueError):validate_input_limits(r,s)
