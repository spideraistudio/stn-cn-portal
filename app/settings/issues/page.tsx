import {portalIdentity} from '@/lib/portal-session';
import {reportMember,reportDb} from '@/lib/report-store';
import {PilotIssueForm} from '@/components/pilot-issue-form';
import {ContactForm} from '@/components/contact-form';
export default async function Issues(){
 const identity=await portalIdentity();
 const member=identity?.modules.stn&&identity.stn_member_id?await reportMember():null;
 if(!member)return <><h1 className="mb-3 text-2xl font-bold">Report a problem</h1><p className="mb-6">Describe whether the problem is in CN Calculator, STN or your account. This form prepares an email to support; send it from your email application. In-app problem tracking is available for approved STN members.</p><ContactForm/></>;
 const result=await reportDb().prepare('SELECT id,issue_type,page_url,description,status,admin_notes,created_at,screenshot_name FROM pilot_issues WHERE member_id=? ORDER BY created_at DESC LIMIT 50').bind(member.id).all();
 return <><h1 className="mb-3 text-2xl font-bold">Report a problem</h1><p className="mb-6">Tell us which application and page you were using. Existing reports for your STN membership are shown below.</p><PilotIssueForm issues={result.results as React.ComponentProps<typeof PilotIssueForm>['issues']}/></>;
}
