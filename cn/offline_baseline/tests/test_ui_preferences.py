import unittest,tempfile
from pathlib import Path
from ui_preferences import preferences
class AppearanceTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.main=Path(self.tmp.name)/'main';self.other=Path(self.tmp.name)/'received'
 def test_restart_isolation_financial_preservation(self):
  self.main.mkdir();db=self.main/'cn.sqlite';db.write_bytes(b'financial sentinel')
  layout={'positions':[{'key':'card','x':123.5,'y':-456}]}
  preferences(self.main,self.main,'a',{'theme':'studio','record_id':'p','layout':layout})
  self.assertEqual(preferences(self.main,self.main,'a',record_id='p')['layout']['positions'],layout['positions'])
  self.assertIsNone(preferences(self.main,self.main,'b',record_id='p')['layout'])
  self.assertIsNone(preferences(self.main,self.other,'a',record_id='p')['layout'])
  self.assertIsNone(preferences(self.main,self.main,'a',record_id='p2')['layout'])
  self.assertEqual(preferences(self.main,self.other,'a')['theme'],'studio')
  self.assertEqual(db.read_bytes(),b'financial sentinel')
 def test_invalid_request_does_not_partially_save(self):
  for x in [float('nan'),float('inf'),True,100001,'42']:
   with self.assertRaises(ValueError):preferences(self.main,self.main,'a',{'theme':'studio','record_id':'p','layout':{'positions':[{'key':'x','x':x,'y':1}]}})
   self.assertEqual(preferences(self.main,self.main,'a')['theme'],'classic')
 def test_reset_and_corrupt_file(self):
  preferences(self.main,self.main,'a',{'theme':'studio','record_id':'p','layout':{'positions':[]}})
  preferences(self.main,self.main,'a',{'record_id':'p','reset':True})
  self.assertIsNone(preferences(self.main,self.main,'a',record_id='p')['layout'])
  (self.main/'ui-theme.json').write_text('invalid');self.assertEqual(preferences(self.main,self.main,'a')['theme'],'classic')

 def test_many_parties_never_evict_saved_positions(self):
  for i in range(45):preferences(self.main,self.main,'a',{'record_id':str(i),'layout':{'positions':[{'key':'x','x':i,'y':0}]}})
  self.assertEqual(preferences(self.main,self.main,'a',record_id='0')['layout']['positions'][0]['x'],0)

 def test_layout_lock_is_optional_and_validated(self):
  preferences(self.main,self.main,'a',{'record_id':'p','layout':{'positions':[],'locked':True}})
  self.assertTrue(preferences(self.main,self.main,'a',record_id='p')['layout']['locked'])
  with self.assertRaises(ValueError):preferences(self.main,self.main,'a',{'record_id':'p','layout':{'positions':[],'locked':'yes'}})
  self.assertTrue(preferences(self.main,self.main,'a',record_id='p')['layout']['locked'])
  preferences(self.main,self.main,'a',{'record_id':'p::classic','layout':{'positions':[],'locked':False}})
  self.assertTrue(preferences(self.main,self.main,'a',record_id='p')['layout']['locked'])
