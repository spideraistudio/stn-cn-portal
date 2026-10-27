import { WorkspaceShell } from "@/components/workspace-shell";
import { combinedPortal } from '@/lib/portal-session';
import { requireApprovedMember } from '@/lib/member-session';

export default async function MemberLayout({ children }: { children: React.ReactNode }) {
  if(combinedPortal())await requireApprovedMember();
  return <WorkspaceShell>{children}</WorkspaceShell>;
}
