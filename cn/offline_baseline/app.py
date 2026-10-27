"""Local loopback app. Python standard library server; SQLite persistence."""
from http.server import ThreadingHTTPServer,BaseHTTPRequestHandler
from pathlib import Path
import json,os,sys,uuid,base64,traceback,webbrowser,secrets
from urllib.parse import urlsplit,parse_qs
from workbooks import Workbooks,bulk_history,bulk_document,resolve_bulk
from store import Store,dump
from projects import Projects
from maintenance import Cleanup,purge,archived
from ui_preferences import preferences
from workbook_print import workbook_print
from allocation_clear import clear_allocations
from allocation_review import review_allocation
from ledger_audit import audit_documents
from reporting import report,product_rows,csv_text
from territory import territory_report
from year_link import match_years,analyse_pair,attach_link
from engine import validate_scheme,validate_input_limits
from importer import import_pdf,compare_import,parse_statement_pages,import_pdf_documents,parse_saved_source
ROOT=Path(__file__).resolve().parent
# Bundle assets are read-only; user databases always stay beside the executable.
DATA_ROOT=Path(sys.executable).resolve().parent if getattr(sys,'frozen',False) else ROOT
store=Store(os.environ.get('CN_DATA_PATH',str(DATA_ROOT/'data'/'calculator.sqlite3')))
books=Workbooks(store)
projects=Projects(books)
TOKEN=secrets.token_urlsafe(32)
class Handler(BaseHTTPRequestHandler):
    def log_message(self,*args):pass
    def respond(self,obj,status=200):
        data=dump(obj).encode();self.send_response(status);self.send_header('Content-Type','application/json');self.send_header('Cache-Control','no-store');self.send_header('X-Content-Type-Options','nosniff');self.end_headers();self.wfile.write(data)
    def local_host(self):
        return self.headers.get('Host','').split(':')[0] in ('127.0.0.1','localhost')
    @projects.serialized
    def do_GET(self):
        if not self.local_host():return self.respond({'error':'Local host required'},403)
        path=urlsplit(self.path).path
        try:
            project=self.headers.get('X-CN-Project','main');store,books=projects.context(project)
            workbook=self.headers.get('X-CN-Workbook','legacy');current=books.get(workbook)
            if path=='/api/state':return self.respond({'project':projects.metadata(project),'projects':projects.list(),'settings':current.settings(),'records':current.all(),'token':TOKEN,'workbook':books.metadata(workbook),'workbooks':books.list(),'deleted_workbooks':[m for m in books.list(True) if m.get('deleted_at')],'bulk_history':bulk_history(current)})
            if path=='/api/ui-preferences':return self.respond(preferences(Path(projects.main.legacy.path).parent,Path(books.legacy.path).parent,workbook,record_id=parse_qs(urlsplit(self.path).query).get('record_id',[''])[0]))
            if path=='/api/backup':return self.respond(books.backup())
            if path=='/api/fixture/ashapura':return self.respond(import_pdf((ROOT/'fixtures/ashapura.pdf').read_bytes(),current.settings()))
            if path=='/api/health':return self.respond({'status':'ok','offline':True})
            names={'/':'index.html','/app.js':'app.js','/polish.js':'polish.js','/ui-theme.js':'ui-theme.js','/studio.js':'studio.js','/payment-workbench.js':'payment-workbench.js','/scheme-options.js':'scheme-options.js','/studio.css':'studio.css','/studio-art.svg':'studio-art.svg','/style.css':'style.css','/fonts/Manrope.ttf':'fonts/Manrope.ttf','/app.ico':'app.ico'}
            if path not in names:return self.respond({'error':'Not found'},404)
            data=(ROOT/'static'/names[path]).read_bytes();self.send_response(200);self.send_header('Content-Type',{'/':'text/html','/app.js':'text/javascript','/polish.js':'text/javascript','/ui-theme.js':'text/javascript','/studio.js':'text/javascript','/payment-workbench.js':'text/javascript','/scheme-options.js':'text/javascript','/studio.css':'text/css','/studio-art.svg':'image/svg+xml','/style.css':'text/css','/fonts/Manrope.ttf':'font/ttf','/app.ico':'image/x-icon'}[path]);self.send_header('Cache-Control','no-store');self.send_header('X-Content-Type-Options','nosniff');self.send_header('Content-Security-Policy',"default-src 'self'; style-src 'self'; script-src 'self'; img-src 'self' data:; connect-src 'self'; base-uri 'none'; frame-ancestors 'none'");self.end_headers();self.wfile.write(data)
        except Exception as e:self.respond({'error':str(e)},400)
    @projects.serialized
    def do_POST(self):
        try:
            if not self.local_host() or self.headers.get('X-CN-Token')!=TOKEN:return self.respond({'error':'Invalid local session'},403)
            path=urlsplit(self.path).path
            length=int(self.headers.get('Content-Length','0'));maximum=128 if path in ('/api/restore','/api/project-import') else 20
            if length>maximum*1024*1024:raise ValueError('Request exceeds '+str(maximum)+' MB')
            b=json.loads(self.rfile.read(length))
            project=self.headers.get('X-CN-Project','main');store,books=projects.context(project)
            workbook=self.headers.get('X-CN-Workbook','legacy');current=books.get(workbook)
            if b.get('workbook_id',workbook)!=workbook:raise ValueError('Calculation belongs to another workbook')
            if path in ('/api/save','/api/calculate','/api/validate-limits') and workbook!='legacy':b['workbook_id']=workbook;b['annual_ledger']=True;b['workbook_scheme_state']=books.metadata(workbook)['state']
            if path=='/api/ui-preferences':out=preferences(Path(projects.main.legacy.path).parent,Path(books.legacy.path).parent,workbook,body=b)
            elif path=='/api/project-export':out=projects.export(project,{**b,'selected_workbook':workbook})
            elif path=='/api/project-import':out=projects.receive(b)
            elif path=='/api/storage':out={**Cleanup(books,ROOT).run(b),'deleted_items':archived(books,workbook)}
            elif path=='/api/purge':out=purge(books,workbook,b)
            elif path=='/api/save':out=current.save(b)
            elif path=='/api/calculate':out=current.calculate(b)
            elif path in ('/api/abs-distribution-preview','/api/abs-distribution-apply'):
                r=b['record']
                if r.get('workbook_id',workbook)!=workbook:raise ValueError('Calculation belongs to another workbook')
                if workbook!='legacy':r.update(workbook_id=workbook,annual_ledger=True,workbook_scheme_state=books.metadata(workbook)['state'])
                out=current.preview_abs_distribution(b,apply=path.endswith('-apply'))
            elif path in ('/api/cash-quantity-preview','/api/cash-quantity-apply'):
                r=b['record']
                if r.get('workbook_id',workbook)!=workbook:raise ValueError('Calculation belongs to another workbook')
                if workbook!='legacy':r.update(workbook_id=workbook,annual_ledger=True,workbook_scheme_state=books.metadata(workbook)['state'])
                out=current.preview_cash_quantity(b,apply=path.endswith('-apply'))
            elif path in ('/api/cash-remove-preview','/api/cash-remove-apply'):
                r=b['record']
                if r.get('workbook_id',workbook)!=workbook:raise ValueError('Calculation belongs to another workbook')
                if workbook!='legacy':r.update(workbook_id=workbook,annual_ledger=True,workbook_scheme_state=books.metadata(workbook)['state'])
                out=current.preview_cash_removal(b,apply=path.endswith('-apply'))
            elif path=='/api/late-ipt-review':out=current.review_late_ipt(b['id'],b['revision'],b['entry_id'],b.get('reason',''),b.get('remove',False))
            elif path=='/api/party-delete':out=current.party_action(b['id'],b.get('restore',False),b.get('confirm',False),b.get('expected'))
            elif path=='/api/workbook-delete':out=books.delete(b['id'],b.get('restore',False),b.get('confirm',False),b.get('expected'))
            elif path=='/api/product-delete':out=current.product_action(b['id'],b['version'],b.get('restore',False))
            elif path=='/api/scheme-delete':out=current.scheme_action(b['id'],b['version'],b.get('restore',False))
            elif path=='/api/validate-limits':
                validate_input_limits(b,current.settings());out={'valid':True}
            elif path=='/api/settings':out=current.save_settings(b)
            elif path=='/api/validate-scheme':out={'errors':validate_scheme(b['scheme'],b.get('production',False))}
            elif path=='/api/finalise':out=current.finalise(b['id'],b['revision'])
            elif path=='/api/issue':out=books.issue(workbook,b['id'],b['revision'])
            elif path=='/api/revise':out=current.revise(b['id'])
            elif path=='/api/import':
                documents=import_pdf_documents(base64.b64decode(b['data'],validate=True),current.settings())
                if len(documents)==1:
                    if documents[0].get('import_error'):raise ValueError(documents[0]['import_error'])
                    out=documents[0]
                else:out={'combined_ledgers':True,'ledger_count':len(documents),'parties':[{'party':d.get('party',''),'error':d.get('import_error')} for d in documents]}
            elif path=='/api/territory-report':out=territory_report(books,b.get('filters'))
            elif path in ('/api/allocation-review-preview','/api/allocation-review-apply'):out=review_allocation(current,b,apply=path.endswith('-apply'))
            elif path in ('/api/allocation-clear-preview','/api/allocation-clear-apply'):out=clear_allocations(current,b,apply=path.endswith('-apply'))
            elif path=='/api/workbook-print':out=workbook_print(current,books.metadata(workbook),b)
            elif path=='/api/report':
                out=report(books,b.get('filters'))
                if b.get('csv'):out={'csv':csv_text(out['rows']),'rows':len(out['rows']),'notes':out['notes']}
            elif path=='/api/product-csv':
                record=current.calculation_record(b['record'])
                if record.get('workbook_id',workbook)!=workbook:raise ValueError('Calculation belongs to another workbook')
                cfg=record.get('frozen_settings') or current.settings()
                computed=record.get('result') if record.get('status') in ('finalised','issued') else current.calculate(record)
                rows=product_rows(record,computed,cfg,books.metadata(workbook));out={'csv':csv_text(rows),'rows':len(rows)}
            elif path=='/api/audit-import':
                out={'documents':import_pdf_documents(base64.b64decode(b['data'],validate=True),current.settings())}
            elif path=='/api/audit-review':
                from ledger_audit import save_audit_review
                out=save_audit_review(current,b)
            elif path=='/api/audit-map':
                cfg=current.settings()
                if b['version']!=cfg['version']:raise ValueError('Settings changed; refresh before saving narration mapping')
                from ledger_audit import norm,cn_product_key
                key=norm(b['narration']);crop=str(b['crop']).strip()
                if not key:raise ValueError('This CN has no narration to map; review the source voucher')
                known=set(cfg.get('crops',[]))|{p['crop'] for p in cfg['products']}
                if crop and crop not in known:raise ValueError('Choose a saved crop in this workbook')
                classification=b.get('classification', 'scheme' if crop else 'unclassified')
                if classification not in ('unclassified','scheme','freight','other','material_return'):raise ValueError('Choose a valid CN classification')
                if classification=='unclassified' and crop:classification='scheme'
                if classification!='scheme':crop=''
                product=str(b.get('product') or '').strip()
                if product:
                    p=next((p for p in cfg['products'] if p['id']==product and not p.get('deleted_at')),None)
                    if classification!='scheme' or not p or p['crop']!=crop:raise ValueError('Choose a product belonging to this crop for a scheme CN')
                pm=cfg.setdefault('audit_product_mappings',{})
                product_key=str(b.get('product_mapping_key') or '')
                if product or product_key:
                    evidence=b.get('voucher')
                    if not isinstance(evidence,dict) or norm(evidence.get('narration'))!=key or cn_product_key(evidence)!=product_key:raise ValueError('Product attribution needs current voucher evidence; rerun the ledger check')
                    if product:pm[product_key]=product
                    else:pm.pop(product_key,None)
                cfg.setdefault('audit_cn_classifications',{})[key]=classification
                mappings=cfg.setdefault('audit_crop_mappings',{})
                if crop:mappings[key]=crop
                else:mappings.pop(key,None)
                out=current.save_settings(cfg)
            elif path=='/api/audit-check':
                out=audit_documents(b['documents'],b['start'],b['end'],current.settings())
                if b.get('coverage_errors'):
                    from ledger_nrv import mark_incomplete
                    mark_incomplete(out['posted_CN_NRV'],'Some uploaded PDFs failed or were not read; combined crop/product averages are withheld')
                    out['warnings'] += [{'party':'Upload coverage','message':str(error)} for error in b['coverage_errors']]

            elif path=='/api/audit-bulk-nrv':
                from ledger_nrv import saved_bulk_report
                out=saved_bulk_report(current,b['start'],b['end'])
            elif path=='/api/year-match':out=match_years(b['previous'],b['current'])
            elif path=='/api/year-pair':out=analyse_pair(b['previous'],b['current'],b.get('identity_reason',''))
            elif path=='/api/year-link-save':out=books.link_year(workbook,b)
            elif path=='/api/reparse':out=parse_saved_source(b['source'],current.settings())
            elif path=='/api/compare-import':out=compare_import(b['existing'],b['incoming'])
            elif path=='/api/workbooks':out=books.create(b,workbook)
            elif path=='/api/bulk-import':out=books.bulk_import(workbook,b)
            elif path=='/api/bulk-document':out=bulk_document(current,b['id'])
            elif path=='/api/bulk-resolve':out=resolve_bulk(current,b['id'],b['record_id'])
            elif path=='/api/restore':out=books.restore(b['backup'],b.get('confirm',False))
            else:return self.respond({'error':'Not found'},404)
            self.respond(out)
        except Exception as e:self.respond({'error':str(e)},400)
if __name__=='__main__':
    # Standalone builds request an available port atomically; explicit CN_PORT wins.
    port=int(os.environ.get('CN_PORT','0' if getattr(sys,'frozen',False) else '8765'))
    server=ThreadingHTTPServer(('127.0.0.1',port),Handler);port=server.server_address[1]
    print(f'All-crop CN calculator: http://127.0.0.1:{port} (keep this window open)',flush=True)
    if '--no-browser' not in sys.argv:webbrowser.open(f'http://127.0.0.1:{port}')
    try:server.serve_forever()
    except KeyboardInterrupt:pass
