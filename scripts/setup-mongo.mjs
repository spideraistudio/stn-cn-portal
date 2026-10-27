import { MongoClient } from "mongodb";

const url=process.env.MONGODB_URI?.trim();
if(!url)throw new Error("MONGODB_URI is missing.");
const client=new MongoClient(url,{tls:process.env.STN_MONGO_TLS!=="0"});
await client.connect();
try{
  const name=new URL(url.replace(/^mongodb\+srv/,"https")).pathname.replace(/^\//,"").split("?")[0]||"sellerstrust";
  const db=client.db(name);
  await db.command({ping:1});
  await Promise.all([
    db.collection("members").createIndexes([{key:{id:1},unique:true},{key:{gstin:1},unique:true},{key:{mobile_number:1},unique:true},{key:{auth_user_id:1},unique:true},{key:{login_id:1},unique:true,sparse:true},{key:{category:1,status:1}}]),
    db.collection("sellers").createIndexes([{key:{id:1},unique:true},{key:{category:1,gst_lookup:1},unique:true}]),
    db.collection("seller_reports").createIndexes([{key:{id:1},unique:true},{key:{seller_id:1,status:1}},{key:{member_id:1,created_at:1}},{key:{status:1,created_at:1}}]),
    db.collection("member_sessions").createIndexes([{key:{token_hash:1},unique:true},{key:{member_id:1}}]),
    db.collection("admin_sessions").createIndexes([{key:{token_hash:1},unique:true},{key:{expires_at:1}}]),
    db.collection("admin_credentials").createIndexes([{key:{login_id:1},unique:true}]),
    db.collection("member_searches").createIndexes([{key:{member_id:1,search_date:1,gst_lookup:1},unique:true}]),
    db.collection("pilot_checks").createIndexes([{key:{check_key:1},unique:true}]),
    db.collection("file_objects").createIndexes([{key:{object_key:1},unique:true}]),
    db.collection("security_rate_limits").createIndexes([{key:{key:1},unique:true}]),
    db.collection("notifications").createIndexes([{key:{audience:1,read_at:1,created_at:-1}}]),
    db.collection("seed_buy_requests").createIndexes([{key:{id:1},unique:true},{key:{ownerId:1,createdAt:-1}},{key:{status:1,quotationDeadline:1}},{key:{status:1,panIndia:1,supplierStates:1}}]),
    db.collection("seed_quotations").createIndexes([{key:{id:1},unique:true},{key:{requestId:1,supplierId:1},unique:true},{key:{requestId:1,status:1}},{key:{supplierId:1,updatedAt:-1}}]),
  ]);
  console.log(`Seller Trust Network MongoDB is ready (${name}).`);
}finally{
  await client.close();
}
