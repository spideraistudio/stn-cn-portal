/**
 * Validates that a request's origin matches the server's origin.
 * Allows for http/https and www/non-www variations (Hostinger proxy compatibility).
 *
 * NOTE (Next.js 16): route handlers see `request.url` rewritten to
 * `http://localhost:<port>` regardless of the incoming Host header, so the
 * server hostname must be derived from the `x-forwarded-host` / `host`
 * headers (with a request.url fallback) instead of `new URL(request.url)`.
 */
export function isOriginValid(request: Request): boolean {
  const origin = request.headers.get("origin");
  if(process.env.PORTAL_MODE==="combined")return !!origin && origin===process.env.PORTAL_ORIGIN;
  if (!origin) return false;
  try {
    const originUrl = new URL(origin);
    // Prefer forwarded host (proxy-safe, first value if comma-separated),
    // then Host header, then the (possibly rewritten) request URL.
    const forwardedHost = (request.headers.get("x-forwarded-host") ?? "").split(",")[0]?.trim();
    const hostHeader = forwardedHost || request.headers.get("host") || new URL(request.url).host;
    const serverHostname = new URL(`http://${hostHeader}`).hostname;
    // Compare hostname (ignore protocol and port for proxy compatibility)
    return originUrl.hostname === serverHostname;
  } catch {
    return false;
  }
}
