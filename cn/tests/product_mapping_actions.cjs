// Production button callbacks, fields, validation and adjacent errors.
const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
class Element{
 constructor(tag){this.tagName=tag;this.children=[];this.value='';this.attributes={};this.listeners={};this.classList={add(){},remove(){},toggle(){}};}
 append(...items){this.children.push(...items);}
 replaceChildren(){this.children=[];}
 setAttribute(k,v){this.attributes[k]=v;}
 addEventListener(k,fn){this.listeners[k]=fn;}
 focus(){this.focused=true;}
 scrollIntoView(){this.scrolled=true;}
}
const walk=node=>[node,...(node.children||[]).filter(x=>x&&typeof x==='object').flatMap(walk)];
(async()=>{
 for(const file of ['static/ledger.js','calculator_static/ledger-panel.js']){
  const source=fs.readFileSync(__dirname+'/../backend/cn_web/'+file,'utf8');
  const root=new Element('div'),noticeNode=new Element('div'),requests=[];let loads=0,reject=false;
  const ctx={root,document:{createElement:t=>new Element(t),body:new Element('body')},$:s=>s==='#notice'?noticeNode:root,
   state:{revision:7,catalogue:[],crops:['Maize'],segments:{Maize:['Single Cross']}},selected:{id:'saved-ledger',mappings:{}},can:()=>true,
   notice:s=>{noticeNode.textContent=s},endpoint:a=>a,
   api:async(path,data)=>{requests.push({path,data});if(reject)throw Error('Source packing differs from this product.');return {revision:8}},
   load:async()=>{loads++},table:(target,headers,rows)=>{for(const row of rows)for(const cell of row)if(cell instanceof Element)target.append(cell)}};
  vm.createContext(ctx);
  vm.runInContext(source.slice(source.indexOf('let running=false;'),source.indexOf('function option(')),ctx);
  for(const [start,end]of [['function para(', 'function table('],['function input(', 'const can='],['function identityEditor(', 'async function loadLedger(']])vm.runInContext(source.slice(source.indexOf(start),source.indexOf(end)),ctx);
  vm.runInContext("renderProductMappings({entries:[{items:[{name:'NEW BRAND',unit:'packet',rate:'100',product:null,mapping_suggestion:{detected_packing_kg:null}}]}]}, {})",ctx);
  const nodes=walk(root),create=nodes.find(n=>n.textContent==='Create product and save mapping');
  assert.ok(create);const select=nodes.find(n=>n.tagName==='select');assert.equal(select.disabled,true);
  assert.equal(select.children[0].textContent,'No saved products in this workbook');
  const fields=nodes.filter(n=>n.tagName==='input');assert.equal(fields.length,3);
  await create.listeners.click({preventDefault(){}});assert.equal(requests.length,0);
  assert.match(nodes.find(n=>n.attributes.role==='alert').textContent,/crop/);
  const selectors=nodes.filter(n=>n.tagName==='select');selectors[1].value='Maize';selectors[1].listeners.change();selectors[2].value='Single Cross';fields[2].value='4';
  await create.listeners.click({preventDefault(){}});assert.equal(requests.length,1);assert.equal(loads,1);
  assert.deepEqual(JSON.parse(JSON.stringify(requests[0])),{path:'mapping',data:{revision:7,ledger_id:'saved-ledger',entry_index:0,item_index:0,same_name:true,new_product:{name:'NEW BRAND',crop:'Maize',segment:'Single Cross',packing_kg:'4'}}});
  assert.match(noticeNode.textContent,/saved/);
  assert.deepEqual(selectors[2].children.map(x=>x.value),['Awaiting scheme','Single Cross']);
  selectors[2].value='Awaiting scheme';await create.listeners.click({preventDefault(){}});
  assert.equal(requests.at(-1).data.new_product.segment,'Awaiting scheme');
  selectors[1].value='__new__';selectors[1].listeners.change();fields[1].value='  maize  ';
  await create.listeners.click({preventDefault(){}});assert.equal(requests.at(-1).data.new_product.crop,'Maize');
  reject=true;await create.listeners.click({preventDefault(){}});
  const error=nodes.find(n=>n.attributes.role==='alert');assert.match(error.textContent,/packing differs/);assert.equal(error.scrolled,true);
  console.log('PASS '+file+': empty catalogue guidance; create/save click posts confirmed fields; missing fields block and focus; server errors visible beside action; saved crop/segment choices, optional segment and canonical crop names.');
 }
})().catch(e=>{console.error(e);process.exitCode=1});
