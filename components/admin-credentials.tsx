/* eslint-disable @next/next/no-location-assign-relative-destination -- Python portal routes require full document navigation across the same-origin gateway. */
"use client";
import { UnifiedPasswordReset } from "./unified-password-reset";
import { UnifiedAccountForm } from "./unified-account-form";
import { useState } from "react";
import { Check, Copy, KeyRound } from "lucide-react";
import { readJsonResponse } from "@/lib/client-response";
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from "@/components/ui/dialog";

function LegacyAdminCredentials({memberId,pending,hasCredentials,compact=false}:{memberId:number|string;pending:boolean;hasCredentials:boolean;compact?:boolean}) {
 const [credentials,setCredentials]=useState<{loginId:string;temporaryPassword:string}|null>(null);
 const [busy,setBusy]=useState(false);
 const [error,setError]=useState("");
 const [copied,setCopied]=useState<"all"|"id"|"password"|null>(null);
 const [dialogTitle,setDialogTitle]=useState("Credentials issued");
 const label=process.env.NEXT_PUBLIC_COMMON_PORTAL==="1"?(busy?"Please wait…":pending?"Approve STN membership":"Manage login in common portal"):busy?"Please wait…":pending?(compact?"Approve & issue ID":"Approve & generate credentials"):hasCredentials?(compact?"Reset password":"Reset temporary password"):(compact?"Issue credentials":"Generate credentials");

 async function issueCredentials(){
  if(process.env.NEXT_PUBLIC_COMMON_PORTAL==="1"&&!pending){location.assign("/account");return;}
  if(process.env.NEXT_PUBLIC_COMMON_PORTAL!=="1" && hasCredentials && !window.confirm("Reset this member’s password? Their current signed-in session will remain active.")) return;
  setBusy(true);setError("");setCopied(null);
  try {
   const r=await fetch("/api/admin/credentials",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({memberId})});
   const data=await readJsonResponse<{error?:string;loginId:string;temporaryPassword:string}>(r);
   if(!r.ok)throw new Error(data.error||"Unable to issue credentials.");
   if("portal" in data){window.alert(String((data as unknown as {message:string;memberId:string}).message)+"\nSTN member ID: "+String((data as unknown as {memberId:string}).memberId));location.reload();return;}
   setDialogTitle(pending?"Membership approved":hasCredentials?"Temporary password reset":"Credentials issued");
   setCredentials(data);
  }catch(e){
   setError(e instanceof Error ? e.message : "Please try again.");
  }finally{
   setBusy(false);
  }
 }

 async function copyText(value:string,which:"all"|"id"|"password"){
  try{
   await navigator.clipboard.writeText(value);
   setCopied(which);
  }catch{
   setError("Copy manually using the text above.");
  }
 }

 function closeAfterCopy(){
  if(!credentials){setError("");return;}
  if(!copied && !window.confirm("Hide credentials? Copy them first — they will not be shown again.")) return;
  window.location.reload();
 }

 const shareText=credentials?`Member login: ${typeof window!=="undefined"?window.location.origin:""}/login\nMember ID: ${credentials.loginId}\nTemporary password: ${credentials.temporaryPassword}\nPlease change your password at first login.`:"";

 return <>
  <div className={compact?"":"mt-0"}>
   <button type="button" disabled={busy} className={`inline-flex h-10 items-center justify-center rounded-[12px] bg-[#15388c] px-4 text-[13px] font-semibold text-white transition hover:bg-[#102d74] disabled:opacity-50 ${compact?"w-full":""}`} onClick={issueCredentials}>{label}</button>
   {error && !credentials && <p role="alert" className="mt-2 text-xs text-rose-700">{error}</p>}
  </div>
  <Dialog open={!!credentials} onOpenChange={open=>{if(!open)closeAfterCopy();}}>
   <DialogContent showCloseButton={false} className="max-h-[min(90vh,36rem)] w-[calc(100%-2rem)] max-w-md gap-0 overflow-y-auto rounded-[12px] border-slate-200 p-0 sm:max-w-md" onPointerDownOutside={event=>event.preventDefault()} onEscapeKeyDown={event=>event.preventDefault()}>
    <DialogHeader className="border-b border-amber-200 bg-amber-50 px-6 py-5 text-left">
     <div className="flex items-start gap-3">
      <span className="grid size-10 shrink-0 place-items-center rounded-xl bg-white text-amber-700 shadow-sm"><KeyRound className="size-5"/></span>
      <div>
       <DialogTitle className="text-lg text-amber-950">{dialogTitle}</DialogTitle>
       <DialogDescription className="mt-1 text-sm text-amber-900">Copy these credentials now. They are shown only once and will not appear again.</DialogDescription>
      </div>
     </div>
    </DialogHeader>
    {credentials&&<div className="space-y-4 px-6 py-5">
     <CredentialField label="Member ID" value={credentials.loginId} copied={copied==="id"} onCopy={()=>copyText(credentials.loginId,"id")}/>
     <CredentialField label="Temporary password" value={credentials.temporaryPassword} copied={copied==="password"} onCopy={()=>copyText(credentials.temporaryPassword,"password")} mono/>
     <p className="rounded-xl border border-amber-200 bg-amber-50 px-4 py-3 text-sm leading-6 text-amber-950">Share privately with this member. They must change the password on first login.</p>
     {error&&<p role="alert" className="text-sm text-rose-700">{error}</p>}
    </div>}
    <div className="flex gap-3 border-t border-slate-100 bg-slate-50 px-6 py-4">
     <button type="button" className="inline-flex flex-1 items-center justify-center gap-2 rounded-xl border border-slate-200 bg-white px-4 py-2.5 text-sm font-semibold text-slate-800 hover:bg-slate-50" onClick={()=>copyText(shareText,"all")}>
      {copied==="all"?<Check className="size-4 text-emerald-700"/>:<Copy className="size-4"/>}
      {copied==="all"?"Copied":"Copy all"}
     </button>
     <button type="button" className="flex-1 rounded-xl bg-[#15388c] px-5 py-2.5 text-sm font-semibold text-white hover:bg-[#102d74]" onClick={()=>window.location.reload()}>Done</button>
    </div>
   </DialogContent>
  </Dialog>
 </>;
}

function CredentialField({label,value,copied,onCopy,mono=false}:{label:string;value:string;copied:boolean;onCopy:()=>void;mono?:boolean}){
 return <div>
  <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">{label}</p>
  <div className="mt-1.5 flex items-center gap-2 rounded-xl border border-slate-200 bg-slate-50 px-3 py-2.5">
   <code className={`min-w-0 flex-1 break-all text-sm font-semibold text-slate-900 ${mono?"font-mono":""}`}>{value}</code>
   <button type="button" className="inline-flex shrink-0 items-center gap-1 rounded-lg border border-slate-200 bg-white px-2.5 py-1.5 text-xs font-semibold text-slate-700 hover:bg-slate-50" onClick={onCopy}>
    {copied?<Check className="size-3.5 text-emerald-700"/>:<Copy className="size-3.5"/>}
    {copied?"Copied":"Copy"}
   </button>
  </div>
 </div>;
}

function CommonAdminCredentials({memberId,pending}:Parameters<typeof LegacyAdminCredentials>[0]){
 const [open,setOpen]=useState(false);
 return <><button type="button" className="w-full whitespace-normal rounded-xl bg-blue-900 px-4 py-2.5 text-sm font-semibold text-white" onClick={()=>setOpen(true)}>{pending?'Approve & create account':'Reset password'}</button><Dialog open={open} onOpenChange={setOpen}><DialogContent className="flex max-h-[calc(100dvh-2rem)] min-w-0 flex-col gap-0 overflow-hidden p-0 sm:max-w-3xl"><DialogHeader className="shrink-0 border-b p-4 pr-12 text-left"><DialogTitle>{pending?'Approve signup & create company admin':'Company login password resets'}</DialogTitle><DialogDescription>{pending?'Review account access and limits, then approve this signup.':'Only explicitly linked individual logins within your permissions appear below.'}</DialogDescription></DialogHeader><div className="min-h-0 overflow-y-auto overscroll-contain p-3 sm:p-5">{pending?<UnifiedAccountForm memberId={memberId}/>:<UnifiedPasswordReset memberId={memberId}/>}</div><div className="shrink-0 border-t bg-white p-3"><button type="button" onClick={()=>setOpen(false)} className="rounded border px-4 py-2">Close</button></div></DialogContent></Dialog></>;
}
export function AdminCredentials(props:Parameters<typeof LegacyAdminCredentials>[0]){return process.env.NEXT_PUBLIC_COMMON_PORTAL==='1'?<CommonAdminCredentials key={props.memberId} {...props}/>:<LegacyAdminCredentials {...props}/>;}
