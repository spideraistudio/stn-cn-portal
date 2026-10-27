import { NextResponse } from "next/server";
import { DB } from "@/lib/runtime-env";
export async function GET(){try{await DB.ping();return NextResponse.json({ok:true,database:"connected",storage:"mongodb"},{headers:{"Cache-Control":"no-store"}});}catch{return NextResponse.json({ok:false,database:"unavailable"},{status:503,headers:{"Cache-Control":"no-store"}});}}
