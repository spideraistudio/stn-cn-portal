// Model-level UI smoke. This is not a rendered/native-browser acceptance test.
const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict'),crypto=require('node:crypto');
const assets=__dirname+'/../backend/cn_web/calculator_static/';
const calls=[],els=new Map(),listeners={};
const storedParty={id:'canonical',revision:3,status:'finalised',party:'Saved party after restart',location:'Town',state:'Gujarat',season:'Kharif',entries:[{id:'voucher',date:'2026-05-01',items:[]}],allocations:[],cash_splits:[]};
const storedResult={issues:[],CNs:[],product_CNs:[],new_CN_total:'0',final_balance:'100',ledger_closing:'100'};
let openedResponse={record:storedParty,result:storedResult};
function el(k){if(!els.has(k))els.set(k,{innerHTML:'',textContent:'',dataset:{},style:{},classList:{toggle(){},add(){},remove(){}},querySelector(){return null},querySelectorAll(){return []},append(){},prepend(){},close(){},showModal(){}});return els.get(k);}
const user={username:'Synthetic',permissions:['view_workspace','edit_ledger','allocate_payments']};
const config={version:1,seasons:[],products:[],schemes:[]};
const state={project:{id:'a'.repeat(32),name:'My project'},projects:[{id:'a'.repeat(32),name:'My project'}],workbook:{id:'b'.repeat(32),name:'My workbook',state:'Gujarat'},workbooks:[{id:'b'.repeat(32),name:'My workbook'}],settings:config,records:[],bulk_history:[],deleted_workbooks:[]};
const stored=new Map([['cn-web-project',state.project.id],['cn-workbook-'+state.project.id,state.workbook.id]]);
const localStorage={getItem:k=>stored.get(k)||null,setItem:(k,v)=>stored.set(k,String(v)),removeItem:k=>stored.delete(k)};
const ctx={localStorage,console,crypto:crypto.webcrypto,structuredClone,URL,Headers,Blob,setTimeout,clearTimeout,location:{origin:'http://127.0.0.1:8787',assign(){}},confirm:()=>true,prompt:()=>null,document:{documentElement:{dataset:{}},getElementById:()=>null,querySelector:el,querySelectorAll:()=>[],createElement:()=>el('created'),addEventListener(t,f){(listeners[t]??=[]).push(f)}},fetch:async(url,options={})=>{calls.push({url,options});return {ok:true,json:async()=>url==='/api/me'?{user,csrf_token:'test-csrf'}:url==='/api/calculator/native-state'?structuredClone(state):url==='/api/calculator/record'?structuredClone(openedResponse):url==='/api/calculator/native-stale-result'?structuredClone(storedResult):url==='/api/calculator/print-record'?{record:structuredClone(storedParty),result:structuredClone(storedResult)}:{error:'unavailable test route'}};}};
ctx.CustomEvent=class {constructor(type,options){this.type=type;this.detail=options?.detail;}};ctx.document.dispatchEvent=()=>true;
ctx.window=ctx;ctx.addEventListener=()=>{};ctx.cnMountLedger=async(root,p,w,fn,section)=>{ctx.lastMount={p,w,section};};
vm.createContext(ctx);const run=s=>vm.runInContext(s,ctx);
for(const file of ['web-session.js','app.js','payment-workbench.js','cd-card-display.js','scheme-options.js','ui-theme.js','web-bridge.js'])run(fs.readFileSync(assets+file,'utf8'));
(async()=>{
 await new Promise(r=>setTimeout(r,30));
 assert.equal(run('activeProject'),state.project.id);assert.equal(run('activeWorkbook'),state.workbook.id);
 const first=calls.find(c=>c.url==='/api/calculator/native-state');assert.ok(first);
 assert.equal(first.options.headers.get('X-CN-Project'),state.project.id);assert.equal(first.options.headers.get('X-CN-Workbook'),state.workbook.id);
 await run("api('/api/ui-preferences?record_id=abc%3A%3Aclassic',undefined,true)");
 const pref=calls.findLast(c=>c.url==='/api/calculator/ui-preferences');assert.equal(pref.options.headers.get('X-CSRF-Token'),'test-csrf');assert.equal(pref.options.headers.get('X-CN-Record'),'abc::classic');
 await run("api('/api/import',{data:'synthetic'})");assert.ok(calls.some(c=>c.url==='/api/calculator/native-import'));
 for(const fn of ['bulkPage','auditPage','yearLinkPage','mappingSummary'])assert.doesNotMatch(run(fn+'.toString()'),/webLedgerPanel|cnMountLedger|web-ledger-panel/);
 run("page='Parties';render()");assert.match(el('#main').innerHTML,/party-search/);assert.doesNotMatch(el('#main').innerHTML,/Saved PDF parties|Saved statement/);
 run('record=null;globalThis.renderCalls=0;render=()=>{globalThis.renderCalls++}');await run("openRecord('canonical')");assert.equal(run('record.party'),storedParty.party);assert.equal(run('record.entries.length'),1);assert.equal(run('renderCalls'),1);
 openedResponse={record:{...storedParty,status:'draft',web_source:{ledger_id:'old'}},source_error:'Source changed'};run('record=null');await run("openRecord('canonical')");assert.equal(run('nativeStale.id'),'canonical');await run('calculate()');assert.ok(calls.some(c=>c.url==='/api/calculator/native-stale-result'));
 run('record=null;nativeStale=null');openedResponse={record:storedParty,result:storedResult};await run("openRecord('canonical')");ctx.printCalls=0;ctx.print=()=>ctx.printCalls++;await run('printCNSummary()');assert.equal(ctx.printCalls,1);assert.match(el('#print-summary').innerHTML,/Credit Note Summary/);
 console.log('PASS: native bootstrap, scoped authenticated transport, preserved offline page functions, canonical reopening/stale-result routing and canonical print. Real browser parity is checked separately.');
})().catch(e=>{console.error(e);process.exitCode=1});
