"use client";

import { useEffect, useMemo, useState } from "react";
import mapData from "@/lib/data/india-map.json";

type MapFeature = { s: string; d: string; b: [number, number, number, number]; p: string };
const features = mapData as MapFeature[];
const normalize = (value = "") => value.toLowerCase().replace(/[^a-z0-9]/g, "").replace("sabarkantha", "sabarkantha");
const union = (boxes: MapFeature["b"][]) => boxes.reduce((box, item) => [Math.min(box[0], item[0]), Math.min(box[1], item[1]), Math.max(box[2], item[2]), Math.max(box[3], item[3])], [Infinity, Infinity, -Infinity, -Infinity]);

export function IndiaWireframeMap({ state, district, prominent = false }: { state?: string; district?: string; prominent?: boolean }) {
  const [stage, setStage] = useState<"india" | "state" | "district">("india");
  const stateFeatures = useMemo(() => features.filter(feature => normalize(feature.s) === normalize(state)), [state]);
  const districtFeature = useMemo(() => stateFeatures.find(feature => normalize(feature.d) === normalize(district)), [stateFeatures, district]);
  useEffect(() => {
    // Reset the zoom animation to the India overview whenever the selected
    // state/district changes, then animate in. The synchronous reset is
    // intentional: it clears the previous zoom transform before the timed
    // transition begins.
    // eslint-disable-next-line react-hooks/set-state-in-effect
    setStage("india");
    if (!state || !stateFeatures.length) return;
    const stateTimer = window.setTimeout(() => setStage("state"), 180);
    const districtTimer = districtFeature ? window.setTimeout(() => setStage("district"), 1450) : undefined;
    return () => { window.clearTimeout(stateTimer); if (districtTimer) window.clearTimeout(districtTimer); };
  }, [state, district, stateFeatures.length, districtFeature]);
  if (!state) return null;
  const box = stage === "district" && districtFeature ? districtFeature.b : stage !== "india" && stateFeatures.length ? union(stateFeatures.map(feature => feature.b)) : [0, 0, 640, 720];
  const pad = stage === "district" ? 70 : stage === "state" ? 45 : 0;
  const width = Math.max(1, box[2] - box[0]), height = Math.max(1, box[3] - box[1]);
  const zoom = stage === "india" ? 1 : Math.min(640 / (width + pad), 720 / (height + pad));
  const x = 320 - ((box[0] + box[2]) / 2) * zoom, y = 360 - ((box[1] + box[3]) / 2) * zoom;
  return <div aria-hidden="true" className="pointer-events-none absolute left-1/2 top-0 z-0 h-full w-screen -translate-x-1/2 overflow-hidden bg-gradient-to-b from-blue-50/80 via-white/20 to-blue-50/80 dark:from-blue-950/60 dark:via-slate-950/20 dark:to-blue-950/60">
    <svg viewBox="0 0 640 720" preserveAspectRatio="xMidYMid slice" className="absolute inset-0 h-full w-full">
      <g style={{ transform: `translate(${x}px, ${y}px) scale(${zoom})`, transformOrigin: "0 0", transition: "transform 1.05s cubic-bezier(.22,.8,.22,1)" }}>
        {features.map((feature, index) => { const inState = normalize(feature.s) === normalize(state); const inDistrict = inState && normalize(feature.d) === normalize(district); return <path key={`${feature.s}-${feature.d}-${index}`} d={feature.p} fill={inDistrict && stage === "district" ? "currentColor" : "none"} fillOpacity={0.2} stroke="currentColor" strokeWidth={inDistrict ? 2.6 : inState ? 1.8 : 0.9} vectorEffect="non-scaling-stroke" className={inDistrict?"text-[#a57c10]":"text-[#2852a4] dark:text-blue-300"}/>; })}
      </g>
    </svg>
    {stage !== "india" && <div className={`absolute right-5 top-5 max-w-[45%] text-right ${prominent ? "text-white" : "text-[#15388c]"}`}><p className="text-xs font-semibold uppercase tracking-[0.18em]">{stage === "district" ? "District located" : "State located"}</p><p className="mt-1 text-xl font-semibold">{state}</p>{stage === "district" && district && <p className="mt-1 text-sm font-medium">{district} district</p>}</div>}
  </div>;
}
