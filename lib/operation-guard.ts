import { reportDb } from "./report-store";

/**
 * operationGuard — transactional guard against TOCTOU races.
 *
 * Inserts a row into `operation_guards` whose `valid` column is computed from a
 * boolean SQL predicate, inside the same MongoDB transaction (via sql-mongo batch)
 * as the guarded mutation.
 * A CHECK(valid=1) style abort (throw on valid≠1) causes the entire batch to
 * roll back if the predicate is false at execution time.
 *
 * ⚠️  SECURITY CONTRACT — the `predicate` string is interpolated into SQL.
 *     It MUST be a hard-coded literal that contains NO user input and NO
 *     runtime-interpolated values. All dynamic values MUST be passed via
 *     `args` (which use bound `?` parameters — safe from SQL injection).
 *
 *     Every call site in this codebase passes a constant string literal as
 *     `predicate`. Do NOT introduce call sites that build the predicate from
 *     request data — if you need a dynamic predicate, add a new fixed template
 *     here and parameterize it via `args`.
 *
 * @param predicate A constant SQL boolean expression containing `?` placeholders.
 * @param args      Bound parameter values (strings/numbers/nulls) matching the `?` count.
 */
export function operationGuard(predicate: string, args: (string|number|null)[]) {
  const id = crypto.randomUUID(), db = reportDb();
  return {
    check: db.prepare(`INSERT INTO operation_guards(id,valid) SELECT ?,CASE WHEN (${predicate}) THEN 1 ELSE 0 END`).bind(id, ...args),
    release: db.prepare("DELETE FROM operation_guards WHERE id=?").bind(id),
  };
}
