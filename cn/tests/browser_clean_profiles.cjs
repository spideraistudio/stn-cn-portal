const assert=require('node:assert/strict'),{chromium}=require('playwright');
const info=JSON.parse(process.env.CN_FLOW_INFO);
(async()=>{const args=(await import('@sparticuz/chromium')).default.args.filter(a=>a!=='--disable-web-security');const browser=await chromium.launch({headless:true,args,executablePath:process.env.CN_BROWSER_EXECUTABLE});try{
const context=await browser.newContext({viewport:{width:1440,height:1000},reducedMotion:'reduce'});await context.addCookies([{name:'cn_dev_session',value:info.token,url:info.origin}]);const page=await context.newPage(),errors=[];page.on('pageerror',e=>errors.push(e.message));await page.goto(info.origin+'/calculator');await page.locator('#first-workbook').waitFor();
for(const [name,value] of Object.entries({name:'My fresh workbook',state:'Gujarat',period:'My season',start:'2026-04-01',end:'2026-08-31',cutoff:'2026-11-30'}))await page.locator(`#first-workbook [name="${name}"]`).fill(value);
await page.locator('#first-workbook button[type="submit"]').click();await page.waitForFunction(()=>state?.settings&&apiBusy===0);
assert.deepEqual(await page.evaluate(()=>[state.settings.products.length,state.settings.schemes.length,state.records.length]),[0,0,0]);assert.equal(await page.locator('[data-action="fixture"],[data-action="saini"]').count(),0);
await page.locator('#nav [data-page="Settings"]').click();await page.waitForFunction(()=>apiBusy===0);
assert.deepEqual(await page.evaluate(()=>[state.settings.products.length,state.settings.schemes.length]),[0,0]);
for(const theme of ['classic','studio']){await page.locator('#cn-ui-theme').selectOption(theme);await page.screenshot({path:process.env.CN_SCREENSHOT_DIR+'/clean-profile-'+theme+'.png'});}
await page.reload();await page.waitForFunction(()=>state?.settings&&apiBusy===0);assert.deepEqual(await page.evaluate(()=>[state.settings.products.length,state.settings.schemes.length,state.records.length]),[0,0,0]);
await page.locator('#nav [data-page="Parties"]').click();await page.locator('#main [data-action="new"]').click();await page.locator('#pdf').waitFor();assert.equal(await page.locator('[data-action="fixture"]').count(),0);
assert.deepEqual(errors,[]);console.log('PASS: fresh profile first-workbook form, empty catalogue/schemes/parties, Settings and import entry, both themes, reload retention, no sample actions or page errors. Windows acceptance pending.');
}finally{await browser.close()}})().catch(e=>{console.error(e);process.exitCode=1});
