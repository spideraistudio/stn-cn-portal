/* Update34: receipt-first allocation controls; all financial checks remain server-owned. */
let paymentWorkbench={scope:'',source:'',clear:null};
let segmentCD=null,unusedCD=null;
function paymentEntryScope(){return JSON.stringify([activeProject,activeWorkbook,record?.id||record?.party||'']);}
function paymentEntrySource(){
 if(!record||!result)return '';
 const scope=paymentEntryScope();
 if(paymentWorkbench.scope!==scope){paymentWorkbench={scope,source:'',clear:null};}
 if(!result.sources.some(s=>s.id===paymentWorkbench.source))paymentWorkbench.source=result.sources.find(s=>Number(exactDifference(s.available,record.allocations.filter(a=>a.source===s.id).map(a=>a.amount||0)))>0)?.id||result.sources[0]?.id||'';
 return paymentWorkbench.source;
}
function selectPaymentEntry(id){
 if(!result.sources.some(s=>s.id===id))throw Error('This payment source is unavailable. Reopen the party.');
 paymentEntrySource();paymentWorkbench.source=id;paymentSelectedId='';allocationPanelCollapsed=true;render();
}
function paymentEntriesHTML(){
 paymentEntrySource();const active=record.allocations.find(a=>a.id===paymentSelectedId);if(active&&result.sources.some(s=>s.id===active.source))paymentWorkbench.source=active.source;
 const source=paymentEntrySource(),selected=result.sources.find(s=>s.id===source),cfg=calculationSettings(),frozen=record.status!=='draft';
 const rows=record.allocations.map((a,i)=>({a,i})).filter(({a})=>a.source===source);
 const picked=rows.find(({a})=>a.id===paymentSelectedId);
 const assigned=allocationTotal(rows.map(x=>x.a)),remaining=selected?exactDifference(selected.available,[assigned]):'0';
 const absent=record.allocations.filter(a=>!result.sources.some(s=>s.id===a.source));
 return `<section class="card payment-workbench" id="payment-workbench"><div class="section-heading"><div><span class="eyebrow">WORK PAYMENT BY PAYMENT</span><h2>Payment entries & allocations</h2></div><button data-clear-allocations="all" class="danger" ${frozen||!record.allocations.length&&!record.cash_splits.length?'disabled':''}>Clear all party allocations…</button></div><div class="payment-workbench-grid"><div class="payment-entry-list" aria-label="Payment entries">${result.sources.map(s=>{const total=allocationTotal(record.allocations.filter(a=>a.source===s.id)),left=exactDifference(s.available,[total]);return `<button class="payment-entry ${s.id===source?'active':''}" data-payment-entry="${esc(s.id)}" aria-pressed="${s.id===source}"><strong>${esc(sourceLabel(s.id))}</strong><span>${s.date?date(s.date):'Undated opening credit'}</span><b>${money(s.amount)}</b><small>Remaining ${money(left)} · ${record.allocations.filter(a=>a.source===s.id).length} split(s)</small>${Number(sourceCDUnused(s.id))>=.01?`<small class="unused-funding">Unused CD ${money(sourceCDUnused(s.id))} still allocated</small>`:''}</button>`;}).join('')||'<p>No registered payment sources. Add a receipt or register opening credit below.</p>'}</div><div class="payment-entry-detail">${selected?`<h3>${esc(sourceLabel(source))} · ${selected.date?date(selected.date):'Undated opening credit'}</h3><div class="payment-entry-metrics">${[['Received',selected.amount],['Old dues cleared',selected.old_dues_cleared],['Available after dues',selected.available],['Allocated',assigned],['Remaining',remaining]].map(([label,value])=>`<div><small>${label}</small><strong>${money(value)}</strong></div>`).join('')}</div><div class="actions"><button data-entry-add class="primary" ${frozen?'disabled':''}>Add allocation for this payment</button><button data-clear-allocations="source" data-clear-target="${esc(source)}" ${frozen||!rows.length?'disabled':''}>Clear this payment’s allocations…</button></div><div class="tablewrap"><table class="payment-entry-splits"><thead><tr><th>Type / destination</th><th>Allocated</th><th>Used / unused</th><th>Actions</th></tr></thead><tbody>${rows.map(({a,i})=>`<tr class="${a.id===paymentSelectedId?'payment-row-selected':''}"><td><strong>${esc(allocationTypeLabel(a.type))} · ${esc(cfg.schemes.find(s=>s.id===a.scheme)?.name||a.scheme||'Choose scheme')}</strong><small class="cell-note">${esc(cfg.products.find(p=>p.id===a.product)?.name||'Scheme pool')}</small></td><td>${money(a.amount)}</td><td>${paymentFundingStatus(a)}</td><td><button data-entry-edit="${esc(a.id)}" ${frozen?'disabled':''}>Edit</button><button data-clear-allocations="row" data-clear-target="${esc(a.id)}" ${frozen?'disabled':''}>Remove…</button></td></tr>`).join('')||'<tr><td colspan="4">No allocations for this payment yet.</td></tr>'}</tbody></table></div>${picked&&picked.a.type!=='Cash'?`<section class="allocation-editor payment-inline-editor"><div class="section-heading"><h3>Edit selected split</h3><button data-entry-done>Done</button></div><div class="allocation-editor-fields"><table><tbody>${allocationRow(picked.a,picked.i)}</tbody></table></div></section>`:''}`:'<p>Select a payment to work on its allocations.</p>'}</div></div>${segmentAllocationButtons()}${absent.length?`<details><summary>Saved allocations with missing payment sources · ${absent.length}</summary>${absent.map(a=>`<p>${esc(a.type)} · ${esc(a.source)} · ${money(a.amount)} <button data-clear-allocations="row" data-clear-target="${esc(a.id)}" ${frozen?'disabled':''}>Remove…</button></p>`).join('')}</details>`:''}<p class="muted">The graphic below shows all party allocations. Highlighted destinations have allocations from the selected payment. Unused direct CD funding is shown above. Release it, then allocate the same receipt to another segment. ABS excess follows its existing first-CD-slab rule.</p></section>`;
}
function newPaymentAllocation(){
 const source=paymentEntrySource();if(!source)throw Error('Select a registered payment first.');
 modal(`<h2>Add allocation · ${esc(sourceLabel(source))}</h2><p>${date(result.sources.find(s=>s.id===source)?.date)} · Select the destination. Amounts are entered explicitly.</p><div class="grid two"><label>Allocation type<select id="entry-add-type">${['ABS','CD','Net','Cash','Settlement'].map(t=>option(t,allocationTypeLabel(t),'CD')).join('')}</select></label><label>Scheme<select id="entry-add-scheme"></select></label><label id="entry-add-product-label">Product<select id="entry-add-product"></select></label></div><p id="entry-add-note"></p><button id="entry-add-confirm" class="primary">Continue</button><button id="closemodal">Cancel</button>`);
 fillPaymentDestination();
}
function fillPaymentDestination(keep=false){
 const type=$('#entry-add-type').value,source=result.sources.find(s=>s.id===paymentEntrySource());
 const schemes=allocationSchemes(type).filter(s=>(type!=='ABS'||s.benefits.includes('ABS')&&absSourceAllowed(source,s))&&(type!=='CD'||s.benefits.includes('CD'))&&(type!=='Cash'||source?.date&&s.cash.start<=source.date&&source.date<=s.cash.end)&&(type!=='Net'||s.benefits.includes('Net')));
 const old=keep?$('#entry-add-scheme').value:'';const sid=schemes.some(s=>s.id===old)?old:schemes[0]?.id||'';
 $('#entry-add-scheme').innerHTML=schemes.length?schemes.map(s=>option(s.id,s.name+' · '+s.crop+' / '+s.segment,sid)).join(''):option('','No eligible scheme','');
 const sc=schemes.find(s=>s.id===sid),cfg=calculationSettings(),sold=soldProductIds();
 const products=cfg.products.filter(p=>sc?.products.includes(p.id)&&sold.has(p.id)&&!p.deleted_at&&(type!=='Cash'||sc.cash.products.includes(p.name)));
 $('#entry-add-product').innerHTML=(type==='ABS'?option('','All eligible products — preview automatic split',''):'')+products.map(p=>option(p.id,p.name+' · '+p.packing_kg+' kg','')).join('');
 $('#entry-add-product-label').hidden=!['ABS','Cash','Net'].includes(type);
 $('#entry-add-confirm').disabled=!sc||['Cash','Net'].includes(type)&&!products.length;
 $('#entry-add-note').textContent=type==='Cash'?'Continue opens the existing Cash quantity and funding preview.':type==='ABS'?'Blank product opens the existing automatic ABS split preview.':'Continue creates an editable zero-amount row for this payment.';
}
async function commitPaymentDestination(){
 if(record.status!=='draft')return;
 const type=$('#entry-add-type').value,scheme=$('#entry-add-scheme').value,product=['ABS','Cash','Net'].includes(type)?$('#entry-add-product').value:'';
 if(!scheme)throw Error('Choose an eligible scheme.');
 if(type==='Cash'){const existing=record.allocations.find(a=>a.source===paymentEntrySource()&&a.type==='Cash'&&a.scheme===scheme&&a.product===product);return await openCashQuantity(scheme,product,existing?.id||'');}
 if(type==='ABS'&&!product)return await openAbsDistribution(null,'',{scheme,source:paymentEntrySource(),type:'ABS'});
 $('#modal').close();await addDestinationAllocation(scheme,type,product);allocationPanelCollapsed=true;render();$('#payment-workbench')?.scrollIntoView?.({block:'start'});
}
async function previewAllocationClear(scope,target=''){
 if(record?.status!=='draft')return;
 clearTimeout(saveTimer);await saveQueue;await saveDraft();await calculate();
 const body={id:record.id,revision:record.revision,scope,target};
 const project=activeProject,workbook=activeWorkbook,snapshot=JSON.stringify(record);
 const plan=await api('/api/allocation-clear-preview',body);
 if(project!==activeProject||workbook!==activeWorkbook||snapshot!==JSON.stringify(record))throw Error('Calculation changed; reopen the clear preview.');
 paymentWorkbench.clear={body,plan,project,workbook,snapshot};
 const cfg=calculationSettings();
 modal(`<h2>${scope==='all'?'Clear all party allocations':scope==='source'?'Clear this payment’s allocations':'Remove allocation'}</h2><p><strong>${esc(record.party)}</strong> · ${plan.removed.length} allocation row(s) · ${plan.cash_splits.length} Cash quantity split(s).</p><div class="warn"><strong>${money(plan.released_total)} becomes unallocated.</strong>${plan.cash_splits.length?'<p>The affected Cash quantity returns to regular net quantity. Its complete Cash funding group is cleared together.</p>':''}${plan.extra_rows?`<p><strong>${plan.extra_rows} linked Cash funding row(s) outside your selection are also included below.</strong></p>`:''}</div><div class="tablewrap"><table><thead><tr><th>Payment</th><th>Type / destination</th><th>Released</th></tr></thead><tbody>${plan.removed.map(a=>`<tr><td>${esc(sourceLabel(a.source))}<small class="cell-note">${date(result.sources.find(s=>s.id===a.source)?.date)}</small></td><td>${esc(a.type)} · ${esc(cfg.schemes.find(s=>s.id===a.scheme)?.name||a.scheme)}<small class="cell-note">${esc(cfg.products.find(p=>p.id===a.product)?.name||'Scheme pool')}</small></td><td>${money(a.amount)}</td></tr>`).join('')}</tbody></table></div>${plan.cash_splits.length?`<p>Cash quantity removed: ${plan.cash_splits.map(x=>esc(cfg.products.find(p=>p.id===x.product)?.name||x.product)+' — supplied '+esc(x.supplied)+', returned '+esc(x.returned)).join('; ')}.</p>`:''}<p>New CN total: ${money(plan.previous_CN)} → ${money(plan.new_CN)}. ${plan.issues.length} review item(s) remain.</p><p>Original receipts, original dates, old-dues treatment and ledger entries remain intact. No released money is reassigned automatically.</p><button id="allocation-clear-confirm" class="danger">Confirm clear</button><button id="allocation-clear-cancel">Cancel</button>`);
}
async function applyAllocationClear(){
 const d=paymentWorkbench.clear;if(!d||d.applying)return;
 if(d.project!==activeProject||d.workbook!==activeWorkbook||d.snapshot!==JSON.stringify(record))throw Error('Calculation changed; reopen the clear preview.');
 d.applying=true;try{record=await api('/api/allocation-clear-apply',{...d.body,expected:d.plan.expected});}finally{d.applying=false;}
 paymentWorkbench.clear=null;paymentSelectedId='';$('#modal').close();await refresh();await calculate();render();toast('Allocations cleared. The released payment is available to allocate again.');
}
function highlightPaymentDestinations(){
 const source=paymentEntrySource();if(!source)return;
 const cfg=calculationSettings(),rows=record.allocations.filter(a=>a.source===source);
 for(const node of document.querySelectorAll('#radial-diagram .radial-node')){
  const d=node.dataset;const matches=rows.some(a=>{const type=allocationViewType(a.type),sc=cfg.schemes.find(s=>s.id===a.scheme);if(d.flowType)return d.flowType===type;if(d.radialProduct!==undefined)return d.radialType===type&&d.radialScheme===a.scheme&&d.radialProduct===a.product;if(d.radialCrop)return d.radialType===type&&d.radialCrop===sc?.crop;return false;});node.classList.toggle('payment-source-linked',matches);
 }
}
(()=>{'use strict';
 const oldTab=paymentTab,oldDraw=refreshAllocationFlow;
 paymentTab=function(){paymentEntrySource();return paymentEntriesHTML()+oldTab();};
 refreshAllocationFlow=function(){oldDraw();if(page==='Calculate CN'&&step===2)highlightPaymentDestinations();};
 document.addEventListener('change',e=>{if(['entry-add-type','entry-add-scheme'].includes(e.target.id))fillPaymentDestination(e.target.id==='entry-add-scheme');},true);
 document.addEventListener('click',e=>{const t=e.target.closest?.('button');if(!t)return;
 const ours=t.dataset.paymentEntry!==undefined||t.dataset.entryEdit!==undefined||t.hasAttribute('data-entry-add')||t.hasAttribute('data-entry-done')||t.dataset.clearAllocations!==undefined||['entry-add-confirm','allocation-clear-confirm','allocation-clear-cancel','segment-cd-preview','segment-cd-apply','segment-cd-cancel','unused-cd-apply','unused-cd-cancel'].includes(t.id)||t.dataset.segmentAllocate!==undefined||t.dataset.cdRelease!==undefined||page==='Calculate CN'&&step===2&&(t.dataset.source!==undefined||t.dataset.removeAllocation!==undefined||t.dataset.action==='add-allocation');
 if(t.dataset.paymentSelect!==undefined){const a=record?.allocations.find(a=>a.id===t.dataset.paymentSelect);if(a){paymentEntrySource();paymentWorkbench.source=a.source;}}
 if(!ours)return;e.preventDefault();e.stopImmediatePropagation();
 (async()=>{if(apiBusy||workbookSwitching||bulkRunning||auditBusy||yearLoading)throw Error('Finish the current operation first.');
 if(t.dataset.paymentEntry!==undefined)return selectPaymentEntry(t.dataset.paymentEntry);
 if(t.dataset.source!==undefined){selectPaymentEntry(t.dataset.source);return newPaymentAllocation();}
 if(t.hasAttribute('data-entry-done')){paymentSelectedId='';render();return;}
 if(record?.status!=='draft')return;
 if(t.dataset.segmentAllocate!==undefined)return await openSegmentAllocation(t.dataset.segmentAllocate,t.dataset.segmentCrop||'',t.dataset.segmentScheme||'');
 if(t.dataset.cdRelease!==undefined)return await previewUnusedCD(t.dataset.cdRelease);
 if(t.id==='segment-cd-preview')return await previewSegmentCD();
 if(t.id==='segment-cd-apply')return await applySegmentCD();
 if(t.id==='unused-cd-apply')return await applyUnusedCD();
 if(['segment-cd-cancel','unused-cd-cancel'].includes(t.id)){segmentCD=unusedCD=null;$('#modal').close();return;}
 if(t.dataset.clearAllocations!==undefined)return await previewAllocationClear(t.dataset.clearAllocations,t.dataset.clearTarget||'');
 if(t.dataset.removeAllocation!==undefined)return await previewAllocationClear('row',record.allocations[+t.dataset.removeAllocation]?.id);
 if(t.dataset.entryEdit!==undefined){const a=record.allocations.find(a=>a.id===t.dataset.entryEdit);if(!a)throw Error('Allocation changed. Reopen the payment.');paymentSelectedId=a.id;if(a.type==='Cash')return await openCashQuantity(a.scheme,a.product,a.id);allocationPanelCollapsed=true;render();return;}
 if(t.id==='entry-add-confirm')return await commitPaymentDestination();
 if(t.id==='allocation-clear-confirm')return await applyAllocationClear();
 if(t.id==='allocation-clear-cancel'){paymentWorkbench.clear=null;$('#modal').close();return;}
 return newPaymentAllocation();})().catch(err=>toast(err.message));
 },true);
})();

/* Update35: engine-owned usage, reviewed releases, and direct crop/segment entry. */
function sourceCDUnused(source){return allocationTotal(record.allocations.filter(a=>a.type==='CD'&&a.source===source).map(a=>({amount:directCDWorking(a)?.unused||'0'})));}
function directCDWorking(a){return a.type==='CD'?result.groups?.find(g=>g.scheme===a.scheme)?.CD_work?.find(w=>w.allocation===a.id):null;}
function paymentFundingStatus(a){
 const w=directCDWorking(a);if(w)return `<strong>Used ${money(w.eligible_payment)}</strong><small class="cell-note">${esc(w.percent)}% CD · CN ${money(w.CD)}</small><span class="${Number(w.unused)>0?'unused-funding':'muted'}">Unused ${money(w.unused)}</span>${Number(w.unused)>0&&Number(w.unused)<.01?'<small class="cell-note">Fraction of a paisa retained to preserve CN.</small>':''}${record.status==='draft'&&Number(w.unused)>=.01?`<button data-cd-release="${esc(a.id)}">Release unused…</button>`:''}`;
 if(a.type==='ABS'){const w=result.CNs?.find(c=>c.scheme===a.scheme&&c.benefit==='ABS')?.working?.find(w=>w.product_id===a.product);return w?`<small>Product total across ABS splits:<br>Token used ${money(w.principal)}<br>Excess to first CD ${money(w.excess)}</small>`:'Needs review';}
 return '<small class="muted">'+(a.type==='Settlement'?'Settlement · no benefit':a.type==='Cash'?'Reviewed Cash quantity funding':'Net-rate assignment')+'</small>';
}
function segmentAllocationButtons(){
 const choices=allocationSchemes('ABS').filter(s=>s.benefits.includes('ABS')||s.benefits.includes('CD'));
 if(!choices.length)return '';
 return `<section class="segment-allocation-actions"><h3>Allocate by crop / segment</h3><p>Select a payment above, then choose the whole segment. You can also click its crop card under ABS or CD.</p><div class="segment-allocation-list">${choices.map(s=>`<div><strong>${esc(s.crop)} · ${esc(s.segment)}</strong><small>${esc(s.name)}</small><span>${['ABS','CD'].filter(type=>s.benefits.includes(type)).map(type=>`<button data-segment-allocate="${type}" data-segment-crop="${esc(s.crop)}" data-segment-scheme="${esc(s.id)}" ${record.status!=='draft'?'disabled':''}>Allocate ${type}…</button>`).join(' ')}</span></div>`).join('')}</div></section>`;
}
async function savedAllocationSnapshot(){
 clearTimeout(saveTimer);await saveQueue;await saveDraft();await calculate();
 return {id:record.id,revision:record.revision};
}
function allocationContext(){return {snapshot:JSON.stringify(record),project:activeProject,workbook:activeWorkbook};}
function requireAllocationContext(d){if(!d||d.project!==activeProject||d.workbook!==activeWorkbook||d.snapshot!==JSON.stringify(record))throw Error('Calculation changed; open a fresh allocation preview.');}
async function openSegmentAllocation(type,crop='',scheme=''){
 if(record?.status!=='draft')return;
 if(apiBusy||workbookSwitching||bulkRunning||auditBusy||yearLoading)throw Error('Finish the current operation first.');
 const source=paymentEntrySource();if(!source)throw Error('Select a registered payment first.');
 if(type==='ABS')return await openAbsDistribution(null,crop,{scheme,source,type:'ABS'});
 if(type!=='CD')return;
 const body=await savedAllocationSnapshot(),context=allocationContext();
 const options=await api('/api/allocation-review-preview',{...body,operation:'cd-group',crop,options:true});
 requireAllocationContext(context);
 if(!options.schemes.length)throw Error('No eligible net-sold CD segment in this crop. Review products and schemes.');
 const choices=options.schemes;
 segmentCD={...context,body,options,plan:null,draft:{operation:'cd-group',crop,scheme:choices.some(s=>s.id===scheme)?scheme:choices.length===1?choices[0].id:'',source,amount:''}};
 segmentCDForm();
}
function segmentCDForm(){
 const d=segmentCD;if(!d)return;const v=d.draft,p=d.plan;
 modal(`<h2>Allocate CD to crop / segment</h2><p>CD funds the combined eligible balance of the selected segment. The original receipt date selects the CD slab. Products share the existing scheme benefit; money is counted once.</p><div class="grid two"><label>Crop / segment / scheme<select id="segment-cd-scheme">${option('','Choose segment',v.scheme)}${d.options.schemes.map(s=>option(s.id,s.crop+' / '+s.segment+' · '+s.name,v.scheme)).join('')}</select></label><label>Payment entry<select id="segment-cd-source">${d.options.sources.map(s=>option(s.id,sourceLabel(s.id)+' · '+(s.date?date(s.date):'Undated opening credit')+' · '+money(s.remaining)+' available',v.source)).join('')}</select></label><label>Amount to offer (₹)<input type="number" min="0" step="any" id="segment-cd-amount" value="${esc(v.amount)}"></label></div><p id="segment-cd-status" role="status">Choose a segment, select the receipt and enter an amount within its available balance. Preview first, then confirm allocation.</p>${p?`<div class="ok"><strong>${esc(p.scheme_name)}</strong> · ${p.original_date?date(p.original_date):'Undated opening credit'} · ${esc(p.percent)}% CD</div>${!Number(p.percent)?'<p class="warn">This receipt has no positive CD rate in the selected scheme. Funding at 0% produces no CD benefit.</p>':''}<div class="tablewrap"><table><tr><th>Amount offered</th><th>Actually usable</th><th>Allocation to save</th><th>Excess left available</th><th>CD from this allocation</th></tr><tr><td>${money(p.requested)}</td><td>${money(p.used)}</td><td>${money(p.retained)}</td><td>${money(p.released)}</td><td>${money(p.CD)}</td></tr></table></div><p>At most one extra paisa is retained for an ordinary rupee allocation so the full calculated CN is preserved. After applying, ${money(p.remaining)} remains available from this receipt.</p><h3>Products covered by this segment</h3><table><tr><th>Product</th><th>Regular net sold</th><th>CD CN after allocation</th></tr>${p.products.map(x=>`<tr><td>${esc(x.product)}</td><td>${esc(x.regular_net)} ${esc(x.unit)}</td><td>${money(x.CD_CN)}</td></tr>`).join('')}</table><p>Product CN is the existing display distribution of the segment's rounded CD. It is not a separate product funding limit.</p>${p.affected.length?`<p class="warn">This receipt is processed before ${p.affected.length} existing CD allocation(s). Their unused funding increases. Review and release unused funding after applying.</p>`:''}<p>Total new CN: ${money(p.previous_CN)} → ${money(p.new_CN)}.</p>${p.issues.length?`<p class="warn">${p.issues.length} existing review item(s) remain. Allocation does not resolve ledger or scheme corrections.</p>`:''}`:''}<div class="actions"><button id="segment-cd-preview" class="primary">Preview allocation</button>${p?`<button id="segment-cd-apply" class="primary" ${Number(p.retained)>0?'':'disabled'}>Allocate usable ${money(p.retained)}</button>`:''}<button id="segment-cd-cancel">Cancel</button></div>`);
}
function readSegmentCD(){const d=segmentCD;if(!d)return;for(const key of ['scheme','source','amount']){const el=$('#segment-cd-'+key);if(el)d.draft[key]=el.value;}}
async function previewSegmentCD(){
 const d=segmentCD;requireAllocationContext(d);readSegmentCD();d.plan=null;
 if(!d.draft.scheme){$('#segment-cd-scheme')?.focus();throw Error('Choose a crop / segment / scheme before previewing.');}
 const source=d.options.sources.find(s=>s.id===d.draft.source);
 if(!source)throw Error('Choose a payment entry before previewing.');
 if(!d.draft.amount||!Number.isFinite(Number(d.draft.amount))||Number(d.draft.amount)<=0){$('#segment-cd-amount')?.focus();throw Error('Enter a positive amount to preview.');}
 const limitError=allocationLimitError({type:'CD',scheme:d.draft.scheme,source:d.draft.source,amount:d.draft.amount},-1);
 if(limitError){$('#segment-cd-amount')?.focus();throw Error('This receipt has '+money(source.remaining)+' available for a new allocation. Reduce the offered amount. '+limitError);}
 const inputs=JSON.stringify(d.draft),button=$('#segment-cd-preview');$('#dialog-feedback')?.remove();
 if(button){button.disabled=true;button.textContent='Preparing preview…';}$('#segment-cd-status').textContent='Calculating usable funding and excess…';
 let plan;try{plan=await api('/api/allocation-review-preview',{...d.body,...d.draft});}catch(err){if(segmentCD===d&&$('#segment-cd-status'))$('#segment-cd-status').textContent='Preview not ready — correct the message above and try again.';throw err;}finally{if(segmentCD===d&&button?.isConnected){button.disabled=false;button.textContent='Preview allocation';}}
 if(segmentCD!==d)return;requireAllocationContext(d);readSegmentCD();if(inputs!==JSON.stringify(d.draft))throw Error('Inputs changed; preview the allocation again.');
 d.plan=plan;d.previewInputs=inputs;segmentCDForm();$('#segment-cd-status').textContent=Number(plan.retained)>0?'Preview ready. Review the figures below, then click Allocate usable to save. Cancel or Close saves no allocation.':'This segment needs no additional CD funding. Nothing will be allocated. Choose another segment or Cancel.';
}
async function applySegmentCD(){
 const d=segmentCD;if(!d?.plan||d.applying)return;requireAllocationContext(d);readSegmentCD();if(d.previewInputs!==JSON.stringify(d.draft))throw Error('Inputs changed; preview again.');
 d.applying=true;try{record=await api('/api/allocation-review-apply',{...d.body,...d.draft,expected:d.plan.expected});}finally{d.applying=false;}
 paymentWorkbench.source=d.draft.source;paymentSelectedId='';segmentCD=null;$('#modal').close();await refresh();await calculate();render();$('#payment-workbench')?.scrollIntoView?.({block:'start'});toast('Usable CD funding allocated. Excess remains available for another segment.');
}
async function previewUnusedCD(target){
 const body={...await savedAllocationSnapshot(),operation:'cd-release',target},context=allocationContext();
 const plan=await api('/api/allocation-review-preview',body);requireAllocationContext(context);unusedCD={...context,body,plan};
 modal(`<h2>Release unused CD funding</h2><p>${esc(sourceLabel(plan.source))} · ${plan.original_date?date(plan.original_date):'Undated opening credit'} · ${esc(plan.percent)}% CD</p><table><tr><th>Allocated</th><th>Actually used</th><th>Retain</th><th>Release to same receipt</th></tr><tr><td>${money(plan.assigned)}</td><td>${money(plan.used)}</td><td>${money(plan.retained)}</td><td>${money(plan.released)}</td></tr></table><p class="ok">${money(plan.released)} becomes available to allocate again. All calculated benefit totals are preserved.</p><p>A fraction of a paisa may remain assigned to preserve full entitlement. Original receipt dates, ledger entries and ABS allocations stay intact. Choose another crop/segment after applying.</p><p>New CN total ${money(plan.previous_CN)} → ${money(plan.new_CN)}.</p><button id="unused-cd-apply" class="primary">Release ${money(plan.released)}</button><button id="unused-cd-cancel">Cancel</button>`);
}
async function applyUnusedCD(){
 const d=unusedCD;if(!d||d.applying)return;requireAllocationContext(d);d.applying=true;
 try{record=await api('/api/allocation-review-apply',{...d.body,expected:d.plan.expected});}finally{d.applying=false;}
 paymentWorkbench.source=d.plan.source;paymentSelectedId='';unusedCD=null;$('#modal').close();await refresh();await calculate();render();$('#payment-workbench')?.scrollIntoView?.({block:'start'});toast('Unused CD released. Select another crop / segment for this same payment.');
}
(()=>{
 const oldClick=allocation28Click;
 allocation28Click=async function(e){const t=e.target.closest?.('button');if(t?.dataset.radialCrop!==undefined&&['ABS','CD'].includes(t.dataset.radialType)&&record?.status==='draft')return await openSegmentAllocation(t.dataset.radialType,t.dataset.radialCrop);return await oldClick(e);};
 document.addEventListener('change',e=>{if(!e.target.id?.startsWith('segment-cd-')||!segmentCD)return;readSegmentCD();segmentCD.plan=null;const apply=$('#segment-cd-apply');if(apply)apply.disabled=true;const status=$('#segment-cd-status');if(status)status.textContent='Inputs changed — preview again before applying.';},true);
})();
(()=>{
 const oldABSForm=absDistributionForm;
 absDistributionForm=function(){oldABSForm();const d=absDistribution,p=d?.plan;if(!p||!Number(p.products.reduce((n,x)=>n+Number(x.excess||0),0)))return;
 const capacity=allocationTotal(p.products.map(x=>({amount:x.remaining_token_capacity}))),button=document.createElement('button');
 if(Number(capacity)<=0||Number(capacity)>=Number(p.amount))return;
 button.type='button';button.id='absd-token-only';button.textContent='Preview token requirement only · '+money(capacity);button.dataset.capacity=capacity;
 $('#absd-preview')?.parentElement?.append(button);
 };
 document.addEventListener('click',e=>{const t=e.target.closest?.('#absd-token-only');if(!t)return;e.preventDefault();e.stopImmediatePropagation();if(apiBusy||!absDistribution)return;$('#absd-amount').value=t.dataset.capacity;previewAbsDistribution().catch(err=>toast(err.message));},true);
})();
