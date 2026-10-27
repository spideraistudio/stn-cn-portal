import {UnifiedUsersEditor} from "@/components/unified-users-editor";
import {portalIdentity} from '@/lib/portal-session';
import {redirect} from 'next/navigation';
import {UnifiedAccountForm} from '@/components/unified-account-form';
export default async function Staff(){const identity=await portalIdentity();if(identity?.role!=='admin')redirect('/portal');return <main><h1 className="mb-4 text-xl font-bold">Create company user</h1><UnifiedAccountForm/><UnifiedUsersEditor/><p className="mt-4"><a href="/account">Edit existing users, reset passwords and view allowances</a></p></main>}
