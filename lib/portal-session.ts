import { cookies } from 'next/headers';
export const combinedPortal = () => process.env.PORTAL_MODE === 'combined';
export type PortalIdentity = {id:string;username:string;role:'superadmin'|'admin'|'user';manage_users:boolean;modules:{cn:boolean;stn:boolean};stn_member_id:string|null};
export async function portalIdentity():Promise<PortalIdentity|null> {
  if(!combinedPortal())return null;
  const token=(await cookies()).get(process.env.PORTAL_COOKIE_NAME||(process.env.NODE_ENV==='production'?'__Host-cn_session':'cn_dev_session'))?.value;
  if(!token || !/^[A-Za-z0-9_-]{43}$/.test(token))return null;
  try{
    const endpoint=process.env.PORTAL_IDENTITY_URL, secret=process.env.PORTAL_BRIDGE_KEY,origin=process.env.PORTAL_ORIGIN;
    if(!endpoint||!secret||!origin)return null;
    const url=new URL(endpoint);
    if(!['127.0.0.1','localhost'].includes(url.hostname))throw Error('Local identity endpoint required');
    const response=await fetch(url,{method:'POST',headers:{'X-Portal-Key':secret,'Host':new URL(origin).host,'Cookie':`${process.env.PORTAL_COOKIE_NAME||(process.env.NODE_ENV==='production'?'__Host-cn_session':'cn_dev_session')}=${token}`},cache:'no-store',signal:AbortSignal.timeout(5000)});
    if(!response.ok)return null;
    return await response.json() as PortalIdentity;
  }catch{return null;}
}
export async function verifyPortalPassword(password:string):Promise<boolean>{
 const identity=await portalIdentity();if(!identity)return false;
 const cookieName=process.env.PORTAL_COOKIE_NAME||(process.env.NODE_ENV==='production'?'__Host-cn_session':'cn_dev_session');
 const token=(await cookies()).get(cookieName)?.value;
 const base=process.env.PORTAL_IDENTITY_URL,secret=process.env.PORTAL_BRIDGE_KEY,origin=process.env.PORTAL_ORIGIN;
 if(!base||!secret||!origin)return false;
 try{const response=await fetch(new URL('/internal/portal/verify-password',base),{method:'POST',headers:{'Host':new URL(origin).host,'X-Portal-Key':secret,'Cookie':`${cookieName}=${token}`,'Content-Type':'application/json'},body:JSON.stringify({password}),cache:'no-store',signal:AbortSignal.timeout(5000)});return response.ok&&(await response.json()).valid===true;}catch{return false;}
}
