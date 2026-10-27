"""Conservative, text-based Tally statement adapter. No OCR or external calls."""
import re,io,hashlib,copy
from datetime import datetime
from decimal import Decimal
from engine import D

MONEY=r'-?[\d,]+\.\d{2}'
ITEM=re.compile(r'^(.*?)\s+([\d,]+\.\d+)\s+(pkt|Bag|kg)\s+@\s+('+MONEY+r')\s+('+MONEY+r')$',re.I)
DATE=re.compile(r'^(\d{2}-[A-Za-z]{3}-\d{2})\s+(.*)$')
def amount(v):return str(Decimal(v.replace(',','')))
def product_suggestion(name,settings):
    pack=re.search(r'(\d+(?:\.\d+)?)\s*(kg|kgs|gm|gms|g)\b',name,re.I)
    kg=Decimal(pack[1])/(1000 if pack[2].lower() in ('gm','gms','g') else 1) if pack else None
    named=[]
    for p in settings['products']:
        if p.get('deleted_at'):continue
        aliases=p.get('aliases',[])+[p['name']]
        if any(alias and re.search(r'(?<!\w)'+re.escape(alias)+r'(?!\w)',name,re.I) for alias in aliases):
            if p['name']=='14D14' and 'gold' in name.casefold():continue
            named.append(p)
    candidates=[p for p in named if kg is None or D(p['packing_kg'])==kg]
    selected=candidates[0] if len(candidates)==1 else None
    return {'product':selected['id'] if selected else None,'crop':selected['crop'] if selected else None,'segment':selected['segment'] if selected else None,'packing_kg':selected['packing_kg'] if selected else None,'detected_packing_kg':str(kg) if kg is not None else None,'candidates':[p['id'] for p in (candidates or named)],'reason':('Name and packing match' if kg is not None else 'Unique catalogue name match; check packing') if selected else 'Several possible products; choose the correct crop/packing' if len(candidates)>1 else 'No matching catalogue product/packing; choose or add the correct product'}

def match_product(name,settings):return product_suggestion(name,settings)['product']

def classify_stock_transfer(entry):
    """Narration overrides invoice/return headings, never creates another voucher."""
    directions=set();parties=[];generic=False
    for source in entry.get('source_lines',[])[1:]:
        line=source['text'].strip()
        if ITEM.match(line):continue
        received=re.match(r'^(?:GOODS?\s+)?(?:REC(?:EIVED|IVED)|RECEIVE|RECD\.?)\s+FROM\s+(.+)$',line,re.I)
        sent=re.match(r'^(?:GOODS?\s+)?(?:DISPATCH(?:ED)?|DESPATCH(?:ED)?|SENT|TRANSFER(?:RED)?)\s+TO\s+(.+)$',line,re.I)
        explicit=re.match(r'^(?:IPT|INTER[ -]?PARTY(?:\s+STOCK)?\s+TRANSFER)\s*[-:]?\s*(IN(?:WARD)?|OUT(?:WARD)?|RECEIVED|GIVEN)\b\s*(?:FROM|TO)?\s*[-:]?\s*(.*)$',line,re.I)
        if received:directions.add('ipt_in');parties.append(received[1].strip())
        if sent:directions.add('ipt_out');parties.append(sent[1].strip())
        if explicit:
            directions.add('ipt_in' if explicit[1].upper() in ('IN','INWARD','RECEIVED') else 'ipt_out')
            if explicit[2]:parties.append(explicit[2].strip())
        if re.search(r'\bIPT\b|INTER[ -]?PARTY.*TRANSFER',line,re.I):generic=True
    if len(directions)==1:
        entry.update(kind=next(iter(directions)),classification_hint='IPT',classification_required=False)
        if parties:entry['transfer_party']='; '.join(dict.fromkeys(parties))
    elif directions or generic:
        entry.update(kind='unknown',classification_hint='IPT',classification_required=True)


def extract_party_details(text):
    lines=[line.strip() for line in text.splitlines() if line.strip()]
    marker=next((i for i,line in enumerate(lines) if re.match(r'^For \d{2}-\w{3}-\d{2} to \d{2}-\w{3}-\d{2}$',line)),None)
    if marker is None or marker+1>=len(lines):return {'party':'','location':'','state':'','address':''}
    party=lines[marker+1];address=[]
    for line in lines[marker+2:]:
        if re.match(r'^(Phone|Data as of|Page |Date Particulars|GSTIN|\d{2}-\w{3}-\d{2})',line,re.I):break
        address.append(line)
    address=' '.join(address)
    states=['Andaman and Nicobar Islands','Andhra Pradesh','Arunachal Pradesh','Assam','Bihar','Chandigarh','Chhattisgarh','Dadra and Nagar Haveli and Daman and Diu','Delhi','Goa','Gujarat','Haryana','Himachal Pradesh','Jammu and Kashmir','Jharkhand','Karnataka','Kerala','Ladakh','Lakshadweep','Madhya Pradesh','Maharashtra','Manipur','Meghalaya','Mizoram','Nagaland','Odisha','Puducherry','Punjab','Rajasthan','Sikkim','Tamil Nadu','Telangana','Tripura','Uttar Pradesh','Uttarakhand','West Bengal']
    found=[state for state in states if re.search(r'(?<!\w)'+re.escape(state)+r'(?!\w)',address,re.I)]
    state=found[0] if len(found)==1 else ''
    # The locality after the firm-name comma is explicit in these Tally headers.
    location=party.split(',',1)[1].strip() if ',' in party else ''
    if not location and state:
        tail=re.split(re.escape(state),address,flags=re.I)[0].rstrip(' ,')
        parts=[part.strip() for part in tail.split(',') if part.strip()]
        if parts and not re.search(r'\d|^Pro:',parts[-1],re.I):location=parts[-1]
    return {'party':party,'location':location,'state':state,'address':address}

def import_pdf_documents(data,settings):
    try:import pdfplumber
    except ImportError:raise ValueError('PDF reader is not installed. Run setup first; manual entry remains available.')
    try:
        with pdfplumber.open(io.BytesIO(data)) as pdf:
            pages=[page.extract_text() or '' for page in pdf.pages]
            if not any(p.strip() for p in pages):raise ValueError('Scanned PDF unsupported. Enter manually or export a text-based Tally PDF.')
            if any(re.search(r'^Ledger:\s|^Group:.*?\bLedger:|^Ledger Account\s*$|^.+?\s+Ledger Account\s*:',p,re.M|re.I) for p in pages):
                from tally_detailed import import_ledgers
                return import_ledgers(pdf,settings,hashlib.sha256(data).hexdigest())
    except ValueError:raise
    except Exception as exc:raise ValueError('Cannot read this PDF') from exc
    return [parse_statement_pages(pages,settings,{'sha256':hashlib.sha256(data).hexdigest(),'pages':len(pages),'text':'\n'.join(pages)})]

def import_pdf(data,settings):
    documents=import_pdf_documents(data,settings)
    if len(documents)!=1:raise ValueError('This PDF contains '+str(len(documents))+' party ledgers. Select a workbook and use Bulk Import.')
    if documents[0].get('import_error'):raise ValueError(documents[0]['import_error'])
    return documents[0]

def parse_saved_source(source,settings):
    if source.get('format')=='tally-detailed-ledger':
        from tally_detailed import parse_ledger
        if source.get('schema_version')!=1 or not source.get('structured_pages'):raise ValueError('Detailed statement source is incomplete; import the PDF again.')
        return parse_ledger(source['structured_pages'],settings,source=source)
    return parse_statement_pages([source['text']],settings,source)

def parse_statement_pages(pages,settings,source=None):
    text='\n'.join(pages)
    if 'Ledger Statement' not in text or 'Opening Balance' not in text or 'Closing Balance' not in text:raise ValueError('Unsupported statement layout: missing ledger markers')
    details=extract_party_details(text)
    party=re.search(r'For \d{2}-\w{3}-\d{2} to \d{2}-\w{3}-\d{2}\n([^\n]+)',text)
    closing=re.search(r'Closing Balance\s+(?:Rs\.\s*)?('+MONEY+')',text)
    if not closing:raise ValueError('Closing balance not recognised')
    entries=[];current=None;opening=None;warnings=[];source_balance=None
    for page_no,page in enumerate(pages,1):
        for line_no,line in enumerate(page.splitlines(),1):
            line=line.strip();m=DATE.match(line)
            if m:
                dt=datetime.strptime(m[1],'%d-%b-%y').date().isoformat();rest=m[2]
                vals=re.findall(MONEY,rest)
                if 'Opening Balance' in rest:
                    if opening is None:opening=amount(vals[-1]);source_balance=D(opening)
                    current=None;continue
                if not vals: warnings.append('Unknown dated line: '+line);continue
                # Require complete amount + running balance and recognised voucher family.
                if len(vals)!=2: warnings.append('Unexpected money columns: '+line);current=None;continue
                if rest.startswith('Receipt'):kind='receipt';credit=amount(vals[0]);debit='0'
                elif rest.startswith('Sales Invoice'):kind='sale';debit=amount(vals[0]);credit='0'
                elif rest.startswith('Credit Note'):
                    kind='return' if 'Sales Return' in rest else 'posted_cn';credit=amount(vals[0]);debit='0'
                elif rest.startswith(('Journal','Debit Note')):kind='adjustment';debit=credit='0'
                else:kind='unknown';debit=credit='0'
                delta=D(amount(vals[1]))-source_balance if source_balance is not None else None
                if kind in ('adjustment','unknown'):
                    if delta is None or abs(delta)!=D(amount(vals[0])):warnings.append('Running balance direction needs review: '+line)
                    debit=amount(vals[0]) if delta is not None and delta>=0 else '0';credit=amount(vals[0]) if delta is not None and delta<0 else '0'
                source_balance=D(amount(vals[1]))
                legacy_header=rest[:rest.rfind(vals[0])].strip();legacy_reference=legacy_header.split()[-1]
                header=rest[:next(re.finditer(MONEY,rest)).start()].strip();reference=header.split()[-1]
                identity=hashlib.sha256((dt+'|'+kind+'|'+reference).encode()).hexdigest()[:24]
                current={'id':identity,'date':dt,'kind':kind,'reference':reference,'debit':debit,'credit':credit,'running_balance':amount(vals[1]),'items':[],'source_lines':[{'page':page_no,'line':line_no,'text':line}],'reviewed':False,'remarks':'','classification_required':kind in ('adjustment','unknown')}
                legacy_id=hashlib.sha256((dt+'|'+kind+'|'+legacy_reference).encode()).hexdigest()[:24]
                if legacy_id!=identity:current['legacy_ids']=[legacy_id]
                entries.append(current)
                continue
            if current and re.search(r'\bSALES?\s+RETURN\b',line,re.I) and not DATE.match(line):
                current['kind']='return';current['classification_required']=False
            elif current and re.search(r'\bIPT\b|INTER[ -]?PARTY.*STOCK.*TRANSFER',line,re.I):
                current['classification_required']=True;current['classification_hint']='IPT';current['kind']='unknown'
            item=ITEM.match(line)
            if item:
                if current is None or current['kind'] not in ('sale','return','posted_cn','adjustment','unknown','ipt_in','ipt_out'):warnings.append('Item without recognised parent voucher: '+line);continue
                name,qty,unit,rate,value=item.groups()
                suggestion=product_suggestion(name,settings)
                it={'name':name,'product':suggestion['product'],'mapping_suggestion':suggestion,'mapping_confirmed':False,'qty':amount(qty),'unit':'kg' if unit.lower()=='kg' else 'packet','rate':amount(rate),'amount':amount(value),'source_page':page_no,'source_line':line_no}
                if not it['product']:warnings.append('Map product/packing: '+name)
                current['items'].append(it)
            if current and line and not any(x in line for x in ['DHANLAXMI','GSTIN/UIN','Ledger Statement','Closing Balance','Opening Balance','Page ','Date Particulars','Data as of','For ','Phone:','Pro:','Computer Generated','Bank:','A/c No:','IFSC:','Motipura,']):
                if not party or line!=party[1]:current['source_lines'].append({'page':page_no,'line':line_no,'text':line})
    if opening is None or not entries:raise ValueError('Opening balance or vouchers not recognised')
    running=D(opening)
    for e in entries:
        classify_stock_transfer(e)
        running+=D(e['debit'])-D(e['credit'])
        if running!=D(e['running_balance']):warnings.append('Running balance mismatch: '+e['reference'])
        # Credit-side non-stock journals are already-posted freight/expense CNs.
        # Keep the original adjustment-based ID for saved-draft re-read matching.
        if e['kind']=='adjustment' and D(e['credit'])>0 and not e['items'] and not e.get('classification_hint') and e['source_lines'][0]['text'].split(' ',1)[1].startswith('Journal'):
            e.update(kind='posted_cn',classification_required=False,posting_label='Posted freight / expense CN (Journal)')
        if e.get('items') and e['kind'] in ('posted_cn','adjustment','unknown') and not e.get('classification_hint'):
            e['classification_required']=True
        expected=abs(D(e['debit'])-D(e['credit'])) if e['kind'].startswith('ipt_') else D(e['debit']) if e['kind']=='sale' else D(e['credit'])
        if e['kind'] in ('sale','return','ipt_in','ipt_out') and sum((D(x['amount']) for x in e['items']),Decimal(0))!=expected:warnings.append('Incomplete item detail: '+e['reference'])
        e['original']=copy.deepcopy(e)
    if running!=D(closing[1].replace(',','')):warnings.append('Closing balance mismatch')
    return {**details,'party_details':details, 'opening':opening,'closing':amount(closing[1]),'entries':entries,'warnings':list(dict.fromkeys(warnings)),'source':source or {'sha256':hashlib.sha256(text.encode()).hexdigest(),'pages':len(pages),'text':text},'reconciled':running==D(amount(closing[1]))}

def source_content(e):
    # Catalogue hints, decimal formatting and within-date running-balance order are not voucher changes.
    def number(v):
        if v in (None,''):return v
        try:
            n=D(v)
            if n==0:return '0'
            text=format(n,'f');return text.rstrip('0').rstrip('.') if '.' in text else text
        except (ValueError,ArithmeticError):return v
    out={k:e.get(k) for k in ('date','kind','reference')}
    out.update({k:number(e.get(k)) for k in ('debit','credit')})
    out['items']=[{'name':i.get('name'),'unit':i.get('unit'),**{k:number(i.get(k)) for k in ('qty','rate','amount')}} for i in e.get('items',[])]
    return out

def compare_import(existing,incoming):
    old={e['id']:e for e in existing};out=[]
    for e in incoming:
        prev=old.get(e['id'])
        if prev is None:
            matches=[old[x] for x in e.get('legacy_ids',[]) if x in old]
            if len(matches)==1:
                prev=matches[0];e=copy.deepcopy(e);e['id']=prev['id']
        status='New' if prev is None else 'Already imported' if source_content(prev.get('latest_import_source') or prev.get('original',prev))==source_content(e.get('original',e)) else 'Changed'
        out.append({'status':status,'incoming':e,'existing':prev})
    return out
