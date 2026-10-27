/* Appearance only. Never writes financial settings, records or allocation inputs. */
'use strict';
const cnAppearance={theme:'studio',serial:0};
function cnSetTheme(theme){
 cnAppearance.theme=theme==='studio'?'studio':'classic';
 document.documentElement.dataset.cnTheme=cnAppearance.theme;
 globalThis.SuiteTheme?.apply(cnAppearance.theme);
 const select=document.getElementById('cn-ui-theme');if(select)select.value=cnAppearance.theme;
 document.dispatchEvent(new CustomEvent('cn:themechange',{detail:{theme:cnAppearance.theme}}));
}
async function cnLoadTheme(){
 if(globalThis.SuiteTheme?.hasPreference())return;
 const seq=cnAppearance.serial;
 try{const r=await fetch('/api/ui-preferences',{headers:{'X-CN-Project':'main'}});if(!r.ok)return;const p=await r.json();if(seq===cnAppearance.serial)cnSetTheme(p.theme);}catch{ /* Navy Studio remains usable if reading a preference fails. */ }
}
document.getElementById('cn-ui-theme')?.addEventListener('change',async e=>{
 const theme=e.target.value,old=cnAppearance.theme,seq=++cnAppearance.serial;
 cnSetTheme(theme);e.target.disabled=true;
 try{await api('/api/ui-preferences',{theme});globalThis.SuiteTheme?.set(theme);if(seq===cnAppearance.serial)toast((theme==='studio'?'Navy Studio':'Classic')+' interface saved.');}
 catch(err){if(seq===cnAppearance.serial)cnSetTheme(old);toast('Interface preference could not be saved: '+err.message);}
 finally{e.target.disabled=false;}
});
document.addEventListener('suite:themechange',e=>{if(e.detail.theme!==cnAppearance.theme){cnAppearance.serial++;cnSetTheme(e.detail.theme);}});
cnSetTheme(globalThis.SuiteTheme?.current()||'studio');
cnLoadTheme();
