"""Read-only State -> HQ -> Party reporting from frozen product rows and PDF Group evidence."""
import re
from collections import defaultdict
from decimal import Decimal
from engine import D
from reporting import report

def source_hq(record):
    source=record.get('latest_statement_source') or record.get('source') or {}
    if source.get('structured_pages'):
        headers=['\n'.join(r.get('text','') for r in p.get('rows',[]) if r.get('line',0)<=p.get('header_line',0)) for p in source['structured_pages']]
    else:
        headers=[re.split(r'^Date\s+.*(?:Particulars|Vch Type).*$',source.get('text',''),maxsplit=1,flags=re.M|re.I)[0]]
    groups=[]
    for header in headers:
        for line in header.splitlines():
            m=re.match(r'^Group\s*:\s*(.*?)(?:\s+Ledger\s*:.*)?$',line.strip(),re.I)
            if m and m[1].strip():groups.append(m[1].strip())
    unique=list(dict.fromkeys(groups))
    if len(unique)==1:return {'hq':unique[0],'hq_evidence':'PDF Group: '+unique[0],'hq_status':'source'}
    return {'hq':'Unassigned HQ','hq_evidence':'Conflicting PDF Group headings' if unique else 'No PDF Group in saved source','hq_status':'review' if unique else 'missing'}

def product_totals(rows):
    groups=defaultdict(list)
    for r in rows:groups[(r['crop'],r['product'],str(r['packing_kg']))].append(r)
    out=[]
    for (crop,product,pack),rr in sorted(groups.items()):
        packets=sum((D(r['net_packets']) for r in rr),Decimal(0));kg=sum((D(r['net_kg']) for r in rr),Decimal(0))
        known=all(r['net_realisation'] is not None for r in rr)
        net=sum((D(r['net_realisation']) for r in rr if r['net_realisation'] is not None),Decimal(0))
        out.append(dict(crop=crop,product=product,packing_kg=pack,net_packets=packets,net_kg=kg,total_CN=sum((D(r['total_CN']) for r in rr),Decimal(0)),net_realisation=net if known else None,NRV_per_packet=net/packets if known and packets else None,NRV_per_kg=net/kg if known and kg else None))
    return out

def summary(rows):
    return {'products':len(rows),'parties':len({(r['workbook_id'],r['party'],r['location']) for r in rows}),'total_CN':sum((D(r['total_CN']) for r in rows),Decimal(0)),'net_realisation':sum((D(r['net_realisation']) for r in rows if r['net_realisation'] is not None),Decimal(0))}

def territory_report(books,filters=None):
    filters=filters or {}
    base=report(books,{k:v for k,v in filters.items() if k!='hq'})
    rows=[];cache={}
    for raw in base['rows']:
        r=dict(raw);key=(r['workbook_id'],r['record_id'])
        if key not in cache:cache[key]=source_hq(books.get(key[0]).get(key[1]))
        r.update(cache[key]);rows.append(r)
    # HQ options stay available within the other selected filters.
    options={**base['options'],'hq':sorted({r['hq'] for r in rows})}
    chosen=[r for r in rows if not filters.get('hq') or r['hq']==filters['hq']]
    states=[]
    for state in sorted({r['state'] for r in chosen}):
        sr=[r for r in chosen if r['state']==state];hqs=[]
        for hq in sorted({r['hq'] for r in sr}):
            hr=[r for r in sr if r['hq']==hq];parties=[]
            for key in sorted({(r['workbook_id'],r['party'],r['location']) for r in hr}):
                pr=[r for r in hr if (r['workbook_id'],r['party'],r['location'])==key]
                parties.append(dict(workbook=pr[0]['workbook'],party=key[1],location=key[2],summary=summary(pr),products=product_totals(pr),evidence=sorted({r['hq_evidence'] for r in pr})))
            hqs.append(dict(hq=hq,summary=summary(hr),parties=parties))
        states.append(dict(state=state or 'State not entered',summary=summary(sr),hqs=hqs))
    notes=list(base['notes']);missing=sum(r['hq_status']!='source' for r in chosen)
    if missing:notes.append(str(missing)+' completed product row(s) have missing/conflicting Group evidence and appear under Unassigned HQ. Town/address was not used as HQ.')
    return dict(options=options,summary=summary(chosen),hierarchy=states,totals=product_totals(chosen),notes=notes,scope=base['scope'],hq_rule='HQ is taken from the saved PDF Group header. State follows the completed calculation reporting state. Frozen source/results are read, never recalculated.')
