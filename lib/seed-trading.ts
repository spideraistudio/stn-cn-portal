import { randomUUID } from "node:crypto";
import { ObjectId } from "mongodb";
import { mongoDb } from "@/lib/sql-mongo";
import type { Member, MemberId } from "@/lib/member-data";
import { notifyMember } from "@/lib/notifications";
import type { SeedRequest } from "@/lib/seed-requests";

export type SeedQuotationStatus = "submitted"|"shortlisted"|"declined"|"selected";
export class SeedConflictError extends Error {}
export type SeedQuotationRevision = { revisedAt:number; values: Omit<SeedQuotation,"revisions"|"revealBuyerName"|"everRevealed"|"status"> };
export type SeedQuotation = {
  id:string; requestId:string; supplierId:MemberId; supplierCompany:string; status:SeedQuotationStatus;
  createdAt:number; updatedAt:number; offeredProduct:string; crop:string; segment:string; varietyType:"hybrid"|"research";
  deviation:string; quantity:number; quantityUnit:"kg"|"MT"; price:number; priceUnit:"kg"|"MT"; normalizedPricePerKg:number;
  cleaning:"clean"|"raw"; treatment:"treated"|"untreated"; earliestDelivery:string; transportIncluded:boolean;
  pricingBasis:string; paymentType:"cash"|"credit"; creditDays:number|null; creditStarts:string;
  germinationAvailable:boolean; gotAvailable:boolean; validUntil:string; remarks:string;
  revealBuyerName:boolean; everRevealed:boolean; revisions:SeedQuotationRevision[];
};
export type SeedSupplierContact = { email:string; mobileNumber:string };
export type SeedBuyerQuotation = SeedQuotation & { supplierContact?:SeedSupplierContact };
export type SeedBuyerContact = SeedSupplierContact & { companyName:string };
export type SeedOwnQuotation = SeedQuotation & { buyerContact?:SeedBuyerContact };

function idKey(id:MemberId){ return typeof id === "string" && ObjectId.isValid(id) ? new ObjectId(id) : id; }
export function isExpired(r:SeedRequest, now=Date.now()){return r.quotationDeadline <= now;}
export function selectionError(r:SeedRequest, candidate:SeedQuotation, otherSelected:SeedQuotation[], now=Date.now()){
  if(r.status!=="published")return "This request is closed or cancelled.";
  const validityEnd=Date.parse(`${candidate.validUntil}T23:59:59+05:30`);
  if(!Number.isFinite(validityEnd)||validityEnd<now)return "This quotation is no longer valid.";
  const required=r.quantity*(r.quantityUnit==="MT"?1000:1);
  const selected=otherSelected.reduce((sum,q)=>sum+q.quantity*(q.quantityUnit==="MT"?1000:1),0);
  const offered=candidate.quantity*(candidate.quantityUnit==="MT"?1000:1);
  if(selected+offered>required+0.000001)return "Approved quotations would exceed the required quantity.";
  return null;
}
export function supplierCanAccess(r:SeedRequest, member: Pick<Member,"id"|"state">){
  if(String(r.ownerId)===String(member.id)) return true;
  if(r.status!=="published" || isExpired(r)) return false;
  return r.panIndia || r.supplierStates.includes(member.state);
}
export function supplierCanQuote(r:SeedRequest,member:Pick<Member,"id"|"state">){
  return String(r.ownerId)!==String(member.id) && supplierCanAccess(r,member);
}
export function buyerLabel(r:SeedRequest, q?:Pick<SeedQuotation,"revealBuyerName">){return !r.anonymous || q?.revealBuyerName ? r.ownerCompany : "Anonymous buyer";}
export function supplierRequestView(r:SeedRequest, q?:Pick<SeedQuotation,"revealBuyerName">){
  const {ownerId,ownerCompany,_id,...rest}=r as SeedRequest & {_id?:unknown};
  void ownerId; void ownerCompany; void _id;
  return {...rest,ownerCompany:buyerLabel(r,q)};
}

export async function getSeedRequest(id:string){return (await mongoDb()).collection<SeedRequest>("seed_buy_requests").findOne({id});}
export async function listAccessibleSeedRequests(member:Member){
  const all=await (await mongoDb()).collection<SeedRequest>("seed_buy_requests").find({status:"published",quotationDeadline:{$gt:Date.now()}}).sort({createdAt:-1}).toArray();
  const accessible=all.filter(r=>supplierCanQuote(r,member));
  const ownQuotes=accessible.length?await (await mongoDb()).collection<SeedQuotation>("seed_quotations").find({supplierId:member.id,requestId:{$in:accessible.map(r=>r.id)}},{projection:{requestId:1,revealBuyerName:1}}).toArray():[];
  const quotes=new Map(ownQuotes.map(q=>[q.requestId,q]));
  return accessible.map(r=>supplierRequestView(r,quotes.get(r.id)));
}
export async function notifyEligibleSeedMembers(r:SeedRequest){
  const db=await mongoDb();
  const query:any={status:"approved",category:"agriculture","notification_preferences.seed_buy":true,_id:{$ne:idKey(r.ownerId)}};
  if(!r.panIndia) query.state={$in:r.supplierStates};
  const members=await db.collection("members").find(query,{projection:{_id:1}}).toArray();
  await Promise.all(members.map(m=>notifyMember(typeof m._id === "number" ? m._id : String(m._id),{type:"seed_requirement",title:"New Seed buying requirement",message:`${r.crop} · ${r.quantity} ${r.quantityUnit}. A requirement matching your approved company state is available.`,href:`/member/buy-sell/${r.id}`})));
  return members.length;
}

const txt=(v:unknown,max:number)=>typeof v==="string"?v.trim().slice(0,max):"";
const yn=(v:unknown)=>typeof v==="boolean";
const dateOnly=(v:unknown)=>{
  if(typeof v!=="string"||!/^\d{4}-\d{2}-\d{2}$/.test(v))return false;
  const [year,month,day]=v.split("-").map(Number);
  const d=new Date(Date.UTC(year,month-1,day));
  return d.getUTCFullYear()===year&&d.getUTCMonth()+1===month&&d.getUTCDate()===day;
};
export function validateQuotation(raw:Record<string,unknown>, r:SeedRequest, now=Date.now()){
  if(r.status!=="published"||isExpired(r,now))throw new Error("This request is closed or the quotation deadline has passed.");
  const quantity=Number(raw.quantity), price=Number(raw.price);
  if(!Number.isFinite(quantity)||quantity<=0)throw new Error("Enter a positive offered quantity.");
  if(!["kg","MT"].includes(String(raw.quantityUnit)))throw new Error("Choose kg or MT for offered quantity.");
  const offeredKg=quantity*(raw.quantityUnit==="MT"?1000:1), requestedKg=r.quantity*(r.quantityUnit==="MT"?1000:1);
  if(offeredKg>requestedKg)throw new Error("Offered quantity cannot exceed the requirement.");
  if(!r.partialAllowed && Math.abs(offeredKg-requestedKg)>0.000001)throw new Error("This buyer does not accept partial quantities.");
  if(!Number.isFinite(price)||price<=0||!["kg","MT"].includes(String(raw.priceUnit)))throw new Error("Enter a positive price and price unit.");
  const validUntil=txt(raw.validUntil,10), earliestDelivery=txt(raw.earliestDelivery,10);
  const validEnd=Date.parse(`${validUntil}T23:59:59+05:30`), deliveryStart=Date.parse(`${earliestDelivery}T00:00:00+05:30`);
  if(!dateOnly(validUntil)||!Number.isFinite(validEnd)||validEnd<now||validEnd>Date.parse(`${r.deliveryBy}T23:59:59+05:30`))throw new Error("Quotation validity must be today/future and no later than the required delivery date.");
  if(!dateOnly(earliestDelivery)||!Number.isFinite(deliveryStart)||deliveryStart>Date.parse(`${r.deliveryBy}T23:59:59+05:30`))throw new Error("Choose a delivery date no later than the buyer requirement.");
  if(![raw.germinationAvailable,raw.gotAvailable,raw.transportIncluded].every(yn))throw new Error("Complete all Yes/No declarations.");
  const paymentType=String(raw.paymentType); if(!["cash","credit"].includes(paymentType))throw new Error("Choose cash or credit.");
  const creditDays=paymentType==="credit"?Number(raw.creditDays):null; if(paymentType==="credit"&&(!Number.isInteger(creditDays)||Number(creditDays)<0||Number(creditDays)>365))throw new Error("Enter valid credit days.");
  const offeredProduct=txt(raw.offeredProduct,240), crop=txt(raw.crop,80), segment=txt(raw.segment,80); if(!offeredProduct||!crop||!segment)throw new Error("Enter offered product, crop and segment.");
  if(!["hybrid","research"].includes(String(raw.varietyType))||!["clean","raw"].includes(String(raw.cleaning))||!["treated","untreated"].includes(String(raw.treatment)))throw new Error("Complete product and condition choices.");
  const pricingBasis=txt(raw.pricingBasis,300); if(!pricingBasis)throw new Error("State the delivery and pricing basis.");
  return {offeredProduct,crop,segment,varietyType:raw.varietyType as "hybrid"|"research",deviation:txt(raw.deviation,700),quantity,quantityUnit:raw.quantityUnit as "kg"|"MT",price,priceUnit:raw.priceUnit as "kg"|"MT",normalizedPricePerKg:price/(raw.priceUnit==="MT"?1000:1),cleaning:raw.cleaning as "clean"|"raw",treatment:raw.treatment as "treated"|"untreated",earliestDelivery,transportIncluded:raw.transportIncluded as boolean,pricingBasis,paymentType:paymentType as "cash"|"credit",creditDays,creditStarts:paymentType==="credit"?txt(raw.creditStarts,180):"",germinationAvailable:raw.germinationAvailable as boolean,gotAvailable:raw.gotAvailable as boolean,validUntil,remarks:txt(raw.remarks,700)};
}
export async function upsertQuotation(r:SeedRequest,supplier:Member,values:ReturnType<typeof validateQuotation>){
  const col=(await mongoDb()).collection<SeedQuotation>("seed_quotations"); const now=Date.now();
  const existing=await col.findOne({requestId:r.id,supplierId:supplier.id});
  if(existing){
    if(existing.status==="selected")throw new SeedConflictError("This quotation was approved by the buyer and can no longer be revised.");
    const snapshot:any={...existing}; delete snapshot.revisions; delete snapshot.revealBuyerName; delete snapshot.everRevealed; delete snapshot.status; delete (snapshot as any)._id;
    const revisions=[...(existing.revisions||[]),{revisedAt:now,values:snapshot}];
    const updated=await col.findOneAndUpdate({id:existing.id,updatedAt:existing.updatedAt},{$set:{...values,updatedAt:now,status:"submitted",revisions}},{returnDocument:"after"});
    if(!updated)throw new SeedConflictError("Quotation changed while you were editing. Reload and review the latest terms.");
    return updated;
  }
  const q:SeedQuotation={...values,id:randomUUID(),requestId:r.id,supplierId:supplier.id,supplierCompany:supplier.companyName,status:"submitted",createdAt:now,updatedAt:now,revealBuyerName:!r.anonymous,everRevealed:!r.anonymous,revisions:[]};
  try {await col.insertOne(q);} catch(error){if(error && typeof error==="object" && "code" in error && error.code===11000)throw new SeedConflictError("A quotation already exists. Reload before revising it.");throw error;} return q;
}
export async function getOwnQuotation(requestId:string,supplierId:MemberId){return (await mongoDb()).collection<SeedQuotation>("seed_quotations").findOne({requestId,supplierId});}
export async function supplierQuotationView(r:SeedRequest,q:SeedQuotation|null):Promise<SeedOwnQuotation|null>{
  if(!q||q.status!=="selected")return q;
  const buyer=await (await mongoDb()).collection<{_id:ObjectId|string|number;status:string;company_name?:string;email?:string;mobile_number?:string}>("members").findOne({_id:idKey(r.ownerId),status:"approved"},{projection:{company_name:1,email:1,mobile_number:1}});
  return buyer?{...q,buyerContact:{companyName:String(buyer.company_name||r.ownerCompany),email:String(buyer.email||""),mobileNumber:String(buyer.mobile_number||"")}}:q;
}
export function supplierCanReadOwnHistory(r:SeedRequest,member:Pick<Member,"state">,q:SeedQuotation|null){return Boolean(q&&(r.panIndia||r.supplierStates.includes(member.state)));}
export async function listOwnSeedQuotations(member:Member){
  const db=await mongoDb();const quotes=await db.collection<SeedQuotation>("seed_quotations").find({supplierId:member.id}).sort({updatedAt:-1}).toArray();
  if(!quotes.length)return [];
  const requests=await db.collection<SeedRequest>("seed_buy_requests").find({id:{$in:quotes.map(q=>q.requestId)}}).toArray();
  const map=new Map(requests.map(r=>[r.id,r]));
  return quotes.flatMap(q=>{const r=map.get(q.requestId);return r&&supplierCanReadOwnHistory(r,member,q)?[{id:q.id,requestId:q.requestId,crop:r.crop,segment:r.segment,offeredQuantity:q.quantity,quantityUnit:q.quantityUnit,price:q.price,priceUnit:q.priceUnit,status:q.status,updatedAt:q.updatedAt}]:[]});
}
export async function listBuyerQuotations(requestId:string,buyerId:MemberId):Promise<SeedBuyerQuotation[]|null>{
  const r=await getSeedRequest(requestId);if(!r||String(r.ownerId)!==String(buyerId))return null;
  const db=await mongoDb();
  const offers=await db.collection<SeedQuotation>("seed_quotations").find({requestId}).sort({normalizedPricePerKg:1}).toArray();
  const selected=offers.filter(q=>q.status==="selected");
  if(!selected.length)return offers;
  const members=await db.collection<{_id:ObjectId|string|number;status:string;email?:string;mobile_number?:string}>("members").find({_id:{$in:selected.map(q=>idKey(q.supplierId))},status:"approved"},{projection:{email:1,mobile_number:1}}).toArray();
  const contacts=new Map(members.map(m=>[String(m._id),{email:String(m.email||""),mobileNumber:String(m.mobile_number||"")} ]));
  return offers.map(q=>q.status==="selected"&&contacts.has(String(q.supplierId))?{...q,supplierContact:contacts.get(String(q.supplierId))}:q);
}
export async function buyerAct(requestId:string,buyerId:MemberId,quotationId:string,action:"shortlisted"|"declined"|"selected"|"submitted"){
  const r=await getSeedRequest(requestId); if(!r||String(r.ownerId)!==String(buyerId))return null;
  const db=await mongoDb();
  const col=db.collection<SeedQuotation>("seed_quotations");
  const before=await col.findOne({id:quotationId,requestId});if(!before)return null;
  if(before.status==="selected"&&action!=="selected")return null;
  if(action==="selected"&&before.status!=="selected"){
    const others=await col.find({requestId,status:"selected",id:{$ne:quotationId}}).toArray();
    const problem=selectionError(r,before,others);
    if(problem)throw new SeedConflictError(problem);
  }
  const disclosure=action==="selected"&&r.anonymous&&!before.revealBuyerName;
  const changes:Partial<SeedQuotation>={status:action,updatedAt:Date.now()};
  if(action==="selected"){changes.revealBuyerName=true;changes.everRevealed=true;}
  const updated=await col.findOneAndUpdate({id:quotationId,requestId},{$set:changes},{returnDocument:"after"});
  if(action==="selected"&&before.status!=="selected"&&updated)await db.collection("audit_logs").insertOne({actor_user_id:String(buyerId),action:"seed.quotation_selected_contact_unlocked",target_member_id:before.supplierId,details:JSON.stringify({requestId,quotationId}),created_at:Date.now()});
  if(disclosure&&updated)await db.collection("audit_logs").insertOne({actor_user_id:String(buyerId),action:"seed.buyer_contact_revealed_on_selection",target_member_id:before.supplierId,details:JSON.stringify({requestId,quotationId}),created_at:Date.now()});
  return updated;
}
export async function setBuyerReveal(requestId:string,buyerId:MemberId,quotationId:string,reveal:boolean){
  const r=await getSeedRequest(requestId); if(!r||String(r.ownerId)!==String(buyerId)||!r.anonymous)return null; const db=await mongoDb(); const q=await db.collection<SeedQuotation>("seed_quotations").findOne({id:quotationId,requestId}); if(!q)return null;
  if(q.status==="selected"&&!reveal)throw new SeedConflictError("Buyer contact has already been shared with the approved supplier.");
  const update:any={$set:{revealBuyerName:reveal,updatedAt:Date.now()}}; if(reveal)update.$set.everRevealed=true; const result=await db.collection<SeedQuotation>("seed_quotations").findOneAndUpdate({id:quotationId},update,{returnDocument:"after"});
  if(reveal&&!q.revealBuyerName)await db.collection("audit_logs").insertOne({actor_user_id:String(buyerId),action:"seed.buyer_name_revealed",target_member_id:q.supplierId,details:JSON.stringify({requestId,quotationId}),created_at:Date.now()});
  return result;
}
