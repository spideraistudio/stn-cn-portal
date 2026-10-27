import { JoinForm } from "@/components/join-form";
import { PublicHeader } from "@/components/public-header";
export const dynamic="force-dynamic";
export default function JoinPage(){return <main className="public-site"><PublicHeader/><div className="public-container public-registration"><div className="public-intro"><p className="public-eyebrow">COMPANY APPLICATION</p><h1>Let’s get your company started.</h1><p className="public-lead">Enter your registered business details for administrator review. After approval, your administrator will share credentials and set your STN and CN access.</p><p className="public-muted">All fields are required. Submitting an application does not create an active login.</p></div><JoinForm/></div></main>}
