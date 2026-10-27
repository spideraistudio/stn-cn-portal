import type { Member } from "@/lib/member-data";
import type { DashboardProfile } from "@/components/member-dashboard";
import { categoryAccess } from "./category-access";

export function dashboardProfile(member: Member): DashboardProfile {
  return {
    companyName: member.companyName, gstin: member.gstin, address: member.address,
    taluka: member.taluka, district: member.district, state: member.state, pincode: member.pincode,
    responsiblePersonName: member.responsiblePersonName, mobileNumber: member.mobileNumber,
    email: member.email, categoryLabel: categoryAccess(member)?.label ?? null, isPilot: Boolean(member.isPilot),
    requestedCategory: member.category === "other" ? member.otherCategory : null,
    searchEnabled: Boolean(member.searchEnabled),
    approvedOn: member.reviewedAt ? member.reviewedAt.toLocaleDateString("en-IN", { timeZone: "Asia/Kolkata" }) : "Not recorded",
  };
}
