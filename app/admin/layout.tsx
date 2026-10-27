import { WorkspaceShell } from "@/components/workspace-shell";
import { combinedPortal } from '@/lib/portal-session';
import { requireChatGPTUser } from '@/app/chatgpt-auth';

export default async function AdminLayout({ children }: { children: React.ReactNode }) {
  if(combinedPortal())await requireChatGPTUser('/admin');
  return <WorkspaceShell admin>{children}</WorkspaceShell>;
}
