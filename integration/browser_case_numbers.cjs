const assert=require('node:assert/strict');
const {chromium}=require('playwright');
const info=JSON.parse(process.env.INTEGRATION_BROWSER_INFO);
(async()=>{
 const browser=await chromium.launch({executablePath:process.env.CN_BROWSER_EXECUTABLE||undefined,args:process.env.CN_BROWSER_SINGLE_PROCESS==='1'?['--no-sandbox','--single-process','--no-zygote','--disable-dev-shm-usage']:[],env:process.env});
 try {
  const p=await browser.newPage({viewport:{width:1440,height:1000}}),errors=[];
  p.on('pageerror',e=>errors.push(e.message));
  await p.goto(info.origin+'/portal');
  await p.locator('[name=username]').fill(info.username);await p.locator('[name=password]').fill(info.password);
  await p.getByRole('button',{name:'Continue',exact:true}).click();await p.locator('#signed').waitFor();
  for(const theme of ['classic','studio']){
   await p.goto(info.origin+'/member/submit-report');await p.getByLabel('Appearance',{exact:true}).selectOption(theme);
   await p.getByRole('checkbox',{name:'Legal proceedings initiated',exact:true}).check();
   const type=p.getByLabel('Case number type *',{exact:true});
   assert.equal(await type.inputValue(),'');
   await type.selectOption('temporary');await p.getByLabel('Temporary / filing number *',{exact:true}).fill('TMP-UI/2026');
   await type.selectOption('permanent');assert.equal(await p.getByLabel('Permanent / registered case number *',{exact:true}).inputValue(),'TMP-UI/2026');
   await p.goto(info.origin+'/member/reports/'+info.case_report_id+'/edit');
   assert.equal(await p.getByLabel('Case number type *',{exact:true}).inputValue(),'permanent');
   assert.equal(await p.getByLabel('Permanent / registered case number *',{exact:true}).inputValue(),'REG-90/2026');
   await p.getByText('Currently saved case details',{exact:true}).click();
   await p.getByText('Previous case numbers (2)',{exact:true}).click();
   await p.getByText(/TMP-1\/2026/).waitFor();await p.getByText(/TMP-2\/2026/).waitFor();
   console.log('PASS real Chromium',theme,'new-report explicit type choice, temporary/permanent field labels, value retention and persisted permanent edit/history');
  }
  assert.deepEqual(errors,[]);
 }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exit(1)});
