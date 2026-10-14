// MEME LAB static read-only UI. No network requests, no trading, no invented live data.
const $ = id => document.getElementById(id);
let observations = [], loaded = null;
const msg = message => { $("message").textContent = message; };
const safe = v => String(v ?? "—");
const amount = v => Number.isFinite(v) ? new Intl.NumberFormat("en-US",{maximumFractionDigits:2}).format(v) : "—";
function show() {
  const query = $("search").value.trim().toLowerCase();
  const rows = observations.filter(r => [r.stock_symbol,r.pool_address,r.chain,r.base_token,r.quote_token].some(x => safe(x).toLowerCase().includes(query)));
  $("mTracked").textContent = String(rows.length);
  $("mSnapshots").textContent = String(rows.length);
  for (const id of ["mNew","mGrowing","mBreakout","mRisk"]) $(id).textContent = "—";
  $("rows").replaceChildren();
  for (const r of rows) {
    const tr = document.createElement("tr");
    const values = [safe(r.base_token),safe(r.stock_symbol)+" / "+safe(r.quote_token),"unknown","UNVERIFIED","—","VERIFY",amount(r.price_usd),amount(r.liquidity_usd),amount(r.volume_24h_usd),"—","—","UNKNOWN","1"];
    for (const value of values) { const td = document.createElement("td"); td.textContent = value; tr.append(td); }
    tr.addEventListener("click", () => {
      $("drawer").classList.add("open");
      $("dTitle").textContent = safe(r.stock_symbol)+" · "+safe(r.pool_address);
      $("dSub").textContent = "Source supplied; contract and stock mapping NOT independently verified";
      $("details").textContent = "Chain: "+safe(r.chain)+" | Snapshot: "+safe(r.observed_at)+" | Source: "+safe(r.source);
      $("risks").textContent = "UNKNOWN: issuer, market exposure, holders and liquidity integrity are not verified.";
      $("history").textContent = JSON.stringify(r,null,2);
    });
    $("rows").append(tr);
  }
}
function importData(text) {
  const payload = JSON.parse(text);
  if (!payload || payload.schema_version !== "0.4.0" || payload.data_gate !== "UNVERIFIED" || !Array.isArray(payload.observations)) throw Error("Incompatible or missing provenance schema");
  for (const r of payload.observations) {
    if (!r || typeof r.chain !== "string" || typeof r.pool_address !== "string" || typeof r.source !== "string" || typeof r.observed_at !== "string") throw Error("Invalid observation");
  }
  loaded = payload;
  observations = payload.observations;
  $("mode").value = "demo";
  $("modeBadge").textContent = "FILE / UNVERIFIED";
  $("apiHealth").textContent = "not connected";
  $("lastScan").textContent = safe(payload.generated_at);
  $("queue").textContent = "offline";
  msg("Imported "+observations.length+" read-only records. No issuer or market data verified.");
  show();
}
const input = document.createElement("input");
input.type = "file"; input.accept = ".json,application/json"; input.hidden = true;
document.body.append(input);
const btn = document.createElement("button"); btn.textContent = "IMPORT COLLECTOR JSON";
$("scan").before(btn);
btn.addEventListener("click",()=>input.click());
input.addEventListener("change",async()=>{
  try { if(input.files?.[0]) importData(await input.files[0].text()); }
  catch(e) { msg("INVALID / VERIFY: "+e.message); }
  input.value = "";
});
$("scan").addEventListener("click",()=>msg("NO LIVE SCANNER: import v0.4 export-ui JSON. No simulated live prices."));
$("refresh").addEventListener("click",()=>msg("NO API CONNECTION: manually import a fresh collector snapshot."));
$("mode").addEventListener("change",()=>{ $("mode").value="demo"; msg("LIVE APIs NOT ENABLED: import a collector export."); });
$("export").addEventListener("click",()=>{
  if(!loaded) return msg("No loaded observations to export.");
  const b = new Blob([JSON.stringify(loaded,null,2)],{type:"application/json"});
  const url = URL.createObjectURL(b), a = document.createElement("a");
  a.href=url; a.download="meme-radar-unverified.json";a.click(); URL.revokeObjectURL(url);
});
$("reset").addEventListener("click",()=>{
  loaded=null;observations=[];$("lastScan").textContent="—";$("modeBadge").textContent="DEMO";
  msg("Browser view cleared. This does not delete SQLite collector records.");show();
});
$("search").addEventListener("input",show);
$("close").addEventListener("click",()=>$("drawer").classList.remove("open"));
for(const id of ["state","gate","sort"]) $(id).disabled=true;
$("mode").value="demo"; $("modeBadge").textContent="DEMO / NO DATA";
msg("Research UI ready. Import a v0.4 collector JSON; nothing is live or verified.");
show();
