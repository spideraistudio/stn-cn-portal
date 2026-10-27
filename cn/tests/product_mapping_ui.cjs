// Exercise production mapping rendering with a DOM model, not Windows rendering.
const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
class Element {
 constructor(tag){this.tagName=tag;this.children=[];this.value='';this.textContent='';}
 append(...nodes){this.children.push(...nodes);}
 setAttribute(key,value){this[key]=value;}
}
for(const file of ['static/ledger.js','calculator_static/ledger-panel.js']){
 const source=fs.readFileSync(__dirname+'/../backend/cn_web/'+file,'utf8');
 const body=source.slice(source.indexOf('function mappingGroups('),source.indexOf('async function loadLedger('));
 for(const rights of [[],['edit_ledger'],['edit_ledger','edit_schemes']]){
  const root=new Element('div'),buttons=[],tables=[],selects=[];
  const ctx={document:{createElement:t=>new Element(t)},$:()=>root,can:p=>rights.includes(p),
   selected:{mappings:{'0:0':'one','1:0':'one'}},identityEditor:()=>({read:()=>({})}),state:{catalogue:[{id:'one',name:'DAWAT 1 kg',crop:'Paddy',segment:'1 kg',packing_kg:'1'},{id:'three',name:'DAWAT 3 kg',crop:'Paddy',segment:'3 kg',packing_kg:'3'}]},
   para:(t,s)=>t.append(s),button:(label,fn,disabled)=>{const b={label,fn,disabled};buttons.push(b);return b;},
   selectField:(label,values,current)=>{const select={values,value:current};selects.push(select);return [select,select]},
   input:(label,type,value)=>[label,{value}],table:(t,headers,rows)=>tables.push({headers,rows})};
  vm.createContext(ctx);vm.runInContext(body,ctx);
  const item=(name,pack,product)=>({name,unit:'packet',rate:'100.00',product,mapping_suggestion:{detected_packing_kg:pack}});
  ctx.doc={entries:[{items:[item('DAWAT 1 kg','1','one')]},{items:[item('DAWAT 1 kg','1','one')]},{items:[item('DAWAT 3 kg','3',null)]},{items:[item('<new printed product>',null,null)]}]};
  vm.runInContext("renderProductMappings(doc,{'2:0':{product_id:'three',reason:'Recognised workbook product'}})",ctx);
  assert.equal(tables[0].rows.length,3);assert.equal(tables[0].rows[0][4].open,false);assert.equal(tables[0].rows[1][4].open,true);
  assert.match(tables[0].rows[0][0],/2 items/);assert.match(tables[0].rows[2][0],/<new printed product>/);
  assert.equal(selects[0].values.length,2); // only compatible packing
  assert.equal(selects[1].value,'three');
  assert.equal(buttons.some(b=>b.label==='Create product and save mapping'),rights.includes('edit_schemes'));
  assert.equal(buttons.find(b=>b.label.includes('Reuse')).disabled,!rights.includes('edit_ledger'));
  assert.equal(selects[0].disabled,!rights.includes('edit_ledger'));
 }
 console.log('PASS '+file+': grouped repeated names, separate packing, recognised status, safe text, and mapping/creation permissions.');
}
