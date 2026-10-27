const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path'),{chromium}=require('playwright');
const info=JSON.parse(process.env.CN_FLOW_INFO);
(async()=>{const args=(await import(process.env.CN_CHROMIUM_PACKAGE)).default.args.filter(a=>a!=='--disable-web-security');const browser=await chromium.launch({headless:true,args,executablePath:process.env.CN_BROWSER_EXECUTABLE});try{
const context=await browser.newContext({viewport:{width:1440,height:1000},reducedMotion:'reduce'});await context.addCookies([{name:'cn_dev_session',value:info.token,url:info.origin}]);await context.addInitScript(i=>{localStorage.setItem('cn-web-project',i.project);localStorage.setItem('cn-workbook-'+i.project,i.workbook)},info);
const page=await context.newPage(),errors=[];page.on('pageerror',e=>errors.push(e.message));page.on('dialog',d=>d.accept());await page.goto(info.origin+'/calculator');
for(const filename of fs.readdirSync(process.env.CN_MULTI_STATEMENT_DIR).filter(n=>/\.pdf$/i.test(n))){
 await page.locator('#nav [data-page="Parties"]').click();await page.locator('#main [data-action="new"]').click();await page.locator('#pdf').setInputFiles(path.join(process.env.CN_MULTI_STATEMENT_DIR,filename));await page.locator('[data-action="review-ledger"]').waitFor();await page.waitForFunction(()=>apiBusy===0);
 assert.ok(await page.getByText('STATEMENT IMPORT REVIEW',{exact:true}).isVisible());const format=await page.evaluate(()=>record.source.format);
 if(format==='account-item-detail-v1'){
  await page.locator('[data-field="opening_review_reason"]').fill('Confirmed zero opening against prior ledger');await page.locator('[data-field="opening_review_reason"]').press('Tab');
  await page.locator('#voucher-0 > summary').click();assert.equal(await page.locator('[data-item="0,0"][data-key="unit"]').inputValue(),'packet');assert.ok((await page.locator('#voucher-0').innerText()).includes('confirmed company/product profile'));
 }
 if(format==='account-compact-v1'){
  await page.locator('#voucher-0 > summary').click();assert.equal(await page.locator('[data-item="0,0"][data-key="unit"]').inputValue(),'packet');
  const unit=page.locator('select[data-item][data-key="unit"]').filter({has:page.locator('option[value="unknown"]')}).first();await unit.selectOption('packet');
  const coords=await unit.getAttribute('data-item');await page.locator(`[data-item="${coords}"][data-key="unit_review_reason"]`).fill('Synthetic browser check only');await page.locator(`[data-item="${coords}"][data-key="unit_review_reason"]`).press('Tab');
  assert.ok(await page.locator('[data-entry="0"][data-key="amount_review_reason"]').isVisible());
 }
 assert.equal(await page.evaluate(()=>result.can_finalise),false);
 for(const theme of ['classic','studio']){await page.locator('#cn-ui-theme').selectOption(theme);await page.getByText('STATEMENT IMPORT REVIEW',{exact:true}).scrollIntoViewIfNeeded();await page.screenshot({path:'/tmp/statement-'+format+'-'+theme+'.png'});}
 await page.evaluate(async()=>{await saveDraft()});const rid=await page.evaluate(()=>record.id);await page.reload();await page.waitForFunction(()=>state?.records&&apiBusy===0);await page.evaluate(async id=>{await openRecord(id)},rid);await page.waitForFunction(()=>apiBusy===0);assert.equal(await page.evaluate(()=>record.source.format),format);
 console.log('PASS rendered import/review/save/reload and both themes:',format);
}
assert.deepEqual(errors,[]);console.log('PASS no page errors; Windows acceptance remains pending.');
}finally{await browser.close()}})().catch(e=>{console.error(e);process.exitCode=1});
