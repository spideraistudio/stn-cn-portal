import {UnifiedUsersEditor} from "@/components/unified-users-editor";
import { requireChatGPTUser } from '@/app/chatgpt-auth';
import {combinedPortal,portalIdentity} from '@/lib/portal-session';
import {redirect} from 'next/navigation';
import {UnifiedAccountForm} from '@/components/unified-account-form';
export default async function CNManagement(){await requireChatGPTUser('/admin/cn');if(combinedPortal()&&(await portalIdentity())?.role!=='superadmin')redirect('/account');return <main><h1 className="mb-4 text-xl font-bold">Company users & application access</h1><UnifiedUsersEditor/><div className="mt-6"><UnifiedAccountForm/></div><p className="mt-5"><a href="/portal/manage">Edit existing company/module access</a> · <a href="/account">Existing users, password resets & quotas</a></p></main>;}
