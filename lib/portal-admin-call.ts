import {cookies} from 'next/headers';
export async function portalAdminCall(action:string,body:unknown){
 const origin=process.env.PORTAL_ORIGIN;if(!origin)throw Error('Common portal unavailable');
 const cookie=(await cookies()).toString();
 const me=await fetch(origin+'/api/me',{headers:{Cookie:cookie},cache:'no-store'});
 if(!me.ok)throw Error('Sign in again');const identity=await me.json();
 const r=await fetch(origin+'/api/portal/'+action,{method:'POST',headers:{Cookie:cookie,Origin:origin,'Content-Type':'application/json','X-CSRF-Token':identity.csrf_token},body:JSON.stringify(body),cache:'no-store'});
 const result=await r.json();if(!r.ok)throw Error(result.error||'Account creation failed');return result;
}
