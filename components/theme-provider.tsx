"use client";
import { ThemeProvider as NextThemesProvider, useTheme } from "next-themes";
import { useEffect } from "react";
const combined=process.env.NEXT_PUBLIC_COMMON_PORTAL==="1";
function SuiteAppearance(){
  const {theme}=useTheme();
  useEffect(()=>{
    if(combined)document.documentElement.dataset.suiteTheme=theme==="classic"?"classic":"studio";
  },[theme]);
  return null;
}
export function ThemeProvider({children,nonce}:{children:React.ReactNode;nonce?:string}){
  return <NextThemesProvider attribute="class" defaultTheme={combined?"studio":"light"} enableSystem={!combined} storageKey={combined?"stn-cn-theme":"theme"} themes={combined?["classic","studio"]:undefined} value={combined?{classic:"light",studio:"dark"}:undefined} disableTransitionOnChange nonce={nonce}><SuiteAppearance/>{children}</NextThemesProvider>;
}
