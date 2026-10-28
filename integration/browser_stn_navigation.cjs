// Actual production gateway route smoke coverage; synthetic test accounts only.
const assert=require('node:assert/strict');
const {chromium}=require('playwright');
const info=JSON.parse(process.env.INTEGRATION_BROWSER_INFO);
(async()=>{
 const bundle=(await import('@sparticuz/chromium')).default;
 const browser=await chromium.launch({headless:true,executablePath:process.env.CN_BROWSER_EXECUTABLE||await bundle.executablePath(),args:bundle.args.filter(x=>!['--disable-web-security','--single-process'].includes(x))});
 try{
  for(const admin of [false,true]) for(const theme of ['classic','studio']){
   const context=await browser.newContext();await context.addInitScript(theme=>{if(/^https?:$/.test(location.protocol))localStorage.setItem('stn-cn-theme',theme);},theme);const page=await context.newPage();const errors=[];page.on('pageerror',e=>errors.push(e.message));
   await page.goto(info.origin+'/portal');await page.locator('[name=username]').fill(admin?info.admin_username:info.username);await page.locator('[name=password]').fill(admin?info.admin_password:info.password);await page.getByRole('button',{name:'Continue',exact:true}).click();await page.locator('#signed').waitFor({state:'visible'});
   const paths=admin?['/admin','/admin/cn','/admin/companies','/admin/reports','/admin/resolutions','/admin/notifications','/admin/seed-trade','/admin/pilot','/admin/governance','/admin/audit','/admin/preview','/admin/members/000000000000000000000001']:['/member','/member/sellers','/member/submit-report','/member/buy-sell','/member/reports','/member/profile','/member/notifications'];
   for(const path of paths){const response=await page.goto(info.origin+path);assert(response.status()<400,`${path}: ${response.status()}`);await page.locator('body').waitFor();assert(!/Application error:|Internal Server Error|This page could not be found/.test(await page.locator('body').innerText()),path);assert.equal(new URL(page.url()).pathname,path,`${path} unexpectedly redirected`);await page.waitForFunction(theme=>document.documentElement.dataset.suiteTheme===theme,theme);console.log('PASS STN rendered navigation '+theme+' '+path);}
   const aliases=admin?{'/admin/security':'/account'}:{'/member/users':'/settings/users','/member/account':'/account','/member/password':'/account','/member/issues':'/settings/issues','/member/about':'/about','/member/contact':'/contact'};
   for(const [path,destination] of Object.entries(aliases)){const response=await page.goto(info.origin+path);assert.equal(response.status(),200);assert.equal(new URL(page.url()).pathname,destination);console.log('PASS STN legacy navigation '+theme+' '+path+' → '+destination);}
   assert.deepEqual(errors,[]);await context.close();
  }
 }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});
