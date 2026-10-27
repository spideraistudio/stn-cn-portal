"""Read-only reporting and spreadsheet-safe CSV; no posting or recalculation of frozen records."""
import csv,io,copy
from collections import defaultdict
from decimal import Decimal
from engine import D,unit_qty,stock_in_period

BENEFITS=('ABS','Quantity','CD','Extra','Return','Net rate','Cash')
COLUMNS=['workbook','state','season','party','location','status','record_id','crop','segment','scheme','product','packing_kg','unit','invoice_supply','ipt_received','ipt_given','returns','net_sold','net_packets','net_kg','billing_rate','billing_unit',*[b+' CN' for b in BENEFITS],'total_CN','CN_per_packet','CN_per_kg','NRV_per_packet','NRV_per_kg','net_realisation','requested_delta_display_only','requested_total_display_only','report_note']

def product_rows(record,result,settings,metadata):
    if result.get('issues'):raise ValueError('Resolve calculation issues before exporting a product summary')
    if 'product_CNs' not in result:raise ValueError('This older frozen record has no product breakdown; its original totals are preserved')
    schemes={s['id']:s for s in settings['schemes']};out=[]
    for p in result['product_CNs']:
        s=schemes.get(p['scheme'])
        if not s:raise ValueError('Frozen scheme is missing; billing/NRV cannot be inferred')
        season=next((x for x in settings['seasons'] if x['name']==record.get('season')), {})
        pack=D(p['packing_kg']);unit=p['unit'];quantities=defaultdict(lambda:Decimal(0))
        for e in record.get('entries',[]):
            if e.get('kind') not in ('sale','return','ipt_in','ipt_out'):continue
            if result.get('stock_scope',{}).get(e['id']) is False:continue
            if 'stock_scope' not in result and record.get('annual_ledger') and not stock_in_period(record,e,season):continue
            for i in e.get('items',[]):
                if i.get('product')==p['product_id'] and not i.get('exclude'):
                    quantities[e['kind']]+=unit_qty(i['qty'],i.get('unit','packet'),unit,pack)
        bill=s.get('billing');billunit=s.get('billing_unit',unit)
        valid=bill not in (None,'') and billunit in ('kg','packet')
        rate=D(bill) if valid else None
        packet_rate=rate*pack if valid and billunit=='kg' else rate
        kg_rate=rate/pack if valid and billunit=='packet' else rate
        cn=D(p['total_CN']);packets=D(p['net_packets']);kg=D(p['net_kg'])
        request=p.get('request') or {}
        row={'workbook':metadata.get('name','Existing calculations'),'workbook_id':metadata.get('id','legacy'),
             'state':record.get('scheme_state') or record.get('workbook_scheme_state') or metadata.get('state') or record.get('state',''),
             'season':record.get('season',''),'party':record.get('party',''),'location':record.get('location',''),
             'status':record.get('status','draft'),'record_id':record.get('id',''),'crop':p['crop'],'segment':p['segment'],
             'scheme':p['scheme_name'],'product':p['product'],'packing_kg':pack,'unit':unit,
             'invoice_supply':quantities['sale'],'ipt_received':quantities['ipt_in'],'ipt_given':quantities['ipt_out'],
             'returns':quantities['return'],'net_sold':D(p['net_sold']),'net_packets':packets,'net_kg':kg,
             'billing_rate':rate,'billing_unit':billunit,'total_CN':cn,'CN_per_packet':D(p['CN_per_packet']),
             'CN_per_kg':D(p['CN_per_kg']),
             'NRV_per_packet':packet_rate-cn/packets if valid and packets else None,
             'NRV_per_kg':kg_rate-cn/kg if valid and kg else None,
             'net_realisation':rate*unit_qty(p['net_sold'],unit,billunit,pack)-cn if valid else None,
             'requested_delta_display_only':D(request.get('delta',0)),
             'requested_total_display_only':request.get('requested_total'),
             'report_note':'Full scheme entitlement; NRV uses configured scheme billing on net sold quantity. Freight/posted ledger CNs and display-only requests excluded from NRV.'}
        for b in BENEFITS:row[b+' CN']=sum((D(x['CN']) for x in p['benefits'] if (x['benefit'].startswith('Cash ') if b=='Cash' else x['benefit']==b)),Decimal(0))
        season=next((x for x in settings['seasons'] if x['name']==record.get('season')), {})
        row['_period']=(season.get('start'),season.get('end'));row['_lineage']=record.get('lineage') or record.get('id')
        out.append(row)
    return out

def report(books,filters=None):
    filters=filters or {};rows=[];notes=[]
    for meta in [books.metadata('legacy'),*books.list()]:
        st=books.get(meta['id']);groups=defaultdict(list)
        for r in st.all():
            if not r.get('deleted_at') and r.get('status') in ('finalised','issued'):
                groups[(r.get('lineage') or r['id'],r.get('season'))].append(r)
        for versions in groups.values():
            # Draft revisions do not suppress the last completed snapshot.
            r=max(versions,key=lambda x:(x.get('issued_at') or x.get('finalised_at') or x.get('saved_at',''),x.get('revision',0),x['id']))
            try:rows.extend(product_rows(r,r['result'],r['frozen_settings'],meta))
            except (ValueError,KeyError) as e:notes.append(f"{meta['name']} / {r.get('party')}: {e}")
    # Distinct lineages/workbooks can hold the same completed product/period.
    # Exclude overlaps with an explicit note rather than silently doubling totals.
    options={k:sorted({str(r[k]) for r in rows}) for k in ('workbook','state','season','crop','segment','product','party')}
    scoped=[r for r in rows if all(not filters.get(k) or str(r[k])==str(filters[k]) for k in options)]
    buckets=defaultdict(list)
    for row in scoped:
        key=(row['party'].strip().casefold(),row['location'].strip().casefold(),row['_period'],row['crop'].casefold(),row['product'].casefold(),str(row['packing_kg'].normalize()))
        buckets[key].append(row)
    accepted=[]
    for group in buckets.values():
        if len(group)>1:
            notes.append('Overlapping completed records excluded; review: '+', '.join(f"{r['workbook']} / {r['party']} / {r['product']} / {r['record_id']}" for r in group))
        else:accepted.extend(group)
    chosen=accepted
    missing=sum(r['net_realisation'] is None for r in chosen)
    if missing:notes.append(f'NRV is unavailable for {missing} row(s); net realisation total includes only rows with known configured billing.')
    net=sum((r['net_realisation'] for r in chosen if r['net_realisation'] is not None),Decimal(0))
    summary={'products':len(chosen),'parties':len({(r['workbook_id'],r['party'],r['location']) for r in chosen}),
             'total_CN':sum((r['total_CN'] for r in chosen),Decimal(0)),'net_realisation':net}
    # Group quantity/NRV by crop/product/packing. Never average unrelated rates or packings.
    totals=defaultdict(lambda:{'net_packets':Decimal(0),'net_kg':Decimal(0),'CN':Decimal(0),'net_realisation':Decimal(0),'nrv_complete':True})
    for r in chosen:
        t=totals[(r['crop'],r['product'],str(r['packing_kg']))]
        for k in ('net_packets','net_kg'):t[k]+=r[k]
        t['CN']+=r['total_CN']
        if r['net_realisation'] is None:t['nrv_complete']=False
        else:t['net_realisation']+=r['net_realisation']
    aggregated=[]
    for (crop,product,pack),t in sorted(totals.items()):
        aggregated.append(dict(crop=crop,product=product,packing_kg=pack,**t,
                              NRV_per_packet=t['net_realisation']/t['net_packets'] if t['nrv_complete'] and t['net_packets'] else None,
                              NRV_per_kg=t['net_realisation']/t['net_kg'] if t['nrv_complete'] and t['net_kg'] else None))
    return dict(rows=[{k:v for k,v in r.items() if not k.startswith('_')} for r in chosen],options=options,summary=summary,totals=aggregated,notes=notes,
                scope='Latest completed snapshot per lineage; drafts/deleted workbooks/deleted parties excluded. Overlapping completed products are excluded for review. Full entitlement, not incremental revision issue amount.')

def csv_text(rows):
    out=io.StringIO(newline='');writer=csv.writer(out);writer.writerow(COLUMNS)
    numeric=set(COLUMNS[11:])-{'unit','billing_unit','report_note'}
    for row in rows:
        values=[]
        for key in COLUMNS:
            value=row.get(key)
            if value is None:value=''
            elif isinstance(value,Decimal):value=format(value,'f')
            else:value=str(value)
            if key not in numeric and value.lstrip().startswith(('=','+','-','@','\t','\r')):value="'"+value
            values.append(value)
        writer.writerow(values)
    return '\ufeff'+out.getvalue()
