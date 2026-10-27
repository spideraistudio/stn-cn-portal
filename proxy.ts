import { NextResponse, type NextRequest } from "next/server";

/**
 * Per-request nonce-based Content-Security-Policy proxy.
 *
 * Generates a cryptographic nonce per request, attaches it to the request
 * headers so the layout can apply it to inline scripts (JSON-LD), and rewrites
 * the static CSP header from next.config.ts to replace `'unsafe-inline'` in
 * script-src with `'nonce-<value>'`. style-src retains `'unsafe-inline'` because
 * Next.js/Tailwind injects many inline styles at runtime that cannot all be
 * nonce-tagged without significant refactoring.
 *
 * This addresses H1 (CSP unsafe-inline for scripts) from the security review.
 */

// Paths that should NOT receive the nonce CSP (static assets, metadata routes).
const STATIC_PATHS = ["/sitemap.xml", "/robots.txt", "/site.webmanifest"];

function generateNonce(): string {
  const bytes = new Uint8Array(16);
  crypto.getRandomValues(bytes);
  // base64url-safe encoding
  return btoa(String.fromCharCode(...bytes))
    .replace(/\+/g, "-")
    .replace(/\//g, "_")
    .replace(/=+$/, "");
}

export function proxy(request: NextRequest) {
  // Skip static/metadata routes — they get default headers from next.config.ts.
  if (STATIC_PATHS.some(p => request.nextUrl.pathname === p)) {
    return NextResponse.next();
  }

  const nonce = generateNonce();
  const isDev = process.env.NODE_ENV !== "production";

  // Attach the nonce to the request so the layout can read it via headers()
  // and apply it to inline <script> tags. Next.js reads the request CSP
  // set below to stamp its own hydration scripts.
  const requestHeaders = new Headers(request.headers);
  requestHeaders.set("x-csp-nonce", nonce);
  requestHeaders.set("x-nonce", nonce);

  // Strict CSP: script-src uses nonce instead of 'unsafe-inline'.
  // style-src keeps 'unsafe-inline' (Next.js injects runtime styles).
  // React's development build uses eval() for stack reconstruction; never allow it in production.
  const csp = [
    "default-src 'self'",
    `script-src 'self' 'nonce-${nonce}'${isDev ? " 'unsafe-eval'" : ""}`,
    "style-src 'self' 'unsafe-inline'",
    "img-src 'self' data: blob:",
    "font-src 'self' data:",
    `connect-src 'self'${isDev ? " ws: wss:" : ""}`,
    "object-src 'none'",
    "base-uri 'none'",
    "form-action 'self'",
    "frame-ancestors 'self'",
  ].join("; ");

  // Next extracts the framework-script nonce from the REQUEST CSP header.
  // x-nonce alone does not nonce the inline hydration bootstrap.
  requestHeaders.set("Content-Security-Policy", csp);
  const response = NextResponse.next({request:{headers:requestHeaders}});
  response.headers.set("Content-Security-Policy", csp);
  // Expose the nonce to the browser for client-side nonce injection if needed.
  response.headers.set("X-CSP-Nonce", nonce);

  return response;
}

export const config = {
  // Run on all routes except static assets and Next.js internals.
  matcher: [
    "/((?!_next/static|_next/image|favicon.svg|.*\\.png$|.*\\.svg$|.*\\.ico$|.*\\.json$).*)",
  ],
};
