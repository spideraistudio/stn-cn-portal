const assert=require('node:assert/strict'),path=require('node:path'),fs=require('node:fs'),{chromium}=require('playwright');
const info=JSON.parse(process.env.CN_FLOW_INFO);
(async()=>{
 const args=(await import(process.env.CN_CHROMIUM_PACKAGE)).default.args.filter(a=>!['--disable-web-security','--single-process'].includes(a));
 const browser=await chromium.launch({headless:true,executablePath:process.env.CN_BROWSER_EXECUTABLE,args});
 let context=await browser.newContext({viewport:{width:1600,height:1100}}),page=await context.newPage();const errors=[],failures=[];
 await context.addCookies([{name:'cn_dev_session',value:info.token,url:info.origin}]);
 await context.addInitScript(i=>{localStorage.setItem('cn-web-project',i.project);localStorage.setItem('cn-workbook-'+i.project,i.workbook)},info);
 page.on('pageerror',e=>errors.push(e.message));page.on('response',r=>{if(r.url().includes('/api/')&&r.status()>=400)failures.push(r.status()+' '+r.url())});
 async function idle(){await page.waitForFunction(()=>apiBusy===0);await page.waitForTimeout(100)}
 async function open(id){await page.locator('#nav [data-page="Parties"]').click();await page.locator('[data-open="'+id+'"]').first().click();await idle();await page.locator('.calculation-steps [data-step="2"]').click();await idle()}
 async function values(){return page.locator('[data-cd-card-amount]').evaluateAll(ns=>ns.map(n=>({amount:n.dataset.cdCardAmount,text:n.parentElement.innerText,highlighted:n.parentElement.classList.contains('payment-source-linked'),overflow:n.parentElement.scrollHeight>n.parentElement.clientHeight+1}))) }
 async function allocate(amount){
  await page.locator('#radial-diagram [data-radial-type="CD"][data-radial-crop="Maize"]').click();
  await page.locator('#segment-cd-amount').fill(amount);await page.locator('#segment-cd-preview').click();
  await page.locator('#segment-cd-apply').waitFor();
  const plan=await page.evaluate(()=>structuredClone(segmentCD.plan));await page.locator('#segment-cd-apply').click();
  await page.waitForFunction(()=>segmentCD===null);await idle();return plan;
 }
 try{
  await page.goto(info.origin+'/calculator');await page.waitForLoadState('networkidle');await open(info.multiple);
  const plan=await allocate('100000');assert.equal(Number(plan.retained),100000);
  const canonical=await page.evaluate(()=>({record:structuredClone(record),result:structuredClone(result)}));
  assert.equal(canonical.record.allocations.length,1);assert.equal(canonical.record.allocations[0].product,'');
  assert.equal(Number(canonical.result.groups[0].CD_work[0].CD),12000);
  for(const theme of ['classic','studio']){
   await page.locator('#cn-ui-theme').selectOption(theme);await idle();const cards=await values();assert.equal(cards.length,3);
   assert.equal(cards.reduce((n,c)=>n+Math.round(Number(c.amount)*100),0),10000000);
   assert.ok(cards.every(c=>Number(c.amount)>0&&c.text.includes('Shared CD')&&c.highlighted&&!c.overflow));
   assert.deepEqual(await page.evaluate(()=>record.allocations),canonical.record.allocations);
   assert.deepEqual(await page.evaluate(()=>result),canonical.result);
   if(process.env.CN_FLOW_SCREENSHOTS){fs.mkdirSync(process.env.CN_FLOW_SCREENSHOTS,{recursive:true});await page.locator('#radial-viewport').screenshot({path:path.join(process.env.CN_FLOW_SCREENSHOTS,'cd-cards-'+theme+'.png')})}
  }
  console.log('PASS: actual CD crop click/preview/apply shows all three product funding shares, which sum to the crop allocation in both themes; receipt highlighting and card fit verified. Only one pooled row persists; engine result unchanged by display.');
  await open(info.multiple);assert.equal((await values()).reduce((n,c)=>n+Math.round(Number(c.amount)*100),0),10000000);
  const storageState=await context.storageState();await context.close();process.stdout.write('CN_TEST_RESTART_SERVER\n');await new Promise(resolve=>process.stdin.once('data',resolve));process.stdin.pause();
  context=await browser.newContext({viewport:{width:1600,height:1100},storageState});page=await context.newPage();page.on('pageerror',e=>errors.push(e.message));page.on('response',r=>{if(r.url().includes('/api/')&&r.status()>=400)failures.push(r.status()+' '+r.url())});await page.goto(info.origin+'/calculator');await page.waitForLoadState('networkidle');await open(info.multiple);assert.equal((await values()).reduce((n,c)=>n+Math.round(Number(c.amount)*100),0),10000000);
  assert.deepEqual(await page.evaluate(()=>record.allocations),canonical.record.allocations);
  await open(info.capped);const capped=await allocate('50000');assert.ok(Number(capped.released)>48000);
  const cards=await values();assert.equal(cards.length,1);assert.equal(Number(cards[0].amount),Number(capped.retained));
  assert.equal(Number(await page.evaluate(()=>result.unallocated)),Number(capped.released));
  console.log('PASS: party reopen/server restart restore product shares; capped one-packet case displays only retained CD funding and leaves excess available.');
  assert.deepEqual(errors,[]);assert.deepEqual(failures,[]);console.log('PASS: no browser/API errors. Linux Chromium; Windows acceptance pending.');
 }catch(e){console.log('DIAGNOSTIC',await page.locator('#toast').innerText(),await values(),errors,failures);throw e}finally{await browser.close()}
})().catch(e=>{console.error(e);process.exitCode=1});
