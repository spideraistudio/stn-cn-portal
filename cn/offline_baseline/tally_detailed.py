"""Tally detailed group ledgers: geometry keeps debit/credit and page boundaries explicit."""
import copy,hashlib,re
from datetime import datetime
from decimal import Decimal
from importer import amount,product_suggestion,extract_party_details,classify_stock_transfer

MONEY=r'-?[\d,]+\.\d{2}'
DAY=r'\d{1,2}-[A-Za-z]{3}-\d{2}'
RANGE=re.compile(r'('+DAY+r')\s+to\s+('+DAY+r')')
VOUCHER=re.compile(r'^(?:('+DAY+r')\s+)?(Dr|Cr)\s+(.+)$',re.I)
ITEM=re.compile(r'^(.*?)\s+(-?[\d,]+(?:\.\d+)?)\s+(pkt|bag|kg|kgs)\s+(?:@\s*)?('+MONEY+r')\s*/\s*(pkt|bag|kg|kgs)\s+('+MONEY+r')$',re.I)

def iso(v):return datetime.strptime(v,'%d-%b-%y').date().isoformat()
def get_party(text):
    # A continuation can start with Ledger: too. Strip only the explicit report
    # suffix before the full first-page header matcher sees it as a new party.
    continued=re.search(r'^Ledger:\s*(.+?)\s+:\s*'+DAY+r'\s+to\s+'+DAY+r'(?:\s+Page\s+\d+)?\s*$',text,re.M|re.I)
    if continued:return continued[1].strip(),False
    first=re.search(r'^Ledger:\s*(.+)$',text,re.M)
    if first:return first[1].strip(),True
    compact=re.search(r'^Group:.*?\bLedger:\s*(.*?)\s+:\s*'+DAY+r'\s+to\s+'+DAY,text,re.M)
    if compact:return compact[1].strip(),False
    account_continued=re.search(r'^(.+?)\s+Ledger Account\s*:\s*'+DAY+r'\s+to\s+'+DAY+r'(?:\s+Page\s+\d+)?\s*$',text,re.M|re.I)
    if account_continued:return account_continued[1].strip(),False
    account_first=re.search(r'^([^\n]+)\nLedger Account\s*$',text,re.M|re.I)
    if account_first:return account_first[1].strip(),True
    raise ValueError('Detailed ledger page is missing its Ledger name')

def detailed_pages(pdf):
    pages=[]
    for n,page in enumerate(pdf.pages,1):
        lines=page.extract_text_lines(return_chars=False)
        text='\n'.join(x['text'] for x in lines);party,first=get_party(text)
        header=next((x for x in lines if re.search(r'\bVch Type\b',x['text']) and 'Debit' in x['text'] and 'Credit' in x['text']),None)
        if not header:raise ValueError('Debit/credit table header missing on page '+str(n))
        words=page.crop((0,max(0,header['top']-1),page.width,min(page.height,header['bottom']+1))).extract_words()
        debit=next((w['x1'] for w in words if w['text']=='Debit'),None);credit=next((w['x1'] for w in words if w['text']=='Credit'),None)
        if debit is None or credit is None or debit>=credit:raise ValueError('Cannot locate debit/credit columns on page '+str(n))
        pages.append({'page':n,'party':party,'first':first,'debit_right':debit,'credit_right':credit,'header_line':next(i for i,l in enumerate(lines,1) if l is header),'rows':[{'line':i,'text':l['text'],'right':l['x1']} for i,l in enumerate(lines,1)]})
    return pages

def group_pages(pages):
    groups=[]
    for page in pages:
        if not groups or page['party']!=groups[-1][0]['party'] or page['first']:
            groups.append([page])
        else:groups[-1].append(page)
    return groups

def side(row,page):
    d=abs(row['right']-page['debit_right']);c=abs(row['right']-page['credit_right'])
    if min(d,c)>3:raise ValueError('Ambiguous debit/credit amount on page '+str(page['page'])+', line '+str(row['line']))
    return 'debit' if d<c else 'credit'

def voucher_kind(body):
    if re.search(r'\bReceipt\b',body,re.I):return 'receipt','Receipt'
    if re.search(r'\bSales[ -]?Return\b',body,re.I):return 'return','Sales Return'
    if re.search(r'\bCredit\s+Note\b',body,re.I):return 'posted_cn','Credit Note'
    if re.search(r'\bJournal\b',body,re.I):return 'adjustment','Journal'
    if re.search(r'\bDebit\s+Note\b',body,re.I):return 'adjustment','Debit Note'
    if re.search(r'\b(?:Gujarat-)?Invoice\b',body,re.I):return 'sale','Invoice'
    return 'unknown','Unknown'

def parse_ledger(pages,settings,source=None,file_sha=None):
    party=pages[0]['party'];text='\n'.join(r['text'] for p in pages for r in p['rows']);period=RANGE.search(text)
    if not period:raise ValueError('Ledger period not recognised: '+party)
    start,end=iso(period[1]),iso(period[2]);entries=[];warnings=[];current=None;last_date=None;opening=Decimal(0);closing=None;debits=credits=Decimal(0);saw_opening=False;final_totals=None;closed=False
    first_text='\n'.join(r['text'] for r in pages[0]['rows']);address=[];after=False
    for line in first_text.splitlines():
        if line.startswith('Ledger:') or line.strip().casefold()=='ledger account':after=True;continue
        if after:
            if RANGE.search(line) or re.match(r'Page\s|Date\s',line):break
            address.append(line)
    fake='For '+datetime.strptime(period[1],'%d-%b-%y').strftime('%d-%b-%y')+' to '+datetime.strptime(period[2],'%d-%b-%y').strftime('%d-%b-%y')+'\n'+party+'\n'+'\n'.join(address)+'\nPhone:'
    details=extract_party_details(fake)
    for page in pages:
        for row in page['rows']:
            if row['line']<=page['header_line']:continue
            line=row['text'].strip()
            if re.search(r'\b(?:Carried Over|Brought Forward)\b',line):
                values=re.findall(MONEY,line)
                if len(values)!=2 or [Decimal(amount(v)) for v in values]!=[debits,credits]:warnings.append('Running balance carry totals require review on page '+str(page['page']))
                continue
            if 'Closing Balance' in line:
                values=re.findall(MONEY,line)
                if len(values)!=1:raise ValueError('Ambiguous closing balance: '+party)
                value=Decimal(amount(values[0]));closing=value if side(row,page)=='credit' else -value;closed=True;current=None;continue
            if closed:continue
            m=VOUCHER.match(line)
            if m:
                date_text,direction,body=m.groups()
                if date_text:last_date=iso(date_text)
                if 'Opening Balance' in body:
                    values=re.findall(MONEY,body)
                    if saw_opening or entries or len(values)!=1:raise ValueError('Unexpected opening balance: '+party)
                    value=Decimal(amount(values[0]));opening=value if side(row,page)=='debit' else -value;saw_opening=True;debits=max(opening,Decimal(0));credits=max(-opening,Decimal(0));current=None;continue
                if not last_date:raise ValueError('Voucher has no preceding printed date: '+party)
                value_match=re.search(r'\s('+MONEY+r')$',body)
                if not value_match:raise ValueError('Voucher amount not recognised: '+line)
                header=body[:value_match.start()].strip();reference=header.split()[-1];kind,family=voucher_kind(header)
                value=Decimal(amount(value_match[1]));column=side(row,page)
                debit=str(value) if column=='debit' else '0';credit=str(value) if column=='credit' else '0'
                debits+=Decimal(debit);credits+=Decimal(credit)
                id=hashlib.sha256((last_date+'|'+kind+'|'+reference).encode()).hexdigest()[:24]
                current={'id':id,'date':last_date,'kind':kind,'reference':reference,'debit':debit,'credit':credit,'running_balance':str(debits-credits),'items':[],'source_lines':[{'page':page['page'],'line':row['line'],'text':line}],'reviewed':False,'remarks':'','classification_required':kind in ('unknown','adjustment'),'voucher_family':family,'date_inherited':not bool(date_text)}
                if kind=='sale' and column!='debit' or kind in ('return','posted_cn','receipt') and column!='credit':current['classification_required']=True
                entries.append(current);continue
            values=re.findall(MONEY,line)
            if re.fullmatch(MONEY+r'\s+'+MONEY,line):
                final_totals=[Decimal(amount(v)) for v in values]
                if final_totals!=[debits,credits]:warnings.append('Running balance final totals require review: '+party)
                continue
            if line.lower().startswith('continued'):continue
            item=ITEM.match(line)
            if item:
                if current is None:raise ValueError('Item has no parent voucher: '+line)
                name,qty,unit,rate,rate_unit,value=item.groups();suggestion=product_suggestion(name,settings)
                if unit.lower().rstrip('s')!=rate_unit.lower().rstrip('s'):warnings.append('Incomplete item unit/rate detail: '+name)
                current['items'].append({'name':name,'product':suggestion['product'],'mapping_suggestion':suggestion,'mapping_confirmed':False,'qty':amount(qty),'unit':'kg' if unit.lower() in ('kg','kgs') else 'packet','rate':amount(rate),'amount':amount(value),'source_page':page['page'],'source_line':row['line']})
                if not suggestion['product']:warnings.append('Map product/packing: '+name)
            if current:current['source_lines'].append({'page':page['page'],'line':row['line'],'text':line})
    if closing is None:
        if final_totals is not None and final_totals==[debits,credits] and debits==credits:closing=Decimal(0)
        else:raise ValueError('Closing balance not recognised: '+party)
    if debits-credits!=closing:warnings.append('Closing balance mismatch: '+party)
    for e in entries:
        # Join wrapped narration lines without including bill-reference/cheque detail rows.
        narration=[]
        for x in e['source_lines'][1:]:
            if ITEM.match(x['text']) or re.match(r'^(?:Agst Ref|New Ref|Cheque/DD|Available Only)',x['text'],re.I):continue
            narration.append(x['text'])
        segments=[]
        marker=re.compile(r'^(?:(?:GOODS?\s+)?(?:REC(?:EIVED|IVED)|RECEIVE|RECD\.?|DISPATCH(?:ED)?|DESPATCH(?:ED)?|SENT|TRANSFER(?:RED)?)\s+(?:FROM|TO)\b|IPT\b|INTER[ -]?PARTY\b)',re.I)
        for line in narration:
            if marker.search(line):segments.append(line)
            elif segments and not re.match(r'^(?:DC\s*NO|CN\s+GIVEN|NEFT|RTGS|IMPS)',line,re.I):segments[-1]+=' '+line
        transfer_copy={**e,'source_lines':[e['source_lines'][0]]+[{'text':x} for x in segments]}
        classify_stock_transfer(transfer_copy)
        # Multiple independent IPT markers still get the existing ambiguity guard.
        if transfer_copy.get('classification_hint')=='IPT':
            for key in ('kind','classification_required','classification_hint','transfer_party'):
                if key in transfer_copy:e[key]=transfer_copy[key]
        if e['voucher_family']=='Journal' and Decimal(e['credit'])>0 and not e['items'] and not e.get('classification_hint'):e.update(kind='posted_cn',classification_required=False,posting_label='Posted freight / expense CN (Journal)')
        if e['items'] and e['kind'] in ('posted_cn','adjustment','unknown'):e['classification_required']=True
        if e['kind'] in ('sale','return','ipt_in','ipt_out'):
            expected=abs(Decimal(e['debit'])-Decimal(e['credit']))
            if not e['items'] or sum((Decimal(i['amount']) for i in e['items']),Decimal(0))!=expected:warnings.append('Incomplete item detail: '+e['reference'])
        e['original']=copy.deepcopy(e)
    if source is None:
        digest=hashlib.sha256(((file_sha or '')+'|'+party+'|'+text).encode()).hexdigest()
        source={'format':'tally-detailed-ledger','schema_version':1,'sha256':digest,'file_sha256':file_sha,'text':text,'pages':len(pages),'page_numbers':[p['page'] for p in pages],'structured_pages':copy.deepcopy(pages),'report_start':start,'report_end':end,'opening_omitted_zero':not saw_opening}
    return {**details,'party_details':details,'opening':str(opening),'closing':str(closing),'entries':entries,'warnings':list(dict.fromkeys(warnings)),'source':source,'reconciled':debits-credits==closing}

def import_ledgers(pdf,settings,file_sha):
    out=[]
    for pages in group_pages(detailed_pages(pdf)):
        try:out.append(parse_ledger(pages,settings,file_sha=file_sha))
        except (ValueError,ArithmeticError,KeyError) as exc:out.append({'party':pages[0]['party'],'import_error':str(exc),'page_numbers':[p['page'] for p in pages]})
    return out
