// Complete UI: template/event/API checks, not rendered browser certification.
const vm=require('node:vm'),fs=require('node:fs'),crypto=require('node:crypto'),assert=require('node:assert/strict');
const elements=new Map(),events={};function element(k){if(!elements.has(k))elements.set(k,{innerHTML:'',textContent:'',style:{},querySelectorAll:()=>[],showModal(){},close(){}});return elements.get(k)}
const context={console,structuredClone,crypto:crypto.webcrypto,setTimeout,clearTimeout,Blob,URL,window:{print(){}},confirm:()=>true,prompt:()=>null,delayReport:false,resolveReports:[],document:{querySelector:element,querySelectorAll:()=>[],createElement:()=>({click(){}}),addEventListener:(type,fn)=>events[type]=fn}};
context.fetch=(url,opt)=>context.delayReport&&url==='/api/territory-report'?new Promise(resolve=>context.resolveReports.push(resolve)):fetch('http://127.0.0.1:8765'+url,opt);
vm.createContext(context);vm.runInContext(fs.readFileSync(__dirname+'/../static/app.js','utf8'),context);const run=s=>vm.runInContext(s,context);
(async()=>{
 for(let n=0;n<100&&!element('#main').innerHTML;n++)await new Promise(r=>setTimeout(r,10));
 assert.match(element('#main').innerHTML,/Recent calculations/);assert.match(element('#main').innerHTML,/ALL ACTIVE WORKBOOKS/);assert.match(element('#nav').innerHTML,/aria-current="page"/);assert.doesNotMatch(element('#nav').innerHTML,/data-page="Calculate CN"/);

 const categories=run(`bulkAuditCategoryHTML([{party:'Alpha dealer',season:'Season A',filename:'a.pdf',ledger_audit:{start:'2026-04-01',end:'2026-12-31',findings:[{type:'Possible duplicate sales return',message:'Review',vouchers:[]}],posted_CNs:[],notes:[],warnings:[],stock_timing:[],party_count:1,voucher_count:1}},{party:'Beta dealer',season:'Season A',filename:'b.pdf',ledger_audit:{start:'2026-04-01',end:'2026-12-31',findings:[{type:'Mixed rates',message:'Review',vouchers:[]}],posted_CNs:[],notes:[],warnings:[],stock_timing:[],party_count:1,voucher_count:1}}])`);
 assert.match(categories,/Possible duplicate sales return/);assert.match(categories,/Mixed rates/);assert.doesNotMatch(categories.split('</summary>')[0],/Alpha dealer|Beta dealer/);assert.doesNotMatch(categories,/<details class="card audit-category bulk-audit-category" open/);assert.match(categories,/Alpha dealer/);
 const initial=await run("api('/api/backup')");
 for(const [page,pattern] of [['Workbooks',/workbook-grid/],['Parties',/party-search/],['Ledger Audit',/audit-files/],['Year Link',/year-previous-files/],['Settings',/saved-scheme/],['History',/Search party, season/]]){run(`page=${JSON.stringify(page)};render()`);assert.match(element('#main').innerHTML,pattern);assert.match(element('#main').innerHTML,/page-masthead/);}
 for(const key of ['seasons','products','backup']){run(`settingsSection=${JSON.stringify(key)};settingsPage()`);assert.match(element('#main').innerHTML,/page-masthead/);}
 await run("(async()=>{page='Reports';await reportsPage()})()");assert.match(element('#main').innerHTML,/report-filter-card/);assert.match(element('#main').innerHTML,/weighted NRV/);
 const after=await run("api('/api/backup')");function normalise(x){if(x&&typeof x==='object'){if(String(x.format||'').startsWith('all-crop-cn'))delete x.created_at;for(const v of Object.values(x))normalise(v);}return x;}assert.deepEqual(normalise(after),normalise(initial));
 assert.doesNotMatch(run("pageHead('<script>','<img>')"),/<script>|<img>/);
 await run("(async()=>{const doc=await api('/api/fixture/ashapura');record={...blank(),...doc};await calculate();page='Calculate CN';})()");const before=run('JSON.stringify(record)');
 for(let i=0;i<5;i++){run(`step=${i};render()`);assert.match(element('#main').innerHTML,/calculation-steps/);assert.match(element('#main').innerHTML,/workflow-footer/);assert.match(element('#main').innerHTML,/aria-current="step"/);}
 assert.equal(run('JSON.stringify(record)'),before);run('record=null');
 // Background dashboard reads must neither block switching nor paint an old workbook response.
 context.delayReport=true;run("page='Dashboard';dashboardPage()");assert.equal(run('apiBusy'),0);const oldResolver=context.resolveReports.shift();
 await run("(async()=>{const w=await api('/api/workbooks',{name:'UI scope guard',state:'Gujarat',period:'UI period',start:'2026-04-01',end:'2026-12-31',cutoff:'2026-12-31',mode:'copy'});await switchWorkbook(w.id);})()");assert.equal(run('state.workbook.name'),'UI scope guard');assert.equal(run('apiBusy'),0);
 const oldData={summary:{products:999,parties:999,total_CN:'999',net_realisation:'999'},notes:[]};oldResolver({ok:true,json:async()=>oldData});await new Promise(r=>setTimeout(r,10));assert.doesNotMatch(element('#dashboard-report').innerHTML,/999/);
 const latest=context.resolveReports.pop();assert.ok(latest);latest({ok:true,json:async()=>({summary:{products:2,parties:1,total_CN:'100',net_realisation:'900'},notes:['Visible overlap review note']})});await new Promise(r=>setTimeout(r,10));assert.match(element('#dashboard-report').innerHTML,/Visible overlap review note/);assert.match(element('#dashboard-report').innerHTML,/₹100.00/);assert.match(element('#dashboard-report').innerHTML,/Freight and requested changes are excluded/);
 console.log('Complete UI: all page routes/settings sections, preserved import/audit/report/backup controls, escaped headings, five workflow steps, read-only rendering/backup comparison, and stale/nonblocking dashboard reporting passed.');
})().catch(e=>{console.error(e);process.exitCode=1});
