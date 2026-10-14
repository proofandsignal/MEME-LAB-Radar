// Browser contract smoke with a minimal DOM harness, without external dependencies.
// This is NOT a full real-browser E2E test.
const fs=require("node:fs");
const vm=require("node:vm");
const assert=require("node:assert/strict");
function element(){
 const e={textContent:"",value:"",disabled:false,hidden:false,children:[],listeners:{},
  classList:{add(){},remove(){}},append(...xs){this.children.push(...xs)},
  replaceChildren(...xs){this.children=[...xs]},addEventListener(k,v){this.listeners[k]=v},
  before(){},click(){},setAttribute(){}};
 return e;
}
const elements=new Map();
const document={
 getElementById(id){if(!elements.has(id))elements.set(id,element());return elements.get(id)},
 createElement(){return element()},
 body:element()
};
const context=vm.createContext({document,console,Intl,Number,String,JSON,Blob,URL});
vm.runInContext(fs.readFileSync("app.js","utf8"),context,{filename:"app.js"});
const fixture={
 schema_version:"0.4.0",data_gate:"UNVERIFIED",generated_at:"2026-10-12T06:00:00Z",
 observations:[{chain:"testnet",pool_address:"pool-1",source:"fixture",
 observed_at:"2026-10-12T06:00:00Z",stock_symbol:"NVDA",
 base_token:"meme-1",quote_token:"stock-1",price_usd:1,liquidity_usd:300,
 volume_24h_usd:200}]
};
function load(v){vm.runInContext("importData("+JSON.stringify(JSON.stringify(v))+")",context)}
load(fixture);
assert.equal(document.getElementById("mTracked").textContent,"1");
assert.equal(document.getElementById("modeBadge").textContent,"FILE / UNVERIFIED");
assert.equal(document.getElementById("apiHealth").textContent,"not connected");
const row=document.getElementById("rows").children[0];
assert.equal(row.children[5].textContent,"VERIFY");
assert.equal(row.children[3].textContent,"UNVERIFIED");
assert.equal(row.children[11].textContent,"UNKNOWN");
assert.throws(()=>load({...fixture,data_gate:"VERIFIED"}),/Incompatible/);
assert.throws(()=>load({...fixture,observations:[{chain:7}]}),/Invalid/);
assert.equal(document.getElementById("mTracked").textContent,"1","bad import must retain previous dataset");
document.getElementById("search").value="absent";
document.getElementById("search").listeners.input();
assert.equal(document.getElementById("rows").children.length,0);
console.log("UI DOM contract smoke PASS: render / unknown provenance / invalid rejection / search");
