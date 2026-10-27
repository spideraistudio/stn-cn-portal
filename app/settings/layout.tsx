import {portalIdentity} from '@/lib/portal-session';
import {redirect} from 'next/navigation';
export const dynamic='force-dynamic';
export default async function SettingsLayout({children}:{children:React.ReactNode}){
 const identity=await portalIdentity();if(!identity)redirect('/account');
 return <main className="mx-auto max-w-5xl px-5 py-8"><nav className="mb-6 flex flex-wrap gap-5 text-sm font-semibold"><a href="/portal">Switch application</a><a href="/account">Account &amp; Settings</a><a href="/settings/issues">Report a problem</a><a href="/contact">Contact us</a></nav>{children}</main>;
}
