"""Financial-year ledger matching and explicitly reviewed carry-forward provenance."""
import copy,re,hashlib,json
from datetime import date,timedelta,datetime
from decimal import Decimal
from ledger_audit import norm,number


def identity(doc):return norm(doc.get('party')),norm(doc.get('location'))
def period(doc):
 s=doc.get('source') or {};start,end=s.get('report_start'),s.get('report_end')
 if not start or not end:
  m=re.search(r'For\s+(\d{2}-[A-Za-z]{3}-\d{2})\s+to\s+(\d{2}-[A-Za-z]{3}-\d{2})',s.get('text',''),re.I)
  if m:start,end=[datetime.strptime(v,'%d-%b-%y').date().isoformat() for v in m.groups()]
 if not start or not end:raise ValueError('PDF reporting period is not recognised; supply ledgers showing April–March dates')
 return date.fromisoformat(start),date.fromisoformat(end)
def reconciles(doc):return number(doc['opening'])+sum((number(e.get('debit'))-number(e.get('credit')) for e in doc.get('entries',[])),Decimal(0))==number(doc['closing'])
def signature(doc):
 entries=[{**{k:e.get(k) for k in ('id','date','kind','debit','credit','reference')},'original_date':(e.get('original') or e).get('date'),'items':[{k:i.get(k) for k in ('name','qty','unit','rate','amount')} for i in e.get('items',[])]} for e in doc.get('entries',[])]
 return hashlib.sha256(json.dumps({'party':identity(doc),'source':doc.get('source'),'opening':doc.get('opening'),'closing':doc.get('closing'),'entries':entries},sort_keys=True,default=str).encode()).hexdigest()

def match_years(previous,current):
 rows=[]
 for i,cur in enumerate(current):
  exact=[j for j,old in enumerate(previous) if identity(cur)==identity(old)]
  candidates=exact or [j for j,old in enumerate(previous) if identity(cur)[0]==identity(old)[0]]
  rows.append({'current_index':i,'party':cur.get('party',''),'location':cur.get('location',''),'candidates':candidates,'previous_index':candidates[0] if len(candidates)==1 else None,'status':'Exact party/location match' if len(exact)==1 else 'Review identity/location' if len(candidates)==1 else 'Ambiguous — choose previous ledger' if candidates else 'No match — choose only after verifying identity'})
 return {'matches':rows}

def analyse_pair(previous,current,identity_reason=''):
 if previous.get('import_error') or current.get('import_error'):raise ValueError('Resolve PDF parsing failures before linking years')
 ps,pe=period(previous);cs,ce=period(current)
 if (ps.month,ps.day)!=(4,1) or (pe.month,pe.day)!=(3,31) or pe.year!=ps.year+1:raise ValueError('Previous ledger must cover the full April–March financial year')
 if cs!=pe+timedelta(days=1) or not cs<=ce<=date(cs.year+1,3,31):raise ValueError('Current ledger must start on the following 1 April; partial current-year reports are allowed')
 if identity(previous)!=identity(current) and not str(identity_reason).strip():raise ValueError('Party/location differs; enter a reason confirming these are the same party')
 for doc,start,end in ((previous,ps,pe),(current,cs,ce)):
  for entry in doc.get('entries',[]):
   dt=(entry.get('original') or entry).get('date')
   if not dt or not start<=date.fromisoformat(dt)<=end:raise ValueError('Source voucher original date is outside its reported financial-year period')
 if not reconciles(previous) or not reconciles(current):raise ValueError('Both source ledgers must reconcile before linking')
 old_close,new_open=number(previous['closing']),number(current['opening'])
 if old_close!=new_open:raise ValueError('31 March closing does not match 1 April opening; review the mismatch before registering advance sources')
 receipts=[{'id':e['id'],'date':(e.get('original') or e).get('date'),'reference':e.get('reference',e['id']),'amount':e['credit'],'source_lines':copy.deepcopy(e.get('source_lines',[]))} for e in previous.get('entries',[]) if e.get('kind')=='receipt' and number(e.get('credit'))>0]
 if len({r['id'] for r in receipts})!=len(receipts):raise ValueError('Ambiguous earlier receipt identities; resolve duplicate ledger entries before linking')
 for receipt in receipts:
  if not receipt['date'] or not ps<=date.fromisoformat(receipt['date'])<=pe:raise ValueError('Earlier receipt original date falls outside its financial-year report')
 activity=[copy.deepcopy(e) for e in previous.get('entries',[]) if e.get('date','')>=str(pe.year)+'-01-01']
 return {'previous_start':ps.isoformat(),'previous_end':pe.isoformat(),'current_start':cs.isoformat(),'current_end':ce.isoformat(),'previous_close':old_close,'current_opening':new_open,'maximum_opening_credit':max(Decimal(0),-new_open),'receipts':receipts,'jan_march_activity':activity,'identity_reason':identity_reason,'previous_signature':signature(previous),'current_signature':signature(current),'message':'Review January–March sales, returns, transfers, CNs and receipts below. Confirm only the unspent portion of each original receipt; no FIFO or automatic ABS balance is assumed.'}

def attach_link(record,previous,current,confirmed,reason,identity_reason='',replace_unused=False):
 review=analyse_pair(previous,current,identity_reason)
 if identity(record)!=identity(current) or number(record['opening'])!=number(current['opening']):raise ValueError('Saved current party/opening does not match this financial-year source')
 if record.get('status')!='draft':raise ValueError('Create a draft revision before linking a frozen calculation')
 if not str(reason).strip():raise ValueError('Enter your reconciliation/review note before saving the year link')
 out=copy.deepcopy(record);old_sources=out.get('opening_sources',[]);allocations=out.get('allocations',[])
 # Updating a link never silently destroys source allocations.
 if out.get('prior_year_link') and out['prior_year_link']['previous_signature']!=review['previous_signature']:raise ValueError('A different prior ledger is already linked. Review it in a separate draft before replacing provenance')
 keep=[]
 for src in old_sources:
  allocated=any(a.get('source')==src['id'] for a in allocations)
  if src.get('year_link_receipt'):
   desired=number(confirmed.get(src['year_link_receipt'],0))
   if allocated and desired!=number(src['amount']):raise ValueError('Remove/review allocations from traced opening sources before changing their amounts')
   continue
  if replace_unused and not src.get('date'):
   if allocated:raise ValueError('Cannot replace an undated opening source with existing allocations')
   continue
  keep.append(src)
 receipt_by={r['id']:r for r in review['receipts']};confirmed_clean={}
 for rid,amount in confirmed.items():
  amount=number(amount)
  if rid not in receipt_by:raise ValueError('Selected earlier receipt was not found in the previous PDF')
  if amount<0 or amount>number(receipt_by[rid]['amount']):raise ValueError('Confirmed unspent amount must be within the original receipt')
  confirmed_clean[rid]=str(amount)
  if amount:
   receipt=receipt_by[rid];keep.append({'id':'fy-'+review['previous_signature'][:12]+'-'+rid,'amount':str(amount),'date':receipt['date'],'year_link_receipt':rid,'year_link_signature':review['previous_signature'],'remark':str(reason).strip(),'label':'Prior FY receipt '+receipt['reference']})
 if sum((number(s['amount']) for s in keep),Decimal(0))>review['maximum_opening_credit']:raise ValueError('Traced and existing opening sources together exceed actual opening credit; review existing source registrations')
 out['prior_year_link']={**review,'previous_document':copy.deepcopy(previous),'current_source':copy.deepcopy(current.get('source')),'confirmed_remaining':confirmed_clean,'review_note':str(reason).strip()}
 out['opening_sources']=keep;out['ledger_confirmed']=False
 return out

def validate_link_sources(record):
 linked=[s for s in record.get('opening_sources',[]) if s.get('year_link_receipt')]
 link=record.get('prior_year_link')
 if not linked:return
 if not link:raise ValueError('Traced opening source has no prior-year proof')
 previous=link['previous_document']
 if signature(previous)!=link['previous_signature'] or number(previous['closing'])!=number(record['opening']):raise ValueError('Prior-year proof/opening changed; review the year link again')
 receipts={e['id']:e for e in previous['entries'] if e.get('kind')=='receipt'};totals={}
 for src in linked:
  rid=src['year_link_receipt'];e=receipts.get(rid)
  if not e or src.get('date')!=(e.get('original') or e).get('date') or src.get('year_link_signature')!=link['previous_signature']:raise ValueError('Traced opening receipt identity/date changed')
  totals[rid]=totals.get(rid,Decimal(0))+number(src['amount'])
  if totals[rid]>min(number(e['credit']),number(link['confirmed_remaining'].get(rid,0))):raise ValueError('Traced opening source exceeds its confirmed unspent original receipt')


def traced_credit_conflict(record,previous_records):
 """Reserve explicitly traced money across issued calculations; revisions replace lineage usage."""
 def lineage(r):return r.get('lineage') or r.get('id')
 latest={}
 for old in previous_records:
  if old.get('status')!='issued' or identity(old)!=identity(record) or lineage(old)==lineage(record):continue
  key=lineage(old)
  if key not in latest or (old.get('issued_at',''),old.get('saved_at',''))>(latest[key].get('issued_at',''),latest[key].get('saved_at','')):latest[key]=old
 totals={};budgets={}
 for r in [*latest.values(),record]:
  link=r.get('prior_year_link')
  if not link:continue
  receipts={e['id']:e for e in link['previous_document']['entries'] if e.get('kind')=='receipt'}
  for source in r.get('opening_sources',[]):
   rid=source.get('year_link_receipt');e=receipts.get(rid)
   if not e:continue
   key=(rid,(e.get('original') or e).get('date'),str(number(e['credit']).normalize()))
   budgets[key]=max(budgets.get(key,Decimal(0)),number(link['confirmed_remaining'].get(rid,0)))
   amount=sum((number(a.get('amount')) for a in r.get('allocations',[]) if a.get('source')==source['id']),Decimal(0))
   totals[key]=totals.get(key,Decimal(0))+amount
 return any(amount>budgets[key] for key,amount in totals.items())
