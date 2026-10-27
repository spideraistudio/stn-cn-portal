"use client";
import { useState } from "react";
import { Eye, EyeOff, Loader2 } from "lucide-react";
import { readJsonResponse } from "@/lib/client-response";

export function AdminLoginForm({returnTo="/admin"}:{returnTo?:string}){
  const [busy,setBusy]=useState(false),[error,setError]=useState(""),[showPassword,setShowPassword]=useState(false);
  return (
    <form className="mt-6 space-y-5" onSubmit={async e=>{
      e.preventDefault();setBusy(true);setError("");
      try{
        const f=new FormData(e.currentTarget),response=await fetch("/api/admin-auth",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({loginId:f.get("loginId"),password:f.get("password")})}),data=await readJsonResponse<{error?:string;redirect?:string}>(response);
        if(!response.ok)throw new Error(data.error||"Sign in failed.");
        window.location.href=data.redirect||returnTo;
      }catch(c){setError(c instanceof Error?c.message:"Sign in failed.");setBusy(false);}
    }}>
      <label className="block text-sm font-medium text-slate-700">Administrator ID
        <input name="loginId" required autoComplete="username" className="mt-2 h-12 w-full rounded-xl border border-slate-200 bg-white px-4 text-base uppercase outline-none transition focus:border-[#15388c] focus:ring-4 focus:ring-[#15388c]/10"/>
      </label>
      <label className="block text-sm font-medium text-slate-700">Password
        <div className="relative mt-2">
          <input name="password" type={showPassword?"text":"password"} required autoComplete="current-password" className="h-12 w-full rounded-xl border border-slate-200 bg-white px-4 pr-12 text-base outline-none transition focus:border-[#15388c] focus:ring-4 focus:ring-[#15388c]/10"/>
          <button type="button" onClick={()=>setShowPassword(v=>!v)} className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 transition hover:text-slate-600" tabIndex={-1} aria-label={showPassword?"Hide password":"Show password"}>
            {showPassword?<EyeOff className="size-5"/>:<Eye className="size-5"/>}
          </button>
        </div>
      </label>
      {error&&<div role="alert" className="rounded-xl border border-rose-200 bg-rose-50 p-3 text-sm text-rose-700">{error}</div>}
      <button disabled={busy} className="flex h-12 w-full items-center justify-center gap-2 rounded-xl bg-[#15388c] font-semibold text-white shadow-lg shadow-[#15388c]/20 transition hover:bg-[#1d46a8] hover:shadow-xl disabled:opacity-50">
        {busy&&<Loader2 className="size-5 animate-spin"/>}
        {busy?"Signing in…":"Sign in to admin panel"}
      </button>
    </form>
  );
}
