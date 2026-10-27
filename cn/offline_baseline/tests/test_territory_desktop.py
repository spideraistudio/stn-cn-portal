import unittest,tempfile,copy,sys,os,importlib,urllib.request,json,threading
from pathlib import Path
from unittest.mock import patch
from decimal import Decimal
from territory import source_hq,territory_report,product_totals
from importer import import_pdf_documents
from settings import initial_settings
from store import Store
from workbooks import Workbooks
from test_calculator import example

class TerritoryTests(unittest.TestCase):
 def test_real_combined_group_and_legacy_missing(self):
  raw=(Path(__file__).resolve().parents[1]/'fixtures/surendranagar_combined.pdf').read_bytes();docs=import_pdf_documents(raw,initial_settings());self.assertEqual(len(docs),49)
  self.assertTrue(all(source_hq(d)['hq']=='Surendranagar' for d in docs));self.assertEqual(source_hq({'location':'Surendranagar'})['hq_status'],'missing')
 def test_header_only_no_guess_and_conflicting_pages(self):
  self.assertEqual(source_hq({'source':{'text':'Ledger Statement\nDate Particulars\nGroup: Narration text'}})['hq_status'],'missing')
  r={'source':{'structured_pages':[{'header_line':2,'rows':[{'line':1,'text':'Group: A'},{'line':3,'text':'Group: voucher narration'}]},{'header_line':2,'rows':[{'line':1,'text':'Group: B'}]}]}}
  self.assertEqual(source_hq(r)['hq_status'],'review')
 def test_frozen_reporting_filter_and_read_only(self):
  with tempfile.TemporaryDirectory() as td:
   st=Store(Path(td)/'a.sqlite3');r,s=example();r['source']={'text':'Group: Ahmedabad HQ\nDate Particulars\n'};st.save_settings(s);saved=st.save(r);st.finalise(saved['id'],saved['revision']);books=Workbooks(st);before=books.backup();out=territory_report(books)
   self.assertTrue(out['hierarchy']);self.assertEqual(out['hierarchy'][0]['hqs'][0]['hq'],'Ahmedabad HQ');self.assertEqual(out['hierarchy'][0]['hqs'][0]['parties'][0]['party'],r['party']);self.assertFalse(territory_report(books,{'hq':'No such HQ'})['hierarchy'])
   st.revise(saved['id']);revised=territory_report(books);self.assertEqual(out['summary'],revised['summary'])
   after_read=books.backup();territory_report(books);after=books.backup()
   for b in (after_read,after):b.pop('created_at',None);b['legacy'].pop('created_at',None)
   self.assertEqual(after_read,after)
 def test_weighted_nrv_packings_and_missing_rates(self):
  rows=[dict(crop='Paddy',product='DAWAT',packing_kg='1',net_packets='10',net_kg='10',total_CN='10',net_realisation='900'),dict(crop='Paddy',product='DAWAT',packing_kg='1',net_packets='30',net_kg='30',total_CN='30',net_realisation='3000'),dict(crop='Paddy',product='DAWAT',packing_kg='3',net_packets='2',net_kg='6',total_CN='20',net_realisation=None)]
  totals=product_totals(rows);self.assertEqual(len(totals),2);self.assertEqual(totals[0]['NRV_per_packet'],Decimal('97.5'));self.assertIsNone(totals[1]['NRV_per_packet'])

class DesktopTests(unittest.TestCase):
 def test_native_window_same_store_health_downloads_close_guard(self):
  import desktop_app
  class Hooks:
   def __init__(self):self.fns=[]
   def __iadd__(self,fn):self.fns.append(fn);return self
  class FakeWindow:
   def __init__(self,url,bridge):
    self.url=url;self.bridge=bridge;self.destroyed=False;self.scripts=[];self.script_ready=threading.Event();self.events=type('Events',(),{'loaded':Hooks(),'closing':Hooks()})()
   def get_current_url(self):return self.url
   def destroy(self):self.destroyed=True
   def run_js(self,script):self.scripts.append(script);self.script_ready.set()
  class FakeWebview:
   settings={}
   def create_window(self,title,url,**kw):self.window=FakeWindow(url,kw['js_api']);return self.window
   def start(self,**kw):
    self.kw=kw
    self.health=json.loads(urllib.request.urlopen(self.window.url+'api/health').read())
    self.window.events.loaded.fns[0]();self.blocked=self.window.events.closing.fns[0]();self.window.script_ready.wait(2)
    self.window.bridge.finish_close();self.allowed=self.window.events.closing.fns[0]()
  with tempfile.TemporaryDirectory() as td,patch.dict(os.environ,CN_DATA_PATH=str(Path(td)/'desktop.sqlite3')):
   previous=sys.modules.pop('app',None)
   try:
    fake=FakeWebview();desktop_app.run_desktop(fake);self.assertEqual(fake.health['status'],'ok');self.assertTrue(fake.settings['ALLOW_DOWNLOADS']);self.assertFalse(fake.blocked);self.assertTrue(fake.allowed);self.assertTrue(fake.window.destroyed);self.assertIn('cnSaveAndClose',fake.window.scripts[0]);self.assertTrue((Path(td)/'desktop.sqlite3').exists())
   finally:
    sys.modules.pop('app',None)
    if previous is not None:sys.modules['app']=previous
