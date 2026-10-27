import Link from "next/link";
import { CredentialForm } from "@/components/credential-form";
import { PublicHeader } from "@/components/public-header";
export const dynamic="force-dynamic";
export default function Login(){return <main className="public-site"><PublicHeader/><div className="public-container public-login"><section><p className="public-eyebrow">WELCOME BACK</p><h1>Your business workspace awaits.</h1><p className="public-lead">Sign in using the credentials shared by your administrator. Your access follows your company’s approved membership and permissions.</p><p className="public-muted">Applied recently? Please wait for approval and your credentials before signing in.</p></section><section className="public-card"><h2>Member login</h2><p>Use your Member ID and password.</p><CredentialForm/><p>New company? <Link href="/join">Register for approval</Link></p></section></div></main>}
