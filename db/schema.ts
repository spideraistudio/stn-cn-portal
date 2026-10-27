import { check, index, integer, sqliteTable, text, uniqueIndex } from "drizzle-orm/sqlite-core";
import { sql } from "drizzle-orm";

/**
 * Legacy Drizzle/SQLite schema kept only for documentation and `drizzle-kit`
 * type generation. Runtime storage is MongoDB via `lib/sql-mongo.ts` +
 * `MONGODB_URI`. Do not treat these tables as a live D1/SQLite database.
 */
export const adminCredentials = sqliteTable("admin_credentials", {
  loginId: text("login_id").primaryKey(),
  passwordHash: text("password_hash").notNull(),
  version: integer("version").notNull(),
  updatedAt: integer("updated_at").notNull(),
});

// Insert/check/delete inside one Mongo batch to abort stale or concurrent mutations.
export const operationGuards = sqliteTable("operation_guards", {
  id: text("id").primaryKey(),
  valid: integer("valid").notNull(),
}, t => [check("operation_guard_valid", sql`${t.valid} = 1`)]);

export const members = sqliteTable("members", {
  id: integer("id").primaryKey({ autoIncrement: true }),
  authUserId: text("auth_user_id").notNull(),
  loginId: text("login_id"),
  passwordHash: text("password_hash"),
  mustChangePassword: integer("must_change_password", { mode: "boolean" }).notNull().default(true),
  credentialVersion: integer("credential_version").notNull().default(0),
  failedLogins: integer("failed_logins").notNull().default(0),
  lockedUntil: integer("locked_until"),
  companyName: text("company_name").notNull(),
  address: text("address").notNull(),
  taluka: text("taluka").notNull(),
  district: text("district").notNull(),
  state: text("state").notNull(),
  pincode: text("pincode").notNull().default(""),
  gstin: text("gstin").notNull(),
  responsiblePersonName: text("responsible_person_name").notNull(),
  mobileNumber: text("mobile_number").notNull(),
  email: text("email").notNull(),
  category: text("category", { enum: ["agriculture", "other"] }).notNull(),
  otherCategory: text("other_category"),
  isPilot: integer("is_pilot", { mode: "boolean" }).notNull().default(false),
  searchEnabled: integer("search_enabled", { mode: "boolean" }).notNull().default(true),
  membershipPlan: text("membership_plan", { enum: ["free", "trial", "monthly", "annual"] }).notNull().default("free"),
  trialEndsAt: integer("trial_ends_at"),
  subscriptionStartsAt: integer("subscription_starts_at"),
  subscriptionEndsAt: integer("subscription_ends_at"),
  role: text("role", { enum: ["member", "admin"] }).notNull().default("member"),
  status: text("status", { enum: ["pending", "approved", "rejected", "deactivated"] }).notNull().default("pending"),
  adminNotes: text("admin_notes"),
  reviewedBy: text("reviewed_by"),
  reviewedAt: integer("reviewed_at", { mode: "timestamp" }),
  createdAt: integer("created_at", { mode: "timestamp" }).notNull().$defaultFn(() => new Date()),
  updatedAt: integer("updated_at", { mode: "timestamp" }).notNull().$defaultFn(() => new Date()),
}, (table) => [
  uniqueIndex("uq_members_login_id").on(table.loginId),
  uniqueIndex("uq_members_auth_user_id").on(table.authUserId),
  uniqueIndex("uq_members_gstin").on(table.gstin),
  uniqueIndex("uq_members_mobile_number").on(table.mobileNumber),
  index("idx_members_category_status").on(table.category, table.status),
]);

export const auditLogs = sqliteTable("audit_logs", {
  id: integer("id").primaryKey({ autoIncrement: true }),
  actorUserId: text("actor_user_id").notNull(),
  action: text("action").notNull(),
  targetMemberId: integer("target_member_id").references(() => members.id),
  details: text("details"),
  createdAt: integer("created_at", { mode: "timestamp" }).notNull().$defaultFn(() => new Date()),
}, (table) => [index("idx_audit_target_created").on(table.targetMemberId, table.createdAt)]);

export type Member = typeof members.$inferSelect;

export const memberSessions = sqliteTable("member_sessions", {
  tokenHash: text("token_hash").primaryKey(),
  memberId: integer("member_id").notNull().references(() => members.id),
  version: integer("version").notNull(),
  expiresAt: integer("expires_at").notNull(),
}, table => [index("idx_sessions_member").on(table.memberId)]);

export const adminSessions = sqliteTable("admin_sessions", {
  tokenHash: text("token_hash").primaryKey(),
  version: integer("version").notNull().default(0),
  loginId: text("login_id").notNull(),
  expiresAt: integer("expires_at").notNull(),
  createdAt: integer("created_at").notNull(),
}, table => [index("idx_admin_sessions_expiry").on(table.expiresAt)]);

export const passwordResetRequests = sqliteTable("password_reset_requests", {
  id: text("id").primaryKey(),
  memberId: integer("member_id").references(() => members.id),
  submittedLoginId: text("submitted_login_id").notNull(),
  submittedEmail: text("submitted_email").notNull(),
  status: text("status").notNull().default("pending"),
  reviewedBy: text("reviewed_by"),
  reviewedAt: integer("reviewed_at"),
  createdAt: integer("created_at").notNull(),
}, table => [index("idx_password_resets_status_created").on(table.status, table.createdAt), index("idx_password_resets_member_status").on(table.memberId, table.status)]);

export const sellers = sqliteTable("sellers", {
 id: text("id").primaryKey(), category: text("category").notNull(),
 gstLookup: text("gst_lookup").notNull(), gstLast4: text("gst_last4").notNull(),
}, t => [uniqueIndex("uq_seller_category_gst").on(t.category,t.gstLookup)]);
export const sellerReports = sqliteTable("seller_reports", {
 id: text("id").primaryKey(), sellerId: text("seller_id").notNull().references(()=>sellers.id),
 revisionOf: text("revision_of"),
 memberId: integer("member_id").notNull().references(()=>members.id), category: text("category").notNull(),
 firmName: text("firm_name").notNull(), personName: text("person_name").notNull(),
 taluka: text("taluka").notNull(), district: text("district").notNull(), state: text("state").notNull(), pincode: text("pincode").notNull().default(""),
 rating: integer("rating").notNull(), dispute: integer("dispute").notNull(), amountPaise: integer("amount_paise"),
 disputeType: text("dispute_type"), disputeOther: text("dispute_other"), legal: integer("legal").notNull(), caseNumber: text("case_number"), caseNumberType: text("case_number_type"), caseNumberHistory: text("case_number_history"),
 disputeStartMonth: text("dispute_start_month"), disputeEndMonth: text("dispute_end_month"), disputeOngoing: integer("dispute_ongoing").notNull().default(0),
 summary: text("summary").notNull(), status: text("status").notNull().default("pending"),
 disputeResolved: integer("dispute_resolved").notNull().default(0), resolvedOn: text("resolved_on"), resolutionSummary: text("resolution_summary"),
 resolvedAmountPaise: integer("resolved_amount_paise").notNull().default(0),
 identityChecked: integer("identity_checked").notNull().default(0), reportReviewed: integer("report_reviewed").notNull().default(0), evidenceReviewed: integer("evidence_reviewed").notNull().default(0), approvedForDisplay: integer("approved_for_display").notNull().default(0),
 reviewNotes: text("review_notes"), reviewer: text("reviewer"), reviewedAt: integer("reviewed_at"), createdAt: integer("created_at").notNull(),
}, t=>[index("idx_reports_revision_status").on(t.revisionOf,t.status),index("idx_reports_seller_status").on(t.sellerId,t.status),index("idx_reports_member_created").on(t.memberId,t.createdAt),index("idx_reports_status_created").on(t.status,t.createdAt)]);
export const reportDocuments = sqliteTable("report_documents", {
 id: text("id").primaryKey(), reportId: text("report_id").notNull().references(()=>sellerReports.id),
 objectKey: text("object_key").notNull(), name: text("name").notNull(), mime: text("mime").notNull(), size: integer("size").notNull(),
},t=>[index("idx_documents_report").on(t.reportId)]);
export const reportAudit = sqliteTable("report_audit", {
 id: text("id").primaryKey(), reportId: text("report_id").notNull().references(()=>sellerReports.id),
 actor: text("actor").notNull(), action: text("action").notNull(), createdAt: integer("created_at").notNull(),
});
export const disputeResolutionRequests = sqliteTable("dispute_resolution_requests", {
 id: text("id").primaryKey(), reportId: text("report_id").notNull().references(()=>sellerReports.id),
 memberId: integer("member_id").notNull().references(()=>members.id), resolvedOn: text("resolved_on").notNull(),
 resolvedAmountPaise: integer("resolved_amount_paise").notNull().default(0),
 description: text("description").notNull(), status: text("status").notNull().default("pending"),
 adminNotes: text("admin_notes"), reviewer: text("reviewer"), reviewedAt: integer("reviewed_at"), createdAt: integer("created_at").notNull(),
},t=>[index("idx_resolution_report_status").on(t.reportId,t.status),index("idx_resolution_status_created").on(t.status,t.createdAt)]);
export const disputeResolutionDocuments = sqliteTable("dispute_resolution_documents", {
 id: text("id").primaryKey(), requestId: text("request_id").notNull().references(()=>disputeResolutionRequests.id),
 objectKey: text("object_key").notNull(), name: text("name").notNull(), mime: text("mime").notNull(), size: integer("size").notNull(),
},t=>[index("idx_resolution_documents_request").on(t.requestId)]);
export const securityRateLimits = sqliteTable("security_rate_limits", {
 key: text("key").primaryKey(), action: text("action").notNull(), windowStart: integer("window_start").notNull(), count: integer("count").notNull(),
},t=>[index("idx_security_limits_action_window").on(t.action,t.windowStart)]);
export const securityEvents = sqliteTable("security_events", {
 id: text("id").primaryKey(), eventType: text("event_type").notNull(), memberId: integer("member_id").references(()=>members.id),
 networkHash: text("network_hash"), details: text("details"), severity: text("severity").notNull().default("warning"), createdAt: integer("created_at").notNull(),
},t=>[index("idx_security_events_created").on(t.createdAt),index("idx_security_events_member_created").on(t.memberId,t.createdAt)]);
export const notifications = sqliteTable("notifications", {
 id: text("id").primaryKey(), audience: text("audience", { enum: ["admin","member"] }).notNull(),
 memberId: integer("member_id").references(()=>members.id), type: text("type").notNull(),
 title: text("title").notNull(), message: text("message").notNull(), href: text("href").notNull(),
 readAt: integer("read_at"), createdAt: integer("created_at").notNull(),
},t=>[index("idx_notifications_audience_read_created").on(t.audience,t.readAt,t.createdAt),index("idx_notifications_member_read_created").on(t.memberId,t.readAt,t.createdAt)]);
export const sellerCorrectionRequests = sqliteTable("seller_correction_requests", {
 id:text("id").primaryKey(),sellerId:text("seller_id").notNull().references(()=>sellers.id),targetReportId:text("target_report_id").references(()=>sellerReports.id),requestType:text("request_type").notNull(),requesterName:text("requester_name").notNull(),requesterEmail:text("requester_email").notNull(),reason:text("reason").notNull(),proposedFirmName:text("proposed_firm_name"),proposedPersonName:text("proposed_person_name"),proposedTaluka:text("proposed_taluka"),proposedDistrict:text("proposed_district"),proposedState:text("proposed_state"),gstCertificateVerified:integer("gst_certificate_verified").notNull().default(0),status:text("status").notNull().default("pending"),decision:text("decision"),adminNotes:text("admin_notes"),reviewer:text("reviewer"),reviewedAt:integer("reviewed_at"),createdAt:integer("created_at").notNull(),
},t=>[index("idx_corrections_status_created").on(t.status,t.createdAt),index("idx_corrections_seller_status").on(t.sellerId,t.status)]);
export const accountDeletionRequests = sqliteTable("account_deletion_requests", {
 id:text("id").primaryKey(),memberId:integer("member_id").notNull().references(()=>members.id),reason:text("reason").notNull(),status:text("status").notNull().default("pending"),adminNotes:text("admin_notes"),reviewer:text("reviewer"),reviewedAt:integer("reviewed_at"),createdAt:integer("created_at").notNull(),
},t=>[index("idx_account_deletions_status_created").on(t.status,t.createdAt),index("idx_account_deletions_member_status").on(t.memberId,t.status)]);
export const profileChangeRequests = sqliteTable("profile_change_requests", {
 id:text("id").primaryKey(),memberId:integer("member_id").notNull().references(()=>members.id),responsiblePersonName:text("responsible_person_name").notNull(),mobileNumber:text("mobile_number").notNull(),email:text("email").notNull(),address:text("address").notNull(),status:text("status").notNull().default("pending"),adminNotes:text("admin_notes"),reviewer:text("reviewer"),reviewedAt:integer("reviewed_at"),createdAt:integer("created_at").notNull(),
},t=>[index("idx_profile_changes_status_created").on(t.status,t.createdAt),index("idx_profile_changes_member_status").on(t.memberId,t.status)]);
export const memberSearches = sqliteTable("member_searches", {
 id:text("id").primaryKey(),memberId:integer("member_id").notNull().references(()=>members.id),searchDate:text("search_date").notNull(),gstLookup:text("gst_lookup").notNull(),createdAt:integer("created_at").notNull(),
},t=>[uniqueIndex("uq_member_searches_day_gst").on(t.memberId,t.searchDate,t.gstLookup),index("idx_member_searches_day").on(t.memberId,t.searchDate)]);
export const legalHolds = sqliteTable("legal_holds", {
 id:text("id").primaryKey(),targetType:text("target_type").notNull(),targetId:text("target_id").notNull(),reason:text("reason").notNull(),createdBy:text("created_by").notNull(),createdAt:integer("created_at").notNull(),releasedAt:integer("released_at"),releasedBy:text("released_by"),
},t=>[index("idx_legal_holds_target_active").on(t.targetType,t.targetId,t.releasedAt)]);

export const pilotIssues = sqliteTable("pilot_issues", {
 id:text("id").primaryKey(),memberId:integer("member_id").notNull().references(()=>members.id),
 issueType:text("issue_type").notNull(),pageUrl:text("page_url").notNull(),description:text("description").notNull(),
 status:text("status").notNull().default("open"),adminNotes:text("admin_notes"),
 screenshotKey:text("screenshot_key"),screenshotName:text("screenshot_name"),screenshotMime:text("screenshot_mime"),screenshotSize:integer("screenshot_size"),
 createdAt:integer("created_at").notNull(),updatedAt:integer("updated_at").notNull(),
},t=>[index("idx_pilot_issues_status_updated").on(t.status,t.updatedAt),index("idx_pilot_issues_member_created").on(t.memberId,t.createdAt)]);

export const pilotChecks = sqliteTable("pilot_checks", {
 id:text("id").primaryKey(),checkKey:text("check_key").notNull(),label:text("label").notNull(),area:text("area").notNull(),
 status:text("status").notNull().default("not_tested"),notes:text("notes"),testedBy:text("tested_by"),updatedAt:integer("updated_at").notNull(),
},t=>[uniqueIndex("uq_pilot_checks_key").on(t.checkKey),index("idx_pilot_checks_status").on(t.status)]);
