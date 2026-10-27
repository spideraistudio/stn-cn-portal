import { NextResponse } from 'next/server';
import { BSON } from 'mongodb';
import { portalIdentity } from '@/lib/portal-session';
import { currentMember } from '@/lib/member-session';
import { mongoDb } from '@/lib/sql-mongo';
export async function GET(){
 const identity=await portalIdentity();
 if(!identity?.modules.stn)return NextResponse.json({error:'STN access required'},{status:403});
 const root=identity.role==='superadmin',member=root?null:await currentMember();
 if(!root&&!member)return NextResponse.json({error:'Approved membership required'},{status:403});
 try{
 const db=await mongoDb(),collections=await db.listCollections().toArray();
 let total=0;const breakdown:Record<string,number>={},shared:Record<string,number>={};
 const reports=root?[]:await db.collection('seller_reports').find({member_id:{$in:[member.id,String(member.id)]}}).toArray();
 const reportIds=new Set(reports.map(r=>String(r._id??r.id)));
 const requests=root?[]:await db.collection('dispute_resolution_requests').find({member_id:{$in:[member.id,String(member.id)]}}).toArray();
 const requestIds=new Set(requests.map(r=>String(r._id??r.id)));
 const objectKeys=new Set<string>();
 // Account documents before files so retained evidence is attributed from ownership.
 for(const collection of collections.filter(c=>c.name!=='file_objects')){
   let sum=0;
   for await(const row of db.collection(collection.name).find({})){
     const size=BSON.calculateObjectSize(row);
     const own=root||String(row.member_id??row.ownerId??row.supplierId??'')===String(member.id)||collection.name==='members'&&String(row._id)===String(member.id)||reportIds.has(String(row.report_id))||requestIds.has(String(row.request_id));
     if(own){sum+=size;if(row.object_key)objectKeys.add(String(row.object_key));if(row.screenshot_key)objectKeys.add(String(row.screenshot_key));}
   }
   if(sum){breakdown[collection.name]=sum;total+=sum;}
 }
 let files=0;
 for await(const row of db.collection('file_objects').find({})){if(root||objectKeys.has(String(row.object_key)))files+=BSON.calculateObjectSize(row);}
 breakdown.file_objects=files;total+=files;
 return NextResponse.json({module:'stn',scope:root?'installation':'own-member',logical_bson_bytes:total,breakdown,shared,cn_allowance_deducted:0,quota_bytes:null,notes:'Retained BSON document bytes including file bodies; database indexes, journal and backups are not included. STN has no quota configured. CN allowances remain separate.'},{headers:{'Cache-Control':'no-store'}});
 }catch{return NextResponse.json({error:'STN storage unavailable'},{status:503});}
}
