import { MongoClient, ObjectId, type ClientSession, type Db, Binary } from "mongodb";

export type QueryResult<T> = { results:T[]; meta:{changes:number;last_row_id?:number} };
type Row = Record<string, unknown>;
type Ctx = Record<string, Row>;

let client:MongoClient|undefined;
let connecting:Promise<MongoClient>|undefined;

function mongoUrl(){
  const url=process.env.MONGODB_URI?.trim();
  if(!url)throw new Error("MONGODB_URI is required");
  return url;
}
function dbNameFromUrl(url:string){
  try{
    const parsed=new URL(url.replace(/^mongodb\+srv/,"https").replace(/^mongodb/,"https"));
    const name=parsed.pathname.replace(/^\//,"").split("?")[0];
    if(name)return name;
  }catch{/* ignore */}
  return "sellerstrust";
}
export async function mongoClient(){
  if(client)return client;
  if(!connecting){
    connecting=MongoClient.connect(mongoUrl(),{maxPoolSize:8,tls:process.env.STN_MONGO_TLS!=="0",serverSelectionTimeoutMS:15000,autoSelectFamily:false}).then(async c=>{
      client=c;
      await ensureIndexes(c.db(dbNameFromUrl(mongoUrl())));
      return c;
    });
  }
  return connecting;
}
export async function mongoDb(){
  const c=await mongoClient();
  return c.db(dbNameFromUrl(mongoUrl()));
}
function asId(value:unknown){
  if(value==null)return value;
  if(typeof value==="object" && typeof (value as {toHexString?:()=>string}).toHexString==="function")return (value as {toHexString:()=>string}).toHexString();
  return value;
}
function toMongoId(value:unknown){
  if(value instanceof ObjectId)return value;
  const text=String(value??"");
  if(/^[a-fA-F0-9]{24}$/.test(text))return new ObjectId(text);
  return value;
}
function assignDocumentId(table:string,doc:Row){
  if(doc.id!==undefined && doc.id!==null && String(doc.id)!=="")doc._id=toMongoId(doc.id);
  else if(table==="admin_credentials" && doc.login_id)doc._id=doc.login_id;
  else if((table==="admin_sessions"||table==="member_sessions") && doc.token_hash)doc._id=doc.token_hash;
  else if(table==="file_objects" && doc.object_key)doc._id=doc.object_key;
  else if(table==="security_rate_limits" && doc.key)doc._id=doc.key;
  delete doc.id;
}
async function ensureIndexes(db:Db){
  await Promise.all([
    db.collection("members").dropIndex("id_1"),
    db.collection("sellers").dropIndex("id_1"),
    db.collection("seller_reports").dropIndex("id_1"),
    db.collection("audit_logs").dropIndex("id_1"),
  ]).catch(()=>{/* index may not exist */});
  await Promise.all([
    db.collection("members").createIndexes([{key:{gstin:1},unique:true},{key:{mobile_number:1},unique:true},{key:{auth_user_id:1},unique:true},{key:{login_id:1},unique:true,sparse:true},{key:{category:1,status:1}}]),
    db.collection("sellers").createIndexes([{key:{category:1,gst_lookup:1},unique:true}]),
    db.collection("seller_reports").createIndexes([{key:{seller_id:1,status:1}},{key:{member_id:1,created_at:1}},{key:{status:1,created_at:1}}]),
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
  ]).catch(()=>{/* indexes may already exist */});
}

function strip(sql:string){return sql.replace(/\s+/g," ").trim();}
function unquote(id:string){return id.replace(/^["`]|["`]$/g,"");}
function splitTop(input:string,sep:string){
  const out:string[]=[];let depth=0,quote="";let cur="";
  const u=sep.toUpperCase();
  const needsSpace=/[A-Za-z]/.test(sep);
  for(let i=0;i<input.length;i++){
    const ch=input[i];
    if(quote){if(ch===quote)quote="";cur+=ch;continue;}
    if(ch==="'"||ch==='"'){quote=ch;cur+=ch;continue;}
    if(ch==="(")depth++;
    if(ch===")")depth--;
    if(depth===0 && input.slice(i,i+sep.length).toUpperCase()===u){
      const leftOk=!needsSpace || i===0 || /\s/.test(input[i-1]||" ");
      const rightOk=!needsSpace || i+sep.length>=input.length || /\s/.test(input[i+sep.length]||"");
      // Do not treat the "=" inside >=, <=, !=, or <> as a separator.
      const multiOp = sep==="=" && (input[i-1]===">" || input[i-1]==="<" || input[i-1]==="!");
      if(leftOk && rightOk && !multiOp){
        out.push(cur.trim());cur="";i+=sep.length-1;continue;
      }
    }
    cur+=ch;
  }
  if(cur.trim())out.push(cur.trim());
  return out;
}
function splitList(input:string){return splitTop(input,",");}
function takeParams(sql:string,values:unknown[]){
  let n=0;
  const bound=sql.replace(/\?/g,()=>{
    const v=values[n++];
    if(v===null||v===undefined)return "NULL";
    if(typeof v==="number")return String(v);
    if(typeof v==="boolean")return v?"1":"0";
    if(v instanceof Buffer||v instanceof Uint8Array)return `__BIN_${n-1}__`;
    return `'${String(v).replace(/'/g,"''")}'`;
  });
  return {sql:bound,blobs:values};
}
function lit(raw:string,blobs:unknown[]):unknown{
  const t=raw.trim();
  if(/^NULL$/i.test(t))return null;
  if(/^__BIN_(\d+)__$/.test(t))return blobs[Number(RegExp.$1)];
  if((t.startsWith("'")&&t.endsWith("'"))||(t.startsWith('"')&&t.endsWith('"')))return t.slice(1,-1).replace(/''/g,"'");
  if(/^-?\d+(\.\d+)?$/.test(t))return Number(t);
  return t;
}
function resolve(path:string,ctx:Ctx,row:Row):unknown{
  const clean=unquote(path.trim());
  if(/^(NULL)$/i.test(clean))return null;
  if(clean.includes(".")){
    const [alias,col]=clean.split(".",2);
    const bucket=ctx[alias]||ctx[unquote(alias)];
    if(bucket && col in bucket)return bucket[unquote(col)];
    if(clean in row)return row[clean];
  }
  if(clean in row)return row[clean];
  for(const v of Object.values(ctx))if(v && clean in v)return v[clean];
  return undefined;
}
function cmp(a:unknown,op:string,b:unknown){
  if(a===undefined)a=null;if(b===undefined)b=null;
  a=asId(a);b=asId(b);
  if(op==="IS" && b===null)return a===null;
  if(op==="IS NOT" && b===null)return a!==null;
  const an=typeof a==="number"||typeof b==="number"?Number(a):a;
  const bn=typeof a==="number"||typeof b==="number"?Number(b):b;
  switch(op){
    case "=": case "==": return an==bn;
    case "<>": case "!=": return an!=bn;
    case ">": return Number(an)>Number(bn);
    case "<": return Number(an)<Number(bn);
    case ">=": return Number(an)>=Number(bn);
    case "<=": return Number(an)<=Number(bn);
    default: return false;
  }
}
function like(value:unknown,pattern:string){
  const s=String(value??"").toLowerCase();
  const p=pattern.toLowerCase().replace(/[.*+?^${}()|[\]\\]/g,"\\$&").replace(/%/g,".*").replace(/_/g,".");
  return new RegExp(`^${p}$`).test(s);
}
async function evalExpr(expr:string,ctx:Ctx,row:Row,db:Db,blobs:unknown[],session?:ClientSession):Promise<unknown>{
  let e=expr.trim();
  if(!e)return null;
  while(e.startsWith("(")&&e.endsWith(")")&&!/^\(\s*SELECT\b/i.test(e)&&splitTop(e.slice(1,-1),"AND").length===1&&splitTop(e.slice(1,-1),"OR").length===1)e=e.slice(1,-1).trim();
  if(/^NULL$/i.test(e))return null;
  if(/^-?\d+(\.\d+)?$/.test(e))return Number(e);
  if((e.startsWith("'")&&e.endsWith("'"))||(e.startsWith('"')&&e.endsWith('"')&&!e.includes(".")))return lit(e,blobs);
  const exists=e.match(/^NOT\s+EXISTS\s*\(([\s\S]+)\)\s*$/i)||e.match(/^EXISTS\s*\(([\s\S]+)\)\s*$/i);
  if(exists){
    const inner=exists[1];
    const not=/^NOT\s+EXISTS/i.test(e);
    const found=await runSelect(inner,db,blobs,session,ctx);
    return not?!found.results.length:found.results.length?1:0;
  }
  if(/^\(\s*SELECT\s+/i.test(e)||/^SELECT\s+/i.test(e)){
    const r=await runSelect(/^SELECT\s+/i.test(e)?e:e.slice(1,-1),db,blobs,session,ctx);
    const first=r.results[0];
    if(!first)return null;
    const vals=Object.values(first);
    return vals.length===1?vals[0]:first;
  }
  // SQLite/D1 CAST(expr AS TYPE) — used when integer ids were stringified for legal holds.
  // On Mongo, ids are already strings/ObjectIds; CAST(... AS TEXT) just normalizes via asId.
  const cast=e.match(/^CAST\s*\(([\s\S]+)\s+AS\s+(\w+)\s*\)$/i);
  if(cast){
    const v=await evalExpr(cast[1],ctx,row,db,blobs,session);
    const t=cast[2].toUpperCase();
    if(t==="TEXT"||t==="VARCHAR"||t==="CHAR"||t==="STRING")return v==null||v===undefined?null:String(asId(v)??"");
    if(t==="INTEGER"||t==="INT"||t==="BIGINT"||t==="REAL"||t==="NUMERIC"||t==="DECIMAL"||t==="FLOAT"||t==="DOUBLE"){
      if(v==null||v===undefined||v==="")return null;
      const n=Number(v);
      return Number.isFinite(n)?n:null;
    }
    return v;
  }
  const fn=e.match(/^(COUNT|SUM|AVG|MAX|MIN|COALESCE|GREATEST|LEAST|LOWER|UPPER|LENGTH|SUBSTR|SUBSTRING|CONCAT|IFNULL|IF|CASE)\b/i);
  if(fn){
    const name=fn[1].toUpperCase();
    if(name==="CASE")return evalCase(e,ctx,row,db,blobs,session);
    const args=parseFnArgs(e);
    if(name==="COALESCE"||name==="IFNULL"){
      for(const a of args){const v=await evalExpr(a,ctx,row,db,blobs,session);if(v!==null&&v!==undefined)return v;}
      return null;
    }
    if(name==="GREATEST")return Math.max(...await mapNums(args,ctx,row,db,blobs,session));
    if(name==="LEAST")return Math.min(...await mapNums(args,ctx,row,db,blobs,session));
    if(name==="LOWER")return String(await evalExpr(args[0],ctx,row,db,blobs,session)??"").toLowerCase();
    if(name==="UPPER")return String(await evalExpr(args[0],ctx,row,db,blobs,session)??"").toUpperCase();
    if(name==="LENGTH")return String(await evalExpr(args[0],ctx,row,db,blobs,session)??"").length;
    if(name==="CONCAT")return (await Promise.all(args.map(a=>evalExpr(a,ctx,row,db,blobs,session)))).map(v=>v??"").join("");
    if(name==="SUBSTR"||name==="SUBSTRING"){
      const s=String(await evalExpr(args[0],ctx,row,db,blobs,session)??"");
      const start=Number(await evalExpr(args[1],ctx,row,db,blobs,session)||1)-1;
      const len=args[2]!==undefined?Number(await evalExpr(args[2],ctx,row,db,blobs,session)):undefined;
      return s.substr(Math.max(0,start),len);
    }
    if(name==="IF"){
      const c=await evalBool(args[0],ctx,row,db,blobs,session);
      return evalExpr(c?args[1]:args[2],ctx,row,db,blobs,session);
    }
    // Per-row aggregate seed values. The grouping pass reduces these.
    if(name==="SUM"||name==="AVG"||name==="MAX"||name==="MIN"){
      return evalExpr(args[0]??"NULL",ctx,row,db,blobs,session);
    }
    if(name==="COUNT"){
      if(!args[0]||args[0].trim()==="*" )return 1;
      if(/^DISTINCT\s+/i.test(args[0]))return resolve(args[0].replace(/^DISTINCT\s+/i,""),ctx,row)==null?0:1;
      return (await evalExpr(args[0],ctx,row,db,blobs,session))==null?0:1;
    }
  }
  const plus=splitTop(e,"+");
  if(plus.length>1){let s=0;for(const p of plus)s+=Number(await evalExpr(p,ctx,row,db,blobs,session)||0);return s;}
  const minus=matchBinary(e,"-");
  if(minus)return Number(await evalExpr(minus[0],ctx,row,db,blobs,session)||0)-Number(await evalExpr(minus[1],ctx,row,db,blobs,session)||0);
  return resolve(e,ctx,row);
}
function parseFnArgs(expr:string){
  const open=expr.indexOf("(");const close=expr.lastIndexOf(")");
  if(open<0)return [];
  return splitList(expr.slice(open+1,close));
}
function matchBinary(e:string,op:string){
  const parts=splitTop(e,op);
  if(parts.length===2)return parts;
  return null;
}
async function mapNums(args:string[],ctx:Ctx,row:Row,db:Db,blobs:unknown[],session?:ClientSession){
  return Promise.all(args.map(async a=>Number(await evalExpr(a,ctx,row,db,blobs,session)||0)));
}
async function evalCase(expr:string,ctx:Ctx,row:Row,db:Db,blobs:unknown[],session?:ClientSession):Promise<unknown>{
  const body=expr.replace(/^CASE\s+/i,"").replace(/\s+END$/i,"").trim();
  // Support both searched CASE (WHEN cond THEN ...) and simple CASE (expr WHEN val THEN ...).
  let subject:string|null=null;
  let work=body;
  if(!/^WHEN\b/i.test(body)){
    const idx=body.search(/\sWHEN\b/i);
    if(idx>0){
      subject=body.slice(0,idx).trim();
      work=body.slice(idx).trim();
    }
  }
  const bits=splitTop(work,"WHEN");
  let elseVal:string|undefined;
  const subjectValue=subject?await evalExpr(subject,ctx,row,db,blobs,session):null;
  for(const bit of bits){
    if(!bit.trim())continue;
    if(/^ELSE\b/i.test(bit.trim()) && !/\bWHEN\b/i.test(bit)){elseVal=bit.replace(/^ELSE\s+/i,"");continue;}
    const thenAt=splitTop(bit,"THEN");
    if(thenAt.length<2)continue;
    const thenParts=splitTop(thenAt.slice(1).join(" THEN "),"ELSE");
    if(thenParts[1]!==undefined)elseVal=thenParts[1];
    const matched=subject
      ? cmp(subjectValue,"=",await evalExpr(thenAt[0],ctx,row,db,blobs,session))
      : await evalBool(thenAt[0],ctx,row,db,blobs,session);
    if(matched)return evalExpr(thenParts[0],ctx,row,db,blobs,session);
  }
  return elseVal!==undefined?evalExpr(elseVal,ctx,row,db,blobs,session):null;
}
async function evalBool(expr:string,ctx:Ctx,row:Row,db:Db,blobs:unknown[],session?:ClientSession):Promise<boolean>{
  let e=expr.trim();
  // Unwrap a fully-parenthesised group before splitting. splitTop only sees
  // operators at depth 0, so "(a AND b)" yields no AND/OR and no comparison,
  // and would otherwise fall through to resolve() and read as false.
  while(e.startsWith("(") && matchingParen(e)===e.length-1 && !/^\(\s*SELECT\b/i.test(e)) e=e.slice(1,-1).trim();
  const ors=splitTop(e,"OR");
  if(ors.length>1){for(const p of ors)if(await evalBool(p,ctx,row,db,blobs,session))return true;return false;}
  const ands=splitTop(e,"AND");
  if(ands.length>1){for(const p of ands)if(!await evalBool(p,ctx,row,db,blobs,session))return false;return true;}
  const not=e.match(/^NOT\s+([\s\S]+)$/i);
  if(not && !/^NOT\s+EXISTS/i.test(e) && !/^NOT\s+NULL/i.test(e))return !(await evalBool(not[1],ctx,row,db,blobs,session));
  const inn=e.match(/^([\w."`]+)\s+IN\s*\(([\s\S]+)\)\s*$/i);
  if(inn){
    const v=await evalExpr(inn[1],ctx,row,db,blobs,session);
    const list=splitList(inn[2]).map(x=>lit(x,blobs));
    return list.some(x=>x==v||Number(x)===Number(v));
  }
  const lk=e.match(/^(.+?)\s+LIKE\s+(.+)$/i);
  if(lk)return like(await evalExpr(lk[1],ctx,row,db,blobs,session),String(await evalExpr(lk[2],ctx,row,db,blobs,session)??""));
  const isn=e.match(/^(.+?)\s+IS\s+(NOT\s+)?NULL$/i);
  if(isn){const v=await evalExpr(isn[1],ctx,row,db,blobs,session);return isn[2]?v!==null&&v!==undefined:v===null||v===undefined;}
  const bet=e.match(/^(.+?)\s+BETWEEN\s+(.+?)\s+AND\s+(.+)$/i);
  if(bet){
    const v=Number(await evalExpr(bet[1],ctx,row,db,blobs,session));
    const a=Number(await evalExpr(bet[2],ctx,row,db,blobs,session));
    const b=Number(await evalExpr(bet[3],ctx,row,db,blobs,session));
    return v>=a && v<=b;
  }
  const ops=["<>",">=","<=","!=",">","<","="];
  for(const op of ops){
    const parts=splitTop(e,op);
    if(parts.length===2)return cmp(await evalExpr(parts[0],ctx,row,db,blobs,session),op,await evalExpr(parts[1],ctx,row,db,blobs,session));
  }
  const v=await evalExpr(e,ctx,row,db,blobs,session);
  return Boolean(v) && v!==0 && v!=="0";
}

type Join={type:"INNER"|"LEFT";table:string;alias:string;on:string};
type From={table:string;alias:string;joins:Join[];subquery?:string};
function matchingParen(sql:string,start=0){
  let depth=0,quote="";
  for(let i=start;i<sql.length;i++){
    const ch=sql[i];
    if(quote){if(ch===quote)quote="";continue;}
    if(ch==="'"||ch==='"'){quote=ch;continue;}
    if(ch==="(")depth++;
    if(ch===")"){depth--;if(depth===0)return i;}
  }
  return -1;
}
function parseJoins(sql:string){
  const joins:Join[]=[];
  if(!sql.trim())return joins;
  const parts=sql.trim().split(/\s+(?=(?:LEFT\s+)?JOIN\b)/i);
  for(const p of parts){
    const m=p.trim().match(/^(LEFT\s+JOIN|JOIN)\s+([\w]+)\s*(?:AS\s+)?(\w+)?\s+ON\s+([\s\S]+)$/i);
    if(!m)continue;
    joins.push({type:/LEFT/i.test(m[1])?"LEFT":"INNER",table:m[2],alias:m[3]||m[2],on:m[4]});
  }
  return joins;
}
function parseFrom(fromSql:string):From{
  const raw=fromSql.trim();
  if(raw.startsWith("(")){
    const close=matchingParen(raw);
    if(close<0)throw new Error("Invalid FROM");
    const subquery=raw.slice(1,close).trim();
    const rest=raw.slice(close+1).trim();
    const as=rest.match(/^(?:AS\s+)?(\w+)([\s\S]*)$/i);
    if(!as)throw new Error("Invalid FROM");
    return {table:as[1],alias:as[1],joins:parseJoins(as[2]||""),subquery};
  }
  const parts=raw.split(/\s+(?=(?:LEFT\s+)?JOIN\b)/i);
  const base=parts[0].trim().match(/^([\w]+)\s*(?:AS\s+)?(\w+)?/i);
  if(!base)throw new Error("Invalid FROM");
  return {table:base[1],alias:base[2]||base[1],joins:parseJoins(parts.slice(1).join(" "))};
}
async function loadAll(db:Db,table:string,session?:ClientSession){
  return db.collection(table).find({}, {session}).toArray() as Promise<Row[]>;
}
function flatten(ctx:Ctx,primary:string):Row{
  const row:Row={};
  for(const [alias,doc] of Object.entries(ctx)){
    if(!doc)continue;
    for(const [k,v] of Object.entries(doc)){
      if(k==="_id")continue;
      row[`${alias}.${k}`]=v;
      if(alias===primary && !(k in row))row[k]=v;
    }
  }
  const main=ctx[primary];
  if(main)Object.assign(row, Object.fromEntries(Object.entries(main).filter(([k])=>k!=="_id")));
  return row;
}
async function joinRows(from:From,db:Db,blobs:unknown[],session?:ClientSession,outer?:Ctx){
  let rows:Ctx[];
  if(from.subquery){
    const sql=/^\s*SELECT\b/i.test(from.subquery)?from.subquery:`SELECT ${from.subquery}`;
    const result=await runSelect(sql,db,blobs,session,outer);
    rows=result.results.map(doc=>({[from.alias]:stripId({...doc,_id:doc.id??doc._id})}));
  }else{
    const lefts=await loadAll(db,from.table,session);
    rows=lefts.map(doc=>({[from.alias]:stripId(doc)}));
  }
  for(const join of from.joins){
    const rights=await loadAll(db,join.table,session);
    const next:Ctx[]=[];
    for(const left of rows){
      let matched=false;
      for(const right of rights){
        const ctx={...outer,...left,[join.alias]:stripId(right)};
        const row=flatten(ctx,from.alias);
        if(await evalBool(join.on,ctx,row,db,blobs,session)){next.push(ctx);matched=true;}
      }
      if(!matched && join.type==="LEFT")next.push({...left,[join.alias]:{}});
    }
    rows=next;
  }
  return rows;
}
function stripId(doc:Row){
  const {_id,...rest}=doc;
  rest.id=asId(_id??rest.id);
  return rest;
}
type Col={expr:string;alias:string};
function parseCols(list:string):Col[]{
  const used=new Set<string>();
  return splitList(list).map((item,index)=>{
    const as=item.match(/^([\s\S]+?)\s+AS\s+("?[\w]+"?)$/i)||item.match(/^([\s\S]+?)\s+("?[\w.]+"?)$/i);
    let expr=item.trim();
    let alias="";
    if(as && !/^\w+\.\*$/.test(item.trim()) && !item.trim().endsWith("*")){
      const candidate=unquote(as[2]);
      if(/^[A-Za-z_][\w]*$/.test(candidate) && !/^(FROM|WHERE|JOIN|LIMIT)$/i.test(candidate)){
        expr=as[1].trim();
        alias=candidate;
      }
    }
    if(!alias){
      const t=item.trim();
      if(t.endsWith(".*"))alias=t;
      else{
        const ident=t.match(/^[\w."`]+$/);
        alias=ident?unquote(t.split(".").pop()||t):"";
      }
    }
    if(!alias || alias==="?" || used.has(alias)) alias=`col_${index}`;
    used.add(alias);
    return {expr,alias};
  });
}
async function project(cols:Col[],ctx:Ctx,row:Row,db:Db,blobs:unknown[],session?:ClientSession){
  const out:Row={};
  for(const col of cols){
    if(col.expr==="*"||col.alias==="*"){
      Object.assign(out, Object.fromEntries(Object.entries(row).filter(([k])=>!k.includes("."))));
      continue;
    }
    const star=col.expr.match(/^(\w+)\.\*$/);
    if(star){
      const doc=ctx[star[1]]||{};
      Object.assign(out,doc);
      continue;
    }
    out[col.alias]=await evalExpr(col.expr,ctx,row,db,blobs,session);
  }
  return out;
}
function parseSelect(sql:string){
  const s=strip(sql).replace(/^SELECT\s+/i,"");
  const union=splitTop(s,"UNION ALL");
  if(union.length>1)return {union,cols:[] as Col[],from:null as From|null,where:"",group:"",order:"",limit:undefined as string|undefined};
  const limitParts=splitTop(s,"LIMIT");
  const limit=limitParts[1]?.trim();
  const orderParts=splitTop(limitParts[0],"ORDER BY");
  const orderBy=orderParts[1]||"";
  const groupParts=splitTop(orderParts[0],"GROUP BY");
  const group=groupParts[1]||"";
  const whereParts=splitTop(groupParts[0],"WHERE");
  const where=whereParts[1]||"";
  const fromParts=splitTop(whereParts[0],"FROM");
  if(fromParts.length<2)return {cols:parseCols(fromParts[0]),from:null as From|null,where,group:"",order:orderBy,limit,union:undefined as string[]|undefined};
  return {cols:parseCols(fromParts[0]),from:parseFrom(fromParts.slice(1).join(" FROM ")),where,group,order:orderBy,limit,union:undefined as string[]|undefined};
}
function parseOrder(order:string){
  if(!order)return [];
  return splitList(order).map(part=>{
    const m=part.trim().match(/^([\s\S]+?)(?:\s+(ASC|DESC))?$/i);
    return {expr:m?.[1]||part,dir:/DESC/i.test(m?.[2]||"")?-1:1};
  });
}
async function runSelect(sql:string,db:Db,blobs:unknown[],session?:ClientSession,outer?:Ctx):Promise<QueryResult<Row>>{
  const s=strip(sql);
  if(/^1(\s+AS\s+ok)?$/i.test(s.replace(/^SELECT\s+/i,"").trim()) || /^SELECT\s+1(\s+AS\s+ok)?$/i.test(s))return {results:[{ok:1}],meta:{changes:0}};
  const parsed=parseSelect(s);
  if(parsed.union){
    const parts=await Promise.all(parsed.union.map(u=>runSelect(/^SELECT/i.test(u)?u:`SELECT ${u}`,db,blobs,session,outer)));
    let rows=parts.flatMap(p=>p.results);
    if(parsed.union){
      const orderMatch=s.match(/ORDER BY\s+([\s\S]+?)(?:\s+LIMIT\s+(\d+))?$/i);
      if(orderMatch){
        const spec=parseOrder(orderMatch[1].replace(/\s+LIMIT\s+\d+$/i,""));
        rows=sortRows(rows,spec);
        if(orderMatch[2])rows=rows.slice(0,Number(orderMatch[2]));
      }
    }
    return {results:rows,meta:{changes:0}};
  }
  if(!parsed.from){
    const ctx=outer||{};
    const row=outer?flatten(outer,Object.keys(outer)[0]||""):{};
    // INSERT…SELECT ? WHERE (subquery) and similar SQLite forms have no FROM clause.
    if(parsed.where && !(await evalBool(parsed.where,ctx,row,db,blobs,session)))return {results:[],meta:{changes:0}};
    const projected=await project(parsed.cols,ctx,row,db,blobs,session);
    return {results:[projected],meta:{changes:0}};
  }
  const ctxs=await joinRows(parsed.from,db,blobs,session,outer);
  const out:Row[]=[];
  for(const ctx of ctxs){
    const merged=outer?{...outer,...ctx}:ctx;
    const row=flatten(merged,parsed.from.alias);
    if(parsed.where && !(await evalBool(parsed.where,merged,row,db,blobs,session)))continue;
    out.push(await project(parsed.cols,merged,row,db,blobs,session));
  }
  let rows=out;
  const needsGroup=Boolean(parsed.group) || parsed.cols.some(c=>/^(COUNT|SUM|AVG|MAX|MIN)\s*\(/i.test(c.expr.trim()));
  if(needsGroup && !parsed.group)parsed.group="__all__";
  if(parsed.group){
    const keys=parsed.group==="__all__"?["__all__"]:splitList(parsed.group).map(k=>unquote(k.trim().split(".").pop()||k));
    const groups=new Map<string,Row[]>();
    if(!rows.length && parsed.group==="__all__")groups.set("__all__",[]);
    for(const r of rows){
      const id=parsed.group==="__all__"?"__all__":keys.map(k=>String(r[k])).join("|");
      const g=groups.get(id)||[];g.push(r);groups.set(id,g);
    }
    const aggregated:Row[]=[];
    for(const g of groups.values()){
      const base=g[0]?{...g[0]}:{};
      for(const col of parsed.cols){
        const e=col.expr;
        if(/^COUNT\s*\(\s*DISTINCT\s+/i.test(e)){
          const field=e.replace(/^COUNT\s*\(\s*DISTINCT\s+/i,"").replace(/\)\s*$/,"");
          const alias=field.includes(".")?unquote(field.split(".").pop()||field):unquote(field);
          const set=new Set(g.map(r=>String(r[col.alias]??r[alias]??resolve(field,{x:r},r))));
          base[col.alias]=set.size;
        }else if(/^COUNT\s*\(/i.test(e))base[col.alias]=g.length;
        else if(/^SUM\s*\(/i.test(e))base[col.alias]=g.reduce((s,r)=>s+Number(r[col.alias]||0),0);
        else if(/^AVG\s*\(/i.test(e))base[col.alias]=g.length?g.reduce((s,r)=>s+Number(r[col.alias]||0),0)/g.length:null;
        else if(/^MAX\s*\(/i.test(e))base[col.alias]=g.length?Math.max(...g.map(r=>Number(r[col.alias]||0))):null;
        else if(/^MIN\s*\(/i.test(e))base[col.alias]=g.length?Math.min(...g.map(r=>Number(r[col.alias]||0))):null;
      }
      aggregated.push(base);
    }
    rows=aggregated;
  }
  const spec=parseOrder(parsed.order||"");
  if(spec.length)rows=sortRows(rows,spec);
  if(parsed.limit)rows=rows.slice(0,Number(parsed.limit));
  return {results:rows,meta:{changes:0}};
}
function sortRows(rows:Row[],spec:{expr:string;dir:number}[]){
  return [...rows].sort((a,b)=>{
    for(const s of spec){
      const ak=s.expr.split(".").pop()||s.expr;
      const av=a[unquote(ak)]??a[s.expr];
      const bv=b[unquote(ak)]??b[s.expr];
      const an=Number(av),bn=Number(bv);
      const cmpN=!Number.isNaN(an)&&!Number.isNaN(bn)?an-bn:String(av??"").localeCompare(String(bv??""));
      if(cmpN)return cmpN*s.dir;
    }
    return 0;
  });
}

async function runInsert(sql:string,db:Db,blobs:unknown[],session?:ClientSession):Promise<QueryResult<Row>>{
  const s=strip(sql);
  const conflict=s.match(/\sON CONFLICT\s*(?:\(([^)]+)\))?\s+(DO NOTHING|DO UPDATE SET\s+([\s\S]+))$/i);
  const returning=s.match(/\sRETURNING\s+(\w+)\s*$/i);
  const core=s.replace(/\sON CONFLICT[\s\S]+$/i,"").replace(/\sRETURNING\s+\w+\s*$/i,"");
  const ins=core.match(/^INSERT\s+INTO\s+([\w]+)\s*\(([^)]+)\)\s+(VALUES|SELECT)\s*([\s\S]+)$/i);
  if(!ins)throw new Error(`Unsupported INSERT: ${s.slice(0,120)}`);
  const table=ins[1];
  const cols=splitList(ins[2]).map(unquote);
  let values:unknown[][]=[];
  if(/^VALUES$/i.test(ins[3])){
    const tuples=ins[4].trim();
    // simpler: single tuple
    const one=tuples.match(/^\(([\s\S]+)\)$/);
    const items=splitList(one?one[1]:tuples);
    values=[await Promise.all(items.map(it=>evalExpr(it,{},{},db,blobs,session)))];
  }else{
    const selectSql=`SELECT ${ins[4]}`.replace(/^SELECT SELECT/i,"SELECT");
    const parsed=parseSelect(selectSql);
    const sel=await runSelect(selectSql,db,blobs,session);
    if(!sel.results.length)return {results:[],meta:{changes:0,last_row_id:0}};
    values=sel.results.map(row=>{
      if(parsed.cols.length)return parsed.cols.map(col=>row[col.alias]);
      return Object.values(row);
    });
  }
  const docs:Row[]=[];
  for(const tuple of values){
    const doc:Row={};
    cols.forEach((c,i)=>doc[c]=normalizeValue(tuple[i]));
    if(table==="operation_guards" && Number(doc.valid)!==1){
      const err=new Error("Operation guard failed");
      (err as {code?:string}).code="GUARD_FAILED";
      throw err;
    }
    assignDocumentId(table,doc);
    docs.push(doc);
  }
  const col=db.collection(table);
  try{
    if(docs.length===1)await col.insertOne(docs[0],{session});
    else if(docs.length)await col.insertMany(docs,{session,ordered:true});
  }catch(error){
    const dup=typeof error==="object"&&error && "code" in error && Number((error as {code:number}).code)===11000;
    if(dup && conflict && /DO NOTHING/i.test(conflict[2]))return {results:[],meta:{changes:0,last_row_id:0}};
    if(dup && conflict && /DO UPDATE SET/i.test(conflict[2])){
      const keys=splitList(conflict[1]||"").map(unquote);
      const filter:Row={};
      for(const k of keys)filter[k]=docs[0][k];
      const sets=splitList(conflict[3]||"");
      const $set:Row={};
      for(const asg of sets){
        const [left,right]=splitTop(asg,"=");
        const field=unquote(left.trim().replace(/^[\w]+\./,""));
        const expr=right.replace(/EXCLUDED\./gi,"");
        $set[field]=docs[0][unquote(expr.trim())]??await evalExpr(expr,{t:docs[0]},docs[0],db,blobs,session);
      }
      await col.updateOne(filter,{$set},{session,upsert:true});
      return {results:docs.map(d=>({...d,id:asId(d._id)})),meta:{changes:1,last_row_id:0}};
    }
    throw error;
  }
  for(const d of docs)d.id=asId(d._id);
  const results=returning?docs.map(d=>({[returning[1]]:d[returning[1]]})):docs;
  return {results,meta:{changes:docs.length,last_row_id:0}};
}
function normalizeValue(v:unknown){
  if(v instanceof Uint8Array)return new Binary(Buffer.from(v));
  if(Buffer.isBuffer(v))return new Binary(v);
  return v;
}
async function runUpdate(sql:string,db:Db,blobs:unknown[],session?:ClientSession):Promise<QueryResult<Row>>{
  const s=strip(sql);
  const m=s.match(/^UPDATE\s+([\w]+)\s+SET\s+([\s\S]+?)(?:\s+WHERE\s+([\s\S]+))?$/i);
  if(!m)throw new Error(`Unsupported UPDATE: ${s.slice(0,120)}`);
  const table=m[1], sets=splitList(m[2]), where=m[3]||"1=1";
  const docs=await loadAll(db,table,session);
  let changes=0;
  for(const raw of docs){
    const doc=stripId(raw);
    const ctx={[table]:doc};
    const row=flatten(ctx,table);
    if(!(await evalBool(where,ctx,row,db,blobs,session)))continue;
    const $set:Row={};
    const $inc:Row={};
    for(const asg of sets){
      const parts=splitTop(asg,"=");
      const field=unquote(parts[0].trim());
      const expr=parts.slice(1).join("=");
      const plus=expr.match(new RegExp(`^${field}\\s*\\+\\s*(.+)$`,"i"));
      if(plus){$inc[field]=Number(await evalExpr(plus[1],ctx,row,db,blobs,session)||0);continue;}
      $set[field]=await evalExpr(expr,ctx,row,db,blobs,session);
    }
    const update:Row={};
    if(Object.keys($set).length)update.$set=$set;
    if(Object.keys($inc).length)update.$inc=$inc;
    const filter=raw._id!==undefined?{_id:raw._id}:{id:doc.id};
    await db.collection(table).updateOne(filter as never,update as never,{session});
    changes++;
  }
  return {results:[],meta:{changes}};
}
async function runDelete(sql:string,db:Db,blobs:unknown[],session?:ClientSession):Promise<QueryResult<Row>>{
  const s=strip(sql);
  const m=s.match(/^DELETE\s+FROM\s+([\w]+)\s*(?:WHERE\s+([\s\S]+))?$/i);
  if(!m)throw new Error(`Unsupported DELETE: ${s.slice(0,120)}`);
  const table=m[1], where=m[2]||"1=1";
  const docs=await loadAll(db,table,session);
  const ids:unknown[]=[];
  for(const raw of docs){
    const doc=stripId(raw);
    const ctx={[table]:doc};
    const row=flatten(ctx,table);
    if(await evalBool(where,ctx,row,db,blobs,session))ids.push(raw._id);
  }
  if(ids.length)await db.collection(table).deleteMany({_id:{$in:ids}} as never,{session});
  return {results:[],meta:{changes:ids.length}};
}

export async function execSql(sql:string,values:unknown[]=[],session?:ClientSession):Promise<QueryResult<Row>>{
  const {sql:bound,blobs}=takeParams(strip(sql),values);
  const db=await mongoDb();
  if(/^SELECT\s+/i.test(bound))return runSelect(bound,db,blobs,session);
  if(/^INSERT\s+/i.test(bound))return runInsert(bound,db,blobs,session);
  if(/^UPDATE\s+/i.test(bound))return runUpdate(bound,db,blobs,session);
  if(/^DELETE\s+/i.test(bound))return runDelete(bound,db,blobs,session);
  throw new Error(`Unsupported SQL: ${bound.slice(0,160)}`);
}

export class Prepared {
  constructor(readonly sql:string,readonly values:unknown[]=[],private session?:ClientSession){}
  bind(...values:unknown[]){return new Prepared(this.sql,values,this.session);}
  async all<T=Row>():Promise<QueryResult<T>>{return execSql(this.sql,this.values,this.session) as Promise<QueryResult<T>>;}
  async first<T=Row>():Promise<T|null>{const r=await this.all<T>();return r.results[0]||null;}
  async run(){return execSql(this.sql,this.values,this.session);}
}
export class MongoSqlDb {
  prepare(sql:string){return new Prepared(sql);}
  async batch(statements:Prepared[]){
    // Sequential execution: the SQL→Mongo emulator already issues discrete
    // collection ops; multi-doc transactions often hit the 60s txnLifetime
    // on Atlas and make API routes look like they never respond.
    const results:QueryResult<Row>[]=[];
    for(const statement of statements){
      results.push(await new Prepared(statement.sql,statement.values).run());
    }
    return results;
  }
  async withConnection<T>(fn:(db:{prepare:(sql:string)=>Prepared})=>Promise<T>){
    return fn({prepare:(sql:string)=>new Prepared(sql)});
  }
  async ping(){
    const db=await mongoDb();
    await db.command({ping:1});
  }
}
