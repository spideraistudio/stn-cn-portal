// Executes the actual billing controller with a minimal DOM/HTTP harness.
// This is a controller regression, not browser/Windows acceptance.
const assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm');
const code=fs.readFileSync(__dirname+'/../backend/cn_web/calculator_static/billing-audit.js','utf8');
const handlers={},nodes={},calls=[];let html='',dialog='',row='',fail=false;
const cfg={revision:1,configuration:{rates:[]},products:[{id:'p',name:'Seed',packing_kg:'4'}],states:['Gujarat'],scheme_rates:[]};
const report={counts:{checked:1,attention:0},notes:[],warnings:[],rows:[]};
const context={activeProject:'p',activeWorkbook:'w',auditStart:'2026-04-01',auditEnd:'2027-03-31',auditDocuments:[],page:'Ledger Audit',esc:String,auditPage(){},modal(x){dialog=x;nodes.modal={close(){}}},toast(){},document:{getElementById(id){return nodes[id]},createElement(){return {remove(){},set innerHTML(v){html=v}}},addEventListener(type,fn){handlers[type]=fn},querySelectorAll(){return [{querySelectorAll(){return [{dataset:{br:'state'},value:'Gujarat'},{dataset:{br:'unit'},value:'kg'},{dataset:{br:'rate'},value:'300'}]}}]}},async api(path,data){calls.push([path,data]);if(path.includes('config')||path.includes('rates'))return structuredClone(cfg);if(fail)throw Error('synthetic recheck failure');return report;}};
nodes.main={append(n){nodes['billing-audit-panel']=n}};
vm.createContext(context);vm.runInContext(code,context);context.auditPage();
const click=async id=>{const b={id,disabled:false,hasAttribute(){return false}};await handlers.click({target:{closest(){return b}}});};
(async()=>{
 await click('billing-rates');assert.match(dialog,/Enter a new state/);assert.match(dialog,/Save approved rates and recheck/);
 nodes['br-state']={value:'Gujarat'};nodes['br-rows']={insertAdjacentHTML(_,v){row=v}};
 await click('br-add');assert.match(row,/<option value="">Choose unit/);assert.doesNotMatch(row,/value="packet" selected/);
 await click('br-save');assert.equal(calls.at(-2)[0],'/api/native-billing-rates');assert.equal(calls.at(-1)[0],'/api/native-billing-run');assert.match(html,/saved and audit rechecked/);
 fail=true;await click('br-save');assert.match(html,/Saved changes remain saved/);assert.match(html,/synthetic recheck failure/);assert.doesNotMatch(html,/1 lines checked/);
 console.log('PASS: explicit units, saved-state/new-state controls, save then recheck, saved-but-recheck-failed state and stale report cleared.');
})().catch(e=>{console.error(e);process.exitCode=1});
