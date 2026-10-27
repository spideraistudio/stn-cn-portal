"""Product identity reuse through real authenticated HTTP/PDF imports."""
import copy
import unittest

import test_accounts_http as helpers
import test_ledger_http as ledger_tests
import test_calculator_http as calculator_tests
from cn_web.security import PERMISSIONS


class ProductMappingHTTPTests(unittest.TestCase):
    setUp = helpers.AccountHTTPTests.setUp
    stop = helpers.AccountHTTPTests.stop
    create = helpers.AccountHTTPTests.create
    user_browser = helpers.AccountHTTPTests.user_browser
    setup_book = ledger_tests.LedgerHTTPTests.setup_book
    url = ledger_tests.LedgerHTTPTests.url
    state = ledger_tests.LedgerHTTPTests.state
    file = ledger_tests.LedgerHTTPTests.file
    imported = ledger_tests.LedgerHTTPTests.imported
    detail = ledger_tests.LedgerHTTPTests.detail
    calc = calculator_tests.CalculatorHTTPTests.calc

    def configure(self, b, w):
        catalogue = copy.deepcopy(ledger_tests.CATALOGUE)
        for p in catalogue:
            p['aliases'] = ['DAWAT']
        catalogue += [
            {'id': 'legend', 'name': 'LEGEND', 'crop': 'Maize', 'segment': 'Single', 'packing_kg': '4', 'aliases': []},
            {'id': 'bajra', 'name': '14D14', 'crop': 'Bajra', 'segment': 'Hybrid', 'packing_kg': '1.5', 'aliases': []},
            {'id': 'gold', 'name': '14D14 Gold', 'crop': 'Bajra', 'segment': 'Hybrid', 'packing_kg': '1.5', 'aliases': []}]
        status, out, _ = b.request(self.url(w, 'config'), {'revision': self.state(b, w)['revision'],
            'catalogue': catalogue, 'periods': ledger_tests.PERIODS}, 'PUT')
        self.assertEqual(status, 200, out)

    def items(self, detail):
        return {i['name']: (ei, ii, i) for ei, e in enumerate(detail['effective']['entries'])
                for ii, i in enumerate(e.get('items', []))}

    def mapped(self, b, w, lid, name, **values):
        ei, ii, _ = self.items(self.detail(b, w, lid))[name]
        return b.request(self.url(w, 'mapping'), {'revision': self.state(b, w)['revision'],
            'ledger_id': lid, 'entry_index': ei, 'item_index': ii, 'same_name': True, **values})

    def test_recognised_preview_no_write_and_exact_source_preservation(self):
        u, b = self.user_browser(); p, w = self.setup_book(b); self.configure(b, w)
        before = self.state(b, w)
        preview, request = self.imported(b, w, 'mapping_a.pdf', False)
        self.assertEqual(self.state(b, w), before)
        self.assertEqual(sum(bool(x['product_id']) for x in preview['results'][0]['mapping_plan'].values()), 3)
        lid = self.imported(b, w, 'mapping_a.pdf'); detail = self.detail(b, w, lid)
        items = self.items(detail)
        for name, pid in [('DAWAT 1 kg', 'dawat1'), ('DAWAT 3 kg', 'dawat3'), ('14D14 Gold 1.5 kg', 'gold')]:
            self.assertEqual(items[name][2]['product'], pid)
        for name in ['PRINTED BRAND', 'DAWAT 2 kg', 'DAWAT', 'LEGEND PLUS 4 kg']:
            self.assertIsNone(items[name][2]['product'])
        original = copy.deepcopy(detail['ledger']['document'])
        self.assertEqual(self.mapped(b, w, lid, 'PRINTED BRAND', product_id='legend')[0], 200)
        self.assertEqual(self.detail(b, w, lid)['ledger']['document'], original)
        for ei, entry in enumerate(original['entries']):
            effective = self.detail(b, w, lid)['effective']['entries'][ei]
            self.assertEqual(entry['date'], effective['date'])
            for ii, item in enumerate(entry.get('items', [])):
                for key in ['name', 'qty', 'unit', 'rate', 'amount']:
                    self.assertEqual(effective['items'][ii][key], item[key])
        self.assertEqual(self.imported(b, w, 'mapping_a.pdf'), lid)
        self.assertEqual(self.mapped(b, w, lid, 'DAWAT 2 kg', product_id='dawat1')[0], 400)

    def test_saved_name_reuse_conflict_and_workbook_isolation(self):
        u, b = self.user_browser(); p, w = self.setup_book(b); self.configure(b, w)
        one = self.imported(b, w, 'mapping_a.pdf')
        self.assertEqual(self.mapped(b, w, one, 'PRINTED BRAND', product_id='legend')[0], 200)
        two = self.imported(b, w, 'mapping_b.pdf')
        self.assertEqual(self.items(self.detail(b, w, two))['PRINTED BRAND'][2]['product'], 'legend')
        self.assertEqual(self.mapped(b, w, two, 'PRINTED BRAND', product_id='gold')[0], 200)
        three = self.imported(b, w, 'mapping_c.pdf')
        self.assertIsNone(self.items(self.detail(b, w, three))['PRINTED BRAND'][2]['product'])
        self.assertTrue(any('Conflicting saved' in x['reason'] for x in self.detail(b, w, three)['mapping_plan'].values()))
        p2, w2 = self.setup_book(b); self.configure(b, w2)
        other = self.imported(b, w2, 'mapping_a.pdf')
        self.assertIsNone(self.items(self.detail(b, w2, other))['PRINTED BRAND'][2]['product'])
        _, stranger = self.user_browser('other-user')
        for browser in [stranger, self.admin]:
            self.assertEqual(browser.request(self.url(w, 'resolve-mappings'), {'revision': 1, 'ledger_id': one})[0], 404)
            self.assertEqual(browser.request(self.url(w, 'mapping'), {'revision': 1, 'ledger_id': one, 'entry_index': 0, 'item_index': 0, 'product_id': 'legend'})[0], 404)

    def test_new_product_atomic_permission_checks_and_empty_financial_benefits(self):
        u, b = self.user_browser(); p, w = self.setup_book(b); self.configure(b, w)
        lid = self.imported(b, w, 'mapping_a.pdf')
        new = {'name': 'PRINTED BRAND', 'crop': 'Maize', 'segment': 'New group', 'packing_kg': '4'}
        rights = list(PERMISSIONS - {'edit_schemes'})
        self.admin.request('/api/admin/users/' + u['id'], {'permissions': rights}, 'PATCH')
        before = self.state(b, w)
        self.assertEqual(self.mapped(b, w, lid, 'PRINTED BRAND', new_product=new)[0], 403)
        self.assertEqual(self.state(b, w), before)
        self.assertEqual(self.mapped(b, w, lid, 'PRINTED BRAND', product_id='legend')[0], 200)
        # Scheme-edit permission is not required for own existing mappings or imports.
        other = self.imported(b, w, 'mapping_b.pdf')
        self.assertEqual(self.items(self.detail(b, w, other))['PRINTED BRAND'][2]['product'], 'legend')
        self.admin.request('/api/admin/users/' + u['id'], {'permissions': list(PERMISSIONS)}, 'PATCH')
        before = self.state(b, w)
        self.assertEqual(self.mapped(b, w, lid, 'DAWAT 2 kg', new_product={**new, 'name': 'Wrong pack'})[0], 400)
        self.assertEqual(self.state(b, w), before)  # no orphan product on failure
        status, result, _ = self.mapped(b, w, lid, 'PRINTED BRAND', new_product=new)
        self.assertEqual(status, 200, result)
        status, runtime, _ = self.calc(b, w, 'state'); self.assertEqual(status, 200, runtime)
        product = next(p for p in runtime['settings']['products'] if p['id'] == result['product_id'])
        scheme = next(s for s in runtime['settings']['schemes'] if s['id'] == product['scheme'])
        self.assertFalse(scheme['confirmed']); self.assertIsNone(scheme['billing']); self.assertEqual(scheme['benefits'], [])
        self.admin.request('/api/admin/users/' + u['id'], {'permissions': list(PERMISSIONS - {'edit_ledger'})}, 'PATCH')
        self.assertEqual(self.mapped(b, w, lid, 'PRINTED BRAND', product_id='legend')[0], 403)
        self.assertEqual(b.request(self.url(w, 'resolve-mappings'), {'revision': self.state(b, w)['revision'], 'ledger_id': lid})[0], 403)

    def test_existing_unmapped_statement_reuse_revision_and_independent_backup(self):
        u, b = self.user_browser(); p, w = self.setup_book(b)
        lid = self.imported(b, w, 'mapping_a.pdf')
        original = self.detail(b, w, lid)['ledger']['document']
        self.assertEqual(self.detail(b, w, lid)['ledger']['mappings'], {})
        self.configure(b, w)
        before = self.state(b, w)
        self.detail(b, w, lid)  # GET suggests without saving
        self.assertEqual(self.state(b, w), before)
        body = {'revision': before['revision'], 'ledger_id': lid}
        status, out, _ = b.request(self.url(w, 'resolve-mappings'), body)
        self.assertEqual(status, 200, out); self.assertEqual(out['mapped'], 3)
        self.assertEqual(b.request(self.url(w, 'resolve-mappings'), body)[0], 409)
        self.assertEqual(self.detail(b, w, lid)['ledger']['document'], original)
        self.assertEqual(self.mapped(b, w, lid, 'PRINTED BRAND', product_id='legend')[0], 200)
        backup = b.request('/api/projects/' + p['id'] + '/export')[1]
        _, receiver = self.user_browser('receiver')
        status, imported, _ = receiver.request('/api/projects/import', {'backup': backup})
        self.assertEqual(status, 201, imported)
        books = receiver.request('/api/data/workbooks')[1]['items']
        new_w = books[0]
        new_lid = self.imported(receiver, new_w, 'mapping_b.pdf')
        self.assertEqual(self.items(self.detail(receiver, new_w, new_lid))['PRINTED BRAND'][2]['product'], 'legend')
        self.assertEqual(self.state(b, w)['ledgers'][0]['id'], lid)

    def test_source_calculator_cannot_diverge_from_saved_mapping(self):
        u, b = self.user_browser(); p, w = self.setup_book(b); self.configure(b, w)
        lid = self.imported(b, w, 'two_seasons.pdf')
        code, record, _ = self.calc(b, w, 'open-source', {'ledger_id': lid, 'season': 'Kharif', 'revision': self.state(b, w)['revision']})
        self.assertEqual(code, 200, record)
        changed = copy.deepcopy(record)
        next(i for e in changed['entries'] for i in e.get('items', []))['product'] = 'dawat3'
        self.assertEqual(self.calc(b, w, 'save', changed)[0], 409)
        self.assertEqual(self.detail(b, w, lid)['ledger']['mappings'], {'0:0':'dawat1','1:0':'dawat3','3:0':'dawat1','4:0':'dawat1','7:0':'dawat1','8:0':'dawat1'})

    def test_saved_crop_segment_choices_no_segment_and_independent_scheme_assignment(self):
        u, b = self.user_browser(); p, w = self.setup_book(b); self.configure(b, w)
        lid = self.imported(b, w, 'mapping_a.pdf')
        labels = self.state(b, w)
        self.assertIn('Maize', labels['crops']); self.assertEqual(labels['segments']['Maize'], ['Single'])
        # Crop spelling/spacing is canonicalised; segment is genuinely optional.
        code, out, _ = self.mapped(b, w, lid, 'PRINTED BRAND', new_product={
            'name': 'Unassigned brand', 'crop': '  maize  ', 'packing_kg': '4'})
        self.assertEqual(code, 200, out); pid = out['product_id']
        product = next(x for x in self.state(b, w)['catalogue'] if x['id'] == pid)
        self.assertEqual(product['crop'], 'Maize'); self.assertEqual(product['segment'], 'Awaiting scheme')
        before = len(self.state(b, w)['catalogue'])
        code, duplicate, _ = self.mapped(b, w, lid, 'PRINTED BRAND', new_product={
            'name': 'unassigned brand', 'crop': 'MAIZE', 'packing_kg': '4.0', 'segment': 'Different label'})
        self.assertEqual(code, 200, duplicate); self.assertEqual(duplicate['product_id'], pid)
        self.assertEqual(len(self.state(b, w)['catalogue']), before)
        code, runtime, _ = self.calc(b, w, 'state'); self.assertEqual(code, 200, runtime)
        cfg = runtime['settings']; product = next(x for x in cfg['products'] if x['id'] == pid)
        self.assertTrue(product['needs_assignment'])
        placeholder = next(x for x in cfg['schemes'] if x['id'] == product['scheme'])
        self.assertTrue(placeholder['mapping_placeholder']); self.assertEqual(placeholder['benefits'], [])
        for sid, segment, season in [('test-group-a', 'State A group', 'Kharif'), ('test-group-b', 'State B group', 'Rabi')]:
            scheme = copy.deepcopy(placeholder)
            scheme.update(id=sid, segment_id=sid, name=segment, segment=segment, season=season, products=[pid])
            scheme.pop('mapping_placeholder'); cfg['schemes'].append(scheme)
        code, saved, _ = self.calc(b, w, 'settings', cfg); self.assertEqual(code, 200, saved)
        self.assertIn('State A group', self.state(b, w)['segments']['Maize'])
        records = []
        for sid, season in [('test-group-a', 'Kharif'), ('test-group-b', 'Rabi')]:
            code, record, _ = self.calc(b, w, 'open-source', {'ledger_id': lid, 'season': season, 'revision': self.state(b, w)['revision']})
            self.assertEqual(code, 200, record)
            record['product_assignments'] = {pid: sid}
            code, record, _ = self.calc(b, w, 'save', record); self.assertEqual(code, 200, record)
            records.append(record)
        self.assertNotEqual(records[0]['id'], records[1]['id'])
        self.assertNotEqual(records[0]['product_assignments'], records[1]['product_assignments'])
        self.assertEqual(next(x for x in self.state(b, w)['catalogue'] if x['id'] == pid)['segment'], 'Awaiting scheme')
        self.admin.request('/api/admin/users/' + u['id'], {'permissions': list(PERMISSIONS - {'edit_schemes'})}, 'PATCH')
        records[0]['product_assignments'] = {pid: 'test-group-b'}
        self.assertEqual(self.calc(b, w, 'save', records[0])[0], 403)
        _, other = self.user_browser('other-user'); _, own = self.setup_book(other)
        self.assertEqual(self.state(other, own)['crops'], [])
