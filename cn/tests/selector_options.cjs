// Production selector logic exercised with a small DOM model; Windows visual acceptance remains pending.
const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
class Element{
 constructor(){this.children=[];this._value='';this.disabled=false;this.dataset={};}
 replaceChildren(){this.children=[];this._value='';}
 append(e){this.children.push(e);if(this.children.length===1)this._value=e.value;}
 get options(){return this.children;}
 get value(){return this._value;}
 set value(v){this._value=this.children.some(x=>x.value===v)?v:'';}
}
for(const file of ['static/ledger.js','calculator_static/ledger-panel.js']){
 const source=fs.readFileSync(__dirname+'/../backend/cn_web/'+file,'utf8');
 const els=new Map();const get=k=>{if(!els.has(k))els.set(k,new Element());return els.get(k)};
 const ctx={console,document:{createElement:()=>({value:'',textContent:''})},$:get,state:{ledgers:[]},yearPending:null,can:()=>true};vm.createContext(ctx);
 vm.runInContext(source.slice(source.indexOf('function option('),source.indexOf('function emptyHelp(')),ctx);
 const run=s=>vm.runInContext(s,ctx);
 run("option($('#ledger'),[],r=>r.name,'','Import a statement first');selectionStatus();yearOptions()");
 assert.equal(get('#ledger').disabled,true);assert.match(get('#ledger').options[0].textContent,/Import/);assert.equal(get('#summary-button').disabled,true);
 const rows=[{id:'old',party:'Party A',report_period:['2025-04-01','2026-03-31']},{id:'now',party:'Party A',report_period:['2026-04-01','2026-10-20']},{id:'partial',party:'Party B',report_period:['2025-04-01','2025-10-20']},{id:'obsolete',party:'Old',report_period:['2025-04-01','2026-03-31'],superseded_by:'old'}];ctx.state.ledgers=rows;
 run('yearOptions()');assert.equal(get('#previous-year').value,'');assert.deepEqual(get('#previous-year').options.map(r=>r.value),['','old']);
 get('#previous-year').value='old';run('yearOptions()');assert.deepEqual(get('#current-year').options.map(r=>r.value),['','now']);assert.equal(get('#year-form button').disabled,true);
 get('#current-year').value='now';run('yearOptions()');assert.equal(get('#year-form button').disabled,false);assert.equal(get('#current-year').value,'now');
 ctx.state.ledgers=[rows[0]];run('yearOptions()');assert.equal(get('#current-year').disabled,true);assert.equal(get('#current-year').value,'');assert.equal(get('#year-form button').disabled,true);
 run("option($('#workbook'),[{id:'a',name:'A'},{id:'b',name:'B'}],r=>r.name,'b')");assert.equal(get('#workbook').value,'b');
 run("option($('#workbook'),[{id:'a',name:'A'},{id:'b',name:'B'}],r=>r.name,$('#workbook').value)");assert.equal(get('#workbook').value,'b');
 run("option($('#season'),[{name:'Kharif'},{name:'Rabi'}],r=>r.name,'Rabi');option($('#ledger'),[{id:'now',name:'Statement'}],r=>r.name);selectionStatus()");assert.equal(get('#season').value,'Rabi');assert.equal(get('#summary-button').disabled,false);
 run('clearYearPreview()');assert.equal(get('#year-apply').hidden,true);assert.equal(ctx.yearPending,null);
 console.log('PASS '+file+': empty lists, saved workbook/season, distinct April–March pair, partial current year, replaced source exclusion, stale preview reset.');
}
