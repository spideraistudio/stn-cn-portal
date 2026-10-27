'use strict';
// Diagram attribution only. Saved CD rows and the financial engine stay pooled.
function cdProductCardShares(items,allocations,productRows){
 const schemes=new Map(),out=new Map();
 for(const {sc,p} of items){
  if(!p)continue;
  if(!schemes.has(sc.id))schemes.set(sc.id,new Map());
  const row=productRows.find(r=>r.scheme===sc.id&&r.product_id===p.id);
  const weight=decimalParts(row?.regular_net||'0');
  schemes.get(sc.id).set(p.id,{id:p.id,weight:{...weight,n:weight.n>0n?weight.n:0n}});
 }
 for(const [scheme,members] of schemes){
  const pool=decimalParts(allocationTotal(allocations.filter(a=>a.type==='CD'&&a.scheme===scheme&&!a.product)));
  if(pool.n<=0n)continue;
  const rows=[...members.values()].sort((a,b)=>a.id<b.id?-1:a.id>b.id?1:0);
  const scale=Math.max(0,...rows.map(r=>r.weight.scale));
  const weights=rows.map(r=>r.weight.n*10n**BigInt(scale-r.weight.scale));
  const total=weights.reduce((a,b)=>a+b,0n);if(!total)continue;
  // Largest-remainder attribution at displayed paise precision; never floats.
  const divisor=10n**BigInt(pool.scale);
  const paise=(pool.n*100n+divisor/2n)/divisor;
  const shares=weights.map(w=>paise*w/total),remainders=weights.map(w=>paise*w%total);
  let left=paise-shares.reduce((a,b)=>a+b,0n);
  const order=rows.map((_,i)=>i).sort((a,b)=>remainders[a]===remainders[b]?a-b:remainders[a]>remainders[b]?-1:1);
  for(const i of order){if(!left)break;shares[i]++;left--;}
  out.set(scheme,new Map(rows.map((r,i)=>[r.id,(shares[i]/100n)+'.'+(shares[i]%100n).toString().padStart(2,'0')])));
 }
 return out;
}
const cdOriginalHighlight=highlightPaymentDestinations;
highlightPaymentDestinations=function(){
 cdOriginalHighlight();
 if(!record||!result||page!=='Calculate CN'||step!==2)return;
 const items=radialGroups('CD').flatMap(g=>g.items),source=paymentEntrySource();
 const shares=cdProductCardShares(items,record.allocations.filter(a=>a.source===source),result.product_CNs||[]);
 for(const node of document.querySelectorAll('#radial-diagram [data-radial-type="CD"][data-radial-product]')){
  const amount=shares.get(node.dataset.radialScheme)?.get(node.dataset.radialProduct);
  if(amount&&decimalParts(amount).n>0n)node.classList.add('payment-source-linked');
 }
};
