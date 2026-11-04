"""Split-reference and user-specified Gram slab acceptance examples."""
import copy, os, unittest
from pathlib import Path
from decimal import Decimal as D
from test_period_accounting_update import e,r,PERIOD
import test_period_accounting_update as period_tests
from period_accounting import view,printed_splits
from engine import compute

def lines(entry,*values):
    entry['source_lines']=[{'text':v} for v in values];return entry

class SplitTests(unittest.TestCase):
    def test_split_current_and_opening(self):
        receipt=lines(e('r','2026-10-10','receipt',credit='100'),'Agst Ref OLD 1-Mar-26 30.00 Cr','Agst Ref new 70.00 Cr')
        record=r([e('new','2026-10-01','sale','100'),receipt],'100');record['source']['report_start']='2026-04-01'
        p=view(record,PERIOD);self.assertEqual(p['sources'][0]['available'],'70.00');self.assertEqual(p['old_dues_remaining'],'70.00')
        self.assertEqual(p['settlements'][0]['posting_date'],'2026-10-10');self.assertEqual(p['settlements'][0]['date'],'2026-03-01')
    def test_posted_cn_does_not_restore_receipt(self):
        for date,expected in [('2026-10-01','50.00'),('2026-10-20','0')]:
            cn=lines(e('cn',date,'posted_cn',credit='50'),'Agst Ref old 50.00 Cr')
            rec=lines(e('r','2026-10-10','receipt',credit='100'),'Agst Ref old 100.00 Cr')
            p=view(r([e('old','2026-09-01','sale','100'),cn,rec]),PERIOD)
            self.assertEqual(D(p['sources'][0]['available']),D(expected))
    def test_invalid_mixed_and_partial_splits_fall_back(self):
        for texts in [('Agst Ref old 20.00 Dr','New Ref x 120.00 Cr'),('Agst Ref old 30.00 Cr',),('On Account 100.00 Cr',)]:
            rec=lines(e('r','2026-10-10','receipt',credit='100'),*texts)
            p=view(r([rec],'100'),PERIOD);self.assertTrue(p['warnings']);self.assertEqual(D(p['sources'][0]['available']),0)
    def test_original_evidence_and_manual_override(self):
        rec=lines(e('r','2026-10-10','receipt',credit='100'),'Agst Ref new 100.00 Cr')
        rec['original']=copy.deepcopy(rec);rec['source_lines']=[]
        self.assertEqual(len(printed_splits(rec)[0]),1)
        rec['settlement_reference']='old'
        p=view(r([e('old','2026-09-01','sale','100'),e('new','2026-10-01','sale','100'),rec]),PERIOD)
        self.assertEqual(D(p['sources'][0]['available']),0)

class GramExampleTests(unittest.TestCase):
    def setup_example(self,cn_date='2026-10-05',receipt_date='2026-10-10',payment='100000',opening='100000',cn='20000',sale='200000'):
        record,cfg=period_tests.GivenCNTests().example();sc=cfg['schemes'][2];pid=sc['products'][0]
        sc.update(name='Gram manual example',crop='Gram',segment='Gram',benefits=['CD'],unit='kg',billing='100',billing_unit='kg',packing_kg='1',products=[pid],cd=[dict(start='2026-10-01',end='2026-10-30',percent='8'),dict(start='2026-10-31',end='2026-10-31',percent='0'),dict(start='2026-11-01',end='2026-11-30',percent='6')])
        next(p for p in cfg['products'] if p['id']==pid).update(crop='Gram',packing_kg='1')
        cfg['seasons'][0].update(**{k:PERIOD[k] for k in ['start','end','cutoff']})
        record.update(opening=opening,old_dues=opening,allocations=[],opening_sources=[])
        record['entries']=[e('sale','2026-10-01','sale',sale),e('cn',cn_date,'posted_cn',credit=cn),e('receipt',receipt_date,'receipt',credit=payment)]
        record['entries'][0]['items']=[dict(name='Gram',product=pid,qty=str(D(sale)/100),unit='kg',rate='100',amount=sale)]
        for entry in record['entries']:entry['reviewed']=True
        record['closing']=str(D(opening)+D(sale)-D(payment)-D(cn))
        record['period_accounting']=view(record,PERIOD)
        available=record['period_accounting']['sources'][0]['available']
        if D(available):record['allocations']=[dict(id='a',source='receipt',scheme=sc['id'],type='CD',amount=available)]
        return record,cfg
    def test_before_after_october_and_november(self):
        for cn_date,receipt_date,expected in [('2026-10-05','2026-10-10','1600'),('2026-10-15','2026-10-10','0'),('2026-10-05','2026-11-10','1200')]:
            record,cfg=self.setup_example(cn_date,receipt_date);out=compute(record,cfg)
            self.assertEqual(out['issues'],[]);self.assertEqual(out['new_CN_total'],D(expected))
    def test_boundaries_and_gap(self):
        for date,expected in [('2026-10-01','1600'),('2026-10-30','1600'),('2026-10-31','0'),('2026-11-01','1200'),('2026-11-30','1200')]:
            record,cfg=self.setup_example('2026-09-30',date);out=compute(record,cfg)
            self.assertEqual(out['new_CN_total'],D(expected))
    def test_inclusive_cap_preserved(self):
        record,cfg=self.setup_example(payment='100000',opening='0',cn='0',sale='108000')
        out=compute(record,cfg);self.assertEqual(out['issues'],[]);self.assertEqual(out['new_CN_total'],8000)
        record,cfg=self.setup_example(payment='100000',opening='0',cn='0',sale='100000')
        out=compute(record,cfg);self.assertEqual(out['new_CN_total'],7407)

@unittest.skipUnless(os.environ.get('CN_SETTLEMENT_FIXTURES'),'Set CN_SETTLEMENT_FIXTURES to the four private PDF directory')
class RealPDFTests(unittest.TestCase):
    def test_four_statements(self):
        from cn_web.ledger_service import LedgerService
        expected={'hari krishna.pdf':('822572','830458.74'),'dhruv seed.pdf':('20569','70819.37'),'ankur agro.pdf':('27907','45964.37'),'ABC bhadrod.pdf':('-58022','-19561.81')}
        for name,(opening,closing) in expected.items():
            with self.subTest(file=name):
                record=LedgerService.parse((Path(os.environ['CN_SETTLEMENT_FIXTURES'])/name).read_bytes(),{'catalogue':[],'periods':[]})[0]
                self.assertTrue(record['reconciled']);before=copy.deepcopy(record);p=view(record,PERIOD)
                self.assertEqual(record,before);self.assertEqual(D(p['opening']),D(opening));self.assertEqual(D(p['closing']),D(closing))
                # No available original-date cash receipt falls inside either supplied Gram slab.
                self.assertEqual(sum((D(s['available']) for s in p['sources'] if '2026-10-01'<=s['date']<='2026-11-30'),D(0)),0)
