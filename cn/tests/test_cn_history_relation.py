import copy,unittest
from decimal import Decimal as D
import test_period_accounting_update as helpers
e=helpers.e
from engine import compute

class CNHistoryRelationTests(unittest.TestCase):
    def example(self):
        r,cfg=helpers.GivenCNTests().example();base=compute(r,cfg);cn=next(c for c in base['CNs'] if c['rounded']>=1000)
        r['prior_issued']={cn['key']:'1000'}
        r['entries'].append(e('posted','2026-08-30','posted_cn',credit='1000'));r['closing']=str(D(r['closing'])-1000)
        r['posted_cn_assignments']={'posted':dict(crop=cn['crop'],season=r['season'],amount='1000')}
        return r,cfg,base['new_CN_total']
    def test_ambiguous_crop_only_match_is_blocked(self):
        r,cfg,total=self.example();out=compute(r,cfg)
        self.assertFalse(out['can_finalise']);self.assertTrue(any('same app-issued' in s for s in out['issues']))
    def test_same_document_is_deducted_once(self):
        r,cfg,total=self.example();r['posted_cn_assignments']['posted']['history_relation']='same_issued'
        out=compute(r,cfg);self.assertTrue(out['can_finalise'],out['issues']);self.assertEqual(out['new_CN_total'],total-1000)
    def test_separate_document_is_additional(self):
        r,cfg,total=self.example();r['posted_cn_assignments']['posted']['history_relation']='separate'
        out=compute(r,cfg);self.assertTrue(out['can_finalise'],out['issues']);self.assertEqual(out['new_CN_total'],total-2000)
        r.update(status='finalised',cn_history_matching='explicit-v1')
        self.assertEqual(compute(r,cfg)['new_CN_total'],total-2000)
    def test_unproven_matching_amount_is_blocked(self):
        r,cfg,total=self.example();r['prior_issued']={}
        r['posted_cn_assignments']['posted']['history_relation']='same_issued'
        self.assertFalse(compute(r,cfg)['can_finalise'])
    def test_legacy_frozen_proof_reproduces_without_reclassification(self):
        r,cfg,total=self.example();r['status']='issued'
        out=compute(r,cfg);self.assertEqual(out['new_CN_total'],total-1000)
        self.assertFalse(any('same app-issued' in s for s in out['issues']))
