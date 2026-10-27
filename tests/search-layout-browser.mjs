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
const css = fs.readdirSync('.next/static/chunks').filter(n => n.endsWith('.css'))
  .map(n => fs.readFileSync('.next/static/chunks/' + n, 'utf8')).join('\n')
  + fs.readFileSync('cn/backend/cn_web/calculator_static/suite-theme.css', 'utf8');
const browser = await chromium.launch({executablePath: process.env.STN_BROWSER_EXECUTABLE || undefined,
  args: ['--no-sandbox', '--single-process', '--no-zygote', '--disable-dev-shm-usage'], env: process.env});
try {
  const page = await browser.newPage({viewport: {width: 1440, height: 900}});
  page.setDefaultTimeout(10000);
  const errors = [];
  page.on('pageerror', e => errors.push(e.message));
  await page.route('http://stn.test/**', route => {
    const name = new URL(route.request().url()).pathname.slice(1);
    if (name.endsWith('.png') && fs.existsSync('public/' + name)) return route.fulfill({contentType: 'image/png', body: fs.readFileSync('public/' + name)});
    return route.fulfill({contentType: 'text/html', body: `<html data-suite-surface="stn" data-suite-theme="studio"><head><style>${css}</style></head><body><div id="root"></div></body></html>`});
  });
  async function open(path, theme) {
    await page.goto('http://stn.test' + path);
    await page.evaluate(theme => localStorage.setItem('stn-cn-theme', theme), theme);
    await page.addScriptTag({content: bundle});
    await page.getByLabel('Appearance', {exact: true}).waitFor();
    await page.waitForFunction(theme => document.documentElement.dataset.suiteTheme === theme, theme);
  }
  async function assertContrast() {
    const findings = await page.evaluate(() => {
      function rgba(css) {
        const canvas = document.createElement('canvas'); canvas.width = canvas.height = 1;
        const ctx = canvas.getContext('2d'); ctx.fillStyle = css; ctx.fillRect(0, 0, 1, 1);
        const [r,g,b,a] = ctx.getImageData(0,0,1,1).data; return [r,g,b,a / 255];
      }
      function background(node) {
        const chain = []; for (let p = node; p; p = p.parentElement) chain.unshift(p);
        return chain.reduce((bg, p) => {const c = rgba(getComputedStyle(p).backgroundColor); return c.slice(0,3).map((v,i) => v*c[3]+bg[i]*(1-c[3]));}, [255,255,255]);
      }
      function luminance(c) {return c.map(v => v/255).map(v => v<=0.04045?v/12.92:((v+0.055)/1.055)**2.4).reduce((v,x,i) => v+x*[0.2126,0.7152,0.0722][i],0);}
      return [...document.querySelectorAll('.stn-search-heading,.stn-search-description,.stn-search-label,.stn-search-eyebrow,.stn-search-category,.stn-search-submit,.stn-search-input,.stn-search-results [class*="bg-rose-50"],.stn-search-results [class*="bg-emerald-50"],.stn-search-results [class*="bg-violet-50"],.stn-search-results [class*="bg-white/70"]')].flatMap(node => {
        const checks = [getComputedStyle(node).color];
        if (node.matches('input')) checks.push(getComputedStyle(node,'::placeholder').color);
        return checks.map(color => {const fg=rgba(color).slice(0,3),bg=background(node),a=luminance(fg),b=luminance(bg);return {label: node.className, ratio:(Math.max(a,b)+.05)/(Math.min(a,b)+.05)};});
      });
    });
    for (const f of findings) assert(f.ratio >= 4.5, `${f.label}: contrast ${f.ratio}`);
  }
  async function assertScroll(width, height) {
    await page.setViewportSize({width,height});
    const result = await page.evaluate(() => {
      const scroll = document.querySelector('[data-workspace-scroll]');
      scroll.scrollTop = scroll.scrollHeight;
      const owners = [...document.querySelectorAll('.stn-content *')].filter(e => /auto|scroll/.test(getComputedStyle(e).overflowY) && e.scrollHeight > e.clientHeight+1);
      const last = document.querySelector('.stn-dashboard .stn-action-card:last-child') || document.querySelector('.stn-search-results');
      const end = last.getBoundingClientRect(), box = scroll.getBoundingClientRect();
      return {owners:owners.map(e=>e.className), bodyHeight:document.documentElement.scrollHeight,
        bodyWidth:document.documentElement.scrollWidth, atEnd:end.bottom <= box.bottom-50, atStart:end.top >= box.top,
        owner: owners[0]?.hasAttribute('data-workspace-scroll')};
    });
    assert(result.owners.length <= 1 && (result.owners.length === 0 || result.owner), JSON.stringify(result));
    assert(result.bodyHeight <= height+1 && result.bodyWidth <= width+1, JSON.stringify(result));
    assert(result.atEnd, 'Bottom of content is obscured: '+JSON.stringify(result));
  }
  for (const theme of ['classic', 'studio']) {
    for (const path of ['/member', '/member/sellers']) {
      await page.setViewportSize({width:1440,height:900});
      await open(path,theme);
      await page.getByRole('heading',{name:'Search seller by GSTIN'}).waitFor();
      assert.equal(await page.getByRole('heading',{name:'Seed marketplace'}).count(),0);
      assert.equal(await page.locator('.market-workspace').count(),0);
      assert.equal(await page.locator('.stn-content').getByLabel('Seller GSTIN',{exact:true}).count(),1);
      const firstTop = await page.locator('.stn-search-panel').evaluate(e=>e.getBoundingClientRect().top);
      const scrollTop = await page.locator('[data-workspace-scroll]').evaluate(e=>e.getBoundingClientRect().top);
      assert(firstTop-scrollTop < 40, 'Search must be first in dashboard content');
      const input = page.getByLabel('Seller GSTIN',{exact:true});
      const submit = page.getByRole('button',{name:'Search seller',exact:true});
      assert(await submit.isDisabled());
      await assertContrast();
      await input.fill('27abcde1234f1z5');
      assert.equal(await input.inputValue(),'27ABCDE1234F1Z5');
      await submit.click();
      await page.getByRole('heading',{name:'Sample seller for layout checks'}).waitFor();
      assert.equal(await page.locator('.stn-search-results article').count(),16);
      assert.equal(await page.evaluate(()=>window.searchCalls[0].query),'27ABCDE1234F1Z5');
      await assertContrast();
      for (const [w,h] of [[1440,900],[1152,720],[960,600],[720,450],[390,844]]) await assertScroll(w,h);
      await page.setViewportSize({width:1440,height:900});
      await page.locator('[data-workspace-scroll]').evaluate(e=>e.scrollTop=0);
      if (process.env.STN_LAYOUT_SCREENSHOTS) await page.screenshot({path:`${process.env.STN_LAYOUT_SCREENSHOTS}/${theme}-${path.endsWith('sellers')?'sellers':'dashboard'}.png`});
      await page.evaluate(()=>window.searchMode='empty'); await input.fill('27ABCDE1234F1Z6'); await submit.click();
      await page.getByText('No approved record found',{exact:true}).waitFor();
      await page.evaluate(()=>window.searchMode='error'); await submit.click();
      await page.getByText('Sample service unavailable. Try again.',{exact:true}).waitFor();
      await assertContrast();
      await page.evaluate(()=>window.searchMode='delay'); await submit.click();
      await page.waitForFunction(()=>typeof window.resolveSearch==='function');
      await input.fill('27ABCDE1234F1Z7'); await page.evaluate(()=>window.resolveSearch());
      await submit.waitFor({state:'visible'});
      await page.waitForFunction(()=>!document.querySelector('.stn-search-submit').disabled);
      assert.equal(await page.getByRole('heading',{name:'Sample seller for layout checks'}).count(),0,'Stale response must be discarded');
      assert.equal(await page.locator('.stn-search-results').count(),0,'Editing clears previous result');
      console.log('PASS',theme,path,'accepted search layout, contrast >=4.5, valid/empty/error/stale search, 16 results, one content scroller at 5 viewport/zoom-equivalent sizes');
    }
    await open('/member?disabled=1',theme);
    await page.getByText('Seller search is disabled',{exact:true}).waitFor();
    assert.equal(await page.locator('.stn-search-input').count(),0);
    await open('/member?preview=1',theme);
    await page.getByText('Administrator preview · Fictional company · No membership data is changed.',{exact:true}).waitFor();
    assert.equal(await page.locator('.stn-search-input').count(),0);
    console.log('PASS',theme,'disabled search and administrator preview remain non-interactive');
  }
  assert.deepEqual(errors,[]);
} finally { await browser.close(); }
