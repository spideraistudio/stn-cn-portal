"use server";

import { revalidatePath } from "next/cache";
import { requireChatGPTUser } from "./chatgpt-auth";
import { isConfiguredAdmin, reviewMember, parseMemberId } from "@/lib/member-data";

const field = (form: FormData, key: string, max = 200) => String(form.get(key) ?? "").trim().slice(0, max);

export async function changeMemberStatus(form: FormData) {
  const user = await requireChatGPTUser("/");
  if (!isConfiguredAdmin(user.email)) throw new Error("Administrator access required.");
  const id = parseMemberId(form.get("memberId"));
  const requested = field(form, "status");
  if (id==null || !["approved", "rejected", "deactivated"].includes(requested)) throw new Error("Invalid review request.");
  await reviewMember(id, requested as "approved" | "rejected" | "deactivated", user.userId, field(form, "adminNotes", 1000));
  revalidatePath("/");
  revalidatePath("/admin");
  revalidatePath("/join");
  revalidatePath("/member");
}
