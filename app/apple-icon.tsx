import { ImageResponse } from "next/og";

export const runtime = "nodejs";
export const size = { width: 180, height: 180 };
export const contentType = "image/png";

/**
 * Apple touch icon — branded STN mark on blue background (180×180).
 * Next.js auto-generates <link rel="apple-touch-icon"> from this.
 */
export default function AppleIcon() {
  return new ImageResponse(
    (
      <div
        style={{
          width: "100%",
          height: "100%",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          background: "linear-gradient(135deg, #15388c 0%, #2852a4 100%)",
          borderRadius: 40,
          fontSize: 90,
          fontWeight: 800,
          color: "#fcd53d",
          fontFamily: "sans-serif",
        }}
      >
        STN
      </div>
    ),
    { ...size }
  );
}
