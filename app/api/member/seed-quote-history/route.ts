import { NextResponse } from "next/server";
import { currentMember } from "@/lib/member-session";
import { categoryAccess } from "@/lib/category-access";
import { listOwnSeedQuotations } from "@/lib/seed-trading";

export async function GET(){
  const member=await currentMember();
  if(!member||member.mustChangePassword||categoryAccess(member)?.id!=="agriculture")return NextResponse.json({error:"Approved Agriculture membership required."},{status:403,headers:{"Cache-Control":"private, no-store"}});
  return NextResponse.json({quotations:await listOwnSeedQuotations(member)},{headers:{"Cache-Control":"private, no-store"}});
}
