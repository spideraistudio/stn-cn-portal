import { currentMember } from "@/lib/member-session";
import { reportAdmin } from "@/lib/report-store";
import { unreadNotifications } from "@/lib/notifications";
import { NotificationMenu } from "@/components/notification-menu";
export async function NotificationLink({admin=false}:{admin?:boolean}){const identity=admin?await reportAdmin():await currentMember();if(!identity)return null;const memberId=admin?null:("id" in identity?identity.id:null);const count=await unreadNotifications(admin?"admin":"member",memberId??null);return <NotificationMenu initialCount={count} admin={admin}/>;}
