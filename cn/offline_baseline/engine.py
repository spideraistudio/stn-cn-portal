import copy,hashlib,json
from decimal import Decimal, localcontext, ROUND_HALF_UP, ROUND_FLOOR
from datetime import date
from collections import defaultdict
from year_link import validate_link_sources

VERSION='6.0.0'
def D(v):
    if v is None or v=='': raise ValueError('Missing number')
    x=Decimal(str(v))
    if not x.is_finite():raise ValueError('Number must be finite')
    return x
def rounded(v):return v.quantize(Decimal('1'),rounding=ROUND_HALF_UP)
def iso(v):return date.fromisoformat(v)
def unit_qty(q,source,target,pack):
    q=D(q);pack=D(pack)
    if pack<=0:raise ValueError('Packing must be positive')
    if source not in ('kg','packet') or target not in ('kg','packet'):raise ValueError('Unknown unit')
    return q if source==target else q*pack if source=='packet' else q/pack

def tier(q,rows):
    if q<=0 or not rows:return None
    if any(row.get('inclusive') for row in rows):
        eligible=[row for row in rows if q>=D(row['above'])]
        return eligible[-1] if eligible else None
    for row in rows:
        lo=D(row['above']);hi=D(row['upto']) if row.get('upto') is not None else None
        if (q>=lo if row.get('inclusive') else q>lo) and (hi is None or q<=hi):return row
    last=rows[-1]
    return last if last.get('upto') is not None and q>D(last['upto']) else None

def slab_cn(q,rows,mode):
    if mode=='whole':
        row=tier(q,rows);return q*D(row['rate']) if row else Decimal(0)
    out=Decimal(0)
    for row in rows:
        lo=D(row['above']);hi=D(row['upto']) if row.get('upto') is not None else q
        out+=max(Decimal(0),min(q,hi)-lo)*D(row['rate'])
    if rows and rows[-1].get('upto') is not None:out+=max(Decimal(0),q-D(rows[-1]['upto']))*D(rows[-1]['rate'])
    return out

def validate_scheme(s,production=False):
    errors=[]
    def err(t):errors.append(t)
    for f in ('name','crop','segment','season','unit','products'):
        if not s.get(f):err('Scheme requires '+f)
    if s.get('unit') not in ('kg','packet'):err('Invalid scheme unit')
    for field in ('billing_unit','abs_unit','return_unit'):
        if s.get(field) not in ('kg','packet'):err('Choose kg or packet for '+field)
    if s.get('extra_unit') not in ('fixed','kg','packet'):err('Choose fixed, kg or packet for extra_unit')
    if any(b not in ('Net','ABS','CD','Quantity','Extra','Return') for b in s.get('benefits',[])):err('Unknown scheme benefit')
    if 'Net' in s.get('benefits',[]) and len(s['benefits'])!=1:err('Net rate cannot combine regular benefits')
    if production:
        if not s.get('confirmed'):err('Scheme production settings not confirmed')
        if not s.get('states'):err('Configure applicable state explicitly')
    for f in ('billing','packing_kg'):
        try:
            if D(s.get(f))<=0:err(f+' must be positive')
        except (ValueError,ArithmeticError):err('Missing/invalid '+f)
    for benefit,fields in [('ABS',['token','abs_rate']),('Return',['return_threshold','return_rate'])]:
        if benefit in s.get('benefits',[]):
            for f in fields:
                try:
                    if D(s.get(f))<0 or (f=='token' and D(s[f])==0):err('Invalid '+f)
                except (ValueError,ArithmeticError):err('Missing '+f)
    if 'Return' in s.get('benefits',[]):
        try:
            if D(s.get('return_threshold',0))>100:err('Return threshold cannot exceed 100%')
        except (ValueError,ArithmeticError):pass
    if 'Net' in s.get('benefits',[]):
        if s.get('net_mode','price') not in ('price','fixed'):err('Choose Net Price or Fixed CN mode')
        if s.get('net_mode')=='fixed':
            try:
                if D(s.get('net_cn_rate'))<0:err('Fixed CN cannot be negative')
            except (ValueError,ArithmeticError):err('Enter fixed CN per unit')
            if s.get('net_cn_unit') not in ('kg','packet'):err('Choose kg or packet for fixed CN')
    for key,benefit in [('quantity','Quantity'),('extra','Extra'),('net','Net')]:
        if benefit not in s.get('benefits',[]) or (key=='net' and s.get('net_mode')=='fixed'):continue
        rows=s.get(key,[])
        if not rows:err('Missing '+key+' slabs');continue
        previous=None
        inclusive=key=='extra' and any(row.get('inclusive') for row in rows)
        if inclusive and not all(row.get('inclusive') for row in rows):err('Use consistent inclusive extra slab boundaries')
        last_minimum=None
        for index,row in enumerate(rows):
            try:
                lo=D(row['above']);hi=D(row['upto']) if row.get('upto') is not None else None;rate=D(row['rate'])
                if lo<0 or rate<0 or (hi is not None and hi<=lo):err('Invalid '+key+' boundary/rate')
                if inclusive:
                    if last_minimum is not None and lo<=last_minimum:err('Inclusive extra minimum quantities must increase')
                    last_minimum=lo
                elif previous is not None and (lo<previous or (key!='extra' and lo!=previous)):err('Overlapping/gapped '+key+' slabs')
                if hi is None and index<len(rows)-1:err('Open-ended '+key+' slab must be last')
                previous=hi
            except (ValueError,ArithmeticError,KeyError):err('Invalid '+key+' slab')
    if 'Quantity' in s.get('benefits',[]) and s.get('quantity_mode','whole') not in ('whole','progressive'):err('Choose whole or progressive quantity calculation')
    cash=s.get('cash')
    if cash:
        if cash.get('unit') not in ('kg','packet'):err('Choose kg or packet for cash rates')
        if not cash.get('products'):err('Choose eligible cash products')
        try:
            if iso(cash['end'])<iso(cash['start']):err('Cash end before start')
        except (ValueError,TypeError,KeyError):err('Enter valid cash start/end dates')
        for field in ('advance','cn_rate'):
            try:
                value=D(cash.get(field))
                if value<0 or (field=='advance' and value==0):err('Cash advance must be positive' if field=='advance' else 'Cash CN rate cannot be negative')
            except (ValueError,ArithmeticError):err('Enter valid cash '+field)
    windows=[]
    for row in s.get('cd',[]) if 'CD' in s.get('benefits',[]) else []:
        try:
            start,end=iso(row['start']),iso(row['end']);r=D(row['percent'])
            if end<start or r<0 or r>100:err('Invalid CD period/rate')
            if any(start<=b and end>=a for a,b in windows):err('Overlapping CD periods')
            windows.append((start,end))
        except (ValueError,ArithmeticError,KeyError):err('Invalid CD date')
    for (_,end),(start,_) in zip(sorted(windows),sorted(windows)[1:]):
        if (start-end).days>1:err('Gap between CD periods; configure explicit 0% window')
    if 'CD' in s.get('benefits',[]) and not windows:err('Missing CD periods')
    if production and 'ABS' in s.get('benefits',[]):
        try:
            if iso(s['abs_end'])<iso(s['abs_start']):err('ABS end before start')
            if s.get('extended_end') and iso(s['extended_end'])<iso(s['abs_end']):err('Extension before normal end')
        except (ValueError,TypeError,KeyError):err('Enter ABS booking start/end')
    return errors



def effective_settings(r,settings):
    assignments=r.get('product_assignments',{})
    if not assignments:return settings
    cfg=copy.deepcopy(settings);products={p['id']:p for p in cfg['products']};schemes={s['id']:s for s in cfg['schemes']}
    for pid,sid in assignments.items():
        p=products.get(pid);base=schemes.get(sid)
        if not p or not base:raise ValueError('Choose a valid scheme for the product')
        dest=schemes.get(r.get('scheme_overrides',{}).get(sid,sid))
        if not dest or p['crop']!=dest['crop'] or D(p['packing_kg'])!=D(dest['packing_kg']):raise ValueError('Product scheme must match its crop and packing')
        if base.get('segment_id',base['segment'])!=dest.get('segment_id',dest['segment']):raise ValueError('Changed scheme must remain in the assigned group')
        p.update(scheme=sid,segment=dest['segment'],segment_id=dest.get('segment_id',dest['segment']),needs_assignment=False)
        for target in (base,dest):
            if pid not in target['products']:target['products'].append(pid)
    return cfg

def abs_booking_allowed(source, scheme):
    """Draft routing window; extended benefit still requires approval and remark."""
    dt=source.get('date')
    if source.get('opening') and not dt:return True
    if not scheme or 'ABS' not in scheme.get('benefits',[]):return False
    if not dt:return False
    normal=bool(scheme.get('abs_start') and scheme.get('abs_end') and scheme['abs_start']<=dt<=scheme['abs_end'])
    extended=bool(scheme.get('abs_end') and scheme.get('extended_end') and scheme['abs_end']<dt<=scheme['extended_end'])
    return normal or extended

def validate_abs_assignment_changes(r, settings, previous=None):
    """Prevent invalid new routing while retaining old drafts for correction."""
    sources={e['id']:{'date':(e.get('original') or e).get('date'),'opening':False} for e in r.get('entries',[]) if e.get('kind')=='receipt'}
    sources.update({e['id']:{'date':e.get('date'),'opening':True} for e in r.get('opening_sources',[])})
    schemes={s['id']:s for s in settings['schemes']}
    old={a['id']:a for a in (previous or {}).get('allocations',[])}
    prior_sources={e['id']:{'date':(e.get('original') or e).get('date'),'opening':False} for e in (previous or {}).get('entries',[]) if e.get('kind')=='receipt'}
    prior_sources.update({e['id']:{'date':e.get('date'),'opening':True} for e in (previous or {}).get('opening_sources',[])})
    for a in r.get('allocations',[]):
        if a.get('type')!='ABS':continue
        source=sources.get(a.get('source'),{})
        if abs_booking_allowed(source,schemes.get(a.get('scheme'))):continue
        before=old.get(a.get('id'))
        # An unchanged/decreased legacy split can be saved, reviewed or removed.
        if before and all(a.get(k)==before.get(k) for k in ('type','source','scheme')) and source==prior_sources.get(a.get('source')) and D(a.get('amount') or 0)<=D(before.get('amount') or 0):continue
        raise ValueError('ABS not allowed for original payment date '+str(source.get('date') or 'missing')+'; choose a payment within the scheme booking period or use CD/Settlement.')

def validate_input_limits(r, settings):
    """Reject impossible splits before saving or producing any benefit preview."""
    settings=effective_settings(r,settings)
    validate_link_sources(r)
    for request in r.get('cn_requests',{}).values():
        if request.get('unit') not in ('kg','packet') or request.get('direction') not in ('increase','decrease'):raise ValueError('Choose a request unit and increase/decrease')
        if D(request.get('rate') or 0)<0:raise ValueError('Requested rate must be zero or positive')
    opening=D(r.get('opening') or 0);due=D(r.get('old_dues') or 0)
    if due<0 or due>max(Decimal(0),opening):raise ValueError('Old dues must be within confirmed opening debit')
    receipts=[];seen=set()
    for e in r.get('entries',[]):
        if D(e.get('debit') or 0)<0 or D(e.get('credit') or 0)<0:raise ValueError('Negative ledger entry')
        if e.get('kind')=='receipt':receipts.append({'id':e.get('id'),'amount':D(e.get('credit') or 0),'date':(e.get('original') or e).get('date')})
    opening_sources=r.get('opening_sources',[])
    if sum((D(x.get('amount') or 0) for x in opening_sources),Decimal(0))>max(Decimal(0),-opening):raise ValueError('Opening-credit sources exceed actual opening credit')
    receipts += [{'id':x.get('id'),'amount':D(x.get('amount') or 0),'date':x.get('date')} for x in opening_sources]
    available={}
    for src in sorted(receipts,key=lambda x:(x['date'] or '',x['id'] or '')):
        if not src['id'] or src['id'] in seen:raise ValueError('Duplicate/missing payment source identity')
        seen.add(src['id'])
        if src['amount']<0:raise ValueError('Negative payment source')
        used=min(due,src['amount']);due-=used;available[src['id']]=src['amount']-used
    assigned=defaultdict(lambda:Decimal(0));seen=set()
    for a in r.get('allocations',[]):
        if not a.get('id') or a['id'] in seen:raise ValueError('Duplicate/missing allocation identity')
        seen.add(a['id']);amount=D(a.get('amount') or 0)
        if amount<0:raise ValueError('Amount to allocate must be zero or positive')
        if r.get('manual_order') and a.get('type')=='CD':
            try:
                order=D(a.get('order') or 0)
                if order<0 or order!=order.to_integral_value():raise ValueError()
            except (ValueError,ArithmeticError):raise ValueError('CD processing order must be a nonnegative whole number; leave blank for 0')
        source=a.get('source')
        if source not in available:
            if amount:raise ValueError('Choose an existing payment source')
            continue
        assigned[source]+=amount
        if assigned[source]>available[source]:raise ValueError('Payment allocated beyond availability: '+source+'; available after old dues '+str(available[source]))
    products={p['id']:p for p in settings['products']};schemes={s['id']:s for s in settings['schemes']}
    season=next((x for x in settings['seasons'] if x['name']==r.get('season')),None)
    totals=defaultdict(lambda:[Decimal(0),Decimal(0),Decimal(0),Decimal(0)])
    for e in r.get('entries',[]):
        if e.get('kind') not in ('sale','return','ipt_in','ipt_out'):continue
        dt=(e.get('original') or e).get('date')
        if season and season.get('confirmed') and season.get('start') and season.get('end') and dt and not stock_in_period(r,e,season):continue
        for item in e.get('items',[]):
            if item.get('exclude'):continue
            p=products.get(item.get('product'))
            if not p:continue
            sc=schemes.get(r.get('scheme_overrides',{}).get(p['scheme'],p['scheme']))
            if not sc:continue
            qty=unit_qty(item.get('qty') or 0,item.get('unit','packet'),sc['unit'],p['packing_kg'])
            if qty<0:raise ValueError('Product quantity cannot be negative')
            t=totals[(sc['id'],p['id'])]
            if e['kind']=='return':t[1]+=qty;t[3]+=D(item.get('amount') or 0)
            else:
                t[0]+=qty*(-1 if e['kind']=='ipt_out' else 1)
                value=D(item.get('amount') or 0);t[2]+=value*((1 if D(e.get('debit') or 0)>=D(e.get('credit') or 0) else -1) if e['kind'].startswith('ipt_') else 1)
    seen=set()
    for split in r.get('cash_splits',[]):
        key=(split.get('scheme'),split.get('product'))
        if key in seen:raise ValueError('Duplicate cash quantity split')
        seen.add(key);sup,ret,sv,rv=totals[key];cs=D(split.get('supplied') or 0);cr=D(split.get('returned') or 0)
        if cs<0 or cr<0 or cr>cs or cs>sup or cr>ret or ret-cr>sup-cs:raise ValueError('Cash/regular quantity conservation: split cannot exceed actual supplied or returned quantity')
        sc=schemes.get(split.get('scheme'))
        if sc and sc['unit']=='packet' and (cs!=cs.to_integral_value() or cr!=cr.to_integral_value()):raise ValueError('Cash packet quantities must be whole packets; use kg calculation for fractional weight')
        for field,limit in [('cash_sales_value',sv),('cash_returns_value',rv)]:
            if split.get(field) not in (None,'') and not 0<=D(split[field])<=limit:raise ValueError('Cash value split exceeds actual invoice/return value')
        if split.get('deduction_rate') not in (None,'') and D(split['deduction_rate'])<0:raise ValueError('Cash deduction cannot be negative')

def physical_items(items):return [{k:i.get(k) for k in ('name','qty','unit','rate','amount')} for i in items]

def payment_work(r):
    opening=D(r.get('opening') or 0);due=D(r.get('old_dues') or 0)
    if due<0 or due>max(Decimal(0),opening):raise ValueError('Old dues must be within confirmed opening debit')
    sources=[{'id':e['id'],'date':(e.get('original') or e).get('date'),'amount':D(e.get('credit') or 0),'opening':False} for e in r.get('entries',[]) if e.get('kind')=='receipt']
    sources += [{'id':x['id'],'date':x.get('date'),'amount':D(x.get('amount') or 0),'opening':True} for x in r.get('opening_sources',[])]
    assigned=defaultdict(lambda:Decimal(0));out=[]
    for a in r.get('allocations',[]):assigned[a.get('source')]+=D(a.get('amount') or 0)
    for src in sorted(sources,key=lambda x:(x['date'] or '',x['id'])):
        if src['amount']<0:raise ValueError('Negative payment source')
        used=min(due,src['amount']);due-=used;out.append({**src,'old_dues_cleared':used,'available':src['amount']-used})
    return out,sum((max(Decimal(0),x['available']-assigned[x['id']]) for x in out),Decimal(0)),due


def stock_fingerprint(entry):
    """Bind period review to physical voucher data, not editable catalogue mapping."""
    payload={k:entry.get(k) for k in ('id','date','kind','debit','credit','reference')}
    payload['source_date']=(entry.get('original') or entry).get('date')
    payload['items']=physical_items(entry.get('items',[]))
    return hashlib.sha256(json.dumps(payload,sort_keys=True,default=str).encode()).hexdigest()

def late_ipt_error(record,entry,season):
    review=record.get('late_ipt_reviews',{}).get(entry.get('id'))
    if review is None:return None
    if not isinstance(review,dict):return 'Invalid late IPT review'
    if entry.get('kind') not in ('ipt_in','ipt_out'):return 'Late-period review is only available for IPT received or given'
    if not season or not season.get('confirmed'):return 'Confirm working-period dates before reviewing late IPT'
    if (review.get('season'),review.get('start'),review.get('end'))!=(record.get('season'),season.get('start'),season.get('end')):return 'Late IPT review belongs to different period dates; review again or remove it'
    dt=(entry.get('original') or entry).get('date')
    try:
        if not iso(season['end'])<iso(dt)<=iso(season['cutoff']):return 'Late IPT must be posted after the period end and on/before the calculation cutoff; review the cutoff if necessary'
    except (ValueError,TypeError,KeyError):return 'Invalid late IPT/period dates'
    if not str(review.get('reason') or '').strip():return 'Enter a reason linking this late IPT to the selected period'
    if review.get('fingerprint')!=stock_fingerprint(entry):return 'Late IPT voucher changed; review it again'
    return ''

def stock_in_period(record,entry,season):
    dt=(entry.get('original') or entry).get('date')
    if not season or not dt or not season.get('start') or not season.get('end'):return False
    return season['start']<=dt<=season['end'] or late_ipt_error(record,entry,season)==''

def late_ipt_issue_conflict(record,previous):
    """A late transfer cannot earn stock benefits again in its posting season."""
    if (record.get('lineage') or record.get('id'))==(previous.get('lineage') or previous.get('id')) and record.get('season')==previous.get('season'):return False
    def selected(r):
        settings=r.get('frozen_settings') or {};season=next((s for s in settings.get('seasons',[]) if s['name']==r.get('season')),None)
        out={}
        for e in r.get('entries',[]):
            if e.get('kind') not in ('ipt_in','ipt_out') or not stock_in_period(r,e,season):continue
            # Original export layout and map IDs do not define transfer identity.
            key=(e.get('id'),(e.get('original') or e).get('date'))
            out[key]=late_ipt_error(r,e,season)==''
        return out
    a,b=selected(record),selected(previous)
    return any(a[k] or b[k] for k in a.keys()&b.keys())

def compute(record,settings):
    with localcontext() as ctx:
        ctx.prec=40
        try:
            limit_error=None
            try:validate_input_limits(record,settings)
            except (ValueError,ArithmeticError) as exc:limit_error=str(exc)
            out=_compute(record,settings)
            if limit_error:
                # Keep source availability visible so a legacy invalid draft can be repaired.
                out.update(CNs=[],proposals=[],groups=[],product_CNs=[],new_CN_total=Decimal(0),final_balance=out['ledger_closing'],party_owes=max(Decimal(0),out['ledger_closing']),excess_credit=max(Decimal(0),-out['ledger_closing']),can_finalise=False)
                out['issues'].insert(0,'Input rejected; no CN preview: '+limit_error)
                out.setdefault('issue_details',[]).insert(0,{'message':out['issues'][0]})
            return out
        except (ValueError, ArithmeticError, KeyError, TypeError) as exc:
            closing=D(record.get('closing') or 0);ledger=closing;sources=[];unallocated=due=Decimal(0)
            try:
                ledger=D(record.get('opening') or 0)+sum((D(e.get('debit') or 0)-D(e.get('credit') or 0) for e in record.get('entries',[])),Decimal(0))
                sources,unallocated,due=payment_work(record)
            except (ValueError,ArithmeticError,KeyError):pass
            issues=['Incomplete or invalid draft input: '+str(exc)];details=[{'message':issues[0]}]
            try:
                cfg=effective_settings(record,settings);active={p['scheme'] for p in cfg['products'] if any(i.get('product')==p['id'] for e in record.get('entries',[]) for i in e.get('items',[]))}
                for sc in cfg['schemes']:
                    if sc['id'] in active:
                        for error in validate_scheme(sc,True):issues.append(sc['name']+': '+error);details.append({'message':issues[-1],'step':3,'scheme':sc['id']})
                if len(details)>1:details[0].update(step=3,scheme=details[1]['scheme'])
            except (ValueError,ArithmeticError,KeyError,TypeError):pass
            return {'engine_version':VERSION,'ledger_computed':ledger,'ledger_closing':closing,'mismatch':ledger-closing,'CNs':[],'proposals':[],'new_CN_total':Decimal(0),'final_balance':closing,'party_owes':max(Decimal(0),closing),'excess_credit':max(Decimal(0),-closing),'groups':[],'sources':sources,'unallocated':unallocated,'old_dues_remaining':due,'issues':issues,'issue_details':details,'information':[],'can_finalise':False}

def _compute(r,settings):
    settings=effective_settings(r,settings)
    issues=[];issue_details=[];info=[];cns=[];groups=[];product_rows=[]
    def flag(message,target=None):
        if message not in issues:
            issues.append(message);issue_details.append({'message':message,**(target or {})})
    products={p['id']:p for p in settings['products']};schemes={s['id']:s for s in settings['schemes']}
    season=next((x for x in settings['seasons'] if x['name']==r.get('season')),None)
    season_valid=False
    try:
        season_valid=bool(season and season.get('confirmed') and iso(season['start'])<=iso(season['end'])<=iso(season['cutoff']))
    except (ValueError,TypeError,KeyError):pass
    if not season_valid:flag('Confirm season dates and calculation cutoff')
    for warning in r.get('import_warnings',[]):
        if any(x in warning for x in ('Unknown dated','Unexpected money','Unsupported voucher','Item without','Running balance','Incomplete item','Closing balance')):flag('Importer requires review: '+warning)
    if r.get('parent') and not r.get('revision_ledger_confirmed'):flag('Revision requires current ledger including previously issued CNs')
    if not r.get('party') or not r.get('state'):flag('Enter party name and address state')
    state=r.get('scheme_state') or r.get('workbook_scheme_state') or r.get('state')
    if r.get('workbook_scheme_state') and r['workbook_scheme_state']!=r.get('state'):info.append('Address state '+str(r.get('state'))+' differs from workbook scheme state '+r['workbook_scheme_state']+'; workbook schemes are used without changing the address.')
    if r.get('scheme_state') and r['scheme_state']!=r.get('state') and not r.get('override_reason'):flag('State override requires reason')
    entries=r.get('entries',[]);opening=D(r.get('opening',0));closing=D(r.get('closing',0))
    if r.get('opening_dues_review_required') and opening>0:
        review=r.get('opening_dues_review') or {}
        if (str(review.get('opening')),str(review.get('old_dues')))!=(str(r.get('opening')),str(r.get('old_dues'))):flag('Confirm opening outstanding handling before allocating payments',{'step':2})
        elif D(r.get('old_dues') or 0)<opening and not str(review.get('reason') or '').strip():flag('Explain the opening balance excluded from old-dues clearance',{'step':2})
    ledger=opening;receipts=[];totals=defaultdict(lambda:{'supplied':Decimal(0),'invoice_supplied':Decimal(0),'ipt_received':Decimal(0),'ipt_given':Decimal(0),'returned':Decimal(0),'billing':Decimal(0),'sales_value':Decimal(0),'returns_value':Decimal(0),'unit_rates':set(),'entries':[]})
    ids=set()
    for reviewed_id in r.get('late_ipt_reviews',{}):
        if not any(e.get('id')==reviewed_id for e in entries):flag('Late IPT review has no matching voucher; remove stale review',{'step':1})
    for e in entries:
        eid=e.get('id')
        if not eid or eid in ids:flag('Duplicate/missing transaction identity')
        ids.add(eid)
        debit=D(e.get('debit',0));credit=D(e.get('credit',0));ledger+=debit-credit
        if debit<0 or credit<0:flag('Negative ledger entry')
        if e.get('classification_required'):flag('Classify voucher as sales return, IPT or other posting: '+str(e.get('reference') or eid),{'step':1,'entry':eid})
        original=e.get('original')
        if original and (any(e.get(k)!=original.get(k) for k in ('date','debit','credit','kind')) or physical_items(e.get('items',[]))!=physical_items(original.get('items',[]))) and not e.get('correction_reason'):flag('Source correction requires a reason: '+str(eid),{'step':1,'entry':eid})
        source_date=(e.get('original') or e).get('date')
        if source_date and e.get('date')!=source_date:flag('Source date changed: eligibility remains original; review '+str(eid))
        try:iso(source_date)
        except (ValueError,TypeError):flag('Invalid/missing source date: '+str(eid))
        review_error=late_ipt_error(r,e,season)
        if review_error:flag(review_error+': '+str(e.get('reference') or eid),{'step':1,'entry':eid,'late_ipt':True})
        elif review_error=='':info.append('Late IPT included once in '+r['season']+': '+str(e.get('reference') or eid)+'; original posting '+str(source_date)+'; '+r['late_ipt_reviews'][eid]['reason'])
        if e.get('kind')=='receipt':receipts.append({'id':eid,'date':source_date,'amount':credit,'opening':False})
        if e.get('kind') not in ('sale','return','receipt','posted_cn','adjustment','ipt_in','ipt_out'):flag('Classify unknown voucher: '+str(eid),{'step':1,'entry':eid})
        if e.get('kind') in ('sale','return','ipt_in','ipt_out'):
            if r.get('annual_ledger') and season_valid and source_date and not stock_in_period(r,e,season):
                info.append('Outside working period; ledger retained, stock excluded: '+str(e.get('reference') or eid))
                continue
            if not e.get('items'):flag('Missing itemised sales/return/IPT detail: '+str(eid),{'step':1,'entry':eid})
            for item in e.get('items',[]):
                pid=item.get('product');p=products.get(pid)
                if item.get('exclude'):
                    if not item.get('review_reason'):flag('Excluded item requires season/scope reason')
                    continue
                if not p:flag('Map product and packing: '+item.get('name','unknown'),{'step':1,'entry':eid,'item_name':item.get('name'),'item_unit':item.get('unit')});continue
                if p.get('deleted_at') and not r.get('frozen_settings'):flag('Selected product is deleted; restore it before calculating: '+p['name'],{'step':1,'entry':eid})
                if p.get('needs_assignment'):flag('Choose a scheme/group for '+p['crop']+' / '+p['name']);continue
                if not e.get('date'):flag('Missing transaction date');continue
                if season_valid and not stock_in_period(r,e,season):
                    flag('Transaction outside selected season: '+str(e.get('reference') or eid)+' / '+str(source_date)+'; review season dates or exclude with a reason',{'step':1,'entry':eid,'settings_section':'seasons'});continue
                s=schemes.get(r.get('scheme_overrides',{}).get(p['scheme'],p['scheme']))
                if not s or pid not in s.get('products',[]) or s.get('segment_id',s['segment'])!=p.get('segment_id',p['segment']):flag('Product not in selected scheme');continue
                qty=unit_qty(item['qty'],item.get('unit','packet'),s['unit'],p['packing_kg'])
                if qty<0:flag('Negative product quantity')
                if (item.get('unit')=='packet' and D(item['qty'])!=D(item['qty']).to_integral_value()) or (s['unit']=='packet' and qty!=qty.to_integral_value()):flag('Fractional packet entry/conversion')
                key=(s['id'],pid);t=totals[key];value=D(item['amount'])
                if e['kind']=='return':t['returned']+=qty;money_sign=-1;t['returns_value']+=value
                else:
                    stock_sign=-1 if e['kind']=='ipt_out' else 1;t['supplied']+=stock_sign*qty
                    t[{'sale':'invoice_supplied','ipt_in':'ipt_received','ipt_out':'ipt_given'}[e['kind']]]+=qty
                    money_sign=(1 if debit>=credit else -1) if e['kind'].startswith('ipt_') else 1;t['sales_value']+=money_sign*value
                t['billing']+=money_sign*value;
                if qty:t['unit_rates'].add(D(item['amount'])/qty)
                t['entries'].append(eid)
            if e.get('items') and sum((D(x['amount']) for x in e['items']),Decimal(0))!=(abs(debit-credit) if e['kind'].startswith('ipt_') else debit if e['kind']=='sale' else credit):flag('Item amounts do not reconcile voucher '+str(eid),{'step':1,'entry':eid})
    for pending in r.get('pending_import_reviews',[]):flag('Re-import correction needs review: '+pending.get('reference',pending['id']),{'step':1,'entry':pending['id'],'reparse':True})
    mismatch=ledger-closing
    if mismatch:flag('Ledger closing mismatch: '+str(mismatch))
    if not r.get('ledger_confirmed'):flag('Confirm reviewed ledger reconciliation')
    # Opening sources are allocation metadata; never add them to accounting receipts.
    for source in r.get('opening_sources',[]):
        receipts.append({'id':source['id'],'date':source.get('date'),'amount':D(source['amount']),'opening':True})
    if sum((x['amount'] for x in receipts if x['opening']),Decimal(0))>max(Decimal(0),-opening):flag('Opening-credit sources exceed actual opening credit')
    due=D(r.get('old_dues',0));availability={};sources={};clearances=[]
    if due<0 or due>max(Decimal(0),opening):flag('Old dues must be within confirmed opening debit')
    for src in sorted(receipts,key=lambda x:(x['date'] or '',x['id'])):
        if src['amount']<0:flag('Negative payment source')
        if src['id'] in sources:flag('Duplicate payment source')
        sources[src['id']]=src
        used=min(max(due,Decimal(0)),src['amount']);due-=used
        availability[src['id']]=src['amount']-used
        clearances.append({**src,'old_dues_cleared':used,'available':src['amount']-used})
        if not src['opening'] and not src['date']:flag('Enter original receipt date: '+src['id'])
    assigned=defaultdict(lambda:Decimal(0));abs_by=defaultdict(lambda:Decimal(0));cd_by=defaultdict(list);cash_by=defaultdict(lambda:Decimal(0));allocation_ids=set()
    for a in r.get('allocations',[]):
        aid=a.get('id')
        if not aid or aid in allocation_ids:flag('Duplicate/missing allocation identity')
        allocation_ids.add(aid)
        src=sources.get(a.get('source'));s=schemes.get(a.get('scheme'));amount=D(a.get('amount',0))
        if not src or not s or amount<0:flag('Invalid allocation source/destination/amount');continue
        assigned[src['id']]+=amount
        if assigned[src['id']]>availability[src['id']]:flag('Payment allocated more than once or beyond availability')
        if r.get('annual_ledger') and season_valid and src['date'] and src['date']>season['cutoff'] and amount and a.get('type')!='Settlement':
            flag('Payment after selected calculation cutoff; use documented Settlement or change cutoff: '+src['id'],{'step':2,'source':src['id']});continue
        if amount and a.get('type')!='Settlement' and r.get('scheme_overrides',{}).get(s['id'],s['id'])!=s['id']:
            flag('Review payment destination after scheme change: '+s['name'],{'step':2,'source':src['id']});continue
        if amount and a.get('type') in ('ABS','Cash','Net') and a.get('product'):
            product=products.get(a['product']);destination=r.get('scheme_overrides',{}).get(product['scheme'],product['scheme']) if product else None
            if destination!=s['id']:flag('Review payment destination after product group/scheme change',{'step':2,'source':src['id']});continue
        if amount and a.get('type')=='CD' and r.get('product_assignments') and not any(sid==s['id'] for sid,pid in totals):flag('Review CD destination after product group/scheme change; use a sold group or Settlement');continue
        if a.get('type')=='ABS':
            pid=a.get('product')
            if 'ABS' not in s['benefits'] or pid not in s['products']:flag('ABS requires eligible product and scheme');continue
            dt=src['date']
            normal=bool(dt and s.get('abs_start') and s.get('abs_end') and s['abs_start']<=dt<=s['abs_end'])
            extended=bool(dt and s.get('abs_end') and s.get('extended_end') and s['abs_end']<dt<=s['extended_end'] and a.get('approved') and str(a.get('remark') or '').strip())
            if not (normal or extended or (src['opening'] and not dt)):
                flag('ABS source outside approved booking period: '+src['id']);continue
            abs_by[(s['id'],pid)]+=amount
        elif a.get('type')=='Net':
            if 'Net' not in s.get('benefits',[]) or not any(ss==s['id'] for ss,pp in totals):flag('Net Rate allocation requires a Net Rate scheme',{'step':2,'source':src['id']})
            elif a.get('product') and a['product'] not in s['products']:flag('Net Rate product does not belong to selected scheme',{'step':2,'source':src['id']})
        elif a.get('type')=='CD':cd_by[s['id']].append({**a,'date':src['date'],'opening':src['opening']})
        elif a.get('type')=='Cash':
            cfg=s.get('cash');pid=a.get('product')
            if not cfg or not products.get(pid) or products[pid]['name'] not in cfg['products'] or not src['date'] or not cfg['start']<=src['date']<=cfg['end']:flag('Cash payment/product outside eligibility');continue
            cash_by[(s['id'],pid)]+=amount
        elif a.get('type')!='Settlement':flag('Unknown allocation type')
    for src in receipts:
        if assigned[src['id']]<availability[src['id']]:flag(('Assign opening credit remainder: ' if src['opening'] else 'Assign ordinary receipt remainder: ')+src['id'],{'step':2,'source':src['id']})
    cash_splits={(x['scheme'],x['product']):x for x in r.get('cash_splits',[])}
    if len(cash_splits)!=len(r.get('cash_splits',[])):flag('Duplicate cash quantity split')
    for key,amount in cash_by.items():
        if amount>0 and (key not in cash_splits or D(cash_splits[key].get('supplied') or 0)<=0):
            flag('Cash supplied/returned split required for '+products[key[1]]['name']+'; select the cash quantity or reassign the payment',{'step':2,'cash_product':key[1]})
    def addcn(s,benefit,precise,working):
        amount=rounded(precise)
        cns.append({'scheme':s['id'],'key':s['crop']+'|'+s.get('segment_id',s['segment'])+'|'+benefit,'crop':s['crop'],'segment':s['segment'],'benefit':benefit,'precise':precise,'rounded':amount,'rounding':amount-precise,'working':working,'narration':s.get('narration','{benefit}').format(party=r.get('party',''),crop=s['crop'],segment=s['segment'],season=r.get('season',''),benefit=benefit)})
    active=set(k[0] for k in totals)|set(cd_by)|set(k[0] for k in abs_by)|set(k[0] for k in cash_by)
    for sid in sorted(active):
        s=schemes[sid]
        if s.get('deleted_at') and not r.get('frozen_settings'):flag('Selected scheme is deleted; restore it or choose an active scheme: '+s['name'])
        for er in validate_scheme(s,True):flag(s['segment']+': '+er)
        if s.get('extra_unit') not in ('fixed','kg','packet'):flag('Invalid extra unit')
        for uk in ('unit','billing_unit','abs_unit','return_unit'):
            if s.get(uk) not in ('kg','packet'):flag('Invalid rate unit: '+uk)
        if s['season']!=r.get('season') or state not in s['states']:flag('No explicit state/season scheme: '+s['segment'])
        if any(products[pid]['crop']!=s['crop'] or products[pid].get('segment_id',products[pid]['segment'])!=s.get('segment_id',s['segment']) or D(products[pid]['packing_kg'])!=D(s['packing_kg']) for ss,pid in totals if ss==sid and pid in products):flag('Scheme crop/packing membership mismatch')
        supplied=returned=billing=principal=excess=abs_cn=Decimal(0);abs_work=[]
        for (schemeid,pid),t in list(totals.items()):
            if schemeid!=sid:continue
            sup,ret=t['supplied'],t['returned'];
            if sup<0:flag('IPT given exceeds adjusted supply: '+products[pid]['name'],{'step':1,'product':pid})
            bill=t['billing'];p=products[pid];cash=cash_splits.get((sid,pid))
            product_row={'key':sid+'|'+pid,'scheme':sid,'scheme_name':s['name'],'product_id':pid,'product':p['name'],'crop':p['crop'],'segment':s['segment'],'packing_kg':D(p['packing_kg']),'unit':s['unit'],'net_sold':max(Decimal(0),sup-ret),'benefits':[],'total_CN':Decimal(0)}
            if cash:
                cs,cr=D(cash['supplied']),D(cash['returned']);cfg=s.get('cash')
                if cs<0 or cr<0 or cr>cs or cs>sup or cr>ret or ret-cr>sup-cs:flag('Cash/regular quantity conservation')
                if not cfg:flag('Cash not enabled for this segment')
                else:
                    csu=unit_qty(cs,s['unit'],cfg['unit'],p['packing_kg']);cru=unit_qty(cr,s['unit'],cfg['unit'],p['packing_kg'])
                    if cash_by[(sid,pid)]<csu*D(cfg['advance']):flag('Cash advance must cover supplied quantity')
                    normal=(csu-cru)*D(cfg['cn_rate']);deduct=Decimal(0)
                    if cr:
                        if cash.get('deduction_rate') in (None,'') or not cash.get('remark'):flag('Resolve cash return deduction with rate and remark')
                        else:deduct=unit_qty(cr,s['unit'],'kg',p['packing_kg'])*D(cash['deduction_rate'])
                    if deduct<0:flag('Cash deduction cannot be negative')
                    if deduct>normal:flag('Cash deduction exceeds CN; review excess '+str(deduct-normal))
                    addcn(s,'Cash '+p['name'],max(Decimal(0),normal-deduct),{'product_id':pid,'normal':normal,'deduction':deduct,'required_advance':csu*D(cfg['advance'])})
                    sup-=cs;ret-=cr
                    # Original invoice/return amounts are preserved; cash uses configured reference value only for split working.
                    if cash.get('cash_sales_value') not in (None,'') and cash.get('cash_returns_value') not in (None,''):
                        csv,crv=D(cash['cash_sales_value']),D(cash['cash_returns_value'])
                        if not cash.get('billing_split_reason') or csv<0 or crv<0 or csv>t['sales_value'] or crv>t['returns_value']:flag('Review traceable cash invoice/return value split')
                        bill-=csv-crv
                    elif len(t['unit_rates'])==1:
                        bill-=(cs-cr)*next(iter(t['unit_rates']))
                    else:
                        flag('Varying invoice rates: enter reviewed cash sales/return values and reason')
            if ret>sup:flag('Returns without matching selected-season supply: '+p['name'])
            net=max(Decimal(0),sup-ret);supplied+=sup;returned+=ret;billing+=bill
            product_row['regular_net']=net;product_rows.append(product_row)
            token_amount=abs_by[(sid,pid)]
            if token_amount and s.get('token') is not None:
                n=unit_qty(net,s['unit'],s.get('abs_unit',s['unit']),p['packing_kg']);eligible=min(n,token_amount/D(s['token']))
                used=eligible*D(s['token']);cn=eligible*D(s['abs_rate']);principal+=used;excess+=token_amount-used;abs_cn+=cn
                abs_work.append({'product_id':pid,'product':p['name'],'allocated':token_amount,'net_sold':n,'unit':s.get('abs_unit',s['unit']),'token_rate':D(s['token']),'CN_rate':D(s['abs_rate']),'eligible':eligible,'principal':used,'excess':token_amount-used,'CN':cn})
        # Allocations to products with zero sales still produce excess ABS for the same segment.
        for (ss,pid),money in list(abs_by.items()):
            if ss==sid and (ss,pid) not in totals:excess+=money
        net=max(Decimal(0),supplied-returned);benefits=s['benefits'];non_cd=Decimal(0)
        if 'Net' in benefits:
            if s.get('net_mode')=='fixed':
                q=unit_qty(net,s['unit'],s['net_cn_unit'],s['packing_kg']);cn=q*D(s['net_cn_rate'])
                if cn<0:flag('Fixed CN cannot be negative');cn=Decimal(0)
                addcn(s,'Net rate',cn,{'mode':'fixed_CN','net_quantity':q,'unit':s['net_cn_unit'],'CN_per_unit':D(s['net_cn_rate'])})
            else:
                row=tier(net,s.get('net',[]));billing_per_unit=D(s['billing'])*unit_qty(1,s['unit'],s['billing_unit'],s['packing_kg']);cn=net*(billing_per_unit-D(row['rate'])) if row else Decimal(0)
                if cn<0:flag('Net rate above billing requires review');cn=max(Decimal(0),cn)
                addcn(s,'Net rate',cn,{'mode':'net_price','net_quantity':net,'unit':s['unit'],'billing_per_unit':billing_per_unit,'tier':row})
            non_cd+=cn
        if 'Quantity' in benefits:
            cn=slab_cn(net,s['quantity'],s.get('quantity_mode','whole'));addcn(s,'Quantity',cn,{'quantity':net,'unit':s['unit'],'tier':tier(net,s['quantity']),'mode':s.get('quantity_mode','whole')});non_cd+=cn
        if 'Extra' in benefits:
            row=tier(net,s['extra']);cn=D(row['rate']) if row else Decimal(0)
            if s.get('extra_unit')!='fixed':cn*=unit_qty(net,s['unit'],s.get('extra_unit','kg'),s['packing_kg'])
            addcn(s,'Extra',cn,{'quantity':net,'tier':row});non_cd+=cn
        if 'ABS' in benefits:addcn(s,'ABS',abs_cn,abs_work);non_cd+=abs_cn
        if 'Return' in benefits:
            percent=returned/supplied*100 if supplied>0 else None
            qualifies=percent is not None and percent<=D(s['return_threshold'])
            cn=unit_qty(net,s['unit'],s.get('return_unit',s['unit']),s['packing_kg'])*D(s['return_rate']) if qualifies else Decimal(0)
            addcn(s,'Return',cn,{'return_percent':percent,'threshold':s['return_threshold'],'qualifies':qualifies});non_cd+=cn
        balance=max(Decimal(0),billing-non_cd-principal);pre_cd=balance;cd_total=Decimal(0);cd_work=[]
        pools=[]
        if excess:
            rate=D(s['cd'][0]['percent'])/100 if 'CD' in benefits and s.get('cd') else Decimal(0)
            pools.append({'id':'Allocated excess ABS','amount':excess,'date':None,'rate':rate,'slab':1 if 'CD' in benefits and s.get('cd') else None,'period':s['cd'][0] if 'CD' in benefits and s.get('cd') else None})
        ordinary=cd_by[sid]
        ordinary=sorted(ordinary,key=lambda a:(int(D(a.get('order') or 0)),a.get('id',''))) if r.get('manual_order') else sorted(ordinary,key=lambda a:(a.get('date') or '',a.get('id','')))
        for a in ordinary:
            dt=a['date'];matches=[w for w in s.get('cd',[]) if dt and w['start']<=dt<=w['end']] if 'CD' in benefits else []
            rate=D(matches[0]['percent'])/100 if matches else Decimal(0)
            if not matches and 'CD' in benefits:info.append('No applicable CD period; 0%: '+a['source'])
            pools.append({**a,'rate':rate,'slab':s['cd'].index(matches[0])+1 if matches else None,'period':matches[0] if matches else None})
        for pool in pools:
            amount=D(pool['amount']);rate=pool['rate'];used=min(amount,balance/(1+rate));cd=used*rate
            balance-=used+cd;cd_total+=cd
            cd_work.append({'allocation':pool['id'],'source':pool.get('source'),'original_date':pool['date'],'slab':pool.get('slab'),'period':pool.get('period'),'assigned':amount,'percent':rate*100,'eligible_payment':used,'unused':amount-used,'CD':cd,'balance_after':balance})
        if 'CD' in benefits:addcn(s,'CD',cd_total,cd_work)
        groups.append({'scheme':sid,'crop':s['crop'],'segment':s['segment'],'supplied':supplied,'invoice_supplied':sum((t['invoice_supplied'] for (ss,pp),t in totals.items() if ss==sid),Decimal(0)),'ipt_received':sum((t['ipt_received'] for (ss,pp),t in totals.items() if ss==sid),Decimal(0)),'ipt_given':sum((t['ipt_given'] for (ss,pp),t in totals.items() if ss==sid),Decimal(0)),'returned':returned,'net':net,'stock_adjusted_supply':sum((t['supplied'] for (ss,pp),t in totals.items() if ss==sid),Decimal(0)),'stock_actual_returned':sum((t['returned'] for (ss,pp),t in totals.items() if ss==sid),Decimal(0)),'unit':s['unit'],'billing':billing,'used_token_principal':principal,'excess_ABS':excess,'pre_CD':pre_cd,'segment_balance':balance,'CD_work':cd_work})
    for key,split in cash_splits.items():
        if key not in totals:flag('Cash split without supplied product')
    prior=r.get('prior_issued',{});proposals=[]
    for cn in cns:
        cn['previous_issued']=D(prior.get(cn['key'],0));cn['proposed']=cn['rounded']-cn['previous_issued']
        if cn['proposed']<0:flag('Negative revised entitlement requires review: '+cn['key'])
        if cn['proposed']!=0:proposals.append(cn)
    for key,amount in prior.items():
        if key not in {cn['key'] for cn in cns} and D(amount)>0:flag('Previously issued benefit removed; review '+key)
    new_total=sum((cn['proposed'] for cn in proposals),Decimal(0));final=closing-new_total
    distribute_product_cns(product_rows,cns,r)
    return {'engine_version':VERSION,'ledger_computed':ledger,'ledger_closing':closing,'mismatch':mismatch,'CNs':cns,'proposals':proposals,'product_CNs':product_rows,'new_CN_total':new_total,'final_balance':final,'party_owes':max(Decimal(0),final),'excess_credit':max(Decimal(0),-final),'groups':groups,'sources':clearances,'unallocated':sum((max(Decimal(0),availability[k]-assigned[k]) for k in availability),Decimal(0)),'old_dues_remaining':due,'issues':issues,'issue_details':issue_details,'information':info,'stock_scope':{e['id']:stock_in_period(r,e,season) for e in entries if e.get('id') and e.get('kind') in ('sale','return','ipt_in','ipt_out')},'can_finalise':not issues}

def apportion_rupees(total,weights):
    """Display attribution only: preserve every already-rounded benefit exactly."""
    weight=sum(weights,Decimal(0))
    if not weight:return [Decimal(0) for _ in weights]
    raw=[total*w/weight for w in weights];out=[x.to_integral_value(rounding=ROUND_FLOOR) for x in raw]
    remainder=int(total-sum(out,Decimal(0)))
    for i in sorted(range(len(weights)),key=lambda i:(-(raw[i]-out[i]),i))[:remainder]:out[i]+=1
    return out

def distribute_product_cns(rows,cns,record):
    rows.sort(key=lambda r:(r['scheme'],r['product_id']))
    for cn in cns:
        members=[r for r in rows if r['scheme']==cn['scheme']]
        if cn['benefit']=='ABS':
            direct={w['product_id']:w['CN'] for w in cn['working']};weights=[direct.get(r['product_id'],Decimal(0)) for r in members]
        elif cn['benefit'].startswith('Cash '):weights=[Decimal(1) if r['product_id']==cn['working']['product_id'] else Decimal(0) for r in members]
        else:weights=[r['regular_net'] for r in members]
        for row,amount in zip(members,apportion_rupees(cn['rounded'],weights)):
            row['benefits'].append({'benefit':cn['benefit'],'CN':amount,'narration':cn['narration']});row['total_CN']+=amount
    for row in rows:
        row['net_packets']=unit_qty(row['net_sold'],row['unit'],'packet',row['packing_kg']);row['net_kg']=unit_qty(row['net_sold'],row['unit'],'kg',row['packing_kg'])
        row['CN_per_packet']=row['total_CN']/row['net_packets'] if row['net_packets'] else Decimal(0)
        row['CN_per_kg']=row['total_CN']/row['net_kg'] if row['net_kg'] else Decimal(0)
        request=record.get('cn_requests',{}).get(row['key'])
        if request:
            quantity=row['net_packets'] if request['unit']=='packet' else row['net_kg'];delta=quantity*D(request.get('rate') or 0)*(1 if request['direction']=='increase' else -1)
            row['request']={**request,'quantity':quantity,'delta':delta,'requested_total':row['total_CN']+delta,'display_only':True}
