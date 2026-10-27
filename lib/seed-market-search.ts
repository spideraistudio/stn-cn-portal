import type {SeedRequest} from './seed-requests';
export type MarketFilters={query:string;crop:string;state:string;type:string;sort:string};
export function searchSeedMarket(rows:SeedRequest[],f:MarketFilters){
 const terms=f.query.toLocaleLowerCase().trim().split(/\s+/).filter(Boolean);
 return rows.filter(r=>(!f.crop||r.crop.toLocaleLowerCase()===f.crop.toLocaleLowerCase())&&(!f.state||r.deliveryState===f.state)&&( !f.type||r.varietyType===f.type)&&terms.every(t=>[r.crop,r.segment,r.description,r.deliveryState,r.deliveryDistrict,r.ownerCompany,r.panIndia?'pan india':''].join(' ').toLocaleLowerCase().includes(t))).sort((a,b)=>f.sort==='deadline'?new Date(a.quotationDeadline).getTime()-new Date(b.quotationDeadline).getTime():f.sort==='quantity'?(b.quantity*(b.quantityUnit==='MT'?1000:1))-(a.quantity*(a.quantityUnit==='MT'?1000:1)):new Date(b.createdAt).getTime()-new Date(a.createdAt).getTime());
}
