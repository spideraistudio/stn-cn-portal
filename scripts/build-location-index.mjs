import fs from "node:fs";

const [source, destinationDirectory] = process.argv.slice(2);
if (!source || !destinationDirectory) throw new Error("Usage: node scripts/build-location-index.mjs SOURCE.csv DESTINATION_DIRECTORY");

function parseCsvLine(line) {
  const values = [];
  let value = "";
  let quoted = false;
  for (let index = 0; index < line.length; index++) {
    const character = line[index];
    if (character === '"' && quoted && line[index + 1] === '"') { value += '"'; index++; }
    else if (character === '"') quoted = !quoted;
    else if (character === "," && !quoted) { values.push(value); value = ""; }
    else value += character;
  }
  values.push(value);
  return values;
}

const cleanName = value => value.trim().replace(/\s+/g, " ").toLowerCase().replace(/(^|[\s(/-])\p{L}/gu, match => match.toUpperCase());
const lines = fs.readFileSync(source, "utf8").split(/\r?\n/).filter(Boolean);
const headers = parseCsvLine(lines.shift());
const column = Object.fromEntries(headers.map((header, index) => [header, index]));
for (const required of ["Pincode", "District", "StateName"]) if (!(required in column)) throw new Error(`Missing ${required} column`);

const stateDistricts = new Map();
const pincodes = new Map();
for (const line of lines) {
  const row = parseCsvLine(line);
  const pincode = row[column.Pincode]?.trim();
  const state = cleanName(row[column.StateName] || "");
  const district = cleanName(row[column.District] || "");
  if (!/^[1-9]\d{5}$/.test(pincode) || !state || !district) continue;
  if (!stateDistricts.has(state)) stateDistricts.set(state, new Set());
  stateDistricts.get(state).add(district);
  if (!pincodes.has(pincode)) pincodes.set(pincode, new Set());
  pincodes.get(pincode).add(`${state}\u0000${district}`);
}

const states = Object.fromEntries([...stateDistricts].sort(([a], [b]) => a.localeCompare(b)).map(([state, districts]) => [state, [...districts].sort((a, b) => a.localeCompare(b))]));
const pinIndex = Object.fromEntries([...pincodes].sort(([a], [b]) => a.localeCompare(b)).map(([pin, locations]) => [pin, [...locations].sort().map(location => location.split("\u0000"))]));
fs.mkdirSync(destinationDirectory, { recursive: true });
fs.writeFileSync(`${destinationDirectory}/state-districts.json`, JSON.stringify(states));
fs.writeFileSync(`${destinationDirectory}/pincode-locations.json`, JSON.stringify(pinIndex));
console.log(`Created ${Object.keys(states).length} states, ${Object.values(states).reduce((total, districts) => total + districts.length, 0)} state/district pairs and ${Object.keys(pinIndex).length} PIN codes.`);
