'use client';
import {usePathname} from 'next/navigation';
export function SharedSettingsReturn(){const path=usePathname();if(process.env.NEXT_PUBLIC_COMMON_PORTAL!=='1'||!['/about','/contact','/privacy','/terms','/disclaimer'].includes(path))return null;return <nav className="flex flex-wrap gap-5 border-b bg-white px-5 py-3 text-sm font-semibold text-slate-800"><a href="/portal">STN + CN portal</a><a href="/account">Account &amp; Settings</a></nav>}
