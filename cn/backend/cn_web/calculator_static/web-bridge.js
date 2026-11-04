'use strict';
// Keep the Update35.2 renderers and event handlers. This file adapts transport,
// ownership and canonical source actions; it does not replace calculator pages.
let nativeStale=null,nativePendingImport=null,workbookMappingReturn=false;
const nativeTransport=api;
const nativeRoutes={state:'native-state',import:'native-import','bulk-import':'native-bulk-import','audit-import':'native-audit-import','audit-check':'native-audit-check','audit-review':'native-audit-review','audit-map':'native-audit-map','audit-bulk-nrv':'native-audit-bulk-nrv','year-match':'native-year-match','year-pair':'native-year-pair','year-link-save':'native-year-link-save','bulk-document':'native-bulk-document',backup:'native-backup',restore:'native-restore','project-export':'native-project-export','project-import':'native-project-import',reparse:'native-reparse','late-ipt-review':'native-late-ipt-review'};
api=async(path,data,background=false)=>{
 const name=path.replace('/api/','');
 if(['audit-review','audit-map'].includes(name))data={...data,documents:auditDocuments};
 if(name==='calculate'&&nativeStale&&nativeStale.id===record?.id)return nativeTransport('/api/native-stale-result',{id:record.id},background);
 if(['import','reparse'].includes(name))data={...(name==='reparse'?{record_id:record.id}:data),season:state.selected_period||record?.season||state.settings.seasons[0]?.name};
 if(name==='backup')data={};
 if(name==='workbook-print'&&background)path='/api/workbook-review';
 else if(nativeRoutes[name])path='/api/'+nativeRoutes[name];
 return nativeTransport(path,data,background);
};
const nativeSaveDraft=saveDraft;
let lastSavedDraft=null;
saveDraft=async()=>{
 if(nativeStale&&nativeStale.id===record?.id)return;
 await saveQueue;
 const fingerprint=JSON.stringify([activeProject,activeWorkbook,record]);
 if(fingerprint===lastSavedDraft)return;
 const savingEpoch=editEpoch;
 const pending=nativeSaveDraft();
 // Report this failure to its caller, but let a corrected draft retry on the
 // next action instead of leaving every await saveQueue permanently rejected.
 saveQueue=pending.catch(()=>{});
 await pending;lastSavedDraft=savingEpoch===editEpoch?JSON.stringify([activeProject,activeWorkbook,record]):null;
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
 if(data.native_record){await nativeAdopt(data.native_record);cnOpenImportSetup();toast('Imported as draft. Map products, review source rates, then configure schemes.');return;}
 if(data.native_import_review){
  nativePendingImport=data;const rows=data.preview.results.filter(r=>r.candidates.length),row=rows[0];
  modal('<h2>Repeat import review</h2><p>Already-imported vouchers remain saved. Review changed/new entries before replacing this statement. Completed history is retained.</p>'+Object.entries(row.comparison||{}).map(([label,count])=>'<p>'+esc(label)+': '+count+'</p>').join('')+'<label>Existing statement<select id="native-replacement">'+row.candidates.map(id=>option(id,row.party+' · '+id.slice(0,6),row.candidates[0])).join('')+'</select></label><label>Review note<input id="native-import-reason" placeholder="Reason for accepting the changed statement"></label><button id="native-commit-import" class="primary">Apply reviewed statement</button>');return;
 }
 return nativeMergeImport(data);
};
openRecord=async id=>{
 workbookMappingReturn=false;
 clearTimeout(saveTimer);await saveQueue;await saveDraft();
 if(id.startsWith('source:')){const source=state.records.find(r=>r.id===id);return nativeAdopt(await nativeTransport('/api/native-open',{ledger_id:id.slice(7),season:state.selected_period||source?.season||state.settings.seasons[0]?.name}));}
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
   (allowed?`<section class="card"><h2>Create your first workbook</h2><p>A workbook holds statements, products, schemes and parties. Choose calculation dates later on Parties.</p><form id="first-workbook"><label>Workbook name<input name="name" required maxlength="100" placeholder="e.g. Gujarat Kharif 2026"></label><label>State<input name="state" required maxlength="100" placeholder="e.g. Gujarat"></label><button class="primary" type="submit">Create workbook &amp; open dashboard</button><p id="first-error" role="alert"></p></form></section>`:
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

// Offline acceptance update: import setup and explicit stock scope.
// Reuses existing stock exclusions and native per-season source drafts; no benefit formula changes.
const cnScopeReason='Working-period product selection: ';
let cnSetupReturn=false,cnScopeDraft=null,cnBulkRows=[];
function cnSourceRatesHTML(group){
 const values=new Map();let uncertain=false;
 for(const {entry,item} of group.items){if(entry.kind!=='sale'||item.exclude)continue;
  const rate=Number(item.rate),qty=Number(item.qty),amount=Number(item.amount);
  if(!(rate>0&&qty>0)||!Number.isFinite(amount)){uncertain=true;continue;}
  const key=String(item.rate)+' / '+item.unit;
  values.set(key,{rate:item.rate,unit:item.unit});
  if(Math.abs(rate*qty-amount)>.02)uncertain=true;
 }
 return [...values.values()].map(v=>esc(v.rate)+' / '+esc(v.unit)).join('<br>')+
  (uncertain?'<small class="warn">Check invoice amount / unit</small>':'')+
  (!values.size?'<small>No usable printed sale rate</small>':'')+
  (values.size>1?'<small>Mixed rates — choose explicitly in the scheme</small>':'');
}
function cnProductSetupHeader(){return '<section class="card"><h2>Products, mapping & billing rates</h2><p>Map the statement products first. Source rates below are evidence, not automatically approved scheme or audit rates. Keep kg / packet units distinct.</p><div class="actions"><button data-cn-action="setup">Open product setup</button><button data-cn-action="scope">Choose working period & CN products</button></div></section>';}
function cnOpenImportSetup(){
 if(!record)return;cnSetupReturn=true;
 modal(`<div class="cn-workflow-dialog"><h2>Imported products → mapping → schemes</h2><p>${esc(record.party)} · ${esc(record.season)}. First save each product mapping; then choose its Scheme / Group. The scheme builder uses the saved catalogue and offers matching source billing rates for review.</p><button data-cn-action="scope">Choose working period & CN products</button>${mappingSummary()}<div class="actions"><button data-cn-action="schemes">Open My Schemes</button><button data-cn-action="setup-done">Continue ledger review</button></div></div>`);
 if(record.status!=='draft')$('#dialogbody').querySelectorAll('input,select,button[data-edit]').forEach(x=>x.disabled=true);
}
const cnSaveMappingBeforeSetup=saveInlineMapping;
saveInlineMapping=async(...args)=>{const back=cnSetupReturn;const value=await cnSaveMappingBeforeSetup(...args);if(back)cnOpenImportSetup();return value;};
function cnScopeEntryIncluded(entry,r,period){
 if(!period?.confirmed||!period.start||!period.end)return true;
 if(entry.items?.length&&entry.items.every(i=>i._web_season_excluded))return false;
 const dt=(entry.original||entry).date,review=entry.web_review||{};
 if(review.season)return review.season===r.season&&dt>=period.start&&dt<=period.cutoff;
 if(dt>=period.start&&dt<=period.end)return true;
 const late=r.late_ipt_reviews?.[entry.id];
 if(late&&late.season===r.season&&['ipt_in','ipt_out'].includes(entry.kind))return dt>period.end&&dt<=period.cutoff;
 return false;
}
function cnScopeGroups(r=record,cfg=calculationSettings(),allDates=false){
 const period=cfg.seasons.find(s=>s.name===r.season),groups=new Map();
 for(const entry of r.entries||[]){
  if(!['sale','return','ipt_in','ipt_out'].includes(entry.kind))continue;
  if(!allDates&&!cnScopeEntryIncluded(entry,r,period))continue;
  for(const item of entry.items||[]){
   const product=cfg.products.find(p=>p.id===item.product),key=product?'product:'+product.id:JSON.stringify([item.name,item.unit]);
   if(!groups.has(key))groups.set(key,{key,name:product?.name||item.name,unit:item.unit,items:[],units:new Set()});
   const row=groups.get(key);row.items.push({entry,item});row.units.add(item.unit);row.unit=[...row.units].join(' / ');
  }
 }
 return [...groups.values()];
}
function cnPeriodOptions(){return state.settings.seasons.map(p=>option(p.name,p.name,record.season)).join('')+option('__new__','+ Add a new working period',record.season);}
function cnScopePanel(){
 const p=calculationSettings().seasons.find(s=>s.name===record.season),rows=cnScopeGroups(),active=rows.filter(g=>g.items.some(x=>!x.item.exclude));
 return `<section class="card cn-allocation-scope"><h2>Working period & CN products</h2><p><strong>${esc(record.season)}</strong> · ${date(p?.start)} to ${date(p?.end)} · Cutoff ${date(p?.cutoff)}</p><p>${active.length} of ${rows.length} statement product(s) included. Only selected-period, included stock earns CN. Full-year balances and original receipt dates remain available.</p><p>${active.map(g=>esc(g.name)+' ('+esc(g.unit)+')').join(', ')||'No products included — review period dates and mappings.'}</p><button data-cn-action="scope">${record.status==='draft'?'Choose / review period & products':'View period & products'}</button><p class="muted">A posted CN does not automatically close every benefit. Pending Kharif work stays in its own Kharif calculation; Rabi uses its own dates and quantities.</p></section>`;
}
const cnPaymentTabBeforeScope=paymentTab;
paymentTab=()=>cnScopePanel()+cnPaymentTabBeforeScope();
function cnOpenScope(){
 if(!record)return;cnSetupReturn=false;
 const p=calculationSettings().seasons.find(s=>s.name===record.season),rows=cnScopeGroups();
 cnScopeDraft={id:record.id,revision:record.revision,season:record.season,rows};
 modal(`<div class="cn-workflow-dialog"><h2>Choose working period & CN products</h2><p>Choose the sales / return period first, then select products. For the same product, Kharif and Rabi quantities are calculated separately. This does not change payment dates or erase the full-year ledger.</p><label>Working period<select id="cn-scope-period">${cnPeriodOptions()}</select></label><div id="cn-new-period" hidden><label>New period name<input id="cn-period-name" maxlength="100" placeholder="Rabi 2026–27"></label><div class="grid"><label>Sales / return start<input id="cn-period-start" type="date"></label><label>Sales / return end<input id="cn-period-end" type="date"></label><label>Calculation cutoff<input id="cn-period-cutoff" type="date"></label></div></div><p id="cn-period-current">Saved stock dates: ${date(p?.start)} to ${date(p?.end)}; cutoff ${date(p?.cutoff)}. To use different dates, add a new period.</p><button data-cn-action="period-apply">Open selected period</button><hr><h3>Products for ${esc(record.season)}</h3><p>Unchecked products receive no ABS, CD, quantity or other CN benefit in this calculation. Their ledger amounts remain in the statement. Existing manual exclusions stay excluded.</p><div class="actions"><button data-cn-action="products-all">Select all</button><button data-cn-action="products-none">Select none</button></div><div>${rows.map((g,i)=>`<label class="check"><input type="checkbox" data-cn-scope-product="${i}" ${g.items.some(x=>!x.item.exclude)?'checked':''}>${esc(g.name)} · ${esc(g.unit)}${g.items.some(x=>x.item.exclude&&!String(x.item.review_reason||'').startsWith(cnScopeReason))?' (has manual exclusions)':''}</label>`).join('')||'<p>No stock products in this saved period. Choose or add the correct dates first.</p>'}</div><p class="warn">Save the product selection before allocating money. To change products after allocating, first remove the existing benefit allocations / cash splits; saved amounts are never silently moved.</p><button data-cn-action="products-save" class="primary">Save CN products & open allocation</button><p id="cn-scope-error" role="alert"></p></div>`);
 const readOnly=record.status!=='draft';
 if(readOnly||!state.permissions?.includes('edit_ledger'))$('#dialogbody').querySelectorAll('input,select,button').forEach(n=>n.disabled=true);
}
async function cnApplyPeriod(){
 if(!cnScopeDraft||record.id!==cnScopeDraft.id)throw Error('Party changed. Reopen this selection.');
 const name=$('#cn-scope-period').value;
 if(name===record.season)return;
 if(!record.web_source)throw Error('This period switch requires a saved imported statement. Use a separate reviewed calculation for a manual ledger.');
 clearTimeout(saveTimer);await saveQueue;await saveDraft();
 let chosen=name;
 if(name==='__new__'){
  chosen=$('#cn-period-name').value.trim();const start=$('#cn-period-start').value,end=$('#cn-period-end').value,cutoff=$('#cn-period-cutoff').value;
  if(!chosen||!start||!end||!cutoff||start>end||end>cutoff)throw Error('Enter a period name and valid start ≤ end ≤ cutoff dates.');
  if(state.settings.seasons.some(s=>s.name.toLocaleLowerCase()===chosen.toLocaleLowerCase()))throw Error('That period name is already saved. Choose it from the list.');
  const cfg=structuredClone(state.settings);cfg.seasons.push({name:chosen,start,end,cutoff,confirmed:true});
  await api('/api/settings',cfg);await refresh();
 }
 const next=await nativeTransport('/api/native-open',{ledger_id:record.web_source.ledger_id,season:chosen});
 await nativeAdopt(next,1);cnOpenScope();
 toast('Opened '+chosen+'. Earlier season work and allocations remain in their own calculation.');
}
async function cnSaveScopeProducts(){
 const view=cnScopeDraft;
 if(!view||record.id!==view.id||record.revision!==view.revision||record.season!==view.season)throw Error('Calculation changed. Reopen the product selection.');
 if($('#cn-scope-period').value!==record.season)throw Error('Open the selected period before choosing its products.');
 const selected=new Set([...document.querySelectorAll('[data-cn-scope-product]:checked')].map(n=>Number(n.dataset.cnScopeProduct)));
 if(view.rows.length&&!selected.size)throw Error('Select at least one product for this CN calculation.');
 const next=structuredClone(record);const rows=cnScopeGroups(next,calculationSettings());let changedScope=false;
 rows.forEach((g,i)=>{for(const {item} of g.items){
  if(!selected.has(i)&&!item.exclude){item.exclude=true;item.review_reason=cnScopeReason+record.season;changedScope=true;}
  else if(selected.has(i)&&item.exclude&&String(item.review_reason||'').startsWith(cnScopeReason)){item.exclude=false;delete item.review_reason;changedScope=true;}
 }});
 if(changedScope&&(record.allocations.some(a=>a.type!=='Settlement')||(record.cash_splits||[]).length))throw Error('Remove existing benefit allocations and cash quantity splits before changing the product scope. Your saved splits have not changed.');
 clearTimeout(saveTimer);await saveQueue;
 if(changedScope){next.ledger_confirmed=false;const saved=await nativeTransport('/api/save',next);await nativeAdopt(saved,2);}
 else {$('#modal').close();step=2;page='Calculate CN';render();}
 cnScopeDraft=null;toast('CN products confirmed for '+record.season+'.');
}
function cnBulkProductList(){
 const groups=new Map();
 for(const r of state.records||[]){if(r.deleted_at||r.status!=='draft'||!r.web_source)continue;
  const cfg=state.settings;
  for(const g of cnScopeGroups(r,cfg,true)){
   const key=JSON.stringify([g.name,g.unit,g.items[0]?.item?.packing_kg||'']);
   if(!groups.has(key))groups.set(key,{...g,recordId:r.id,ledgerId:r.web_source.ledger_id,season:r.season,parties:new Set([partyKey(r)])});
   else {const row=groups.get(key);row.items.push(...g.items);row.parties.add(partyKey(r));}
  }
 }
 cnBulkRows=[...groups.values()];
 return `<section class="card"><h2>Imported products — map before building schemes</h2><p>Workbook list grouped by distinct statement product and packing across all dates and parties. Map products and review printed rates before choosing them in a scheme. Save a product mapping once to apply it to matching names, units and packing across this workbook. Finalised calculations retain their saved history.</p><div class="tablewrap"><table><tr><th>Statement product</th><th>Working period</th><th>Source billing rates</th><th>Parties</th><th>Action</th></tr>${cnBulkRows.map((g,i)=>`<tr><td>${esc(g.name)} · ${esc(g.unit)}</td><td>${esc(g.season)}</td><td>${cnSourceRatesHTML(g)}</td><td>${g.parties.size}</td><td>${g.items.every(x=>state.settings.products.some(p=>p.id===x.item.product)&&x.item.mapping_confirmed!==false)?'<strong class="ok">✓ Mapped</strong>':'<strong class="warn">Needs mapping</strong>'}<button data-cn-bulk-product="${i}">Map / configure scheme</button></td></tr>`).join('')}</table></div></section>`;
}
const cnBulkPageBeforeSetup=bulkPage;
bulkPage=()=>{cnBulkPageBeforeSetup();if(state.selected_period&&$('#bulk-season'))$('#bulk-season').value=state.selected_period;if(activeWorkbook!=='legacy')$('#main').insertAdjacentHTML('beforeend',cnBulkProductList());};
document.addEventListener('change',e=>{
 if(e.target.id==='cn-scope-period'){
  $('#cn-new-period').hidden=e.target.value!=='__new__';
  const p=state.settings.seasons.find(s=>s.name===e.target.value);
  $('#cn-period-current').textContent=p?'Saved stock dates: '+date(p.start)+' to '+date(p.end)+'; cutoff '+date(p.cutoff)+'. Open this period to load its products.':'Enter the new dates, then open this period.';
 }
});
document.addEventListener('click',async e=>{
 const b=e.target.closest('button');if(!b)return;
 if(!b.dataset.cnAction&&!b.hasAttribute('data-cn-bulk-product'))return;
 try{
  b.disabled=true;
  if(b.hasAttribute('data-cn-bulk-product')){await openWorkbookProduct(Number(b.dataset.cnBulkProduct));return;}
  const action=b.dataset.cnAction;
  if(action==='setup')cnOpenImportSetup();
  else if(action==='scope')cnOpenScope();
  else if(action==='setup-done'){cnSetupReturn=false;$('#modal').close();step=1;render();}
  else if(action==='schemes'){
   if(mappingGroups().some(g=>g.items.some(x=>!state.settings.products.some(p=>p.id===x.item.product))))throw Error('Save product mappings first, then choose the mapped products in a scheme.');
   cnSetupReturn=false;$('#modal').close();settingDraft=structuredClone(state.settings);settingsSection='schemes';page='Settings';settingsPage();
  }else if(action==='period-apply')await cnApplyPeriod();
  else if(action==='products-save')await cnSaveScopeProducts();
  else if(action==='products-all'||action==='products-none')document.querySelectorAll('[data-cn-scope-product]').forEach(n=>n.checked=action==='products-all');
 }catch(err){const box=$('#cn-scope-error');if(box)box.textContent=err.message;else toast(err.message);}
 finally{b.disabled=false;}
});
const cnCommitMappingBeforeSetup=commitInlineMapping;
commitInlineMapping=async()=>{const back=cnSetupReturn;await cnCommitMappingBeforeSetup();if(workbookMappingReturn){page='Parties';render();modal('<h2>Workbook Product Mapping</h2>'+cnBulkProductList());}else if(back)cnOpenImportSetup();};

const periodPartiesPage=partiesPage;
partiesPage=()=>{periodPartiesPage();$('#main').insertAdjacentHTML('afterbegin',`<section class="card"><h2>Workbook controls</h2><p>Product Mapping applies across parties and later imports. Calculation Period applies when opening a party; earlier drafts and issued history remain saved.</p><button id="workbook-product-mapping">Product Mapping</button><button id="workbook-period">Calculation Period</button><strong> ${esc(state.selected_period||'Choose calculation dates')}</strong></section>`);};
const periodOpenRecord=openRecord;
openRecord=async id=>{const useWorkbookPeriod=page==='Parties'&&!$('#modal')?.open;await periodOpenRecord(id);if(useWorkbookPeriod&&state.selected_period&&record?.web_source&&record.season!==state.selected_period)await nativeAdopt(await nativeTransport('/api/native-open',{ledger_id:record.web_source.ledger_id,season:state.selected_period}),1);};
function workbookPeriodDialog(){modal(`<h2>Workbook Calculation Period</h2><label>Saved period<select id="workbook-period-select">${state.settings.seasons.filter(p=>p.confirmed).map(p=>option(p.name,p.name,state.selected_period)).join('')}${option('__new__','+ New calculation period','')}</select></label><p>For a new period enter all four fields. Overlapping views are allowed; receipts cannot be allocated twice.</p><label>Name<input id="workbook-period-name"></label><label>From<input id="workbook-period-start" type="date"></label><label>To<input id="workbook-period-end" type="date"></label><label>Cutoff<input id="workbook-period-cutoff" type="date"></label><button id="workbook-period-save">Save workbook period</button>`);}
const periodLedgerTab=ledgerTab;
ledgerTab=()=>{const p=result?.period_accounting;const base=periodLedgerTab();if(!p)return base;return `<section class="card"><h2>Calculation period accounting</h2><p>${date(p.start)} to ${date(p.end)} · Opening ${money(p.opening)} · Closing ${money(p.closing)}</p><table><tr><th>Activity</th><th>Debit</th><th>Credit</th></tr>${Object.entries(p.totals).map(([k,v])=>`<tr><td>${esc(k)}</td><td>${money(v.debit)}</td><td>${money(v.credit)}</td></tr>`).join('')}</table><details><summary>Selected-period transactions</summary>${record.entries.filter(e=>p.entry_ids.includes(e.id)).map(e=>`<p>${date(e.date)} · ${esc(e.reference)} · ${esc(e.kind)} · ${money(e.debit)} / ${money(e.credit)}</p>`).join('')}</details></section>`+base;};
const periodBenefitTab=benefitTab;
benefitTab=()=>periodBenefitTab()+`<section class="card"><h2>Already-given CN</h2><p>Choose crop, season and amount for an actual posted CN. It reduces that entitlement once. Freight and material returns stay separate.</p>${record.entries.filter(e=>e.kind==='posted_cn').map(e=>{const a=record.posted_cn_assignments?.[e.id]||{};return `<div><strong>${date(e.date)} · ${esc(e.reference)} · ${money(e.credit)}</strong><label>Crop<select data-given-cn="${esc(e.id)}" data-given-key="crop">${option('','Separate / not benefit CN',a.crop||'')}${[...new Set(state.settings.products.map(p=>p.crop))].map(c=>option(c,c,a.crop)).join('')}</select></label><label>Season<select data-given-cn="${esc(e.id)}" data-given-key="season">${state.settings.seasons.map(p=>option(p.name,p.name,a.season||record.season)).join('')}</select></label><label>Amount<input type="number" min="0" max="${esc(e.credit)}" data-given-cn="${esc(e.id)}" data-given-key="amount" value="${esc(a.amount||e.credit)}"></label><label>Relation to this app's issued history<select data-given-cn="${esc(e.id)}" data-given-key="history_relation">${option('','Choose if issued history exists',a.history_relation||'')}${option('same_issued','Same app-issued CN now entered in Tally',a.history_relation||'')}${option('separate','Separate CN given outside this app',a.history_relation||'')}</select></label></div>`;}).join('')}</section>`;
document.addEventListener('change',async e=>{const t=e.target;if(!t.dataset.givenCn)return;try{const id=t.dataset.givenCn;record.posted_cn_assignments||={};const entry=record.entries.find(e=>e.id===id);const a=record.posted_cn_assignments[id]||{crop:'',season:record.season,amount:entry.credit};a[t.dataset.givenKey]=t.value;if(a.crop)record.posted_cn_assignments[id]=a;else delete record.posted_cn_assignments[id];if(record.web_source){const saved=await nativeTransport('/api/native-given-cn',{id:record.id,revision:record.revision,entry:id,value:a.crop?a:null});await nativeAdopt(saved,3);}else{await saveDraft();await calculate();render();}}catch(err){toast(err.message);}});
document.addEventListener('click',async e=>{const t=e.target.closest('button');if(!t)return;try{
 if(t.id==='workbook-product-mapping'){workbookMappingReturn=true;modal('<h2>Workbook Product Mapping</h2>'+cnBulkProductList());return;}
 if(t.id==='workbook-period'){workbookPeriodDialog();return;}
 if(t.id==='workbook-period-save'){
  let chosen=$('#workbook-period-select').value;const name=$('#workbook-period-name').value.trim();
  if(name){const start=$('#workbook-period-start').value,end=$('#workbook-period-end').value,cutoff=$('#workbook-period-cutoff').value;if(!start||start>end||end>cutoff)throw Error('Choose valid start, end and cutoff dates');chosen=name;const cfg=structuredClone(state.settings);if(cfg.seasons.some(p=>p.name===name))throw Error('That period name already exists');cfg.seasons.push({name,start,end,cutoff,confirmed:true});await nativeTransport('/api/settings',cfg);}
  if(!chosen||chosen==='__new__')throw Error('Choose or add a calculation period');
  await nativeTransport('/api/native-workbook-period',{season:chosen});$('#modal').close();await refresh();partiesPage();toast('Workbook calculation period saved');
 }
}catch(err){toast(err.message);}});

const periodSettlementLedgerTab=ledgerTab;
ledgerTab=()=>periodSettlementLedgerTab()+(record.web_source?`<details class="card"><summary>Receipt settlement references</summary><p>Use an explicit invoice reference only when supported by the statement. Otherwise old outstanding clears first.</p>${record.entries.filter(e=>e.kind==='receipt').map(e=>`<label>${date(e.date)} · ${esc(e.reference)}<select data-settlement-receipt="${esc(e.id)}">${option('','Oldest outstanding first',e.settlement_reference||'')}${record.entries.filter(i=>i.kind==='sale'&&i.date<=e.date).map(i=>option(i.reference,i.reference,e.settlement_reference||'')).join('')}</select></label>`).join('')}</details>`:'');
document.addEventListener('change',async e=>{const t=e.target;if(!t.dataset.settlementReceipt)return;try{const saved=await nativeTransport('/api/native-settlement-reference',{id:record.id,revision:record.revision,entry:t.dataset.settlementReceipt,value:t.value});await nativeAdopt(saved,1);}catch(err){toast(err.message);}});

const periodOpeningDuesPanel=openingDuesPanel;
openingDuesPanel=()=>{const p=result?.period_accounting;if(!p)return periodOpeningDuesPanel();return `<section class="opening-dues-panel"><h3>Period opening ${money(p.opening)}</h3><p>Derived from all earlier transactions. Outstanding clears chronologically before benefit allocation; reviewed invoice references take precedence.</p><strong>Earlier outstanding remaining: ${money(result.old_dues_remaining)}</strong></section>`;};
const periodFinalLedgerTab=ledgerTab;
ledgerTab=()=>{const html=periodFinalLedgerTab();return result?.period_accounting?html.replace(field('Confirmed old outstanding to clear','old_dues',record.old_dues,'number'),'<p>Outstanding clearance is derived automatically for the selected calculation period.</p>'):html;};

// Preserved printed allocation evidence; displayed separately from voucher dates.
const splitEvidenceLedgerTab=ledgerTab;
ledgerTab=()=>{const html=splitEvidenceLedgerTab(),p=result?.period_accounting;if(!p)return html;return html+`<section class="card"><h3>Printed bill allocations</h3>${(p.warnings||[]).map(w=>`<p>${esc(w)}</p>`).join('')}<details><summary>Settlement evidence (${(p.settlements||[]).length})</summary><table><tr><th>Posting date</th><th>Reference</th><th>Bill date</th><th>Printed amount</th><th>Applied amount</th><th>Applied to</th></tr>${(p.settlements||[]).map(s=>`<tr><td>${date(s.posting_date)}</td><td>${esc(s.reference)}</td><td>${s.date?date(s.date):'—'}</td><td>${money(s.amount)}</td><td>${money(s.applied_amount)}</td><td>${esc(s.destination)}</td></tr>`).join('')}</table></details></section>`;};

// Period credit and carried receipts are separate sources; never count dated advances twice.
const periodCreditAvailableBefore=openingCreditAvailable;
openingCreditAvailable=()=>{const p=result?.period_accounting;if(!p)return periodCreditAvailableBefore();return String(Math.max(0,Number(p.untraced_opening_remaining||0)-allocationTotal(record.opening_sources||[])));};
const periodCreditPanelBefore=openingCreditPanel;
openingCreditPanel=()=>{const p=result?.period_accounting;if(!p)return periodCreditPanelBefore();const credit=Math.max(0,-Number(p.opening)),free=Number(openingCreditAvailable());return `<section class="card"><h3>Credit at selected period start · ${date(p.start)}</h3><p>Selected-period opening credit: <strong>${money(credit)}</strong>. Original statement opening: ${money(record.opening)}.</p><p>Unregistered carried credit available: <strong>${money(free)}</strong>. Earlier unused dated receipts are listed separately with their original dates. Credit already consumed by later transactions or protected receipts is excluded from this amount.</p>${free>0?'<button data-action="opening-source" data-edit>Allocate available carried credit</button>':''}</section>`;};
const periodPaymentTabBefore=paymentTab;
paymentTab=()=>{const p=result?.period_accounting;if(!p)return periodPaymentTabBefore();const all=result.sources;try{result.sources=all.filter(s=>Number(s.available)>0||record.allocations.some(a=>a.source===s.id));return `<p class="muted">Working period ${date(p.start)}–${date(p.end)}. Earlier unused advances retain original dates and must satisfy the scheme booking windows. Fully consumed receipts are hidden from this allocation view.</p>`+periodPaymentTabBefore();}finally{result.sources=all;}};
// Suggest billing in the printed unit across the workbook, including schemes created after mapping.
const workbookSourceRatesBefore=sourceSaleRates;
sourceSaleRates=(pid,target,packing)=>{const rates=new Set();for(const r of [...(state.records||[]),record].filter(Boolean)){if(r.deleted_at)continue;for(const e of r.entries||[]){if(e.kind!=='sale')continue;for(const i of e.items||[]){if(i.product!==pid||!['packet','kg'].includes(i.unit))continue;const n=Number(i.rate),q=Number(i.qty),amount=Number(i.amount);if(!(n>0&&q>0)||Math.abs(n*q-amount)>.02)continue;const rate=i.unit===target?n:i.unit==='packet'?n/Number(packing):n*Number(packing);if(Number.isFinite(rate))rates.add(String(Number(rate.toFixed(8))));}}}return [...rates].sort((a,b)=>Number(a)-Number(b));};
const workbookCreateProductSchemeBefore=createProductScheme;
createProductScheme=pid=>{workbookCreateProductSchemeBefore(pid);const product=settingDraft.products.find(p=>p.id===pid),units=new Set();for(const r of [...(state.records||[]),record].filter(Boolean))for(const e of r.entries||[])if(e.kind==='sale')for(const i of e.items||[])if(i.product===pid&&['kg','packet'].includes(i.unit))units.add(i.unit);if(units.size===1)builder.billing_unit=[...units][0];const rates=sourceSaleRates(pid,builder.billing_unit,product.packing_kg);builder.pdf_rate_options=rates;builder.pdf_rate_unit=builder.billing_unit;if(rates.length===1){builder.billing=rates[0];builder.pdf_rate_note='Prefilled from workbook statement sales in the printed billing unit; verify before confirming';}else if(rates.length>1){builder.billing=null;builder.pdf_rate_note='Mixed statement sales rates: choose explicitly';}builderForm();};

let workbookProductDraft=null;
async function openWorkbookProduct(index){
 clearTimeout(saveTimer);await saveQueue;if(record?.status==='draft'&&record.id&&!nativeStale)await saveDraft();
 const row=cnBulkRows[index];if(!row)throw Error('Reopen the mapping list.');
 const first=row.items[0];
 const request={ledger_id:row.ledgerId,entry_id:first.entry.id,item_index:first.entry.items.indexOf(first.item)};
 const context=await nativeTransport('/api/native-workbook-map-context',request);
 workbookProductDraft={request,evidence:context.evidence};const item=context.item,p=state.settings.products.find(p=>p.id===item.product);
 modal(`<h2>Map workbook product</h2><p>${esc(item.name)} · ${esc(item.unit)} · Applies across parties</p><label>Saved crop<select id="wm-crop">${option('','Choose crop',p?.crop||'')}${context.crops.map(c=>option(c,c,p?.crop||'')).join('')}</select></label><label>Or new crop<input id="wm-new-crop"></label><label>Product name<input id="wm-name" value="${esc(p?.name||item.name)}"></label><label>kg per packet<input id="wm-pack" type="number" value="${esc(p?.packing_kg||item.packing_kg||item.mapping_suggestion?.detected_packing_kg||sourcePacking(item.name))}"></label><button id="wm-save" class="primary">Save workbook mapping</button><button id="wm-back">Back to mapping list</button>`);
}
document.addEventListener('click',async e=>{const b=e.target.closest('button');if(!b||!['wm-save','wm-back'].includes(b.id))return;try{b.disabled=true;if(b.id==='wm-save'){const d=workbookProductDraft;if(!d)throw Error('Reopen product mapping');await nativeTransport('/api/native-workbook-map',{...d.request,evidence:d.evidence,crop:$('#wm-new-crop').value.trim()||$('#wm-crop').value,name:$('#wm-name').value.trim(),packing:$('#wm-pack').value});await refresh();toast('Workbook mapping saved');}workbookProductDraft=null;modal('<h2>Workbook Product Mapping</h2>'+cnBulkProductList());}catch(err){toast(err.message);}finally{b.disabled=false;}});
const allocationProductPanelBefore=paymentTab;
paymentTab=()=>{const sold=soldProductIds(),cfg=calculationSettings();const rows=cfg.products.filter(p=>sold.has(p.id));return `<section class="card"><h3>Selected-period products & schemes</h3><p>Each product with positive net quantity in this period appears here. Choose its scheme to place it in the applicable payment branches.</p>${rows.map(p=>{const sid=record.scheme_overrides?.[p.scheme]||p.scheme,sc=cfg.schemes.find(s=>s.id===sid),ready=sc&&!sc.deleted_at&&!sc.mapping_placeholder&&sc.season===record.season&&!p.needs_assignment;return `<p><strong>${esc(p.crop)} / ${esc(p.name)}</strong> · ${ready?esc(sc.name)+' · '+esc(sc.benefits.join(', ')||'No payment benefits enabled'):'Scheme selection needed'} <button data-product-scheme="${esc(p.id)}" data-edit>Choose Scheme / Group</button></p>`;}).join('')||'<p>No positive net product quantity in this period. Review stock dates, returns and mappings.</p>'}</section>`+allocationProductPanelBefore();};
// Reuse read-only derived settings/stock within one synchronous paint only.
// Every subsequent render/action starts fresh after settings or record changes.
let paintDerivations=null;
const paintSettingsBefore=calculationSettings,paintSoldBefore=soldProductIds;
calculationSettings=()=>paintDerivations?(paintDerivations.settings||=(paintSettingsBefore())):paintSettingsBefore();
soldProductIds=()=>paintDerivations?(paintDerivations.sold||=(paintSoldBefore())):paintSoldBefore();
const paintRenderBefore=render;
render=()=>{const previous=paintDerivations;paintDerivations={};try{return paintRenderBefore();}finally{paintDerivations=previous;}};
function accountingReviewPanel(){
 const p=result?.period_accounting;if(!p?.review_items?.length)return '';
 return `<section class="card ${p.review_required?'warn':'ok'}"><h3>Accounting evidence review ${p.review_required?'required':'recorded'}</h3><ul>${p.review_items.map(i=>`<li>${esc(i.message)}</li>`).join('')}</ul>${p.review_required?'<p>Finalising is blocked until the bill allocation and same-day voucher order are verified.</p>':`<p>Reviewed: ${esc(p.accounting_review?.reason||'')}</p>`}${record.status==='draft'&&record.web_source?'<button id="accounting-review-open" data-edit>Review allocations / same-day order</button>':''}</section>`;
}
const evidenceLedgerBefore=ledgerTab,evidencePaymentBefore=paymentTab;
ledgerTab=()=>accountingReviewPanel()+evidenceLedgerBefore();
paymentTab=()=>accountingReviewPanel()+evidencePaymentBefore();
let accountingReviewDialog=null;
document.addEventListener('click',async e=>{
 const b=e.target.closest('button');if(!b||!['accounting-review-open','accounting-review-save'].includes(b.id))return;
 try{
  b.disabled=true;
  if(b.id==='accounting-review-open'){
   clearTimeout(saveTimer);await saveQueue;await saveDraft();await calculate();
   const p=result.period_accounting;accountingReviewDialog={id:record.id,revision:record.revision,evidence:p.review_evidence};
   const dates=[...new Set(p.review_items.filter(i=>i.kind==='same_day_order').map(i=>i.date))];
   modal(`<h2>Verify accounting evidence</h2><p>Check these vouchers against the original statement/Tally. Confirm fallback only if it matches the actual allocation. Otherwise correct the receipt reference/source first. Dates are never changed.</p><ul>${p.review_items.map(i=>`<li>${esc(i.message)}</li>`).join('')}</ul>${dates.map(dt=>`<section><strong>${date(dt)}</strong><p>${record.entries.filter(e=>(e.original||e).date===dt&&['receipt','posted_cn'].includes(e.kind)).map(e=>esc(e.reference)+' · '+esc(e.kind)+' · '+money(e.credit)).join('<br>')}</p><label>Verified order<select data-accounting-order="${esc(dt)}">${option('','Choose after checking','')}${option('source','As printed in this statement','')}${option('cn_first','CN before receipt','')}${option('receipt_first','Receipt before CN','')}</select></label></section>`).join('')}<label>Evidence / reason<textarea id="accounting-review-reason" minlength="12" placeholder="What did you verify in the original books?"></textarea></label><p>Only this saved period and these unchanged vouchers are covered. A source/reference change requires review again. Incompatible saved allocations are rejected, never silently changed.</p><button id="accounting-review-save" class="primary">Save verified review</button>`);
  }else{
   const d=accountingReviewDialog;if(!d||record.id!==d.id||record.revision!==d.revision)throw Error('Calculation changed; reopen review');
   const same_day_order=Object.fromEntries([...document.querySelectorAll('[data-accounting-order]')].map(t=>[t.dataset.accountingOrder,t.value]));
   const saved=await nativeTransport('/api/native-accounting-review',{...d,reason:$('#accounting-review-reason').value,same_day_order});
   accountingReviewDialog=null;await nativeAdopt(saved,1);toast('Accounting review saved; dates and existing allocations preserved');
  }
 }catch(err){toast(err.message);}finally{b.disabled=false;}
});
