// Payment Studio: real API, isolated test store, UI event/template checks.
const vm=require('node:vm'),fs=require('node:fs'),crypto=require('node:crypto'),assert=require('node:assert/strict');
const elements=new Map(),events={};function element(k){if(!elements.has(k))elements.set(k,{innerHTML:'',textContent:'',style:{},querySelectorAll:()=>[],showModal(){},close(){}});return elements.get(k)}
const context={console,structuredClone,crypto:crypto.webcrypto,fetch:(url,opt)=>fetch('http://127.0.0.1:8765'+url,opt),setTimeout,clearTimeout,Blob,URL,window:{print(){}},confirm:()=>true,prompt:()=>null,document:{querySelector:element,querySelectorAll:()=>[],createElement:()=>({click(){}}),addEventListener:(type,fn)=>events[type]=fn}};
vm.createContext(context);vm.runInContext(fs.readFileSync(__dirname+'/../static/app.js','utf8'),context);
const run=s=>vm.runInContext(s,context);
const click=dataset=>events.click({target:{closest:()=>({dataset})}});
(async()=>{
 for(let n=0;n<100&&!element('#main').innerHTML;n++)await new Promise(r=>setTimeout(r,10));
 await run(`(async()=>{const sc=state.settings.schemes.find(s=>s.id==='scheme-4');sc.states=['Gujarat'];sc.confirmed=true;sc.abs_start='2026-01-01';sc.abs_end='2026-03-31';state.settings.seasons[0].start='2026-04-01';state.settings.seasons[0].end='2026-10-01';state.settings.seasons[0].cutoff='2026-10-16';state.settings.seasons[0].confirmed=true;state.settings=await api('/api/settings',state.settings);record=blank();record.party='Automatic distribution';record.state='Gujarat';record.entries=[{id:'advance',kind:'receipt',date:'2026-03-01',credit:'30000',debit:'0'},{id:'sale',kind:'sale',date:'2026-05-01',debit:'105000',credit:'0',items:[{name:'First',product:sc.products[0],qty:'100',unit:'kg',amount:'35000'},{name:'Second',product:sc.products[1],qty:'200',unit:'kg',amount:'70000'}]}];record.allocations=[{id:'automatic',type:'ABS',source:'advance',scheme:sc.id,product:'',amount:'30000',remark:''}];record.closing='75000';record.ledger_confirmed=true;step=2;page='Calculate CN';await calculate();await saveDraft();render();})()`);
 const before=run('JSON.stringify(record)');await run('openAbsDistribution(0)');assert.equal(run('JSON.stringify(record)'),before);assert.match(element('#dialogbody').innerHTML,/Automatic ABS distribution/);assert.equal(run('absDistribution.draft.scheme'),'scheme-4');
 for(const key of ['crop','scheme','source','amount','remark'])element('#absd-'+key).value=run('absDistribution.draft.'+key);element('#absd-approved').checked=false;
 await run('previewAbsDistribution()');assert.equal(run('JSON.stringify(record)'),before);assert.equal(run('absDistribution.plan.ABS_CN'),'3000');assert.match(element('#dialogbody').innerHTML,/Apply split to draft/);
 await run('applyAbsDistribution()');assert.equal(run('record.allocations.length'),2);assert.equal(run("record.allocations.reduce((n,a)=>n+Number(a.amount),0)"),30000);assert.equal(run('result.CNs.find(c=>c.benefit==="ABS").rounded'),'3000');assert.equal(run('record.entries[0].date'),'2026-03-01');
 const id=run('record.id');await run(`openRecord(${JSON.stringify(id)})`);assert.equal(run('record.allocations.length'),2);assert.equal(run('record.allocations.every(a=>!!a.product)'),true);
 await run('openAbsDistribution(0)');run("record.party='Changed during preview'");run("absDistribution.plan={settings_version:state.settings.version}");await assert.rejects(run('applyAbsDistribution()'),/Calculation changed/);
 run("record.allocations[0].type='CD';record.allocations[0].product='';globalThis.beforeTypePreview=JSON.stringify(record)");await events.change({target:{dataset:{allocation:'0',key:'type'},type:'text',value:'ABS',closest:()=>null}});assert.equal(run('JSON.stringify(record)===beforeTypePreview'),true);assert.equal(run('absDistribution.record.allocations[0].type'),'ABS');

 // A slow response must never authorize a different amount entered during the wait.
 run("record.allocations[0].type='ABS'");
 await run('openAbsDistribution(0)');
 for(const key of ['crop','scheme','source','amount','remark'])element('#absd-'+key).value=run('absDistribution.draft.'+key);
 run("globalThis.realApi=api;api=(path,payload)=>path==='/api/abs-distribution-preview'?new Promise(resolve=>globalThis.releasePreview=resolve):realApi(path,payload)");
 const pending=run('previewAbsDistribution()');run("absDistribution.draft.amount='1';releasePreview({settings_version:state.settings.version})");
 await assert.rejects(pending,/Inputs changed/);assert.equal(run('absDistribution.plan'),null);run('api=realApi');
 // Apply must re-read fields even if a change event has not reached the handler yet.
 await run('openAbsDistribution(0)');for(const key of ['crop','scheme','source','amount','remark'])element('#absd-'+key).value=run('absDistribution.draft.'+key);
 await run('previewAbsDistribution()');element('#absd-amount').value='1';await assert.rejects(run('applyAbsDistribution()'),/preview the split again/);
 // Multiple eligible cash products require a visible choice; duplicate splits are excluded.
 run(`record.status='draft';record.cash_splits=[];globalThis.realChoices=allocationSchemes;globalThis.realSold=soldProductIds;globalThis.realCfg=calculationSettings;
 calculationSettings=()=>({products:[{id:'p1',name:'One'},{id:'p2',name:'Two'}],schemes:[{id:'cash',name:'Cash Scheme'}]});soldProductIds=()=>new Set(['p1','p2']);allocationSchemes=()=>[{id:'cash',name:'Cash Scheme',unit:'kg',products:['p1','p2'],cash:{products:['One','Two']}}];addCashSplit();`);
 assert.match(element('#dialogbody').innerHTML,/Choose Cash product and scheme/);assert.equal(run('record.cash_splits.length'),0);
 run("globalThis.oldRender=render;render=()=>{};commitCashSplit('cash','p2')");assert.equal(run('record.cash_splits[0].product'),'p2');assert.equal(run('cashSplitChoices().length'),1);assert.throws(()=>run("commitCashSplit('cash','p2')"),/choice changed/);
 run('render=oldRender;allocationSchemes=realChoices;soldProductIds=realSold;calculationSettings=realCfg');
 const frozen=run("record.status='issued';JSON.stringify(record)");await run('openAbsDistribution(0)');assert.equal(run('JSON.stringify(record)'),frozen);
 clearTimeout(run('saveTimer'));console.log('Automatic ABS UI: preview/cancel safety, single segment selection, product splits, save/reopen, original dates, stale preview and frozen guards passed.');
})().catch(e=>{console.error(e);process.exitCode=1});
