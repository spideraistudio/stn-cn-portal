"use strict";
window.cnMountLedger=async function(root,projectId,workbookId,onOpen,section,options={}){
root.inert=true;
root.innerHTML="<div id=\"notice\" role=\"status\" aria-live=\"polite\"></div><section class=\"card\"><div class=\"inline-form\"><label>Project<select id=\"project\"></select></label><label>Workbook<select id=\"workbook\"></select></label><button id=\"reload\" type=\"button\">Reload</button></div><p>Create projects/workbooks in <a href=\"/workspace\">My workspace</a>. PDF processing uses this workbook's own catalogue and periods.</p></section><section class=\"card\"><h2>1 \u00b7 Working periods</h2><div id=\"period-list\"></div><form id=\"period-form\" class=\"inline-form\"><label>Season name<input name=\"name\" placeholder=\"Rabi 2026\u201327\" required maxlength=\"100\"></label><label>Start<input name=\"start\" type=\"date\" required></label><label>End<input name=\"end\" type=\"date\" required></label><label>Calculation cutoff<input name=\"cutoff\" type=\"date\" required></label><button>Add period</button></form><p>Cutoff allows reviewed late IPT. Receipt dates stay as printed in the statement.</p></section><section class=\"card\"><h2>2 \u00b7 Products & packing</h2><div id=\"catalogue-list\" class=\"tablewrap\"></div><form id=\"product-form\" class=\"inline-form\"><label>Product<input name=\"name\" placeholder=\"DAWAT 1 kg\" required></label><label>Crop<input name=\"crop\" required></label><label>Segment<input name=\"segment\" required></label><label>Packet weight (kg)<input name=\"packing_kg\" type=\"number\" min=\"0.000001\" step=\"any\" required></label><label>Other printed names (one per line)<textarea name=\"aliases\" rows=\"2\"></textarea></label><button>Add product</button></form><p>Product/packing changes require Edit schemes. Mapping to an existing product requires Edit ledger.</p></section><section class=\"card\"><h2>3 \u00b7 Import statements</h2><form id=\"import-form\"><label>Single, combined-party or multiple PDFs<input id=\"pdfs\" type=\"file\" accept=\"application/pdf,.pdf\" multiple required></label><button id=\"preview-button\">Preview import</button></form><progress id=\"progress\" max=\"100\" value=\"0\" hidden></progress><p id=\"progress-label\"></p><div id=\"import-preview\"></div><label>Reason for replacing a changed statement<input id=\"replace-reason\" maxlength=\"500\"></label><button id=\"apply-import\" type=\"button\" hidden>Apply reviewed import</button><button id=\"cancel-import\" type=\"button\" class=\"secondary\" hidden>Cancel preview</button><p>Preview saves nothing. Applying a batch saves every valid ledger and its source file together. A changed statement needs an explicit replacement choice; earlier history remains saved.</p></section><section class=\"card\"><h2>4 \u00b7 Parties & ledger review</h2><label>Saved statement<select id=\"ledger\"></select></label><label>Working season<select id=\"season\"></select></label><button id=\"summary-button\" type=\"button\">Check season stock</button><button id=\"reread-button\" type=\"button\" class=\"secondary\">Re-read saved PDF</button><div id=\"ledger-summary\"></div><div id=\"stock-summary\"></div><div id=\"entries\" class=\"tablewrap\"></div></section><section class=\"card\"><h2>5 \u00b7 Ledger audit</h2><form id=\"audit-form\" class=\"inline-form\"><label>From<input name=\"start\" type=\"date\" required></label><label>To<input name=\"end\" type=\"date\" required></label><button>Run workbook audit</button></form><p>Audit checks active statements across the workbook by posting date. Choose a category to see its findings. Season stock review above uses your explicit season decisions.</p><div id=\"audit-categories\"></div><div id=\"audit-results\"></div><div id=\"posted-cns\"></div></section><section class=\"card\"><h2>6 \u00b7 April\u2013March Year Link</h2><form id=\"year-form\"><div class=\"inline-form\"><label>Previous full financial year<select id=\"previous-year\"></select></label><label>Current financial year<select id=\"current-year\"></select></label><label>Identity/location review note (if different)<input name=\"identity_reason\" maxlength=\"500\"></label></div><button>Review year link</button></form><div id=\"year-preview\"></div><label>Reconciliation note<input id=\"year-reason\" maxlength=\"500\"></label><button id=\"year-apply\" type=\"button\" hidden>Save confirmed remaining receipt amounts</button><div id=\"saved-links\"></div></section>";
'use strict';
const $=s=>root.querySelector(s);let csrf='',user=null,state=null,workbook='',selected=null,pending=null,yearPending=null;
function notice(s,error=false){$('#notice').textContent=s;$('#notice').classList.toggle('error',error)}
async function api(path,data,method=data===undefined?'GET':'POST'){const r=await fetch(path,{method,credentials:'same-origin',headers:data===undefined?{}:{'Content-Type':'application/json','X-CSRF-Token':csrf},body:data===undefined?undefined:JSON.stringify(data)});const d=await r.json();if(!r.ok)throw Error(d.error||'Request failed');if(method!=='GET'&&/\/(mapping|resolve-mappings|review|config|apply-import|year-apply)$/.test(path)){window.cnSourceChanged?.(workbook);await options.onChanged?.();}return d}
function endpoint(action='',w=workbook){if(!w)throw Error('Choose a workbook first');return '/api/ledger/workbooks/'+w+(action?'/'+action:'')}
let running=false;
function run(fn){return async event=>{event?.preventDefault();if(running){notice('Please wait for the current operation to finish, then choose again.');return;}running=true;root.inert=true;root.classList.add('busy');try{await fn(event)}catch(e){notice(e.message,true)}finally{running=false;root.inert=false;root.classList.remove('busy')}}}
function option(select,rows,label,old='',empty='No saved options yet',prompt=''){
 select.replaceChildren();
 if(!rows.length||prompt){const o=document.createElement('option');o.value='';o.textContent=rows.length?prompt:empty;select.append(o)}
 for(const r of rows){const o=document.createElement('option');o.value=r.id??r.name;o.textContent=label(r);select.append(o)}
 select.disabled=!rows.length;
 if(old&&[...select.options].some(x=>x.value===old))select.value=old;
}
function clearYearPreview(){yearPending=null;$('#year-apply').hidden=true;$('#year-preview').replaceChildren()}
function yearOptions(){
 const rows=(state?.ledgers||[]).filter(r=>!r.superseded_by);
 const label=r=>r.party+' · '+r.report_period.join(' → ');
 const full=rows.filter(r=>{const [a,b]=r.report_period;return /^\d{4}-04-01$/.test(a)&&b===String(Number(a.slice(0,4))+1)+'-03-31'});
 option($('#previous-year'),full,label,$('#previous-year').value,'Import a full April–March statement first','Choose previous full financial year');
 const prev=full.find(r=>r.id===$('#previous-year').value);
 const current=rows.filter(r=>{const [a,b]=r.report_period;return r.id!==prev?.id&&/^\d{4}-04-01$/.test(a)&&a<=b&&b<=String(Number(a.slice(0,4))+1)+'-03-31'&&(!prev||a===String(Number(prev.report_period[1].slice(0,4)))+'-04-01')});
 option($('#current-year'),current,label,$('#current-year').value,'Import the following financial-year statement first','Choose current financial year');
 $('#year-form button').disabled=!$('#previous-year').value||!$('#current-year').value;
}
function selectionStatus(){
 $('#summary-button').disabled=!$('#ledger').value||!$('#season').value;
 $('#reread-button').disabled=!$('#ledger').value||!can('import_statements');
 for(const id of ['#product-form button','#period-form button','#preview-button'])$(id).disabled=!state||!can(id==='#product-form button'?'edit_schemes':id==='#preview-button'?'import_statements':'edit_ledger')||(id==='#preview-button'&&!can('edit_ledger'));
 $('#audit-form button').disabled=!state;
}
function emptyHelp(){
 let box=$('#selection-help');if(!box){box=document.createElement('p');box.id='selection-help';$('#notice').after(box)}
 box.textContent=!workbook?'Create a project and workbook in Projects & workbooks.':!state?'':[
 !state.periods.length?'Working season is empty: add a working period with its dates in Parties → Bulk Import PDFs.':'',
 !state.ledgers.some(r=>!r.superseded_by)?'Saved statement is empty: use Parties → Bulk Import PDFs to preview and apply PDFs in this workbook.':'',
 'Year Link uses two saved statements in this workbook: a full previous April–March year and the following year (which may be partial).'
 ].filter(Boolean).join(' ');
}

function para(target,message){const p=document.createElement('p');p.textContent=message;target.append(p);return p}
function button(label,fn,disabled=false){const b=document.createElement('button');b.type='button';b.className='secondary';b.textContent=label;b.disabled=disabled;b.addEventListener('click',run(fn));return b}
function table(target,headers,rows){const t=document.createElement('table'),head=document.createElement('thead'),tr=document.createElement('tr');for(const label of headers){const th=document.createElement('th');th.textContent=label;tr.append(th)}head.append(tr);t.append(head);const body=document.createElement('tbody');for(const row of rows){const tr=document.createElement('tr');for(const val of row){const td=document.createElement('td');if(val instanceof Node)td.append(val);else td.textContent=val??'—';tr.append(td)}body.append(tr)}t.append(body);target.append(t)}
function input(label,type='text',value=''){const l=document.createElement('label');l.textContent=label;const i=document.createElement('input');i.type=type;i.value=value;l.append(i);return [l,i]}
function selectField(label,values,current=''){const l=document.createElement('label');l.textContent=label;const s=document.createElement('select');for(const [value,caption]of values){const o=document.createElement('option');o.value=value;o.textContent=caption;s.append(o)}s.value=current;l.append(s);return [l,s]}
const can=p=>user?.permissions.includes(p);
function clearPreview(){pending=null;$('#import-preview').replaceChildren();$('#apply-import').hidden=true;$('#cancel-import').hidden=true}
async function init(){const me=await api('/api/me');user=me.user;csrf=me.csrf_token;const projects=(await api('/api/data/projects')).items.filter(r=>r.id===projectId);option($('#project'),projects,r=>r.data.name,projectId);await loadBooks()}
async function loadBooks(){const rows=(await api('/api/data/workbooks')).items.filter(r=>r.project===$('#project').value&&r.id===workbookId);option($('#workbook'),rows,r=>r.data.name,$('#workbook').value||workbookId,'No workbooks — create one in Projects & workbooks');await load()}
async function load(selection={}){workbook=$('#workbook').value;clearPreview();yearPending=null;$('#year-apply').hidden=true;$('#year-preview').replaceChildren();$('#audit-categories').replaceChildren();$('#audit-results').replaceChildren();$('#posted-cns').replaceChildren();$('#stock-summary').replaceChildren();if(!workbook){state=null;selected=null;for(const id of ['#ledger','#season','#previous-year','#current-year'])option($(id),[],r=>r.name);for(const id of ['#entries','#ledger-summary','#period-list','#catalogue-list','#saved-links'])$(id).replaceChildren();selectionStatus();emptyHelp();notice('Create a project and workbook in My workspace to begin.');return}state=await api(endpoint());configureProductForm();$('#period-list').replaceChildren();for(const p of state.periods)para($('#period-list'),p.name+' · '+p.start+' → '+p.end+' · cutoff '+p.cutoff);$('#catalogue-list').replaceChildren();table($('#catalogue-list'),['Product','Crop','Segment','kg / packet'],state.catalogue.map(p=>[p.name,p.crop,p.segment,p.packing_kg]));option($('#season'),state.periods,p=>p.name,$('#season').value,'No working periods — add one below');const rows=state.ledgers.filter(r=>!r.superseded_by);option($('#ledger'),rows,r=>r.party+' · '+r.report_period.join(' → ')+' · '+r.entries+' entries',selection.ledgerId||$('#ledger').value,'No saved statements — apply a PDF import first');yearOptions();selectionStatus();emptyHelp();$('#saved-links').replaceChildren();for(const [lid,link]of Object.entries(state.year_links))para($('#saved-links'),lid.slice(0,6)+' · '+(link.stale?'SOURCE CHANGED — review link again':'Saved')+' · '+link.review_note+' · '+link.opening_sources.map(s=>s.date+': ₹'+s.amount).join(', '));$('#product-form button').disabled=!can('edit_schemes');$('#period-form button').disabled=!can('edit_ledger');$('#preview-button').disabled=!can('import_statements')||!can('edit_ledger');await loadLedger();addOpenButton()}
function addOpenButton(){
 const box=$('#ledger-summary');box.querySelector('[data-open-calculator]')?.remove();
 const ready=Boolean(selected&&$('#season').value&&can('edit_ledger'));
 for(const b of root.querySelectorAll('[data-source-step]'))b.disabled=Number(b.dataset.sourceStep)>0&&!ready;
 if($('#continue-calculation'))$('#continue-calculation').disabled=!ready;
 if(!selected||!$('#season').value)return;
 const open=button('Continue to Check Ledger →',async()=>{await onOpen(selected.id,$('#season').value,state.revision,1)},!can('edit_ledger'));open.dataset.openCalculator='';box.append(open);
}
function sourceWorkflow(){
 if(section!=='import')return;
 const box=document.createElement('div');box.className='card';box.id='source-workflow';
 const tabs=document.createElement('div');tabs.className='tabs calculation-steps';tabs.setAttribute('aria-label','Calculation steps');
 for(const [i,label]of ['Select Party','Check Ledger','Assign Payments','Check Benefits','Review & Finish'].entries()){
  const b=button('',async()=>{if(i===0){$('#ledger').focus();return;}if(!selected||!$('#season').value)throw Error('Choose a saved statement and working season first.');await onOpen(selected.id,$('#season').value,state.revision,i)});
  b.dataset.sourceStep=String(i);b.innerHTML='<span class="step-number">'+(i+1)+'</span><span>'+label+'</span>';tabs.append(b);
 }
 box.append(tabs);
 const choices=document.createElement('div');choices.className='inline-form';
 choices.append($('#ledger').closest('label'),$('#season').closest('label'));box.append(choices);
 const next=button('Continue to Check Ledger →',async()=>{if(!selected||!$('#season').value)throw Error('Choose a saved statement and working season first.');await onOpen(selected.id,$('#season').value,state.revision,1)});
 next.id='continue-calculation';box.append(next);$('#notice').after(box);
}
sourceWorkflow();
// Product identity is separate from calculation-specific scheme/group assignment.
function identityEditor(target,initial={}){
 const fields={}, [nameLabel,name]=input('Product name','text',initial.name||'');fields.name=name;target.append(nameLabel);
 const crops=state.crops||[...new Set(state.catalogue.map(p=>p.crop))];
 const [cropLabel,crop]=selectField('Crop',[['','Choose saved crop'],...crops.map(c=>[c,c]),['__new__','+ Add new crop']],initial.crop||'');fields.crop=crop;target.append(cropLabel);
 const [newLabel,newCrop]=input('New crop name','text','');newLabel.hidden=true;target.append(newLabel);
 const [segmentLabel,segment]=selectField('Segment / group (optional)',[['Awaiting scheme','No segment — assign when building / choosing a scheme']],'Awaiting scheme');fields.segment=segment;target.append(segmentLabel);
 function segments(){const chosen=crop.value==='__new__'?newCrop.value.trim():crop.value;const old=segment.value;const names=state.segments?.[chosen]||[...new Set(state.catalogue.filter(p=>p.crop===chosen&&p.segment!=='Awaiting scheme').map(p=>p.segment))];segment.replaceChildren();for(const [value,caption]of [['Awaiting scheme','No segment — assign when building / choosing a scheme'],...names.map(s=>[s,s])]){const o=document.createElement('option');o.value=value;o.textContent=caption;segment.append(o)}segment.value=names.includes(old)?old:'Awaiting scheme';}
 crop.addEventListener('change',()=>{newLabel.hidden=crop.value!=='__new__';segments()});newCrop.addEventListener('input',segments);segments();
 const [packLabel,pack]=input('Packet weight (kg)','number',initial.packing_kg||'');pack.min='0.000001';pack.step='any';fields.packing_kg=pack;target.append(packLabel);
 for(const field of [name,crop,pack])field.required=true;
 function read(){
  const values={name:name.value.trim(),crop:(crop.value==='__new__'?newCrop.value:crop.value).trim(),segment:segment.value||'Awaiting scheme',packing_kg:pack.value.trim()};
  for(const key of ['name','crop','packing_kg'])if(!values[key]||(key==='packing_kg'&&(!Number.isFinite(Number(values[key]))||Number(values[key])<=0))){(key==='crop'&&crop.value==='__new__'?newCrop:fields[key]).focus?.();throw Error('Enter '+({name:'a product name',crop:'a saved crop or a new crop name',packing_kg:'a positive packet weight in kg (0.475 for 475 g)'})[key]+', then save again.')}
  const canonical=crops.find(c=>c.toLowerCase()===values.crop.replace(/\s+/g,' ').toLowerCase());values.crop=canonical||values.crop.replace(/\s+/g,' ');return values;
 }
 return {fields,newCrop,read};
}
let catalogueEditor=null;
function configureProductForm(){
 const form=$('#product-form');form.replaceChildren();const editor=identityEditor(form);
 const [label,aliases]=input('Other printed names (separate with commas)','text','');form.append(label);
 const submit=document.createElement('button');submit.type='submit';submit.textContent='Add product';form.append(submit);
 catalogueEditor={editor,aliases};
}

// One row per printed name/unit/packing; source voucher details remain below.
function mappingGroups(doc){
 const groups=new Map();
 for(const [ei,e]of doc.entries.entries())for(const [ii,item]of (e.items||[]).entries()){
  const pack=item.mapping_suggestion?.detected_packing_kg??'';
  const key=JSON.stringify([item.name.toLowerCase().trim().replace(/\s+/g,' '),item.unit,pack?Number(pack):'']);
  if(!groups.has(key))groups.set(key,[]);groups.get(key).push({ei,ii,item});
 }
 return [...groups.values()];
}
function renderProductMappings(doc,plans){
 const box=document.createElement('div');$('#ledger-summary').append(box);
 para(box,'Product mapping · recognised products reuse this workbook’s catalogue and saved choices. Review new, ambiguous or conflicting names below.');
 if(!can('edit_ledger'))para(box,'Mapping requires Edit ledger. Ask your administrator to grant that permission to your login.');
 if(!can('edit_schemes'))para(box,'You can map existing products with Edit ledger. Adding products, packing or scheme settings also requires Edit schemes.');
 const reusable=Object.entries(plans).filter(([key,p])=>p.product_id&&!selected.mappings[key]).length;
 if(reusable)box.append(button('Reuse '+reusable+' recognised item mappings',async()=>{await api(endpoint('resolve-mappings'),{revision:state.revision,ledger_id:selected.id});await load();notice('Recognised products reused. Source evidence retained.')},!can('edit_ledger')));
 const rows=[];
 for(const group of mappingGroups(doc)){
  const {ei,ii,item}=group[0],ids=[...new Set(group.map(x=>x.item.product))];
  const product=ids.length===1&&state.catalogue.find(p=>p.id===ids[0]);
  const decision=plans[ei+':'+ii]||{};
  const control=document.createElement('details'),title=document.createElement('summary');
  title.textContent=product?'Change mapping':'Choose product / packing';control.append(title);
  control.open=!product;
  para(control,decision.reason||'Confirm crop, product and packing');
  const pack=item.mapping_suggestion?.detected_packing_kg;
  const candidates=state.catalogue.filter(p=>!pack||Number(p.packing_kg)===Number(pack));
  const emptyCaption=state.catalogue.length?'No products with this printed packing':'No saved products in this workbook';
  const [label,select]=selectField('Existing workbook product',[['',candidates.length?'Choose product':emptyCaption],...candidates.map(p=>[p.id,p.name+' · '+p.crop+' / '+p.segment+' · '+p.packing_kg+' kg'])],product?.id||decision.product_id||'');
  select.disabled=!can('edit_ledger')||!candidates.length;control.append(label);
  if(!candidates.length)para(control,emptyCaption+'. '+(can('edit_schemes')&&can('edit_ledger')?'Use Add / name new product below, enter its details, then click Create product and save mapping.':'Adding products needs Edit ledger and Edit schemes on your login.'));
  const feedback=document.createElement('p');feedback.setAttribute('role','status');feedback.setAttribute('aria-live','polite');control.append(feedback);
  async function saveMapping(values){
   feedback.textContent='Saving product mapping…';feedback.className='';
   try{await api(endpoint('mapping'),{...base(),...values});await load();notice('Product mapping saved in this workbook.'+(values.new_product?' If settings were already saved, use Settings → Load newly added source products / periods, then configure actual scheme rates and benefits.':''));$('#notice').scrollIntoView?.({block:'nearest'});}
   catch(error){feedback.textContent=error.message;feedback.className='error';feedback.setAttribute('role','alert');feedback.scrollIntoView?.({block:'nearest'});notice(error.message,true);}
  }
  const base=()=>({revision:state.revision,ledger_id:selected.id,entry_index:ei,item_index:ii,same_name:true});
  control.append(button('Save mapping for these '+group.length+' items',async()=>{if(!select.value){feedback.textContent='Choose an existing product, or add a new product below.';return;}await saveMapping({product_id:select.value});},!can('edit_ledger')||!candidates.length));
  if(can('edit_schemes')&&can('edit_ledger')){
   const add=document.createElement('details'),heading=document.createElement('summary');heading.textContent='Add / name new product';add.open=!candidates.length;add.append(heading);
   const editor=identityEditor(add,{name:item.name,packing_kg:pack||''});
   para(add,'Choose the saved crop to avoid duplicate names. Segment is optional here; assign the final state/season group in Choose Scheme / Group or scheme building. Printed packing and rates are evidence only.');
   add.append(button('Create product and save mapping',async()=>{
    let new_product;try{new_product=editor.read()}catch(error){feedback.textContent=error.message;feedback.className='error';feedback.setAttribute('role','alert');return;}
    await saveMapping({new_product});
   }));control.append(add);
  }
  rows.push([item.name+' · '+item.unit+' · '+group.length+' items',pack?pack+' kg':'Not printed — confirm for a new name',[...new Set(group.map(x=>'₹'+x.item.rate+' / '+x.item.unit))].join(', '),product?product.name+' · '+product.crop+' / '+product.segment+' · '+product.packing_kg+' kg':'Needs mapping',control]);
 }
 table(box,['Printed product','Printed packing','Printed rates','Saved mapping','Review'],rows);
}

async function loadLedger(){selected=null;$('#entries').replaceChildren();$('#ledger-summary').replaceChildren();$('#stock-summary').replaceChildren();if(!$('#ledger').value)return;const d=await api(endpoint('ledgers/'+$('#ledger').value));state.revision=d.revision;selected=d.ledger;const doc=d.effective;para($('#ledger-summary'),doc.party+' · Opening ₹'+doc.opening+' · Closing ₹'+doc.closing+' · '+(doc.reconciled?'Reconciled':'Needs reconciliation'));for(const warning of doc.warnings)para($('#ledger-summary'),warning);renderProductMappings(doc,d.mapping_plan||{});const rows=[];for(const [ei,e]of doc.entries.entries()){const details=document.createElement('details'),title=document.createElement('summary');title.textContent='Review / map items';details.append(title);para(details,(e.source_lines||[]).map(x=>x.text).join('\n'));for(const [ii,item]of (e.items||[]).entries()){para(details,item.name+' · '+item.qty+' '+item.unit+' · printed rate ₹'+item.rate+' · suggested pack '+(item.mapping_suggestion?.detected_packing_kg??'unknown')+' kg');}const review=e.web_review||{};const[klabel,kind]=selectField('Voucher type',['sale','return','ipt_in','ipt_out','posted_cn','adjustment','unknown','receipt'].map(x=>[x,x.replaceAll('_',' ')]),review.kind||e.kind);const[slabel,season]=selectField('Benefit / stock season',[['','Use original posting period'],...state.periods.map(p=>[p.name,p.name])],review.season||'');const[clabel,cls]=selectField('Posted CN category',[['','Not reviewed'],['scheme','Scheme benefit CN'],['freight','Freight / expense'],['other','Other adjustment']],review.cn_class||'');const[cropLabel,crop]=selectField('Scheme CN crop',[['','Not mapped'],...[...new Set(state.catalogue.map(p=>p.crop))].map(c=>[c,c])],review.crop||'');const[reasonLabel,reason]=input('Review note','text',review.reason||'');details.append(klabel,slabel,clabel,cropLabel,reasonLabel);details.append(button('Save voucher review',async()=>{const body={kind:kind.value,reason:reason.value};if(season.value)body.season=season.value;if(cls.value)body.cn_class=cls.value;if(crop.value)body.crop=crop.value;await api(endpoint('review'),{revision:state.revision,ledger_id:selected.id,entry_index:ei,review:body});await load();notice('Review saved. Original source retained.')},!can('edit_ledger')));rows.push([e.date,e.reference,e.kind,e.debit,e.credit,review.season||'Posting period',details])}table($('#entries'),['Original date','Voucher','Type','Debit','Credit','Reviewed season','Details'],rows)}
$('#project').addEventListener('change',run(loadBooks));$('#workbook').addEventListener('change',run(load));$('#reload').addEventListener('click',run(init));$('#ledger').addEventListener('change',run(async()=>{await loadLedger();addOpenButton()}));$('#season').addEventListener('change',()=>{$('#stock-summary').replaceChildren();selectionStatus();addOpenButton()});
$('#previous-year').addEventListener('change',()=>{clearYearPreview();yearOptions()});
$('#current-year').addEventListener('change',()=>{clearYearPreview();yearOptions()});
$('#period-form').addEventListener('submit',run(async e=>{const f=e.target;const p=Object.fromEntries(['name','start','end','cutoff'].map(k=>[k,f.elements[k].value]));await api(endpoint('config'),{revision:state.revision,periods:[...state.periods,p]},'PUT');f.reset();await load();notice('Working period saved')}));
$('#product-form').addEventListener('submit',run(async()=>{const p={id:crypto.randomUUID().replaceAll('-',''),...catalogueEditor.editor.read(),aliases:catalogueEditor.aliases.value.split(',').map(x=>x.trim()).filter(Boolean)};await api(endpoint('config'),{revision:state.revision,catalogue:[...state.catalogue,p]},'PUT');await load();notice('Product saved in this workbook. Assign its calculation scheme/group separately.')}));
async function pdfBytes(file){const bytes=new Uint8Array(await file.arrayBuffer());let value='';for(let start=0;start<bytes.length;start+=32768)value+=String.fromCharCode(...bytes.subarray(start,start+32768));return btoa(value)}
$('#import-form').addEventListener('submit',run(async()=>{clearPreview();if(!state)throw Error('Choose a workbook');const files=[...$('#pdfs').files];if(!files.length||files.length>30)throw Error('Select 1–30 PDFs');if(files.reduce((n,f)=>n+f.size,0)>10*1024*1024)throw Error('Choose a batch under 10 MiB for this review console');$('#progress').hidden=false;$('#progress').value=0;const payload=[];for(const [i,file]of files.entries()){payload.push({name:file.name,content_base64:await pdfBytes(file)});$('#progress').value=Math.round((i+1)/files.length*100);$('#progress-label').textContent='Prepared '+(i+1)+' of '+files.length+' files'}$('#progress').removeAttribute('value');$('#progress-label').textContent='Reading PDF ledgers…';const request={revision:state.revision,files:payload};const result=await api(endpoint('preview-import'),request);pending={request,result,workbook};$('#progress').value=100;$('#progress-label').textContent='Preview ready. '+result.results.length+' ledgers checked.';const box=$('#import-preview');for(const r of result.results){para(box,r.party+' · '+r.entries+' entries · '+r.status+' · '+(r.reconciled?'reconciled':'balance needs review'));for(const w of r.warnings)para(box,w);const choices=Object.values(r.mapping_plan||{});para(box,choices.filter(p=>p.product_id).length+' recognised items will reuse workbook mappings · '+choices.filter(p=>!p.product_id).length+' items need product/packing review after applying.');if(r.candidates.length){const[l,s]=selectField('Choose existing ledger to replace',[['','Select after reviewing'],...r.candidates.map(id=>[id,id.slice(0,8)])]);s.dataset.replacement=r.key;box.append(l);para(box,JSON.stringify(r.comparison))}}$('#apply-import').hidden=false;$('#cancel-import').hidden=false;notice('Preview only. No files or ledgers saved.')}));
$('#cancel-import').addEventListener('click',()=>{clearPreview();notice('Preview cancelled. No data saved.')});
$('#apply-import').addEventListener('click',run(async()=>{if(!pending||pending.workbook!==workbook)throw Error('Preview again');const replacements={};for(const s of $('#import-preview').querySelectorAll('select[data-replacement]'))replacements[s.dataset.replacement]=s.value;const result=await api(endpoint('apply-import'),{...pending.request,preview_digest:pending.result.preview_digest,replacements,reason:$('#replace-reason').value});const ids=[...new Set(result.results.map(x=>x.id))];await load(ids.length===1?{ledgerId:ids[0]}:{});
 notice(result.results.map(x=>x.status).join(' · ')+'. Saved party vouchers are available below.');
 if(options.continueAfterImport&&ids.length===1&&$('#season').value&&can('edit_ledger')){
  try{await onOpen(ids[0],$('#season').value,state.revision,1)}catch(e){notice('PDF saved. '+e.message+' Use Continue to Check Ledger after resolving this.',true)}
 }else if(ids.length>1){
  const box=$('#import-preview');para(box,'Choose a party to continue its calculation.');
  for(const id of ids){const row=state.ledgers.find(r=>r.id===id);if(!row)continue;box.append(button('Open '+row.party+' ('+row.entries+' vouchers)',async()=>{$('#ledger').value=id;await loadLedger();addOpenButton();if(!$('#season').value)throw Error('Choose or add a working season first.');await onOpen(id,$('#season').value,state.revision,1)},!can('edit_ledger')));}
 }else if(!$('#season').value)notice('PDF saved. Add a working period below, then choose Continue to Check Ledger.');
 if(root.isConnected)root.scrollIntoView({block:'start'});
}));
$('#reread-button').addEventListener('click',run(async()=>{if(!selected)throw Error('Choose a ledger');const result=await api(endpoint('reread'),{revision:state.revision,ledger_id:selected.id});notice('Saved PDF re-read: '+result.comparison.length+' vouchers; '+result.comparison.filter(x=>x.status!=='Already imported').length+' changed/new. No saved review changed.')}));
$('#summary-button').addEventListener('click',run(async()=>{if(!selected||!$('#season').value)throw Error('Choose a saved statement and add/select a working period first');const result=await api(endpoint('summary'),{ledger_id:selected.id,season:$('#season').value});const box=$('#stock-summary');box.replaceChildren();table(box,['Product','Segment','Supply','IPT in','IPT out','Returns','Net sold','Unit','Net kg'],result.products.map(p=>[p.product,p.segment,p.supply,p.ipt_in,p.ipt_out,p.returns,p.net_sold,p.unit,p.net_sold_kg]));for(const w of result.needs_review)para(box,w.message);for(const cn of result.posted_CNs)para(box,'Posted CN ₹'+cn.amount+' · '+cn.date+' · '+cn.cn_class+' · '+(cn.season||'season needs review'));para(box,result.note)}));
let auditRequest=null;
$('#audit-form').addEventListener('submit',run(async e=>{auditRequest={start:e.target.elements.start.value,end:e.target.elements.end.value};await renderAudit()}));
async function renderAudit(){const result=await api(endpoint('audit'),auditRequest);state.revision=result.revision;$('#audit-categories').replaceChildren();$('#audit-results').replaceChildren();const groups=new Map();for(const f of result.findings){if(!groups.has(f.type))groups.set(f.type,[]);groups.get(f.type).push(f)}for(const [name,findings]of groups){$('#audit-categories').append(button(name+' ('+findings.length+')',async()=>{const box=$('#audit-results');box.replaceChildren();for(const f of findings){const details=document.createElement('details'),summary=document.createElement('summary');summary.textContent=f.type+(f.review?' · Not applicable':'');details.append(summary);para(details,f.message||f.reason||f.description||'Review source evidence');for(const v of f.vouchers)para(details,v.party+' · '+v.date+' · '+v.reference+' · '+(v.narration||''));const [label,reason]=input('Why not applicable?','text',f.review?.reason||'');details.append(label);details.append(button(f.review?'Reset not-applicable review':'Mark not applicable',async()=>{await api(endpoint('audit-review'),{revision:state.revision,...auditRequest,review_id:f.review_id,reason:reason.value,reset:!!f.review});await renderAudit()},!can('edit_ledger')));box.append(details)}}))}if(!groups.size)para($('#audit-categories'),'No findings in this posting-date period.');const cnbox=$('#posted-cns');cnbox.replaceChildren();para(cnbox,result.party_count+' parties · '+result.voucher_count+' vouchers checked');for(const w of result.warnings)para(cnbox,w.party+': '+w.message);table(cnbox,['Posted CN party','Date','Amount','Classification','Crop'],result.posted_CNs.map(c=>[c.party,c.date,c.credit,c.cn_classification,c.crop]))}
$('#year-form').addEventListener('submit',run(async e=>{clearYearPreview();if(!state||!$('#previous-year').value||!$('#current-year').value)throw Error('Import and choose the previous full April–March statement and the following year first');const request={revision:state.revision,previous_id:$('#previous-year').value,current_id:$('#current-year').value,identity_reason:e.target.elements.identity_reason.value};const result=await api(endpoint('year-preview'),request);yearPending={request,workbook};const box=$('#year-preview');box.replaceChildren();para(box,result.review.message);para(box,'Maximum opening credit ₹'+result.review.maximum_opening_credit);for(const r of result.review.receipts){const [label,amount]=input(r.date+' · '+r.reference+' · original ₹'+r.amount,'number','0');amount.min='0';amount.step='0.01';amount.max=r.amount;amount.dataset.receipt=r.id;box.append(label)}for(const e of result.review.jan_march_activity)para(box,e.date+' · '+e.reference+' · '+e.kind+' · debit ₹'+e.debit+' / credit ₹'+e.credit);$('#year-apply').hidden=!can('edit_ledger')}));
$('#year-apply').addEventListener('click',run(async()=>{if(!yearPending||yearPending.workbook!==workbook)throw Error('Review Year Link again');const confirmed={};for(const i of $('#year-preview').querySelectorAll('input[data-receipt]'))confirmed[i.dataset.receipt]=i.value||'0';await api(endpoint('year-apply'),{...yearPending.request,confirmed,reason:$('#year-reason').value});await load();notice('Year Link saved with original receipt dates. No automatic ABS allocation.')}));
try{await init()}finally{root.inert=false}

const sections=[...root.querySelectorAll('section')];
for(const [i,el]of sections.entries())el.hidden=section==='audit'?i!==5:section==='year'?i!==6&&i!==4:i>4;
$('#project').closest('section').hidden=true;
};
