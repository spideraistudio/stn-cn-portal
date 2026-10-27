'use strict';
// UX Phase 4: presentation only. Evidence, review identities and export remain
// owned by the existing audit services and renderers; no persisted UI state.
(()=>{
 const safe=v=>esc(String(v??''));
 const parties=f=>[...new Map((f.vouchers||[]).map(v=>{const p=[v.party||'',v.location||'',v.state||''];return [JSON.stringify(p),p];})).values()];
 const partyKey=f=>JSON.stringify(parties(f).map(p=>JSON.stringify(p)).sort());
 const partyCount=rows=>new Set(rows.flatMap(({f})=>parties(f).map(p=>JSON.stringify(p)))).size;
 const reviewed=f=>auditReviewFor(f)?.status==='not_applicable';
 const countLabel=rows=>`${rows.length} finding(s) · ${partyCount(rows)} parties`;
 function finding(row,index){const context=row.item?`<p class="muted">Saved import: ${safe(row.item.party)} · ${safe(row.item.season)} · ${safe(row.item.filename||'Saved import')} · ${date(row.item.ledger_audit.start)}–${date(row.item.ledger_audit.end)}</p>`:'';return context+auditFindingHTML(row.f,index);}
 function partyGroups(rows){
  const groups=new Map();for(const row of rows){const key=partyKey(row.f);if(!groups.has(key))groups.set(key,[]);groups.get(key).push(row);}
  return [...groups.values()].map(group=>`<details class="audit-party card"><summary><strong>${parties(group[0].f).map(p=>p.filter(Boolean).map(safe).join(' · ')).join(' / ')||'Unspecified party'}</strong> · ${group.length} finding(s)</summary>${group.map(finding).join('')}</details>`).join('');
 }
 function categories(rows,bulk=false){
  if(!rows.length)return '<div class="ok">No findings under these checks in the selected period.</div>';
  const groups=new Map();for(const row of rows){if(!groups.has(row.f.type))groups.set(row.f.type,[]);groups.get(row.f.type).push(row);}
  return '<div class="audit-category-grid">'+[...groups].map(([type,items])=>{
   const pending=items.filter(x=>!reviewed(x.f)),done=items.filter(x=>reviewed(x.f));
   return `<details class="card audit-category${bulk?' bulk-audit-category':''}"><summary><strong>${safe(type)}</strong><span class="pill">${countLabel(items)}</span><span>${pending.length} need review · ${done.length} reviewed / not applicable</span><small>Open category, then expand a party to inspect evidence.</small></summary>${pending.length?`<h3>Needs review · ${pending.length}</h3>${partyGroups(pending)}`:'<p class="ok">No pending findings in this category.</p>'}${done.length?`<details class="audit-reviewed"><summary>Reviewed / not applicable · ${done.length} finding(s)</summary><p>Reasons and original vouchers remain available. Use View / change review to reopen a finding.</p>${partyGroups(done)}</details>`:''}</details>`;
  }).join('')+'</div>';
 }
 auditCategoriesHTML=report=>categories(report.findings.map(f=>({f})));
 auditReportHTML=function(report){
  if(!report)return '';
  const done=report.findings.filter(reviewed).length;
  return `<section class="card"><h2>Ledger audit: ${date(report.start)} to ${date(report.end)}</h2><p>${report.party_count} parties · ${report.voucher_count} vouchers · ${report.findings.length} findings</p><p><strong>${report.findings.length-done} need review · ${done} reviewed / not applicable</strong></p>${report.warnings.length?`<p class="warn">${report.warnings.length} import / coverage warning(s). Review the warnings below before relying on these checks.</p>`:''}</section><h2>Finding categories</h2><p>Choose a category, then expand a party and finding. Reviewed items stay available in their own collapsed section.</p>${auditCategoriesHTML(report)}<details class="card audit-auxiliary"><summary>CN given & realised net rate — expand CN / NRV report · ${report.posted_CN_NRV?.mapping_targets?.length||0} unmapped line(s) · ${report.posted_CN_NRV?.pending_CNs?.length||0} CN item(s) need classification</summary>${postedNRVHTML(report.posted_CN_NRV)}</details><details class="card"><summary>Already-given / posted credit vouchers — includes excluded journal/freight (${report.posted_CNs.length})</summary>${report.posted_CNs.map(v=>`<h3>${safe(auditCNLabel(v))}</h3>${auditCropEditor(v)}${auditVoucher(v)}`).join('')||'<p>No posted CNs in this period.</p>'}<p>All posted credit amount (includes exclusions; not the scheme NRV deduction): ${money(report.posted_CNs.reduce((a,v)=>a+Number(v.credit),0))}</p></details>${report.stock_timing?.length?`<details class="card"><summary>Stock timing / invoice-rate notes (${report.stock_timing.length})</summary>${report.stock_timing.map(n=>`<h3>${safe(n.party)} / ${safe(n.product)}</h3><p>${safe(n.message)}</p>${n.vouchers.map(auditVoucher).join('')}`).join('')}</details>`:''}${report.warnings.length?`<details class="card"><summary>Import / coverage warnings (${report.warnings.length})</summary>${report.warnings.map(w=>`<p>${safe(w.party)}: ${safe(w.message)}</p>`).join('')}</details>`:''}<details class="card"><summary>Checking rules & coverage notes</summary>${report.notes.map(n=>`<p>${safe(n)}</p>`).join('')}</details>`;
 };
 bulkAuditCategoryHTML=function(recent){
  const rows=recent.flatMap(item=>item.ledger_audit.findings.map(f=>({f,item})));
  return '<p>Counts below are saved import findings; repeated import histories are retained, not merged. Standalone checks above use their own selected period.</p>'+categories(rows,true)+'<details class="audit-auxiliary"><summary>Posted CNs, source notes and warnings from saved imports</summary>'+recent.map(x=>`<details><summary>${safe(x.party)} · ${safe(x.season)}</summary>${auditReportHTML({...x.ledger_audit,findings:[]})}</details>`).join('')+'</details>';
 };
})();
