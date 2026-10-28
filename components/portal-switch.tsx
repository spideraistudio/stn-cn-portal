/* eslint-disable @next/next/no-location-assign-relative-destination -- Python portal routes require full document navigation across the same-origin gateway. */
'use client';
import { useRef, useState } from 'react';
export function PortalSwitch({admin=false}:{admin?:boolean}){
 const busy = useRef(false);
 const [pending, setPending] = useState(false);
 const [error, setError] = useState('');
 if(process.env.NEXT_PUBLIC_COMMON_PORTAL!=='1')return null;
 async function signOut(){
  if(busy.current)return;
  busy.current=true;setPending(true);setError('');
  try{
   const response=await fetch('/api/me',{cache:'no-store'});
   if(response.status===401){location.assign('/portal');return;}
   if(!response.ok)throw new Error('Could not check your session. Please retry sign out.');
   const me=await response.json();
   if(!me.csrf_token)throw new Error('Could not verify your session. Please retry sign out.');
   const result=await fetch('/api/auth/logout',{method:'POST',headers:{'Content-Type':'application/json','X-CSRF-Token':me.csrf_token},body:'{}'});
   if(!result.ok && result.status!==401)throw new Error('Sign-out did not complete. Please retry.');
   location.assign('/portal');
  }catch(e){setError(e instanceof Error?e.message:'Sign-out did not complete. Please retry.');}
  finally{busy.current=false;setPending(false);}
 }
 return <nav aria-label="Shared application navigation" className="flex flex-wrap items-center gap-3 text-xs font-semibold text-blue-900 dark:text-blue-200"><a href="/portal">Switch application</a>{admin&&<a href="/portal/manage">CN & companies</a>}<a href="/account">Account & Settings</a><button disabled={pending} aria-busy={pending} onClick={signOut} className="min-w-24 disabled:opacity-60">{pending?'Signing out…':'Sign out'}</button>{error&&<span role="alert" className="text-red-700 dark:text-red-300">{error}</span>}</nav>;
}
