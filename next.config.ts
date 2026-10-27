import type { NextConfig } from "next";
import path from "node:path";

const nextConfig: NextConfig = {
  // Hostinger injects output:"standalone" itself and starts the bundled server.
  // Pinning the tracing root keeps that standalone output inside this app folder
  // even when another lockfile exists above the checkout on the build machine.
  outputFileTracingRoot: path.join(process.cwd()),
  poweredByHeader: false,
  async headers() {
    // NOTE: Content-Security-Policy is set per-request by proxy.ts with a
    // cryptographic nonce (H1 fix). Static security headers remain here.
    const security = [
      { key: "X-Content-Type-Options", value: "nosniff" },
      { key: "Referrer-Policy", value: "strict-origin-when-cross-origin" },
      { key: "Permissions-Policy", value: "camera=(), microphone=(), geolocation=()" },
    ];
    // HSTS only in production — applying it locally forces https://0.0.0.0 / localhost.
    if (process.env.NODE_ENV === "production") {
      security.push({ key: "Strict-Transport-Security", value: "max-age=31536000" });
    }
    return [
      { source: "/:path*", headers: security },
      ...[
        "/admin/:path*",
        "/member/:path*",
        "/api/:path*",
        "/login",
        "/admin-login",
        "/forgot-password",
      ].map(source => ({
        source,
        headers: [{ key: "Cache-Control", value: "private, no-store" }],
      })),
    ];
  },
};

export default nextConfig;
