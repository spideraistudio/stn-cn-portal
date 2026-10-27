import { ObjectId } from "mongodb";
import { mongoDb } from "@/lib/sql-mongo";
import type { Member, MemberId } from "@/lib/member-data";

type MemberPreferenceDocument = {
  _id: ObjectId | number | string;
  notification_preferences?: { seed_buy?: boolean };
  status?: string;
  category?: string;
  credential_version?: number;
};

function memberKey(id: MemberId) {
  return typeof id === "string" && ObjectId.isValid(id) ? new ObjectId(id) : id;
}

// Missing preference means off, including for all members created before Phase 1.
export async function seedNotificationsEnabled(id: MemberId): Promise<boolean> {
  const db = await mongoDb();
  const record = await db.collection<MemberPreferenceDocument>("members").findOne(
    { _id: memberKey(id) },
    { projection: { "notification_preferences.seed_buy": 1 } },
  );
  return record?.notification_preferences?.seed_buy === true;
}

export async function setSeedNotifications(member: Member, enabled: boolean) {
  const db = await mongoDb();
  const result = await db.collection<MemberPreferenceDocument>("members").updateOne(
    {
      _id: memberKey(member.id),
      status: "approved",
      category: "agriculture",
    },
    { $set: { "notification_preferences.seed_buy": enabled, updated_at: Date.now() } },
  );
  return result.matchedCount === 1;
}
