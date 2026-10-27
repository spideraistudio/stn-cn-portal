import {MongoClient,ObjectId} from 'mongodb';
const url=process.env.MONGODB_URI;
if(!/^mongodb:\/\/127\.0\.0\.1:\d+\/integration_/.test(url||''))throw Error('Synthetic local database required');
const c=await MongoClient.connect(url);const db=c.db();
for(let i=1;i<=5;i++){
 const id=String(i).padStart(24,'0');
 await db.collection('members').updateOne({_id:new ObjectId(id)},{$set:{company_name:`Synthetic Company ${i}`,auth_user_id:`synthetic-${i}`,mobile_number:`999999999${i}`,gstin:`24ABCDE123${i}F1Z5`,email:`staff${i}@example.test`,address:'Synthetic address',taluka:'Ahmedabad',district:'Ahmedabad',state:i===3?'Maharashtra':'Gujarat',pincode:'380001',responsible_person_name:`Staff ${i}`,category:'agriculture',status:i>=4?'pending':'approved',credential_version:0,search_enabled:1,is_pilot:0,notification_preferences:{seed_buy:true},membership_plan:'trial',created_at:Date.now(),updated_at:Date.now()}},{upsert:true});
}
console.log('Synthetic STN members ready; existing member IDs explicitly linked by the test.');await c.close();
