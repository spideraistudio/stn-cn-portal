import test, {before,after,mock} from 'node:test';
import assert from 'node:assert/strict';
import {buyerLabel, selectionError, supplierCanAccess, supplierCanQuote, supplierRequestView, validateQuotation} from '../lib/seed-trading';
import type {SeedRequest} from '../lib/seed-requests';

const NOW = Date.parse('2026-09-29T10:00:00+05:30');
before(()=>mock.method(Date,'now',()=>NOW));
after(()=>mock.restoreAll());
const request: SeedRequest = {
  id:'req-1', ownerId:'buyer-id', ownerCompany:'Private Buyer Ltd', status:'published',
  createdAt:NOW, updatedAt:NOW, publishedAt:NOW, crop:'Maize', segment:'Hybrid', description:'Seed',
  varietyType:'hybrid', productMatch:'equivalent', quantity:20, quantityUnit:'MT', partialAllowed:true,
  cleaning:'either', treatment:'either', germinationRequired:true, gotRequired:false,
  deliveryState:'Gujarat', deliveryDistrict:'Ahmedabad', destination:'Warehouse', deliveryBy:'2026-10-20',
  transport:'included', paymentTerms:'', quotationDeadline:Date.parse('2026-10-10T23:59:59+05:30'),
  anonymous:true, panIndia:false, supplierStates:['Gujarat']
};
const quote = {offeredProduct:'Maize A',crop:'Maize',segment:'Hybrid',varietyType:'hybrid',quantity:10,
  quantityUnit:'MT',price:42000,priceUnit:'MT',cleaning:'clean',treatment:'treated',
  earliestDelivery:'2026-10-18',transportIncluded:true,pricingBasis:'Delivered to Ahmedabad',
  paymentType:'cash',germinationAvailable:true,gotAvailable:false,validUntil:'2026-10-10'};

test('approved company state scopes access independently of notification preference',()=>{
  assert.equal(supplierCanAccess(request,{id:'a',state:'Gujarat'}),true);
  assert.equal(supplierCanAccess(request,{id:'b',state:'Maharashtra'}),false);
  assert.equal(supplierCanAccess(request,{id:'c',state:''}),false);
  assert.equal(supplierCanAccess({...request,panIndia:true},{id:'b',state:'Maharashtra'}),true);
  assert.equal(supplierCanAccess({...request,status:'closed'},{id:'buyer-id',state:''}),true);
  assert.equal(supplierCanAccess({...request,status:'closed'},{id:'a',state:'Gujarat'}),false);
  assert.equal(supplierCanAccess(request,{id:'a',state:'Gujarat'}),true);
  assert.equal(supplierCanAccess(request,{id:'a',state:'Gujarat'}),true);
});

test('the same member may buy on one request and supply on another, but never quote their own',()=>{
  const x={id:'buyer-id',state:'Gujarat'};
  const a={id:'a',state:'Gujarat'};
  assert.equal(supplierCanQuote(request,x),false);
  assert.equal(supplierCanQuote(request,a),true);
  assert.equal(supplierCanQuote({...request,ownerId:'a'},a),false);
  assert.equal(supplierCanQuote({...request,ownerId:'a'},x),true);
});

test('anonymous supplier view omits owner identifiers and reveals per quotation',()=>{
  const hidden=supplierRequestView(request);
  assert.equal(hidden.ownerCompany,'Anonymous buyer');
  assert.equal('ownerId' in hidden,false);
  assert.equal(JSON.stringify(hidden).includes('Private Buyer Ltd'),false);
  assert.equal(buyerLabel(request,{revealBuyerName:true}),'Private Buyer Ltd');
  assert.equal(supplierRequestView(request,{revealBuyerName:true}).ownerCompany,'Private Buyer Ltd');
  assert.equal(supplierRequestView(request,{revealBuyerName:false}).ownerCompany,'Anonymous buyer');
});

test('quotation validates partial/full kg conversion, deadline and dates',()=>{
  assert.equal(validateQuotation(quote,request,NOW).normalizedPricePerKg,42);
  assert.throws(()=>validateQuotation({...quote,quantity:21},request,NOW),/exceed/);
  assert.throws(()=>validateQuotation(quote,{...request,partialAllowed:false},NOW),/partial/);
  assert.equal(validateQuotation({...quote,quantity:20000,quantityUnit:'kg'}, {...request,partialAllowed:false}, NOW).quantity,20000);
  assert.throws(()=>validateQuotation(quote,request,request.quotationDeadline),/deadline/);
  assert.throws(()=>validateQuotation({...quote,validUntil:'2026-02-30'},request,NOW),/validity/);
  assert.throws(()=>validateQuotation({...quote,pricingBasis:''},request,NOW),/pricing basis/);
});

test('approval respects remaining quantity and quote validity',()=>{
  const candidate={quantity:12,quantityUnit:'MT',validUntil:'2026-10-10'} as Parameters<typeof selectionError>[1];
  const existing={quantity:9,quantityUnit:'MT'} as Parameters<typeof selectionError>[1];
  assert.match(selectionError(request,candidate,[existing],NOW)||'',/exceed/);
  assert.equal(selectionError(request,{...candidate,quantity:11},[existing],NOW),null);
  assert.equal(selectionError(request,{...candidate,validUntil:'2026-10-15'},[],request.quotationDeadline+1000),null);
  assert.match(selectionError({...request,status:'closed'},candidate,[],NOW)||'',/closed/);
  assert.match(selectionError(request,{...candidate,validUntil:'2026-09-28'},[],NOW)||'',/no longer valid/);
});
