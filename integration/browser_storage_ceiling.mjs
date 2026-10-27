// Isolated Linux Chromium form checks. API payloads are synthetic fixtures;
// real HTTP authority checks run separately in test_storage_ceiling.py.
import assert from 'node:assert/strict';
import {createServer} from 'node:http';
import {readFileSync,mkdtempSync} from 'node:fs';
import {tmpdir} from 'node:os';
import {join} from 'node:path';
process.env.TMPDIR=mkdtempSync(join(tmpdir(),'storage-chromium-'));
import {build} from 'esbuild';
import {chromium} from 'playwright';
const bundle=await build({stdin:{contents:`import React from 'react';import{createRoot}from'react-dom/client';import{UnifiedAccountForm}from'./components/unified-account-form';import{UnifiedUsersEditor}from'./components/unified-users-editor';createRoot(document.getElementById('root')).render(<><UnifiedAccountForm/><UnifiedUsersEditor/></>);`,resolveDir:process.cwd(),loader:'tsx'},jsx:'automatic',bundle:true,write:false});
const server=createServer((req,res)=>{res.setHeader('Content-Type',req.url==='/bundle.js'||req.url==='/account.js'?'text/javascript':'text/html');res.end(req.url==='/bundle.js'?bundle.outputFiles[0].contents:req.url==='/account.js'?readFileSync('cn/backend/cn_web/static/account.js'):req.url==='/account'?readFileSync('cn/backend/cn_web/static/index.html'):'<div id="root"></div><script src="/bundle.js"></script>')});
await new Promise(r=>server.listen(0,'127.0.0.1',r));const origin=`http://127.0.0.1:${server.address().port}`;
const c=(await import('@sparticuz/chromium')).default;
const browser=await chromium.launch({executablePath:process.env.CN_BROWSER_EXECUTABLE||await c.executablePath(),args:c.args.filter(x=>!['--single-process','--disable-web-security'].includes(x)),headless:true});
try{
 for(const [role,ceiling] of [['admin',250],['admin',100],['admin',500],['superadmin',250]]){
  const page=await browser.newPage();const errors=[];page.on('pageerror',e=>errors.push(e.message));let writes=0;
  const user={id:'admin',username:'synthetic-admin',role,permissions:['view_workspace'],user_quota_bytes:ceiling*1048576,is_admin:true,manage_users:true,must_change_password:false};
  const staff={id:'staff',username:'synthetic-staff',role:'user',parent_admin:'admin',enabled:true,permissions:[],quota_bytes:100*1048576,used_bytes:0,requested_cn:true,requested_stn:false};
  await page.route('**/api/**',route=>{const path=new URL(route.request().url()).pathname;if(route.request().method()!=='GET')writes++;return route.fulfill({json:path==='/api/portal/state'?{user,users:[staff]}:path==='/api/me'?{user,csrf_token:'synthetic'}:path==='/api/admin/users'?{users:[staff]}:path==='/api/admin/audit'?{events:[]}:path==='/api/workspace'?{used_bytes:0,quota_bytes:1048576}:{} })});
  await page.goto(origin);const create=page.locator('form').first();await create.locator('[name=quota]').waitFor();
  assert.equal(await create.locator('[name=quota]').inputValue(),String(role==='admin'?Math.min(250,ceiling):250));
  await create.locator('[name=username]').fill('browser-staff');await create.locator('[name=password]').fill('Synthetic test password!');
  await page.getByRole('combobox').last().selectOption('staff');const edit=page.locator('form').nth(1);
  for(const form of [create,edit]){
   const q=form.locator('[name=quota]');assert.equal(await q.getAttribute('max'),role==='admin'?String(ceiling):null);
   await q.fill('2560');assert.equal(await q.evaluate(e=>e.checkValidity()),role==='superadmin');
   if(role==='admin'){
    assert.match(await form.textContent(),new RegExp(`Granted maximum: ${ceiling} MiB`));await form.locator('button').click();assert.equal(writes,0);assert.equal(await q.evaluate(e=>e.validity.rangeOverflow),true);
    await q.fill(String(ceiling));assert.equal(await q.evaluate(e=>e.checkValidity()),true);
   }
  }
  await page.goto(origin+'/account');await page.locator('#create-user [name=quota_mib]').waitFor({state:'visible'});await page.locator('#users button').click();
  for(const selector of ['#create-user','#edit-form']){
   const q=page.locator(selector+' [name=quota_mib]');assert.equal(await q.getAttribute('max'),role==='admin'?String(ceiling):null);await q.fill('2560');assert.equal(await q.evaluate(e=>e.checkValidity()),role==='superadmin');
   if(role==='admin')assert.match(await page.locator(selector).textContent(),new RegExp(`Granted maximum: ${ceiling} MiB`));
  }
  assert.deepEqual(errors,[]);await page.close();console.log(`PASS Chromium: ${role}, ${ceiling} MiB grant; create/edit STN and Account forms; defaults, maximum and native submit validation.`);
 }
}finally{await browser.close();await new Promise(r=>server.close(r))}
