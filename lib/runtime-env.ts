import { Binary } from "mongodb";
import { MongoSqlDb, mongoDb } from "@/lib/sql-mongo";

class DatabaseFiles {
  async put(key:string,body:ReadableStream|ArrayBuffer|Uint8Array|Blob,_options?:unknown){
    const bytes=body instanceof ReadableStream?new Uint8Array(await new Response(body).arrayBuffer()):body instanceof Blob?new Uint8Array(await body.arrayBuffer()):new Uint8Array(body as ArrayBufferLike);
    const db=await mongoDb();
    await db.collection("file_objects").updateOne({object_key:key},{ $set:{_id:key,object_key:key,body:new Binary(Buffer.from(bytes)),created_at:Date.now()} },{upsert:true});
  }
  async get(key:string){
    const db=await mongoDb();
    const row=await db.collection("file_objects").findOne({object_key:key});
    if(!row?.body)return null;
    const raw=row.body;
    const bytes=Buffer.isBuffer(raw)?raw:Buffer.from((raw as {buffer?:Buffer}).buffer||raw as Uint8Array);
    return {body:new Uint8Array(bytes)};
  }
  async delete(keys:string|string[]){
    const db=await mongoDb();
    for(const key of Array.isArray(keys)?keys:[keys])await db.collection("file_objects").deleteOne({object_key:key});
  }
}

export const DB=new MongoSqlDb();
export const REPORT_FILES=new DatabaseFiles();
export const env={DB,REPORT_FILES,ADMIN_LOGIN_ID:process.env.ADMIN_LOGIN_ID||"",ADMIN_PASSWORD_HASH:process.env.ADMIN_PASSWORD_HASH||"",ADMIN_INITIAL_PASSWORD:process.env.ADMIN_INITIAL_PASSWORD||"",ADMIN_EMAILS:process.env.ADMIN_EMAILS||"",IDENTIFIER_LOOKUP_KEY:process.env.IDENTIFIER_LOOKUP_KEY||""};
