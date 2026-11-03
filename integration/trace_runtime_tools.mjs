// Run only in setup's isolated build directory. Trace local Mongo/setup helpers.
import fs from 'node:fs';
import path from 'node:path';
import { createRequire } from 'node:module';
const require=createRequire(import.meta.url);
const {nodeFileTrace}=require('next/dist/compiled/@vercel/nft');
const base=process.cwd(),dest=path.resolve(process.argv[2]);
const {fileList}=await nodeFileTrace(['integration/mongo_local.mjs','scripts/setup-mongo.mjs'],{base,processCwd:base});
for(const relative of new Set([...fileList,'package.json'])){
 const from=path.resolve(base,relative),to=path.resolve(dest,relative);
 if(!from.startsWith(base+path.sep)||!to.startsWith(dest+path.sep))throw Error('Unexpected trace path');
 fs.mkdirSync(path.dirname(to),{recursive:true});
 // Materialize targets: generated runtime must not retain build-directory links.
 fs.copyFileSync(from,to);
}
