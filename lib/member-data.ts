import { env } from "@/lib/runtime-env";
import { reportDb } from "./report-store";
import { mongoDb } from "./sql-mongo";
import { notifyMember } from "./notifications";
export type RegistrationInput={authUserId:string;companyName:string;address:string;taluka:string;district:string;state:string;pincode:string;gstin:string;responsiblePersonName:string;mobileNumber:string;email:string;category:"agriculture"|"other";otherCategory?:string|null};
export function isConfiguredAdmin(email:string){return (env.ADMIN_EMAILS||"").split(",").map(v=>v.trim().toLowerCase()).filter(Boolean).includes(email.toLowerCase());}
// Member row shape produced by memberFromRow (camelCase projection of the
// snake_case members collection). The input row is dynamically shaped by sql-mongo.
type MemberRow = Record<string, unknown>;
export type MemberId = string | number;
export const MEMBER_LOGIN_ID_PATTERN=/^MEM[0-9A-F]{6,}$/i;
export function isMemberLoginId(value:string){return MEMBER_LOGIN_ID_PATTERN.test(value.trim());}
export function parseMemberId(value:unknown):MemberId|null{
  if(typeof value==="number" && Number.isInteger(value) && value>0)return value;
  const text=String(value??"").trim();
  if(/^[a-fA-F0-9]{24}$/.test(text))return text;
  if(/^[1-9][0-9]*$/.test(text))return Number(text);
  return null;
}
function rowId(value:unknown):MemberId{
  const parsed=parseMemberId(value);
  if(parsed!=null)return parsed;
  if(value && typeof value==="object" && typeof (value as {toHexString?:()=>string}).toHexString==="function")return (value as {toHexString:()=>string}).toHexString();
  return String(value??"");
}
export type Member = {
  id:MemberId;authUserId:string;loginId:string|null;passwordHash:string|null;
  mustChangePassword:boolean;credentialVersion:number;failedLogins:number;lockedUntil:number|null;
  companyName:string;address:string;taluka:string;district:string;state:string;pincode:string;gstin:string;
  responsiblePersonName:string;mobileNumber:string;email:string;category:string;otherCategory:string|null;
  isPilot:boolean;searchEnabled:boolean;membershipPlan:string;trialEndsAt:number|null;
  subscriptionStartsAt:number|null;subscriptionEndsAt:number|null;role:string;status:string;
  adminNotes:string|null;reviewedBy:string|null;reviewedAt:Date|null;createdAt:Date;updatedAt:Date;
};
const str = (v:unknown):string => v==null?"":String(v);
const numOrNull = (v:unknown):number|null => v===null||v===undefined||v===""?null:Number(v);
function asDate(v:unknown){const n=Number(v);return Number.isFinite(n)&&n>0?new Date(n):null;}
// Returns a camelCase projection of the members table row. The return type is
// intentionally `any` because the 35-field projection is consumed by many dense
// admin pages that rely on loose property access.
// eslint-disable-next-line @typescript-eslint/no-explicit-any
export function memberFromRow(r:MemberRow|null):any{if(!r)return null;return {id:rowId(r.id),authUserId:str(r.auth_user_id),loginId:r.login_id===null||r.login_id===undefined?null:str(r.login_id),passwordHash:r.password_hash===null||r.password_hash===undefined?null:str(r.password_hash),mustChangePassword:Boolean(r.must_change_password),credentialVersion:Number(r.credential_version||0),failedLogins:Number(r.failed_logins||0),lockedUntil:numOrNull(r.locked_until),companyName:str(r.company_name),address:str(r.address),taluka:str(r.taluka),district:str(r.district),state:str(r.state),pincode:str(r.pincode),gstin:str(r.gstin),responsiblePersonName:str(r.responsible_person_name),mobileNumber:str(r.mobile_number),email:str(r.email),category:str(r.category||"agriculture"),otherCategory:r.other_category===null||r.other_category===undefined?null:str(r.other_category),isPilot:Boolean(r.is_pilot),searchEnabled:Boolean(r.search_enabled),membershipPlan:str(r.membership_plan||"free"),trialEndsAt:numOrNull(r.trial_ends_at),subscriptionStartsAt:numOrNull(r.subscription_starts_at),subscriptionEndsAt:numOrNull(r.subscription_ends_at),role:str(r.role||"member"),status:str(r.status||"pending"),adminNotes:r.admin_notes===null||r.admin_notes===undefined?null:str(r.admin_notes),reviewedBy:r.reviewed_by===null||r.reviewed_by===undefined?null:str(r.reviewed_by),reviewedAt:asDate(r.reviewed_at),createdAt:asDate(r.created_at)||new Date(),updatedAt:asDate(r.updated_at)||new Date()};}
export async function getMemberByAuthId(authUserId:string){return memberFromRow(await reportDb().prepare("SELECT * FROM members WHERE auth_user_id=? LIMIT 1").bind(authUserId).first<MemberRow>());}
export async function createRegistration(i:RegistrationInput){const now=Date.now(),db=reportDb();const result=await db.prepare("INSERT INTO members(auth_user_id,company_name,address,taluka,district,state,pincode,gstin,responsible_person_name,mobile_number,email,category,other_category,status,role,created_at,updated_at) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,'pending','member',?,?) RETURNING id").bind(i.authUserId,i.companyName,i.address,i.taluka,i.district,i.state,i.pincode,i.gstin,i.responsiblePersonName,i.mobileNumber,i.email,i.category,i.otherCategory||null,now,now).first<{id:MemberId}>();const id=result?.id;await db.prepare("INSERT INTO audit_logs(actor_user_id,action,target_member_id,created_at) VALUES(?,'member.registered',?,?)").bind(i.authUserId,id,now).run();return memberFromRow(await db.prepare("SELECT * FROM members WHERE id=?").bind(id).first<MemberRow>());}
function memberDocToRow(doc:Record<string,unknown>):MemberRow{
  const {_id,...rest}=doc;
  return {...rest,id:_id};
}
export async function listMembersForAdmin(){
  const db=await mongoDb();
  const [docs,stats]=await Promise.all([
    db.collection("members").find({}).sort({created_at:-1}).toArray(),
    db.collection("seller_reports").aggregate<{_id:unknown;reported_disputes:number;resolved_disputes:number}>([
      {$match:{status:"approved",dispute:{$in:[1,true,"1"]}}},
      {$group:{
        _id:"$member_id",
        reported_disputes:{$sum:1},
        resolved_disputes:{$sum:{$cond:[
          {$or:[
            {$in:["$dispute_resolved",[1,true,"1"]]},
            {$and:[
              {$gt:[{$ifNull:["$amount_paise",0]},0]},
              {$gte:[{$ifNull:["$resolved_amount_paise",0]},{$ifNull:["$amount_paise",0]}]},
            ]},
          ]},
          1,
          0,
        ]}},
      }},
    ]).toArray(),
  ]);
  const map=new Map(stats.map(r=>[String(r._id),r]));
  return docs.map(doc=>{
    const member=memberFromRow(memberDocToRow(doc as Record<string,unknown>));
    const row=map.get(String(member.id));
    return {...member,reportedDisputes:Number(row?.reported_disputes||0),resolvedDisputes:Number(row?.resolved_disputes||0)};
  });
}
export async function reviewMember(id:MemberId,status:"approved"|"rejected"|"deactivated",actorUserId:string,notes?:string){const db=reportDb(),existing=memberFromRow(await db.prepare("SELECT * FROM members WHERE id=?").bind(id).first<MemberRow>());if(!existing||(status==="approved"&&existing.status!=="deactivated")||(status==="rejected"&&existing.status!=="pending")||(status==="deactivated"&&existing.status!=="approved"))throw new Error("Invalid membership transition.");const now=Date.now();await db.batch([db.prepare("UPDATE members SET status=?,credential_version=credential_version+1,admin_notes=?,reviewed_by=?,reviewed_at=?,updated_at=? WHERE id=?").bind(status,notes||null,actorUserId,now,now,id),db.prepare("INSERT INTO audit_logs(actor_user_id,action,target_member_id,details,created_at) VALUES(?,?,?,?,?)").bind(actorUserId,`member.${status}`,id,notes||null,now)]);const title=status==="approved"?"Membership reactivated":status==="rejected"?"Membership rejected":"Membership deactivated";await notifyMember(id,{type:`membership_${status}`,title,message:notes?`${title}. Administrator note: ${notes}`:`${title}.`,href:status==="approved"?"/login":"/"});}
