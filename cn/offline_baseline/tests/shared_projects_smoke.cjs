// UI templates and scope-reset controls, backed by a real isolated HTTP server.
const vm=require('node:vm'),fs=require('node:fs'),crypto=require('node:crypto'),assert=require('node:assert/strict');
const elements=new Map(),events={},headers=[];
function element(k){if(!elements.has(k))elements.set(k,{innerHTML:'',textContent:'',value:'',style:{},querySelectorAll:()=>[],showModal(){},close(){}});return elements.get(k)}
const context={console,structuredClone,crypto:crypto.webcrypto,fetch:(url,opt)=>{headers.push({url,...opt.headers});return fetch('http://127.0.0.1:8765'+url,opt)},setTimeout,clearTimeout,Blob,URL,btoa,atob,window:{print(){}},confirm:()=>true,prompt:()=>null,document:{querySelector:element,querySelectorAll:()=>[],createElement:()=>({click(){}}),addEventListener:(type,fn)=>events[type]=fn}};
vm.createContext(context);vm.runInContext(fs.readFileSync(__dirname+'/../static/app.js','utf8'),context);const run=s=>vm.runInContext(s,context);
(async()=>{
 for(let n=0;n<100&&!element('#main').innerHTML;n++)await new Promise(r=>setTimeout(r,10));
 await run("refresh()");assert.equal(run('activeProject'),'main');assert.match(element('#nav').innerHTML,/Working project/);
 await run("(async()=>{if(apiBusy)throw Error('busy');record=blank();record.party='Shared UI Owner';record=await api('/api/save',record);await refresh();})()");
 await run('exportSharedPreview()');assert.match(element('#dialogbody').innerHTML,/Review editable project export/);assert.match(element('#dialogbody').innerHTML,/deleted records/);
 const bundle=await run("api('/api/project-export',{confirm:true,expected:sharedExportPending.sha256,name:'UI Received Project',sender:'User One'})");context.bundle=bundle;
 await run("previewSharedImport({size:bundle.data.length*.75,arrayBuffer:async()=>Uint8Array.from(atob(bundle.data),c=>c.charCodeAt(0)).buffer})");assert.match(element('#dialogbody').innerHTML,/User One/);assert.match(element('#dialogbody').innerHTML,/Open New Separate Copy/);
 await run("auditDocuments=[{party:'Old audit'}];auditReport={old:true};yearPrevious=[{party:'Old previous'}];yearLoadResults=[{filename:'Old file'}];reportFilters={party:'Old filter'};territoryFilters={party:'Old filter'}");
 await run("sharedClick({dataset:{sharedAction:'receive'}})");const received=run('activeProject');assert.notEqual(received,'main');assert.equal(run('auditDocuments.length'),0);assert.equal(run('yearPrevious.length'),0);assert.equal(run('yearLoadResults.length'),0);assert.equal(run('Object.keys(reportFilters).length'),0);assert.match(element('#nav').innerHTML,/Received · UI Received Project/);
 await run("(async()=>{record=state.records.find(r=>r.party==='Shared UI Owner');record.party='Receiver changes';record=await api('/api/save',record);await refresh();})()");
 await run("switchProject('main')");assert.equal(run("state.records.some(r=>r.party==='Receiver changes')"),false);assert.equal(run("state.records.some(r=>r.party==='Shared UI Owner')"),true);assert.equal(run('record'),null);
 await run("(async()=>{page='Settings';settingsSection='storage';settingsPage();await scanStorage();})()");assert.match(element('#main').innerHTML,/Storage &amp; Permanent Delete/);assert.match(element('#storage-results').innerHTML,/Optional: retained safety backups/);
 assert(headers.some(h=>h['X-CN-Project']===received));assert(headers.some(h=>h['X-CN-Project']==='main'));
 await run("(async()=>{const r=state.records.find(r=>r.party==='Shared UI Owner');const p=await api('/api/party-delete',{id:r.id});await api('/api/party-delete',{id:r.id,confirm:true,expected:p.expected});await refresh();await scanStorage();})()");assert.match(element('#purge-items').innerHTML,/Shared UI Owner/);assert.match(element('#purge-items').innerHTML,/Permanently Delete/);
 await run("sharedClick({dataset:{purgeKind:'party',purgeId:state.records.find(r=>r.party==='Shared UI Owner').id}})");assert.match(element('#dialogbody').innerHTML,/Type Shared UI Owner to confirm/);element('#purge-typed-name').value='Shared UI Owner';await run("sharedClick({dataset:{sharedAction:'purge'}})");assert.equal(run("state.records.some(r=>r.party==='Shared UI Owner')"),false);
 const receiver=await fetch('http://127.0.0.1:8765/api/state',{headers:{'X-CN-Project':received}}).then(r=>r.json());assert(receiver.records.some(r=>r.party==='Receiver changes'));
 clearTimeout(run('saveTimer'));console.log('Shared projects UI/API: editable export, preview, independent copy, per-request project headers, transient view reset, return to My Work, storage scan and typed permanent party deletion passed.');
})().catch(e=>{console.error(e);process.exitCode=1});
