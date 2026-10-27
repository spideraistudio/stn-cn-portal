import {portalIdentity} from '@/lib/portal-session';
import {redirect} from 'next/navigation';
import {UnifiedAccountForm} from '@/components/unified-account-form';
import {UnifiedUsersEditor} from '@/components/unified-users-editor';
export default async function Users(){const identity=await portalIdentity();if(!identity||identity.role==='user'||!identity.manage_users)redirect('/account');return <><h1 className="mb-3 text-2xl font-bold">Company users</h1><p className="mb-6">Each person has an individual login and private CN work. Manage only the accounts within your permissions.</p><UnifiedAccountForm/><UnifiedUsersEditor/></>}
