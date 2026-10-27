import { NextResponse } from "next/server";
import { currentMember } from "@/lib/member-session";
import { categoryAccess } from "@/lib/category-access";
import { listAccessibleSeedRequests } from "@/lib/seed-trading";
const reply=(body:object,status=200)=>NextResponse.json(body,{status,headers:{"Cache-Control":"private, no-store"}});
export async function GET(){const m=await currentMember();if(!m||m.mustChangePassword||categoryAccess(m)?.id!=="agriculture")return reply({error:"Approved Agriculture membership required."},403);return reply({requests:await listAccessibleSeedRequests(m)});}
