// Real Chromium, real HTML/events/fetch and an isolated real HTTP server.
// This verifies Linux Chromium; Windows acceptance remains a separate check.
const assert=require('node:assert/strict'),path=require('node:path'),fs=require('node:fs');
const {chromium}=require('playwright');
const info=JSON.parse(process.env.CN_FLOW_INFO),root=path.resolve(__dirname,'..');
const delay=ms=>new Promise(r=>setTimeout(r,ms));
(async()=>{
 let args=['--no-sandbox'];
 if(process.env.CN_CHROMIUM_PACKAGE)args=(await import(process.env.CN_CHROMIUM_PACKAGE)).default.args.filter(a=>!['--disable-web-security','--single-process'].includes(a));
 const browser=await chromium.launch({headless:true,args,...(process.env.CN_BROWSER_EXECUTABLE?{executablePath:process.env.CN_BROWSER_EXECUTABLE}:{})});
 let context,page;const errors=[],failedRequests=[];
 async function attach(storageState){
  context=await browser.newContext({viewport:{width:1440,height:1000},...(storageState?{storageState}:{})});
  if(!storageState){
   await context.addCookies([{name:'cn_dev_session',value:info.token,url:info.origin}]);
   await context.addInitScript(i=>{if(location.origin!==i.origin)return;localStorage.setItem('cn-web-project',i.project);localStorage.setItem('cn-workbook-'+i.project,i.workbook)},info);
  }
  page=await context.newPage();page.setDefaultTimeout(15000);
  page.on('pageerror',e=>errors.push(e.message));
  page.on('response',r=>{if(r.url().includes('/api/')&&r.status()>=400)failedRequests.push(r.status()+' '+new URL(r.url()).pathname)});
  page.on('dialog',d=>d.accept());
  if(process.env.CN_FLOW_ASSETS){
   for(const name of ['web-bridge.js','ledger-panel.js'])await page.route('**/'+name,route=>route.fulfill({contentType:'text/javascript',body:fs.readFileSync(path.join(process.env.CN_FLOW_ASSETS,name))}));
  }
  await page.goto(info.origin+'/calculator');await page.waitForLoadState('networkidle');
  await page.locator('#nav [data-page="Parties"]').waitFor();
 }
 async function settled(){await page.waitForFunction(()=>typeof apiBusy!=='undefined'&&apiBusy===0);await page.waitForTimeout(100)}
 async function openImport(){await page.locator('#nav [data-page="Parties"]').click();await page.locator('#main [data-page="Bulk Import"]').click();await page.locator('#pdfs').waitFor();await page.locator('#source-workflow').waitFor();await page.waitForFunction(()=>document.querySelector('#pdfs')&&!document.querySelector('#web-ledger-panel').classList.contains('busy'))}
 async function importFiles(names){await page.locator('#pdfs').setInputFiles(names.map(n=>path.join(root,'tests/fixtures',n)));await page.locator('#preview-button').click();await page.locator('#apply-import').waitFor({state:'visible'});await page.locator('#apply-import').click()}
 async function assertCalculation(){await page.locator('.workspace-title').waitFor();assert.equal(await page.locator('.calculation-steps button').count(),5);await settled();assert.ok(await page.evaluate(()=>record.entries.length)>0,'The imported party must contain its vouchers')}
 try{
  await attach();assert.equal(await page.locator('[data-web-build="6.2"]').count(),1);await openImport();assert.equal(await page.locator('#source-workflow .calculation-steps button').count(),5);
  await importFiles(['two_seasons.pdf']);await assertCalculation();
  assert.equal(await page.evaluate(()=>step),1,'Single import must continue directly to Check Ledger');
  const original=await page.evaluate(()=>({entries:record.entries,party:record.party,location:record.location,state:record.state,season:record.season,id:record.id}));
  assert.ok(original.entries.some(e=>e.kind==='receipt'));assert.ok(original.entries.some(e=>e.kind==='return'));
  await page.locator('#cn-ui-theme').selectOption('studio');await settled();
  assert.ok((await page.locator('#main').innerText()).includes('Products: Sales'));
  // Save a legitimate destination through the real permission-checked endpoint.
  await page.evaluate(async()=>{clearTimeout(saveTimer);await saveQueue;const r=structuredClone(record),receipt=r.entries.find(e=>e.kind==='receipt');r.allocations=[{id:crypto.randomUUID(),source:receipt.id,type:'Settlement',amount:'50',scheme:'',product:'',remark:'Saved reopening destination'}];record=await api('/api/save',r);await refresh();await calculate();render()});
  const saved=await page.evaluate(()=>structuredClone(record));
  await page.locator('.calculation-steps [data-step="2"]').click();await page.waitForFunction(()=>step===2);assert.ok(await page.locator('#work').innerText());
  await page.locator('#nav [data-page="Parties"]').click();await page.locator('[data-open="'+saved.id+'"]').first().click();await assertCalculation();
  assert.deepEqual(await page.evaluate(()=>record.entries.map(e=>[e.id,e.date,e.debit,e.credit])),saved.entries.map(e=>[e.id,e.date,e.debit,e.credit]));
  assert.deepEqual(await page.evaluate(()=>record.allocations),saved.allocations);
  console.log('PASS: single PDF preview/apply opens Check Ledger with all five steps; real party Open retains original vouchers/dates and payment allocations.');
  // A full server restart plus a fresh browser context retains the chosen workbook.
  const storage=await context.storageState();await context.close();
  process.stdout.write('CN_TEST_RESTART_SERVER\n');await new Promise(resolve=>process.stdin.once('data',resolve));process.stdin.pause();
  await attach(storage);await page.locator('#nav [data-page="Parties"]').click();await page.locator('[data-open="'+saved.id+'"]').first().click();await assertCalculation();
  assert.equal(await page.evaluate(()=>activeWorkbook),info.workbook);assert.equal(await page.evaluate(()=>record.party),saved.party);
  assert.deepEqual(await page.evaluate(()=>record.entries),saved.entries);assert.deepEqual(await page.evaluate(()=>record.allocations),saved.allocations);
  await page.locator('#cn-ui-theme').selectOption('classic');await settled();assert.equal(await page.locator('.calculation-steps button').count(),5);
  console.log('PASS: actual server restart and fresh browser context reopen the same workbook/party, source mappings, dates and saved allocations in both interfaces.');
  // Repeat + another party in a batch must not silently open an unrelated source.
  await openImport();await importFiles(['two_seasons.pdf','mapping_a.pdf']);
  await page.getByText('Choose a party to continue its calculation.',{exact:true}).waitFor();
  assert.equal(await page.locator('.calculation-steps button').count(),5);
  assert.equal(await page.evaluate(()=>state.source_ledgers.length),2,'The shell directory must refresh immediately after import');
  assert.equal(await page.evaluate(()=>state.records.filter(r=>r.web_source&&r.web_source.ledger_id===record.web_source.ledger_id).length),1,'Repeat import must reuse saved draft');
  const source=await page.evaluate(()=>state.source_ledgers.find(r=>r.party!==record.party));assert.ok(source);
  await page.locator('#nav [data-page="Parties"]').click();await page.locator('[data-web-ledger="'+source.id+'"]').click();await page.locator('#continue-calculation').waitFor();
  await page.waitForFunction(id=>document.querySelector('#ledger').value===id&&!document.querySelector('#continue-calculation').disabled,source.id);
  await page.locator('#continue-calculation').click();await assertCalculation();assert.equal(await page.evaluate(()=>record.party),source.party);assert.equal(await page.evaluate(()=>record.entries.length),source.entries);
  console.log('PASS: multi-PDF import keeps all five steps and refreshes Parties immediately; saved-source selection opens the chosen party with its full vouchers.');
  // Stale evidence never makes the saved vouchers or destinations disappear.
  await page.locator('#nav [data-page="Parties"]').click();await page.locator('[data-open="'+saved.id+'"]').first().click();await assertCalculation();
  await page.evaluate(async()=>{const p='/api/ledger/workbooks/'+activeWorkbook;const me=await (await cnWebFetch('/api/me')).json(),s=await (await cnWebFetch(p)).json();const r=await cnWebFetch(p+'/review',{method:'POST',headers:{'Content-Type':'application/json','X-CSRF-Token':me.csrf_token},body:JSON.stringify({revision:s.revision,ledger_id:record.web_source.ledger_id,entry_index:0,review:{kind:'sale',reason:'Review note for stale display test'}})});if(!r.ok)throw Error(await r.text())});
  await page.locator('#nav [data-page="Parties"]').click();await page.locator('[data-open="'+saved.id+'"]').first().click();await page.locator('[data-web-stale-step="1"]').waitFor();
  await page.locator('[data-web-stale-step="1"]').click();assert.equal(await page.locator('#main tbody tr').count(),saved.entries.length);assert.ok((await page.locator('#main').innerText()).includes(saved.entries[0].date));
  await page.locator('[data-web-stale-step="2"]').click();assert.ok((await page.locator('#main').innerText()).includes('50'));assert.deepEqual(await page.evaluate(()=>record.allocations),saved.allocations);
  console.log('PASS: changed source shows all five steps with actual saved vouchers/dates and allocations read-only, plus source-review guidance.');
  // A new workbook without dates must keep its imported data visible and
  // explain the missing choice, rather than making a blank calculation.
  const emptyBook=await page.evaluate(async()=>{const me=await (await cnWebFetch('/api/me')).json();const response=await cnWebFetch('/api/data/workbooks',{method:'POST',headers:{'Content-Type':'application/json','X-CSRF-Token':me.csrf_token},body:JSON.stringify({project:activeProject,data:{name:'Empty-period workbook'}})});if(!response.ok)throw Error(await response.text());const b=await response.json();await refresh();return b});
  await page.locator('#workbook-select').selectOption(emptyBook.id);await page.waitForFunction(id=>activeWorkbook===id,emptyBook.id);await settled();
  await page.locator('#nav [data-page="Parties"]').click();await page.locator('#main [data-action="new"]').click();await page.locator('#pdf').setInputFiles(path.join(root,'tests/fixtures/two_seasons.pdf'));await page.locator('#pdfs').waitFor();
  await page.waitForFunction(()=>document.querySelector('#pdfs')?.files.length===1&&!document.querySelector('#web-ledger-panel').inert);assert.equal(await page.locator('#pdfs').evaluate(e=>e.files.length),1,'The file chosen in Step 1 must reach source import');
  await page.locator('#preview-button').click();await page.locator('#apply-import').waitFor({state:'visible'});await page.locator('#apply-import').click();
  await page.getByText('PDF saved. Add a working period below, then choose Continue to Check Ledger.',{exact:true}).waitFor();
  assert.equal(await page.locator('.calculation-steps button').count(),5);const stepsBox=await page.locator('.calculation-steps').boundingBox();assert.ok(stepsBox.y>=0&&stepsBox.y+stepsBox.height<=1000,'Import completion must bring the five steps into view');assert.equal(await page.locator('#continue-calculation').isDisabled(),true);assert.ok(await page.locator('#entries tbody tr').count()>0);
  if(process.env.CN_FLOW_SCREENSHOTS){fs.mkdirSync(process.env.CN_FLOW_SCREENSHOTS,{recursive:true});await page.screenshot({path:path.join(process.env.CN_FLOW_SCREENSHOTS,'import-without-period.png')})}
  await page.locator('#period-form [name="name"]').fill('Kharif');await page.locator('#period-form [name="start"]').fill('2026-04-01');await page.locator('#period-form [name="end"]').fill('2026-08-31');await page.locator('#period-form [name="cutoff"]').fill('2026-11-15');await page.locator('#period-form').getByRole('button',{name:'Add period',exact:true}).click();
  await page.waitForFunction(()=>!document.querySelector('#continue-calculation').disabled&&!document.querySelector('#web-ledger-panel').classList.contains('busy'));
  await page.locator('#continue-calculation').click();await assertCalculation();assert.equal(await page.evaluate(()=>record.entries.length),original.entries.length);
  if(process.env.CN_FLOW_SCREENSHOTS)await page.screenshot({path:path.join(process.env.CN_FLOW_SCREENSHOTS,'party-ledger-classic.png')});
  await page.locator('#cn-ui-theme').selectOption('studio');await settled();if(process.env.CN_FLOW_SCREENSHOTS)await page.screenshot({path:path.join(process.env.CN_FLOW_SCREENSHOTS,'party-ledger-studio.png')});
  console.log('PASS: Step 1 file selection reaches source import; a workbook without dates shows saved vouchers and all five steps, then continues directly after an explicit working-period choice.');
  assert.deepEqual(errors,[],'No uncaught browser errors');assert.deepEqual(failedRequests,[],'No failed API calls during the tested workflow');
  console.log('PASS: no page errors or failed API calls. Linux Chromium verified; Windows acceptance remains pending.');
 }finally{await browser.close()}
})().catch(e=>{console.error(e);process.exitCode=1});
