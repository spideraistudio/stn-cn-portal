// Restore/run against a separate DB before calling; no writes to uploaded backup.
const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict'),crypto=require('node:crypto');
const backup=JSON.parse(fs.readFileSync(process.env.CN_ACCEPTANCE_BACKUP,'utf8'));
const elements=new Map(),events={};function element(key){if(!elements.has(key))elements.set(key,{innerHTML:'',textContent:'',style:{},querySelectorAll:()=>[],showModal(){this.open=true},close(){this.open=false}});return elements.get(key);}
(async()=>{let tested=0;for(const workbook of backup.workbooks){if(workbook.metadata.deleted_at)continue;const rows=workbook.backup.records.map(r=>JSON.parse(r.data));const cases=rows.filter(r=>r.selected_party_id&&!r.entries.length&&rows.some(p=>p.id===r.selected_party_id&&p.entries.length));if(!cases.length)continue;
 const ctx={console,structuredClone,crypto:crypto.webcrypto,fetch:(url,opts)=>fetch('http://127.0.0.1:18766'+url,opts),setTimeout,clearTimeout,Blob,URL,window:{print(){}},localStorage:{getItem:()=>workbook.metadata.id,setItem(){},removeItem(){}},confirm:()=>true,prompt:()=>null,document:{querySelector:element,querySelectorAll:()=>[],createElement:()=>({click(){}}),addEventListener:(type,fn)=>events[type]=fn}};vm.createContext(ctx);vm.runInContext(fs.readFileSync(__dirname+'/../static/app.js','utf8'),ctx);
 for(let i=0;i<200&&!vm.runInContext('Boolean(state)',ctx);i++)await new Promise(r=>setTimeout(r,25));
 for(const empty of cases){ctx.expectedParty=empty.party;ctx.expectedId=empty.selected_party_id;ctx.emptyId=empty.id;const expected=rows.find(r=>r.id===empty.selected_party_id);vm.runInContext("globalThis.selectedGroup=partyList().find(p=>p.calculations.some(r=>r.id===expectedId))",ctx);assert.equal(vm.runInContext('selectedGroup.entries.length',ctx),expected.entries.length);assert.match(vm.runInContext('partyRows([selectedGroup],false)',ctx),/Open Party \/ Ledger/);
 await events.click({target:{closest:()=>({dataset:{open:vm.runInContext('selectedGroup.id',ctx)}})}});assert.equal(vm.runInContext('record.entries.length',ctx),expected.entries.length);assert.equal(vm.runInContext('step',ctx),1);assert.match(element('#main').innerHTML,/Check Ledger/);assert.match(element('#main').innerHTML,/Original source voucher and lines/);
 await vm.runInContext('openRecord(emptyId)',ctx);assert.match(element('#main').innerHTML,/name\/address-only draft/);assert.match(element('#main').innerHTML,/Open saved ledger/);
 await events.change({target:{id:'saved-party',value:expected.id,dataset:{}}});assert.equal(vm.runInContext('record.entries.length',ctx),expected.entries.length);assert.equal(vm.runInContext('step',ctx),1);tested++;
 }
 }
 assert.ok(tested>=1);console.log('Actual backup navigation: '+tested+' empty/name-only versus imported ledger cases passed; default opens stored vouchers and Check Ledger.');
})().catch(e=>{console.error(e);process.exitCode=1});
