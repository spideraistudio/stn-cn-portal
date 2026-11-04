const assert=require('node:assert/strict'),path=require('node:path'),{chromium}=require('playwright');
const info=JSON.parse(process.env.CN_FLOW_INFO);
(async()=>{
 const pkg=process.env.CN_CHROMIUM_PACKAGE?(await import(process.env.CN_CHROMIUM_PACKAGE)).default:null;
 const browser=await chromium.launch({headless:true,...(process.env.CN_BROWSER_EXECUTABLE?{executablePath:process.env.CN_BROWSER_EXECUTABLE}:{}),args:pkg?pkg.args.filter(a=>!['--disable-web-security','--single-process'].includes(a)):['--no-sandbox']});
 try{
  const context=await browser.newContext({viewport:{width:1500,height:1000},reducedMotion:'reduce'});
  await context.addCookies([{name:'cn_dev_session',value:info.token,url:info.origin}]);
  await context.addInitScript(i=>{localStorage.setItem('cn-web-project',i.project);localStorage.setItem('cn-workbook-'+i.project,i.workbook)},info);
  const page=await context.newPage(),errors=[];page.on('pageerror',e=>errors.push(e.message));
  await page.goto(info.origin+'/calculator');await page.waitForFunction(()=>typeof state!=='undefined'&&state?.records);
  await page.evaluate(async id=>{await openRecord(id);step=1;render()},info.kharif);
  assert.ok(await page.getByRole('heading',{name:'Products, mapping & billing rates'}).isVisible());
  assert.ok((await page.locator('#work').innerText()).includes('Source billing rates'));
  await page.locator('#work [data-cn-action="scope"]').click();
  const choices=page.locator('[data-cn-scope-product]');assert.ok(await choices.count()>=2);
  if(process.env.CN_SCOPE_PREVIEW)await page.screenshot({path:process.env.CN_SCOPE_PREVIEW});
  const original=await page.evaluate(()=>({entries:structuredClone(record.entries),closing:result.ledger_closing,sources:structuredClone(result.sources)}));
  const excludedName=await choices.first().locator('..').innerText();await choices.first().uncheck();
  await page.locator('[data-cn-action="products-save"]').click();await page.waitForFunction(()=>!document.querySelector('#modal').open&&step===2);
  await page.locator('.cn-allocation-scope').waitFor();assert.ok(await page.locator('.cn-allocation-scope').isVisible());
  const after=await page.evaluate(()=>({closing:result.ledger_closing,sources:result.sources,excluded:record.entries.flatMap(e=>e.items||[]).filter(i=>String(i.review_reason||'').startsWith(cnScopeReason)).length}));
  assert.equal(after.closing,original.closing);assert.deepEqual(after.sources,original.sources);assert.ok(after.excluded>0);
  await page.reload();await page.waitForFunction(()=>typeof state!=='undefined'&&state?.records);await page.evaluate(async id=>{await openRecord(id);step=2;render()},info.kharif);
  await page.locator('.cn-allocation-scope [data-cn-action="scope"]').click();assert.equal(await page.locator('[data-cn-scope-product]').first().isChecked(),false);
  await page.locator('#cn-scope-period').selectOption('Rabi');await page.locator('[data-cn-action="period-apply"]').click();
  await page.waitForFunction(()=>record.season==='Rabi'&&document.querySelector('#modal').open&&document.querySelector('#cn-scope-period')?.value==='Rabi');
  assert.equal(await page.locator('[data-cn-scope-product]').count(),1);
  const rabi=await page.evaluate(()=>({id:record.id,excluded:cnScopeGroups().flatMap(g=>g.items).filter(x=>x.item.exclude).length}));assert.notEqual(rabi.id,info.kharif);assert.equal(rabi.excluded,0);
  await page.locator('[data-cn-action="products-save"]').click();await page.waitForFunction(()=>!document.querySelector('#modal').open);
  // Add a fresh season without changing earlier season definitions or saved drafts.
  await page.locator('.cn-allocation-scope [data-cn-action="scope"]').click();await page.locator('#cn-scope-period').selectOption('__new__');
  await page.locator('#cn-period-name').fill('Rabi review');await page.locator('#cn-period-start').fill('2026-10-01');await page.locator('#cn-period-end').fill('2027-02-28');await page.locator('#cn-period-cutoff').fill('2027-03-31');
  await page.locator('[data-cn-action="period-apply"]').click();await page.waitForFunction(()=>document.querySelector('#cn-scope-error')?.textContent.includes('overlap'));
  assert.equal(await page.evaluate(()=>record.season),'Rabi');
  await page.locator('#cn-period-start').fill('2027-03-01');await page.locator('#cn-period-end').fill('2027-03-31');await page.locator('#cn-period-cutoff').fill('2027-04-15');
  await page.locator('[data-cn-action="period-apply"]').click();await page.waitForFunction(()=>record.season==='Rabi review'&&document.querySelector('#modal').open&&document.querySelector('#cn-scope-period')?.value==='Rabi review');
  assert.ok((await page.locator('#cn-period-current').innerText()).includes('2027'));
  await page.locator('#closemodal').click();
  await page.evaluate(()=>{page='Bulk Import';bulkPage()});assert.ok((await page.locator('#main').innerText()).includes('Imported products — map before building schemes'));
  assert.ok(await page.locator('[data-cn-bulk-product]').count());await page.locator('[data-cn-bulk-product]').first().click();await page.getByRole('heading',{name:'Imported products → mapping → schemes'}).waitFor();
  await page.locator('#closemodal').click();
  // Fresh actual PDF import must open product setup immediately.
  await page.evaluate(()=>{record=blank();page='Calculate CN';step=0;render()});
  await page.locator('#pdf').setInputFiles(path.join(__dirname,'../cn/tests/fixtures/mapping_a.pdf'));
  await page.getByRole('heading',{name:'Imported products → mapping → schemes'}).waitFor();
  await page.locator('#dialogbody tr').filter({hasText:'PRINTED BRAND'}).locator('[data-inline-map]').first().click();await page.locator('#im-new-crop').fill('Maize');await page.locator('#im-pack').fill('4');
  await page.locator('#save-inline-mapping').click();try{await page.getByRole('heading',{name:'Imported products → mapping → schemes'}).waitFor();}catch(e){console.log('Mapping feedback:',await page.locator('#dialogbody').innerText());console.log('Toast:',await page.locator('#toast').innerText());console.log('Page errors:',errors);throw e;}
  assert.ok(await page.locator('#dialogbody [data-product-scheme]').count());
  await page.locator('#dialogbody tr').filter({hasText:'PRINTED BRAND'}).locator('[data-product-scheme]').first().click();await page.locator('[data-create-product-scheme]').click();
  assert.ok((await page.locator('#dialogbody').innerText()).includes('Create New Scheme'));
  await page.locator('#closemodal').click();await page.locator('#cn-ui-theme').selectOption('classic');
  await page.evaluate(()=>{step=2;page='Calculate CN';render()});await page.locator('.cn-allocation-scope [data-cn-action="scope"]').click();
  assert.ok(await page.getByRole('heading',{name:'Choose working period & CN products'}).isVisible());
  await page.locator('#closemodal').click();
  assert.deepEqual(errors,[]);
  console.log('PASS: Linux Chromium import opens product/rate setup; mapping returns to setup; mapped product opens scheme builder; product exclusions persist across reload; full ledger and receipts preserved; same-product Rabi opens separately; new period works; bulk product list navigates to setup.');
  await context.close();
  const admin=await browser.newContext();await admin.addCookies([{name:'cn_dev_session',value:info.admin,url:info.origin}]);const adminPage=await admin.newPage();await adminPage.goto(info.origin+'/account');
  await adminPage.locator('#create-user [name="username"]').fill('ADMIN');await adminPage.locator('#create-user [name="username"]').blur();await adminPage.waitForFunction(()=>document.getElementById('username-availability')?.textContent.includes('already registered'));
  await adminPage.locator('#create-user [name="username"]').fill('brand-new-user');await adminPage.locator('#create-user [name="username"]').blur();await adminPage.waitForFunction(()=>document.getElementById('username-availability')?.textContent.includes('is available'));
  console.log('PASS: account creation checks existing and available usernames before submission.');
 }finally{await browser.close()}
})().catch(e=>{console.error(e);process.exitCode=1});
