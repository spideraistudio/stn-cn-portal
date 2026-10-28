import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
import ts from 'typescript';

// Exercise the actual route and bounded request reader, replacing only external
// services so malformed requests never need a database or emit notifications.
function load(path, dependencies={}) {
 const exports={};
 const code=ts.transpileModule(fs.readFileSync(new URL('../'+path,import.meta.url),'utf8'),{compilerOptions:{module:ts.ModuleKind.CommonJS,target:ts.ScriptTarget.ES2022}}).outputText;
 vm.runInNewContext(code,{exports,require:name=>{assert(name in dependencies,'Unexpected import '+name);return dependencies[name];},Request,Response,TextDecoder,Uint8Array,Error,SyntaxError,JSON,crypto,console});
 return exports;
}
const body=load('lib/request-body.ts');
let saved=0;
const route=load('app/api/register/route.ts',{
 '@/lib/request-body':body,
 'next/server':{NextResponse:{json:(data,options)=>Response.json(data,options)}},
 '@/lib/member-data':{createRegistration:async()=>{saved++;}},
 '@/lib/security':{consumeLimit:async()=>({allowed:true}),networkHash:()=> 'test',recordSecurityEvent:async()=>{}},
 '@/lib/notifications':{notifyAdmin:async()=>{}},
 '@/lib/india-locations':{validateIndianLocation:()=>({valid:true,state:'Gujarat',district:'Ahmadabad',pincode:'380001'})}
});
for(const [name,input,status] of [['malformed JSON','{',400],['non-object JSON','[]',400],['null JSON','null',400],['streamed oversized body',' '.repeat(33*1024),413]]) {
 test(name,async()=>{const before=saved;const response=await route.POST(new Request('http://localhost/api/register',{method:'POST',body:input,headers:{'Content-Type':'application/json'}}));assert.equal(response.status,status);assert.equal(saved,before);assert.ok((await response.json()).error);});
}
test('declared oversized request',async()=>{const response=await route.POST(new Request('http://localhost/api/register',{method:'POST',body:'{}',headers:{'Content-Length':String(21*1024)}}));assert.equal(response.status,413);});
const valid={companyName:'Synthetic Company',address:'Synthetic Address',taluka:'Test Taluka',district:'Ahmadabad',state:'Gujarat',responsiblePersonName:'Synthetic Person',gstin:'24PQRST6789L1Z5',mobileNumber:'9876543210',email:'test@example.test',category:'agriculture',pincode:'380001'};
for(const [name,changes] of [['required company',{companyName:''}],['invalid GSTIN',{gstin:'invalid'}],['invalid mobile',{mobileNumber:'123'}],['invalid email',{email:'bad'}],['other category details',{category:'other',otherCategory:''}]]){
 test(name,async()=>{const before=saved;const response=await route.POST(new Request('http://localhost/api/register',{method:'POST',body:JSON.stringify({...valid,...changes}),headers:{'Content-Type':'application/json'}}));assert.equal(response.status,400);assert.equal(saved,before);assert.ok((await response.json()).error);});
}
test('valid application persists once',async()=>{const before=saved;const response=await route.POST(new Request('http://localhost/api/register',{method:'POST',body:JSON.stringify(valid),headers:{'Content-Type':'application/json'}}));assert.equal(response.status,200);assert.equal(saved,before+1);assert.equal((await response.json()).success,true);});
test('honeypot does not persist',async()=>{const before=saved;const response=await route.POST(new Request('http://localhost/api/register',{method:'POST',body:JSON.stringify({...valid,website:'spam'}),headers:{'Content-Type':'application/json'}}));assert.equal(response.status,200);assert.equal(saved,before);});
