'use strict';
// Keep the Update35.2 renderers and event handlers. This file adapts transport,
// ownership and canonical source actions; it does not replace calculator pages.
let nativeStale=null,nativePendingImport=null;
const nativeTransport=api;
const nativeRoutes={state:'native-state',import:'native-import','bulk-import':'native-bulk-import','audit-import':'native-audit-import','audit-check':'native-audit-check','audit-review':'native-audit-review','audit-map':'native-audit-map','audit-bulk-nrv':'native-audit-bulk-nrv','year-match':'native-year-match','year-pair':'native-year-pair','year-link-save':'native-year-link-save','bulk-document':'native-bulk-document',backup:'native-backup',restore:'native-restore','project-export':'native-project-export','project-import':'native-project-import',reparse:'native-reparse','late-ipt-review':'native-late-ipt-review'};
api=async(path,data,background=false)=>{
 const name=path.replace('/api/','');
 if(['audit-review','audit-map'].includes(name))data={...data,documents:auditDocuments};
 if(name==='calculate'&&nativeStale&&nativeStale.id===record?.id)return nativeTransport('/api/native-stale-result',{id:record.id},background);
 if(['import','reparse'].includes(name))data={...(name==='reparse'?{record_id:record.id}:data),season:record?.season||state.settings.seasons[0]?.name};
 if(name==='backup')data={};
 if(name==='workbook-print'&&background)path='/api/workbook-review';
 else if(nativeRoutes[name])path='/api/'+nativeRoutes[name];
 return nativeTransport(path,data,background);
};
const nativeSaveDraft=saveDraft;
saveDraft=async()=>{
 if(nativeStale&&nativeStale.id===record?.id)return;
 if(record?.status==='draft'&&record.web_source&&record.id){
  const current=await nativeTransport('/api/record',{id:record.id});
  if(current.source_error){nativeStale={id:record.id,message:current.source_error};return;}
 }
 const pending=nativeSaveDraft();
 // Report this failure to its caller, but let a corrected draft retry on the
 // next action instead of leaving every await saveQueue permanently rejected.
 saveQueue=pending.catch(()=>{});
 return pending;
};
const nativeWorkspace=workspace;
workspace=()=>{
 nativeWorkspace();
 if(!nativeStale||nativeStale.id!==record?.id||page!=='Calculate CN')return;
 $('#work')?.querySelectorAll('input,select,textarea,button').forEach(e=>e.disabled=true);
 $('#main').insertAdjacentHTML('afterbegin','<div class="warn">'+esc(nativeStale.message)+' Saved vouchers and allocations are retained. <button data-native-refresh>Review updated source</button></div>');
};
async function nativeAdopt(r,targetStep=1){
 $('#modal')?.close();
 record=r;nativeStale=null;mappingCropChoices={};editEpoch++;
 await refresh();page='Calculate CN';step=targetStep;await calculate();render();globalThis.scrollTo?.(0,0);
}
const nativeMergeImport=mergeImport;
mergeImport=async data=>{
 if(data.native_record){await nativeAdopt(data.native_record);toast('Imported as draft. Review vouchers, aliases and season classifications.');return;}
 if(data.native_import_review){
  nativePendingImport=data;const rows=data.preview.results.filter(r=>r.candidates.length),row=rows[0];
  modal('<h2>Repeat import review</h2><p>Already-imported vouchers remain saved. Review changed/new entries before replacing this statement. Completed history is retained.</p>'+Object.entries(row.comparison||{}).map(([label,count])=>'<p>'+esc(label)+': '+count+'</p>').join('')+'<label>Existing statement<select id="native-replacement">'+row.candidates.map(id=>option(id,row.party+' · '+id.slice(0,6),row.candidates[0])).join('')+'</select></label><label>Review note<input id="native-import-reason" placeholder="Reason for accepting the changed statement"></label><button id="native-commit-import" class="primary">Apply reviewed statement</button>');return;
 }
 return nativeMergeImport(data);
};
openRecord=async id=>{
 clearTimeout(saveTimer);await saveQueue;await saveDraft();
 if(id.startsWith('source:')){const source=state.records.find(r=>r.id===id);return nativeAdopt(await nativeTransport('/api/native-open',{ledger_id:id.slice(7),season:source?.season||state.settings.seasons[0]?.name}));}
 const opened=await nativeTransport('/api/record',{id});
 if(opened.record.deleted_at)throw Error('Restore this party from Deleted Parties first.');
 record=opened.record;nativeStale=opened.source_error?{id:record.id,message:opened.source_error}:null;
 $('#modal').close();page='Calculate CN';step=record.entries?.length||record.source?1:0;
 if(nativeStale)await calculate();else result=opened.result;
 mappingCropChoices={};render();globalThis.scrollTo?.(0,0);
};
const nativeInlineMapping=saveInlineMapping;
saveInlineMapping=async(index,values)=>{
 if(!record?.web_source)return nativeInlineMapping(index,values);
 clearTimeout(saveTimer);await saveQueue;await saveDraft();
 const group=mappingGroups()[index],first=group.items[0];
 const saved=await nativeTransport('/api/native-map',{id:record.id,revision:record.revision,entry_id:first.entry.id,item_index:first.entry.items.indexOf(first.item),crop:values.crop.trim(),name:values.name.trim(),packing:String(values.packing).trim()});
 record=saved.record;nativeStale=null;editEpoch++;await refresh();await calculate();render();return state.settings.products.find(p=>p.id===saved.product_id);
};
const nativeReviewBulk=reviewBulk;
reviewBulk=async id=>{const pending=await api('/api/bulk-document',{id});if(!pending.native_data)return nativeReviewBulk(id);await mergeImport(await nativeTransport('/api/native-import',{data:pending.native_data,filename:pending.filename,season:pending.season}));};
const nativeDrawNav=drawNav;
drawNav=()=>{nativeDrawNav();const context=$('#workspace-context'),season=state?.settings?.seasons?.find(s=>s.name===record?.season)||state?.settings?.seasons?.[0];if(context&&season){const year=Number(season.start?.slice(0,4)),month=Number(season.start?.slice(5,7)),fy=year-(month<4?1:0);context.textContent+=' · '+season.name+(year?' · FY '+fy+'–'+(fy+1):'');}const foot=$('#nav .nav-foot');if(foot){const link=document.createElement('a');link.href='/account';link.textContent='Account & Settings';foot.append(link);const version=document.createElement('small');version.dataset.webBuild='7.2.1';version.textContent='Phase 7.2.1';foot.append(version);const storage=document.createElement('a');storage.href='/account';storage.textContent='Storage usage';foot.append(storage);fetch('/api/workspace',{credentials:'same-origin'}).then(r=>r.ok?r.json():null).then(w=>{if(w)storage.textContent='Storage: '+(w.used_bytes/1048576).toFixed(2)+' / '+(w.quota_bytes/1048576).toLocaleString()+' MiB';}).catch(()=>{});}};
projectNav=()=>`<label class="workbook-nav project-nav">Working project<select id="project-select">${(state?.projects||[]).map(p=>option(p.id,p.name,activeProject)).join('')}</select><small>Independent project · edits stay here</small></label>`;
const nativeWorkbookNav=workbookNav;
workbookNav=()=>nativeWorkbookNav().replace(/<option value="legacy"[^>]*>Existing calculations<\/option>/,'');
// Existing forms remain unchanged. Configuration/transition rights are enforced
// server-side, including inline mapping, Save and alternate mutation routes.
document.addEventListener('click',async e=>{
 const b=e.target.closest('button');if(!b)return;
 try{
  if(b.id==='native-commit-import'){
   e.stopImmediatePropagation();if(!nativePendingImport)return;
   const r=await nativeTransport('/api/native-replace-import',{...nativePendingImport.request,replacement:$('#native-replacement').value,reason:$('#native-import-reason').value,expected:nativePendingImport.preview.preview_digest});nativePendingImport=null;$('#modal').close();await mergeImport(r);return;
  }
  if(b.hasAttribute('data-native-refresh')){e.stopImmediatePropagation();modal('<h2>Review updated source</h2><p>'+esc(nativeStale?.message)+' Existing draft corrections and payment allocations are retained for review. Completed records remain frozen.</p><button id="native-refresh-confirm" class="primary">Open updated ledger</button>');return;}
  if(b.id==='native-refresh-confirm'){e.stopImmediatePropagation();const r=await nativeTransport('/api/native-refresh',{id:record.id,revision:record.revision});$('#modal').close();await nativeAdopt(r);return;}
  if(b.dataset.action==='fixture'){e.stopImmediatePropagation();toast('Import your Tally PDF using Import Tally PDF.');return;}
  if(b.dataset.action==='export'){e.stopImmediatePropagation();if(record.status==='draft')await saveDraft();const prepared=await nativeTransport('/api/print-record',{id:record.id,revision:record.revision});download('CN-'+(prepared.record.party||'draft').replace(/[^a-z0-9]/gi,'_')+'.json',prepared);}
 }catch(err){toast(err.message);}
},true);
printCNSummary=async(detailed=false)=>{
 if(record.status==='draft'){clearTimeout(saveTimer);await saveDraft();}
 const prepared=await nativeTransport('/api/print-record',{id:record.id,revision:record.revision});record=prepared.record;result=prepared.result;
 $('#print-summary').innerHTML=detailed?detailedCNPrintSummary():cnPrintSummary();window.print();
};

// Install transport before the first state read, including older source-only parties.
startCN();

async function startCN(){
 const direct=globalThis.cnWebFetch;
 async function read(path){const r=await direct(path,{credentials:'same-origin'});const d=await r.json();if(!r.ok)throw Error(d.error||'Unable to load your account');return d;}
 try{
  const me=await read('/api/me');
  if(me.user.must_change_password){location.assign('/account');return;}
  const projects=(await read('/api/data/projects')).items;
  const books=(await read('/api/data/workbooks')).items.filter(w=>projects.some(p=>p.id===w.project));
  if(books.length){
   const chosen=books.find(w=>w.project===activeProject&&w.id===activeWorkbook)||books.find(w=>w.project===activeProject)||books[0];
   activeProject=chosen.project;activeWorkbook=chosen.id;
   globalThis.cnStartCalculator();return;
  }
  $('#workspace-context').textContent='Your private CN workspace';
  $('#nav').innerHTML='<h2>All Crop CN</h2><p>Dashboard</p><a href="/account">Account &amp; Settings</a>';
  const allowed=['edit_ledger','edit_schemes'].every(p=>me.user.permissions.includes(p));
  $('#main').innerHTML='<div class="page-masthead"><div><span class="eyebrow">WELCOME</span><h1>Dashboard</h1><p>Create your first workbook to start your CN work.</p></div></div>'+
   (allowed?`<section class="card"><h2>Create your first workbook</h2><p>A workbook keeps one state and working season together, with its own schemes and parties.</p><form id="first-workbook"><label>Workbook name<input name="name" required maxlength="100" placeholder="e.g. Gujarat Kharif 2026"></label><label>State<input name="state" required maxlength="100" placeholder="e.g. Gujarat"></label><label>Working season<input name="period" required maxlength="100" placeholder="e.g. Kharif 2026"></label><div class="grid"><label>Season starts<input type="date" name="start" required></label><label>Season ends<input type="date" name="end" required></label><label>Calculation cutoff<input type="date" name="cutoff" required></label></div><p class="muted">Cutoff is the last date included for reviewed late entries. Financial-year statements can still cover April–March.</p><button class="primary" type="submit">Create workbook &amp; open dashboard</button><p id="first-error" role="alert"></p></form></section>`:
   '<section class="card"><h2>Your workspace is ready</h2><p>You need Edit ledger and Edit schemes permissions to create your first workbook. Ask your administrator to enable them for your own account.</p><a href="/account">Account &amp; Settings</a></section>');
  const f=$('#first-workbook');if(f)f.addEventListener('submit',async e=>{
   e.preventDefault();const button=f.querySelector('button');button.disabled=true;$('#first-error').textContent='';
   try{const data=Object.fromEntries(new FormData(f));if(projects.length)data.project=projects[0].id;
    const r=await direct('/api/portal/start-workbook',{method:'POST',credentials:'same-origin',headers:{'Content-Type':'application/json','X-CSRF-Token':me.csrf_token},body:JSON.stringify(data)});
    const d=await r.json();if(!r.ok)throw Error(d.error||'Unable to create workbook');
    activeProject=d.project;activeWorkbook=d.workbook;globalThis.cnStartCalculator();
   }catch(err){$('#first-error').textContent=err.message;button.disabled=false;}
  });
 }catch(err){$('#main').innerHTML='<h1>All Crop CN</h1><p>'+esc(err.message)+'</p><a href="/portal">Sign in / choose application</a> · <a href="/account">Account &amp; Settings</a>';}
}

// Prior-year receipts live inside Assign Payments. Canonical PDF amounts are read server-side.
let paymentHistoryReview=null,paymentHistoryRequest=0;
const historyPaymentTab=paymentTab;
paymentTab=()=>`<div class="card"><span class="eyebrow">PREVIOUS-YEAR PAYMENT EVIDENCE</span><h2>Prior receipts & crop reservations</h2><p>Upload last year's statement. Seller name and full address are matched automatically to this saved statement; no retyping. Earlier dues clear first. Later crop invoices do not consume a reservation.</p>${record.payment_history?`<p class="ok">Linked ${esc(record.payment_history.start)}–${esc(record.payment_history.end)} · ${(record.reserved_sources||[]).length} reserved receipt(s).</p><details><summary>Saved receipt and earlier-dues working</summary><table><tr><th>Receipt</th><th>Received</th><th>Earlier dues</th><th>Late CN adjustment</th><th>Cleared</th><th>Available</th></tr>${record.payment_history.plan.rows.map(r=>`<tr><td>${date(r.date)} · ${esc(r.reference)}</td><td>${money(r.amount)}</td><td>${money(r.earlier_dues)}</td><td>${money(r.cn_adjustment)}</td><td>${money(r.cleared)}</td><td>${money(r.available)}</td></tr>`).join('')}</table></details>`:''}<button data-payment-history-open data-edit ${record.status!=='draft'||!record.web_source?'disabled':''}>${record.payment_history?'Review prior receipts':'Add previous-year statement PDF'}</button>${record.payment_history||record.prior_year_link?'<button data-payment-history-unlink data-edit>Unlink previous year</button>':''}${!record.web_source?'<p>Import/open the current statement first.</p>':''}</div>`+historyPaymentTab();
const historySourceLabel=sourceLabel;
sourceLabel=id=>(record.reserved_sources||[]).find(s=>s.id===id)?.label||historySourceLabel(id);
const historyOpeningAvailable=openingCreditAvailable;
openingCreditAvailable=()=>{if(!(record.reserved_sources||[]).length)return historyOpeningAvailable();return exactDifference(String(Math.max(0,-Number(record.opening)-allocationTotal(record.reserved_sources))),record.opening_sources.map(s=>s.amount||0));};
const historyOpeningPanel=openingCreditPanel;
openingCreditPanel=()=>{if(!(record.reserved_sources||[]).length)return historyOpeningPanel();const free=Math.max(0,-Number(record.opening)-allocationTotal(record.reserved_sources));return free>0?`<div class="card"><h2>Opening credit available for ABS</h2><p>Total opening credit <strong>${money(Math.max(0,-Number(record.opening)))}</strong> · Protected prior receipts <strong>${money(allocationTotal(record.reserved_sources))}</strong> · Other carried credit <strong>${money(free)}</strong>.</p><p>Unused carried credit, including prior CN credit, can fund next-season ABS. Each amount is allocated once.</p><button data-action="opening-source" data-edit>Allocate available opening credit</button></div>`:'';};
const historyDuesPanel=openingDuesPanel;
openingDuesPanel=()=>{if(!(record.reserved_sources||[]).length)return historyDuesPanel();return `<section class="opening-dues-panel"><div><h3>Earlier dues with protected crop reservations</h3><p>Net statement opening ${money(record.opening)} + protected receipts ${money(allocationTotal(record.reserved_sources))} = gross opening dues ${money(Math.max(0,Number(record.opening)+allocationTotal(record.reserved_sources)))}.</p><p>Ordinary receipts clear ${money(record.old_dues)} first; still due ${money(result.old_dues_remaining)}. Protected receipts have already cleared their own earlier dues and are not deducted twice.</p></div></section>`;};
async function openPaymentHistory(){
 clearTimeout(saveTimer);await saveQueue;await saveDraft();
 paymentHistoryReview=null;paymentHistoryRequest++;
 modal(`<h2>Previous-year receipts · ${esc(record.party)}</h2><p>${esc(record.address||record.location)}. The current saved statement is used automatically.</p><label>Previous full April–March statement PDF<input id="payment-history-file" type="file" accept=".pdf,application/pdf"></label><p id="payment-history-status">Choose the PDF. Same seller name/address and year-boundary balances must match.</p><div id="payment-history-body"></div>`);
}
function readHistoryApprovals(){if(!paymentHistoryReview)return [];return [...document.querySelectorAll('[data-history-cn]')].filter(el=>el.value).map(el=>({cn:el.dataset.historyCn,receipt:el.value,earned:document.querySelector('[data-history-earned="'+el.dataset.historyCn+'"]').value,reason:document.querySelector('[data-history-cn-note="'+el.dataset.historyCn+'"]').value}));}
function renderHistoryPlan(){
 const h=paymentHistoryReview,p=h.plan,crops=catalogCrops();
 $('#payment-history-body').innerHTML=`<div class="ok">${esc(h.match.message)}<br>${esc(h.match.current.party)} · ${esc(h.match.current.address)}</div><p>${date(p.previous_end)} closing ${money(p.previous_close)} = current opening ${money(p.current_opening)}. No receipt is inserted into the ledger again.</p><div class="grid"><label>Receipt period from<input id="payment-history-from" type="date" value="${esc(p.start)}"></label><label>To<input id="payment-history-to" type="date" value="${esc(p.end)}"></label></div><details><summary>Late-posted CNs earned before a receipt (optional)</summary><p>Amounts and posting dates come from the PDF. Only choose the affected receipt, actual earlier earning date and approval evidence. A CN is used once; do not approve one already reflected in the earlier dues.</p>${p.cn_candidates.map(c=>{const a=(p.approvals||[]).find(a=>a.cn===c.id);return `<div class="card"><strong>${date(c.date)} · ${esc(c.reference)} · ${money(c.credit)}</strong><label>Release against earlier receipt<select data-history-cn="${esc(c.id)}">${option('','No retrospective adjustment',a?.receipt||'')}${p.rows.map(r=>option(r.id,date(r.date)+' · '+r.reference,a?.receipt||'')).join('')}</select></label><label>Earned before receipt on<input type="date" data-history-earned="${esc(c.id)}" value="${esc(a?.earned||'')}"></label><label>Approval evidence / reason<input data-history-cn-note="${esc(c.id)}" value="${esc(a?.reason||'')}"></label></div>`;}).join('')||'<p>No posted CNs in this statement.</p>'}</details><button id="payment-history-recalculate">Refresh receipt working</button><div class="tablewrap"><table><tr><th>Reserve</th><th>Original receipt</th><th>Received</th><th>Earlier dues</th><th>Approved CN</th><th>Dues cleared</th><th>Available</th><th>Crop</th><th>Reserve amount ₹</th></tr>${p.rows.map((r,i)=>{const prior=(record.reserved_sources||[]).find(s=>s.receipt===r.id);return `<tr><td><input type="checkbox" data-history-select="${i}" ${Number(r.available)<=0?'disabled':''} ${prior?'checked':''}></td><td>${date(r.date)}<br>${esc(r.reference)}</td><td>${money(r.amount)}</td><td>${money(r.earlier_dues)}</td><td>${money(r.cn_adjustment)}</td><td>${money(r.cleared)}</td><td>${money(r.available)}</td><td><select data-history-crop="${i}">${option('','Choose crop',prior?.crop||'')}${crops.map(c=>option(c,c,prior?.crop||'')).join('')}</select></td><td><input data-history-amount="${i}" type="number" min="0" max="${esc(r.available)}" step="0.01" value="${esc(prior?.amount||r.available)}"></td></tr>`;}).join('')}</table></div><p>Only selected receipts are reserved. Unselected receipts were included in this period's chronological working; later invoices cannot consume the available portion shown. Review/reduce an available amount if it already settled another purpose.</p><details><summary>Original prior-year activity</summary><div class="tablewrap"><table><tr><th>Date / reference</th><th>Type</th><th>Debit</th><th>Credit</th></tr>${p.activity.map(e=>`<tr><td>${date(e.date)} · ${esc(e.reference)}</td><td>${esc(e.kind)}</td><td>${money(e.debit)}</td><td>${money(e.credit)}</td></tr>`).join('')}</table></div></details><p role="status">Review any earlier settlement or late-CN exceptions. Each amount can be allocated only once.</p><button id="payment-history-save" class="primary">Save reviewed receipt sources</button>`;
 h.dirty=false;
}
async function refreshHistoryPlan(){const h=paymentHistoryReview;if(!h)throw Error('Upload a statement first');const approvals=readHistoryApprovals();const p=await nativeTransport('/api/native-payment-history-preview',{id:record.id,revision:record.revision,previous:h.previous,start:$('#payment-history-from').value,end:$('#payment-history-to').value,approvals});h.plan=p;renderHistoryPlan();}
document.addEventListener('change',async e=>{
 const t=e.target;
 if(t.id==='payment-history-file'){
  e.stopImmediatePropagation();const file=t.files[0];if(!file)return;
  const request=++paymentHistoryRequest,historyRecordId=record.id;paymentHistoryReview=null;$('#payment-history-body').innerHTML='';$('#payment-history-status').textContent='Reading and matching '+file.name+'…';t.disabled=true;
  try{const imported=await api('/api/audit-import',{data:await fileBase64(file),filename:file.name});
   if(request!==paymentHistoryRequest||!$('#modal').open||record.id!==historyRecordId)return;
   const h=await nativeTransport('/api/native-payment-history-match',{id:record.id,revision:record.revision,documents:imported.documents});if(request!==paymentHistoryRequest||!$('#modal').open||record.id!==historyRecordId)return;paymentHistoryReview=h;$('#payment-history-status').textContent='Matched automatically. Amounts, dates and earlier-dues working were read from the PDFs.';renderHistoryPlan();
  }catch(err){if(request===paymentHistoryRequest&&$('#modal').open&&$('#payment-history-status')){$('#payment-history-status').textContent=err.message;toast(err.message);}}finally{if(t.isConnected)t.disabled=false;}
  return;
 }
 if(t.id?.startsWith('payment-history-')||t.hasAttribute('data-history-cn')||t.hasAttribute('data-history-earned')||t.hasAttribute('data-history-cn-note')){
  if(t.id==='payment-history-confirm')return;
  if(paymentHistoryReview){paymentHistoryReview.dirty=true;$('#payment-history-save')?.setAttribute('disabled','');}
 }
},true);
document.addEventListener('click',async e=>{
 const b=e.target.closest('button');if(!b)return;
 try{
  if(b.hasAttribute('data-payment-history-unlink')){e.stopImmediatePropagation();clearTimeout(saveTimer);await saveQueue;await saveDraft();const r=await nativeTransport('/api/native-payment-history-unlink',{id:record.id,revision:record.revision});await nativeAdopt(r,2);toast('Previous year unlinked. Opening credit remains available for allocation.');return;}
  if(b.hasAttribute('data-payment-history-open')){e.stopImmediatePropagation();await openPaymentHistory();return;}
  if(b.id==='payment-history-recalculate'){e.stopImmediatePropagation();b.disabled=true;try{await refreshHistoryPlan();}finally{if(b.isConnected)b.disabled=false;}return;}
  if(b.id==='payment-history-save'){
   e.stopImmediatePropagation();const h=paymentHistoryReview;if(!h||h.dirty)throw Error('Refresh receipt working after changing dates or CN approvals.');
   const selections=[...document.querySelectorAll('[data-history-select]:checked')].map(t=>{const i=+t.dataset.historySelect;return {receipt:h.plan.rows[i].id,crop:document.querySelector('[data-history-crop="'+i+'"]').value,amount:document.querySelector('[data-history-amount="'+i+'"]').value};});
   b.disabled=true;try{const r=await nativeTransport('/api/native-payment-history-save',{id:record.id,revision:record.revision,previous:h.previous,start:h.plan.start,end:h.plan.end,approvals:h.plan.approvals,selections});$('#modal').close();await nativeAdopt(r,2);toast('Prior receipts saved with original dates and protected crop reservations. Choose ABS/CD/Settlement explicitly.');}finally{if(b.isConnected)b.disabled=false;}return;
  }
 }catch(err){toast(err.message);}
},true);

// Carried credit is booked on the explicitly selected conversion date.
allocateOpeningCredit=async()=>{
 if(record.status!=='draft')return;
 const available=openingCreditAvailable(),schemes=calculationSettings().schemes.filter(s=>s.benefits.includes('ABS'));
 if(Number(available)<=0){toast('No unregistered opening credit remains. Review existing sources and allocations.');return;}
 modal(`<h2>Convert carried credit to booking</h2><p>Available ${money(available)}. Original statement dates remain in the linked evidence; this conversion date controls the booking slab.</p><label>Crop<select id="credit-crop">${[...new Set(schemes.map(s=>s.crop))].map(c=>option(c,c,'')).join('')}</select></label><label>Scheme<select id="credit-scheme">${schemes.filter(s=>s.crop===schemes[0]?.crop).map(s=>option(s.id,s.name+' · '+s.crop,'')).join('')}</select></label><label>Conversion date<input id="credit-date" type="date"></label><label>Amount ₹<input id="credit-amount" type="number" min="0.01" step="0.01" value="${esc(available)}"></label><button id="credit-convert" class="primary">Convert credit</button><button id="closemodal">Cancel</button>`);
};
document.addEventListener('click',async e=>{
 const b=e.target.closest('#credit-convert');if(!b)return;e.stopImmediatePropagation();
 try{
  const crop=$('#credit-crop').value,scheme=$('#credit-scheme').value,dt=$('#credit-date').value,amount=$('#credit-amount').value;
  const sc=calculationSettings().schemes.find(s=>s.id===scheme);
  if(!sc||sc.crop!==crop)throw Error('Choose a scheme belonging to the selected crop.');
  if(!dt||!(Number(amount)>0)||Number(amount)>Number(openingCreditAvailable()))throw Error('Choose a conversion date and an amount within available credit.');
  const source={id:uid(),amount,date:dt,conversion:true,crop,scheme,original_date:null};
  const candidate={...record,opening_sources:[...record.opening_sources,source]};
  await api('/api/validate-limits',candidate);record.opening_sources.push(source);
  record.allocations.push({id:uid(),source:source.id,type:'ABS',scheme,product:'',amount:'0',remark:'Carried-credit conversion '+dt});
  paymentSelectedId=record.allocations.at(-1).id;changed();await saveDraft();$('#modal').close();await calculate();render();toast('Credit converted. Choose the product and allocation amount.');
 }catch(err){toast(err.message);}
},true);

document.addEventListener('change',e=>{
 if(e.target.id!=='credit-crop')return;
 const crop=e.target.value,schemes=calculationSettings().schemes.filter(s=>s.crop===crop&&s.benefits.includes('ABS'));
 $('#credit-scheme').innerHTML=schemes.map(s=>option(s.id,s.name,'')).join('');
});
