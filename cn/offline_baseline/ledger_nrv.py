"""Read-only realised rates from source invoices, material returns and posted scheme CNs."""
import copy,re
from collections import defaultdict
from decimal import Decimal,localcontext
from importer import product_suggestion

ZERO=Decimal(0)
NUMBERS=('sales_value','returns_value','supplied_kg','returned_kg','supplied_packets','returned_packets','scheme_CN')

def build(entries,settings=None):
    from ledger_audit import number,norm,narration,voucher_view,cn_classification
    settings=settings or {};catalog={p['id']:p for p in settings.get('products',[])}
    crops=set(settings.get('crops',[]))|{p['crop'] for p in catalog.values()}
    rows={};pools=defaultdict(lambda:ZERO);pending=[];excluded=[];included=[];party_blocks=defaultdict(list);crop_blocks=defaultdict(list)
    def blank(identity,doc,crop,pid,name,pack):
        return {'party':doc.get('party',''),'location':doc.get('location',''),'crop':crop,'product_id':pid,'product':name,'packing_kg':pack,'identity':identity,**{k:ZERO for k in NUMBERS},'kg_known':True,'packets_known':True,'issues':[],'voucher_count':0,'cn_count':0}
    def resolve(name,item=None):
        item=item or {};hint=product_suggestion(name,settings) if catalog else {};pid=hint.get('product');p=catalog.get(pid)
        detected=hint.get('detected_packing_kg')
        pack=item.get('packing_kg') or detected or (p or {}).get('packing_kg')
        if pack not in (None,''):
            try:pack=number(pack);pack=pack if pack>0 else None
            except (ValueError,ArithmeticError):pack=None
        else:pack=None
        if p and pack is not None and pack!=number(p['packing_kg']):p=None;pid=None
        candidates=[catalog[x] for x in hint.get('candidates',[]) if x in catalog]
        matches={p['crop']} if p else {p['crop'] for p in candidates}
        if not matches:matches={c for c in crops if re.search(r'(?<!\w)'+re.escape(norm(c))+r'(?!\w)',norm(name))}
        crop=next(iter(matches)) if len(matches)==1 else 'Unmapped crop'
        return crop,pid if p else None,(p or {}).get('name',str(name or 'Unidentified product')),pack
    def getrow(identity,doc,crop,pid,name,pack):
        key=(identity,crop,pid or norm(name),str(pack.normalize()) if pack is not None else '')
        if key not in rows:rows[key]=blank(identity,doc,crop,pid,name,pack)
        return rows[key]
    def block(identity,crop,view,reason):
        pending.append({**view,'reason':reason,'crop':crop or 'Needs mapping'})
        (crop_blocks[(identity,crop)] if crop and crop!='Unmapped crop' else party_blocks[identity]).append(reason)
    def journal(e):
        original=e.get('original') or {};headers=[(e.get('source_lines') or [{}])[0].get('text',''),(original.get('source_lines') or [{}])[0].get('text','')]
        return norm(e.get('voucher_family') or original.get('voucher_family'))=='JOURNAL' or any(re.search(r'\bJOURNAL\b',norm(h)) for h in headers) or 'JOURNAL' in norm(e.get('posting_label'))
    def ismaterial(e,text,classification):
        return e.get('kind')=='return' or classification=='material_return' or bool(re.search(r'\b(?:SALES?|MATERIAL|GOODS)\s+RETURN(?:ED)?\b',text))
    def stock(identity,doc,e,kind):
        items=e.get('items') or [];view=voucher_view(doc,e)
        if not items:
            block(identity,None,view,'Sales/material return has no readable product quantities or item values');return
        expected=number(e.get('debit'))-number(e.get('credit')) if kind=='sale' else number(e.get('credit'))-number(e.get('debit'))
        complete=all(i.get('amount') not in (None,'') for i in items)
        reconciles=complete and sum((number(i['amount']) for i in items),ZERO)==expected
        for item in items:
            crop,pid,name,pack=resolve(item.get('name'),item);r=getrow(identity,doc,crop,pid,name,pack);r['voucher_count']+=1
            if crop=='Unmapped crop':r['issues'].append('Crop could not be identified from source product/packing')
            if not reconciles:r['issues'].append('Source item values do not reconcile the invoice/return voucher; review taxes, charges or missing lines')
            if item.get('qty') in (None,'') or item.get('amount') in (None,''):
                r['issues'].append('Missing printed quantity or item amount');r['kg_known']=r['packets_known']=False;continue
            q=number(item['qty']);value=number(item['amount']);unit=norm(item.get('unit'));r['sales_value' if kind=='sale' else 'returns_value']+=value
            if q<0 or value<0:r['issues'].append('Negative source quantity/value needs review')
            if q==0 and value!=0:r['issues'].append('Nonzero invoice/return value without physical quantity needs review')
            kg=packets=None
            if unit in ('KG','KGS','KILOGRAM','KILOGRAMS'):kg=q;packets=q/pack if pack else None
            elif unit in ('PACKET','PACKETS','PKT','PKTS','BAG','BAGS'):packets=q;kg=q*pack if pack else None
            else:r['issues'].append('Unsupported or missing printed quantity unit')
            if kg is None:r['kg_known']=False
            else:r['supplied_kg' if kind=='sale' else 'returned_kg']+=kg
            if packets is None:r['packets_known']=False
            else:r['supplied_packets' if kind=='sale' else 'returned_packets']+=packets
    # Conflicting overlapping exports must not add an old and a corrected voucher together.
    versions=defaultdict(set)
    def source_identity(identity,e):
        family='JOURNAL' if journal(e) else 'CREDIT' if e.get('kind') in ('return','posted_cn') else 'SALE' if e.get('kind')=='sale' else e.get('kind')
        return identity,e.get('date'),norm(e.get('reference') or e.get('id')),family
    for identity,doc,e in entries:
        signature=(e.get('kind'),number(e.get('debit')),number(e.get('credit')),tuple((norm(i.get('name')),norm(i.get('unit')),number(i.get('qty')),number(i.get('amount'))) for i in e.get('items',[])))
        versions[source_identity(identity,e)].add(signature)
    conflicts={k for k,v in versions.items() if len(v)>1}
    for identity,day,ref,family in conflicts:party_blocks[identity].append('Conflicting source versions of voucher '+str(ref)+' on '+str(day)+'; review overlapping exports')
    seen_documents=set()
    for identity,doc,e in entries:
        key=(identity,id(doc))
        if key in seen_documents:continue
        seen_documents.add(key)
        for warning in doc.get('warnings',[]):party_blocks[identity].append('Source coverage warning: '+str(warning))
    with localcontext() as ctx:
        ctx.prec=40
        for identity,doc,e in entries:
            view=voucher_view(doc,e)
            if source_identity(identity,e) in conflicts:
                pending.append({**view,'crop':'Needs review','reason':'Conflicting overlapping source voucher versions; excluded until reviewed'})
                continue
            text=view['narration'];evidence=text+' '+norm(' '.join(l.get('text','') for l in e.get('source_lines',[])));classification=cn_classification(view,settings)
            if e.get('kind') in ('sale','return'):
                stock(identity,doc,e,e['kind'])
                if e['kind']=='return':excluded.append({**view,'reason':'Material sales return: deducted from net sales, not counted as scheme CN'})
                continue
            if e.get('kind') not in ('posted_cn','adjustment','unknown'):continue
            if journal(e):excluded.append({**view,'reason':'Journal excluded from scheme CN / NRV deduction'});continue
            if classification=='freight' or re.search(r'\b(?:FREIGHT|TRANSPORT|TRANSPORTATION|COURIER)\b',evidence):excluded.append({**view,'reason':'Freight / transport CN excluded'});continue
            if ismaterial(e,evidence,classification):
                stock(identity,doc,e,'return');excluded.append({**view,'reason':'Material return: deducted from net sales, not counted as scheme CN'});continue
            if classification=='other':excluded.append({**view,'reason':'Other adjustment excluded'});continue
            if e.get('kind')!='posted_cn':
                if number(e.get('credit')) or e.get('items'):block(identity,None,view,'Unclassified non-journal credit/stock voucher needs review')
                continue
            crop,pid,name,pack=resolve(text)
            mapped_product=settings.get('audit_product_mappings',{}).get(view['product_mapping_key'])
            if mapped_product in catalog:
                p=catalog[mapped_product];crop,pid,name,pack=p['crop'],p['id'],p['name'],number(p['packing_kg'])
            mapped_crop=settings.get('audit_crop_mappings',{}).get(text)
            if mapped_crop:
                crop=mapped_crop
                if pid and catalog[pid]['crop']!=crop:pid=None
            amount=number(e.get('credit'))-number(e.get('debit'))
            if e.get('items') and not (classification=='scheme' and (mapped_crop or mapped_product)):
                block(identity,crop,view,'Credit note with material/quantity lines needs explicit scheme classification and crop/product mapping; no physical return or benefit is guessed');continue
            benefit=bool(re.search(r'\b(?:ABS|CD|INCENTIVE|REBATE|BENEFIT|BONUS|DISCOUNT|SCHEME|NET\s+RATE|CASH\s+CN|QTY\s+CN|QUANTITY\s+CN)\b',text))
            if classification!='scheme' and not (benefit and crop!='Unmapped crop'):
                block(identity,crop,view,'Confirm this financial credit note is a scheme benefit');continue
            if crop=='Unmapped crop' or not crop:
                block(identity,None,view,'Scheme CN crop/product could not be identified; map its narration');continue
            if amount<=0:
                block(identity,crop,view,'Zero/debit scheme CN or reversal needs review before netting benefits');continue
            v={**view,'cn_classification':'scheme','crop':crop,'product_id':pid,'product':name if pid else None,'scheme_CN':amount,'mapping_key':text};included.append(v)
            if pid:
                r=getrow(identity,doc,crop,pid,name,pack);r['scheme_CN']+=amount;r['cn_count']+=1
            else:pools[(identity,crop)]+=amount
        raw=list(rows.values())
        for r in raw:
            r['net_sales_value']=r['sales_value']-r['returns_value'];r['net_kg']=r['supplied_kg']-r['returned_kg'] if r['kg_known'] else None;r['net_packets']=r['supplied_packets']-r['returned_packets'] if r['packets_known'] else None
            if r['net_sales_value']<0 or r['net_kg'] is not None and r['net_kg']<0 or r['net_packets'] is not None and r['net_packets']<0:r['issues'].append('Returns exceed selected-period sales; review supply coverage')
            if r['cn_count'] and not r['voucher_count']:r['issues'].append('CN product has no matching selected-period sales/returns')
            r['issues']+=party_blocks[r['identity']]+crop_blocks[(r['identity'],r['crop'])];r['issues']=list(dict.fromkeys(r['issues']))
        # A mapped crop CN without any matching stock must stay visible, not disappear.
        for (identity,crop),amount in list(pools.items()):
            if not any(r['identity']==identity and r['crop']==crop for r in raw):
                doc={'party':identity[0],'location':identity[1]};r=blank(identity,doc,crop,None,'No matching sales/returns',None);r.update(net_sales_value=ZERO,net_kg=ZERO,net_packets=ZERO);r['issues']=['Crop CN has no matching selected-period sales'];raw.append(r)
        def aggregate(group,scope,extra_cn=ZERO):
            base={'scope':scope,'crop':group[0]['crop'],'party_count':len({r['identity'] for r in group}),**{k:sum((r[k] for r in group),ZERO) for k in NUMBERS}}
            base['scheme_CN']+=extra_cn;base['net_sales_value']=base['sales_value']-base['returns_value'];base['after_CN_value']=base['net_sales_value']-base['scheme_CN'];base['net_kg']=sum((r['net_kg'] for r in group),ZERO) if all(r['net_kg'] is not None for r in group) else None
            packs={r['packing_kg'] for r in group};same_pack=len(packs)==1 and None not in [r['packing_kg'] for r in group]
            base['net_packets']=sum((r['net_packets'] for r in group),ZERO) if all(r['net_packets'] is not None for r in group) and (same_pack or len(group)==1) else None
            base['issues']=list(dict.fromkeys(i for r in group for i in r['issues']))
            if base['after_CN_value']<0:base['issues'].append('Scheme CN exceeds net sales value; review period/benefit attribution')
            base['CN_status']='Needs review' if base['issues'] else 'CN given' if base['scheme_CN'] else 'No scheme CN found'
            base['NRV_per_kg']=base['after_CN_value']/base['net_kg'] if not base['issues'] and base['net_kg'] is not None and base['net_kg']>0 else None
            base['NRV_per_packet']=base['after_CN_value']/base['net_packets'] if not base['issues'] and base['net_packets'] is not None and base['net_packets']>0 else None
            base['unit_note']='Per-packet average withheld for mixed/unknown packing; use per-kg where available' if base['net_packets'] is None else ''
            return base
        pc=defaultdict(list)
        for r in raw:pc[(r['identity'],r['crop'])].append(r)
        party_rows=[]
        for (identity,crop),group in pc.items():
            x=aggregate(group,'party_crop',pools[(identity,crop)]);x.update(party=group[0]['party'],location=group[0]['location'],crop_CN_pool=pools[(identity,crop)]);party_rows.append(x)
        crop_groups=defaultdict(list)
        for r in raw:crop_groups[r['crop']].append(r)
        crop_rows=[]
        for crop,group in crop_groups.items():crop_rows.append(aggregate(group,'crop',sum((v for (identity,c),v in pools.items() if c==crop),ZERO)))
        product_rows=[]
        for r in raw:
            x=aggregate([r],'party_product');x.update(party=r['party'],location=r['location'],product=r['product'],product_id=r['product_id'],packing_kg=r['packing_kg'],crop_CN_pool=pools[(r['identity'],r['crop'])])
            if x['crop_CN_pool']:
                x['NRV_per_kg']=x['NRV_per_packet']=None;x['CN_status']='Needs review' if x['issues'] else 'Crop CN given — product split unavailable';x['issues'].append('Crop-only scheme CN is not apportioned across products; see crop NRV')
            product_rows.append(x)
        product_groups=defaultdict(list)
        for r in raw:
            if not r['product_id']:continue
            rr=copy.deepcopy(r)
            if pools[(r['identity'],r['crop'])]:rr['issues'].append('Crop-only CN cannot be apportioned to this product')
            product_groups[(r['crop'],r['product_id'],str(r['packing_kg']))].append(rr)
        averages=[]
        for group in product_groups.values():
            x=aggregate(group,'product_average');x.update(product=group[0]['product'],product_id=group[0]['product_id'],packing_kg=group[0]['packing_kg']);averages.append(x)
        result={'product_average_rows':sorted(averages,key=lambda x:(x['crop'],x['product'],str(x['packing_kg']))),'crop_rows':sorted(crop_rows,key=lambda x:x['crop']),'party_rows':sorted(party_rows,key=lambda x:(x['crop'],x['party'],x['location'])),'product_rows':sorted(product_rows,key=lambda x:(x['crop'],x['party'],x['product'],str(x['packing_kg']))),'included_CNs':included,'pending_CNs':pending,'excluded_credits':excluded,'confirmed_CN_total':sum((v['scheme_CN'] for v in included),ZERO),'notes':['NRV = (actual invoiced sales value − actual material return value − eligible posted scheme CN) ÷ net sold quantity. Calculator-proposed/issued CNs are never used.','Journal, freight/transport and other classified adjustments do not reduce this scheme NRV. Material return credits reduce net sales once and are not counted as scheme CNs.','Weighted crop NRV uses total net realisation divided by total net quantity, never an average of party rates. Per-packet crop averages require consistent known packing.','No scheme CN found means no identifiable posting in the selected period; it does not establish entitlement, non-payment or coverage outside the imported ledger. Unclassified credits suppress affected NRV until reviewed.','Crop-only CNs are not guessed across products. Product NRV remains unavailable where only crop-level attribution is supported. IPT is excluded from invoiced sales/returns in this report.']}
        represented={r['identity'] for r in raw}
        if any(reasons and identity not in represented for identity,reasons in party_blocks.items()):
            mark_incomplete(result,'Unmapped credit/source evidence belongs to a party with no matching selected-period sales; combined averages require review')
        for (identity,crop),reasons in crop_blocks.items():
            if not reasons or (identity,crop) in pc:continue
            for row in result['crop_rows']+result['product_average_rows']:
                if row['crop']==crop:
                    row['NRV_per_kg']=row['NRV_per_packet']=None;row['CN_status']='Needs review';row['issues'].append('Unclassified crop credit has no matching sales for its party; review period and mapping')
        return result



def saved_bulk_report(store,start,end):
    """Combine source vouchers behind active bulk imports, never calculated/issued CNs."""
    import json
    from ledger_audit import audit_documents
    with store.db() as c:
        history=[json.loads(r[0]) for r in c.execute('SELECT data FROM bulk_imports')]
        records={r['id']:r for r in (json.loads(x[0]) for x in c.execute('SELECT data FROM records'))}
    documents=[];seen=set();seen_lineages=set();warnings=[]
    for log in history:
        id=log.get('record_id')
        if id and log.get('status')=='Needs review':warnings.append({'party':log.get('party',''),'message':'A changed source ledger is awaiting import review'})
        if not id:
            if log.get('status') in ('Needs review','Failed'):warnings.append({'party':log.get('party',''),'message':'Bulk file/party needs review and is not part of the combined NRV coverage'})
            continue
        if id in seen:continue
        seen.add(id);record=records.get(id)
        if not record or record.get('deleted_at'):continue
        lineage=record.get('lineage') or record['id']
        versions=[r for r in records.values() if not r.get('deleted_at') and (r.get('lineage') or r['id'])==lineage]
        record=max(versions,key=lambda r:(r.get('saved_at') or '',r.get('revision',0)))
        if lineage in seen_lineages:continue
        seen_lineages.add(lineage)
        doc={'party':record.get('party',''),'location':record.get('location',''),'audit_filename':log.get('filename','Saved bulk ledger'),'entries':[],'warnings':[]}
        for e in record.get('entries',[]):
            # Prefer explicitly accepted latest import, otherwise preserved source. Manual entries
            # and later hand-entered changes are not proof of a posting in the imported PDF.
            source=copy.deepcopy(e.get('latest_import_source') or e.get('original') or e)
            if not source.get('source_lines'):
                doc['warnings'].append('An entry has no imported PDF evidence and was excluded from the source-only NRV report')
                continue
            doc['entries'].append(source)
        documents.append(doc)
    out=audit_documents(documents,start,end,store.settings());out['warnings']+=warnings
    if warnings:mark_incomplete(out['posted_CN_NRV'],'Some bulk files/parties remain failed or pending review; combined crop NRV is withheld')
    out['source']='saved_bulk_source_entries';out['notes'].append('Combined saved-bulk report uses imported source voucher evidence only. Repeated/overlapping source vouchers are deduplicated. Deleted parties and entries without PDF evidence are excluded and identified in coverage warnings.')
    return out


def mark_incomplete(report,reason):
    report['coverage_complete']=False
    report.setdefault('coverage_notes',[]).append(reason)
    for row in report['crop_rows']+report.get('product_average_rows',[]):
        row['NRV_per_kg']=row['NRV_per_packet']=None
        row['CN_status']='Needs review'
        row['issues'].append(reason)
