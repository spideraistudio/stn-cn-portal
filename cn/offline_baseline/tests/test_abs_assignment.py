import copy,tempfile,unittest
from pathlib import Path
from test_calculator import example
from engine import compute,validate_abs_assignment_changes
from store import Store,dump

class ABSAssignmentTests(unittest.TestCase):
 def test_booking_boundaries_and_original_date(self):
  for dt,allowed in [('2025-12-31',False),('2026-01-01',True),('2026-03-31',True),('2026-04-01',False),('2026-07-10',False)]:
   with self.subTest(date=dt):
    r,s=example();e=next(e for e in r['entries'] if e['id']=='advance');e['date']=dt
    if allowed:validate_abs_assignment_changes(r,s)
    else:
     with self.assertRaisesRegex(ValueError,'ABS not allowed'):validate_abs_assignment_changes(r,s)
     self.assertFalse(compute(r,s)['can_finalise'])
  r,s=example();e=next(e for e in r['entries'] if e['id']=='advance');e['original']={**copy.deepcopy(e),'date':'2026-07-01'}
  with self.assertRaisesRegex(ValueError,'2026-07-01'):validate_abs_assignment_changes(r,s)
 def test_extension_requires_approval_for_benefit(self):
  r,s=example();sc=next(s for s in s['schemes'] if s['id']=='scheme-3');sc['extended_end']='2026-04-15';next(e for e in r['entries'] if e['id']=='advance')['date']='2026-04-10'
  validate_abs_assignment_changes(r,s);self.assertFalse(compute(r,s)['can_finalise'])
  r['allocations'][0].update(approved=True,remark='Approved extension');self.assertTrue(compute(r,s)['can_finalise'])
  next(e for e in r['entries'] if e['id']=='advance')['date']='2026-07-01'
  with self.assertRaises(ValueError):validate_abs_assignment_changes(r,s)
 def test_undated_opening_credit_and_dated_july(self):
  r,s=example();r['opening_sources']=[{'id':'opening','amount':'30000','date':None}];r['allocations'][0]['source']='opening';validate_abs_assignment_changes(r,s)
  draft=copy.deepcopy(r);draft['allocations'][0].update(scheme='',amount='0');validate_abs_assignment_changes(draft,s)
  r['opening_sources'][0]['date']='2026-07-01'
  with self.assertRaises(ValueError):validate_abs_assignment_changes(r,s)
 def test_save_is_atomic_and_old_invalid_draft_correctable(self):
  r,s=example()
  with tempfile.TemporaryDirectory() as d:
   st=Store(Path(d)/'test.sqlite');s['version']=st.settings()['version'];st.save_settings(s);saved=st.save(r)
   for key,value in [('source','receipt1'),('scheme','scheme-1')]:
    bad=copy.deepcopy(saved);bad['allocations'][0][key]=value
    if key=='source':bad['allocations'][2]['amount']='0'
    with self.assertRaisesRegex(ValueError,'ABS not allowed'):st.save(bad)
    self.assertEqual(st.get(saved['id']),saved)
   bad=copy.deepcopy(saved);bad['allocations'][2]['type']='ABS'
   with self.assertRaisesRegex(ValueError,'ABS not allowed'):st.save(bad)
   legacy=copy.deepcopy(saved);legacy['allocations'][2]['type']='ABS'
   with st.db() as c:c.execute('UPDATE records SET data=? WHERE id=?',(dump(legacy),legacy['id']))
   legacy=st.save(legacy);self.assertEqual(legacy['allocations'][2]['type'],'ABS');self.assertFalse(compute(legacy,s)['can_finalise'])
   legacy['allocations'][2]['amount']='100';legacy=st.save(legacy);legacy['allocations'][2]['amount']='101'
   with self.assertRaises(ValueError):st.save(legacy)
   legacy['allocations'][2]['type']='CD';st.save(legacy)
 def test_invalid_zero_row_and_changed_source_date(self):
  r,s=example();r['allocations'][0].update(source='receipt1',amount='0')
  with self.assertRaises(ValueError):validate_abs_assignment_changes(r,s)
  r,s=example();previous=copy.deepcopy(r);next(e for e in r['entries'] if e['id']=='advance')['date']='2026-07-01'
  with self.assertRaises(ValueError):validate_abs_assignment_changes(r,s,previous)
