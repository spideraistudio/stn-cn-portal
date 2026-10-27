"use client";
import { Button } from "@/components/ui/button";
export default function MemberError({ reset }: { reset: () => void }) {
  return <main className="grid min-h-screen place-items-center bg-slate-50 p-6"><section className="max-w-lg rounded-2xl border bg-white p-8"><h1 className="text-2xl font-semibold">Workspace temporarily unavailable</h1><p className="my-4 text-slate-600">Your membership details could not be loaded. Please try again.</p><Button onClick={reset}>Try again</Button></section></main>;
}
