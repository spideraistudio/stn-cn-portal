// Execute production zoom/layout in a geometry harness, not a native browser.
const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
let theme='studio',oldCalls=0;
const root={x:800,y:600,w:180,h:100,el:{style:{setProperty(){}},dataset:{}}};
const nodes=[root,{x:470,y:360,w:150,h:80,el:{style:{setProperty(){}},dataset:{}}}];
const view={clientWidth:1100,clientHeight:700,clientLeft:2,clientTop:2,scrollTop:0,scrollLeft:0,getBoundingClientRect:()=>({left:80,top:120})};
const diagram={isConnected:true,style:{},classList:{toggle(){}}};
const current={v:view,d:diagram,sizer:{style:{}},nodes,edges:[],width:2000,height:1600,session:{locked:false,positions:[{key:'saved',x:470,y:360}]}};
const context={document:{documentElement:{dataset:{get cnTheme(){return theme}}},querySelector:()=>null,addEventListener(){}},window:{addEventListener(){}},radialView:{scale:.5,left:0,top:0},drawAllocationFlow(){},radialPointerDown(){},radialPointerMove(){},radialZoomAt(){oldCalls++},console};
vm.createContext(context);let src=fs.readFileSync(process.env.CN_ZOOM_SCRIPT||'static/studio.js','utf8');src=src.replace(/\}\)\(\);\s*$/, 'globalThis.zoomTest={set(m){current=m},layout};})();');vm.runInContext(src,context);context.zoomTest.set(current);context.zoomTest.layout();
function transform(){const n=diagram.style.transform.match(/-?\d*\.?\d+(?:e[+-]?\d+)?/g).map(Number);return {x:n[0],y:n[1],z:n[2]};}
function anchored(delta,px,py){const a=transform(),wx=(px-a.x)/a.z,wy=(py-a.y)/a.z;context.radialZoomAt(delta,px+82,py+122);const b=transform();assert.ok(Math.abs(b.x+wx*b.z-px)<1e-8,'cursor x moved');assert.ok(Math.abs(b.y+wy*b.z-py)<1e-8,'cursor y moved');assert.ok(b.z>=.06&&b.z<=2.5);}
const original=JSON.stringify([nodes.map(n=>[n.x,n.y]),current.session]);
for(const [x,y] of [[130,90],[950,110],[140,590],[960,600],[550,350]]){anchored(-150,x,y);anchored(75,x,y);}
for(let i=0;i<40;i++)anchored(-300,170,140);
assert.equal(context.radialView.scale,2.5);for(let i=0;i<40;i++)anchored(300,910,580);assert.equal(context.radialView.scale,.06);
context.radialView.scale=null;context.zoomTest.layout();let fit=transform();assert.ok(Math.abs(fit.x+root.x*fit.z-view.clientWidth/2)<1e-8);assert.ok(Math.abs(fit.y+root.y*fit.z-view.clientHeight/2)<1e-8);assert.equal(current.cameraX,0);assert.equal(current.cameraY,0);
anchored(-120,200,180);context.zoomTest.layout();anchored(-80,900,500);assert.equal(JSON.stringify([nodes.map(n=>[n.x,n.y]),current.session]),original,'zoom changed card positions or saved layout');
theme='classic';context.radialZoomAt(-120,300,300);assert.equal(oldCalls,1,'Classic zoom delegation changed');
console.log('PASS: production Studio cursor anchor in four quadrants and centre, repeated zoom in/out, scale limits, Fit reset, redraw, unchanged card coordinates/saved layouts, Classic delegation. Geometry harness; Windows/native browser pending.');
