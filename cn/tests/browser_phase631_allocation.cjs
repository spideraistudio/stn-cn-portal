const assert=require('node:assert/strict'),path=require('node:path');
const {chromium}=require('playwright'),info=JSON.parse(process.env.CN_FLOW_INFO);
(async()=>{
 const args=(await import(process.env.CN_CHROMIUM_PACKAGE)).default.args.filter(a=>!['--disable-web-security','--single-process'].includes(a));
 const browser=await chromium.launch({headless:true,executablePath:process.env.CN_BROWSER_EXECUTABLE,args});
 const context=await browser.newContext(),page=await context.newPage(),errors=[],failures=[];
 await context.addCookies([{name:'cn_dev_session',value:info.token,url:info.origin}]);
 await context.addInitScript(i=>{localStorage.setItem('cn-web-project',i.project);localStorage.setItem('cn-workbook-'+i.project,i.workbook)},info);
 page.on('pageerror',e=>errors.push(e.message));page.on('response',r=>{if(r.url().includes('/api/')&&r.status()>=400)failures.push(r.status())});
 async function idle(){await page.waitForFunction(()=>apiBusy===0);await page.waitForTimeout(150)}
 try{
  await page.goto(info.origin+'/calculator');await page.waitForLoadState('networkidle');
  await page.locator('#nav [data-page="Parties"]').click();await page.locator('#main [data-action="new"]').click();
  await page.locator('#pdf').setInputFiles(path.join(__dirname,'fixtures/current_year.pdf'));await page.locator('[data-action="review-ledger"]').waitFor();await idle();
  assert.equal(Number(await page.evaluate(()=>record.opening)),-10000);
  await page.locator('.calculation-steps [data-step="2"]').click();await idle();
  await page.locator('[data-action="opening-source"]').click();await idle();
  await page.locator('[data-action="save"]').click();await idle();
  let saved=await page.evaluate(async()=>{await saveQueue;return structuredClone(record)});
  assert.equal(saved.opening_sources.length,1);assert.equal(saved.opening_sources[0].date,null);
  assert.equal(Number(saved.opening_sources[0].amount),10000);
  // Use the real original row controls; opening credit can fund Settlement.
  await page.locator('#payment-workbench [data-allocation="0"][data-key="type"]').selectOption('Settlement');await idle();
  await page.locator('#payment-workbench [data-allocation="0"][data-key="amount"]').fill('5000');
  await page.locator('#payment-workbench [data-allocation="0"][data-key="amount"]').dispatchEvent('change');await idle();
  await page.locator('[data-action="save"]').click();await idle();
  saved=await page.evaluate(async()=>{await saveQueue;return structuredClone(record)});
  assert.equal(saved.allocations[0].type,'Settlement');assert.equal(Number(saved.allocations[0].amount),5000);
  for(const n of [1,0,3,0,4,2]){await page.locator('.calculation-steps [data-step="'+n+'"]').click();await idle();assert.equal(await page.evaluate(()=>step),n)}
  await page.locator('#nav [data-page="Parties"]').click();await page.locator('[data-open="'+saved.id+'"]').first().click();await idle();
  assert.deepEqual(await page.evaluate(()=>record.opening_sources),saved.opening_sources);assert.deepEqual(await page.evaluate(()=>record.allocations),saved.allocations);
  console.log('PASS: real PDF with opening credit → actual Allocate available opening credit button → actual Settlement/amount controls → Save → five tabs → Parties/reopen; sources and allocations retained.');
  // A failed save must still report its error, while a corrected draft can retry.
  const failure=await page.evaluate(async()=>{
   const before=structuredClone(record.opening_sources);record.opening_sources[0].date='2026-04-01';
   let message='';try{await saveDraft()}catch(e){message=e.message}
   await saveQueue;record.opening_sources=before;return message;
  });assert.match(failure,/Year Link/);
  await page.locator('#nav [data-page="Parties"]').click();await page.locator('[data-open="'+saved.id+'"]').first().click();await idle();
  assert.deepEqual(await page.evaluate(()=>record.allocations),saved.allocations);
  console.log('PASS: dated source forgery is rejected; corrected draft retries through ordinary navigation without a permanently failed save queue.');
  process.stdout.write('CN_TEST_RESTART_SERVER\n');await new Promise(resolve=>process.stdin.once('data',resolve));process.stdin.pause();
  await page.reload();await page.waitForLoadState('networkidle');await page.locator('#nav [data-page="Parties"]').click();await page.locator('[data-open="'+saved.id+'"]').first().click();await idle();
  assert.deepEqual(await page.evaluate(()=>record.opening_sources),saved.opening_sources);assert.deepEqual(await page.evaluate(()=>record.allocations),saved.allocations);
  assert.deepEqual(errors,[]);assert.deepEqual(failures,[400]);console.log('PASS: real server restart retains opening-credit allocation. Only the deliberate forgery failed; no browser errors.');
 }catch(e){console.log('DIAGNOSTIC',await page.locator('#main').innerText(),await page.locator('#toast').innerText(),errors,failures);throw e}finally{await browser.close()}
})().catch(e=>{console.error(e);process.exitCode=1});
