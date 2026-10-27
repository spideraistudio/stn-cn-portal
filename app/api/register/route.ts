import { readJsonBody } from "@/lib/request-body";
import { NextResponse } from "next/server";
import { createRegistration } from "@/lib/member-data";
import { consumeLimit,networkHash,recordSecurityEvent } from "@/lib/security";
import { notifyAdmin } from "@/lib/notifications";
import { validateIndianLocation } from "@/lib/india-locations";

const value = (data: Record<string, unknown>, key: string, max = 200) => String(data[key] ?? "").trim().slice(0, max);

export async function POST(request: Request) {
  if(Number(request.headers.get("content-length")||0)>20*1024)return NextResponse.json({error:"Registration request is too large."},{status:413});
  try {
    const limited=await consumeLimit(request,"public_registration",networkHash(request),5,30*60*1000);if(!limited.allowed){if(limited.count===6)await recordSecurityEvent(request,"registration_rate_limited",null,"More than five registration attempts within 30 minutes");return NextResponse.json({error:`Too many registration attempts. Try again in about ${Math.ceil(limited.retryAfterSeconds/60)} minute(s).`},{status:429,headers:{"Retry-After":String(limited.retryAfterSeconds)}});}
    const data = await readJsonBody(request) as Record<string, unknown>;
    if(value(data,"website",200))return NextResponse.json({success:true});
    const gstin = value(data, "gstin", 15).toUpperCase();
    const mobileNumber = value(data, "mobileNumber", 20).replace(/\D/g, "");
    const category = value(data, "category") === "other" ? "other" : "agriculture";
    const required = ["companyName", "address", "taluka", "district", "state", "responsiblePersonName"];
    if (required.some(key => value(data, key).length < 2)) return NextResponse.json({ error: "Please complete every required company field." }, { status: 400 });
    if (!/^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z][1-9A-Z]Z[0-9A-Z]$/.test(gstin)) return NextResponse.json({ error: "Enter a valid 15-character GSTIN." }, { status: 400 });
    if (!/^[6-9][0-9]{9}$/.test(mobileNumber)) return NextResponse.json({ error: "Enter a valid 10-digit Indian mobile number." }, { status: 400 });
    const email = value(data, "email", 320).toLowerCase();
    if (!/^\S+@\S+\.\S+$/.test(email)) return NextResponse.json({ error: "Enter a valid email address." }, { status: 400 });
    const otherCategory = category === "other" ? value(data, "otherCategory", 100) : null;
    if (category === "other" && !otherCategory) return NextResponse.json({ error: "Please specify the other business category." }, { status: 400 });
    const location=validateIndianLocation(value(data,"state",80),value(data,"district",100),value(data,"pincode",6));
    if(!location.valid)return NextResponse.json({error:location.error},{status:400});
    await createRegistration({ authUserId: `public:${crypto.randomUUID()}`, companyName: value(data, "companyName"), address: value(data, "address", 1000), taluka: value(data, "taluka", 100), district: location.district!, state: location.state!, pincode: location.pincode!, gstin, responsiblePersonName: value(data, "responsiblePersonName"), mobileNumber, email, category, otherCategory });
    await notifyAdmin({type:"member_registration",title:"New company registration",message:`${value(data,"companyName")} submitted a membership application.`,href:"/admin#companies"});
    return NextResponse.json({ success: true });
  } catch (error) {
    console.error("[registration]", error);
    const code = (error as { code?: string } | null)?.code;
    const duplicate = Boolean(code === "11000" || (error instanceof Error && /duplicate key/i.test(error.message)));
    return NextResponse.json({ error: duplicate ? "This GSTIN or mobile number is already registered." : "The application could not be saved. Please try again." }, { status: duplicate?409:500 });
  }
}
