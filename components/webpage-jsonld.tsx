/**
 * WebPage JSON-LD structured data for SEO.
 * Helps search engines understand individual content pages.
 *
 * Usage: <WebPageJsonLd name="About" path="/about" description="..." />
 */
export function WebPageJsonLd({ name, path, description }: { name: string; path: string; description: string }) {
  const baseUrl = "https://sellerstrustnetwork.com";
  const data = {
    "@context": "https://schema.org",
    "@type": "WebPage",
    name,
    description,
    url: `${baseUrl}${path}`,
    isPartOf: { "@id": `${baseUrl}/#website` },
    publisher: { "@id": `${baseUrl}/#organization` },
  };
  return (
    <script
      type="application/ld+json"
      dangerouslySetInnerHTML={{ __html: JSON.stringify(data) }}
    />
  );
}
