import { scryptSync, timingSafeEqual, randomBytes, createHash } from "node:crypto";
export function randomSecret() { return randomBytes(24).toString("base64url"); }
export function digest(value: string) { return createHash("sha256").update(value).digest("hex"); }
export function hashPassword(password: string) {
  const salt = randomBytes(16).toString("hex");
  const hash = scryptSync(password, salt, 64, { N: 16384, r: 8, p: 5 }).toString("hex");
  return `scrypt$${salt}$${hash}`;
}
export function verifyPassword(password: string, stored: string) {
  if(typeof password!=="string"||password.length>128||typeof stored!=="string")return false;
  const [kind, salt, hash] = stored.split("$");
  if (kind !== "scrypt" || !/^[a-f0-9]{32}$/.test(salt||"") || !/^[a-f0-9]{128}$/.test(hash||"")) return false;
  const actual = scryptSync(password, salt, 64, { N: 16384, r: 8, p: 5 });
  const expected = Buffer.from(hash, "hex");
  return actual.length === expected.length && timingSafeEqual(actual, expected);
}
