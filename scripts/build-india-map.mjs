import fs from "node:fs";

const [source, destination] = process.argv.slice(2);
if (!source || !destination) throw new Error("Usage: node scripts/build-india-map.mjs SOURCE_TOPOJSON DESTINATION_JSON");
const topology = JSON.parse(fs.readFileSync(source, "utf8"));
const collection = Object.values(topology.objects)[0];
const { scale, translate } = topology.transform;
const decoded = topology.arcs.map(arc => { let x = 0, y = 0; return arc.map(([dx, dy]) => { x += dx; y += dy; return [x * scale[0] + translate[0], y * scale[1] + translate[1]]; }); });
const readArc = index => { const points = decoded[index < 0 ? ~index : index]; return index < 0 ? [...points].reverse() : points; };
const readRings = geometry => (geometry.type === "Polygon" ? [geometry.arcs] : geometry.arcs).flatMap(polygon => polygon.map(ring => ring.flatMap((index, position) => readArc(index).slice(position ? 1 : 0))));
const raw = collection.geometries.map(geometry => ({ state: geometry.properties.st_nm, district: geometry.properties.district, rings: readRings(geometry) }));
const points = raw.flatMap(feature => feature.rings.flat());
const [minLon, minLat, maxLon, maxLat] = points.reduce((bounds, [x, y]) => [Math.min(bounds[0], x), Math.min(bounds[1], y), Math.max(bounds[2], x), Math.max(bounds[3], y)], [Infinity, Infinity, -Infinity, -Infinity]);
const width = 640, height = 720, padding = 18;
const factor = Math.min((width - padding * 2) / (maxLon - minLon), (height - padding * 2) / (maxLat - minLat));
const project = ([lon, lat]) => [Math.round((padding + (lon - minLon) * factor) * 10) / 10, Math.round((padding + (maxLat - lat) * factor) * 10) / 10];
const distanceToSegment = (point, start, end) => { const dx = end[0] - start[0], dy = end[1] - start[1]; if (!dx && !dy) return Math.hypot(point[0] - start[0], point[1] - start[1]); const t = Math.max(0, Math.min(1, ((point[0] - start[0]) * dx + (point[1] - start[1]) * dy) / (dx * dx + dy * dy))); return Math.hypot(point[0] - (start[0] + t * dx), point[1] - (start[1] + t * dy)); };
function simplify(points, tolerance = 0.55) { if (points.length <= 4) return points; let furthest = 0, index = 0; for (let i = 1; i < points.length - 1; i++) { const distance = distanceToSegment(points[i], points[0], points.at(-1)); if (distance > furthest) { furthest = distance; index = i; } } if (furthest <= tolerance) return [points[0], points.at(-1)]; const left = simplify(points.slice(0, index + 1), tolerance), right = simplify(points.slice(index), tolerance); return [...left.slice(0, -1), ...right]; }
const output = raw.map(feature => { const projected = feature.rings.map(ring => simplify(ring.map(project))); const flat = projected.flat(); const xs = flat.map(([x]) => x), ys = flat.map(([, y]) => y); return { s: feature.state, d: feature.district, b: [Math.min(...xs), Math.min(...ys), Math.max(...xs), Math.max(...ys)].map(value => Math.round(value * 10) / 10), p: projected.map(ring => ring.map(([x, y], index) => `${index ? "L" : "M"}${x} ${y}`).join("") + "Z").join("") }; });
fs.writeFileSync(destination, JSON.stringify(output));
console.log(`Created ${output.length} district wireframes.`);
