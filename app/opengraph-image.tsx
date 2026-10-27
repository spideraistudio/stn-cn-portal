import { ImageResponse } from "next/og";

export const runtime = "nodejs";
export const alt = "Sellers Trust Network — Verified seller intelligence for Indian businesses";
export const size = { width: 1200, height: 630 };
export const contentType = "image/png";

export default function OpenGraphImage() {
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
        {/* Decorative circles */}
        <div
          style={{
            position: "absolute",
            right: -60,
            top: 40,
            width: 280,
            height: 280,
            borderRadius: "50%",
            background: "rgba(96, 165, 250, 0.15)",
            display: "flex",
          }}
        />
        <div
          style={{
            position: "absolute",
            left: -40,
            bottom: -20,
            width: 320,
            height: 320,
            borderRadius: "50%",
            background: "rgba(252, 211, 77, 0.08)",
            display: "flex",
          }}
        />

        {/* Logo badge */}
        <div
          style={{
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            width: 80,
            height: 80,
            borderRadius: 20,
            background: "rgba(255,255,255,0.1)",
            border: "1px solid rgba(255,255,255,0.2)",
            marginBottom: 32,
          }}
        >
          <span style={{ fontSize: 44, fontWeight: 800, color: "#fcd53d" }}>STN</span>
        </div>

        {/* Main heading */}
        <div
          style={{
            display: "flex",
            fontSize: 56,
            fontWeight: 800,
            color: "white",
            textAlign: "center",
            maxWidth: 900,
            lineHeight: 1.1,
            letterSpacing: -1,
          }}
        >
          Know who you can trust before you trade.
        </div>

        {/* Subtitle */}
        <div
          style={{
            display: "flex",
            fontSize: 26,
            color: "rgba(219, 234, 254, 0.9)",
            marginTop: 24,
            textAlign: "center",
            maxWidth: 800,
            lineHeight: 1.4,
          }}
        >
          Private, category-controlled company verification network for Indian businesses
        </div>

        {/* Feature badges */}
        <div
          style={{
            display: "flex",
            gap: 16,
            marginTop: 40,
          }}
        >
          {["GSTIN search", "Dispute resolution", "Category isolation"].map((feature) => (
            <div
              key={feature}
              style={{
                display: "flex",
                alignItems: "center",
                padding: "10px 20px",
                borderRadius: 999,
                background: "rgba(255,255,255,0.1)",
                border: "1px solid rgba(255,255,255,0.15)",
                fontSize: 18,
                fontWeight: 600,
                color: "white",
              }}
            >
              {feature}
            </div>
          ))}
        </div>

        {/* URL bar */}
        <div
          style={{
            display: "flex",
            position: "absolute",
            bottom: 48,
            fontSize: 22,
            fontWeight: 600,
            color: "rgba(252, 211, 77, 0.9)",
            letterSpacing: 0.5,
          }}
        >
          sellerstrustnetwork.com
        </div>
      </div>
    ),
    { ...size }
  );
}
