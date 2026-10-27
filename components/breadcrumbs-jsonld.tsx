/**
 * BreadcrumbList JSON-LD structured data for SEO.
 * Helps search engines display breadcrumb trails in rich results.
 *
 * Usage: <BreadcrumbsJsonLd items={[{name:"Privacy", path:"/privacy"}]} />
 * The home page is always included as the first breadcrumb.
 */
export function BreadcrumbsJsonLd({ items }: { items: { name: string; path: string }[] }) {
  const baseUrl = "https://sellerstrustnetwork.com";
  const allItems = [{ name: "Home", path: "/" }, ...items];
  const data = {
    "@context": "https://schema.org",
    "@type": "BreadcrumbList",
    itemListElement: allItems.map((item, i) => ({
      "@type": "ListItem",
      position: i + 1,
      name: item.name,
      item: `${baseUrl}${item.path}`,
    })),
  };
  return (
    <script
      type="application/ld+json"
      dangerouslySetInnerHTML={{ __html: JSON.stringify(data) }}
    />
  );
}
