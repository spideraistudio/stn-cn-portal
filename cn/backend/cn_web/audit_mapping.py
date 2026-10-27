"""Mapping links from owned audit evidence; no financial source edits."""
import copy
from .ledger_service import digest
from .product_mapping import plan, identity, compatible


def targets(documents,references,state,start,end):
    products={p['id']:p for p in state['catalogue']};out=[]
    for doc,ref in zip(documents,references):
        ref=({'web_ledger_id':ref['web_ledger_id']} if ref.get('web_ledger_id') else {'web_file_id':ref.get('web_file_id'),'web_document_index':ref.get('web_document_index')})
        mapped=plan(doc,state)
        for ei,e in enumerate(doc.get('entries',[])):
            if e.get('kind') not in ('sale','return','ipt_in','ipt_out') or not start<=e.get('date','')<=end:continue
            for ii,item in enumerate(e.get('items',[])):
                pid=item.get('product') if item.get('mapping_confirmed') and item.get('product') in products else mapped[f'{ei}:{ii}']['product_id']
                if pid and compatible(item,products[pid]):continue
                suggestion=item.get('mapping_suggestion') or {}
                row={'source':ref,'entry_id':e['id'],'item_index':ii,'party':doc.get('party',''),'location':doc.get('location',''),
                     'date':e['date'],'reference':e.get('reference',''),'kind':e['kind'],'name':item['name'],
                     'qty':item.get('qty',''),'unit':item.get('unit',''),'rate':item.get('rate',''),'amount':item.get('amount',''),
                     'packing':suggestion.get('detected_packing_kg') or '', 'crop':suggestion.get('crop') or '',
                     'reason':mapped[f'{ei}:{ii}']['reason']}
                row['id']=digest([ref,e['id'],ii]);out.append(row)
    return out


def nrv_for_audit(documents,state,cfg,start,end):
    """Give legacy NRV exact mapped identities after original-source deduplication.

    Internal aliases prevent broad-name ambiguity (e.g. Seed and Seed Gold).
    Original printed evidence is restored before returning the report. No source
    item, financial setting or preserved module is changed.
    """
    import json
    from collections import Counter
    from ledger_audit import norm,number,cn_product_key
    from ledger_nrv import build
    cfg=copy.deepcopy(cfg);products={p['id']:p for p in cfg['products']};entries=[];seen=Counter()
    for original in documents:
        if original.get('import_error'):continue
        doc=copy.deepcopy(original);mapped=plan(original,state);local=Counter()
        party=(norm(doc.get('party')),norm(doc.get('location')))
        for ei,e in enumerate(doc.get('entries',[])):
            if not e.get('date') or not start<=e['date']<=end:continue
            stable=[party,e.get('date'),e.get('reference'),e.get('kind'),str(number(e.get('debit')).normalize()),str(number(e.get('credit')).normalize()),
                    [(norm(i.get('name')),i.get('unit'),str(number(i.get('qty')).normalize()),str(number(i.get('rate')).normalize()),str(number(i.get('amount')).normalize())) for i in e.get('items',[])]]
            rawkey=json.dumps(stable,sort_keys=True);local[rawkey]+=1
            if local[rawkey]<=seen[rawkey]:continue
            if e['kind'] in ('sale','return'):
                for ii,item in enumerate(e.get('items',[])):
                    pid=item.get('product') if item.get('mapping_confirmed') and item.get('product') in products else mapped[f'{ei}:{ii}']['product_id']
                    if pid not in products or not compatible(item,products[pid]):continue
                    marker='__CN_AUDIT_'+digest([pid,identity(item)])+'__'
                    p=products[pid];p['aliases']=list(dict.fromkeys(p.get('aliases',[])+[marker]))
                    item['audit_original_name']=item['name'];item['audit_original_packing']=[('packing_kg' in item),item.get('packing_kg')];item['name']=marker;item['packing_kg']=p['packing_kg']
            entries.append((party,doc,e))
        seen|=local
    out=build(entries,cfg)
    def restore(value):
        if isinstance(value,list):
            for child in value:restore(child)
        elif isinstance(value,dict):
            if 'audit_original_name' in value:
                value['name']=value.pop('audit_original_name')
                had,packing=value.pop('audit_original_packing')
                if had:value['packing_kg']=packing
                else:value.pop('packing_kg',None)
            for child in list(value.values()):restore(child)
            if 'product_mapping_key' in value and 'items' in value:value['product_mapping_key']=cn_product_key(value)
    restore(out)
    return out
