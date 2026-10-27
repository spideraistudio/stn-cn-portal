"""Additional text-PDF statement adapters; the preserved Tally reader is unchanged.

Detection is based on printed structure, never a company-name substring. Every
posting is reconciled against printed columns/balances. Unknown units remain
unknown; calculated item extensions are explicitly marked, not printed evidence.
"""
import copy
import hashlib
import io
import re
from collections import Counter
from datetime import datetime
from decimal import Decimal

from importer import import_pdf_documents as legacy_import, product_suggestion
from tally_detailed import get_party

NUM = r'-?[\d,]+(?:\.\d+)?'
MONEY = r'[\d,]+\.\d{2}'
DAY = r'\d{1,2}-[A-Za-z]{3}-\d{2}'
SLASH_DAY = r'\d{2}/\d{2}/\d{4}'
STOCK = {'sale', 'return', 'ipt_in', 'ipt_out'}
FORMAT_VERSION = 1

def number(value):
    n = Decimal(str(value).replace(',', '').replace('(-)', '-'))
    if not n.is_finite():
        raise ValueError('Non-finite statement amount')
    return n

def iso(value):
    return datetime.strptime(value, '%d/%m/%Y' if '/' in value else '%d-%b-%y').date().isoformat()

def source_line(row):
    return {k: row[k] for k in ('page', 'line', 'text')}

def page_rows(page, n):
    rows = []
    for i, line in enumerate(page.extract_text_lines(return_chars=False), 1):
        words = page.crop((0, max(0, line['top'] - .1), page.width,
                           min(page.height, line['bottom'] + .1))).extract_words()
        rows.append({'page': n, 'line': i, 'text': line['text'].strip(),
                     'words': [{k: w[k] for k in ('text', 'x0', 'x1')} for w in words]})
    return rows

def columns(row):
    out = {}
    for word in row['words']:
        if word['text'] in ('Debit', 'Credit'):
            out[word['text'].lower()] = word['x1']
    if set(out) != {'debit', 'credit'} or abs(out['debit']-out['credit']) < 10:
        raise ValueError('Cannot distinguish the printed debit/credit columns')
    return out

def monetary_cells(row, cols, tolerance=3):
    out = {'debit': Decimal(0), 'credit': Decimal(0)}
    found = set()
    for w in row['words']:
        if not re.fullmatch(MONEY, w['text']):
            continue
        matches = [key for key, x in cols.items() if abs(w['x1']-x) <= tolerance]
        if len(matches) > 1:
            raise ValueError('Ambiguous amount column on page '+str(row['page']))
        if matches:
            key = matches[0]
            if key in found:
                raise ValueError('Multiple amounts in '+key+' column')
            found.add(key); out[key] = number(w['text'])
    return out, found

def printed_balance(text):
    m = re.search(r'('+MONEY+r')\s+(DB|DR|CR)\s*$', text, re.I)
    if not m:
        raise ValueError('Printed running balance or DB/CR direction is missing: '+text)
    return number(m[1]) * (-1 if m[2].upper() == 'CR' else 1)

def require_equal(actual, expected, label):
    if actual != expected:
        raise ValueError(label+' does not reconcile; check the source PDF (difference '+str(actual-expected)+')')

def item(name, qty, unit, rate, value, row, settings, calculated=False):
    name = name.strip()
    hint = product_suggestion(name, settings)
    # Printed grams spelling used by these statements, without changing catalogue names.
    pack = re.search(r'(\d+(?:\.\d+)?)\s*(grms?|grams?)\b', name, re.I)
    if pack and hint['detected_packing_kg'] is None:
        hint['detected_packing_kg'] = str(number(pack[1])/1000)
        hint['product'] = None
        hint['reason'] = 'Printed gram packing detected; choose or add the matching product'
    return {'name': name, 'product': hint['product'], 'mapping_suggestion': hint,
            'mapping_confirmed': False, 'qty': str(number(qty)), 'unit': unit,
            'rate': str(number(rate)), 'amount': str(number(value)),
            'source_page': row['page'], 'source_line': row['line'],
            'amount_basis': 'calculated_qty_times_rate' if calculated else 'printed',
            'unit_basis': 'not_printed' if unit == 'unknown' else 'printed'}

def entry(date, kind, reference, cells, row, family, classification=False):
    return {'id': '', 'date': date, 'kind': kind, 'reference': reference,
            'debit': str(cells['debit']), 'credit': str(cells['credit']),
            'items': [], 'source_lines': [source_line(row)], 'reviewed': False,
            'remarks': '', 'classification_required': classification,
            'voucher_family': family}

def complete_document(pages, entries, party, issuer, start, end, opening, closing,
                      fmt, file_sha, settings, notes=None, summary=None, location='', address='', implicit=False):
    if not entries:
        raise ValueError('No recognised vouchers found in this statement')
    if closing is None:
        raise ValueError('Statement has no recognised closing balance')
    require_equal(opening+sum((number(e['debit'])-number(e['credit']) for e in entries), Decimal(0)), closing, 'Closing balance')
    warnings = list(notes or []); seen = Counter()
    for e in entries:
        for i in e['items']:
            name=' '.join(i['name'].upper().split()).rstrip(' (')
            confirmed = (issuer.upper()=='REMIK AGRI SEEDS PVT. LTD.' and name=='SSG (WHITE) REMIK MILKY WHITE 3 KG') or (issuer.upper()=='DHANWEL HYBRID SEEDS LIMITED' and name=='SOYABEAN SEEDS KDS-726')
            if i['unit']=='unknown' and confirmed:
                i.update(unit='packet', unit_basis='confirmed_profile', unit_confirmation='Owner confirmed on 2026-10-26: quantity and rate are per packet; packing only where printed or separately mapped')

    for e in entries:
        if not start <= e['date'] <= end:
            raise ValueError('Voucher date is outside its printed report period')
        ident = '|'.join((issuer, party, e['date'], e['voucher_family'], e['reference']))
        seen[ident] += 1
        e['id'] = hashlib.sha256((ident+'|'+str(seen[ident])).encode()).hexdigest()[:24]
        if seen[ident] > 1:
            warnings.append('Repeated date/reference retained as separate source vouchers; review duplicates')
        issues = []
        if e['kind'] in STOCK and not e['items']:
            issues.append('Itemised stock details are missing; obtain the invoice before calculating CN')
        if any(i['unit'] == 'unknown' for i in e['items']):
            issues.append('Quantity unit is not printed. Confirm kg or packet/bag for each item')
        if any(i['amount_basis'] != 'printed' for i in e['items']):
            issues.append('Item amounts are working quantity × rate, not printed amounts. Verify against the invoice')
        if e['items']:
            value = sum((number(i['amount']) for i in e['items']), Decimal(0))
            diff = value-abs(number(e['debit'])-number(e['credit']))
            if diff:
                e['item_total_difference'] = str(diff)
                issues.append('Item working total differs from voucher by '+str(diff)+'. Review actual line amounts/tax/discount; no split was guessed')
        e['import_notes'] = issues
        for i in e['items']:
            if not i.get('product'):
                warnings.append('Map product/packing: '+i['name'])
        warnings.extend('Source review '+e['reference']+': '+v for v in issues)
        e['original'] = copy.deepcopy(e)
    text = '\n'.join(r['text'] for p in pages for r in p)
    source = {'format': fmt, 'schema_version': FORMAT_VERSION, 'sha256': file_sha,
              'file_sha256': file_sha, 'text': text, 'pages': len(pages),
              'issuer': issuer, 'report_start': start, 'report_end': end,
              'opening_omitted_zero': implicit, 'stock_summary': summary}
    if implicit:
        warnings.append('Opening balance was not printed; zero is implied by the first running balance and verified totals. Confirm it in Check Ledger')
    details = {'party': party, 'location': location, 'state': '', 'address': address}
    return {**details, 'party_details': details, 'opening': str(opening), 'closing': str(closing),
            'entries': entries, 'warnings': list(dict.fromkeys(warnings)), 'source': source, 'reconciled': True}


def parse_tally_balance(pages, settings, file_sha):
    first = '\n'.join(r['text'] for r in pages[0]); party, _ = get_party(first)
    period = re.search(r'('+DAY+r')\s+to\s+('+DAY+r')', first)
    if not period:
        raise ValueError('Ledger reporting period is missing')
    start, end = map(iso, period.groups()); issuer = pages[0][0]['text']
    lines=first.splitlines(); marker=lines.index('Ledger Account')
    address=' '.join(lines[marker+1:next(i for i,l in enumerate(lines) if period[0] in l)])
    entries=[]; current=None; opening=None; closing=None; last_date=None
    debit=credit=Decimal(0); notes=[]; summary=None; closed=False
    for page in pages:
        text='\n'.join(r['text'] for r in page)
        page_party, _ = get_party(text)
        if page[0]['text'] != issuer or page_party != party or not re.search(re.escape(period[0]), text):
            raise ValueError('Mixed party/report periods require separate PDFs')
        if 'Stockitem Name' in text and 'Nett Sales' in text:
            if not closed:
                raise ValueError('Stock summary appears before the ledger closing balance')
            if summary is not None:
                raise ValueError('Repeated stock summary page needs review')
            m=re.search(r'^('+NUM+r')\s+PKT\s+('+MONEY+r')\s+('+NUM+r')\s+PKT\s+('+MONEY+r')\s+('+NUM+r')\s+PKT\s+('+MONEY+r')\s*$',text,re.M|re.I)
            if not m:
                raise ValueError('Stock summary totals are not recognised; summary was not imported as vouchers')
            expected=list(map(number,m.groups()));sales=[i for e in entries if e['voucher_family']=='Sales' for i in e['items']];returns=[i for e in entries if e['voucher_family']=='Sales Return' for i in e['items']]
            actual=[sum((number(i[k]) for i in rows),Decimal(0)) for rows in (sales,returns) for k in ('qty','amount')]
            actual += [actual[0]-actual[2],actual[1]-actual[3]]
            for a,b in zip(actual,expected):require_equal(a,b,'Stock summary total')
            summary={'page':page[0]['page'],'verified':True,'supply_qty':str(actual[0]),'supply_value':str(actual[1]),'return_qty':str(actual[2]),'return_value':str(actual[3]),'net_qty':str(actual[4]),'net_value':str(actual[5]),'unit':'packet'}
            notes.append('Printed stock-summary page verified against vouchers; not added again as transactions')
            continue
        header=next((r for r in page if re.search(r'Date.*Vch Type.*Debit.*Credit.*Balance',r['text'])),None)
        if not header:
            raise ValueError('Unrecognised ledger page; no page was silently skipped')
        cols=columns(header)
        for row in page:
            if row['line']<=header['line']:continue
            line=row['text'];cells,found=monetary_cells(row,cols)
            if re.search(r'\b(Carried Over|Brought Forward)\b',line):
                if found!={'debit','credit'}:raise ValueError('Carry totals missing')
                require_equal(cells['debit'],debit,'Debit carry total');require_equal(cells['credit'],credit,'Credit carry total');continue
            if 'Closing Balance' in line:
                if closing is not None or len(found)!=1:raise ValueError('Ambiguous closing balance')
                closing=cells['credit']-cells['debit']  # balancing row is on the opposite side
                require_equal(debit-credit,closing,'Closing balance');closed=True;current=None;continue
            if re.fullmatch(MONEY+r'\s+'+MONEY,line):
                expected=(max(debit,credit),)*2 if closed else (debit,credit)
                vals=list(map(number,re.findall(MONEY,line)))
                for a,b in zip(vals,expected):require_equal(a,b,'Ledger printed total')
                continue
            m=re.match(r'^(?:('+DAY+r')\s+)?(To|By)\s+(.+)$',line,re.I)
            if m:
                if closed:raise ValueError('Voucher after closing balance')
                if m[1]:last_date=iso(m[1])
                body=m[3]
                if 'Opening Balance' in body:
                    if opening is not None or entries or len(found)!=1:raise ValueError('Invalid opening balance row')
                    opening=cells['debit']-cells['credit'];debit=cells['debit'];credit=cells['credit'];continue
                if opening is None or last_date is None or len(found)!=1:raise ValueError('Voucher lacks opening/date/amount evidence')
                # Read voucher type and reference from their own header columns.
                ws=header['words'];vt=next(w['x0'] for w in ws if w['text']=='Vch');vn=[w['x0'] for w in ws if w['text']=='Vch'][1]
                type_text=' '.join(w['text'] for w in row['words'] if vt-2<=w['x0']<vn-12)
                ref=' '.join(w['text'] for w in row['words'] if vn-12<=w['x0']<min(cols.values())-55)
                if not ref:raise ValueError('Voucher reference is missing')
                if re.match('Sales',type_text,re.I):kind,family='sale','Sales'
                elif re.match('Credit Note',type_text,re.I):
                    kind,family=('return','Sales Return') if re.search(r'Sales?\s+Retu?rn|Sales?\s+Retun',body,re.I) else ('posted_cn','Credit Note')
                elif re.match('Receipt',type_text,re.I):kind,family='receipt','Receipt'
                elif re.match('Journal',type_text,re.I):kind,family=('posted_cn' if cells['credit'] else 'adjustment'),'Journal'
                else:kind,family='unknown',type_text or 'Unknown'
                if (kind=='sale' and not cells['debit']) or (kind in ('return','receipt','posted_cn') and not cells['credit']):raise ValueError('Voucher type disagrees with printed debit/credit column')
                current=entry(last_date,kind,ref,cells,row,family,kind in ('unknown','adjustment'))
                debit+=cells['debit'];credit+=cells['credit'];balance=printed_balance(line);require_equal(debit-credit,balance,'Running balance on page '+str(row['page']))
                current['running_balance']=str(balance);entries.append(current);continue
            if closed:
                if re.match(r'^\d',line):raise ValueError('Unrecognised numeric row after closing')
                continue
            if line.lower().startswith('continued'):continue
            it=re.match(r'^(.*?)\s+('+NUM+r')\s+(PKT|BAG|KG|KGS)\s+('+MONEY+r')\s*/\s*(PKT|BAG|KG|KGS)\s+('+MONEY+r')$',line,re.I)
            if it:
                if current is None:raise ValueError('Item has no parent voucher')
                name,qty,unit,rate,rate_unit,value=it.groups()
                if unit.upper().rstrip('S')!=rate_unit.upper().rstrip('S'):raise ValueError('Quantity/rate unit mismatch')
                current['items'].append(item(name,qty,'kg' if unit.upper() in ('KG','KGS') else 'packet',rate,value,row,settings))
            elif re.match(r'^'+DAY+r'\b',line):raise ValueError('Unrecognised dated voucher: '+line)
            elif re.search(r'\b(?:PKT|BAG|KG)\s+.*?/\s*(?:PKT|BAG|KG)',line,re.I):raise ValueError('Unrecognised item row: '+line)
            if current:current['source_lines'].append(source_line(row))
    for e in entries:
        text=' '.join(r['text'] for r in e['source_lines'][1:])
        m=re.search(r'\b(?:MATERIAL|MATIREAL|GOODS)\s+(RECEIVED\s+FROM|(?:SENT|DISPATCHED|DESPATCHED)\s+TO)\s+(.+)',text,re.I)
        if m and e['items']:
            e['kind']='ipt_in' if m[1].upper().startswith('RECEIVED') else 'ipt_out';e['classification_required']=False;e['transfer_party']=m[2].strip()
        if e['voucher_family']=='Journal' and e['kind']=='posted_cn' and not e['items']:
            e['posting_label']='Posted freight / expense CN (Journal)'
    return complete_document(pages,entries,party,issuer,start,end,opening,closing,'tally-balance-columns-v1',file_sha,settings,notes,summary,address=address)


def parse_account_statement(pages,settings,file_sha,compact):
    first='\n'.join(r['text'] for r in pages[0]);pm=re.search(r'^Account Statement For (.+)$',first,re.M)
    period=re.search(r'From\s+('+SLASH_DAY+r')\s+To\s+('+SLASH_DAY+r')',first,re.I)
    if not pm or not period:raise ValueError('Account name or reporting dates not recognised')
    party=pm[1].strip();issuer=pages[0][0]['text'];start,end=map(iso,period.groups())
    location=re.search(r'\(([^()]*)\)\s*$',party);location=location[1].strip() if location else ''
    entries=[];current=None;debit=credit=Decimal(0);opening=None;closing=None;implicit=False;pending_name=[];last_total=False
    for page in pages:
        text='\n'.join(r['text'] for r in page)
        if 'Account Statement For '+party not in text or period[0] not in text or page[0]['text']!=issuer:raise ValueError('Mixed company/party/period pages require separate PDFs')
        header=next((r for r in page if re.match(r'^Date\b',r['text']) and 'Closing Balance' in r['text'] and 'Debit' in r['text'] and 'Credit' in r['text']),None)
        if not header:raise ValueError('Statement table header missing')
        cols=columns(header)
        for row in page:
            if row['line']<=header['line']:continue
            line=row['text'];cells,found=monetary_cells(row,cols,20 if compact else 3)
            if re.match(r'^[CB]/F\s*->',line):
                if found!={'debit','credit'}:raise ValueError('Page carry totals missing')
                require_equal(cells['debit'],debit,'Debit carry total');require_equal(cells['credit'],credit,'Credit carry total');continue
            if line.startswith('Opening Balance'):
                if entries or opening is not None or len(found)!=1:raise ValueError('Unexpected opening balance')
                opening=cells['debit']-cells['credit'];require_equal(opening,printed_balance(line),'Opening balance');debit=cells['debit'];credit=cells['credit'];continue
            if line.startswith('Total :'):
                require_equal(cells['debit'],debit,'Printed debit total');require_equal(cells['credit'],credit,'Printed credit total');last_total=True;continue
            if line.startswith('Closing Balance :'):
                if closing is not None or not last_total:raise ValueError('Closing balance requires printed totals')
                closing=printed_balance(line);require_equal(debit-credit,closing,'Closing balance');continue
            m=re.match(r'^('+SLASH_DAY+r')\s+(.+)$',line)
            if m:
                if closing is not None:raise ValueError('Voucher after closing balance')
                if pending_name:
                    raise ValueError('Item name has no quantity/rate before the next voucher: '+' '.join(pending_name))
                if len(found)!=1:raise ValueError('Voucher has ambiguous debit/credit amount')
                balance=printed_balance(line)
                if opening is None:
                    opening=balance-cells['debit']+cells['credit']
                    if opening!=0:raise ValueError('Nonzero opening balance is not printed; obtain a complete statement')
                    implicit=True
                if compact:
                    # Locate by header geometry, allowing the table to move on the page.
                    hx=next(w['x0'] for w in header['words'] if w['text']=='Type');px=next(w['x0'] for w in header['words'] if w['text']=='Particulars')
                    types=[w for w in row['words'] if hx-12<=w['x0']<px and re.fullmatch(r'[A-Za-z/]+',w['text'])]
                    if len(types)!=1:raise ValueError('Unknown or ambiguous document type: '+line)
                    kind_text=types[0]['text'];ref=' '.join(w['text'] for w in row['words'] if w['x0']>row['words'][0]['x1']+2 and w['x0']<hx-12)
                    kind={'Sale':'sale','SRet':'return','BRct':'receipt','C/N':'posted_cn','Purc':'adjustment','PRet':'adjustment'}.get(kind_text,'unknown')
                    reference=ref or 'Unnumbered '+kind_text+' p'+str(row['page'])+' l'+str(row['line'])
                else:
                    kind='unknown';kind_text='Unclassified';reference='Unnumbered p'+str(row['page'])+' l'+str(row['line'])
                current=entry(iso(m[1]),kind,reference,cells,row,kind_text,kind in ('adjustment','unknown'))
                debit+=cells['debit'];credit+=cells['credit'];require_equal(debit-credit,balance,'Running balance on page '+str(row['page']))
                current['running_balance']=str(balance);entries.append(current);last_total=False;continue
            if not current:
                if line:raise ValueError('Unexpected statement content before first voucher')
                continue
            if closing is not None:
                if line:raise ValueError('Unexpected statement content after closing')
                continue
            current['source_lines'].append(source_line(row))
            if not compact:
                if line in ('Sale','SRet','Receipt','BRct','C/N'):
                    current.update(kind={'Sale':'sale','SRet':'return','Receipt':'receipt','BRct':'receipt','C/N':'posted_cn'}[line],voucher_family=line,classification_required=False);continue
                if line.startswith('Bill No '):current['reference']=line[len('Bill No '):].strip();continue
                it=re.match(r'^(.*?)\s+\(\s*('+NUM+r')\s*\*\s*('+MONEY+r')\s+('+MONEY+r')\s*\)$',line)
                if it:
                    name,qty,rate,value=it.groups();current['items'].append(item(name,qty,'unknown',rate,value,row,settings));continue
                if '(' in line and '*' in line:raise ValueError('Unrecognised quantity/rate detail: '+line)
            else:
                it=re.fullmatch(r'Qty\s*:\s*('+NUM+r')\s+Rate\s*:\s*('+MONEY+r')',line,re.I)
                if it:
                    if not pending_name:raise ValueError('Quantity/rate has no product name')
                    name=' '.join(pending_name);pending_name=[]
                    current['items'].append(item(name,it[1],'unknown',it[2],str(number(it[1])*number(it[2])),row,settings,True));continue
                if re.match(r'Qty\s*:',line,re.I):raise ValueError('Unrecognised item quantity/rate row')
                if current['kind'] in STOCK|{'adjustment'}:
                    if line.upper()=='GERMINATION':current['remarks']=(current['remarks']+' '+line).strip();continue
                    pending_name.append(line)
    if pending_name:raise ValueError('Last product name has no quantity/rate detail')
    for e in entries:
        if e['kind']=='sale' and number(e['debit'])==0 or e['kind'] in ('return','receipt','posted_cn') and number(e['credit'])==0:
            raise ValueError('Document type disagrees with the printed debit/credit column')
    return complete_document(pages,entries,party,issuer,start,end,opening,closing,'account-compact-v1' if compact else 'account-item-detail-v1',file_sha,settings,location=location,implicit=implicit)


def _import_pdf_documents(data,settings):
    import pdfplumber
    with pdfplumber.open(io.BytesIO(data)) as pdf:
        first=pdf.pages[0].extract_text() or ''
        account=bool(re.search(r'^Account Statement For .+',first,re.M) and re.search(r'From\s+'+SLASH_DAY+r'\s+To\s+'+SLASH_DAY,first,re.I))
        tally=bool('Ledger Account' in first and re.search(r'Date.*Vch Type.*Debit.*Credit.*Balance',first) and re.search(r'\b(?:To|By) Opening Balance',first))
        if not account and not tally:
            return legacy_import(data,settings)
        pages=[page_rows(page,n) for n,page in enumerate(pdf.pages,1)]
        sha=hashlib.sha256(data).hexdigest()
        if tally:return [parse_tally_balance(pages,settings,sha)]
        return [parse_account_statement(pages,settings,sha,'Doc/Chq.' in first)]


def import_pdf_documents(data, settings):
    try:
        return _import_pdf_documents(data, settings)
    except ValueError:
        raise
    except Exception as exc:
        raise ValueError('Cannot read this PDF; choose a complete, unlocked text-based statement') from exc
