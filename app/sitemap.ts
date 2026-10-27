import type { MetadataRoute } from "next";

/**
 * Dynamic sitemap for Sellers Trust Network.
 * Lists all public (non-authenticated) pages. Authenticated routes
 * (/admin/*, /member/*) and API routes are excluded as they require
 * session cookies and should not be indexed.
 */
export default function sitemap(): MetadataRoute.Sitemap {
  const baseUrl = "https://sellerstrustnetwork.com";
  const lastModified = new Date();

  const publicRoutes = [
    { url: "/", priority: 1.0, changeFrequency: "weekly" as const },
    { url: "/about", priority: 0.9, changeFrequency: "monthly" as const },
    { url: "/plans", priority: 0.9, changeFrequency: "monthly" as const },
    { url: "/contact", priority: 0.8, changeFrequency: "monthly" as const },
    { url: "/faq", priority: 0.8, changeFrequency: "monthly" as const },
    { url: "/join", priority: 0.7, changeFrequency: "monthly" as const },
    { url: "/login", priority: 0.6, changeFrequency: "yearly" as const },
    { url: "/admin-login", priority: 0.3, changeFrequency: "yearly" as const },
    { url: "/forgot-password", priority: 0.3, changeFrequency: "yearly" as const },
    { url: "/privacy", priority: 0.5, changeFrequency: "yearly" as const },
    { url: "/terms", priority: 0.5, changeFrequency: "yearly" as const },
    { url: "/disclaimer", priority: 0.5, changeFrequency: "yearly" as const },
  ];

  return publicRoutes.map(route => ({
    url: `${baseUrl}${route.url}`,
    lastModified,
    changeFrequency: route.changeFrequency,
    priority: route.priority,
  }));
}
