import { reportDb } from "./report-store";
import { mongoDb } from "./sql-mongo";

export type AdminCounts = {
  pendingMembers: number;
  approvedMembers: number;
  deactivatedMembers: number;
  rejectedMembers: number;
  totalMembers: number;
  pendingReports: number;
  approvedReports: number;
  rejectedReports: number;
  totalReports: number;
  pendingResolutions: number;
  approvedResolutions: number;
  rejectedResolutions: number;
  openDisputes: number;
  resolvedDisputes: number;
  totalDisputedPaise: number;
  openDisputedPaise: number;
  resolvedDisputedPaise: number;
  pendingPasswordResets: number;
  expiringMemberships: number;
  unusualLast24: number;
};

export type AuditEntry = {
  source: string;
  action: string;
  actor: string;
  subject: string;
  details: string | null;
  created_at: number;
};

/** Match numeric 1 or boolean true for flag fields stored inconsistently. */
const flagTrue = { $in: [1, true, "1"] };
const flagNotTrue = { $nin: [1, true, "1"] };
const pendingStatus = {
  $or: [{ status: "pending" }, { status: null }, { status: "" }, { status: { $exists: false } }],
};

function asNumber(value: unknown) {
  const n = Number(value);
  return Number.isFinite(n) ? n : 0;
}

function isFlagTrue(value: unknown) {
  return value === 1 || value === true || value === "1";
}

async function sumDisputeAmounts(db: Awaited<ReturnType<typeof mongoDb>>) {
  const rows = await db
    .collection("seller_reports")
    .find({
      dispute: flagTrue,
      status: { $in: ["pending", "approved"] },
    })
    .project({ amount_paise: 1, resolved_amount_paise: 1, dispute_resolved: 1, status: 1 })
    .toArray();

  let total = 0;
  let resolved = 0;
  let open = 0;

  for (const row of rows) {
    const amount = asNumber(row.amount_paise);
    const resolvedAmount = asNumber(row.resolved_amount_paise);
    const done = isFlagTrue(row.dispute_resolved) || (amount > 0 && resolvedAmount >= amount);
    total += amount;
    if (done) {
      resolved += resolvedAmount > 0 ? resolvedAmount : amount;
    } else {
      open += Math.max(0, amount - resolvedAmount);
      // Partial resolutions still count toward resolved total
      resolved += resolvedAmount;
    }
  }

  return { total, resolved, open };
}

export async function adminCounts(): Promise<AdminCounts> {
  const db = await mongoDb();
  const now = Date.now();
  const expireUntil = now + 30 * 24 * 60 * 60 * 1000;
  const last24 = now - 24 * 60 * 60 * 1000;

  const approvedDispute = { status: "approved", dispute: flagTrue };

  const [
    pendingMembers,
    approvedMembers,
    deactivatedMembers,
    rejectedMembers,
    totalMembers,
    pendingReports,
    approvedReports,
    rejectedReports,
    totalReports,
    pendingResolutions,
    approvedResolutions,
    rejectedResolutions,
    openDisputes,
    resolvedDisputes,
    pendingPasswordResets,
    unusualLast24,
    disputeTotals,
    expiringMemberships,
  ] = await Promise.all([
    db.collection("members").countDocuments(pendingStatus),
    db.collection("members").countDocuments({ status: "approved" }),
    db.collection("members").countDocuments({ status: "deactivated" }),
    db.collection("members").countDocuments({ status: "rejected" }),
    db.collection("members").countDocuments({}),
    db.collection("seller_reports").countDocuments(pendingStatus),
    db.collection("seller_reports").countDocuments({ status: "approved" }),
    db.collection("seller_reports").countDocuments({ status: "rejected" }),
    db.collection("seller_reports").countDocuments({}),
    db.collection("dispute_resolution_requests").countDocuments({ status: "pending" }),
    db.collection("dispute_resolution_requests").countDocuments({ status: "approved" }),
    db.collection("dispute_resolution_requests").countDocuments({ status: "rejected" }),
    // Open = approved/pending disputes not fully resolved (flag or amount-paid)
    db.collection("seller_reports").countDocuments({
      dispute: flagTrue,
      status: { $in: ["pending", "approved"] },
      $nor: [
        { dispute_resolved: flagTrue },
        {
          $expr: {
            $and: [
              { $gt: [{ $ifNull: ["$amount_paise", 0] }, 0] },
              {
                $gte: [
                  { $ifNull: ["$resolved_amount_paise", 0] },
                  { $ifNull: ["$amount_paise", 0] },
                ],
              },
            ],
          },
        },
      ],
    }),
    // Resolved = approved disputes fully closed (flag OR paid in full)
    db.collection("seller_reports").countDocuments({
      ...approvedDispute,
      $or: [
        { dispute_resolved: flagTrue },
        {
          $expr: {
            $and: [
              { $gt: [{ $ifNull: ["$amount_paise", 0] }, 0] },
              {
                $gte: [
                  { $ifNull: ["$resolved_amount_paise", 0] },
                  { $ifNull: ["$amount_paise", 0] },
                ],
              },
            ],
          },
        },
      ],
    }),
    db.collection("password_reset_requests").countDocuments({ status: "pending" }),
    db.collection("security_events").countDocuments({
      severity: "warning",
      created_at: { $gte: last24 },
    }),
    sumDisputeAmounts(db),
    db.collection("members").countDocuments({
      status: "approved",
      $or: [
        {
          subscription_ends_at: { $gte: now, $lte: expireUntil },
        },
        {
          subscription_ends_at: { $in: [null, ""] },
          trial_ends_at: { $gte: now, $lte: expireUntil },
        },
        {
          subscription_ends_at: { $exists: false },
          trial_ends_at: { $gte: now, $lte: expireUntil },
        },
      ],
    }),
  ]);

  return {
    pendingMembers: asNumber(pendingMembers),
    approvedMembers: asNumber(approvedMembers),
    deactivatedMembers: asNumber(deactivatedMembers),
    rejectedMembers: asNumber(rejectedMembers),
    totalMembers: asNumber(totalMembers),
    pendingReports: asNumber(pendingReports),
    approvedReports: asNumber(approvedReports),
    rejectedReports: asNumber(rejectedReports),
    totalReports: asNumber(totalReports),
    pendingResolutions: asNumber(pendingResolutions),
    approvedResolutions: asNumber(approvedResolutions),
    rejectedResolutions: asNumber(rejectedResolutions),
    openDisputes: asNumber(openDisputes),
    resolvedDisputes: asNumber(resolvedDisputes),
    totalDisputedPaise: asNumber(disputeTotals.total),
    openDisputedPaise: asNumber(disputeTotals.open),
    resolvedDisputedPaise: asNumber(disputeTotals.resolved),
    pendingPasswordResets: asNumber(pendingPasswordResets),
    expiringMemberships: asNumber(expiringMemberships),
    unusualLast24: asNumber(unusualLast24),
  };
}

export async function auditEntries(limit = 500): Promise<AuditEntry[]> {
  const result = await reportDb()
    .prepare(
      `SELECT source,action,actor,subject,details,created_at FROM (
 SELECT 'membership' source,a.action,CASE WHEN a.actor_user_id LIKE 'member:%' THEN COALESCE(m.company_name,'Member') WHEN a.action='member.registered' THEN COALESCE(m.company_name,'Applicant') ELSE 'Administrator' END actor,COALESCE(m.company_name,'Company membership') subject,a.details,a.created_at created_at FROM audit_logs a LEFT JOIN members m ON m.id=a.target_member_id
 UNION ALL
 SELECT 'seller report' source,a.action,CASE WHEN a.actor LIKE 'member:%' THEN COALESCE(m.company_name,'Member') ELSE 'Administrator' END actor,COALESCE(r.firm_name,'Seller report') subject,NULL details,a.created_at created_at FROM report_audit a LEFT JOIN seller_reports r ON r.id=a.report_id LEFT JOIN members m ON m.id=r.member_id
 UNION ALL
 SELECT 'security' source,e.event_type action,COALESCE(m.company_name,'Public visitor') actor,COALESCE(e.details,'Security event') subject,CONCAT('Network ref: ',substr(COALESCE(e.network_hash,'unknown'),1,10)) details,e.created_at created_at FROM security_events e LEFT JOIN members m ON m.id=e.member_id
 ) AS activity ORDER BY created_at DESC LIMIT ?`,
    )
    .bind(limit)
    .all<AuditEntry>();
  return result.results;
}

export function actionLabel(action: string) {
  return (
    (
      {
        "member.registered": "Company registered",
        "member.approved": "Company reactivated",
        "member.rejected": "Company rejected",
        "member.deactivated": "Company deactivated",
        "member.approved_credentials_issued": "Membership approved and credentials issued",
        "member.credentials_reset": "Member credentials reset",
        "member.password_changed": "Member changed password",
        "admin.export_members": "Member records exported",
        "admin.export_reports": "Approved reports exported",
        submitted: "Seller report submitted",
        edited: "Pending report edited",
        revision_requested: "Approved report change requested",
        approved: "Seller report approved",
        rejected: "Seller report rejected",
        resolution_requested: "Dispute resolution requested",
        resolution_approved: "Dispute resolution approved",
        resolution_rejected: "Dispute resolution rejected",
        repeated_failed_login: "Repeated failed login attempts",
        concurrent_login_replaced: "Earlier member session replaced",
        gstin_search_rate_limited: "Excessive GSTIN searches blocked",
        registration_rate_limited: "Excessive registrations blocked",
        repeated_invalid_upload: "Repeated invalid uploads",
        duplicate_seller_submission: "Duplicate seller submission blocked",
      } as Record<string, string>
    )[action] || action.replaceAll("_", " ").replaceAll(".", " ")
  );
}
