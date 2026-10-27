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
