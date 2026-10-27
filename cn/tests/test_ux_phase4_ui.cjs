// Actual disclosure renderers in a VM. No browser/Windows rendering claim.
const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
const root=__dirname+'/../backend/cn_web/calculator_static/';
const source=fs.readFileSync(root+'app.js','utf8');
const escape=v=>String(v??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const c={state:{settings:{audit_finding_reviews:{}}},esc:escape,date:String,money:String,auditVoucher:v=>`<article>${escape(v.reference)}</article>`,auditCNLabel:()=>'',auditCropEditor:()=>'',postedNRVHTML:()=>'<p>NRV-DETAIL-EVIDENCE</p>',auditCategoriesHTML(){},auditReportHTML(){},bulkAuditCategoryHTML(){}};
vm.createContext(c);
for(const name of ['auditReviewFor','auditReviewControls','auditFindingHTML']){const a=source.indexOf('function '+name+'(');vm.runInContext(source.slice(a,source.indexOf('\n',a)),c);}
vm.runInContext(fs.readFileSync(root+'audit-categories.js','utf8'),c);
function f(id,location='Town',type='Duplicate payment reference'){return {review_id:id,type,message:'Check bank evidence',evidence:'NEFT<123>',vouchers:[{party:'Same name',location,reference:'V-'+id},{party:'Same name',location,reference:'W-'+id}]};}
const report={start:'2026-04-01',end:'2027-03-31',party_count:2,voucher_count:6,findings:[f('pending'),f('done'),f('other','Other town','Return rate above supply')],posted_CNs:[],warnings:[{party:'Coverage',message:'Missing earlier statement'}],notes:['Original bill review required'],stock_timing:[],posted_CN_NRV:{}};
c.state.settings.audit_finding_reviews.done={status:'not_applicable',reason:'Bank checked <safe>',reviewed_at:'2026-10-24T00:00:00Z'};
const before=JSON.stringify(report);
let html=c.auditReportHTML(report);
assert.ok(html.indexOf('Finding categories')<html.indexOf('NRV-DETAIL-EVIDENCE'));
assert.match(html,/2 need review · 1 reviewed/);
assert.match(html,/Reviewed \/ not applicable · 1 finding/);
assert.match(html,/Bank checked &lt;safe&gt;/);assert.match(html,/NEFT&lt;123&gt;/);
assert.match(html,/data-audit-review="done"/);assert.match(html,/data-audit-review="pending"/);
assert.equal((html.match(/data-audit-review=/g)||[]).length,3);
assert.doesNotMatch(html,/<details[^>]*\bopen(?:[\s=>])/);
assert.equal(JSON.stringify(report),before);
// Reopening moves the exact same evidence to pending; nothing disappears.
delete c.state.settings.audit_finding_reviews.done;
html=c.auditReportHTML(report);assert.match(html,/3 need review · 0 reviewed/);assert.doesNotMatch(html,/class="audit-reviewed"/);
// Stale review IDs cannot suppress new-evidence findings.
c.state.settings.audit_finding_reviews.old={status:'not_applicable',reason:'old'};
assert.match(c.auditReportHTML(report),/3 need review · 0 reviewed/);
// Same name at different locations is counted independently, within one category.
const sameType={...report,findings:[f('a'),f('b','Other town')]};
assert.match(c.auditCategoriesHTML(sameType),/2 finding\(s\) · 2 parties/);
const recent=[{party:'Same name',season:'Kharif',filename:'one.pdf',ledger_audit:sameType},{party:'Same name',season:'Rabi',filename:'two.pdf',ledger_audit:sameType}];
html=c.bulkAuditCategoryHTML(recent);assert.match(html,/4 finding\(s\) · 2 parties/);assert.match(html,/Saved import: Same name · Kharif/);assert.match(html,/Saved import: Same name · Rabi/);
assert.match(c.auditCategoriesHTML({...report,findings:[]}),/No findings/);
c.state.settings.audit_finding_reviews={pending:{status:'not_applicable'},done:{status:'not_applicable'},other:{status:'not_applicable'}};
assert.match(c.auditReportHTML(report),/0 need review · 3 reviewed/);
assert.equal(c.auditReportHTML(null),'');
console.log('PASS: categories before NRV, closed category/party/finding/reviewed disclosures, pending/reviewed counts, unique party locations, multi-import evidence, review/reopen/stale identities, escaping, empty/all-reviewed cases and no report mutation.');
