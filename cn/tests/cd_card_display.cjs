const assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm'),path=require('node:path');
const root=path.resolve(__dirname,'..'),app=fs.readFileSync(path.join(root,'backend/cn_web/calculator_static/app.js'),'utf8');
const ctx=vm.createContext({highlightPaymentDestinations(){}});
for(const name of ['decimalParts','exactDifference','allocationTotal'])vm.runInContext(app.match(new RegExp('function '+name+'\\([^\\n]+'))[0],ctx);
vm.runInContext(fs.readFileSync(path.join(root,'backend/cn_web/calculator_static/cd-card-display.js'),'utf8'),ctx);
function shares(weights,amount,extra=[]){
 const items=weights.map((_,i)=>({sc:{id:'s'},p:{id:'p'+i}}));
 const products=weights.map((n,i)=>({scheme:'s',product_id:'p'+i,regular_net:n}));
 const allocations=[{type:'CD',scheme:'s',product:'',amount},...extra],before=JSON.stringify([items,products,allocations]);
 const result=ctx.cdProductCardShares(items,allocations,products).get('s');
 assert.equal(JSON.stringify([items,products,allocations]),before,'Display must not mutate financial data');
 return result&&[...result.values()];
}
assert.deepEqual(shares(['800','32','60'],'100000'),['89686.10','3587.44','6726.46']);
assert.deepEqual(shares(['1','1','1'],'0.01'),['0.01','0.00','0.00']);
assert.deepEqual(shares(['1','0','-1'],'23.48'),['23.48','0.00','0.00']);
assert.equal(shares(['0','0'],'1000'),undefined,'No fabricated credit when eligibility is missing');
assert.deepEqual(shares(['0.00003','0.00001'],'100'),['75.00','25.00']);
assert.deepEqual(shares(['1','1'],'9999999999999999.99'),['5000000000000000.00','4999999999999999.99']);
assert.deepEqual(shares(['1','1'],'10',[{type:'CD',scheme:'s',product:'p0',amount:'4'},{type:'CD',scheme:'other',amount:'1000'},{type:'ABS',scheme:'s',amount:'1000'}]),['5.00','5.00']);
assert.deepEqual(shares(['1'],'0.005'),['0.01']);
assert.equal(shares(['1'],'0'),undefined);
const mixed=ctx.cdProductCardShares([{sc:{id:'s'},p:{id:'p'}},{sc:{id:'t'},p:{id:'p'}}],[{type:'CD',scheme:'s',amount:'10'},{type:'CD',scheme:'t',amount:'30'}],[{scheme:'s',product_id:'p',regular_net:'4'},{scheme:'t',product_id:'p',regular_net:'8'}]);
assert.equal(mixed.get('s').get('p'),'10.00');assert.equal(mixed.get('t').get('p'),'30.00');
console.log('PASS: exact CD card attribution, cent remainders, fractional/large amounts, zero/negative eligibility, direct/other-scheme exclusion and no mutations.');
