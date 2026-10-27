'use strict';
// Browser-local appearance only. No account, workbook or financial writes.
(()=>{
 const key='stn-cn-theme';let stored=null;
 try{stored=localStorage.getItem(key);}catch{/* Storage may be disabled. */}
 const valid=t=>t==='classic'||t==='studio';
 let current=valid(stored)?stored:'studio',hasPreference=valid(stored);
 function apply(theme){current=valid(theme)?theme:'studio';document.documentElement.dataset.suiteTheme=current;document.documentElement.style.colorScheme=current==='studio'?'dark':'light';const select=document.getElementById('suite-theme');if(select)select.value=current;}
 function set(theme){if(!valid(theme))return;hasPreference=true;try{localStorage.setItem(key,theme);}catch{/* Remains usable for this page. */}apply(theme);document.dispatchEvent(new CustomEvent('suite:themechange',{detail:{theme}}));}
 globalThis.SuiteTheme={apply,set,current:()=>current,hasPreference:()=>hasPreference};apply(current);
 document.addEventListener('DOMContentLoaded',()=>{const select=document.getElementById('suite-theme');if(select){select.value=current;select.addEventListener('change',e=>set(e.target.value));}});
 window.addEventListener('storage',e=>{if(e.key===key&&valid(e.newValue)){hasPreference=true;apply(e.newValue);document.dispatchEvent(new CustomEvent('suite:themechange',{detail:{theme:e.newValue}}));}});
})();
