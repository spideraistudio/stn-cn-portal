"use strict";
(() => {
 const originalFetch=window.fetch.bind(window);
 window.cnWebFetch=originalFetch;
 window.fetch=async(input,options={})=>{
  if(typeof input!=="string"||!input.startsWith('/api/'))return originalFetch(input,options);
  const url=new URL(input,location.origin);
  if(!url.pathname.startsWith('/api/calculator/')&&!/^\/api\/(me|auth\/|admin\/|data\/|ledger\/|projects\/|files\/|workspace)/.test(url.pathname)){
   input='/api/calculator/'+url.pathname.slice(5);
   const headers=new Headers(options.headers||{});
   if(url.searchParams.has('record_id'))headers.set('X-CN-Record',url.searchParams.get('record_id'));
   options={...options,headers};
  }
  if(input.startsWith('/api/calculator/')){
   const response=await originalFetch('/api/me',{credentials:'same-origin'});
   if(!response.ok){location.assign('/');throw Error('Sign in to continue.');}
   const me=await response.json(),headers=new Headers(options.headers||{});
   headers.set('X-CSRF-Token',me.csrf_token);
   if(!headers.has('X-CN-Project'))headers.set('X-CN-Project',globalThis.cnWebProject||'main');
   if(!headers.has('X-CN-Workbook'))headers.set('X-CN-Workbook',globalThis.cnWebWorkbook||'legacy');
   options={...options,headers,credentials:'same-origin'};
  }
  return originalFetch(input,options);
 };
})();

addEventListener('DOMContentLoaded',()=>{const a=document.createElement('a');a.href='/portal';a.textContent='⇄ Switch application';a.style.cssText='position:fixed;bottom:10px;left:12px;z-index:9999;padding:8px 14px;border-radius:8px;background:#112e48;color:#aaf4da;font:600 12px system-ui;text-decoration:none';document.body.append(a)});
