import pincodeLocations from "@/lib/data/pincode-locations.json";

type LocationPair = [string, string];
const locations = pincodeLocations as unknown as Record<string, LocationPair[]>;

export function validateIndianLocation(state: string, district: string, pincode: string) {
  const cleanState = state.trim();
  const cleanDistrict = district.trim();
  const cleanPincode = pincode.trim();
  if (!/^[1-9][0-9]{5}$/.test(cleanPincode)) return { valid: false, error: "Enter a valid six-digit PIN code." };
  const matches = locations[cleanPincode] || [];
  if (!matches.length) return { valid: false, error: "This PIN code was not found in the India PIN directory." };
  const match = matches.find(([candidateState, candidateDistrict]) => candidateState === cleanState && candidateDistrict === cleanDistrict);
  if (!match) return { valid: false, error: "This PIN code does not belong to the selected state and district." };
  return { valid: true, state: match[0], district: match[1], pincode: cleanPincode };
}
