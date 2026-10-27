/* eslint-disable @next/next/no-location-assign-relative-destination -- Python portal routes require full document navigation across the same-origin gateway. */
'use client';
export function PortalSwitch({admin=false}:{admin?:boolean}){
 if(process.env.NEXT_PUBLIC_COMMON_PORTAL!=='1')return null;
 async function signOut(){const me=await fetch('/api/me').then(r=>r.json());await fetch('/api/auth/logout',{method:'POST',headers:{'Content-Type':'application/json','X-CSRF-Token':me.csrf_token},body:'{}'});location.assign('/portal');}
 return <nav className="flex gap-3 text-xs font-semibold text-blue-900"><a href="/portal">Switch application</a>{admin&&<a href="/portal/manage">CN & companies</a>}<a href="/account">Account & Settings</a><button onClick={signOut}>Sign out</button></nav>;
}
