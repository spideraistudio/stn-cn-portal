import { MongoClient } from "mongodb";
const uri = process.env.MONGODB_URI?.trim();
if (!uri) throw new Error("MONGODB_URI is required.");
const name = new URL(uri.replace(/^mongodb\+srv/, "https").replace(/^mongodb/, "https")).pathname.replace(/^\//, "").split("?")[0] || "sellerstrust";
const client = new MongoClient(uri);
try {
  await client.connect();
  const db = client.db(name);
  await Promise.all([
    db.collection("seed_buy_requests").createIndexes([{key:{id:1},unique:true},{key:{ownerId:1,createdAt:-1}},{key:{status:1,quotationDeadline:1}},{key:{status:1,panIndia:1,supplierStates:1}}]),
    db.collection("seed_quotations").createIndexes([{key:{id:1},unique:true},{key:{requestId:1,supplierId:1},unique:true},{key:{requestId:1,status:1}},{key:{supplierId:1,updatedAt:-1}}]),
  ]);
  console.log("Seed request and quotation indexes are ready.");
} finally { await client.close(); }
