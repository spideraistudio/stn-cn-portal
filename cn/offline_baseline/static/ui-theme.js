/* Appearance only. Never writes financial settings, records or allocation inputs. */
'use strict';
const cnAppearance={theme:'classic',serial:0};
function cnSetTheme(theme){
 cnAppearance.theme=theme==='studio'?'studio':'classic';
 document.documentElement.dataset.cnTheme=cnAppearance.theme;
 const select=document.getElementById('cn-ui-theme');if(select)select.value=cnAppearance.theme;
 document.dispatchEvent(new CustomEvent('cn:themechange',{detail:{theme:cnAppearance.theme}}));
}
async function cnLoadTheme(){
 const seq=cnAppearance.serial;
 try{const r=await fetch('/api/ui-preferences',{headers:{'X-CN-Project':'main'}});if(!r.ok)return;const p=await r.json();if(seq===cnAppearance.serial)cnSetTheme(p.theme);}catch{ /* Classic remains usable if reading a preference fails. */ }
}
document.getElementById('cn-ui-theme')?.addEventListener('change',async e=>{
 const theme=e.target.value,old=cnAppearance.theme,seq=++cnAppearance.serial;
 cnSetTheme(theme);e.target.disabled=true;
 try{await api('/api/ui-preferences',{theme});if(seq===cnAppearance.serial)toast((theme==='studio'?'Navy Studio':'Classic')+' interface saved.');}
 catch(err){if(seq===cnAppearance.serial)cnSetTheme(old);toast('Interface preference could not be saved: '+err.message);}
 finally{e.target.disabled=false;}
});
cnLoadTheme();
