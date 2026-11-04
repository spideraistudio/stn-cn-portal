import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
import crypto from 'node:crypto';
import ts from 'typescript';
import { MongoMemoryServer } from 'mongodb-memory-server';

// Real MongoDB and SQL adapter; only request identity and side effects outside
// seller search are stubbed. No live server, keys, database or user files.
function load(file, dependencies={}) {
  const exports={};
  const code=ts.transpileModule(fs.readFileSync(new URL('../'+file,import.meta.url),'utf8'),{
    compilerOptions:{module:ts.ModuleKind.CommonJS,target:ts.ScriptTarget.ES2022}
  }).outputText;
  vm.runInNewContext(code,{exports,require:name=>{
    assert(name in dependencies,'Unexpected import '+name);return dependencies[name];
  },Request,Response,TextDecoder,Uint8Array,Error,SyntaxError,JSON,crypto,console});
  return exports;
}

test('new and legacy accounts can find approved reports without leaking pilot/category data',async t=>{
  const server=await MongoMemoryServer.create({binary:{version:'8.0.17'},instance:{ip:'127.0.0.1',args:['--nounixsocket']}});
  process.env.MONGODB_URI=server.getUri('seller_search_regression');
  process.env.STN_MONGO_TLS='0';
  const adapter=await import('../lib/sql-mongo.ts');
  const db=new adapter.MongoSqlDb();
  const native=await adapter.mongoDb();
  let identity=null;
  const env={DB:db,IDENTIFIER_LOOKUP_KEY:'synthetic-search-regression-key',ADMIN_EMAILS:''};
  const categories=load('lib/category-access.ts');
  const store=load('lib/report-store.ts',{
    '@/lib/runtime-env':{env},'node:crypto':crypto,
    './member-session':{currentMember:async()=>identity},'./category-access':categories,
    '@/app/chatgpt-auth':{getChatGPTUser:async()=>null},'./member-data':{isConfiguredAdmin:()=>false}
  });
  const members=load('lib/member-data.ts',{
    '@/lib/runtime-env':{env},'./report-store':store,'./sql-mongo':adapter,
    './notifications':{notifyMember:async()=>{}}
  });
  const reader=load('lib/request-body.ts');
  const dependencies={
    '@/lib/request-body':reader,'next/server':{NextResponse:{json:(data,options)=>Response.json(data,options)}},
    '@/lib/report-store':store,'@/lib/sync-approved-resolutions':{syncApprovedResolutionsToReports:async()=>{}}
  };
  const search=load('app/api/seller-search/route.ts',dependencies);
  const lookup=load('app/api/seller-identity/route.ts',dependencies);
  const gst='24ABCDE1234F1Z5';
  async function call(route,body){return route.POST(new Request('http://localhost/api/test',{method:'POST',body:JSON.stringify(body)}));}
  async function select(member){identity=members.memberFromRow(await db.prepare('SELECT * FROM members WHERE id=?').bind(member.id).first());}
  async function report(member,status='approved',category='agriculture'){
    const seller=category==='agriculture'?'synthetic-seller':'synthetic-other-seller';
    const id=crypto.randomUUID();
    await db.prepare('INSERT INTO seller_reports(id,seller_id,member_id,category,status,firm_name,taluka,district,state,pincode,rating,dispute,legal,created_at,reviewed_at) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)')
      .bind(id,seller,member.id,category,status,'Synthetic Seller','Test','Test','Gujarat','380001',3,1,0,Date.now(),Date.now()).run();
    return id;
  }
  try {
    const fresh=await members.createRegistration({authUserId:'fresh',companyName:'Synthetic Company',address:'Test',taluka:'Test',district:'Test',state:'Gujarat',pincode:'380001',gstin:'24PQRST6789L1Z5',responsiblePersonName:'Test',mobileNumber:'9876543210',email:'test@example.test',category:'agriculture'});
    await t.test('registration persists an explicit normal-account flag',async()=>{
      const row=await db.prepare('SELECT * FROM members WHERE id=?').bind(fresh.id).first();
      assert.equal(row.is_pilot,0);
      assert.equal(row.status,'pending');
    });
    await db.prepare("UPDATE members SET status='approved',search_enabled=1 WHERE id=?").bind(fresh.id).run();
    for(const category of ['agriculture','other']){
      await db.prepare('INSERT INTO sellers(id,category,gst_lookup,gst_last4) VALUES(?,?,?,?)')
        .bind(category==='agriculture'?'synthetic-seller':'synthetic-other-seller',category,store.identifierKey(category,'gst',gst),gst.slice(-4)).run();
    }
    const pilot={id:crypto.randomUUID()},legacy={id:crypto.randomUUID()},nullLegacy={id:crypto.randomUUID()};
    await db.prepare("INSERT INTO members(id,auth_user_id,company_name,category,status,is_pilot,search_enabled,gstin,mobile_number) VALUES(?,?,?,'agriculture','approved',1,1,?,?)").bind(pilot.id,'pilot','Pilot','24AAAAA1111A1Z1','9000000001').run();
    await db.prepare("INSERT INTO members(id,auth_user_id,company_name,category,status,search_enabled,gstin,mobile_number) VALUES(?,?,?,'agriculture','approved',1,?,?)").bind(legacy.id,'legacy','Legacy','24BBBBB2222B1Z2','9000000002').run();
    await db.prepare("INSERT INTO members(id,auth_user_id,company_name,category,status,is_pilot,search_enabled,gstin,mobile_number) VALUES(?,?,?,'agriculture','approved',NULL,1,?,?)").bind(nullLegacy.id,'null-legacy','Null legacy','24CCCCC3333C1Z3','9000000003').run();
    const normalId=await report(fresh),legacyId=await report(legacy),nullId=await report(nullLegacy),pilotId=await report(pilot);
    await report(fresh,'pending');await report(fresh,'approved','other');
    for(const member of [fresh,legacy,nullLegacy]){
      await t.test((member===fresh?'new':member===legacy?'missing-flag legacy':'null-flag legacy')+' normal account sees approved normal/legacy reports only',async()=>{
        await select(member);const response=await call(search,{query:gst});
        assert.equal(response.status,200);const result=await response.json();
        assert.equal(result.seller.report_count,3);
        assert.deepEqual(result.reports.map(r=>r.id).sort(),[normalId,legacyId,nullId].sort());
        assert.equal(result.seller.gstin,'***********'+gst.slice(-4));
        const idResponse=await call(lookup,{gstin:gst});
        assert.equal(idResponse.status,200);assert.equal((await idResponse.json()).seller.report_count,3);
      });
    }
    await t.test('explicit pilot account sees only pilot reports',async()=>{
      await select(pilot);const response=await call(search,{query:gst});const result=await response.json();
      assert.equal(response.status,200);assert.equal(result.seller.report_count,1);
      assert.deepEqual(result.reports.map(r=>r.id),[pilotId]);
      assert.equal((await (await call(lookup,{gstin:gst})).json()).seller.report_count,1);
    });
    await t.test('unapproved/category-unassigned accounts remain blocked',async()=>{
      await select(fresh);identity.status='pending';
      assert.equal((await call(search,{query:gst})).status,403);
      await select(fresh);identity.category='other';
      assert.equal((await call(search,{query:gst})).status,403);
    });
    await t.test('search permission remains enforced',async()=>{
      await select(fresh);identity.searchEnabled=false;
      assert.equal((await call(search,{query:gst})).status,403);
    });
  } finally {
    await (await adapter.mongoClient()).close();await server.stop();
  }
});
