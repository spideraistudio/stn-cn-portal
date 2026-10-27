import type { MetadataRoute } from "next";

/**
 * robots.txt for Sellers Trust Network.
 * Allows all crawlers on public pages, disallows authenticated and API routes.
 */
export default function robots(): MetadataRoute.Robots {
  return {
    rules: [
      {
        userAgent: "*",
        allow: "/",
        disallow: ["/admin/", "/member/", "/api/", "/home"],
      },
    ],
    sitemap: "https://sellerstrustnetwork.com/sitemap.xml",
    host: "https://sellerstrustnetwork.com",
  };
}
