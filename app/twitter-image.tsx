import { ImageResponse } from "next/og";

export const runtime = "nodejs";
export const alt = "Sellers Trust Network — Verified seller intelligence";
export const size = { width: 1200, height: 600 };
export const contentType = "image/png";

/**
 * Twitter card image (summary_large_image).
 * Slightly shorter aspect ratio than OG (1200×600 vs 1200×630) for Twitter.
 */
export default function TwitterImage() {
  return new ImageResponse(
    (
      <div
        style={{
          width: "100%",
          height: "100%",
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          justifyContent: "center",
          background: "linear-gradient(135deg, #15388c 0%, #1e4daf 50%, #2852a4 100%)",
          position: "relative",
          fontFamily: "sans-serif",
        }}
      >
        <div style={{ position: "absolute", right: -60, top: 20, width: 260, height: 260, borderRadius: "50%", background: "rgba(96,165,250,0.15)", display: "flex" }} />
        {/* Logo badge */}
        <div style={{ display: "flex", alignItems: "center", justifyContent: "center", width: 76, height: 76, borderRadius: 18, background: "rgba(255,255,255,0.1)", border: "1px solid rgba(255,255,255,0.2)", marginBottom: 28 }}>
          <span style={{ fontSize: 40, fontWeight: 800, color: "#fcd53d" }}>STN</span>
        </div>
        <div style={{ display: "flex", fontSize: 52, fontWeight: 800, color: "white", textAlign: "center", maxWidth: 880, lineHeight: 1.1, letterSpacing: -1 }}>
          Sellers Trust Network
        </div>
        <div style={{ display: "flex", fontSize: 24, color: "rgba(219,234,254,0.9)", marginTop: 20, textAlign: "center", maxWidth: 760 }}>
          Verified seller intelligence for Indian businesses
        </div>
        <div style={{ display: "flex", position: "absolute", bottom: 40, fontSize: 20, fontWeight: 600, color: "rgba(252,211,77,0.9)" }}>
          sellerstrustnetwork.com
        </div>
      </div>
    ),
    { ...size }
  );
}
