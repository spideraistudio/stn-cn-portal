import { ReportShell } from "@/components/report-shell";
import { notFound,redirect } from "next/navigation";
import { requireApprovedMember } from "@/lib/member-session";
import { categoryAccess } from "@/lib/category-access";
import { getOwnQuotation,getSeedRequest,supplierCanAccess,supplierCanReadOwnHistory,supplierQuotationView,listBuyerQuotations,supplierRequestView } from "@/lib/seed-trading";
import { SeedTradingDetail } from "@/components/seed-trading-detail";
export const dynamic="force-dynamic";
export default async function Page({params}:{params:Promise<{id:string}>}){const member=await requireApprovedMember();if(categoryAccess(member)?.id!=="agriculture")redirect("/member");const {id}=await params;const item=await getSeedRequest(id);if(!item)notFound();const owner=String(item.ownerId)===String(member.id);const ownQuote=owner?null:await getOwnQuotation(id,member.id);if(!supplierCanAccess(item,member)&&!supplierCanReadOwnHistory(item,member,ownQuote))notFound();const quotations=owner?await listBuyerQuotations(id,member.id):null;const safe=owner?item:supplierRequestView(item,ownQuote||undefined);return <ReportShell title="Seed buying request" description={owner?"Manage your requirement and quotations received.":"Review the requirement and your private quotation."}><SeedTradingDetail item={JSON.parse(JSON.stringify(safe))} owner={owner} ownQuote={JSON.parse(JSON.stringify(owner?null:await supplierQuotationView(item,ownQuote)))} quotations={JSON.parse(JSON.stringify(quotations||[]))}/></ReportShell>;}
