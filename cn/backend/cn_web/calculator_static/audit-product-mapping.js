'use strict';
// Audit-only entry point. Never replaces the active calculation or its draft.
(()=>{
 let scope='',targets=new Map(),editing=null;
 const current=()=>String(activeProject)+'/'+String(activeWorkbook);
 const safe=v=>esc(String(v??''));
 function remember(rows){if(scope!==current()){scope=current();targets.clear();editing=null;}for(const r of rows||[])targets.set(r.id,r);return rows||[];}
 function buttons(rows){return remember(rows).map(r=>`<button type="button" data-audit-product-map="${safe(r.id)}">Map ${safe(r.name)}</button>`).join(' ');}
 globalThis.CNAuditMapping={buttons};
 const originalNRV=postedNRVHTML;
 postedNRVHTML=function(nrv){
  const html=originalNRV(nrv);if(!nrv?.mapping_targets?.length)return html;
  const rows=remember(nrv.mapping_targets),box=document.createElement('div');box.innerHTML=html;
  const tables=box.querySelectorAll('.ledger-nrv-table');
  const kinds=[nrv.crop_rows,nrv.product_average_rows||[],nrv.party_rows,nrv.product_rows];
  tables.forEach((table,ti)=>{let ri=0;for(const tr of table.querySelectorAll('tbody tr')){
   if(!tr.querySelector('td strong'))continue;const data=kinds[ti]?.[ri++];if(!data)continue;
   const possible=rows.filter(r=>(!data.party||r.party===data.party&&r.location===data.location)&&(!data.product||r.name===data.product)&&(!data.crop||data.crop==='Unmapped crop'||r.crop===data.crop));
   if(!possible.length)continue;
   tr.dataset.auditMapGroup=possible.map(r=>r.id).join(',');tr.style.cursor='pointer';tr.title='Open statement product mapping';
   const action=document.createElement('button');action.type='button';action.dataset.auditMapGroup=tr.dataset.auditMapGroup;action.textContent='Map statement product'+(possible.length>1?'s':'');tr.cells[0].append(document.createElement('br'),action);
  }});
  const section=document.createElement('section');section.className='card';section.innerHTML=`<h2>Unmapped statement products</h2><p>Click a product line to map it. Statement names, packing suggestions, quantities and rates are shown for reference; bill values and CN schemes are not changed.</p><div class="tablewrap"><table><tr><th>Party / original bill</th><th>Statement product</th><th>Quantity / rate / amount</th><th>Action</th></tr>${rows.map(r=>`<tr data-audit-map-group="${safe(r.id)}" style="cursor:pointer"><td>${safe(r.party)} · ${safe(r.location)}<br>${safe(r.date)} · ${safe(r.reference)}</td><td>${safe(r.name)}<br>${safe(r.reason)}</td><td>${safe(r.qty)} ${safe(r.unit)} · ${safe(r.rate)}<br>${safe(r.amount)}</td><td>${buttons([r])}</td></tr>`).join('')}</table></div>`;box.append(section);return box.innerHTML;
 };
 function chooser(ids){const rows=ids.map(id=>targets.get(id)).filter(Boolean);if(rows.length===1)return open(rows[0]);modal(`<h2>Choose statement product</h2>${rows.map(r=>`<p>${safe(r.party)} · ${safe(r.date)} · ${safe(r.reference)}<br>${buttons([r])}</p>`).join('')}`);}
 async function open(row){
  const requested=current(),out=await api('/api/native-audit-product-context',{source:row.source,entry_id:row.entry_id,item_index:row.item_index});if(requested!==current())return;
  editing={row,context:out,scope:requested};const item=out.item,p=out.products.find(p=>p.id===item.product),crop=p?.crop||row.crop||'';
  modal(`<h2>Map statement product</h2><p><b>${safe(out.party)}</b> · ${safe(out.entry.date)} · ${safe(out.entry.reference)}<br><b>${safe(item.name)}</b><br>Statement: ${safe(item.qty)} ${safe(item.unit)} × ${safe(item.rate)} · amount ${safe(item.amount)}</p><div class="grid two"><label>Saved product<select id="am-existing"><option value="">Add / name product</option>${out.products.map(p=>`<option value="${safe(p.id)}" ${item.product===p.id?'selected':''}>${safe(p.crop)} · ${safe(p.name)} · ${safe(p.packing_kg)} kg</option>`).join('')}</select></label><label>Saved crop<select id="am-crop"><option value="">Choose crop</option>${out.crops.map(c=>`<option ${crop===c?'selected':''}>${safe(c)}</option>`).join('')}</select></label><label>Or name a new crop<input id="am-new-crop"></label><label>Product name<input id="am-name" value="${safe(p?.name||item.name)}"></label><label>Packing: kg per packet<input id="am-pack" type="number" min="0.000001" step="any" value="${safe(p?.packing_kg||item.mapping_suggestion?.detected_packing_kg||sourcePacking(item.name)||'')}"></label></div><p>Only explicitly printed packing is suggested. Confirm missing packing yourself. A new product has no benefits until you assign its scheme separately.</p><button type="button" id="am-save" class="primary">Save Mapping and recheck</button><p id="am-error" role="alert"></p>`);
 }
 document.addEventListener('change',e=>{if(e.target.id!=='am-existing'||!editing)return;const p=editing.context.products.find(p=>p.id===e.target.value);if(!p)return;$('#am-crop').value=p.crop;$('#am-new-crop').value='';$('#am-name').value=p.name;$('#am-pack').value=p.packing_kg;});
 document.addEventListener('click',async e=>{
  const b=e.target.closest('[data-audit-product-map],[data-audit-map-group],#am-save');if(!b)return;e.preventDefault();e.stopImmediatePropagation();
  try{
   if(scope!==current())throw Error('Workbook changed. Run the audit again.');
   if(b.dataset.auditProductMap!==undefined)return await open(targets.get(b.dataset.auditProductMap));
   if(b.dataset.auditMapGroup!==undefined)return await chooser(b.dataset.auditMapGroup.split(','));
   if(!editing||editing.scope!==current())throw Error('Reopen the statement line.');
   const pending=editing;b.disabled=true;
   const values={crop:$('#am-new-crop').value.trim()||$('#am-crop').value,name:$('#am-name').value.trim(),packing:$('#am-pack').value};
   await api('/api/native-audit-product-save',{source:pending.row.source,entry_id:pending.row.entry_id,item_index:pending.row.item_index,revision:pending.context.revision,evidence:pending.context.evidence,...values});
   if(pending.scope!==current())return;await refresh();$('#modal').close();editing=null;targets.clear();
   if(page==='Ledger Audit'&&auditReport){if(auditNRVSource==='saved_bulk')await runSavedBulkNRV();else await runAudit();}
   document.dispatchEvent(new Event('cn-audit-product-mapped'));toast('Mapping saved. Statement values and CN calculations are unchanged.');
  }catch(ex){const box=$('#am-error');if(box)box.textContent=ex.message;else toast(ex.message);}finally{b.disabled=false;}
 },true);
})();
