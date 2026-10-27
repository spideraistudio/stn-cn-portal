import copy
from decimal import Decimal
from test_billing_audit import BillingTests


class BillingPrecision(BillingTests):
    def test_identical_901_at_475g_has_no_false_auto_or_selected_variation(self):
        self.s['catalogue'][0]['packing_kg']='0.475'
        self.add('sale','S','2026-05-01',100000,901)
        self.add('return','R','2026-06-01',10000,901)
        before=copy.deepcopy((self.s,self.doc))
        rows=self.run_audit()['rows']
        self.assertTrue(all(not r['attention'] for r in rows),rows)
        self.assertTrue(all(r['expected_rate']=='901' and Decimal(r['difference'])==0 for r in rows))
        matched=self.run_audit(matches={rows[1]['id']:[{'sale':rows[0]['id'],'qty':'10000'}]})['rows'][1]
        self.assertFalse(matched['attention']); self.assertEqual(Decimal(matched['difference']),0)
        self.assertEqual(before,(self.s,self.doc))

    def test_fractional_packings_never_turn_equal_printed_rates_into_mixed_rates(self):
        for pack in ['0.475','1.5','3','4','0.75']:
            with self.subTest(pack=pack):
                self.doc['entries']=[]; self.s['catalogue'][0]['packing_kg']=pack
                for i in range(3): self.add('sale','S'+str(i),'2026-05-01',100,901)
                self.add('return','R','2026-06-01',50,901)
                row=self.run_audit()['rows'][-1]
                self.assertFalse(row['attention']); self.assertEqual(row['expected_rate'],'901')
                self.assertEqual(row['allocations'],[]); self.assertFalse(row['invoice_match_confirmed'])

    def test_cross_unit_rates_use_printed_precision_without_bulk_amplification(self):
        self.s['catalogue'][0]['packing_kg']='0.475'
        self.add('sale','S','2026-05-01',100000,901)
        self.add('return','R','2026-06-01',10000,1896.84,'kg')
        rows=self.run_audit()['rows']; row=rows[-1]
        self.assertFalse(row['attention']); self.assertEqual(row['expected_rate'],'1896.84')
        self.assertEqual(Decimal(row['difference']),0)
        matched=self.run_audit(matches={row['id']:[{'sale':rows[0]['id'],'qty':'10000'}]})['rows'][-1]
        self.assertFalse(matched['attention']); self.assertEqual(Decimal(matched['difference']),0)

    def test_real_one_paise_and_high_precision_differences_still_flag(self):
        self.s['catalogue'][0]['packing_kg']='0.475'
        for rate,status in [(901.01,'Return rate above supply'),(900.99,'Return rate below supply'),(901.001,'Return rate above supply')]:
            with self.subTest(rate=rate):
                self.doc['entries']=[]; self.add('sale','S','2026-05-01',1000,901); self.add('return','R','2026-06-01',100,rate)
                self.assertEqual(self.run_audit()['rows'][-1]['status'],status)

    def test_mixed_real_rates_stay_ambiguous_and_opposing_splits_do_not_cancel(self):
        self.s['catalogue'][0]['packing_kg']='0.475'
        self.add('sale','S1','2026-05-01',1000,900.99); self.add('sale','S2','2026-05-02',1000,901.01)
        self.add('return','R','2026-06-01',100,901)
        rows=self.run_audit()['rows']; row=rows[-1]
        self.assertEqual(row['status'],'Mixed supply rates — review return')
        self.assertTrue(row['requires_original_bill'])
        matched=self.run_audit(matches={row['id']:[{'sale':rows[0]['id'],'qty':'50'},{'sale':rows[1]['id'],'qty':'50'}]})['rows'][-1]
        self.assertEqual(Decimal(matched['difference']),0); self.assertEqual(matched['status'],'Return rate mismatch')
