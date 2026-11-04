// Run after a combined production build. API responses and Next navigation are mocked.
import {createRequire} from 'node:module';
import fs from 'node:fs';
import assert from 'node:assert/strict';
const require = createRequire(import.meta.url);
const {chromium} = require('playwright');
const bundle = (await require('esbuild').build({
  entryPoints: ['tests/fixtures/search-layout.jsx'], bundle: true, write: false, platform: 'browser', jsx: 'automatic',
  define: {'process.env': JSON.stringify({NODE_ENV: 'production', NEXT_PUBLIC_COMMON_PORTAL: '1'})},
  plugins: [{name: 'test-navigation', setup(build) {
    build.onResolve({filter: /^next\/(navigation|link)$/}, args => ({path: args.path, namespace: 'test-navigation'}));
    build.onLoad({filter: /.*/, namespace: 'test-navigation'}, args => ({
      contents: args.path === 'next/navigation'
        ? 'export const usePathname=()=>location.pathname; export const useRouter=()=>({push(){},refresh(){}});'
        : 'import React from "react"; export default React.forwardRef(function Link({prefetch,replace,scroll,...props},ref){return <a {...props} ref={ref}/>})',
      loader: 'jsx', resolveDir: process.cwd(),
    }));
  }}],
})).outputFiles[0].text;
const css = fs.readdirSync('.next/static', {recursive:true}).filter(n => n.endsWith('.css'))
  .map(n => fs.readFileSync('.next/static/' + n, 'utf8')).join('\n')
  + fs.readFileSync('cn/backend/cn_web/calculator_static/suite-theme.css', 'utf8');
const browser=await chromium.launch({executablePath:process.env.STN_BROWSER_EXECUTABLE||undefined,args:['--no-sandbox']});
try {
 const page=await browser.newPage();const errors=[];page.on('pageerror',e=>errors.push(e.message));
 await page.route('http://stn.test/**',route=>{const name=new URL(route.request().url()).pathname.slice(1);if(name.endsWith('.png')&&fs.existsSync('public/'+name))return route.fulfill({contentType:'image/png',body:fs.readFileSync('public/'+name)});return route.fulfill({contentType:'text/html',body:`<html data-suite-surface="stn"><head><style>${css}</style></head><body><div id="root"></div></body></html>`});});
 for(const theme of ['classic','studio']){
  for(const path of ['/member/submit-report','/member/reports/sample/edit','/member/reports/sample/edit?approved']){
   for(const [width,height] of [[1366,768],[1280,600],[1024,640]]){
    await page.setViewportSize({width,height});await page.goto('http://stn.test'+path);
    await page.evaluate(t=>localStorage.setItem('stn-cn-theme',t),theme);await page.addScriptTag({content:bundle});
    const appearance=page.getByLabel('Appearance',{exact:true});await appearance.waitFor();
    await page.waitForFunction(t=>document.documentElement.dataset.suiteTheme===t,theme);
    assert.equal(await appearance.count(),1);assert.equal(await page.locator('.stn-topbar').getByLabel('Appearance').count(),1);
    const submit=page.locator('.stn-report-actions button[type=submit]');assert(await submit.isVisible());
    const geometry=await page.evaluate(()=>{
     const form=document.querySelector('.stn-report-form'),panel=form.firstElementChild,scroll=panel.firstElementChild,footer=document.querySelector('.stn-report-actions');
     const owners=[...document.querySelectorAll('.stn-content *')].filter(e=>/auto|scroll/.test(getComputedStyle(e).overflowY)&&e.scrollHeight>e.clientHeight+1);
     window.formScroller=scroll;
     return {owners:owners.length,owner:owners[0]===scroll,scrollHeight:scroll.clientHeight,footer:footer.getBoundingClientRect().toJSON(),viewport:innerHeight,pageHeight:document.documentElement.scrollHeight,pageWidth:document.documentElement.scrollWidth,viewportWidth:innerWidth};
    });
    assert.equal(geometry.owners,1,JSON.stringify(geometry));assert(geometry.owner,JSON.stringify(geometry));
    assert(geometry.scrollHeight>=height*(width<1100?.50:.58),JSON.stringify(geometry));
    assert(geometry.footer.bottom<=height && geometry.footer.top>=0,JSON.stringify(geometry));
    assert(geometry.footer.height<=64,JSON.stringify(geometry));
    assert(geometry.pageHeight<=height+1 && geometry.pageWidth<=width+1,JSON.stringify(geometry));
    if(width===1366&&path==='/member/submit-report') await page.screenshot({path:'/tmp/report-layout-'+theme+'.png',animations:'disabled'});
    if(path==='/member/submit-report'){
     const gst=page.locator('input[name=gstin]'),firm=page.locator('input[name=firmName]');
     const a=await gst.boundingBox(),b=await firm.boundingBox();assert(Math.abs(a.y-b.y)<2,'GSTIN and firm must share a row');
     await gst.fill('24ABCDE1234F1Z5');await firm.fill('Synthetic Seller');
     await submit.click();await page.getByRole('alert').waitFor();assert(await page.getByRole('alert').isVisible());
     assert(await submit.isVisible());
    }else{
     assert(await page.locator('input[name=gstin]').getAttribute('readonly')!==null);
     assert.equal(await page.locator('input[name=firmName]').inputValue(),'Synthetic Seller');
    }
    await page.getByRole('checkbox',{name:'Legal proceedings initiated'}).check();
    await page.locator('#report-case-number-type').selectOption('temporary');
    await page.locator('input[name=caseNumber]').fill('TEMP-123');
    await page.locator('textarea[name=summary]').fill('Draft text remains while switching appearance.');
    await appearance.selectOption(theme==='classic'?'studio':'classic');
    assert.equal(await page.locator('textarea[name=summary]').inputValue(),'Draft text remains while switching appearance.');
    await page.locator('input[name=documents]').scrollIntoViewIfNeeded();
    const lower=await page.locator('input[name=documents]').boundingBox(),bar=await page.locator('.stn-report-actions').boundingBox();
    assert(lower.y+lower.height<=bar.y+1,'Document input must not be covered');assert(await submit.isVisible());
    console.log('PASS report layout',theme,path,width,height);
   }
  }
 }
 assert.deepEqual(errors,[]);
}finally{await browser.close();}
