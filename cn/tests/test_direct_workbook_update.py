import copy,sqlite3,unittest
import test_native_interface_http as native
import test_ledger_http as ledgers
from cn_web import storage_ops
from cn_web.security import PERMISSIONS

class DirectMappingTests(unittest.TestCase):
    for name in ['setUp','stop','create','user_browser','setup_book','config','state','url','file','detail','calc','saved']:
        locals()[name]=getattr(native.NativeInterfaceTests,name)
    def test_map_without_opening_or_creating_party_calculation(self):
        u,b=self.user_browser();_,w=self.setup_book(b);self.config(b,w)
        lid=ledgers.LedgerHTTPTests.imported(self,b,w,'mapping_a.pdf')
        doc=self.detail(b,w,lid)['ledger']['document'];entry=next(e for e in doc['entries'] if e.get('items'));item=entry['items'][0]
        request=dict(ledger_id=lid,entry_id=entry['id'],item_index=0)
        self.assertEqual(self.saved(b,w)['records'],[])
        code,context,_=self.calc(b,w,'native-workbook-map-context',request);self.assertEqual(code,200,context)
        body={**request,'evidence':context['evidence'],'crop':'Maize','name':item['name'],'packing':item.get('mapping_suggestion',{}).get('detected_packing_kg') or '4'}
        self.admin.request('/api/admin/users/'+u['id'],{'permissions':list(PERMISSIONS-{'edit_schemes'})},'PATCH')
        self.assertEqual(self.calc(b,w,'native-workbook-map',body)[0],403)
        self.admin.request('/api/admin/users/'+u['id'],{'permissions':list(PERMISSIONS)},'PATCH')
        code,saved,_=self.calc(b,w,'native-workbook-map',body);self.assertEqual(code,200,saved)
        self.assertEqual(self.saved(b,w)['records'],[])
        self.assertEqual(self.calc(b,w,'native-workbook-map',body)[0],409)
        _,other=self.user_browser('another');self.assertEqual(self.calc(other,w,'native-workbook-map-context',request)[0],404)
        second=ledgers.LedgerHTTPTests.imported(self,b,w,'mapping_b.pdf')
        self.assertTrue(any(i.get('product')==saved['product_id'] for e in self.detail(b,w,second)['effective']['entries'] for i in e.get('items',[])))

class ByteIndexTests(unittest.TestCase):
    def test_utf8_replace_update_delete_rollback_and_later_table(self):
        db=sqlite3.connect(':memory:')
        db.execute('CREATE TABLE workspace_documents(owner TEXT,id TEXT,payload TEXT,PRIMARY KEY(owner,id))')
        db.execute('INSERT INTO workspace_documents VALUES(?,?,?)',('u','a','ગુજરાત'))
        self.assertEqual(storage_ops.usage(db),{'u':len('ગુજરાત'.encode())});db.commit()
        db.execute('INSERT OR REPLACE INTO workspace_documents VALUES(?,?,?)',('u','a','abc'))
        self.assertEqual(storage_ops.usage(db),{'u':3});db.rollback()
        self.assertEqual(storage_ops.usage(db),{'u':len('ગુજરાત'.encode())})
        db.execute("UPDATE workspace_documents SET payload='longer' WHERE id='a'")
        self.assertEqual(storage_ops.usage(db),{'u':6})
        db.execute('DELETE FROM workspace_documents');self.assertEqual(storage_ops.usage(db),{})
        db.execute('CREATE TABLE calculator_workspaces(owner TEXT,workbook TEXT,payload TEXT,PRIMARY KEY(owner,workbook))')
        db.execute("INSERT INTO calculator_workspaces VALUES('u','w','12345')")
        self.assertEqual(storage_ops.usage(db),{'u':5})
