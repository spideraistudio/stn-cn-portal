// Payment Studio: real API, isolated test store, UI event/template checks.
const vm=require('node:vm'),fs=require('node:fs'),crypto=require('node:crypto'),assert=require('node:assert/strict');
const elements=new Map(),events={};function element(k){if(!elements.has(k))elements.set(k,{innerHTML:'',textContent:'',style:{},querySelectorAll:()=>[],showModal(){},close(){}});return elements.get(k)}
const context={console,structuredClone,crypto:crypto.webcrypto,fetch:(url,opt)=>fetch('http://127.0.0.1:8765'+url,opt),setTimeout,clearTimeout,Blob,URL,window:{print(){}},confirm:()=>true,prompt:()=>null,document:{querySelector:element,querySelectorAll:()=>[],createElement:()=>({click(){}}),addEventListener:(type,fn)=>events[type]=fn}};
vm.createContext(context);vm.runInContext(fs.readFileSync(__dirname+'/../static/app.js','utf8'),context);
const run=s=>vm.runInContext(s,context);
const click=dataset=>events.click({target:{closest:()=>({dataset})}});
(async()=>{
 for(let n=0;n<100&&!element('#main').innerHTML;n++)await new Promise(r=>setTimeout(r,10));
 await run(`(async()=>{for(const sc of state.settings.schemes)if(sc.benefits.includes('ABS')){sc.abs_start='2026-01-01';sc.abs_end='2026-03-31';sc.extended_end=null;}state.settings=await api('/api/settings',state.settings);record=blank();record.party='ABS regression';const p=state.settings.products.find(p=>p.scheme==='scheme-3');record.entries=[{id:'july',date:'2026-07-10',original:{date:'2026-07-10'},kind:'receipt',credit:'1000',debit:'0',reference:'July receipt'},{id:'march',date:'2026-03-31',kind:'receipt',credit:'1000',debit:'0',reference:'March receipt'},{id:'sale',date:'2026-05-01',kind:'sale',credit:'0',debit:'2000',items:[{product:p.id,name:p.name,qty:'10',unit:'packet',amount:'2000'}]}];record.closing='0';record.allocations=[{id:'july-cd',source:'july',type:'CD',scheme:'scheme-3',amount:'1000',remark:''}];step=2;page='Calculate CN';await calculate();})()`);
 const edit=async(key,value,index='0')=>{const t={dataset:{allocation:index,key},type:'text',value,closest:()=>null};await events.change({target:t});return t;};
 await edit('type','ABS');assert.equal(run('record.allocations[0].type'),'CD');assert.match(element('#toast').textContent,/ABS not allowed/);
 await run("addDestinationAllocation('scheme-3','ABS')");assert.equal(run('record.allocations[1].source'),'march');assert.equal(run('record.allocations[1].amount'),'0');
 await edit('source','july','1');assert.equal(run('record.allocations[1].source'),'march');
 await edit('product',run("state.settings.schemes.find(s=>s.id==='scheme-3').products[0]"),'1');await edit('amount','500','1');assert.equal(run('record.allocations[1].amount'),'500');
 assert.equal(run("absSourceAllowed(result.sources.find(s=>s.id==='july'),calculationSettings().schemes.find(s=>s.id==='scheme-3'))"),false);
 assert.match(run('allocationRow(record.allocations[1],1)'),/<option disabled value="july"/);
 await run('saveDraft()');const saved=run('record.id');await run(`openRecord(${JSON.stringify(saved)})`);assert.equal(run('record.allocations[1].source'),'march');
 const denied=await run(`(async()=>{const bad=structuredClone(record);bad.allocations[0].type='ABS';try{await api('/api/save',bad);return false;}catch(e){return /ABS not allowed/.test(e.message);}})()`);assert.equal(denied,true);
 run("record.allocations=[];record.entries=record.entries.filter(e=>e.id!=='march')");await run('calculate()');const before=run('JSON.stringify(record)');
 await assert.rejects(run("addDestinationAllocation('scheme-3','ABS')"),/No receipt is eligible/);assert.equal(run('JSON.stringify(record)'),before);
 clearTimeout(run('saveTimer'));console.log('ABS regression: July type/source/add blocked, March selected, disabled receipt option, zero row safety, save/reopen and independent server rejection passed.');
})().catch(e=>{console.error(e);process.exitCode=1});
