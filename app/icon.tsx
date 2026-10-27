import { ImageResponse } from "next/og";

export const runtime = "nodejs";
export const size = { width: 32, height: 32 };
export const contentType = "image/png";

/**
 * Dynamic favicon — branded STN mark on blue background.
 * Next.js auto-generates <link rel="icon"> tags from this.
 */
export default function Icon() {
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
          borderRadius: 7,
          fontSize: 18,
          fontWeight: 800,
          color: "#fcd53d",
          fontFamily: "sans-serif",
        }}
      >
        S
      </div>
    ),
    { ...size }
  );
}
