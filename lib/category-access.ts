import type { Member } from "@/lib/member-data";

// The persisted membership is authoritative. Never accept a category from a URL
// or form as authorization. 'other' is a request, never a shared data partition.
export function categoryAccess(member: Pick<Member, "status" | "category" | "otherCategory">) {
  if (member.status !== "approved") return null;
  if (member.category === "agriculture") return { id: "agriculture", label: "Agriculture" } as const;
  return null;
}
